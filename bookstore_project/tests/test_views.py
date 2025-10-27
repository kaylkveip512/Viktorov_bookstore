from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from main.models import Author, Book, Publisher, Genre
from main.serializers import BookSerializer, AuthorSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class TestAuthorView(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.regular_user = User.objects.create_user(
            username='testuser_author',
            email='testuser_author@example.com',
            password='testpass123'
        )
        self.staff_user = User.objects.create_user(
            username='staffuser_author',
            email='staffuser_author@example.com',
            password='testpass123',
            is_staff=True
        )
        self.authenticated_client = APIClient()
        self.authenticated_client.force_authenticate(user=self.regular_user)
        self.staff_client = APIClient()
        self.staff_client.force_authenticate(user=self.staff_user)

    def test_get_authors_authenticated(self):
        Author.objects.create(name="Author 1")
        Author.objects.create(name="Author 2")
        Author.objects.create(name="Author 3")
        
        url = reverse('author')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_authors_unauthenticated(self):
        url = reverse('author')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_author_as_staff(self):
        url = reverse('author')
        data = {'name': 'New Author'}
        
        response = self.staff_client.post(url, data, content_type='application/json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Author')
        self.assertTrue(Author.objects.filter(name='New Author').exists())

    def test_create_author_as_regular_user(self):
        url = reverse('author')
        data = {'name': 'New Author'}
        
        response = self.authenticated_client.post(url, data, content_type='application/json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['error'], "Only administrators can create authors")

class TestBookView(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.regular_user = User.objects.create_user(
            username='testuser_book',
            email='testuser_book@example.com',
            password='testpass123'
        )
        self.staff_user = User.objects.create_user(
            username='staffuser_book',
            email='staffuser_book@example.com',
            password='testpass123',
            is_staff=True
        )
        self.authenticated_client = APIClient()
        self.authenticated_client.force_authenticate(user=self.regular_user)
        self.staff_client = APIClient()
        self.staff_client.force_authenticate(user=self.staff_user)

    def test_get_books_authenticated(self):
        author = Author.objects.create(name="Test Author")
        publisher = Publisher.objects.create(name="Test Publisher")
        
        Book.objects.create(
            name="Book 1",
            author=author,
            publisher=publisher,
            price=10.99,
            genre="Fiction"
        )
        Book.objects.create(
            name="Book 2", 
            author=author,
            publisher=publisher,
            price=15.99,
            genre="Science Fiction"
        )
        
        url = reverse('book')
        response = self.authenticated_client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_book_as_staff(self):
        author = Author.objects.create(name="Test Author")
        publisher = Publisher.objects.create(name="Test Publisher")
        
        url = reverse('book')
        data = {
            'name': 'New Book',
            'author': author.id,
            'publisher': publisher.id,
            'price': '29.99',
            'genre': 'Science Fiction'
        }
        
        response = self.staff_client.post(url, data, content_type='application/json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Book')
        self.assertTrue(Book.objects.filter(name='New Book').exists())

class TestPublisherView(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser_publisher',
            email='testuser_publisher@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_get_publishers_authenticated(self):
        Publisher.objects.create(name="Publisher 1")
        Publisher.objects.create(name="Publisher 2")
        
        url = reverse('publisher')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

class TestGenreView(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser_genre',
            email='testuser_genre@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_get_genres_authenticated(self):
        Genre.objects.create(name="Genre 1")
        Genre.objects.create(name="Genre 2")
        
        url = reverse('genre')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

class TestIntegration(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.staff_user = User.objects.create_user(
            username='staffuser_integration',
            email='testuser_integration@example.com',
            password='testpass123',
            is_staff=True
        )
        self.client.force_authenticate(user=self.staff_user)

    def test_complete_book_management_flow(self):
        author_data = {'name': 'J.K. Rowling'}
        author_response = self.client.post(reverse('author'), author_data, content_type='application/json')
        self.assertEqual(author_response.status_code, status.HTTP_201_CREATED)
    
        publisher_data = {'name': 'Bloomsbury Publishing'}
        publisher_response = self.client.post(reverse('publisher'), publisher_data, content_type='application/json')
        self.assertEqual(publisher_response.status_code, status.HTTP_201_CREATED)

        author = Author.objects.get(name='J.K. Rowling')
        publisher = Publisher.objects.get(name='Bloomsbury Publishing')
    
        book_data = {
            'name': 'Harry Potter and the Philosopher\'s Stone',
            'author': author.id,
            'publisher': publisher.id,
            'price': '19.99',
            'genre': 'Fantasy'
        }
        book_response = self.client.post(reverse('book'), book_data, content_type='application/json')
        self.assertEqual(book_response.status_code, status.HTTP_201_CREATED)
        
        self.assertEqual(Author.objects.count(), 1)
        self.assertEqual(Publisher.objects.count(), 1)  
        self.assertEqual(Book.objects.count(), 1)
        
        book = Book.objects.first()
        self.assertEqual(book.name, 'Harry Potter and the Philosopher\'s Stone')
        self.assertEqual(book.author.name, 'J.K. Rowling')
        self.assertEqual(book.publisher.name, 'Bloomsbury Publishing')
        self.assertEqual(book.genre, 'Fantasy')

    def test_multiple_books_by_same_author(self):
        author_data = {'name': 'Stephen King'}
        author_response = self.client.post(reverse('author'), author_data, content_type='application/json')
        author = Author.objects.get(name='Stephen King')
        author_id = author.id
        
        books_data = [
            {
                'name': 'The Shining',
                'author': author_id,
                'price': '12.99',
                'genre': 'Horror'
            },
            {
                'name': 'IT', 
                'author': author_id,
                'price': '14.99',
                'genre': 'Horror'
            },
            {
                'name': 'The Stand',
                'author': author_id, 
                'price': '16.99',
                'genre': 'Post-Apocalyptic'
            }
        ]
        
        for book_data in books_data:
            response = self.client.post(reverse('book'), book_data, content_type='application/json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        author = Author.objects.get(id=author_id)
        self.assertEqual(author.book_set.count(), 3)
        
        book_titles = [book.name for book in author.book_set.all()]
        self.assertIn('The Shining', book_titles)
        self.assertIn('IT', book_titles)  
        self.assertIn('The Stand', book_titles)

    def test_book_with_different_genres(self):
        author = Author.objects.create(name='Test Author')
        publisher = Publisher.objects.create(name='Test Publisher')
        
        genres_books = [
            ('Science Fiction', 'Dune'),
            ('Fantasy', 'The Hobbit'), 
            ('Mystery', 'Sherlock Holmes'),
            ('Romance', 'Pride and Prejudice')
        ]
        
        for genre, title in genres_books:
            book_data = {
                'name': title,
                'author': author.id,
                'publisher': publisher.id,
                'price': '15.99',
                'genre': genre
            }
            response = self.client.post(reverse('book'), book_data, content_type='application/json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        self.assertEqual(Book.objects.count(), 4)
        
        science_fiction_books = Book.objects.filter(genre='Science Fiction')
        self.assertEqual(science_fiction_books.count(), 1)
        self.assertEqual(science_fiction_books.first().name, 'Dune')

    def test_full_crud_workflow_for_author(self):
        response = self.client.get(reverse('author'))
        self.assertEqual(len(response.data), 0)
        
        authors = ['George Orwell', 'Agatha Christie', 'J.R.R. Tolkien']
        for author_name in authors:
            response = self.client.post(reverse('author'), {'name': author_name}, content_type='application/json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        response = self.client.get(reverse('author'))
        self.assertEqual(len(response.data), 3)
        
        author_names = [author['name'] for author in response.data]
        for author_name in authors:
            self.assertIn(author_name, author_names)

    def test_permissions_integration(self):
        regular_user = User.objects.create_user(
            username='regularuser_integration',
            email='regularuser_integration@example.com',
            password='testpass123'
        )
        regular_client = APIClient()
        regular_client.force_authenticate(user=regular_user)
        
        response = regular_client.get(reverse('author'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response = regular_client.post(reverse('author'), {'name': 'Test Author'}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        response = self.client.get(reverse('author')) 
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response = self.client.post(reverse('author'), {'name': 'Test Author'}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
