import argparse
import os

from academic_copilot.academic_crawler import get_ieee_paper
from academic_copilot.gpt_integration.translate import translate_markdown
from academic_copilot.semantic_scholar.get_paper_info import save_paper_info_from_paper_list, \
    find_files_with_external_id, get_ieee_id_from_semantic_id
from academic_copilot.util.env import *

def get_paper_from_list(file_path):
    print(f"Getting paper information from: {file_path}")
    save_paper_info_from_paper_list(file_path)
    # Logic for processing the paper list


def get_paper_from_biblioinfo():
    print("Getting paper information from biblio information")
    # Logic for processing biblio information


def get_paper_from_semantic_id(semantic_id):
    print(f"Getting paper information from semantic ID: {semantic_id}")
    # Logic for processing semantic ID

# academic_crawler

def download_paper_from_ieeexplore(ieee_id):

    def list_yaml_files_without_extension(directory_path):
        return [
            os.path.splitext(f)[0]
            for f in os.listdir(directory_path)
            if os.path.isfile(os.path.join(directory_path, f)) and f.endswith(('_original.md'))
        ]


    if ieee_id is None:
        ieee_paper_list = find_files_with_external_id("IEEE")
        downloaded_paper_list = list_yaml_files_without_extension(ORIGINAL_PAPER_PATH)
        semantic_id = list(set(ieee_paper_list) - set(downloaded_paper_list))
        print(f"Downloaded {len(semantic_id)} paper list")

        new_paper_list = [get_ieee_id_from_semantic_id(f) for f in semantic_id]
        print(len(new_paper_list))
        print(new_paper_list)
        return
    else:
        get_ieee_paper(ieee_id)
        print(f"Downloading paper from IEEE Xplore: {ieee_id}")
        # Logic for downloading paper from IEEE Xplore


def main():
    parser = argparse.ArgumentParser(description="Academic Copilot: Automate academic tasks.")

    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    # Subcommand: get_paper
    get_paper_parser = subparsers.add_parser("get_paper", help="Get paper information")

    get_paper_parser.add_argument("--from", dest="source", type=str,
                                  choices=["paper_list", "biblioinfo", "semantic_id"], required=True,
                                  help="Source of the paper information")
    get_paper_parser.add_argument("--path", type=str, help="Path to the file (if applicable)")
    get_paper_parser.add_argument("--id", type=str, help="Semantic ID (if applicable)")

    # Subcommand: download_paper
    download_paper_parser = subparsers.add_parser("download_paper", help="Download paper")

    download_paper_parser.add_argument("---from", dest="source", type=str, choices=["ieeexplore"], required=True,
                                       help="Source to download the paper from")
    download_paper_parser.add_argument("--id", type=str, help="Journal ID (if applicable)")

    # Subcommand: translate
    translate_parser = subparsers.add_parser("translate", help="Translate text")
    translate_parser.add_argument("--from_lang", default="english", type=str,)
    translate_parser.add_argument("--to_lang", default="korean", type=str, required=True,)
    translate_parser.add_argument("--read_file_path", required=True, help="Path to the input file")
    translate_parser.add_argument("--write_file_path", required=True, help="Path to the output file")

    args = parser.parse_args()

    if args.command == "get_paper":
        if args.source == "paper_list":
            if args.path:
                get_paper_from_list(args.path)
            else:
                get_paper_from_list(NEW_PAPER_LIST)


        elif args.source == "biblioinfo":
            get_paper_from_biblioinfo()
        elif args.source == "semantic_id":
            if args.id:
                get_paper_from_semantic_id(args.id)
            else:
                print("Error: --id is required when --from is 'semantic_id'")

    elif args.command == "download_paper":
        if args.source == "ieeexplore":
            if args.id:
                download_paper_from_ieeexplore(args.id)
            else:
                download_paper_from_ieeexplore(None)

    elif args.command == "translate":
        if args.from_lang and args.to_lang:
            print(f"Translating from {args.from_lang} to {args.to_lang}")
            translate_markdown(args.read_file_path, args.write_file_path)



if __name__ == "__main__":
    main()
