export PYTHONPATH="/home/parkdongho/dev/academic_copilot:$PYTHONPATH"
export VAULT_PATH="/home/parkdongho/dev/Obsidian4Academic"

# paper-archive
export PAPER_ARCHIVE_PATH="${VAULT_PATH}/20_Works/21_Research/1_paper_archive"

export PAPER_IMG_PATH="${PAPER_ARCHIVE_PATH}/img"
export PAPER_INFO_PATH="${PAPER_ARCHIVE_PATH}/.paper_info"
export REFERENCE_INFO_PATH="${PAPER_ARCHIVE_PATH}/.semantic_graph/reference"
export CITATION_INFO_PATH="${PAPER_ARCHIVE_PATH}/.semantic_graph/citation"

export JOURNAL_LIST_PATH="${PAPER_ARCHIVE_PATH}/journal_list.csv"
export NEW_PAPER_LIST="${PAPER_ARCHIVE_PATH}/new_paper_list.txt"

source "$HOME/.semanticscholar/setup.sh"
source "$HOME/.openai/settings.sh"

