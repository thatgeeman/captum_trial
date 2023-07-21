# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/02_run.ipynb.

# %% auto 0
__all__ = ['CIFARLightningModule']

# %% ../nbs/02_run.ipynb 2
import torch
from torch import nn
import torch.nn.functional as F
import pytorch_lightning as pl
from pytorch_lightning.callbacks import TQDMProgressBar
from sklearn.metrics import roc_auc_score

from typing import Any, Union, Tuple

# %% ../nbs/02_run.ipynb 3
_size_2_t = Union[int, Tuple[int, int]]

# %% ../nbs/02_run.ipynb 7
class CIFARLightningModule(pl.LightningModule):
    def __init__(
        self,
        model,
        dls,
        lr=3e-3,
        wd=1e-4,
        loss_func=nn.CrossEntropyLoss,
        verbose=True,
        patience=10,
    ):
        # x = B 1 5 20 20
        super(CIFARLightningModule, self).__init__()
        self.model = model
        self.verbose = verbose
        self.patience = patience
        self.loss_func = loss_func(label_smoothing=0.1)
        self.lr = lr
        self.wd = wd
        self.train_dls, self.valid_dls = dls
        # self.flat = nn.Flatten()
        self.save_hyperparameters(ignore="model")

    def forward(self, x):
        return self.model(x)

    def train_dataloader(self):
        return self.train_dls
    
    def val_dataloader(self):
        return self.valid_dls

    def training_step(self, batch, bidx):
        images, labels = batch
        logits = self(images)
        acts = F.softmax(logits, dim=-1)
        preds = acts.argmax(-1).squeeze().cpu()
        preds_raw = acts.detach().cpu() 
        labels = labels.to(torch.long)
        train_loss = self.loss_func(logits.squeeze(), labels.squeeze())
        return {
            "loss": train_loss,
            "train_preds_step": preds,
            "train_preds_raw_step": preds_raw,
            "train_labels_step": labels.squeeze().cpu(),
        }

    def validation_step(self, batch, bidx):
        images, labels = batch
        logits = self(images)
        acts = F.softmax(logits, dim=-1)
        preds = acts.argmax(-1).squeeze().cpu()
        preds_raw = acts.detach().cpu()  
        labels = labels.to(torch.long)
        valid_loss = self.loss_func(logits.squeeze(), labels.squeeze())
        return {
            "valid_loss_step": valid_loss.item(),
            "valid_preds_step": preds,
            "valid_preds_raw_step": preds_raw,
            "valid_labels_step": labels.squeeze().cpu(),
        }

    def on_training_epoch_end(self, outputs):
        # outputs from all training steps
        preds = []
        labels = []
        loss = 0.0
        for out in outputs:
            preds.extend(list(out["train_preds_raw_step"]))
            labels.extend(list(out["train_labels_step"]))
            loss += out["loss"] / len(outputs)
        train_score = self.scorer(labels, preds)
        self.log("train_score", train_score, on_step=False, on_epoch=True)
        self.log("train_loss", loss, on_step=False, on_epoch=True)

    def on_validation_epoch_end(self, outputs):
        # outputs from all valid steps
        preds = []
        labels = []
        loss = 0.0
        for out in outputs:
            preds.extend(list(out["valid_preds_step"]))
            labels.extend(list(out["valid_preds_raw_step"]))
            loss += out["valid_loss_step"] / len(outputs)
        valid_score = self.scorer(labels, preds)
        self.log("valid_score", valid_score, on_step=False, on_epoch=True)
        self.log("valid_loss", loss, on_step=False, on_epoch=True)

    def scorer(self, y_true, y_pred):
        return roc_auc_score(y_true, y_pred)

    def configure_optimizers(self):
        params = self.model.parameters()
        optimizer = torch.optim.Adam(params=params, lr=self.lr, weight_decay=self.wd)
        lr_scheduler = None
        """
        {
            "scheduler": torch.optim.lr_scheduler.ReduceLROnPlateau(
                optimizer, patience=self.patience, verbose=self.verbose
            ),
            "monitor": "valid_loss",
            "interval": "epoch",  # for ReduceLROnPlateau
        }
        """
        return (
            {"optimizer": optimizer, "lr_scheduler": lr_scheduler}
            if lr_scheduler is not None
            else optimizer
        )
