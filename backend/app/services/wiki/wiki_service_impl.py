from .wiki_service_base import WikiServiceBase
from .wiki_service_catalog import WikiServiceCatalogMixin
from .wiki_service_bootstrap import WikiServiceBootstrapMixin
from .wiki_service_indexing import WikiServiceIndexingMixin
from .wiki_service_linting import WikiServiceLintingMixin
from .wiki_service_query import WikiServiceQueryMixin


class WikiService(
    WikiServiceQueryMixin,
    WikiServiceLintingMixin,
    WikiServiceIndexingMixin,
    WikiServiceBootstrapMixin,
    WikiServiceCatalogMixin,
    WikiServiceBase,
):
    pass
