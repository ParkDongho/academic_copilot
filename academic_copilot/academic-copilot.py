import argparse
import os

from academic_copilot.semantic_scholar.get_paper_info import save_paper_info_from_paper_list

NEW_PAPER_LIST = os.environ.get('NEW_PAPER_LIST', '')


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


def download_paper_from_ieeexplore(ieee_id):
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


if __name__ == "__main__":
    main()
