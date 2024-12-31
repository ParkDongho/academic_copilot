import openai
import re
import tiktoken
import time 
import os 
import argparse

def translate(text, client):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content":
                "영문 논문을 한국어로 번역.\n"
                "- 제목과 부제목은 영문을 유지\n"
                "- 전문용어는 원문을 최대한 유지\n"
                "- 입력 및 출력 포멧은 마크다운 임"},
            {"role": "user", "content": text}
        ]
    )
    translated_text = response.choices[0].message.content
    return translated_text

def read_and_split_texts(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        chapters = re.split(r'(# \d+|## \d+)', content)
        chapters = [chapters[i] + chapters[i+1] for i in range(1, len(chapters), 2)]
    return chapters

def save_text(file_path, file_content):
    # Create directory if not exists
    # file_path를 받아서 파일명을 제외한 디렉토리 경로를 체크
    directory = os.path.dirname(file_path)
    os.makedirs(directory, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(file_content)
    print(f"Saved: {file_path}")

def count_tokens(text: str, model: str = "gpt-4o") -> int:
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)
    return len(tokens)

def split_text_by_length_into_n_parts(text, n):
    total_length = len(text)
    part_length = total_length // n
    parts = []
    start = 0

    for i in range(n):
        if i == n - 1:
            parts.append(text[start:])
            break

        end = start + part_length
        split_index = text.rfind("\n\n", start, end)
        if split_index == -1:
            split_index = end

        parts.append(text[start:split_index])
        start = split_index + 2

    return parts


def main():
    client = openai.OpenAI()
    parser = argparse.ArgumentParser(description="Translate and process text files.")
    parser.add_argument("--read_file_path", required=True, help="Path to the input file")
    parser.add_argument("--write_file_path", required=True, help="Path to the output file")
    parser.add_argument("--re_translate_threshold", type=int, default=100, help="Minimum length of translated text to trigger re-translation")

    args = parser.parse_args()


    chapter_texts = read_and_split_texts(args.read_file_path)
    result = ""
    chapter_num = 1
    chapter_len = len(chapter_texts)
    print(f"Total chapters: {chapter_len}")

    for chapter in chapter_texts: 
        print("\n----------------------")
        print(f"chapter {chapter_num}/{chapter_len}")
        token_num = count_tokens(chapter)
        print(f"Tokens: {token_num}")

        if token_num > 2000:
            n = token_num // 2000 + 1
            splited_chapter = split_text_by_length_into_n_parts(chapter, n)
            translated_text_list = []

            for j, part in enumerate(splited_chapter):
                print(f"Part {j + 1} tokens: {count_tokens(part)}")
                translated_text = translate(part, client)
                translated_text_list.append(translated_text)

            translated_text = "\n\n".join(translated_text_list)
        else:
            translated_text = translate(chapter, client)
            print(f"Translated text length: {len(translated_text)}")
            while len(translated_text) < args.re_translate_threshold:
                print("ERROR! Re-translating...")
                time.sleep(5)
                translated_text = translate(chapter, client)

        result = result + "\n\n" + translated_text
        chapter_num += 1

    output_path = f"{args.write_file_path}"
    save_text(output_path, result)
    print("----------------------\n")

if __name__ == "__main__":
    main()


