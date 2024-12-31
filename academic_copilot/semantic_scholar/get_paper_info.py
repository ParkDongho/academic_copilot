import os
import requests
from requests import Session
import time
import yaml
import pandas as pd
from typing import Any, Dict
import re
import dotenv

from selenium.webdriver.common.by import By
from academic_copilot.semantic_scholar.academic_database import search_from_database
from academic_copilot.util.env import *

dotenv.load_dotenv()


def create_yaml(metadata, paper_id):
    """
    Create a YAML file from the metadata of a paper.

    :param metadata: metadata of a paper
    :param paper_id: semantic scholar paper id
    :return: yaml data
    """
    authors = [author['name'] for author in metadata.get('authors', [])]
    title = metadata.get('title', 'Unknown Title')
    date = metadata.get('publicationDate', 'Unknown Date')
    year = metadata.get('year', 'Unknown Year')
    venue = metadata.get('venue', 'Unknown Venue')
    abstract = clean_abstract(metadata.get('abstract', 'No abstract available.'))
    citation_count = metadata.get('citationCount', 'Unknown')
    external_ids = metadata.get('externalIds', {})

    journal_list = load_journal_list(JOURNAL_LIST_PATH)

    # external_ids에 새로운 키 추가
    external_ids['SEMANTIC'] = paper_id

    external_ids['IEEE'] = None
    external_ids['ACM'] = None
    doi = external_ids.get('DOI', None)
    if doi != None:
        journal_key = get_journal_id_from_doi(doi)
        if journal_key[0] == "IEEE":
            external_ids['IEEE'] = journal_key[1]
        elif journal_key[0] == "ACM":
            external_ids['ACM'] = journal_key[1]


    short_name = "Unknown Venue"
    for key in journal_list:
        if key.lower() in venue.lower():
            short_name = journal_list[key]
            break

    yaml_data = {
        'title': title,
        'date': date,
        'authors': authors,
        'year': year,
        'venue': venue,
        'venue_short': short_name,
        'abstract': abstract,
        'citation_count': citation_count,
        'external_ids': external_ids
    }
    return yaml_data

def clean_abstract(abstract: str) -> str:
    # "$\\time $"와 같은 패턴에서 닫는 $ 이전의 공백 제거
    return re.sub(r'(\\\S+)\s+\$', r'\1$', abstract)



def get_paper_metadata(session: Session, paper_id: str,
                       fields: str = 'title,authors,year,venue,abstract,citationCount') -> Dict[str, Any]:
    """
    Get paper metadata from Semantic Scholar API.

    :param session:
    :param paper_id:
    :param fields:
    :return:
    """

    params = {
        'fields': fields,
    }
    headers = {
        'X-API-KEY': S2_API_KEY,
    }

    url = f'https://api.semanticscholar.org/graph/v1/paper/{paper_id}'
    with session.get(url, params=params, headers=headers) as response:
        response.raise_for_status()
        return response.json()


def load_journal_list(journal_list_path):
    """
    Journal list CSV 파일을 읽어 딕셔너리로 반환
    :param journal_list_path: journal list에 대한 csv 파일 경로
    :return: jounal_list_dict journal list를 딕셔너리로 변환하여 반환
    """
    # CSV 파일을 읽어 'journal'과 'short' 컬럼을 딕셔너리로 반환
    df = pd.read_csv(journal_list_path)
    return dict(zip(df['journal'], df['name_short']))




def get_paper_info(s2id_file):
    """
    Get paper metadata from Semantic Scholar API and save as YAML files.
    :param s2id_file: paper_list 가 있는 파일 경로
    :return:
    """
    # Change working directory to output directory
    PAPER_INFO_PATH = os.environ.get('PAPER_INFO_PATH', '')
    os.chdir(PAPER_INFO_PATH)

    with open(s2id_file, 'r') as s2id_file:
        s2ids = [line.strip() for line in s2id_file.readlines()]
    fields = 'title,authors,year,venue,abstract,citationCount,externalIds,publicationDate'
    for paper_id in s2ids:
        with Session() as session:
            paper_metadata = get_paper_metadata(session, paper_id, fields=fields)

        if not paper_metadata:
            print(f'No metadata found for paper ID {paper_id}')
            continue

        yaml_content = create_yaml(paper_metadata, paper_id)
        output_filename = f'{paper_id}.yaml'
        with open(output_filename, 'w') as yamlfile:
            yaml.dump(yaml_content, yamlfile, default_flow_style=False, allow_unicode=True)

        time.sleep(3)
        print(f'Wrote YAML for paper ID {paper_id} to {output_filename}')




