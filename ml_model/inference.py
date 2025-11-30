"""
Inference module for trained plant disease detection model
Replaces API calls with local model predictions
"""
import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
import json
from pathlib import Path
from typing import Dict, Tuple, List
import numpy as np


class PlantDiseaseInference:
    """Inference wrapper for plant disease detection model"""
    
    def __init__(self, model_path: str, class_mapping_path: str = None):
        """
        Initialize inference module
        
        Args:
            model_path: Path to trained model checkpoint (.pth file)
            class_mapping_path: Path to class mapping JSON file
        """
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Load class mapping
        if class_mapping_path is None:
            class_mapping_path = Path(model_path).parent / 'class_mapping.json'
        
        with open(class_mapping_path, 'r') as f:
            mapping = json.load(f)
            self.classes = mapping['classes']
            self.class_to_idx = mapping['class_to_idx']
            self.idx_to_class = {v: k for k, v in self.class_to_idx.items()}
        
        # Load model
        self.model = self._load_model(model_path, len(self.classes))
        self.model.eval()
        
        # Setup transforms
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
        
        print(f"✅ Model loaded successfully on {self.device}")
        print(f"📊 Trained on {len(self.classes)} disease classes")
    
    def _load_model(self, model_path: str, num_classes: int):
        """Load trained model from checkpoint"""
        # Create model architecture
        model = models.resnet50(pretrained=False)
        num_features = model.fc.in_features
        model.fc = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(num_features, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, num_classes)
        )
        
        # Load weights
        checkpoint = torch.load(model_path, map_location=self.device)
        model.load_state_dict(checkpoint['model_state_dict'])
        model = model.to(self.device)
        
        return model
    
    def predict(self, image_path: str, top_k: int = 3) -> Dict:
        """
        Predict disease from plant image
        
        Args:
            image_path: Path to plant image
            top_k: Number of top predictions to return
            
        Returns:
            Dictionary with prediction results
        """
        # Load and preprocess image
        image = Image.open(image_path).convert('RGB')
        original_size = image.size
        image_tensor = self.transform(image).unsqueeze(0).to(self.device)
        
        # Predict
        with torch.no_grad():
            outputs = self.model(image_tensor)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            top_probs, top_indices = torch.topk(probabilities, top_k)
        
        # Format results
        predictions = []
        for prob, idx in zip(top_probs[0], top_indices[0]):
            class_name = self.idx_to_class[idx.item()]
            disease_info = self._parse_class_name(class_name)
            
            predictions.append({
                'disease': disease_info['disease'],
                'plant': disease_info['plant'],
                'confidence': float(prob.item()),
                'confidence_percent': f"{prob.item() * 100:.2f}%"
            })
        
        # Primary prediction
        primary = predictions[0]
        
        return {
            'primary_prediction': {
                'plant': primary['plant'],
                'disease': primary['disease'],
                'confidence': primary['confidence'],
                'severity': self._estimate_severity(primary['confidence'])
            },
            'alternative_predictions': predictions[1:],
            'all_predictions': predictions,
            'model_info': {
                'device': str(self.device),
                'num_classes': len(self.classes),
                'image_size': original_size
            }
        }
    
    def _parse_class_name(self, class_name: str) -> Dict[str, str]:
        """
        Parse class name into plant and disease
        Format: "Plant___Disease" (e.g., "Tomato___Early_Blight")
        """
        parts = class_name.split('___')
        if len(parts) == 2:
            plant = parts[0].replace('_', ' ')
            disease = parts[1].replace('_', ' ')
        else:
            plant = class_name.replace('_', ' ')
            disease = "Unknown"
        
        return {
            'plant': plant,
            'disease': disease,
            'full_name': class_name
        }
    
    def _estimate_severity(self, confidence: float) -> str:
        """Estimate disease severity based on confidence"""
        if confidence > 0.9:
            return "High confidence detection - Immediate action recommended"
        elif confidence > 0.7:
            return "Moderate confidence - Monitor closely"
        else:
            return "Low confidence - Consider consulting expert"
    
    def get_disease_description(self, disease_name: str) -> Dict[str, str]:
        """
        Get detailed description of disease
        This is a basic implementation - can be enhanced with a knowledge base
        """
        # Load disease knowledge base
        knowledge_base_path = Path(__file__).parent / 'disease_knowledge.json'
        
        if knowledge_base_path.exists():
            with open(knowledge_base_path, 'r') as f:
                knowledge = json.load(f)
                return knowledge.get(disease_name, {
                    'name': disease_name,
                    'description': 'Description not available',
                    'treatment': 'Consult agricultural expert',
                    'prevention': 'Follow general plant health practices'
                })
        
        return {
            'name': disease_name,
            'description': 'Description not available',
            'treatment': 'Consult agricultural expert',
            'prevention': 'Follow general plant health practices'
        }
    
    def batch_predict(self, image_paths: List[str], top_k: int = 3) -> List[Dict]:
        """
        Predict diseases for multiple images
        
        Args:
            image_paths: List of image paths
            top_k: Number of top predictions per image
            
        Returns:
            List of prediction dictionaries
        """
        results = []
        for image_path in image_paths:
            try:
                result = self.predict(image_path, top_k)
                result['image_path'] = image_path
                result['status'] = 'success'
                results.append(result)
            except Exception as e:
                results.append({
                    'image_path': image_path,
                    'status': 'error',
                    'error': str(e)
                })
        
        return results


# Singleton instance for reuse
_inference_instance = None


def get_inference_model(model_path: str = None) -> PlantDiseaseInference:
    """
    Get or create inference model instance (singleton pattern)
    
    Args:
        model_path: Path to model checkpoint. If None, uses default path.
    
    Returns:
        PlantDiseaseInference instance
    """
    global _inference_instance
    
    if _inference_instance is None:
        if model_path is None:
            # Default model path
            model_path = Path(__file__).parent / 'checkpoints' / 'best_model.pth'
        
        if not Path(model_path).exists():
            raise FileNotFoundError(
                f"Model not found at {model_path}. "
                "Please train the model first using train_model.py or download a pre-trained model."
            )
        
        _inference_instance = PlantDiseaseInference(model_path)
    
    return _inference_instance


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Test plant disease inference')
    parser.add_argument('--image', type=str, required=True,
                       help='Path to plant image')
    parser.add_argument('--model', type=str, 
                       default='ml_model/checkpoints/best_model.pth',
                       help='Path to model checkpoint')
    parser.add_argument('--top-k', type=int, default=3,
                       help='Number of top predictions to show')
    
    args = parser.parse_args()
    
    # Load model and predict
    model = get_inference_model(args.model)
    result = model.predict(args.image, args.top_k)
    
    # Print results
    print("\n" + "="*50)
    print("Plant Disease Detection Results")
    print("="*50)
    
    primary = result['primary_prediction']
    print(f"\n🌱 Plant: {primary['plant']}")
    print(f"🦠 Disease: {primary['disease']}")
    print(f"📊 Confidence: {primary['confidence']*100:.2f}%")
    print(f"⚠️  Severity: {primary['severity']}")
    
    if result['alternative_predictions']:
        print(f"\n📋 Alternative possibilities:")
        for i, pred in enumerate(result['alternative_predictions'], 1):
            print(f"  {i}. {pred['plant']} - {pred['disease']} ({pred['confidence_percent']})")
