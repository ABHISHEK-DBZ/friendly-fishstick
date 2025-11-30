"""
Quick test of inference pipeline without training
Uses pre-trained ResNet50 from ImageNet
"""
import torch
import torchvision.models as models
from torchvision import transforms
from PIL import Image
import time

print("🔬 Testing ML Model Inference Pipeline")
print("=" * 50)

# Load pre-trained ResNet50
print("\n1. Loading pre-trained ResNet50...")
model = models.resnet50(pretrained=True)
model.eval()
print("   ✅ Model loaded (25M parameters)")

# Setup transforms
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                       std=[0.229, 0.224, 0.225])
])

print("\n2. Creating test image...")
# Create a dummy image (3x224x224)
test_image = Image.new('RGB', (224, 224), color='green')
print("   ✅ Test image created (224x224)")

print("\n3. Running inference...")
start_time = time.time()

with torch.no_grad():
    # Transform image
    input_tensor = transform(test_image).unsqueeze(0)
    
    # Inference
    outputs = model(input_tensor)
    probabilities = torch.nn.functional.softmax(outputs, dim=1)
    top_prob, top_idx = torch.max(probabilities, 1)

inference_time = time.time() - start_time

print(f"   ✅ Inference complete!")
print(f"   ⏱️  Time: {inference_time*1000:.1f}ms")
print(f"   📊 Output shape: {outputs.shape}")
print(f"   🎯 Top prediction index: {top_idx.item()}")
print(f"   📈 Confidence: {top_prob.item()*100:.2f}%")

print("\n" + "=" * 50)
print("✅ ML Pipeline Working!")
print(f"💡 Expected inference time: {inference_time*1000:.0f}ms per image")
print("💡 Ready for plant disease model training")
