import streamlit as st
import pandas as pd
import openai
import json
from PIL import Image
import time
from recommend import *
import os

# st.set_page_config(page_title="Don't PERget Me", layout="wide")

# streamlit 웹 배포를 위한 절대경로 포함
def get_absolute_path(relative_path):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, relative_path)

big_path = get_absolute_path('transparent.png')
tiny_path = get_absolute_path('tiny.png')

# 여백을 위한 이미지
big = Image.open(big_path)   # 경로에 있는 이미지 파일을 통해 변수 저장
tiny = Image.open(tiny_path)

# OpenAI API 키 로드
api_key = get_absolute_path('../Data/Prompting/ChatGPT_api_key.json')
with open(api_key, 'r', encoding='utf8') as f:
    data = json.load(f)

st.title("Don't PERget Me: 여행지 기반 향수 추천 시스템")
st.write('안녕하세요, 저희는 2024-1 머신러닝기반데이터분석 5조 _돈펄겟미_ 팀 입니다. 기말고사 팀 프로젝트로 "여행지 기반 향수 추천 시스템"을 구현해 보았습니다. 저희의 프로젝트를 웹으로 체험해 보고 가세요!')
st.info('**<Demo Page 사용설명서>**'
        '\n 1. 나라와 도시를 선택 후 추천 버튼 클릭'
        '\n 2. 도시가 없을 경우, 직접 영어로 도시명 기입 후 추천 버튼 클릭'
        '\n      - 직접 영어로 도시명 기입하기 위해서는 나라 임의적으로 선택 후 도시에서 Other (Specify) 선택 후 기입 가능'
        '\n - 언어가 영어로 제공됩니다.'
        )
st.write('- **베타(Beta) 서비스**: 체험해보고 싶은 여행 도시명 직접 기입하기'
            '\n    - 최종 발표로부터 2일 후, 즉 **6월 14일 00:00**부터는 사용 불가능 합니다.')

st.image(tiny)

# OpenAI API 설정
openai.api_key = data['API_KEY']


# 데이터 파일 경로 설정
destination_file_path = get_absolute_path('../Data/Prompting/dataset/destination_mood.csv')
perfume_file_path = get_absolute_path('../Data/preprocess-data/final_perfume-info.csv')

# 데이터 로드
destinations = pd.read_csv(destination_file_path)
perfumes = load_perfume_data(perfume_file_path)

st.subheader('체험을 위한 Input 정보 넣기')

# 성별, 국가, 도시 선택을 한 행에 배치
col1, col2, col3 = st.columns(3)

with col1:
    gender_option = st.radio("성별을 선택하세요.", ('unisex', 'women', 'men'))

with col2:
    countries = sorted(destinations['nation'].unique().tolist())
    selected_country = st.selectbox("여행지의 국가를 선택하세요.", countries)

with col3:
    cities = sorted(destinations[destinations['nation'] == selected_country]['city'].tolist())
    cities.append("Other (Specify)")
    selected_city = st.selectbox("여행지 도시명을 선택하세요.", cities)

# 선택된 성별에 따라 향수 데이터 필터링
if gender_option == 'women':
    perfumes = perfumes[perfumes['for_gender'].str.contains('for women|unisex', na=False)]
elif gender_option == 'men':
    perfumes = perfumes[perfumes['for_gender'].str.contains('for men|unisex', na=False)]

# 여행지 분위기 추출
tfidf_vectorizer, destination_tfidf_matrix, destinations = extract_destination_moods(destinations, n_topics=18)

# 향수 데이터 TF-IDF 매트릭스 생성
perfume_tfidf_matrix = tfidf_vectorizer.transform(perfumes['processed_notes'])

if col2.button("향수 추천받기"):
    if selected_city:
        if selected_city in destinations['city'].values:
            description = destinations[destinations['city'] == selected_city]['description'].values[0]
            moods = destinations[destinations['city'] == selected_city]['moods'].values[0]
        else:
            description = gpt_prompt_attractions(selected_city)
            moods = []  # 새로 생성된 도시 설명에는 분위기 키워드가 없음

        with st.container():
            with st.spinner('향수를 추천하고 있어요...'):
                time.sleep(2)
                recommended_perfumes = recommend_perfumes_for_destination(description, tfidf_vectorizer, perfume_tfidf_matrix, perfumes, top_n=5)

        st.markdown('---')        
        st.success(f':trophy:  **{selected_city}**의 향수 추천이 성공적으로 이루어 졌어요!'
                   '\n 스크롤해서 결과를 확인해 주세요.')
        st.image(tiny)
        
        st.subheader(f'{selected_city}의 분위기 설명')
        st.write(f":globe_with_meridians: **{selected_city}**의 분위기 키워드: {', '.join(moods)}")
        st.write(f":ribbon: **{selected_city}**의 분위기 설명 텍스트:")
        with st.expander(":mag: See Explanation Here: "):
            st.write(description)
        st.write('\n\n\n')
        
        st.image(tiny)
        st.subheader(f'돈펄겟미의 {selected_city}의 Top-5 Perfumes Recommendation')
        with st.expander(":hibiscus: 어울리는 향수를 버튼을 눌러 확인해 보세요!"):
            cols = st.columns(len(recommended_perfumes))
            i = 0
            for col, (_, perfume) in zip(cols, recommended_perfumes.iterrows()):
                i += 1
                col.write(f"{i}. {perfume['name']}")
                col.image(perfume['image'], caption=perfume['name'])
                
            st.write()
        
        st.write(f'이 향수가 당신을 {selected_city}로 데려가게 해줄 거예요. :sparkles:')
            
    else:
        st.error("**도시를 선택**하거나 **도시명을 입력**해 주세요.")
        

st.image(big)
st.image(big)
st.markdown('---')
st.warning('**Project Information**'
        '\n - 저희 프로젝트를 관심있게 지켜봐주셔서 감사합니다. :seedling:'
        '\n - Project Contributors: 김수아, 박서진, 오서연'
        '\n     - 배포 by. 오서연'
        '\n - 프로젝트 관련 질문이나 제안사항은 이메일 sohtks@swu.ac.kr로 받습니다.'
        )