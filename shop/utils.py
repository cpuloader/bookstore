from django.core.cache import cache
from django.db.models import Count

from shop.models import Book

def set_top_books():
    queryset = Book.objects.annotate(users_count=Count('users')).order_by('-users_count')[:3]
    cache.set('books_top', list(queryset), 60*60*24)
