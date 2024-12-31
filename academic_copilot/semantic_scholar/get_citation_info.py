import os
import argparse
import time
import json
import requests
from requests import Session
from typing import Generator, TypeVar
import dotenv
dotenv.load_dotenv()

S2_API_KEY = os.environ.get('S2_API_KEY', '')
PAPER_INFO_PATH = os.environ.get('PAPER_INFO_PATH', '')
CITATION_INFO_PATH = os.environ.get('CITATION_INFO_PATH', '')

T = TypeVar('T')

def find_missing_citations(json_dir, paper_dir):
    # Get the list of JSON filenames without the '-citation' and '.json' extensions
    json_files = [
        f.replace('-citation', '').replace('.json', '')
        for f in os.listdir(json_dir)
        if f.endswith('.json')
    ]

    # Get the list of YAML filenames without extensions
    paper_files = [
        os.path.splitext(f)[0]
        for f in os.listdir(paper_dir)
        if f.endswith('.yaml') and os.path.isfile(os.path.join(paper_dir, f))
    ]

    # Find papers in the list that don't have a corresponding JSON file
    missing_papers = [paper for paper in paper_files if paper not in json_files]

    return missing_papers, paper_files


def batched(items: list[T], batch_size: int) -> list[T]:
    return [items[i:i + batch_size] for i in range(0, len(items), batch_size)]

def get_citation_batch(session: Session, paper_id: str, fields: str = 'paperId,title,year,venue,intents,isInfluential', retries=3, backoff_factor=60.0, **kwargs) -> list[dict]:
    params = {
        'fields': fields,
        **kwargs,
    }
    headers = {
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"),
        "Accept": "application/json",
        "X-API-KEY": S2_API_KEY,
    }

    url = f'https://api.semanticscholar.org/graph/v1/paper/{paper_id}/citations'
    for attempt in range(retries):
        try:
            with session.get(url, params=params, headers=headers) as response:
                response.raise_for_status()
                return response.json().get('data', [])
        except requests.exceptions.HTTPError as err:
            if response.status_code == 429:
                # Handle 429 error by waiting and retrying
                retry_after = int(response.headers.get("Retry-After", 60))  # Default to 60 seconds if not provided
                wait_time = backoff_factor * (2 ** attempt) + retry_after
                print(f"Rate limit hit. Retrying after {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                raise  # Re-raise the exception if it's not a 429 error
        except requests.RequestException as e:
            print(f"Request failed: {e}. Retrying...")
            time.sleep(backoff_factor * (2 ** attempt))

    # If all retries are exhausted
    raise requests.exceptions.HTTPError(f"Failed to fetch citations after {retries} retries.")

def get_citations(paper_id: str, **kwargs) -> Generator[dict, None, None]:
    with Session() as session:
        yield from get_citation_batch(session, paper_id, **kwargs)

def fetch_citations(papers, output_dir):
    fields = 'paperId,title,year,venue,intents,isInfluential'

    for paper_id in papers:
        try:
            citations = list(get_citations(paper_id, fields=fields))
            if not citations:
                print(f'No citations found for paper ID {paper_id}')
                continue

            output_filename = os.path.join(output_dir, f'{paper_id}-citation.json')
            with open(output_filename, 'w') as jsonfile:
                json.dump(citations, jsonfile, indent=4)

            print(f'Wrote citations for paper ID {paper_id} to {output_filename}')
            time.sleep(5)  # To avoid hitting rate limits
        except Exception as e:
            print(f"Failed to fetch citations for paper ID {paper_id}: {e}")

def get_citation_info():
    parser = argparse.ArgumentParser(description="Find missing citation JSON files and fetch citations.")
    parser.add_argument(
        '--mode',
        choices=['missing', 'all'],
        default='missing',
        help="Mode to fetch citations: 'missing' fetches only missing ones, 'all' fetches all papers."
    )
    args = parser.parse_args()

    # Ensure the output directory exists
    os.makedirs(CITATION_INFO_PATH, exist_ok=True)

    # Find missing papers or use all papers based on the mode
    missing_papers, all_papers = find_missing_citations(CITATION_INFO_PATH, PAPER_INFO_PATH)

    papers_to_fetch = missing_papers if args.mode == 'missing' else all_papers

    print(f"Fetching citations for {len(papers_to_fetch)} papers in '{args.mode}' mode.")

    # Fetch citations for the selected papers
    fetch_citations(papers_to_fetch, CITATION_INFO_PATH)

if __name__ == "__main__":
    get_citation_info()
