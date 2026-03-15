"""
Pagination utilities for query results
"""
from flask import request, url_for
from math import ceil

class Pagination:
    """
    Pagination helper class for database queries
    """
    
    def __init__(self, query, page=1, per_page=20, total=None, items=None):
        """
        Initialize pagination
        
        Args:
            query: SQLAlchemy query object
            page: Current page number (1-indexed)
            per_page: Number of items per page
            total: Total number of items (optional, calculated from query if not provided)
            items: List of items (optional, fetched from query if not provided)
        """
        self.query = query
        self.per_page = per_page
        self.page = max(1, page)  # Ensure page is at least 1
        
        if total is None:
            total = query.count()
        self.total = total
        
        if items is None:
            offset = (self.page - 1) * per_page
            items = query.limit(per_page).offset(offset).all()
        self.items = items
    
    @property
    def pages(self):
        """Total number of pages"""
        return ceil(self.total / self.per_page) if self.per_page > 0 else 0
    
    @property
    def has_prev(self):
        """Check if there is a previous page"""
        return self.page > 1
    
    @property
    def has_next(self):
        """Check if there is a next page"""
        return self.page < self.pages
    
    @property
    def prev_num(self):
        """Previous page number"""
        return self.page - 1 if self.has_prev else None
    
    @property
    def next_num(self):
        """Next page number"""
        return self.page + 1 if self.has_next else None
    
    def iter_pages(self, left_edge=2, left_current=2, right_current=3, right_edge=2):
        """
        Iterate over page numbers with ellipsis
        
        Args:
            left_edge: Number of pages at the beginning
            left_current: Number of pages to the left of current page
            right_current: Number of pages to the right of current page
            right_edge: Number of pages at the end
            
        Yields:
            Page numbers or None for ellipsis
        """
        last = 0
        for num in range(1, self.pages + 1):
            if (num <= left_edge or
                (num > self.page - left_current - 1 and num < self.page + right_current) or
                num > self.pages - right_edge):
                if last + 1 != num:
                    yield None
                yield num
                last = num
    
    def get_url(self, page, endpoint=None, **kwargs):
        """
        Get URL for a specific page
        
        Args:
            page: Page number
            endpoint: URL endpoint (uses current endpoint if not provided)
            **kwargs: Additional URL parameters
            
        Returns:
            URL string
        """
        if endpoint is None:
            endpoint = request.endpoint
        
        args = request.view_args.copy() if request.view_args else {}
        args.update(request.args.to_dict())
        args.update(kwargs)
        args['page'] = page
        
        return url_for(endpoint, **args)

def paginate(query, page=None, per_page=20):
    """
    Helper function to paginate a query
    
    Args:
        query: SQLAlchemy query object
        page: Page number (from request if not provided)
        per_page: Items per page
        
    Returns:
        Pagination object
    """
    if page is None:
        page = request.args.get('page', 1, type=int)
    
    return Pagination(query, page=page, per_page=per_page)

def get_page_range(current_page, total_pages, max_display=7):
    """
    Get page range for pagination display
    
    Args:
        current_page: Current page number
        total_pages: Total number of pages
        max_display: Maximum number of page links to display
        
    Returns:
        List of page numbers to display
    """
    if total_pages <= max_display:
        return list(range(1, total_pages + 1))
    
    half_display = max_display // 2
    
    if current_page <= half_display:
        # Near the beginning
        return list(range(1, max_display + 1))
    elif current_page >= total_pages - half_display:
        # Near the end
        return list(range(total_pages - max_display + 1, total_pages + 1))
    else:
        # In the middle
        return list(range(current_page - half_display, current_page + half_display + 1))

class PaginationInfo:
    """
    Simple pagination info for API responses
    """
    
    def __init__(self, total, page, per_page, items):
        """
        Initialize pagination info
        
        Args:
            total: Total number of items
            page: Current page number
            per_page: Items per page
            items: List of items for current page
        """
        self.total = total
        self.page = page
        self.per_page = per_page
        self.items = items
        self.pages = ceil(total / per_page) if per_page > 0 else 0
    
    def to_dict(self):
        """Convert to dictionary for API response"""
        return {
            'total': self.total,
            'page': self.page,
            'per_page': self.per_page,
            'pages': self.pages,
            'has_next': self.page < self.pages,
            'has_prev': self.page > 1
        }
