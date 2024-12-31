Academic Copilot
---------

# Overview 

**[ISCA'16]** Eyeriss [\[translated\]](), [\[original\]](), [\[slide\]]()  
**[ISCA'16]** Eyeriss [\[translated\]](), [\[original\]](), [\[slide\]]()  
**[ISCA'16]** Eyeriss [\[translated\]](), [\[original\]](), [\[slide\]]()  
**[ISCA'16]** Eyeriss [\[translated\]](), [\[original\]](), [\[slide\]]()  



# Installation



# Tutorial

## 1. Get Paper Information

### 1.1 from the `paper_list.txt`

논문 리스트가 담긴 텍스트 파일을 이용하여 논문 정보를 가져옴

```bash
python3 academic_copilot.py get_paper --from paper_list --path ./new_paper_list.txt
```


`--path` 옵션을 사용하지 않으면 기본 경로인 `$NEW_PAPER_LIST` 를 사용함

```bash
python3 academic_copilot.py get_paper --from paper_list
```


### 1.2 from the biblio information

기존에 가져온 논문들의 인용 정보에서 다음에 가져올 논문 정보를 선택 

```bash
python3 academic_copilot.py get_paper --from biblioinfo
```

`--id` 옵션을 사용하여 특정 논문의 인용 정보에서 다음에 가져올 논문 정보를 선택

```bash
python3 academic_copilot.py get_paper --from biblioinfo --id=123456789
```

#todo: filter 처리에 대한 내용 추가 필요 


### 1.3 from the semantic id

```bash
python3 academic_copilot.py get_paper --from=semantic_id --id=123456789
```


## 2. Download paper as markdown format

### 2.1 From the IEEEXplore

```bash
python3 academic_copilot.py download_paper ---from=ieeexplore
```

```bash
python3 academic_copilot.py download_paper ---from=ieeexplore --id=123456789
```

### 2.2 From the ACM Digital Library

```python

```

### 2.3 From the ArXiv

```python

```

### 2.4 From the PDF (AI based OCR)

```python
# 

```

## 3. Generate Document

### 3.1 Translate Paper Text

```python

```

### 3.2 Generate Summary

```python

```

### 3.3 Generate Review

```python

```

### 3.4 Generate Slide

```python

```


# Project Structure

## academic_crawler

- [x] **ieeexplore.py** : ieeexplore에서 논문 정보를 가져옴
- [ ] acm.py : <!-- TODO -->
- [ ] arxiv.py : <!-- TODO -->

## document_generator : `import academic_copilot.document_generator`

- [ ] pdf_to_text.py : <!-- TODO --> 
- [ ] text_to_pdf.py : <!-- TODO --> 
- [ ] text_to_ppt.py : <!-- TODO --> 
- [ ] text_to_slide.py : <!-- TODO --> 
  
## gpt_integration : `import academic_copilot.gpt_integration`

- [ ] **ocr.py** : <!-- TODO -->  
- [ ] **text_gen.py** : <!-- TODO -->  
- [ ] **slide_gen.py** : <!-- TODO -->  
- [ ] **summarize.py** : <!-- TODO -->  
- [x] **translate.py** : <!-- TODO -->  
   
## semantic_scholar : `import academic_copilot.semantic_scholar` 

**get_paper_info.py** semantic scholar api를 이용하여 논문 정보를 가져옴 
- [x] `save_paper_info_from_semantic_id(semantic_id)` :  
- [x] `save_paper_info_from_paper_list(new_paper_list)` : 
- [x] `get_semantic_id_from_doi()` :
- [x] `get_semantic_id_from_ieee_id()` :
- [x] `get_journal_id_from_doi()` :
- [x] `get_doi_from_ieee_id(ieee_id, driver) -> doi_id` :
 
**get_biblio_info.py :** semantic scholar api를 이용하여 reference/citation 정보 및 인용 스타일을 추출 
- [ ] `#TODO`: `get_citation_info.py` 와 `get_reference_info.py`를 하나의 파일(`get_biblio_info.py`) 로 결합 
- [x] `get_citation_info.py` :  
- [x] `get_reference_info.py` :  

**academic_database.py**
- [x] `search_from_database(key, value, result_key) -> result_value` :  

## rag_integration : `import academic_copilot.rag_integration`
- #TODO



# Environment Variables

- `SEMMANTIC_SCHOLAR_API_KEY` : Semantic Scholar API Key
- `PAPER_INFO_PATH` : 논문 정보를 저장할 경로
- `REFERENCE_INFO_PATH` : 논문의 참고문헌 정보를 저장할 경로
- `CITATION_INFO_PATH` : 논문의 인용 정보를 저장할 경로
- `NEW_PAPER_LIST` : 새로운 논문 리스트에 대한 텍스트 파일 경로


