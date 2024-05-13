import requests
from bs4 import BeautifulSoup
import csv
import argparse


def get_args_parser():
    parser = argparse.ArgumentParser(
        'get Fragrantica Perfume URL', add_help=False)
    parser.add_argument('--olfactory', default='chypre', 
                        choices=['floral', 'amber', 'aromatic', 'woody', 'leather', 'citrus', 'chypre'], type=str)
    parser.add_argument('--output_dir', default='dataset/url/', type=str,
                        help='path where to save, empty for no saving')
    return parser


def main(args):
    # 첫 번째 페이지 URL
    url = "https://www.fragrantica.com/groups/" + args.olfactory + ".html"

    # User-Agent 헤더 추가
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
    }

    # 웹사이트에 GET 요청 보내기
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # 요청이 성공했는지 확인

    # 페이지의 HTML 내용 파싱
    soup = BeautifulSoup(response.text, 'html.parser')

    # 향수 링크를 저장할 리스트
    perfume_links = []

    # 모든 향수의 링크 추출
    divs = soup.select('div.cell.large-6')  # 각 향수 정보를 포함하는 div 선택
    for div in divs:
        h3_tag = div.find('h3')
        a_tag = h3_tag.find('a') if h3_tag else None
        if a_tag and 'href' in a_tag.attrs:
            perfume_links.append("https://www.fragrantica.com" + a_tag['href'])

    # CSV 파일로 저장
    output = args.output_dir + 'perfume_urls_' + args.olfactory + '.csv'
    with open(output, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for url in perfume_links:
            writer.writerow([url])

    print("URLs have been successfully saved to '" + output + "'.")
    

if __name__ == '__main__':
    parser = get_args_parser()
    args = parser.parse_args()
    main(args)