from django.test import TestCase
from main.models import Author, Publisher, Genre, Book

class TestAuthorModel(TestCase):
    def test_author_creation(self):
        author = Author.objects.create(name="Test Author")
        self.assertEqual(author.name, "Test Author")
        self.assertEqual(Author.objects.count(), 1)
    
    def test_author_string_representation(self):
        author = Author.objects.create(name="John Doe")
        self.assertEqual(str(author), "John Doe")

class TestPublisherModel(TestCase):
    def test_publisher_creation(self):
        publisher = Publisher.objects.create(name="Test Publisher")
        self.assertEqual(publisher.name, "Test Publisher")
        self.assertEqual(Publisher.objects.count(), 1)

class TestGenreModel(TestCase):
    def test_genre_creation(self):
        genre = Genre.objects.create(name="Test Genre")
        self.assertEqual(genre.name, "Test Genre")
        self.assertEqual(Genre.objects.count(), 1)

class TestBookModel(TestCase):
    def test_book_creation(self):
        author = Author.objects.create(name="Test Author")
        publisher = Publisher.objects.create(name="Test Publisher")
        
        book = Book.objects.create(
            name="Test Book",
            author=author,
            publisher=publisher,
            price=25.99,
            genre="Fiction"
        )
        
        self.assertEqual(book.name, "Test Book")
        self.assertEqual(book.author, author)
        self.assertEqual(book.publisher, publisher)
        self.assertEqual(book.price, 25.99)
        self.assertEqual(book.genre, "Fiction")
        self.assertEqual(Book.objects.count(), 1)
    
    def test_book_without_publisher(self):
        author = Author.objects.create(name="Test Author")
        
        book = Book.objects.create(
            name="Test Book",
            author=author,
            price=19.99,
            genre="Fiction"
        )
        
        self.assertIsNone(book.publisher)
    
    def test_book_string_representation(self):
        author = Author.objects.create(name="George Orwell")
        book = Book.objects.create(
            name="1984",
            author=author,
            price=12.99,
            genre="Dystopian"
        )
        self.assertEqual(str(book), "1984")
