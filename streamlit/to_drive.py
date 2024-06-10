import streamlit as st
import json
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# # Google Drive API 설정 함수
# def upload_to_drive(file_name, file_path):
#     # Streamlit secrets에서 서비스 계정 정보 로드
#     credentials_info = st.secrets["connections"]["gcs"]
#     credentials = service_account.Credentials.from_service_account_info(credentials_info)

#     # Google Drive API 서비스 생성
#     service = build('drive', 'v3', credentials=credentials)

#     # 파일 메타데이터 설정
#     file_metadata = {'name': file_name}

#     # 파일 업로드 준비
#     media = MediaFileUpload(file_path, mimetype='application/json')

#     # 파일 업로드
#     file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
#     st.write(f"File ID: {file.get('id')}")


def upload_to_drive_local(file_name, file_path):
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    SERVICE_ACCOUNT_FILE = 'forapp/dontpergetme-f0e0c66d678d.json'  # 서비스 계정 키 파일 경로
    
    # 서비스 계정 자격 증명 생성
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    
    # Google Drive API 서비스 생성
    service = build('drive', 'v3', credentials=creds)
    
    # 파일 메타데이터 설정
    file_metadata = {'name': file_name}
    
    # 파일 업로드 준비
    media = MediaFileUpload(file_path, mimetype='application/json')
    
    # 파일 업로드
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    st.write(f"File ID: {file.get('id')}")

# # 피드백 처리 함수
# def process_feedback(survey):
#     new_feedback = json.loads(survey.to_json())
    
#     file_path = "data/feedback.json"
#     os.makedirs(os.path.dirname(file_path), exist_ok=True)

#     # 기존 데이터를 읽어옴
#     if os.path.exists(file_path):
#         with open(file_path, "r", encoding="utf-8") as json_file:
#             existing_data = json.load(json_file)
#     else:
#         existing_data = []

#     # 새로운 피드백 추가
#     existing_data.append(new_feedback)

#     # 업데이트된 데이터를 JSON 파일로 저장
#     with open(file_path, "w", encoding="utf-8") as json_file:
#         json.dump(existing_data, json_file, ensure_ascii=False, indent=4)
    
#     # Google Drive에 업로드
#     upload_to_drive("feedback.json", file_path)
#     st.success(":floppy_disk: 소중한 피드백이 전송됐습니다.")

# 피드백 처리 함수
def process_feedback_local(survey):
    new_feedback = json.loads(survey.to_json())
    
    file_path = "data/feedback.json"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # 기존 데이터를 읽어옴
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as json_file:
            existing_data = json.load(json_file)
    else:
        existing_data = []

    # 새로운 피드백 추가
    existing_data.append(new_feedback)

    # 업데이트된 데이터를 JSON 파일로 저장
    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(existing_data, json_file, ensure_ascii=False, indent=4)
    
    # Google Drive에 업로드
    upload_to_drive_local("feedback.json", file_path)
    st.success(":floppy_disk: 소중한 피드백이 전송됐습니다.")
    
# Google Drive API 설정 함수
def upload_to_drive(file_name, data):
    credentials_info = st.secrets["connections"]["gcs"]["web"]
    credentials = service_account.Credentials.from_service_account_info(credentials_info)
    service = build('drive', 'v3', credentials=credentials)

    # 임시 파일에 데이터를 저장
    temp_file_path = f"/tmp/{file_name}"
    with open(temp_file_path, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

    # 파일 메타데이터 설정
    folder_id = "19xJsMBeLEZRFMHvFcJyFeMfKKtK6fr6p"  # 구글 드라이브 폴더 ID
    file_metadata = {'name': file_name, 'parents': [folder_id]}

    # 파일 업로드 준비
    media = MediaFileUpload(temp_file_path, mimetype='application/json')

    # 파일 업로드
    file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
    st.write(f"File ID: {file.get('id')}")
    st.write(f"File webViewLink: {file.get('webViewLink')}")

# 피드백 처리 함수
def process_feedback(survey):
    new_feedback = json.loads(survey.to_json())
    existing_data = []
    existing_data.append(new_feedback)

    # 업데이트된 데이터를 Google Drive에 업로드
    upload_to_drive("feedback.json", existing_data)
    st.success(":floppy_disk: 소중한 피드백이 전송됐습니다.")