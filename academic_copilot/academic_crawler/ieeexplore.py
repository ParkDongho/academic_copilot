from bs4 import BeautifulSoup
import argparse
import os
import json
import requests
from requests import Session
import argparse
import re

from selenium import webdriver
import time

from bs4 import Tag, NavigableString
from academic_copilot.util.env import *
from academic_copilot.semantic_scholar.get_paper_info import get_semantic_id_from_ieee_id
from academic_copilot.semantic_scholar.get_paper_info import get_semantic_id_from_doi


def convert_to_markdown_link(title):
    # 1. 제목 데이터를 소문자로 변환
    # 2. 공백을 %20으로 변환 (Obsidian 내부 링크 형식, 하이픈은 지원 안함)
    # 3. 특수 문자를 제거 (단, 숫자와 하이픈은 유지)
    link = re.sub(r'[^\w\s-]', '', title)  # 특수문자 제거
    link = link.lower().replace(' ', '%20')  # 소문자로 변환 및 공백 -> 하이픈
    return f"#{link}"

def parsePaper(input, ieee_paper_info):
    sections = []
    fig_table_data = []

    for section in input:
        single_section, fig_table_tmp= parseSection(section, ieee_paper_info)
        sections = sections + single_section
        fig_table_data = fig_table_data + fig_table_tmp
    return (sections, fig_table_data)



def parseSection(input, ieee_paper_info):

    single_section = []
    fig_table_data = []
    subsec_list = []
    heading_level = None
    section_title = ""
    section_content = ""
    section_id = ""

    for paragraph in input.contents:
        # Tag인지 NavigableString인지 확인
        if isinstance(paragraph, NavigableString):
            if (paragraph.strip() != ""):
                print(f"Invalid NavigableString!: {paragraph}")
            continue

        # subsection 처리
        if 'section_2' in paragraph.get('class', "div"):
            subsec_tmp, fig_table_data_tmp = parseSection(paragraph, ieee_paper_info)
            subsec_list = subsec_list + subsec_tmp
            fig_table_data = fig_table_data + fig_table_data_tmp

        else:
            if (paragraph.name in ["h3", "h4", "h5", "h6"]) or ('header' in paragraph.get('class', "div")):
                for level in range(2, 7):
                    heading_tag = input.find(f'h{level}')
                    if heading_tag:
                        heading_level = level
                        section_title = heading_tag.text.strip()
                        section_id = input.attrs['id']
                        break

            elif paragraph.name == "disp-formula":
                # 찾고자 하는 <span> 태그와 그 내부의 텍스트를 추출
                span_tag = paragraph.find('span', class_="tex tex2jax_ignore")
                if span_tag and span_tag.text:
                    latex_code = span_tag.text #텍스트를 가져와서 공백 제거
                    section_content += f"\n\n$$\n{latex_code}\n$$\n\n"
                else:
                    print("No latex code found in disp-formula")

            # 본문 처리
            elif paragraph.name == "p":
                section_content += f"{parseParagraph(paragraph, ieee_paper_info)}\n\n"

            elif paragraph.name == "ol":
                for li in paragraph.find_all('li'):
                    section_content += f"1. {parseParagraph(li.contents[0], ieee_paper_info)}\n"
                section_content += "\n\n"

            elif paragraph.name == "ul":
                for li in paragraph.find_all('li'):
                    section_content += f"- {parseParagraph(li.contents[0], ieee_paper_info)}\n"
                section_content += "\n\n"



            # Figure 생성
            elif any(cls in paragraph.get('class', []) for cls in ["figure", "figure-full", "table"]):
                # 이미지와 캡션 파싱
                image_wrap = paragraph.find('div', class_='img-wrap')
                fig_caption = paragraph.find('div', class_='figcaption')

                if image_wrap and fig_caption:
                    # 링크와 이미지 경로 추출
                    link_tag = image_wrap.find('a')
                    img_tag = link_tag.find('img') if link_tag else None
                    image_href = link_tag['href'] if link_tag else ''
                    alt_text = img_tag.get('alt', 'Image') if img_tag else ''
                    data_fig_id = paragraph.get('id') if img_tag else ''

                    # 캡션 추출
                    caption_title = fig_caption.find('b', class_='title').get_text(strip=True) \
                        if fig_caption.find('b', class_='title') else ''

                    if fig_caption:  # fig_caption이 None이 아닌지 먼저 확인
                        # 먼저 <p> 태그를 찾음
                        p_tag = fig_caption.find('p')

                        # <p> 태그가 존재하면 해당 텍스트를 사용
                        if p_tag:
                            caption_text = p_tag.get_text(strip=True)
                        else:
                            # <p> 태그가 없으면, fig_caption.contents[1]을 사용하기 전에 인덱스가 안전한지 확인
                            if len(fig_caption.contents) > 1:
                                caption_text = fig_caption.contents[1]

                    alt_text = alt_text.replace("\n", "")

                    img_file_name = f"ieee_{ieee_paper_info['ieee_paper_id']}_{data_fig_id}.gif"
                    img_file_path = f"{ieee_paper_info['relative_img_dir']}/{img_file_name}"

                    # 마크다운 형식으로 변환
                    markdown_output = f"![{alt_text}]({img_file_path})\n\n**{caption_title}** {caption_text}"

                    # 섹션 내용에 추가
                    section_content += f"\n{markdown_output}\n\n"
                    fig_table_data.append({
                        "image_href": f"https://ieeexplore.ieee.org/{image_href}",
                        "img_file_name": img_file_name,
                        "data_fig_id": data_fig_id
                    })

                else:
                    section_content += "\nFigure could not be parsed.\n"


            else:
                print("\n\n/home/parkdongho/dev/academic_copilot/academic_copilot/academic_crawler/ieeexplore.py:144 Unhandled Tag:")
                print(paragraph)


        single_section = [(heading_level, section_title, section_content, section_id)] + subsec_list

    return (single_section, fig_table_data)

