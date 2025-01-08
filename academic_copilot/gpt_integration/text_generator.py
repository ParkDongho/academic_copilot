from os.path import split

import openai
import re
import tiktoken
import time
import os

def generate_text(text, client, gpt_command, model="gpt-4o", re_translate_threshold=100):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": gpt_command},
            {"role": "user", "content": text}
        ]
    )

    generated_text = response.choices[0].message.content

    # re-translate
    # retranslate_cnt = 0
    # while len(translated_text) < re_translate_threshold:
    #     if retranslate_cnt > 3:
    #         print("ERROR! Re-translate failed 3 times. skipping...")
    #         translated_text = "ERROR! Re-translate failed 3 times. skipping..."
    #         break
    #     print("ERROR! Re-translating...")
    #     time.sleep(5)
    #     translated_text = generate_text(chapter, client, command, model=model)
    #     retranslate_cnt += 1

    return generated_text

def read_and_split_texts(file_path, exclude_header=True):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

        # YAML 헤더를 식별하여 분리
        yaml_header = ""
        if exclude_header and content.startswith("---"):
            yaml_end_idx = content.find("---", 3) + 3
            if yaml_end_idx > 3:
                yaml_header = content[:yaml_end_idx].strip()
                content = content[yaml_end_idx:].strip()

        # ##를 포함한 제목을 기준으로 나눔
        chapters = re.split(r'(?=^## )', content, flags=re.MULTILINE)
        chapters = [chapter.strip() for chapter in chapters if chapter.strip()]
    return yaml_header, chapters

def save_text(file_path, file_content):
    # Create directory if not exists
    directory = os.path.dirname(file_path)
    os.makedirs(directory, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(file_content)
    print(f"Saved: {file_path}")

def count_tokens(text: str, model: str = "gpt-4o") -> int:
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)
    return len(tokens)


def split_text_by_length_into_n_parts(text, n, pattern=r'\n\n'):
    total_length = len(text)
    part_length = total_length // n
    parts = []
    start = 0

    for i in range(n):
        if i == n - 1:
            parts.append(text[start:])
            break

        end = start + part_length

        # 뒤에서 부터 패턴을 찾아서 나누기
        text_tmp = text[start:end]
        matches = list(re.finditer(pattern, text_tmp))
        split_index = -1
        if matches:
            split_index = matches[-1].start() + start  # 마지막 매칭의 시작 인덱스 반환

        if split_index == -1:
            split_index = end

        parts.append(text[start:split_index])
        start = split_index

    return parts

def generate_markdown(read_file_path, write_file_path, command,
                      re_translate_threshold=100, split_text_threshold=2000, model="gpt-4o", exclude_header=True):
    client = openai.OpenAI()

    yaml_header, chapter_texts = read_and_split_texts(read_file_path, exclude_header=exclude_header)
    result = yaml_header + "\n\n" if yaml_header else ""
    chapter_num = 1
    chapter_len = len(chapter_texts)
    print(f"Total chapters: {chapter_len}")

    for chapter in chapter_texts:

        print("\n----------------------")
        print(f"chapter {chapter_num}/{chapter_len}")
        token_num = count_tokens(chapter)
        print(f"Tokens: {token_num}")

        if token_num > split_text_threshold:
            n = token_num // split_text_threshold + 1
            splited_chapter = split_text_by_length_into_n_parts(chapter, n)
            translated_text_list = []

            for j, part in enumerate(splited_chapter):
                print(f"Part {j + 1} tokens: {count_tokens(part)}")
                translated_text = generate_text(part, client, command, model=model)
                translated_text_list.append(translated_text)

            translated_text = "\n\n".join(translated_text_list)
            print(f"Translated text length: {len(translated_text)}")

        else:
            translated_text = generate_text(chapter, client, command, model=model)
            print(f"Translated text length: {len(translated_text)}")

        result = result + "\n\n" + translated_text
        chapter_num += 1

    output_path = f"{write_file_path}"
    save_text(output_path, result)
    print("----------------------\n")


if __name__ == "__main__":
    command = "\n".join([
        "영문 논문을 한국어로 번역.",
        "- 제목과 부제목은 영문을 유지",
        "- 전문용어는 원문을 최대한 유지",
        "- 입력 및 출력 포멧은 마크다운 임"
    ])
    generate_markdown(
        read_file_path="/home/parkdongho/dev/academic-copilot-obsidian-template/20_Works/21_Research/1_paper_archive/original/ffdaa12ef011de9dbf43be46d45a3abcc8288965_original.md",
        write_file_path="/home/parkdongho/dev/academic-copilot-obsidian-template/20_Works/21_Research/1_paper_archive/.translated/ffdaa12ef011de9dbf43be46d45a3abcc8288965_original_kr.md",
        command=command,
        exclude_header=True
    )

