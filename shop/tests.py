# coding: utf-8
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase, APIClient, force_authenticate
from django.core.cache import cache
from django.test import TestCase

from user.models import User
from shop.models import Author, Book
from shop.utils import set_top_books


class AuthorModelTests(TestCase):

    def setUp(self):
        self.raw_password = 'testpass'
        self.user = User.objects.create_user(username='test1',
             phone='1234567', password=self.raw_password, cards='000')
        self.author1 = Author.objects.create(name='author1', surname='surname1', photo='photo1.jpg')
        self.author2 = Author.objects.create(name='author2', surname='surname2', photo='photo2.jpg')
        book1 = Book(title='title1', about='about text1', price=100)
        book1.save()
        self.author1.books.add(book1)
        book2 = Book(title='title2', about='about text2', price=100)
        book2.save()
        self.author2.books.add(book2)
        book3 = Book(title='title3', about='about text3', price=100)
        book3.save()
        self.author1.books.add(book3)
        self.author2.books.add(book3)

    def test_delete_author_delete_his_books(self):
        author_name = self.author1.name
        books_of_author1 = Book.objects.filter(authors__name=author_name)
        print(list(books_of_author1))
        self.author1.delete()
        books_of_author1 = list(Book.objects.filter(authors__name=author_name))
        self.assertEqual(books_of_author1, [])


class ListBooksTest(APITestCase):
    client_class = APIClient

    def setUp(self):
        self.raw_password = 'testpass'
        self.user = User.objects.create_user(username='test1',
             phone='1234567', password=self.raw_password, cards='000')
        self.author1 = Author.objects.create(name='author1', surname='surname1', photo='photo1.jpg')
        self.author2 = Author.objects.create(name='author2', surname='surname2', photo='photo2.jpg')
        self.author3 = Author.objects.create(name='surname3', surname='author1', photo='photo3.jpg')
        book1 = Book(title='title1', about='about text1', price=100)
        book1.save()
        self.author1.books.add(book1)
        book2 = Book(title='title2', about='about text2', price=100)
        book2.save()
        self.author2.books.add(book2)
        book3 = Book(title='title3', about='about text3', price=100)
        book3.save()
        self.author1.books.add(book3)
        self.author2.books.add(book3)
        book4 = Book(title='title3', about='about text4', price=100)
        book4.save()
        self.author3.books.add(book4)
        return super(ListBooksTest, self).setUp()

    def test_get_all_books(self):
        response = self.client.get('/api/v1/books/')
        self.assertEqual(response.status_code, 200)

    def test_get_all_books_of_author_by_anonymous_user(self):
        author_surname = self.author1.surname
        response = self.client.get('/api/v1/books/?authorsurname={0}'.format(author_surname))
        self.assertEqual(response.status_code, 200)

    def test_get_all_books_of_author_by_logged_user(self):
        author_surname = self.author2.surname
        self.client.login(username=self.user.username, password=self.raw_password)
        response = self.client.get('/api/v1/books/?authorsurname={0}'.format(author_surname))
        self.client.logout()
        self.assertEqual(response.status_code, 200)

    def test_search(self):
        search_str = 'tle3 or1 name3 '
        response = self.client.get('/api/v1/books/?search={0}'.format(search_str))
        #for i, obj in enumerate(response.data):
        #    print(i, obj.items())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(list(response.data)) == 3, True)
        search_elements = search_str.strip().split(' ')
        for el in search_elements:
            self.assertContains(response, el)


class BookDetailsTest(APITestCase):
    client_class = APIClient

    def setUp(self):
        self.raw_password = 'testpass'
        self.user1 = User.objects.create_user(username='test1',
             phone='1234567', password=self.raw_password, cards='000')
        self.user2 = User.objects.create_user(username='test2',
             phone='1234567', password=self.raw_password, cards='000')
        author1 = Author.objects.create(name='author1', surname='surname1', photo='photo1.jpg')
        author2 = Author.objects.create(name='author2', surname='surname2', photo='photo2.jpg')
        book1 = Book(title='title1', about='about text1', price=100)
        book1.save()
        author1.books.add(book1)
        book2 = Book(title='title2', about='about text2', price=100)
        book2.save()
        author2.books.add(book2)
        book3 = Book(title='title3', about='about text3', price=100)
        book3.save()
        author1.books.add(book3)
        author2.books.add(book3)
        self.user1.books.add(book1)
        return super(BookDetailsTest, self).setUp()

    def test_get_book_by_anonymous_user(self):
        response = self.client.get('/api/v1/bookdetails/1/')
        self.assertEqual(response.status_code, 200)

    def test_get_book_by_buyer_user(self):
        self.client.login(username=self.user1.username, password=self.raw_password)
        response = self.client.get('/api/v1/bookdetails/1/')
        self.assertEqual(response.status_code, 200)

    def test_get_book_by_another_user(self):
        self.client.login(username=self.user2.username, password=self.raw_password)
        response = self.client.get('/api/v1/bookdetails/1/')
        self.assertEqual(response.status_code, 200)


