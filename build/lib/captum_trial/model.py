# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/01_model.ipynb.

# %% auto 0
__all__ = ['ConvBnRelu', 'ConvNet']

# %% ../nbs/01_model.ipynb 2
import torch
from torch import nn
import torch.nn.functional as F

from typing import Any, Union, Tuple

import pytorch_lightning as pl

# %% ../nbs/01_model.ipynb 3
_size_2_t = Union[int, Tuple[int, int]]

# %% ../nbs/01_model.ipynb 5
class ConvBnRelu(nn.Module):
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: _size_2_t,
        stride: _size_2_t = 1,
        padding: _size_2_t | str = 0,
        dilation: _size_2_t = 1,
        groups: int = 1,
        bias: bool = True,
        padding_mode: str = "zeros",
        device: Any | None = None,
        dtype: Any | None = None,
        eps: float = 0.00001,
        momentum: float = 0.1,
        affine: bool = True,
        track_running_stats: bool = True,
    ):
        super(ConvBnRelu, self).__init__()
        self.conv = nn.Conv2d(
            in_channels=in_channels,
            out_channels=out_channels,
            kernel_size=kernel_size,
            stride=stride,
            padding=padding,
            dilation=dilation,
            groups=groups,
            bias=bias,
            padding_mode=padding_mode,
            device=device,
            dtype=dtype,
        )
        self.bn = nn.BatchNorm2d(
            num_features=out_channels,
            eps=eps,
            momentum=momentum,
            affine=affine,
            track_running_stats=track_running_stats,
            device=device,
            dtype=dtype,
        )

    def forward(self, x):
        x = self.conv(x)
        x = self.bn(x)
        return F.relu(x)

# %% ../nbs/01_model.ipynb 7
class ConvNet(nn.Module):
    def __init__(self, n_cls:int):
        super(ConvNet, self).__init__()
        self.conv1 = ConvBnRelu(3, 16, 3) 
        self.drop1 = nn.Dropout2d(p=0.2)
        self.conv2 = ConvBnRelu(16, 32, 3)
        self.drop2 = nn.Dropout2d(p=0.2)
        self.flat = nn.Flatten()
        self.linear = nn.LazyLinear(out_features=n_cls)
    def forward(self, x):
        x = self.drop1(self.conv1(x))
        x = self.drop2(self.conv2(x)) 
        x = self.flat(x)
        return self.linear(x)
