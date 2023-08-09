from django.shortcuts import render, get_object_or_404
from .models import Movie, Actor

def search_view(request):
    query = request.GET.get('query', '')
    movies = Movie.objects.filter(title__icontains=query)
    actors = Actor.objects.filter(name__icontains=query)
    return render(request, 'search.html', {'movies': movies, 'actors': actors})

def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    return render(request, 'movie_detail.html', {'movie': movie})

def actor_detail(request, actor_id):
    actor = get_object_or_404(Actor, id=actor_id)
    return render(request, 'actor_detail.html', {'actor': actor})