def save_paper_info(s2id_file):
    """
    Get paper metadata from Semantic Scholar API and save as YAML files.
    :param s2id_file:
    :return:
    """

    PAPER_INFO_PATH = os.environ.get('PAPER_INFO_PATH', '')
    # Create output directory if it doesn't exist
    os.makedirs(PAPER_INFO_PATH, exist_ok=True)
    get_paper_info(s2id_file)


def save_paper_info_from_paper_list(new_paper_list):
    """
    `new_paper_list.txt` 파일을 읽어 paper_info를 yaml 확장자로 저장합니다.

    :param new_paper_list: `new_paper_list.txt` 파일 경로
    :return: 반환값 없음
    """

    # Change working directory to output directory
    PAPER_INFO_PATH = os.environ.get('PAPER_INFO_PATH', '')
    # NEW_PAPER_LIST = os.environ.get('NEW_PAPER_LIST', '')

    os.makedirs(PAPER_INFO_PATH, exist_ok=True)
    os.chdir(PAPER_INFO_PATH)

    with open(new_paper_list, 'r') as s2id_file:
        s2ids = [line.strip() for line in s2id_file.readlines()]
    for paper_id in s2ids:
        save_paper_info_from_semantic_id(paper_id)


def save_paper_info_from_semantic_id(semantic_id, ieee_paper_id=None, acm_paper_id=None, doi_id=None):
    PAPER_INFO_PATH = os.environ.get('PAPER_INFO_PATH', '')
    os.makedirs(PAPER_INFO_PATH, exist_ok=True)
    download_paper_info(semantic_id,
                        ieee_paper_id=ieee_paper_id,
                        acm_paper_id=acm_paper_id,
                        doi_id=doi_id)


def download_paper_info(semantic_id, ieee_paper_id=None, acm_paper_id=None, doi_id=None):
    # Change working directory to output directory
    PAPER_INFO_PATH = os.environ.get('PAPER_INFO_PATH', '')
    os.chdir(PAPER_INFO_PATH)

    fields = 'title,authors,year,venue,abstract,citationCount,externalIds,publicationDate'
    with Session() as session:
        paper_metadata = get_paper_metadata(session, semantic_id, fields=fields)

    if not paper_metadata:
        print(f'No metadata found for paper ID {semantic_id}')
        return None

    yaml_content = create_yaml(paper_metadata, semantic_id)
    if ieee_paper_id:
        yaml_content['external_ids']['IEEE'] = ieee_paper_id
    if acm_paper_id:
        yaml_content['external_ids']['ACM'] = acm_paper_id
    if doi_id:
        yaml_content['external_ids']['DOI'] = doi_id

    output_filename = f'{semantic_id}.yaml'
    with open(output_filename, 'w') as yamlfile:
        yaml.dump(yaml_content, yamlfile, default_flow_style=False, allow_unicode=True)

    time.sleep(3)
    print(f'Wrote YAML for paper ID {semantic_id} to {output_filename}')


def get_redirected_url(doi):
    """
    DOI를 통하여 웹페이지에 접속하여 최종 리다이렉션된 URL을 반환.
    """

    base_url = "https://doi.org/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(base_url + doi, allow_redirects=True, timeout=10, headers=headers)
        response.raise_for_status()
        return response.url
    except requests.exceptions.RequestException as e:
        print(f"Error accessing DOI: {e}")
        return None


def identify_source_and_id(url):
    """
    URL에서 출처와 DOI 또는 문서 ID를 추출합니다.
    """
    if "ieee.org" in url:
        source = "IEEE"
        match = re.search(r"/document/(\d+)", url)
        document_id = match.group(1) if match else "Unknown"
    elif "dl.acm.org" in url:
        source = "ACM"
        match = re.search(r"/doi/(10\.\d{4,}/.+)", url)
        document_id = match.group(1) if match else "Unknown"
    else:
        source = "Other"
        document_id = "Unknown"
    return source, document_id

