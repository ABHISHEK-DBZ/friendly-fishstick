"""
Download pre-trained plant disease detection model
"""
import requests
from pathlib import Path
from tqdm import tqdm
import json


def download_file(url: str, destination: Path):
    """Download file with progress bar"""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(destination, 'wb') as f, tqdm(
        desc=destination.name,
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as pbar:
        for data in response.iter_content(chunk_size=1024):
            size = f.write(data)
            pbar.update(size)


def main():
    """Download pre-trained model and class mapping"""
    
    # Create checkpoints directory
    checkpoint_dir = Path(__file__).parent / "checkpoints"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    
    print("🔽 Downloading pre-trained plant disease detection model...")
    print("📦 Model size: ~90MB")
    print()
    
    # Model URL (replace with actual hosted model URL)
    # For now, providing instructions
    model_url = "https://huggingface.co/YOUR_USERNAME/plant-disease-resnet50/resolve/main/best_model.pth"
    mapping_url = "https://huggingface.co/YOUR_USERNAME/plant-disease-resnet50/resolve/main/class_mapping.json"
    
    # Note: You need to upload your trained model to HuggingFace or Google Drive first
    print("⚠️  Model download not yet configured!")
    print()
    print("To use pre-trained model:")
    print("1. Train your own model: python ml_model/train_model.py")
    print("2. Or download from: [Add your model hosting URL]")
    print("3. Place in: ml_model/checkpoints/best_model.pth")
    print()
    print("Alternative: Use PlantVillage pre-trained weights:")
    print("   Download from: https://github.com/spMohanty/PlantVillage-Dataset")
    
    # Create sample class mapping for reference
    sample_mapping = {
        "classes": [
            "Apple___Apple_scab", "Apple___Black_rot", "Apple___Cedar_apple_rust", 
            "Apple___healthy", "Corn___Cercospora_leaf_spot Gray_leaf_spot",
            "Corn___Common_rust", "Corn___Northern_Leaf_Blight", "Corn___healthy",
            "Grape___Black_rot", "Grape___Esca_(Black_Measles)", "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
            "Grape___healthy", "Potato___Early_blight", "Potato___Late_blight", "Potato___healthy",
            "Tomato___Bacterial_spot", "Tomato___Early_blight", "Tomato___Late_blight",
            "Tomato___Leaf_Mold", "Tomato___Septoria_leaf_spot", "Tomato___Spider_mites Two-spotted_spider_mite",
            "Tomato___Target_Spot", "Tomato___Tomato_Yellow_Leaf_Curl_Virus", "Tomato___Tomato_mosaic_virus",
            "Tomato___healthy"
        ],
        "class_to_idx": {}
    }
    
    # Generate class to index mapping
    sample_mapping["class_to_idx"] = {
        cls: idx for idx, cls in enumerate(sample_mapping["classes"])
    }
    
    # Save sample mapping
    mapping_file = checkpoint_dir / "class_mapping_sample.json"
    with open(mapping_file, 'w') as f:
        json.dump(sample_mapping, f, indent=2)
    
    print(f"✅ Sample class mapping saved to: {mapping_file}")


if __name__ == '__main__':
    main()
