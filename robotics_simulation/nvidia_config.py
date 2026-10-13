import os

venv_cudnn_path = "/home/ubuntu/repository/physical-ai-control/venv/lib/python3.12/site-packages/nvidia/cudnn/lib"
os.environ["LD_LIBRARY_PATH"] = f"{venv_cudnn_path}:{os.environ.get('LD_LIBRARY_PATH', '')}"
try:
    import torch
    torch.backends.cudnn.enabled = False
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
except ImportError:
    pass