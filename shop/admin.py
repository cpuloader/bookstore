from django.contrib import admin

from .models import Author, Book

class BookAdmin(admin.ModelAdmin):
    exclude = ('users',)

admin.site.register(Author)
admin.site.register(Book, BookAdmin)
