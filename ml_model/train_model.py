"""
Plant Disease Detection Model Training Script
Uses CNN architecture trained on PlantVillage dataset
"""
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms, models
from pathlib import Path
import json
from PIL import Image
from tqdm import tqdm
import os


class PlantDiseaseDataset(Dataset):
    """Dataset loader for plant disease images"""
    
    def __init__(self, root_dir, transform=None):
        self.root_dir = Path(root_dir)
        self.transform = transform
        self.classes = sorted([d.name for d in self.root_dir.iterdir() if d.is_dir()])
        self.class_to_idx = {cls_name: i for i, cls_name in enumerate(self.classes)}
        
        # Load all image paths and labels
        self.samples = []
        for class_name in self.classes:
            class_dir = self.root_dir / class_name
            for img_path in class_dir.glob('*.jpg'):
                self.samples.append((img_path, self.class_to_idx[class_name]))
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        img_path, label = self.samples[idx]
        image = Image.open(img_path).convert('RGB')
        
        if self.transform:
            image = self.transform(image)
        
        return image, label


class PlantDiseaseModel(nn.Module):
    """CNN model for plant disease classification"""
    
    def __init__(self, num_classes, pretrained=True):
        super(PlantDiseaseModel, self).__init__()
        
        # Use ResNet50 as backbone
        self.backbone = models.resnet50(pretrained=pretrained)
        
        # Replace final layer for our number of classes
        num_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(num_features, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, num_classes)
        )
    
    def forward(self, x):
        return self.backbone(x)


def get_transforms():
    """Get data augmentation transforms"""
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                           std=[0.229, 0.224, 0.225])
    ])
    
    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                           std=[0.229, 0.224, 0.225])
    ])
    
    return train_transform, val_transform


def train_model(
    train_dir: str,
    val_dir: str,
    output_dir: str = "ml_model/checkpoints",
    num_epochs: int = 50,
    batch_size: int = 32,
    learning_rate: float = 0.001
):
    """
    Train plant disease detection model
    
    Args:
        train_dir: Path to training data directory
        val_dir: Path to validation data directory
        output_dir: Directory to save model checkpoints
        num_epochs: Number of training epochs
        batch_size: Batch size for training
        learning_rate: Learning rate for optimizer
    """
    # Setup device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Load datasets
    train_transform, val_transform = get_transforms()
    train_dataset = PlantDiseaseDataset(train_dir, transform=train_transform)
    val_dataset = PlantDiseaseDataset(val_dir, transform=val_transform)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, 
                             shuffle=True, num_workers=4)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, 
                           shuffle=False, num_workers=4)
    
    # Save class mapping
    class_mapping = {
        'classes': train_dataset.classes,
        'class_to_idx': train_dataset.class_to_idx
    }
    with open(output_path / 'class_mapping.json', 'w') as f:
        json.dump(class_mapping, f, indent=2)
    
    print(f"Training on {len(train_dataset)} images")
    print(f"Validating on {len(val_dataset)} images")
    print(f"Number of classes: {len(train_dataset.classes)}")
    
    # Initialize model
    model = PlantDiseaseModel(num_classes=len(train_dataset.classes))
    model = model.to(device)
    
    # Loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='max', factor=0.5, patience=5, verbose=True
    )
    
    # Training loop
    best_accuracy = 0.0
    
    for epoch in range(num_epochs):
        print(f"\nEpoch {epoch+1}/{num_epochs}")
        print("-" * 50)
        
        # Training phase
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0
        
        train_pbar = tqdm(train_loader, desc="Training")
        for images, labels in train_pbar:
            images, labels = images.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            _, predicted = outputs.max(1)
            train_total += labels.size(0)
            train_correct += predicted.eq(labels).sum().item()
            
            train_pbar.set_postfix({
                'loss': f'{train_loss/train_total:.4f}',
                'acc': f'{100.*train_correct/train_total:.2f}%'
            })
        
        train_accuracy = 100. * train_correct / train_total
        
        # Validation phase
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        
        with torch.no_grad():
            val_pbar = tqdm(val_loader, desc="Validation")
            for images, labels in val_pbar:
                images, labels = images.to(device), labels.to(device)
                
                outputs = model(images)
                loss = criterion(outputs, labels)
                
                val_loss += loss.item()
                _, predicted = outputs.max(1)
                val_total += labels.size(0)
                val_correct += predicted.eq(labels).sum().item()
                
                val_pbar.set_postfix({
                    'loss': f'{val_loss/val_total:.4f}',
                    'acc': f'{100.*val_correct/val_total:.2f}%'
                })
        
        val_accuracy = 100. * val_correct / val_total
        
        print(f"\nTrain Loss: {train_loss/train_total:.4f} | Train Acc: {train_accuracy:.2f}%")
        print(f"Val Loss: {val_loss/val_total:.4f} | Val Acc: {val_accuracy:.2f}%")
        
        # Learning rate scheduling
        scheduler.step(val_accuracy)
        
        # Save best model
        if val_accuracy > best_accuracy:
            best_accuracy = val_accuracy
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'accuracy': val_accuracy,
                'classes': train_dataset.classes
            }, output_path / 'best_model.pth')
            print(f"✅ Saved best model with accuracy: {val_accuracy:.2f}%")
        
        # Save checkpoint every 5 epochs
        if (epoch + 1) % 5 == 0:
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'accuracy': val_accuracy,
            }, output_path / f'checkpoint_epoch_{epoch+1}.pth')
    
    print(f"\n🎉 Training complete! Best validation accuracy: {best_accuracy:.2f}%")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Train plant disease detection model')
    parser.add_argument('--train-dir', type=str, required=True,
                       help='Path to training data directory')
    parser.add_argument('--val-dir', type=str, required=True,
                       help='Path to validation data directory')
    parser.add_argument('--output-dir', type=str, default='ml_model/checkpoints',
                       help='Directory to save model checkpoints')
    parser.add_argument('--epochs', type=int, default=50,
                       help='Number of training epochs')
    parser.add_argument('--batch-size', type=int, default=32,
                       help='Batch size for training')
    parser.add_argument('--lr', type=float, default=0.001,
                       help='Learning rate')
    
    args = parser.parse_args()
    
    train_model(
        train_dir=args.train_dir,
        val_dir=args.val_dir,
        output_dir=args.output_dir,
        num_epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr
    )
