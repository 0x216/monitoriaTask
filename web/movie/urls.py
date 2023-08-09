from django.urls import path
from . import views

urlpatterns = [
    path('search', views.search_view, name='search_view'),
    path('movie/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('actor/<int:actor_id>/', views.actor_detail, name='actor_detail'),
]