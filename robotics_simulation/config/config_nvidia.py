from config.config_vars import config
import torch
import os

os.environ["LD_LIBRARY_PATH"] = f"{config.CUDNN_LIBRARY_PATH}:{os.environ.get('LD_LIBRARY_PATH', '')}"
torch.backends.cudnn.enabled = config.CUDNN_ENABLED
torch.backends.cudnn.benchmark = config.CUDNN_BENCHMARK
torch.backends.cudnn.deterministic = config.CUDNN_DETERMINISTIC