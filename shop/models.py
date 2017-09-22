import os, random
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save, pre_delete
from django.core.exceptions import ObjectDoesNotExist

from user.models import User

class Author(models.Model):
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=100)
    photo = models.ImageField()

    def __str__(self):
        return "{0} {1}".format(self.name, self.surname)

    def make_unique_photo_name(self):
        name, name_ext = os.path.splitext(self.photo.name)
        self.photo.name = 'author' + str(random.random())[2:] + name_ext

    def save(self, *args, **kwargs):
        try:
            this_author = Author.objects.get(pk=self.pk)
            if this_author.photo != self.photo:
                self.make_unique_photo_name()
                this_author.photo.delete(save = False)
        except ValueError:
            pass
        except ObjectDoesNotExist: # creating new object
            self.make_unique_photo_name()
        super(Author, self).save(*args, **kwargs)


class Book(models.Model):
    authors = models.ManyToManyField(Author, related_name='books')
    users = models.ManyToManyField(User, related_name='books', blank=True)
    title = models.CharField(max_length=100)
    picture = models.ImageField(blank=True)
    about = models.TextField()
    price = models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self):
        return self.title

    def make_unique_picture_name(self):
        name, name_ext = os.path.splitext(self.picture.name)
        self.picture.name = 'book' + str(random.random())[2:] + name_ext

    def save(self, *args, **kwargs):
        try:
            this_book = Book.objects.get(pk=self.pk)
            if this_book.picture != self.picture:
                self.make_unique_picture_name()
                this_book.picture.delete(save = False)
        except ValueError:
            pass
        except ObjectDoesNotExist:
            if self.picture.name:
                self.make_unique_picture_name()
        super(Book, self).save(*args, **kwargs)


@receiver(pre_delete, sender=Author)
def pre_delete_handler(sender, **kwargs):
    author = kwargs['instance']
    for book in author.books.all():
        book.delete()
    try:
        storage, path = author.photo.storage, author.photo.path
        storage.delete(path)
    except ValueError: pass

@receiver(post_delete, sender=Book)
def post_delete_handler(sender, **kwargs):
    book = kwargs['instance']
    try:
        storage, path = book.picture.storage, book.picture.path
        storage.delete(path)
    except ValueError: pass
