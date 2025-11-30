import torch
import torchvision

print("✅ PyTorch installed successfully!")
print(f"PyTorch version: {torch.__version__}")
print(f"Torchvision version: {torchvision.__version__}")
print(f"Device: {'GPU (CUDA)' if torch.cuda.is_available() else 'CPU'}")
print(f"Number of CPU cores: {torch.get_num_threads()}")
