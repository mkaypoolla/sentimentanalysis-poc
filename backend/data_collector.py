import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time
import re
from bs4 import BeautifulSoup
import random

class TwitterDataCollector:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def scrape_tweets_snscrape(self, keyword: str, max_tweets: int = 100, days_back: int = 7) -> List[Dict]:
        """
        Scrape tweets using snscrape library.
        This is a fallback method that uses snscrape if available.
        """
        tweets = []
        try:
            import snscrape.modules.twitter as sntwitter
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # Create search query
            query = f"{keyword} since:{start_date.strftime('%Y-%m-%d')} until:{end_date.strftime('%Y-%m-%d')}"
            
            # Scrape tweets
            for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
                if i >= max_tweets:
                    break
                
                tweets.append({
                    'tweet_id': str(tweet.id),
                    'content': tweet.rawContent,
                    'username': tweet.user.username,
                    'created_at': tweet.date.isoformat(),
                    'keyword': keyword,
                    'url': tweet.url,
                    'retweet_count': tweet.retweetCount,
                    'like_count': tweet.likeCount
                })
                
                # Add small delay to be respectful
                time.sleep(0.1)
        
        except ImportError:
            print("snscrape not available, using sample data generator")
            tweets = self.generate_sample_tweets(keyword, max_tweets)
        except Exception as e:
            print(f"Error scraping tweets: {e}")
            tweets = self.generate_sample_tweets(keyword, max_tweets)
        
        return tweets
    
    def generate_sample_tweets(self, keyword: str, count: int = 100) -> List[Dict]:
        """
        Generate sample tweets for demonstration purposes.
        This simulates real tweet data when scraping is not available.
        """
        
        # Sample tweet templates related to Meghalaya Government
        positive_templates = [
            f"Great initiative by {keyword}! This will really help the people of Meghalaya. #MeghalayaDevelopment",
            f"Impressed with the recent policies from {keyword}. Moving in the right direction! 👍",
            f"Thank you {keyword} for the excellent work on infrastructure development in Shillong",
            f"{keyword} is doing amazing work for tribal welfare. Keep it up! #TribalWelfare",
            f"The new education policies by {keyword} are really promising for our youth",
            f"Kudos to {keyword} for the transparent governance and development initiatives",
            f"Happy to see {keyword} focusing on sustainable development in the Northeast",
            f"The healthcare improvements under {keyword} are commendable #Healthcare",
            f"Excellent work by {keyword} on preserving our cultural heritage while promoting development",
            f"The tourism initiatives by {keyword} are bringing positive changes to Meghalaya"
        ]
        
        negative_templates = [
            f"Disappointed with the recent decisions by {keyword}. Expected better leadership",
            f"{keyword} needs to address the infrastructure issues more seriously",
            f"The promises made by {keyword} during elections are still unfulfilled",
            f"Concerned about the environmental policies of {keyword}. Need more action!",
            f"{keyword} should focus more on rural development rather than urban areas",
            f"The corruption allegations against {keyword} officials need proper investigation",
            f"Traffic and road conditions in Shillong are getting worse under {keyword}",
            f"{keyword} needs to do more for employment generation in the state",
            f"The tribal land issues are not being handled properly by {keyword}",
            f"Disappointed with the slow progress of development projects under {keyword}"
        ]
        
        neutral_templates = [
            f"{keyword} announced new policies for the upcoming fiscal year",
            f"Meeting scheduled between {keyword} and central government officials",
            f"{keyword} to review the progress of ongoing development projects",
            f"Budget allocation for various departments announced by {keyword}",
            f"{keyword} officials to visit remote areas for assessment",
            f"New appointments made in various departments under {keyword}",
            f"{keyword} to participate in the Northeast Council meeting next week",
            f"Statistical report on state development released by {keyword}",
            f"{keyword} to hold public consultation on new infrastructure projects",
            f"Administrative reforms being considered by {keyword} for better governance"
        ]
        
        usernames = [
            "meghalaya_citizen", "shillong_resident", "northeast_observer", "tribal_voice",
            "development_watch", "meghalaya_news", "citizen_reporter", "local_activist",
            "youth_meghalaya", "concerned_citizen", "meghalaya_today", "northeast_times",
            "shillong_times", "meghalaya_mirror", "tribal_times", "hill_voice"
        ]
        
        tweets = []
        now = datetime.now()
        
        for i in range(count):
            # Randomly select sentiment and template
            sentiment_choice = random.choices(
                ['positive', 'negative', 'neutral'], 
                weights=[0.4, 0.3, 0.3]
            )[0]
            
            if sentiment_choice == 'positive':
                content = random.choice(positive_templates)
            elif sentiment_choice == 'negative':
                content = random.choice(negative_templates)
            else:
                content = random.choice(neutral_templates)
            
            # Generate random timestamp within last 7 days
            random_hours = random.randint(0, 7 * 24)
            created_at = now - timedelta(hours=random_hours)
            
            tweets.append({
                'tweet_id': f"sample_{i}_{int(time.time())}",
                'content': content,
                'username': random.choice(usernames),
                'created_at': created_at.isoformat(),
                'keyword': keyword,
                'url': f"https://twitter.com/sample/status/{i}",
                'retweet_count': random.randint(0, 50),
                'like_count': random.randint(0, 200)
            })
        
        return tweets
    
    def collect_tweets(self, keyword: str = "Meghalaya Govt", max_tweets: int = 100, days_back: int = 7) -> List[Dict]:
        """
        Main method to collect tweets for a given keyword.
        """
        print(f"Collecting tweets for keyword: '{keyword}'")
        
        # Try snscrape first, fallback to sample data
        tweets = self.scrape_tweets_snscrape(keyword, max_tweets, days_back)
        
        if not tweets:
            print("No tweets found, generating sample data for demonstration")
            tweets = self.generate_sample_tweets(keyword, max_tweets)
        
        print(f"Collected {len(tweets)} tweets")
        return tweets
    
    def clean_tweet_content(self, content: str) -> str:
        """Clean tweet content by removing URLs, mentions, and extra whitespace."""
        # Remove URLs
        content = re.sub(r'http\S+|www\S+|https\S+', '', content, flags=re.MULTILINE)
        # Remove mentions and hashtags for cleaner analysis (keep hashtags for keyword extraction)
        content = re.sub(r'@\w+', '', content)
        # Remove extra whitespace
        content = ' '.join(content.split())
        return content.strip()
