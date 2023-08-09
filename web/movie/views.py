import hashlib
from django.shortcuts import render, get_object_or_404
from django.core.cache import cache
from .models import Movie, Actor

# In production we must create some utils files to avoid rewriting function in different apps
# but in our simple case i have put this here
def generate_cache_key(base, query):
    query_hash = hashlib.md5(query.encode()).hexdigest()
    return f"{base}_{query_hash}"


# About optimization
# I wrote simple function for that, but of coruse for 
# large data and better functionality in production we must use smth like elastic
# in that case we just use simple caching for 1 minute 
# In prodction i would do caching using Redis as example 
# Also PostgreSQL can provide caching for us, but in that case we using just Sqlite due to task requirements
def search_view(request):
    query = request.GET.get('query', '')

    # We use hash keys for memcached safety 
    movie_key = generate_cache_key("movie", query)
    actor_key = generate_cache_key("actors", query)

    movies = cache.get(movie_key)
    if not movies:
        movies = Movie.objects.filter(title__icontains=query)
        cache.set(movie_key, movies, 60)

    actors = cache.get(actor_key)
    if not actors:
        actors = Actor.objects.filter(name__icontains=query)
        cache.set(actor_key, actors, 60)

    return render(request, 'search.html', {'movies': movies, 'actors': actors})


def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    return render(request, 'movie_detail.html', {'movie': movie})

def actor_detail(request, actor_id):
    actor = get_object_or_404(Actor, id=actor_id)
    return render(request, 'actor_detail.html', {'actor': actor})
