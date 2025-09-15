# Sentiment Dashboard - Meghalaya Government

A full-stack sentiment analysis application that collects tweets from free sources, performs sentiment analysis, and visualizes results in an interactive dashboard.

## Features

- **Keyword Configuration**: Enter keywords/hashtags to track (default: "Meghalaya Govt")
- **Data Collection**: Uses snscrape for free Twitter data collection
- **Sentiment Analysis**: Powered by Hugging Face transformers (cardiffnlp/twitter-roberta-base-sentiment)
- **Interactive Dashboard**: Built with Streamlit
- **Visualizations**: 
  - Sentiment distribution pie chart
  - Timeline sentiment trends
  - Word cloud of top keywords
  - Recent tweets feed with sentiment labels
- **Export**: Download results as CSV

## Tech Stack

- **Backend**: FastAPI
- **Frontend**: Streamlit
- **Sentiment Analysis**: Hugging Face Transformers
- **Data Collection**: snscrape
- **Database**: SQLite
- **Visualization**: Plotly, WordCloud

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
streamlit run dashboard.py
```

3. Access the dashboard at `http://localhost:8501`

## Docker Deployment

```bash
docker-compose up
```

## Project Structure

```
sentimentanalysis/
├── requirements.txt
├── README.md
├── dashboard.py          # Main Streamlit dashboard
├── backend/
│   ├── __init__.py
│   ├── api.py           # FastAPI backend
│   ├── data_collector.py # Twitter scraping
│   ├── sentiment_analyzer.py # Sentiment analysis
│   └── database.py      # SQLite operations
├── data/
│   └── tweets.db        # SQLite database
└── docker-compose.yml
```
