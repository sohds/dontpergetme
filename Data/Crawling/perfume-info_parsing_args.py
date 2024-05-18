# 라이브러리 임포트
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import argparse
import pandas as pd


# argument parser 지정
def get_args_parser():
    parser = argparse.ArgumentParser(
        'get Fragrantica Perfume URL', add_help=False)
    parser.add_argument('--olfactory', default='chypre', 
                        choices=['floral', 'amber', 'aromatic', 'woody', 'leather', 'citrus', 'chypre'], type=str)
    parser.add_argument('--index', type=int, help='csv 속 url 접근하는 index')
    return parser


# main 함수 지정
def main(args):
    # Chrome 드라이버 생성
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    # options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_argument("start-maximized")
    # options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    # options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # options.add_experimental_option("useAutomationExtension", False)
    
    driver = webdriver.Chrome(service=service, options=options)

    # 향수 정보를 저장할 딕셔너리
    perfume_data = {}

    # csv 파일
    file_path = f'dataset/url/perfume_urls_{args.olfactory}.csv'
    file_csv = pd.read_csv(file_path, header=None)

    try:
        # 향수 제품페이지로 이동
        url = file_csv.iloc[args.index, 0]
        driver.get(url)
        print(args.index, '접근:', url)
        print('Crawling START!')
        # time.sleep(random.uniform(3, 7))  # 랜덤한 시간 지연

        # 향수 이름과 성별 정보 가져오기
        name_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "h1[itemprop='name']"))
        )
        perfume_name = name_element.text.strip()
        gender_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "h1[itemprop='name'] small"))
        )
        gender = gender_element.text.strip()
        company_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "span[itemprop='name']"))
        )
        company_name = company_element.text.strip()
        perfume_data['name'] = perfume_name
        perfume_data['company'] = company_name
        
        # 향수 이미지 URL 가져오기
        image_element = driver.find_element(By.CSS_SELECTOR, "img[itemprop='image']")
        image_url = image_element.get_attribute("src")
        perfume_data['image'] = image_url
        
        perfume_data['for_gender'] = gender
        

        # main accord의 note와 width를 저장할 딕셔너리
        main_accord = {}

        # main accord가 표시될 때까지 기다림 (최대 10초 대기)
        main_accord_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#main-content > div:nth-child(1) > div.small-12.medium-12.large-9.cell > div > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div"))
        )

        # accord-bar 요소 추출
        accord_elements = main_accord_element.find_elements(By.CLASS_NAME, "accord-bar")

        # accord-bar에서 note와 width 추출하여 딕셔너리에 저장
        for element in accord_elements:
            note = element.text.strip()
            width = element.get_attribute("style").split("width: ")[1].split("%")[0]
            main_accord[note] = width

        perfume_data['main accords'] = main_accord

        # 각각의 노트를 저장할 딕셔너리
        notes = {"top notes": [], "middle notes": [], "base notes": []}
        try:
            # Top Notes
            top_note_elements = WebDriverWait(driver, 10).until(
                EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "#pyramid > div:nth-child(1) > div > div:nth-child(2) > div:nth-child(4)"))
            )
            notes["top notes"] = ', '.join([note_element.text.strip() for note_element in top_note_elements])

            # Middle Notes
            middle_note_elements = WebDriverWait(driver, 10).until(
                EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "#pyramid > div:nth-child(1) > div > div:nth-child(2) > div:nth-child(6)"))
            )
            notes["middle notes"] = ', '.join([note_element.text.strip() for note_element in middle_note_elements])

            # Base Notes
            base_note_elements = WebDriverWait(driver, 10).until(
                EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "#pyramid > div:nth-child(1) > div > div:nth-child(2) > div:nth-child(8)"))
            )
            notes["base notes"] = ', '.join([note_element.text.strip() for note_element in base_note_elements])

            # 향수 정보에 각각의 노트를 저장
            perfume_data.update(notes)
            
        except Exception as e:
            print("노트를 가져오는 중 오류가 발생했습니다:", e)


    except Exception as e:
        print("향수 정보를 가져오는 중 오류가 발생했습니다:", e)
    finally:
        print('향수 정보 크롤링 DONE!')
        # 브라우저 닫기
        driver.quit()

    # CSV 파일에 저장하기 위해 문자열로 변환
    for key in perfume_data:
        if isinstance(perfume_data[key], list):
            perfume_data[key] = str(perfume_data[key])

    # 기존 CSV 파일에 향수 정보 추가
    try:
        file_path = 'dataset/perfume-info-raw/used_dataset.csv'
        # amber ~ chypre 맡았으면 파일명(amber_aromatic_chypre)으로 변경해주고, 
        # citrus ~ leather 맡았으면 파일명(citrus_floral_leather)으로 변경
        # leather은 used_dataset에 바로 넣기
        # 이 세 파일 나중에 전처리 전에 병합할 예정
        file_exists = pd.read_csv(file_path, header=0).shape[0] > 0

        with open(file_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=perfume_data.keys())
            if not file_exists:
                writer.writeheader()
            # 딕셔너리의 값들이 쉼표로 구분되도록 수정
            perfume_data_values = {key: ', '.join(value.split('\n')) if isinstance(value, str) else value for key, value in perfume_data.items()}
            writer.writerow(perfume_data_values)

        print("CSV 파일에 향수 정보를 성공적으로 저장했습니다.")
    except Exception as e:
        print("CSV 파일에 향수 정보를 저장하는 중 오류가 발생했습니다:", e)


# START
if __name__ == '__main__':
    parser = get_args_parser()
    args = parser.parse_args()
    main(args)