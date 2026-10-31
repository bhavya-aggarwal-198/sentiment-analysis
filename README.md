# Sentiment Analysis

A Django web application that predicts sentiment from submitted text using a trained scikit-learn model.

## Run locally

```powershell
cd sentiment_analysis
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

For deployment, set `DJANGO_SECRET_KEY` to a secure, unique value.
