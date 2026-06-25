"""
Custom paginator for API data (non-Django ORM)
This allows django-tables2 to work with data from external APIs
"""
from django.core.paginator import Page, Paginator as DjangoPaginator


class ApiPaginator(DjangoPaginator):
    """
    Custom paginator that works with API data instead of Django QuerySet
    """
    
    def __init__(self, object_list, per_page, total_count, current_page=1, **kwargs):
        """
        Initialize paginator with API data
        
        Args:
            object_list: List of items for current page
            per_page: Items per page
            total_count: Total number of items across all pages
            current_page: Current page number
        """
        self._current_page = current_page
        self._total_count = total_count
        # Don't call super().__init__ because we don't have full object_list
        self.per_page = int(per_page)
        self.orphans = kwargs.get('orphans', 0)
        self.allow_empty_first_page = kwargs.get('allow_empty_first_page', True)
        self.object_list = object_list
    
    @property
    def count(self):
        """Return total count of objects across all pages"""
        return self._total_count
    
    @property
    def num_pages(self):
        """Return total number of pages"""
        if self.count == 0:
            return 1
        hits = max(1, self.count - self.orphans)
        return (hits + self.per_page - 1) // self.per_page
    
    def page(self, number):
        """Return a Page object for the given 1-based page number"""
        number = self.validate_number(number)
        return ApiPage(self.object_list, number, self)


class ApiPage(Page):
    """
    Custom Page object for API data
    """
    
    def __init__(self, object_list, number, paginator):
        """
        Initialize page with API data
        
        Args:
            object_list: List of items for this page
            number: Page number (1-based)
            paginator: ApiPaginator instance
        """
        self.object_list = object_list
        self.number = number
        self.paginator = paginator
    
    def __repr__(self):
        return f'<ApiPage {self.number} of {self.paginator.num_pages}>'
    
    def __len__(self):
        return len(self.object_list)
    
    def __getitem__(self, index):
        return self.object_list[index]
    
    def has_next(self):
        return self.number < self.paginator.num_pages
    
    def has_previous(self):
        return self.number > 1
    
    def has_other_pages(self):
        return self.has_previous() or self.has_next()
    
    def next_page_number(self):
        return self.paginator.validate_number(self.number + 1)
    
    def previous_page_number(self):
        return self.paginator.validate_number(self.number - 1)
    
    def start_index(self):
        """
        Return the 1-based index of the first object on this page,
        relative to total objects across all pages.
        """
        if self.paginator.count == 0:
            return 0
        return (self.number - 1) * self.paginator.per_page + 1
    
    def end_index(self):
        """
        Return the 1-based index of the last object on this page,
        relative to total objects across all pages.
        """
        if self.number == self.paginator.num_pages:
            return self.paginator.count
        return self.number * self.paginator.per_page
