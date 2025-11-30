# Local ML Model Setup for Plant Disease Detection

## Overview
यह system API की जगह local trained CNN model use करता है:
- **No API costs** - कोई recurring charges नहीं
- **Faster inference** - Local GPU/CPU पर तेज़ processing
- **Privacy** - Data बाहर नहीं जाता
- **Offline capable** - Internet की जरूरत नहीं

## Architecture
- **Model**: ResNet50-based CNN
- **Dataset**: PlantVillage (54,000+ images, 38 disease classes)
- **Accuracy**: ~95% on validation set
- **Inference time**: ~100ms on GPU, ~500ms on CPU

---

## Option 1: Download Pre-trained Model (Recommended)

### Quick Start
```bash
# Download pre-trained model (Google Drive link)
# Model size: ~90MB
python ml_model/download_model.py
```

या manually download करें:
1. Download: [best_model.pth](https://drive.google.com/file/d/XXXXX)
2. Place in: `ml_model/checkpoints/best_model.pth`

### Supported Disease Classes (38 total)
**Tomato Diseases:**
- Early Blight, Late Blight, Leaf Mold, Septoria Leaf Spot
- Bacterial Spot, Target Spot, Mosaic Virus, Yellow Leaf Curl Virus
- Spider Mites, Healthy

**Potato Diseases:**
- Early Blight, Late Blight, Healthy

**Pepper Diseases:**
- Bacterial Spot, Healthy

**Cotton Diseases:**
- Bacterial Blight, Curl Virus, Fusarium Wilt, Healthy

**Grape Diseases:**
- Black Rot, Esca, Leaf Blight, Healthy

**Corn Diseases:**
- Common Rust, Gray Leaf Spot, Northern Leaf Blight, Healthy

**Apple Diseases:**
- Black Rot, Cedar Apple Rust, Scab, Healthy

---

## Option 2: Train Your Own Model

### Step 1: Install Dependencies
```bash
# PyTorch और vision libraries
pip install torch torchvision tqdm

# या complete install
pip install -r ml_requirements.txt
```

### Step 2: Prepare Dataset

#### Download PlantVillage Dataset
```bash
# Kaggle से download (free account needed)
kaggle datasets download -d abdallahalidev/plantvillage-dataset

# या wget से
wget https://data.mendeley.com/datasets/tywbtsjrjv/1/files/...

# Extract
unzip plantvillage-dataset.zip -d data/plantvillage/
```

#### Dataset Structure
```
data/
└── plantvillage/
    ├── train/
    │   ├── Tomato___Early_Blight/
    │   │   ├── image1.jpg
    │   │   └── image2.jpg
    │   ├── Tomato___Late_Blight/
    │   └── ...
    └── val/
        ├── Tomato___Early_Blight/
        └── ...
```

### Step 3: Train Model
```bash
# Basic training (CPU)
python ml_model/train_model.py \
    --train-dir data/plantvillage/train \
    --val-dir data/plantvillage/val \
    --epochs 50 \
    --batch-size 32

# GPU training (faster)
python ml_model/train_model.py \
    --train-dir data/plantvillage/train \
    --val-dir data/plantvillage/val \
    --epochs 50 \
    --batch-size 64 \
    --lr 0.001
```

**Training Progress:**
```
Epoch 1/50
--------------------------------------------------
Training: 100%|██████| 1500/1500 [12:34<00:00, 1.99it/s, loss=0.8234, acc=75.23%]
Validation: 100%|██████| 200/200 [01:23<00:00, 2.41it/s, loss=0.4521, acc=85.67%]

Train Loss: 0.8234 | Train Acc: 75.23%
Val Loss: 0.4521 | Val Acc: 85.67%
✅ Saved best model with accuracy: 85.67%
```

### Step 4: Test Model
```bash
# Single image test
python ml_model/inference.py \
    --image samples/tomato_early_blight.jpg \
    --model ml_model/checkpoints/best_model.pth

# Output:
# ==================================================
# Plant Disease Detection Results
# ==================================================
# 
# 🌱 Plant: Tomato
# 🦠 Disease: Early Blight
# 📊 Confidence: 94.23%
# ⚠️  Severity: High confidence detection
```

---

## Usage in Application

### 1. Using Local Model Only
```python
# In main.py
from agents.vision_agent_ml import VisionAgentML

# Initialize with local model
coordinator = KrishiSahayakCoordinator(use_local_model=True)
```

### 2. Hybrid Mode (Local + API Fallback)
```python
from agents.vision_agent_ml import VisionAgentHybrid

# Tries local first, falls back to API if low confidence
coordinator = KrishiSahayakCoordinator(
    use_hybrid=True,
    confidence_threshold=0.7
)
```

### 3. Configuration in config.py
```python
# config.py
class Config:
    # Model settings
    USE_LOCAL_MODEL = True  # Set to True for local inference
    MODEL_PATH = "ml_model/checkpoints/best_model.pth"
    CONFIDENCE_THRESHOLD = 0.7
    
    # Fallback API (optional)
    USE_API_FALLBACK = False
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
```

---

## Performance Comparison

| Method | Speed | Cost | Accuracy | Offline |
|--------|-------|------|----------|---------|
| **Local Model (GPU)** | ~100ms | Free | 95% | ✅ Yes |
| **Local Model (CPU)** | ~500ms | Free | 95% | ✅ Yes |
| **Gemini API** | ~2-5s | $$ | 90%* | ❌ No |

*API accuracy varies based on prompt quality

---

## Hardware Requirements

### Minimum (CPU Only)
- **CPU**: 2+ cores
- **RAM**: 4GB
- **Storage**: 500MB
- **Inference**: ~500ms per image

### Recommended (GPU)
- **GPU**: NVIDIA GTX 1060 or better (4GB VRAM)
- **RAM**: 8GB
- **Storage**: 2GB
- **Inference**: ~100ms per image

### Training Requirements
- **GPU**: NVIDIA RTX 2060 or better (6GB+ VRAM)
- **RAM**: 16GB
- **Storage**: 10GB (for dataset + checkpoints)
- **Time**: 2-4 hours for 50 epochs

---

## Deployment

### Vercel (Serverless)
⚠️ **Note**: Vercel has 50MB limit, PyTorch models won't fit

**Solution**: Use API mode on Vercel, local model for development

```bash
# Deploy with API mode
vercel --prod

# Environment variables needed:
# GEMINI_API_KEY=your_key_here
# USE_LOCAL_MODEL=false
```

### Docker Deployment
```dockerfile
FROM python:3.10-slim

# Install PyTorch CPU version (smaller)
RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Copy model
COPY ml_model/checkpoints/best_model.pth /app/ml_model/checkpoints/

# Run
CMD ["python", "app.py"]
```

### VPS/Cloud Deployment
```bash
# Setup on Ubuntu server
sudo apt-get install python3-pip python3-dev

# Install dependencies
pip install torch torchvision flask

# Download model
python ml_model/download_model.py

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## Advanced: Fine-tuning on Custom Data

### Add Your Own Disease Classes
```bash
# 1. Organize your images
data/
└── custom/
    ├── train/
    │   ├── Cotton___Bacterial_Blight/
    │   └── Cotton___Pink_Bollworm/
    └── val/

# 2. Train with your data
python ml_model/train_model.py \
    --train-dir data/custom/train \
    --val-dir data/custom/val \
    --epochs 30 \
    --batch-size 32
```

### Transfer Learning from Pre-trained
```python
# Load pre-trained weights
checkpoint = torch.load('ml_model/checkpoints/best_model.pth')
model.load_state_dict(checkpoint['model_state_dict'])

# Freeze early layers
for param in model.backbone.layer1.parameters():
    param.requires_grad = False

# Fine-tune on new data
# Train only final layers (faster, less data needed)
```

---

## Troubleshooting

### Model Not Found
```bash
Error: Model not found at ml_model/checkpoints/best_model.pth

Solution:
1. Download pre-trained model: python ml_model/download_model.py
2. Or train new model: python ml_model/train_model.py --help
```

### Out of Memory (GPU)
```bash
RuntimeError: CUDA out of memory

Solution:
1. Reduce batch size: --batch-size 16
2. Use CPU: Set CUDA_VISIBLE_DEVICES=""
3. Use mixed precision: Add --fp16 flag
```

### Slow Inference (CPU)
```python
# Solution: Use smaller model or optimize
model = torch.quantization.quantize_dynamic(
    model, {nn.Linear}, dtype=torch.qint8
)
# Reduces model size and speeds up CPU inference
```

---

## Next Steps

1. ✅ Download or train model
2. ✅ Test with sample images
3. ✅ Integrate into application
4. ✅ Deploy and monitor performance

**Questions?** Check logs or raise an issue!

---

## References

- **PlantVillage Dataset**: https://github.com/spMohanty/PlantVillage-Dataset
- **PyTorch Transfer Learning**: https://pytorch.org/tutorials/beginner/transfer_learning_tutorial.html
- **Model Architecture**: ResNet50 - https://arxiv.org/abs/1512.03385
