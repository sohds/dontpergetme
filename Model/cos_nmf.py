import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
from sklearn.metrics.pairwise import cosine_similarity
import re
import numpy as np

# 기본 전처리 함수
def preprocess_text(text):
    text = re.sub(r'\b\w{1,2}\b', '', text)  # Remove short words
    text = re.sub(r'\s+', ' ', text)  # Remove multiple spaces
    text = re.sub(r'\d+', '', text)  # Remove numbers
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    text = text.lower()  # Lowercase text
    words = text.split()
    stopwords = set(['the', 'and', 'is', 'in', 'to', 'with', 'of', 'a', 'for', 'on', 'that', 'this'])
    words = [word for word in words if word not in stopwords]
    return ' '.join(words)

# 여행지 분위기 추출 함수 (여러 주제)
def extract_destination_moods(destinations, n_topics=18):
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(destinations['description'].apply(preprocess_text))
    
    # NMF를 사용하여 주제 모델링
    nmf_model = NMF(n_components=n_topics, random_state=1)
    W = nmf_model.fit_transform(tfidf_matrix)
    
    # 각 주제를 미리 정의된 레이블로 매핑
    mood_labels = ['picturesque', 'peaceful', 'grand', 'tranquil', 'lush', 'exquisite', 
                    'vibrant', 'bustling', 'traditional', 'cultural', 'unique', 'trendy', 'relaxing', 
                    'romantic', 'luxurious', 'exotic', 'adventurous', 'active']
    topic_to_mood = {i: mood_labels[i] for i in range(n_topics)}
    
    # 각 여행지에 대해 상위 3개의 주제를 추출하여 분위기 매핑
    top_topics = np.argsort(W, axis=1)[:, -3:]
    top_moods = [[topic_to_mood[topic] for topic in topics] for topics in top_topics]
    
    destinations['moods'] = top_moods
    
    return tfidf_vectorizer, tfidf_matrix, destinations

# 향수 데이터 로드 및 전처리
def load_perfume_data(perfume_file_path):
    perfumes = pd.read_csv(perfume_file_path)
    perfumes['processed_notes'] = perfumes['notes'].apply(preprocess_text)
    return perfumes

# 향수와 여행지 매핑 (코사인 유사도)
def map_perfumes_to_destinations(perfumes, tfidf_vectorizer):
    perfume_tfidf_matrix = tfidf_vectorizer.transform(perfumes['processed_notes'])
    return perfume_tfidf_matrix

# 추천 시스템
def recommend_perfumes_for_destination(destination_index, destinations, tfidf_matrix, perfume_tfidf_matrix, perfumes, top_n=10):
    destination_vector = tfidf_matrix[destination_index].reshape(1, -1)
    cosine_sim = cosine_similarity(destination_vector, perfume_tfidf_matrix).flatten()
    top_perfume_indices = cosine_sim.argsort()[-top_n:][::-1]  # 상위 n개 향수 추천
    recommended_perfumes = [perfumes.iloc[idx]['name'] for idx in top_perfume_indices]
    
    return recommended_perfumes