def get_journal_id_from_doi(doi):
    """
    doi 입력을 받고 Journal Key/ID 쌍을 추출합니다.

    **Example :**

    - doi -> ("IEEE", "12345678")
    - doi -> ("ACM", doi)
    """
    redirected_url = get_redirected_url(doi)
    if redirected_url:
        source, document_id = identify_source_and_id(redirected_url)
        return source, document_id
    else:
        print("Failed to retrieve URL.")
        return None, None


def get_semantic_id_from_doi(doi_id, ieee_paper_id=None, acm_paper_id=None):
    """
    Get the Semantic **Scholar ID** using **DOI**. `(DOI -> Semantic Scholar ID)`

    - Step 1: search for the DOI number in the YAML files
    - Step 2: if not found, fetch Semantic Scholar ID from DOI
    - Step 2.1: Create new YAML file with this information

    :param doi_id: DOI number
    :param ieee_paper_id: IEEE paper number
    :param acm_paper_id: ACM paper number
    :returns: Semantic Scholar ID
    """

    # Step 1: search for the DOI number in the YAML files
    semantic_id = search_from_database(
        "DOI", doi_id,
        "SEMANTIC")

    # Step 2: if not found, fetch Semantic Scholar ID from DOI
    if not semantic_id:
        url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi_id}?fields=paperId"
        response = requests.get(url)

        if response.status_code == 200:
            semantic_id = response.json().get('paperId', None)
            # Step 2.1: Create new YAML file with this information
            save_paper_info_from_semantic_id(semantic_id,
                                             ieee_paper_id=ieee_paper_id, acm_paper_id=acm_paper_id, doi_id=doi_id)

            # return : Step 2의 결과가 있을 경우
            return semantic_id

        # return : Step 2의 결과가 없을 경우
        return None

    # return : Step 1(database 검색)의 결과가 있을 경우
    return semantic_id


def get_semantic_id_from_ieee_id(ieee_paper_id, driver, acm_paper_id=None):
    """
    Get the Semantic Scholar ID using IEEE paper number.

    - **Step 1:** search for the IEEE paper number in the YAML files
    - **Step 2:** if not found, fetch DOI and Semantic Scholar ID
    - Step 2.1: fetch semantic scholar id from DOI

    :param ieee_paper_id: IEEE paper number
    :param driver: Selenium WebDriver
    :param acm_paper_id: ACM paper number
    :returns: Semantic Scholar ID
    """

    # Step 1: search for the IEEE paper number in the YAML files
    semantic_id = search_from_database(
        "IEEE", ieee_paper_id,
        "SEMANTIC")

    # Step 2: if not found, fetch DOI from ieee_id
    if not semantic_id:
        tmp_doi = get_doi_from_ieee_id(ieee_paper_id, driver)

        # Step 2.1: fetch semantic scholar id from DOI
        return get_semantic_id_from_doi(tmp_doi, ieee_paper_id=ieee_paper_id, acm_paper_id=acm_paper_id)

    return semantic_id

def get_doi_from_ieee_id(ieee_id, driver):
    """
    IEEE 문서 번호를 사용하여 DOI를 가져옵니다.

    selenium driver를 사용하여 ieeexplore에서 doi를 크롤링합니다.

    :param ieee_id: ieee document number
    :param driver: selenium driver
    :return: doi_id
    """
    try:
        # IEEE 문서 URL
        url = f"https://ieeexplore.ieee.org/document/{ieee_id}"
        driver.get(url)

        # DOI 정보 가져오기
        doi_element = driver.find_element(By.CSS_SELECTOR,
            "#xplMainContentLandmark > div > xpl-document-details > div > div.document-main.global-content-width-w-rr > "
            "div > div.document-main-content-container.col-19-24 > section > div.document-main-left-trail-content > "
            "div > xpl-document-abstract > section > div.abstract-desktop-div.hide-mobile.text-base-md-lh > "
            "div.row.g-0.u-pt-1 > div:nth-child(2) > div.u-pb-1.stats-document-abstract-doi > a")

        doi_text = doi_element.accessible_name # DOI 텍스트 추출
        return doi_text

    except Exception as e:
        return f"오류 발생: {e}"



if __name__ == "__main__":
    save_paper_info(NEW_PAPER_LIST)

