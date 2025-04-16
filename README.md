# Auto Error Correction Platform

An AI model training and deployment system built with Flask, featuring automated data handling, feature generation from SMILES, AutoML-based model selection, and web-based visualization.

## 🔧 Features
- Upload datasets and automatically preprocess data (missing values, outliers)
- Extract chemical features from SMILES using open-source tools
- Perform feature selection to improve performance
- Train and compare models: Decision Tree, Regression, Neural Network, Auto-sklearn
- Web UI built with Flask for easy access and interaction
- Deployment on local server with optional external access via DDNS

## 📦 Tech Stack
- Python, pandas, PyTorch, Auto-sklearn
- Flask (frontend + backend)
- Notion for planning
- DDNS, domain hosting for deployment

## 🚀 Getting Started
```bash
# clone the repo
git clone https://github.com/your-username/delta-learning-platform.git
cd delta-learning-platform

# create environment and install
pip install -r requirements.txt

# start flask app
python app.py
