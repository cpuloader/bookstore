from rest_framework import serializers
from rest_framework.response import Response

from user.serializers import UserSerializer
from user.models import User
from .models import Author, Book

class AuthorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Author
        fields = ('id', 'name', 'surname', 'photo')
        read_only_fields = ('id',)


class BookSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True, read_only=True)
    can_buy = serializers.SerializerMethodField('is_user_authenticated')

    class Meta:
        model = Book
        fields = ('id', 'title', 'picture', 'about', 'authors', 'price', 'can_buy')
        read_only_fields = ('id',)

    def is_user_authenticated(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return True
        else:
            return False

class BookDownloadSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True, read_only=True)
    download_link = serializers.SerializerMethodField('is_user_authenticated')

    class Meta:
        model = Book
        fields = ('id', 'title', 'picture', 'about', 'authors', 'price', 'download_link')
        read_only_fields = ('id',)

    def is_user_authenticated(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            if user in obj.users.all():
                return '<download link>'
            else:
                return None
        else:
            return None