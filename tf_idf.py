import re
import nltk
import math

def find_frequencies(sentences, stopwords, st):
    freq_mat = {}
    for sent in sentences:
        stripped_sent = re.sub('[^a-zA-Z0-9]', ' ', sent)
        formatted_sent = re.sub(r'\s+', ' ', stripped_sent)
        words = nltk.word_tokenize(formatted_sent)
        word_freqs = {}
        for word in words:
            formatted = st.stem(word.lower())
            if formatted not in stopwords:
                if word not in word_freqs:
                    word_freqs[word] = 1
                else:
                    word_freqs[word] += 1
        freq_mat[sent] = word_freqs
    return freq_mat

def create_tf(frequencies):
    tf_mat = {}
    for sent, word_freqs in frequencies.items():
        words_per_sentence = len(word_freqs)
        sent_tfs = {}
        for word, count in word_freqs.items():
            sent_tfs[word] = count / words_per_sentence
        tf_mat[sent] = sent_tfs
    return tf_mat

def find_sentences_per_word(frequencies):
    words_per_sent = {}
    for word_freqs in frequencies.values():
        for word in word_freqs:
            if word not in words_per_sent:
                words_per_sent[word] = 1
            else:
                words_per_sent[word] += 1
    return words_per_sent

def create_idf(frequencies, sents_per_words, total):
    idf_mat = {}
    for sent, word_freqs in frequencies.items():
        sent_idfs = {}
        for word in word_freqs:
            sent_idfs[word] = math.log10(total / float(sents_per_words[word]))
        idf_mat[sent] = sent_idfs
    return idf_mat

def calculate_tf_idf(tfs, idfs):
    tf_idf_mat = {}
    for tf_sent, tf_wfs in tfs.items():
        for idf_wfs in idfs.values():
            sent_tf_idfs = {}
            for tf_word, tf in tf_wfs.items():
                for idf in idf_wfs.values():
                    sent_tf_idfs[tf_word] = float(tf * idf)
            tf_idf_mat[tf_sent] = sent_tf_idfs
    return tf_idf_mat

def calculate_scores(tf_idfs):
    sentence_scores = {}
    for sent, word_tf_idfs in tf_idfs.items():
        total_tf_idf = sum(word_tf_idfs.values())
        sentence_scores[sent] = total_tf_idf / len(word_tf_idfs)
    return sentence_scores

def generate_summary(sentences, scores, threshold):
    return [
        sent
        for sent in sentences
        if sent in scores and scores[sent] >= threshold
    ]

"""
Matrix summarizer using TF-IDF algorithm
Sources:
https://en.wikipedia.org/wiki/Tf%E2%80%93idf
https://towardsdatascience.com/text-summarization-using-tf-idf-e64a0644ace3
"""
def tf_idf_summarizer(passage: str, quality: int = 1.25):
    nltk.download('punkt')
    nltk.download("stopwords")
    stemmer = nltk.PorterStemmer()
    stopwords = nltk.corpus.stopwords.words("english")

    token_sentences = nltk.sent_tokenize(passage)
    total_sentences = len(token_sentences)

    # TF step: find total frequencies of words in each sentence
    frequency_matrix = find_frequencies(token_sentences, stopwords, stemmer)
    tf_matrix = create_tf(frequency_matrix)

    # IDF step: find rarity of a word relative to each "document" (sentence)
    sentences_containing_words = find_sentences_per_word(frequency_matrix)
    idf_matrix = create_idf(
        frequency_matrix,
        sentences_containing_words,
        total_sentences
    )

    # TF_IDF step: multiply the TF values and the IDF values
    tf_idf_matrix = calculate_tf_idf(tf_matrix, idf_matrix)

    # Score sentences and generate summary from best sentences
    sentence_scores = calculate_scores(tf_idf_matrix)
    average_score = sum(sentence_scores.values()) / len(sentence_scores)
    summary_sentences = generate_summary(token_sentences, sentence_scores, quality * average_score)
    return " ".join(summary_sentences)