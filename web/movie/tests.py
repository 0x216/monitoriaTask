from django.test import TestCase, RequestFactory
from django.core.cache import cache
from .models import Movie, Actor
from .views import search_view, movie_detail, actor_detail

class SearchViewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

        self.actor1 = Actor.objects.create(name="Test Actor 1")
        self.actor2 = Actor.objects.create(name="Test Actor 2")
        self.movie = Movie.objects.create(title="Test Movie", link="http://example.com")
        self.movie.actors.add(self.actor1, self.actor2)

    def test_search(self):
        request = self.factory.get('/search/', {'query': 'Test'})
        response = search_view(request)

        self.assertContains(response, 'Test Movie')
        self.assertContains(response, 'Test Actor 1')
        self.assertContains(response, 'Test Actor 2')

        self.movie.delete()
        self.actor1.delete()
        self.actor2.delete()

    def test_partial_search(self):
        request = self.factory.get('/search/', {'query': 'Test Movi'})
        response = search_view(request)

        self.assertContains(response, 'Test Movie')

        request = self.factory.get('/search/', {'query': 'Actor 1'})
        response = search_view(request)

        self.assertContains(response, 'Test Actor 1')

    def test_no_results(self):
        request = self.factory.get('/search/', {'query': 'Nonexistent'})
        response = search_view(request)

        self.assertNotContains(response, 'Test Movie')
        self.assertNotContains(response, 'Test Actor 1')
        self.assertNotContains(response, 'Test Actor 2')

    def test_movie_detail(self):
        request = self.factory.get(f'/movie/{self.movie.id}/')
        response = movie_detail(request, self.movie.id)
        self.assertContains(response, 'Test Movie', status_code=200)
        self.assertContains(response, 'Test Actor 1')
        self.assertContains(response, 'Test Actor 2')

    def test_actor_detail(self):
        request = self.factory.get(f'/actor/{self.actor1.id}/')
        response = actor_detail(request, self.actor1.id)
        self.assertContains(response, 'Test Actor 1', status_code=200)
        self.assertContains(response, 'Test Movie')

    def test_cache_works(self):
        request = self.factory.get('/search/', {'query': 'Test'})
        response_without_cache = search_view(request)
        
        with self.assertNumQueries(0):  
            response_with_cache = search_view(request)
            
        self.assertEqual(response_without_cache.content, response_with_cache.content)

    def tearDown(self):
        cache.clear()
