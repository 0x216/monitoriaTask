import aiohttp
from bs4 import BeautifulSoup
import asyncio

class CsfdScraper:
    BASE_SITE_URL = "http://www.csfd.cz"
    BASE_SEARCH_URL = f"{BASE_SITE_URL}/zebricky/filmy/nejlepsi/?showMore=1"
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    def __init__(self, max_concurrent=11, delay=0):
        self.session = None
        self.soup = None
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.delay = delay

    async def start(self):
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
        tasks = [self.extract_movie_links(f"{self.BASE_SEARCH_URL}&from={offset}") for offset in [1, 100, 200, 300]]
        movie_links = []
        for task in asyncio.as_completed(tasks):
            links = await task
            movie_links.extend(links)
        return movie_links[:300]

    async def extract_film_info(self, link):
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

if __name__ == "__main__":
    scraper = CsfdScraper()
    info = asyncio.run(scraper.main())
    print(info)
