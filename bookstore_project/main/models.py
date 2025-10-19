from django.db import models

class Author(models.Model):
    name = models.CharField(max_length = 50)

class Publisher(models.Model):
    name = models.CharField(max_length = 50)

class Genre(models.Model):
    name = models.CharField(max_length = 50)

class Book(models.Model):
    name = models.CharField(max_length = 50)
    author = models.ForeignKey(Author, on_delete = models.PROTECT)
    publisher = models.ForeignKey(Publisher, on_delete = models.SET_NULL, null = True)
    price = models.DecimalField(max_digits = 6, decimal_places = 2)
    genre = models.CharField(max_length = 50)
