# Academic Crawler

This script is used to crawl academic paper from ieeexplore, acm digital library, arxiv, etc.

## Features 

- Crawl academic paper and save text as markdown file
- download images in paper
- save references list in paper as bibtex file



## Functions

- `paper_info_list` 에서 논문 정보를 가져옴
- 크롤링을 하지 않은 논문 리스트를 가져옴
    - `paper_info_list` 에서 가져온 논문 리스트와 크롤링을 진행한 논문(`1_paper_archive/.original/`) 리스트를 비교하여 크롤링을 하지 않은 논문 리스트를 가져옴
- 크롤링을 하지 않은 논문 중 ieeexplore 논문에 대하여 크롤링을 진행함
    - 현재 지원하는 사이트: **ieeexplore**
    - 지원 예정 사이트 : acm digital library, arxiv
- `1_paper_archive/.original/` 디렉토리에 논문 텍스트를 `markdown` 파일로 저장함 
- 인용문을 변환
    - 크롤링시 논문의 인용문의 doi를 추출하여 저장
    - doi를 semantic scholar key로 변환
    - 가져온 논문 리스트에서 검색하여 doi를 찾아내고, 만약 존재하지 않는다면 semantic scholar api를 활용하여 key를 얻음




## IEEE Xplore

```bash
python3 ieeexplore.py 
```


## paperinfo.py

### get_ieee_to_semantic()

