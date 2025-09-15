# Deployment Guide

## Option 1: GitHub + Streamlit Cloud (Recommended - Free)

### Step 1: Create GitHub Repository
1. Go to [GitHub.com](https://github.com) and sign in
2. Click "New repository" 
3. Repository name: `sentiment-dashboard-meghalaya`
4. Description: `Sentiment Analysis Dashboard for Meghalaya Government`
5. Make it Public (required for free Streamlit Cloud)
6. Don't initialize with README (we already have one)
7. Click "Create repository"

### Step 2: Push to GitHub
Run these commands in your terminal:

```bash
cd /Users/admin/Desktop/sentimentanalysis
git remote add origin https://github.com/YOUR_USERNAME/sentiment-dashboard-meghalaya.git
git branch -M main
git push -u origin main
```

### Step 3: Deploy to Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository: `sentiment-dashboard-meghalaya`
5. Main file path: `dashboard.py`
6. Click "Deploy!"

Your app will be live at: `https://YOUR_USERNAME-sentiment-dashboard-meghalaya-dashboard-xxxxx.streamlit.app`

## Option 2: Hugging Face Spaces (Alternative - Free)

### Step 1: Create Hugging Face Account
1. Go to [huggingface.co](https://huggingface.co) and sign up
2. Go to "Spaces" tab
3. Click "Create new Space"
4. Space name: `sentiment-dashboard-meghalaya`
5. License: `mit`
6. SDK: `Streamlit`
7. Make it Public
8. Click "Create Space"

### Step 2: Upload Files
1. Clone the created space repository
2. Copy all files from this project
3. Rename `dashboard.py` to `app.py` (required by HF Spaces)
4. Push to the space repository

## Option 3: Railway (Alternative - Free Tier)

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway will auto-detect and deploy

## Option 4: Render (Alternative - Free Tier)

1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Click "New" → "Web Service"
4. Connect your GitHub repository
5. Build Command: `pip install -r requirements.txt`
6. Start Command: `streamlit run dashboard.py --server.port=$PORT --server.address=0.0.0.0`

## Environment Variables (if needed)
- No API keys required for basic functionality
- Uses sample data generator by default
- All dependencies are in requirements.txt

## Notes
- The app uses sample data by default (no Twitter API required)
- Hugging Face models are downloaded automatically on first run
- SQLite database is created automatically
- All visualizations work out of the box
