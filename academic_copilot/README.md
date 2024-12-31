# Academic Copilot

## Overview 



## Installation



## Project Structure

- academic_crawler
  - [x] **ieeexplore.py** : ieeexplore에서 논문 정보를 가져옴
  - [ ] acm.py : <!-- TODO -->
  - [ ] arxiv.py : <!-- TODO -->

- document_generator
  - [ ] pdf_to_text.py : <!-- TODO --> 
  - [ ] text_to_pdf.py : <!-- TODO --> 
  - [ ] text_to_ppt.py : <!-- TODO --> 
  - [ ] text_to_slide.py : <!-- TODO --> 
  
- gpt_integration
  - [ ] **ocr.py** : <!-- TODO -->  
  - [ ] **text_gen.py** : <!-- TODO -->  
  - [ ] **slide_gen.py** : <!-- TODO -->  
  - [ ] **summarize.py** : <!-- TODO -->  
  - [x] **translate.py** : <!-- TODO -->  
   
- semantic_scholar : `academic_copilot/semantic_scholar` 
  - **get_paper_info.py** semantic scholar api를 이용하여 논문 정보를 가져옴 
    - [x] `save_paper_info_from_semantic_id(semantic_id)` :  
    - [x] `save_paper_info_from_paper_list(new_paper_list)` : 
    - [x] `get_semantic_id_from_doi()` :
    - [x] `get_semantic_id_from_ieee_id()` :
    - [x] `get_journal_id_from_doi()` :
    - [x] `get_doi_from_ieee_id(ieee_id, driver) -> doi_id` :
  - **get_biblio_info.py :** semantic scholar api를 이용하여 reference/citation 정보 및 인용 스타일을 추출 
    - [ ] `#TODO`: `get_citation_info.py` 와 `get_reference_info.py`를 하나의 파일(`get_biblio_info.py`) 로 결합 
    - [x] `get_citation_info.py` :  
    - [x] `get_reference_info.py` :  
  - **academic_database.py**
    - [x] `search_from_database(key, value, result_key) -> result_value` :  


## Environment Variables

- `SEMMANTIC_SCHOLAR_API_KEY` : Semantic Scholar API Key
- `PAPER_INFO_PATH` : 논문 정보를 저장할 경로
- `REFERENCE_INFO_PATH` : 논문의 참고문헌 정보를 저장할 경로
- `CITATION_INFO_PATH` : 논문의 인용 정보를 저장할 경로
- `NEW_PAPER_LIST` : 새로운 논문 리스트에 대한 텍스트 파일 경로


