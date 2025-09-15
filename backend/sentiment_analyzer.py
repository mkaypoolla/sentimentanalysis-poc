from typing import Dict, List
import re

class SentimentAnalyzer:
    def __init__(self):
        """
        Initialize the sentiment analyzer with VADER for cloud deployment.
        """
        self.load_vader()
    
    def load_vader(self):
        """Load VADER sentiment analyzer."""
        try:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            self.vader_analyzer = SentimentIntensityAnalyzer()
            print("VADER sentiment analyzer loaded successfully")
        except ImportError:
            print("VADER not available, using simple rule-based sentiment")
            self.vader_analyzer = None
    
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
        
        # Use VADER or fallback to simple analysis
        if hasattr(self, 'vader_analyzer') and self.vader_analyzer:
            return self.analyze_sentiment_vader(text)
        else:
            return self.analyze_sentiment_simple(text)
    
    def analyze_batch(self, texts: List[str]) -> List[Dict]:
        """Analyze sentiment for a batch of texts."""
        results = []
        for text in texts:
            results.append(self.analyze_sentiment(text))
        return results
