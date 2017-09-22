from django.conf.urls import include, url
from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from rest_framework import routers

from .views import index
from shop.views import ListBooks, BookDetails, buy_book, ListMyBooks, MainView

urlpatterns = [
    url(r'^api/v1/books/', ListBooks.as_view()),
    url(r'^api/v1/bookdetails/(?P<pk>\d+)/$', BookDetails.as_view()),
    url(r'^api/v1/buy/(?P<pk>\d+)/$', buy_book),
    url(r'^api/v1/mybooks/$', ListMyBooks.as_view()),
    url(r'^api/v1/$', MainView.as_view()),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$',  index, name='index'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
