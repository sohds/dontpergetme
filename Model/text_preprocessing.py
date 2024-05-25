#nltk 사용하지 않은 def 코드
import pandas as pd
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
import re

# CSV 파일 읽기 함수
def read_csv(file_path):
    return pd.read_csv(file_path)

# 간단한 어간 추출기 함수
def simple_stemmer(word):
    suffixes = ['ing', 'ly', 'ed', 'ious', 'ies', 'ive', 'es', 's', 'ment']
    for suffix in suffixes:
        if word.endswith(suffix):
            return word[:-len(suffix)]
    return word

# 텍스트 전처리 함수 정의
def preprocess_text(text, stop_words):
    # 소문자 변환
    text = text.lower()
    
    # 특수 문자 제거
    text = re.sub(r'\W', ' ', text)
    
    # 불용어 제거 및 어간 추출
    words = text.split()
    words = [simple_stemmer(word) for word in words if word not in stop_words]
    
    # 전처리된 단어들을 다시 하나의 문자열로 결합
    return ' '.join(words)

# 데이터 프레임의 텍스트 열 전처리 함수
def preprocess_dataframe(df, text_column, stop_words):
    df[text_column] = df[text_column].apply(lambda text: preprocess_text(text, stop_words))
    return df

# TF-IDF 벡터화 함수
def tfidf_vectorize(df, text_column):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(df[text_column])
    return tfidf_matrix, vectorizer

# TF-IDF 결과를 데이터 프레임에 추가하는 함수
def add_tfidf_to_dataframe(df, tfidf_matrix, vectorizer):
    tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=vectorizer.get_feature_names())
    return pd.concat([df, tfidf_df], axis=1)

# 전처리된 데이터 저장 함수
def save_csv(df, file_path):
    df.to_csv(file_path, index=False)

# 전체 프로세스를 실행하는 메인 함수
def main(input_file, output_file, text_column):
    # 데이터 읽기
    df = read_csv(input_file)
    
    # 불용어 목록 설정
    stop_words = set(ENGLISH_STOP_WORDS)
    
    # 데이터 전처리
    df = preprocess_dataframe(df, text_column, stop_words)
    
    # TF-IDF 벡터화
    tfidf_matrix, vectorizer = tfidf_vectorize(df, text_column)
    
    # TF-IDF 결과를 데이터 프레임에 추가
    df = add_tfidf_to_dataframe(df, tfidf_matrix, vectorizer)
    
    # 전처리된 데이터 저장
    save_csv(df, output_file)

# 파일 경로 및 텍스트 열 이름 설정
input_file = 'final_perfume-info.csv'
output_file = 'pre_data3.csv'
text_column = 'notes'

# 메인 함수 실행
main(input_file, output_file, text_column)
