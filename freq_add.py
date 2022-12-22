import re
import math
import nltk
import heapq
import random

"""
Simple summarizer using aggregated sentence scores (TF-IDF algorithm)
Sources:
https://stackabuse.com/text-summarization-with-nltk-in-python/
"""
def freq_add_summarizer(passage: str, brevity: int = 50):
    nltk.download('punkt')
    nltk.download("stopwords")
    stopwords = nltk.corpus.stopwords.words("english")

    stripped_passage = re.sub('[^a-zA-Z0-9]', ' ', passage)
    formatted_passage = re.sub(r'\s+', ' ', stripped_passage)

    token_sentences = nltk.sent_tokenize(passage)
    token_words = nltk.word_tokenize(formatted_passage)

    length_factor = random.uniform(0.05, 0.15)
    summary_length = math.ceil(length_factor * len(token_sentences))

    # Find all word frequencies
    word_frequencies = {}
    for word in token_words:
        if word not in stopwords:
            if word not in word_frequencies:
                word_frequencies[word] = 1
            else:
                word_frequencies[word] += 1

    # Normalize/weight the word frequencies
    maximum_frequency = max(word_frequencies.values())
    norm_word_frequencies = {
        word: word_frequencies[word] / maximum_frequency
        for word in word_frequencies
    }

    # Calculate sentence importance scores
    sent_importance = {}
    for sent in token_sentences:
        sent_tokens = nltk.word_tokenize(sent.lower())
        for word in sent_tokens:
            if word in norm_word_frequencies:
                if len(sent.split(' ')) <= brevity:
                    if sent not in sent_importance:
                        sent_importance[sent] = norm_word_frequencies[word]
                    else:
                        sent_importance[sent] += norm_word_frequencies[word]
    
    # Make a summary with the top N most important token_sentences
    summary_sentences = heapq.nlargest(
        summary_length,
        sent_importance,
        key = sent_importance.get,
    )
    return ' '.join(summary_sentences)
