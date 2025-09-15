import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os

class TweetDatabase:
    def __init__(self, db_path: str = "data/tweets.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the SQLite database with required tables."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tweets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tweet_id TEXT UNIQUE,
                    content TEXT NOT NULL,
                    username TEXT,
                    created_at TIMESTAMP,
                    keyword TEXT,
                    sentiment TEXT,
                    sentiment_score REAL,
                    positive_score REAL,
                    negative_score REAL,
                    neutral_score REAL,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_created_at ON tweets(created_at);
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_keyword ON tweets(keyword);
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_sentiment ON tweets(sentiment);
            """)
            
            conn.commit()
    
    def insert_tweets(self, tweets: List[Dict]):
        """Insert multiple tweets into the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for tweet in tweets:
                cursor.execute("""
                    INSERT OR REPLACE INTO tweets 
                    (tweet_id, content, username, created_at, keyword, sentiment, 
                     sentiment_score, positive_score, negative_score, neutral_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    tweet.get('tweet_id'),
                    tweet.get('content'),
                    tweet.get('username'),
                    tweet.get('created_at'),
                    tweet.get('keyword'),
                    tweet.get('sentiment'),
                    tweet.get('sentiment_score'),
                    tweet.get('positive_score'),
                    tweet.get('negative_score'),
                    tweet.get('neutral_score')
                ))
            
            conn.commit()
    
    def get_tweets(self, keyword: Optional[str] = None, 
                   start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None,
                   limit: Optional[int] = None) -> pd.DataFrame:
        """Retrieve tweets based on filters."""
        query = "SELECT * FROM tweets WHERE 1=1"
        params = []
        
        if keyword:
            query += " AND keyword LIKE ?"
            params.append(f"%{keyword}%")
        
        if start_date:
            query += " AND created_at >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND created_at <= ?"
            params.append(end_date.isoformat())
        
        query += " ORDER BY created_at DESC"
        
        if limit:
            query += f" LIMIT {limit}"
        
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query(query, conn, params=params)
    
    def get_sentiment_distribution(self, keyword: Optional[str] = None,
                                 start_date: Optional[datetime] = None,
                                 end_date: Optional[datetime] = None) -> Dict:
        """Get sentiment distribution counts."""
        query = """
            SELECT sentiment, COUNT(*) as count 
            FROM tweets 
            WHERE 1=1
        """
        params = []
        
        if keyword:
            query += " AND keyword LIKE ?"
            params.append(f"%{keyword}%")
        
        if start_date:
            query += " AND created_at >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND created_at <= ?"
            params.append(end_date.isoformat())
        
        query += " GROUP BY sentiment"
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            return {sentiment: count for sentiment, count in results}
    
    def get_sentiment_timeline(self, keyword: Optional[str] = None,
                             start_date: Optional[datetime] = None,
                             end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Get sentiment trends over time."""
        query = """
            SELECT 
                DATE(created_at) as date,
                sentiment,
                COUNT(*) as count,
                AVG(sentiment_score) as avg_score
            FROM tweets 
            WHERE 1=1
        """
        params = []
        
        if keyword:
            query += " AND keyword LIKE ?"
            params.append(f"%{keyword}%")
        
        if start_date:
            query += " AND created_at >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND created_at <= ?"
            params.append(end_date.isoformat())
        
        query += " GROUP BY DATE(created_at), sentiment ORDER BY date"
        
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query(query, conn, params=params)
    
    def get_top_keywords(self, limit: int = 20) -> List[str]:
        """Get most frequent words from tweet content."""
        query = "SELECT content FROM tweets"
        
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query(query, conn)
            
            if df.empty:
                return []
            
            # Simple word frequency analysis
            all_text = ' '.join(df['content'].dropna().astype(str))
            words = all_text.lower().split()
            
            # Filter out common words and short words
            stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'rt', 'https', 'http'}
            
            word_freq = {}
            for word in words:
                if len(word) > 3 and word not in stop_words and word.isalpha():
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            return sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    def export_to_csv(self, filepath: str, keyword: Optional[str] = None,
                     start_date: Optional[datetime] = None,
                     end_date: Optional[datetime] = None):
        """Export tweets to CSV file."""
        df = self.get_tweets(keyword, start_date, end_date)
        df.to_csv(filepath, index=False)
        return len(df)
