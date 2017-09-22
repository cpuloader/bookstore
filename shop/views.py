from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, Count
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import permissions, generics


from .models import Book
from user.models import User
from .serializers import AuthorSerializer, BookSerializer, BookDownloadSerializer
from .payment import make_payment

class ListBooks(generics.ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def list(self, request):
        search_str = request.GET.get('search', None)
        author_surname = request.GET.get('authorsurname', None)
        if search_str:
            q_name = Q()
            q_surname = Q()
            q_title = Q()
            search_str = search_str.strip().split(' ')
            for el in search_str:
                q_name |= Q(authors__name__icontains=el)
                q_surname |= Q(authors__surname__icontains=el)
                q_title |= Q(title__icontains=el)
            queryset = Book.objects.filter(q_name | q_surname | q_title).distinct()
        elif author_surname:
            queryset = Book.objects.filter(authors__surname=author_surname)
        else:
            queryset = self.get_queryset()
        serializer = BookSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)


class BookDetails(generics.RetrieveAPIView):
    serializer_class = BookDownloadSerializer

    def get(self, request, pk):
        queryset = Book.objects.get(pk=pk)
        serializer = BookDownloadSerializer(queryset, context={'request': request})
        return Response(serializer.data)


@api_view(['GET'])
def buy_book(request, pk):
    if request.method == 'GET' and request.user.is_authenticated:
        try:
            user = User.objects.get(pk=request.user.id)
            book = Book.objects.get(pk=pk)
            result = make_payment(user.cards, book.price)
            if result:
                user.books.add(book)
                return Response({"message": "OK!"})
            else:
                return Response({"message": "payment error"}, status=status.HTTP_402_PAYMENT_REQUIRED)
        except ObjectDoesNotExist:
            return Response({"message": "object not found"}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({"message": "error"}, status=status.HTTP_403_FORBIDDEN)


class ListMyBooks(generics.ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request):
        queryset = self.queryset.filter(users__id=request.user.id)
        serializer = BookSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)


class MainView(generics.ListAPIView):
    serializer_class = BookSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return (permissions.AllowAny(),)

    def list(self, request):
        stored_top = cache.get('books_top')
        if stored_top:
            #print('from cache')
            serializer = BookSerializer(stored_top, many=True, context={'request': request})
            return Response(serializer.data)
        else:
            #print('from db')
            queryset = Book.objects.annotate(users_count=Count('users')).order_by('-users_count')[:3]
            serializer = BookSerializer(queryset, many=True, context={'request': request})
            return Response(serializer.data)
