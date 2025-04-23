from app.core.constants import ITEMS_PER_PAGE
from app.models.core import TotalItems


def update_values_from_page(*, values: dict, page: int | None) -> dict:
    limit = ITEMS_PER_PAGE
    offset = (page - 1) * limit if page is not None else 0
    if page is not None:
        values.update({"limit": limit, "offset": offset})
    return values


def get_total_items(*, total: int) -> TotalItems:
    return TotalItems(total_items=total, total_pages=total // ITEMS_PER_PAGE + 1)
