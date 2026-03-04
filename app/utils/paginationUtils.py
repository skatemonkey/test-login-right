# utils/pagination.py
import math
from sqlalchemy import or_

def apply_search(query, search_term, fields):
    """Apply search across multiple fields"""
    if not search_term:
        return query
    term = f"%{search_term}%"
    return query.filter(or_(*[f.ilike(term) for f in fields]))

def apply_sorting(query, sort_field, sort_order, field_map, default_field):
    """Apply sorting with field mapping"""
    column = field_map.get(sort_field, default_field)
    return query.order_by(column.asc() if sort_order == 'asc' else column.desc())

def paginate(query, page, page_size):
    """Apply pagination and return (results, total_elements, total_pages)"""
    total = query.count()
    total_pages = math.ceil(total / page_size) if page_size > 0 else 0
    results = query.offset((page - 1) * page_size).limit(page_size).all()
    return results, total, total_pages