def parseParagraph(paragraph, ieee_paper_info):

        # 본문 처리
        paragraph_contetns_list = []
        if isinstance(paragraph, NavigableString):
            return paragraph.text
        else:
            for paragrph_element in paragraph.contents:
                if isinstance(paragrph_element, NavigableString):
                    paragraph_contetns_list.append(paragrph_element.text)

                elif isinstance(paragrph_element, Tag):
                    # inline formula
                    if paragrph_element.name == "inline-formula":
                        latex_code = paragrph_element.find('script', {'type': 'math/tex'}).text
                        latex_code = latex_code.replace("\n", "")
                        paragraph_contetns_list.append(f"${latex_code}$")

                    # disp-formula
                    elif paragrph_element.name == "disp-formula":
                        span_tag = paragrph_element.find('span', class_="tex tex2jax_ignore")
                        if span_tag and span_tag.text:
                            latex_code = span_tag.text
                            latex_code = latex_code.replace("\n", "")
                            paragraph_contetns_list.append(f"\n\n$$\n{latex_code}\n$$\n\n")

                    # bold, italic 처리
                    elif paragrph_element.name == "i":
                        paragraph_contetns_list.append(f"*{paragrph_element.text}*")
                    elif paragrph_element.name == "b":
                        paragraph_contetns_list.append(f"**{paragrph_element.text}**")


                    # 인용문 처리
                    elif paragrph_element.name == "a":
                        if paragrph_element.attrs['ref-type'] == "bibr":
                            link_text = paragrph_element.text
                            if paragrph_element.text[0] == "[":
                                link_text = paragrph_element.text.replace("[", "\[")
                            if paragrph_element.text[-1] == "]":
                                link_text = link_text.replace("]", "\]")
                            paragraph_contetns_list.append(f"[{link_text}]({paragrph_element.attrs['anchor']})")

                        elif paragrph_element.attrs['ref-type'] == "fig":
                            anchor = paragrph_element.attrs['anchor']
                            img_name = next((img for img in ieee_paper_info["img_info"] if img["data_fig_id"] == anchor), None)
                            img_path = f"{ieee_paper_info['relative_img_dir']}/{img_name['img_file_name']}" if img_name else "none"
                            paragraph_contetns_list.append(f"[{paragrph_element.text}]({img_path})")

                        elif paragrph_element.attrs['ref-type'] == "table":
                            anchor = paragrph_element.attrs['anchor']
                            img_name = next((img for img in ieee_paper_info["img_info"] if img["data_fig_id"] == anchor), None)
                            img_path = f"{ieee_paper_info['relative_img_dir']}/{img_name['img_file_name']}" if img_name else "none"
                            paragraph_contetns_list.append(f"[{paragrph_element.text}]({img_path})")

                        elif paragrph_element.attrs['ref-type'] == "sec":
                            anchor = paragrph_element.attrs['anchor']
                            section_link_title = str(next((item[1] for item in ieee_paper_info["section_info"] if item[3] == anchor), None))
                            section_path = f"{convert_to_markdown_link(section_link_title)}" if section_link_title else "none"
                            paragraph_contetns_list.append(f"[{paragrph_element.text}]({section_path})")

                        elif paragrph_element.attrs['ref-type'] == "fn":
                            paragraph_contetns_list.append(f"[{paragrph_element.text}]({paragrph_element.attrs['anchor']})")

                        elif paragrph_element.attrs['ref-type'] == "disp-formula":
                            paragraph_contetns_list.append(f"[{paragrph_element.text}]({paragrph_element.attrs['anchor']})")

                        else:
                            print("Unhandled Link: ", paragrph_element.text, ", ", paragrph_element.attrs['ref-type'], ", ", paragrph_element.attrs['anchor'])
                    else:
                        print("Unhandled Tag: academic_copilot/academic_crawler/ieeexplore.py:221")
                        print(paragrph_element.name)
                        paragraph_contetns_list.append(paragrph_element.text)

            return "".join(paragraph_contetns_list)