class BookBuyTest(APITestCase):
    client_class = APIClient

    def setUp(self):
        self.raw_password = 'testpass'
        self.user1 = User.objects.create_user(username='test1',
             phone='1234567', password=self.raw_password, cards='000')
        self.user2 = User.objects.create_user(username='test2',
             phone='1234567', password=self.raw_password, cards='000')
        author1 = Author.objects.create(name='author1', surname='surname1', photo='photo1.jpg')
        author2 = Author.objects.create(name='author2', surname='surname2', photo='photo2.jpg')
        book1 = Book(title='title1', about='about text1', price=100)
        book1.save()
        author1.books.add(book1)
        book2 = Book(title='title2', about='about text2', price=100)
        book2.save()
        author2.books.add(book2)
        book3 = Book(title='title3', about='about text3', price=100)
        book3.save()
        author1.books.add(book3)
        author2.books.add(book3)
        return super(BookBuyTest, self).setUp()

    def test_buy_book_by_anonymous_user(self):
        response = self.client.get('/api/v1/buy/1/')
        self.assertEqual(response.status_code, 403)

    def test_buy_book_by_anonymous_user_wrong_method(self):
        response = self.client.post('/api/v1/buy/1/', {'test':'test'})
        self.assertEqual(response.status_code, 405)

    def test_buy_book_by_logged_user(self):
        self.client.login(username=self.user1.username, password=self.raw_password)
        response = self.client.get('/api/v1/buy/1/')
        #print(response.data)
        book = Book.objects.get(pk=1)
        #print(book.users.all())
        #print(self.user1.books.all())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.data.values())[0], 'OK!')
        self.assertEqual(book.users.get(pk=self.user1.pk), self.user1)
        self.assertEqual(self.user1.books.get(pk=book.pk), book)


class ListMyBooksTest(APITestCase):
    client_class = APIClient

    def setUp(self):
        self.raw_password = 'testpass'
        self.user1 = User.objects.create_user(username='test1',
             phone='1234567', password=self.raw_password, cards='000')
        self.user2 = User.objects.create_user(username='test2',
             phone='1234567', password=self.raw_password, cards='000')
        author1 = Author.objects.create(name='author1', surname='surname1', photo='photo1.jpg')
        author2 = Author.objects.create(name='author2', surname='surname2', photo='photo2.jpg')
        book1 = Book(title='title1', about='about text1', price=100)
        book1.save()
        author1.books.add(book1)
        book2 = Book(title='title2', about='about text2', price=100)
        book2.save()
        author2.books.add(book2)
        book3 = Book(title='title3', about='about text3', price=100)
        book3.save()
        author1.books.add(book3)
        author2.books.add(book3)
        self.user1.books.add(book1, book2)
        self.user2.books.add(book2)
        return super(ListMyBooksTest, self).setUp()

    def test_list_my_books_by_anonymous_user(self):
        response = self.client.get('/api/v1/mybooks/')
        self.assertEqual(response.status_code, 403)

    def test_list_my_books_by_logged_user(self):
        self.client.login(username=self.user1.username, password=self.raw_password)
        response = self.client.get('/api/v1/mybooks/')
        self.assertEqual(response.status_code, 200)
        mybooks = []
        for book in self.user1.books.all():
            mybooks.append(book.pk)
        for el in list(response.data):
            self.assertEqual(el['id'] in mybooks, True)


class MainViewTest(APITestCase):
    client_class = APIClient

    def setUp(self):
        self.raw_password = 'testpass'
        self.user1 = User.objects.create_user(username='test1',
             phone='1234567', password=self.raw_password, cards='000')
        self.user2 = User.objects.create_user(username='test2',
             phone='1234567', password=self.raw_password, cards='000')
        author1 = Author.objects.create(name='author1', surname='surname1', photo='photo1.jpg')
        author2 = Author.objects.create(name='author2', surname='surname2', photo='photo2.jpg')
        book1 = Book(title='title1', about='about text1', price=100)
        book1.save()
        author1.books.add(book1)
        book2 = Book(title='title2', about='about text2', price=100)
        book2.save()
        author2.books.add(book2)
        book3 = Book(title='title3', about='about text3', price=100)
        book3.save()
        author1.books.add(book3)
        author2.books.add(book3)
        book4 = Book(title='title4', about='about text3', price=100)
        book4.save()
        author2.books.add(book4)
        self.user1.books.add(book1, book2)
        self.user2.books.add(book2)

        cache.delete('books_top')
        return super(MainViewTest, self).setUp()

    def test_get_top_books_from_base(self):
        response = self.client.get('/api/v1/')
        result = []
        for i, el in enumerate(response.data):
            result.append(el['title'])
            #print(i, result[i])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(result, ['title2','title1','title3'])

    def test_get_top_books_from_cache(self):
        set_top_books()
        response = self.client.get('/api/v1/')
        result = []
        for i, el in enumerate(response.data):
            result.append(el['title'])
            #print(i, result[i])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(result, ['title2','title1','title3'])
        cache.delete('books_top')
