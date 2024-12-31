import os
import yaml


PAPER_INFO_PATH = os.environ.get('PAPER_INFO_PATH', '')


def search_from_database(key, value, result_key):
    """
    Search for a key-value pair in the YAML files.
      search_from_database(key, value, result_key) -> result_value


    **Example:**

    - `search_from_database("IEEE", "8686088", "SEMANTIC") -> "d3b8b9e6b3"`
    - `search_from_database("DOI", "10.1109/ACCESS.2019.2920679", "SEMANTIC") -> "d3b8b9e6b3"`

    """

    database_path = PAPER_INFO_PATH
    for filename in os.listdir(database_path):
        if filename.endswith(".yaml"):
            file_path = os.path.join(database_path, filename)
            with open(file_path, 'r') as file:
                content = yaml.safe_load(file)
                if 'external_ids' in content and content['external_ids'].get(key) == value:
                    return content['external_ids'].get(result_key)
    return None


if __name__ == "__main__":
    key = "IEEE"
    value = "8686088"
    result_key = "SEMANTIC"
    semantic_id = search_from_database(key, value, result_key)

    if semantic_id:
        print(f"Semantic Scholar ID for {key} {value}: {semantic_id}")
    else:
        print(f"Semantic Scholar ID for {key} {value}: not found.")
