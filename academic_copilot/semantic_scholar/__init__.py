# academic_copilot.semantic_scholar.get_biblio_info



# academic_copilot.semantic_scholar.get_paper_info
from .get_paper_info import save_paper_info_from_semantic_id
from .get_paper_info import save_paper_info_from_paper_list

from .get_paper_info import get_semantic_id_from_doi # doi -> semantic_id
from .get_paper_info import get_semantic_id_from_ieee_id # ieee_id -> semantic_id
from .get_paper_info import get_journal_id_from_doi # doi -> Tuple(source, document_id)
from .get_paper_info import get_doi_from_ieee_id # ieee_id -> doi


# academic_copilot.semantic_scholar.academic_database
from .academic_database import search_from_database # search(key, value, result_key) -> result_value

