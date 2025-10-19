from django.urls import path
from . import views

urlpatterns = [
    path('author/', views.AuthorView.as_view(), name='author'),
    path('publisher/', views.PublisherView.as_view(), name='publisher'),
    path('genre/', views.GenreView.as_view(), name='genre'),
    path('book/', views.BookView.as_view(), name='book'),
]
