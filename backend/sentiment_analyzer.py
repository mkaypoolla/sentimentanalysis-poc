from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch
import numpy as np
from typing import Dict, List
import re

class SentimentAnalyzer:
    def __init__(self, model_name: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"):
        """
        Initialize the sentiment analyzer with a pre-trained model.
        Default model is optimized for Twitter sentiment analysis.
        """
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.sentiment_pipeline = None
        self.load_model()
    
    def load_model(self):
        """Load the sentiment analysis model and tokenizer."""
        try:
            print(f"Loading sentiment analysis model: {self.model_name}")
            
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            
            # Create pipeline for easier inference
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if torch.cuda.is_available() else -1
            )
            
            print("Sentiment analysis model loaded successfully")
            
        except Exception as e:
            print(f"Error loading model {self.model_name}: {e}")
            print("Falling back to VADER sentiment analyzer")
            self.load_vader_fallback()
    
    def load_vader_fallback(self):
        """Load VADER sentiment analyzer as fallback."""
        try:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            self.vader_analyzer = SentimentIntensityAnalyzer()
            self.sentiment_pipeline = None
            print("VADER sentiment analyzer loaded as fallback")
        except ImportError:
            print("VADER not available, using simple rule-based sentiment")
            self.vader_analyzer = None
            self.sentiment_pipeline = None
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text for sentiment analysis."""
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove user mentions
        text = re.sub(r'@\w+', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Limit length for model input
        if len(text) > 512:
            text = text[:512]
        
        return text.strip()
    
    def analyze_sentiment_transformers(self, text: str) -> Dict:
        """Analyze sentiment using Hugging Face transformers."""
        try:
            preprocessed_text = self.preprocess_text(text)
            
            if not preprocessed_text:
                return self.get_neutral_sentiment()
            
            # Get prediction
            result = self.sentiment_pipeline(preprocessed_text)[0]
            
            # Map labels to standard format
            label_mapping = {
                'LABEL_0': 'negative',
                'LABEL_1': 'neutral', 
                'LABEL_2': 'positive',
                'NEGATIVE': 'negative',
                'NEUTRAL': 'neutral',
                'POSITIVE': 'positive'
            }
            
            sentiment = label_mapping.get(result['label'].upper(), result['label'].lower())
            confidence = result['score']
            
            # Create score distribution (simplified)
            if sentiment == 'positive':
                positive_score = confidence
                negative_score = (1 - confidence) / 2
                neutral_score = (1 - confidence) / 2
            elif sentiment == 'negative':
                negative_score = confidence
                positive_score = (1 - confidence) / 2
                neutral_score = (1 - confidence) / 2
            else:
                neutral_score = confidence
                positive_score = (1 - confidence) / 2
                negative_score = (1 - confidence) / 2
            
            return {
                'sentiment': sentiment,
                'sentiment_score': confidence,
                'positive_score': positive_score,
                'negative_score': negative_score,
                'neutral_score': neutral_score
            }
            
        except Exception as e:
            print(f"Error in transformer sentiment analysis: {e}")
            return self.get_neutral_sentiment()
    
    def analyze_sentiment_vader(self, text: str) -> Dict:
        """Analyze sentiment using VADER."""
        try:
            preprocessed_text = self.preprocess_text(text)
            
            if not preprocessed_text:
                return self.get_neutral_sentiment()
            
            scores = self.vader_analyzer.polarity_scores(preprocessed_text)
            
            # Determine primary sentiment
            if scores['compound'] >= 0.05:
                sentiment = 'positive'
                sentiment_score = scores['pos']
            elif scores['compound'] <= -0.05:
                sentiment = 'negative'
                sentiment_score = scores['neg']
            else:
                sentiment = 'neutral'
                sentiment_score = scores['neu']
            
            return {
                'sentiment': sentiment,
                'sentiment_score': sentiment_score,
                'positive_score': scores['pos'],
                'negative_score': scores['neg'],
                'neutral_score': scores['neu']
            }
            
        except Exception as e:
            print(f"Error in VADER sentiment analysis: {e}")
            return self.get_neutral_sentiment()
    
    def analyze_sentiment_simple(self, text: str) -> Dict:
        """Simple rule-based sentiment analysis as last resort."""
        text = text.lower()
        
        positive_words = [
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 
            'awesome', 'brilliant', 'outstanding', 'superb', 'impressive',
            'thank', 'thanks', 'grateful', 'appreciate', 'love', 'like',
            'happy', 'pleased', 'satisfied', 'proud', 'success', 'achievement'
        ]
        
        negative_words = [
            'bad', 'terrible', 'awful', 'horrible', 'disappointing', 'frustrated',
            'angry', 'upset', 'concerned', 'worried', 'problem', 'issue',
            'fail', 'failure', 'wrong', 'error', 'mistake', 'poor',
            'hate', 'dislike', 'disgusted', 'annoyed', 'corruption'
        ]
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count:
            sentiment = 'positive'
            score = min(0.8, 0.5 + (positive_count - negative_count) * 0.1)
        elif negative_count > positive_count:
            sentiment = 'negative'
            score = min(0.8, 0.5 + (negative_count - positive_count) * 0.1)
        else:
            sentiment = 'neutral'
            score = 0.6
        
        return {
            'sentiment': sentiment,
            'sentiment_score': score,
            'positive_score': positive_count / max(1, positive_count + negative_count + 1),
            'negative_score': negative_count / max(1, positive_count + negative_count + 1),
            'neutral_score': 1 / max(1, positive_count + negative_count + 1)
        }
    
    def get_neutral_sentiment(self) -> Dict:
        """Return neutral sentiment as default."""
        return {
            'sentiment': 'neutral',
            'sentiment_score': 0.5,
            'positive_score': 0.33,
            'negative_score': 0.33,
            'neutral_score': 0.34
        }
    
    def analyze_sentiment(self, text: str) -> Dict:
        """Main method to analyze sentiment of text."""
        if not text or not text.strip():
            return self.get_neutral_sentiment()
        
        # Try different methods in order of preference
        if self.sentiment_pipeline:
            return self.analyze_sentiment_transformers(text)
        elif hasattr(self, 'vader_analyzer') and self.vader_analyzer:
            return self.analyze_sentiment_vader(text)
        else:
            return self.analyze_sentiment_simple(text)
    
    def analyze_batch(self, texts: List[str]) -> List[Dict]:
        """Analyze sentiment for a batch of texts."""
        results = []
        for text in texts:
            results.append(self.analyze_sentiment(text))
        return results
