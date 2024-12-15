positive_recommender is the flask server and the positive recommender system
sentiment directory is the virtual env

### Need to update the details below

Model Documentation

Model name: `cardiffnlp/twitter-roberta-base-sentiment-latest`
This model is a RoBERTa-based model specifically trained for sentiment analysis on tweets.

RoBERTa is a transformers model pretrained on a large corpus of English data in a self-supervised fashion. This means it was pretrained on the raw texts only, with no humans labelling them in any way with an automatic process to generate inputs and labels from those texts.

More precisely, it was pretrained with the Masked language modeling (MLM) objective. Taking a sentence, the model randomly masks 15% of the words in the input then run the entire masked sentence through the model and has to predict the masked words. It allows the model to learn a bidirectional representation of the sentence.

You can use the raw model for masked language modeling, but it's mostly intended to be fine-tuned on a downstream task. Here, we are using it specifically for sentiment analysis.

### Model Description

The `cardiffnlp/twitter-roberta-base-sentiment-latest` model is a sentiment analysis model based on RoBERTa-base architecture, a transformer-based model that enhances BERT by training on more data and with larger batch sizes. This specific model is trained to understand and classify sentiments expressed in tweets.

### Intended Use

This model is intended for sentiment analysis of English tweets. It can classify tweets into three sentiment categories:

- 0: Negative
- 1: Neutral
- 2: Positive

### Training Data

The model was trained on approximately 124 million tweets collected from January 2018 to December 2021. The training data includes a wide range of topics and sentiments, ensuring the model is well-rounded for general tweet sentiment analysis tasks

### Evaluation

The model's performance was evaluated using the TweetEval benchmark, which includes various datasets and metrics tailored for tweet sentiment analysis.

TweetEval is a Multi-task Classification Benchmark. It consists of seven heterogenous tasks. The tasks include - irony, hate, offensive, stance, emoji, emotion, and sentiment. All tasks have been unified into the same benchmark, with each dataset presented in the same format and with fixed training, validation and test splits.
### Limitations

1. **Language Limitation**: The model is designed to work with English tweets only.
2. **Context Understanding**: The model might struggle with understanding the context or nuances of certain tweets, especially those involving sarcasm, slang, or emerging trends.
3. **Bias in Training Data**: The training data, being sourced from Twitter, may contain inherent biases present in the platform's user base and content.


## How to Run
Follow the steps below to run the server after cloning/pulling into your local device.  
You will also need to be running our frontend simultaneously ([mystodon](https://github.com/Vikalp-Social/mystodon)).  
Default port of the server is set to `3000`.

1) `python api.py` (Ensure all required libraries are installed)
