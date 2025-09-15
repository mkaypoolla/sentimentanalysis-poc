import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import requests
import json
# Removed wordcloud and matplotlib for cloud deployment compatibility
import io
import base64

# Import backend modules
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database import TweetDatabase
from backend.data_collector import TwitterDataCollector
from backend.sentiment_analyzer import SentimentAnalyzer

# Page configuration
st.set_page_config(
    page_title="Sentiment Dashboard - Meghalaya Government",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .sentiment-positive {
        color: #28a745;
        font-weight: bold;
    }
    .sentiment-negative {
        color: #dc3545;
        font-weight: bold;
    }
    .sentiment-neutral {
        color: #6c757d;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize components
@st.cache_resource
def init_components():
    db = TweetDatabase()
    collector = TwitterDataCollector()
    analyzer = SentimentAnalyzer()
    return db, collector, analyzer

db, collector, analyzer = init_components()

# Main title
st.markdown('<h1 class="main-header">🏛️ Sentiment Dashboard - Meghalaya Government</h1>', unsafe_allow_html=True)

# Sidebar configuration
st.sidebar.title("⚙️ Configuration")

# Keyword input
keyword = st.sidebar.text_input(
    "Enter Keywords/Hashtags",
    value="Meghalaya Govt",
    help="Enter keywords to search for in tweets"
)

# Data collection settings
st.sidebar.subheader("Data Collection")
max_tweets = st.sidebar.slider("Max Tweets to Collect", 50, 500, 100)
days_back = st.sidebar.slider("Days Back", 1, 30, 7)

# Date range filter
st.sidebar.subheader("Date Range Filter")
end_date = st.sidebar.date_input("End Date", datetime.now().date())
start_date = st.sidebar.date_input("Start Date", (datetime.now() - timedelta(days=7)).date())

# Convert dates to datetime
start_datetime = datetime.combine(start_date, datetime.min.time())
end_datetime = datetime.combine(end_date, datetime.max.time())

# Action buttons
if st.sidebar.button("🔄 Collect New Tweets", type="primary"):
    with st.spinner("Collecting and analyzing tweets..."):
        try:
            # Collect tweets
            tweets = collector.collect_tweets(keyword, max_tweets, days_back)
            
            if tweets:
                # Analyze sentiment
                analyzed_tweets = []
                progress_bar = st.progress(0)
                
                for i, tweet in enumerate(tweets):
                    sentiment_result = analyzer.analyze_sentiment(tweet['content'])
                    tweet.update(sentiment_result)
                    analyzed_tweets.append(tweet)
                    progress_bar.progress((i + 1) / len(tweets))
                
                # Store in database
                db.insert_tweets(analyzed_tweets)
                
                st.sidebar.success(f"✅ Collected {len(analyzed_tweets)} tweets!")
                st.rerun()
            else:
                st.sidebar.error("❌ No tweets found for the given keyword")
                
        except Exception as e:
            st.sidebar.error(f"❌ Error: {str(e)}")

# Export functionality
if st.sidebar.button("📥 Export to CSV"):
    try:
        filename = f"tweets_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = f"data/{filename}"
        count = db.export_to_csv(filepath, keyword, start_datetime, end_datetime)
        st.sidebar.success(f"✅ Exported {count} tweets to {filename}")
    except Exception as e:
        st.sidebar.error(f"❌ Export error: {str(e)}")

# Main dashboard content
def load_data():
    """Load data from database with current filters."""
    return db.get_tweets(keyword=keyword, start_date=start_datetime, end_date=end_datetime, limit=1000)

# Load data
df = load_data()

if df.empty:
    st.warning("📭 No data available. Please collect some tweets first using the sidebar.")
    st.info("💡 Click 'Collect New Tweets' in the sidebar to get started with the default keyword 'Meghalaya Govt'")
else:
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_tweets = len(df)
    sentiment_counts = df['sentiment'].value_counts()
    
    with col1:
        st.metric("📊 Total Tweets", total_tweets)
    
    with col2:
        positive_count = sentiment_counts.get('positive', 0)
        positive_pct = (positive_count / total_tweets * 100) if total_tweets > 0 else 0
        st.metric("😊 Positive", f"{positive_count} ({positive_pct:.1f}%)")
    
    with col3:
        negative_count = sentiment_counts.get('negative', 0)
        negative_pct = (negative_count / total_tweets * 100) if total_tweets > 0 else 0
        st.metric("😞 Negative", f"{negative_count} ({negative_pct:.1f}%)")
    
    with col4:
        neutral_count = sentiment_counts.get('neutral', 0)
        neutral_pct = (neutral_count / total_tweets * 100) if total_tweets > 0 else 0
        st.metric("😐 Neutral", f"{neutral_count} ({neutral_pct:.1f}%)")
    
    # Charts row 1
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Sentiment Distribution")
        if not sentiment_counts.empty:
            fig_pie = px.pie(
                values=sentiment_counts.values,
                names=sentiment_counts.index,
                color=sentiment_counts.index,
                color_discrete_map={
                    'positive': '#28a745',
                    'negative': '#dc3545',
                    'neutral': '#6c757d'
                },
                title="Overall Sentiment Distribution"
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No sentiment data available")
    
    with col2:
        st.subheader("📅 Sentiment Timeline")
        # Create timeline data
        df['date'] = pd.to_datetime(df['created_at']).dt.date
        timeline_data = df.groupby(['date', 'sentiment']).size().reset_index(name='count')
        
        if not timeline_data.empty:
            fig_timeline = px.line(
                timeline_data,
                x='date',
                y='count',
                color='sentiment',
                color_discrete_map={
                    'positive': '#28a745',
                    'negative': '#dc3545',
                    'neutral': '#6c757d'
                },
                title="Sentiment Trends Over Time"
            )
            fig_timeline.update_layout(xaxis_title="Date", yaxis_title="Number of Tweets")
            st.plotly_chart(fig_timeline, use_container_width=True)
        else:
            st.info("No timeline data available")
    
    # Charts row 2
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔤 Top Keywords (Text)")
        try:
            # Get top keywords and display as text
            top_keywords = db.get_top_keywords(20)
            
            if top_keywords:
                keywords_text = ", ".join([f"{word} ({count})" for word, count in top_keywords[:10]])
                st.write(f"**Most frequent keywords:** {keywords_text}")
                
                # Create a simple bar chart instead of word cloud
                keywords_df = pd.DataFrame(top_keywords[:10], columns=['Keyword', 'Frequency'])
                fig_keywords = px.bar(
                    keywords_df,
                    x='Keyword',
                    y='Frequency',
                    title="Top 10 Keywords",
                    color='Frequency',
                    color_continuous_scale='viridis'
                )
                st.plotly_chart(fig_keywords, use_container_width=True)
            else:
                st.info("No keywords available")
        except Exception as e:
            st.error(f"Error displaying keywords: {str(e)}")
    
    with col2:
        st.subheader("📊 Sentiment Score Distribution")
        try:
            # Show sentiment score statistics
            if not df.empty:
                score_stats = df['sentiment_score'].describe()
                st.write("**Sentiment Score Statistics:**")
                st.write(f"- Mean: {score_stats['mean']:.3f}")
                st.write(f"- Median: {score_stats['50%']:.3f}")
                st.write(f"- Std Dev: {score_stats['std']:.3f}")
                
                # Histogram of sentiment scores
                fig_hist = px.histogram(
                    df,
                    x='sentiment_score',
                    color='sentiment',
                    title="Distribution of Sentiment Scores",
                    color_discrete_map={
                        'positive': '#28a745',
                        'negative': '#dc3545',
                        'neutral': '#6c757d'
                    }
                )
                st.plotly_chart(fig_hist, use_container_width=True)
            else:
                st.info("No sentiment data available")
        except Exception as e:
            st.error(f"Error displaying sentiment distribution: {str(e)}")
    
    # Recent tweets feed
    st.subheader("📋 Recent Tweets Feed")
    
    # Display recent tweets with sentiment colors
    recent_tweets = df.head(20)
    
    for _, tweet in recent_tweets.iterrows():
        sentiment = tweet['sentiment']
        sentiment_class = f"sentiment-{sentiment}"
        
        # Format the tweet display
        col1, col2, col3 = st.columns([1, 6, 1])
        
        with col1:
            if sentiment == 'positive':
                st.markdown("😊")
            elif sentiment == 'negative':
                st.markdown("😞")
            else:
                st.markdown("😐")
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <strong>@{tweet['username']}</strong> • {pd.to_datetime(tweet['created_at']).strftime('%Y-%m-%d %H:%M')}
                <br>
                {tweet['content'][:200]}{'...' if len(tweet['content']) > 200 else ''}
                <br>
                <span class="{sentiment_class}">Sentiment: {sentiment.title()} ({tweet['sentiment_score']:.2f})</span>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"**{tweet['sentiment_score']:.2f}**")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6c757d;'>
    <p>🌊 Built with Streamlit • Powered by Hugging Face Transformers • Data from Free Sources</p>
    <p>Sentiment Dashboard for Meghalaya Government - Real-time Social Media Analysis</p>
</div>
""", unsafe_allow_html=True)
