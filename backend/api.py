from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import uvicorn

from .database import TweetDatabase
from .data_collector import TwitterDataCollector
from .sentiment_analyzer import SentimentAnalyzer

app = FastAPI(title="Sentiment Analysis API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
db = TweetDatabase()
collector = TwitterDataCollector()
analyzer = SentimentAnalyzer()

class KeywordRequest(BaseModel):
    keyword: str
    max_tweets: int = 100
    days_back: int = 7

class AnalysisRequest(BaseModel):
    keyword: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "Sentiment Analysis API for Meghalaya Government"}

@app.post("/collect-tweets")
async def collect_tweets(request: KeywordRequest):
    """Collect tweets for a given keyword and store them in the database."""
    try:
        # Collect tweets
        tweets = collector.collect_tweets(
            keyword=request.keyword,
            max_tweets=request.max_tweets,
            days_back=request.days_back
        )
        
        if not tweets:
            raise HTTPException(status_code=404, detail="No tweets found for the given keyword")
        
        # Analyze sentiment for each tweet
        analyzed_tweets = []
        for tweet in tweets:
            sentiment_result = analyzer.analyze_sentiment(tweet['content'])
            
            tweet.update(sentiment_result)
            analyzed_tweets.append(tweet)
        
        # Store in database
        db.insert_tweets(analyzed_tweets)
        
        return {
            "message": f"Successfully collected and analyzed {len(analyzed_tweets)} tweets",
            "keyword": request.keyword,
            "tweets_count": len(analyzed_tweets)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error collecting tweets: {str(e)}")

@app.get("/tweets")
async def get_tweets(
    keyword: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    limit: Optional[int] = Query(100)
):
    """Get tweets from the database with optional filters."""
    try:
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        df = db.get_tweets(keyword=keyword, start_date=start_dt, end_date=end_dt, limit=limit)
        
        return {
            "tweets": df.to_dict('records'),
            "total_count": len(df)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving tweets: {str(e)}")

@app.get("/sentiment-distribution")
async def get_sentiment_distribution(
    keyword: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """Get sentiment distribution for tweets."""
    try:
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        distribution = db.get_sentiment_distribution(
            keyword=keyword,
            start_date=start_dt,
            end_date=end_dt
        )
        
        return {"sentiment_distribution": distribution}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting sentiment distribution: {str(e)}")

@app.get("/sentiment-timeline")
async def get_sentiment_timeline(
    keyword: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """Get sentiment trends over time."""
    try:
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        df = db.get_sentiment_timeline(
            keyword=keyword,
            start_date=start_dt,
            end_date=end_dt
        )
        
        return {
            "timeline_data": df.to_dict('records')
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting sentiment timeline: {str(e)}")

@app.get("/top-keywords")
async def get_top_keywords(limit: int = Query(20)):
    """Get most frequent keywords from tweets."""
    try:
        keywords = db.get_top_keywords(limit=limit)
        return {"top_keywords": keywords}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting top keywords: {str(e)}")

@app.post("/export-csv")
async def export_csv(request: AnalysisRequest):
    """Export tweets to CSV file."""
    try:
        start_dt = datetime.fromisoformat(request.start_date) if request.start_date else None
        end_dt = datetime.fromisoformat(request.end_date) if request.end_date else None
        
        filename = f"tweets_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = f"data/{filename}"
        
        count = db.export_to_csv(
            filepath=filepath,
            keyword=request.keyword,
            start_date=start_dt,
            end_date=end_dt
        )
        
        return {
            "message": f"Successfully exported {count} tweets to {filename}",
            "filename": filename,
            "filepath": filepath,
            "count": count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting CSV: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "database": "connected",
            "sentiment_analyzer": "loaded",
            "data_collector": "ready"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
