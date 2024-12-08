# Sentiment Analyzer Dependencies
import time
import torch
from bs4 import BeautifulSoup
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import os

# Check if Sentiment Analyzer model is already downloaded
folder = 'sentimentAnalyzerFolder'
def check_folder_exists(folder_path):
    return os.path.isdir(folder_path)

if not check_folder_exists(folder):
    # DistilBERT Model Parameters
    modelName = "distilbert-base-uncased-finetuned-sst-2-english"
    model = DistilBertForSequenceClassification.from_pretrained(modelName)
    tokenizer = DistilBertTokenizer.from_pretrained(modelName)

    # Set model to evaluation mode
    model.eval()

    # Save Pre-trained models so that it is not downloaded repeatedly
    localDir = "./sentimentAnalyzerFolder"
    model.save_pretrained(localDir)
    tokenizer.save_pretrained(localDir)
    print(f"Model and tokenizer saved to {localDir}")

# Model Parameters
localDir = "./sentimentAnalyzerFolder"
model = DistilBertForSequenceClassification.from_pretrained(localDir)
tokenizer = DistilBertTokenizer.from_pretrained(localDir)
model.eval()
torch.backends.quantized.engine = 'qnnpack'
print("Model and tokenizer loaded from the local directory")

# Encode Sentiment Label to value
label_to_value = {
    'NEGATIVE': -1,
    'POSITIVE': 1
}

# Analyze Sentiment of Posts
def analyzeSentiment(toots):
    results = []
    for t in toots:
        if t.get('language', None) == 'en' or (t.get('reblog', {}) and t.get('reblog', {}).get('language', None) == 'en'):
            results.append(t)

    def getProbability(model, text):
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        with torch.no_grad():
            outputs = model(**inputs)
        logits = outputs.logits
        probabilities = torch.nn.functional.softmax(logits, dim=-1)
        return probabilities

    def getSentiment(text):
        # Process HTML Text to obtain Plain Text
        soup = BeautifulSoup(text, "html.parser")
        plain_text = soup.get_text()

        # Analyze Sentiment
        probabilities = getProbability(model, plain_text)
        prediction = torch.argmax(probabilities, dim=-1).item()
        label = model.config.id2label[prediction]
        return label_to_value[label]

    # Get list of positive and negative posts
    positivePosts = []
    negativePosts = []
    for row in results:
        if row['content'] and getSentiment(row['content']) == 1:
            positivePosts.append(row)
        elif row['content'] and getSentiment(row['content']) == -1:
            negativePosts.append(row)
        elif 'reblog' in row and row['reblog'] and getSentiment(row['reblog']['content']) == 1:
            positivePosts.append(row)
        elif 'reblog' in row and row['reblog'] and getSentiment(row['reblog']['content']) == -1:
            negativePosts.append(row)

    # Return positive posts
    return positivePosts
