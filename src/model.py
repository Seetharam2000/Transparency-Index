import os
import pandas as pd
import torch
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
from transformers import Trainer, TrainingArguments
from torch.utils.data import Dataset
from sklearn.model_selection import train_test_split
from typing import List, Dict, Tuple
import numpy as np


class DarkPatternDataset(Dataset):
    """PyTorch Dataset for dark pattern classification."""
    
    def __init__(self, texts, labels, tokenizer, max_length=128):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]
        
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }


class DarkPatternClassifier:
    """
    DistilBERT-based classifier for dark pattern detection.
    Classes: none, fee_obfuscation, false_urgency, hard_cancellation, misleading_rate
    """
    
    LABEL_MAP = {
        'none': 0,
        'fee_obfuscation': 1,
        'false_urgency': 2,
        'hard_cancellation': 3,
        'misleading_rate': 4
    }
    
    LABEL_NAMES = ['none', 'fee_obfuscation', 'false_urgency', 'hard_cancellation', 'misleading_rate']
    
    def __init__(self, model_path: str = None):
        self.model_path = model_path or 'models/distilbert_darkpattern'
        self.tokenizer = None
        self.model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    def train(self, csv_path: str, epochs: int = 3, batch_size: int = 8):
        """
        Train the model on a labeled CSV dataset.
        CSV should have columns: 'text', 'label'
        """
        print(f"Loading data from {csv_path}...")
        df = pd.read_csv(csv_path)
        
        # Map labels to integers
        df['label_id'] = df['label'].map(self.LABEL_MAP)
        df = df.dropna(subset=['label_id'])
        
        # Split into train and validation
        train_texts, val_texts, train_labels, val_labels = train_test_split(
            df['text'].tolist(),
            df['label_id'].tolist(),
            test_size=0.2,
            random_state=42,
            stratify=df['label_id']
        )
        
        # Initialize tokenizer
        print("Initializing tokenizer...")
        self.tokenizer = DistilBertTokenizerFast.from_pretrained('distilbert-base-uncased')
        
        # Create datasets
        train_dataset = DarkPatternDataset(train_texts, train_labels, self.tokenizer)
        val_dataset = DarkPatternDataset(val_texts, val_labels, self.tokenizer)
        
        # Initialize model
        print("Initializing model...")
        self.model = DistilBertForSequenceClassification.from_pretrained(
            'distilbert-base-uncased',
            num_labels=len(self.LABEL_MAP)
        )
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=self.model_path,
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            warmup_steps=500,
            weight_decay=0.01,
            logging_dir=f'{self.model_path}/logs',
            logging_steps=10,
            evaluation_strategy='epoch',
            save_strategy='epoch',
            load_best_model_at_end=True,
            metric_for_best_model='eval_loss',
            greater_is_better=False,
            no_cuda=not torch.cuda.is_available()
        )
        
        # Initialize trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset
        )
        
        # Train
        print("Starting training...")
        trainer.train()
        
        # Save model and tokenizer
        print(f"Saving model to {self.model_path}...")
        trainer.save_model(self.model_path)
        self.tokenizer.save_pretrained(self.model_path)
        
        print("Training complete!")
    
    def load_model(self):
        """Load a trained model from disk."""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model not found at {self.model_path}. Train first or provide correct path.")
        
        print(f"Loading model from {self.model_path}...")
        self.tokenizer = DistilBertTokenizerFast.from_pretrained(self.model_path)
        self.model = DistilBertForSequenceClassification.from_pretrained(self.model_path)
        self.model.to(self.device)
        self.model.eval()
        print("Model loaded!")
    
    def predict(self, clauses: List[str]) -> List[Dict]:
        """
        Predict dark pattern labels for a list of text clauses.
        Returns list of dicts with label, confidence, and original text.
        """
        if self.model is None or self.tokenizer is None:
            self.load_model()
        
        results = []
        
        for clause in clauses:
            # Tokenize
            inputs = self.tokenizer(
                clause,
                truncation=True,
                padding=True,
                max_length=128,
                return_tensors='pt'
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Predict
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probs = torch.softmax(logits, dim=-1)
                confidence, predicted = torch.max(probs, dim=-1)
            
            label_name = self.LABEL_NAMES[predicted.item()]
            confidence_score = confidence.item()
            
            results.append({
                'text': clause,
                'label': label_name,
                'confidence': confidence_score
            })
        
        return results
    
    def predict_batch(self, clauses: List[str]) -> List[Dict]:
        """Batch prediction for better performance."""
        if self.model is None or self.tokenizer is None:
            self.load_model()
        
        if not clauses:
            return []
        
        # Tokenize all at once
        inputs = self.tokenizer(
            clauses,
            truncation=True,
            padding=True,
            max_length=128,
            return_tensors='pt'
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Predict
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=-1)
            confidences, predicted = torch.max(probs, dim=-1)
        
        results = []
        for i, clause in enumerate(clauses):
            label_name = self.LABEL_NAMES[predicted[i].item()]
            confidence_score = confidences[i].item()
            results.append({
                'text': clause,
                'label': label_name,
                'confidence': confidence_score
            })
        
        return results


if __name__ == "__main__":
    # Test the classifier
    classifier = DarkPatternClassifier()
    
    # Try to load existing model, or print message to train first
    try:
        classifier.load_model()
        test_clauses = [
            "Interest rate is 15% APR clearly stated.",
            "Fees as applicable may be charged to your account.",
            "Act now limited time offer expires today.",
            "To cancel you must send written notice to head office."
        ]
        predictions = classifier.predict(test_clauses)
        for pred in predictions:
            print(f"Text: {pred['text'][:50]}...")
            print(f"Label: {pred['label']}, Confidence: {pred['confidence']:.2f}\n")
    except FileNotFoundError:
        print("No trained model found. Train first using classifier.train('data/labeled/darkpatterns.csv')")
