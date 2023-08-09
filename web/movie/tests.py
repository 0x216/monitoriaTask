from django.test import TestCase, RequestFactory
from django.core.cache import cache
from .models import Movie, Actor
from .views import search_view

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

    def tearDown(self):
        cache.clear()
