from django.core.management.base import BaseCommand
from movie.models import Movie, Actor
import aiohttp
from bs4 import BeautifulSoup
import asyncio
import random

class CsfdScraper:
    BASE_SITE_URL = "http://www.csfd.cz"
    BASE_SEARCH_URL = f"{BASE_SITE_URL}/zebricky/filmy/nejlepsi/?showMore=1"
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }


    # I found 11 as highest value to do not get blocked by CSFD website
    # If we'll make it above, csfd will block us
    # Under - slower 
    # Use 3 for safe
    def __init__(self, max_concurrent=3, delay=0):
        self.session = None
        self.soup = None
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.delay = delay

    async def start(self):
        # Headers for simple bypass site robots checking
        self.session = aiohttp.ClientSession(headers=self.HEADERS)

    async def get_soup(self, url):
        async with self.session.get(url) as response:
            response.raise_for_status()
            content = await response.text()
            self.soup = BeautifulSoup(content, 'html.parser')

    async def extract_movie_links(self, url):
        await self.get_soup(url)
        links = [a['href'] for a in self.soup.find_all('a', href=True) 
                if '/film/' in a['href'] 
                and not a['href'].startswith('/pridat/')]
        return links

    async def fetch_top_300_movies_links(self):
        max_retries = 5  # maximum number of retries
        retry_delay = 3  # initial delay
        retries = 0

        offsets = [1, 100, 200, 300]
        movie_links = []

        while retries < max_retries:
            try:
                tasks = [self.extract_movie_links(f"{self.BASE_SEARCH_URL}&from={offset}") for offset in offsets]
                results = await asyncio.gather(*tasks)

                # Processing results in the correct order
                for index, links in enumerate(results):
                    if index == 3:  #
                        links = links[:2]  # Only grab the 2 three links to make total 300
                    movie_links.extend(links)

                return movie_links

            except Exception as e:
                print(f"Error occurred while fetching movie links: {e}. Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
                retries += 1
                retry_delay *= random.uniform(1, 2) 

        print(f"Failed to fetch movie links after {max_retries} retries.")
        return []

    async def extract_film_info(self, link):
        max_retries = 5 
        retry_delay = 3  # initial delay
        retries = 0

        while retries < max_retries:
            try:
                async with self.semaphore:
                    await asyncio.sleep(self.delay)
                    link = self.BASE_SITE_URL + link
                    await self.get_soup(link)
                    film_title = self.soup.select_one(".film-header-name h1").get_text(strip=True)
                    actors_element = self.soup.find("h4", string="Hrají:")
                    try:
                        actors_links = actors_element.find_next_siblings("a")
                    except Exception as e:
                        actors_links = []
                    actors = [link.get_text(strip=True) for link in actors_links]
                    return {
                        "link": link,
                        "title": film_title,
                        "actors": actors
                    }
            except Exception as e:
                print(f"Error occurred: {e}. Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
                retries += 1
                retry_delay *= random.uniform(1, 2)  

        print(f"Failed to fetch info for {link} after {max_retries} retries.")
        return None


    async def main(self):
        try:
            await self.start()
            top_300_links = await self.fetch_top_300_movies_links()
            
            tasks = [self.extract_film_info(link) for link in top_300_links]
            info = []
            for task in asyncio.as_completed(tasks):
                film_info = await task
                info.append(film_info)
        except Exception as e:
            print(e)
        finally:
            await self.close()
        return info

    async def close(self):
        if self.session:
            await self.session.close()

class Command(BaseCommand):
    help = 'Scrape CSFD for top 300 movies and their actors.'

    def handle(self, *args, **options):
        scraper = CsfdScraper()
        info = asyncio.run(scraper.main())

        for movie_info in info:
            movie, created = Movie.objects.get_or_create(title=movie_info['title'], link=movie_info['link'])
            for actor_name in movie_info['actors']:
                actor, created = Actor.objects.get_or_create(name=actor_name)
                movie.actors.add(actor)