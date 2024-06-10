import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
from sklearn.metrics.pairwise import cosine_similarity
import re
import numpy as np
import openai
import time

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

# OpenAI GPT-3.5를 사용하여 여행지 설명을 가져오는 함수
def gpt_prompt_attractions(city):
    query = f"Can you give me a description focused on the characteristics of {city} as a tourist destination?"
    while True:
        try:
            response = openai.ChatCompletion.create(
                model='gpt-3.5-turbo',
                messages=[
                        {"role": "system", "content": "You are a helpful tourist assistant."},
                        {"role": "user", 
                        "content": '''
                            When describing a city as a tourist destination, please provide a detailed description that includes its overall atmosphere, historical and cultural significance, and any distinctive features that contribute to the city's character.

                            Here's an example that best represents the features of New York as a tourist destination:
                
                                New York City, often referred to as "The Big Apple," is a vibrant metropolis known for its fast-paced lifestyle, iconic skyline, and cultural diversity. 
                                The city's atmosphere is electric, with bustling streets, bright lights, and an ever-present sense of movement. 
                                Its skyline is dominated by towering skyscrapers, including the Empire State Building and One World Trade Center. 
                                Times Square epitomizes the energy of the city, with its dazzling lights and bustling crowds. 
                                Central Park provides a green oasis amidst the urban landscape, offering a place for relaxation and recreation. 
                                The Statue of Liberty stands as a symbol of freedom and democracy, welcoming visitors from around the world. 
                                New York is also renowned for its cultural institutions, such as the Metropolitan Museum of Art and Broadway theaters, where world-class performances take place. 
                                The diverse neighborhoods, from the historic charm of Greenwich Village to the vibrant streets of Chinatown, reflect the city's multicultural fabric. 
                                The fast-paced atmosphere, coupled with the city's role as a global hub for finance, fashion, and media, creates a unique and dynamic environment.

                            Please use this format and style to describe the characteristics of {city} as a tourist destination.
                        '''},
                        {"role": "user", "content": query}
                        ]
                )
            return response.choices[0].message['content']
        
        except openai.error.RateLimitError:
            st.warning("Rate limit exceeded, waiting to retry...")
            time.sleep(5)
            
        except openai.error.APIError as e:
            st.error(':loudspeaker: 현재는 새롭게 도시명을 넣을 수 없습니다. 기존에 있는 도시명을 선택해 진행해 주세요.')
            st.write(f"OpenAI API returned an API Error: {e}")
            break
        
        except openai.error.Timeout as e:
            st.error(':loudspeaker: 현재는 새롭게 도시명을 넣을 수 없습니다. 기존에 있는 도시명을 선택해 진행해 주세요.')
            st.write(f"OpenAI API request timed out: {e}")
            break
        
        except openai.error.APIConnectionError as e:
            st.error(':loudspeaker: 현재는 새롭게 도시명을 넣을 수 없습니다. 기존에 있는 도시명을 선택해 진행해 주세요.')
            st.write(f"OpenAI API connection error: {e}")    
            break
        
        except openai.error.InvalidRequestError as e:
            st.error(':loudspeaker: 현재는 새롭게 도시명을 넣을 수 없습니다. 기존에 있는 도시명을 선택해 진행해 주세요.')
            st.write(f"OpenAI API invalid request: {e}")
            break
        
        except Exception as e:
            st.error(':loudspeaker: 현재는 새롭게 도시명을 넣을 수 없습니다. 기존에 있는 도시명을 선택해 진행해 주세요.')
            st.write(f"An unexpected error occurred: {e}")
            break

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
    perfumes_raw = pd.read_csv(perfume_file_path)
    # 텍스트 전처리 전, notes 열에서 결측치가 있는 행은 제거하고 진행
    # 결측치가 존재하는 경우, np.nan으로 결측치가 처리되어 float 타입으로 인식되어 전처리가 불가능함
    perfumes = perfumes_raw.dropna(subset=['notes'])
    perfumes['processed_notes'] = perfumes['notes'].apply(preprocess_text)
    return perfumes

# 추천 시스템
def recommend_perfumes_for_destination(description, tfidf_vectorizer, perfume_tfidf_matrix, perfumes, top_n=5):
    description_vector = tfidf_vectorizer.transform([description])
    cosine_sim = cosine_similarity(description_vector, perfume_tfidf_matrix).flatten()
    top_perfume_indices = cosine_sim.argsort()[-top_n:][::-1]  # 상위 n개 향수 추천
    recommended_perfumes = perfumes.iloc[top_perfume_indices]
    
    return recommended_perfumes