# Function to extract content and convert to Markdown
def html_to_markdown(driver, ieee_paper_info):


    time.sleep(5)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # Extract sections and process paragraphs
    sections, fig_table_data = parsePaper(soup.find_all('div', class_=['section']), ieee_paper_info)

    markdown_content = ""
    for heading_level, section_title, section_content, section_id in sections:
        markdown_content += f"{'#' * heading_level} {section_title}\n\n{section_content}\n\n"

    ieee_paper_info['img_info'] = fig_table_data
    ieee_paper_info['section_info'] = sections
    return (markdown_content, ieee_paper_info)


def download_images(driver, ieee_paper_info):
    """
    셀레니움과 쿠키를 사용하여 이미지 다운로드 함수

    Args:
        driver (webdriver): Selenium WebDriver 인스턴스
    """
    # 디렉토리 생성
    os.makedirs(ieee_paper_info['final_img_dir'], exist_ok=True)

    data = ieee_paper_info["img_info"]

    # Selenium에서 쿠키 가져오기
    cookies = driver.get_cookies()
    session = Session()

    # requests 세션에 쿠키 추가
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])

    # 이미지 다운로드
    for item in data:
        image_url = item.get('image_href')
        file_name = item.get('img_file_name')

        if image_url and file_name:
            file_path = os.path.join(ieee_paper_info['final_img_dir'], file_name)
            try:
                response = session.get(image_url, stream=True)
                if response.status_code == 200:
                    with open(file_path, 'wb') as img_file:
                        for chunk in response.iter_content(1024):
                            img_file.write(chunk)
                    print(f"Downloaded: {file_path}")
                else:
                    print(f"Failed to download {image_url}, status code: {response.status_code}")
            except Exception as e:
                print(f"Error downloading {image_url}: {e}")




def extract_references(driver, ieee_paper_info):
    """
    HTML 파일에서 참조와 링크를 추출합니다.

    Args:
        file_path (str): 로컬 HTML 파일 경로

    Returns:
        list: 참조 번호, 제목, 링크 정보가 포함된 딕셔너리 리스트
    """

    driver.get(f"https://ieeexplore.ieee.org/document/{ieee_paper_info['ieee_paper_id']}/references#references")

    time.sleep(5)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # 참조 목록 추출
    reference_list = []
    references = soup.select(".reference-container")

    for ref in references:
        try:
            # 참조 번호
            number_element = ref.select_one(".number b")
            number = number_element.text.strip() if number_element else None

            # 제목
            title_element = ref.select_one(".col > div:first-child")
            title = title_element.text.strip() if title_element else None

            # 링크들
            links = {}
            link_elements = ref.select(".ref-link a")
            semantic_id = None
            for link in link_elements:
                link_text = link.text.strip()
                href = link.get("href")
                if link_text and href:
                    links[link_text] = href

                if link_text == "CrossRef":
                    semantic_id = get_semantic_id_from_doi(href.replace("https://doi.org/", ""))
                elif link_text == "View Article":
                    ieee_id = href.replace("/document/", "")
                    print(ieee_id)
                    semantic_id = get_semantic_id_from_ieee_id(ieee_id, driver)


            reference_list.append({
                "number": number,
                "title": title,
                "links": links,
                "semantic": semantic_id
            })

        except Exception as e:
            print(f"error processing reference: {e}")
            reference_list.append({
                "number": number,
                "title": title,
                "links": links,
                "semantic": None
            })

    ieee_paper_info['reference_info'] = reference_list
    return ieee_paper_info

def get_ieee_paper(ieee_paper_id = 7738524,
                   output_dir     = ORIGINAL_PAPER_PATH,
                   output_img_dir = PAPER_IMG_PATH,
                   paper_info_dir = ORIGINAL_PAPER_INFO_PATH):

    driver = webdriver.Chrome()

    semantic_id = get_semantic_id_from_ieee_id(ieee_paper_id, driver)
    if not semantic_id:
        print(f"Semantic Scholar ID for IEEE {ieee_paper_id}: not found.")
        return

    output_md_path  = f"{output_dir}/{semantic_id}_original.md"
    paper_info_path = f"{paper_info_dir}/{semantic_id}_original.json"
    final_img_dir = f"{output_img_dir}/{semantic_id}_img"
    relative_img_dir = f"../img/{semantic_id}_img"

    ieee_paper_info = {
        "ieee_paper_id": ieee_paper_id,
        "semantic_id": semantic_id,

        # output-dir
        "output_dir": output_dir,
        "output_md_path": output_md_path,

        # img-dir
        "output_img_dir": output_img_dir,
        "final_img_dir":  final_img_dir,
        "relative_img_dir": relative_img_dir,

        # paper-info-dir
        "paper_info_dir": paper_info_dir,
        "paper_info_path": paper_info_path,

        "reference_info": [],
        "img_info": [],
        "section_info": [],
    }

    # step 1 : get reference data
    ieee_paper_info = extract_references(driver, ieee_paper_info)

    # step 2 : get markdown data
    driver.get(f"https://ieeexplore.ieee.org/document/{ieee_paper_info['ieee_paper_id']}")
    (markdown_contents, ieee_paper_info) = html_to_markdown(driver, ieee_paper_info)
    (markdown_contents, ieee_paper_info) = html_to_markdown(driver, ieee_paper_info)

    # step 3 : download images
    download_images(driver, ieee_paper_info)

    # step 4 : download markdown file
    with open(ieee_paper_info["output_md_path"], 'w', encoding='utf-8') as md_file:
        md_file.write(markdown_contents)
        print(f"Markdown file saved: {ieee_paper_info['output_md_path']}")

    # step 5 : save ieee_paper_info as json file
    with open(ieee_paper_info["paper_info_path"], 'w', encoding='utf-8') as json_file:
        json.dump(ieee_paper_info, json_file, ensure_ascii=False, indent=4)



# argSparse를 이용하여 cli에서 argument를 입력하여 실행 할 수 있도록 함
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='IEEEXplore Crawler')
    parser.add_argument('--ieee_paper_id', type=int, default=9586216, help='IEEE Paper ID')
    parser.add_argument('--output_md_path', type=str, default='test/gemmini.md', help='Output Markdown File Path')
    parser.add_argument('--output_img_dir', type=str, default='test/img', help='Output Image Directory Path')
    parser.add_argument('--paper_info_path', type=str, default='test/paper_info.json', help='Paper Info JSON File Path')
    args = parser.parse_args()

    get_ieee_paper(args.ieee_paper_id, args.output_md_path, args.output_img_dir, args.final_img_dir, args.paper_info_path)

