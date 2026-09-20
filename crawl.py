from urllib.parse import SplitResult, urlsplit, urljoin
from bs4 import BeautifulSoup
import asyncio
import aiohttp

class AsyncCrawler:
    def __init__(self, base_url, max_concurrency, max_pages):
        self.base_url = base_url
        self.base_domain = urlsplit(base_url).netloc
        self.page_data = {}
        self.visited = set()
        self.lock = asyncio.Lock()
        self.max_concurrency = max_concurrency
        self.semaphore = asyncio.Semaphore(self.max_concurrency)
        self.session = None
        self.max_pages = max_pages
        self.should_stop = False
        self.all_tasks = set()

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self


    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def add_page_visit(self, normalized_url):
        if self.should_stop:
            return False

        async with self.lock:

            if len(self.visited) >= self.max_pages:
                self.should_stop = True
                print("Reached maximum number of pages to crawl")
                return False

            if normalized_url in self.visited:
                return False
            else:
                self.visited.add(normalized_url)
                return True


    async def get_html(self, url):
        try:
            async with self.session.get(url) as response:
                if response.status >= 400:
                    raise Exception("error communication with the server")
                elif "text/html" not in response.headers.get("content-type", ""):
                    raise Exception("content is not a html or text")
                html = await response.text()
        except Exception as e:
            raise Exception(f"Error: {e}")

        return html

    async def crawl_page(self, current_url: str | None = None):
        try:
            if self.should_stop:
                return self.page_data

            if current_url is None:
                current_url: str = self.base_url

            if urlsplit(self.base_url).netloc.lower() != urlsplit(current_url).netloc.lower():
                return self.page_data

            normal_url = normalize_url(current_url)

            new_page: bool = await self.add_page_visit(normal_url)

            if not new_page:
                return self.page_data

            if normal_url in self.page_data.keys():
                return self.page_data

            async with self.semaphore:
                try:
                    html = await self.get_html(current_url)
                    data = extract_page_data(html, current_url)
                    async with self.lock:
                        self.page_data[normal_url] = data
                except Exception as e:
                    print(f"Error: {e}")
                    return self.page_data

            for url in self.page_data[normal_url]["outgoing_links"]:
                task = asyncio.create_task(self.crawl_page(url))
                self.all_tasks.add(task)

        finally:
            self.all_tasks.discard(asyncio.current_task())


    async def crawl(self):
        await self.crawl_page(self.base_url)
        while len(self.all_tasks) > 0:
            await asyncio.wait(self.all_tasks.copy(), return_when=asyncio.FIRST_COMPLETED)
        return self.page_data


def normalize_url(url:str) -> str:
    url_split: SplitResult = urlsplit(url)
    normal_url: str = f"{url_split.netloc.lower()}{url_split.path}"
    normal_url: str = normal_url.rstrip('/')
    return normal_url.lower()

async def crawl_site_async(base_url, max_concurrency, max_pages):
    async with AsyncCrawler(base_url, max_concurrency, max_pages) as Crawler:
        data = await Crawler.crawl()

    return data


def get_heading_from_html(html: str) -> str:
    soup: BeautifulSoup = BeautifulSoup(html, "html.parser")

    if soup.find("h1"):
        return soup.find("h1").get_text(strip=True)
    elif soup.find("h2"):
        return soup.find("h2").get_text(strip=True)
    else:
        return ""

def get_first_paragraph_from_html(html: str) -> str:
    soup: BeautifulSoup = BeautifulSoup(html, "html.parser")

    if soup.main:
        if soup.main.p:
            return soup.main.p.text
        elif soup.p:
            return soup.p.text
        else:
            return ""
    elif soup.p:
        return soup.p.text
    else:
        return ""

def get_urls_from_html(html: str, base_url: str) -> list[str]:
    soup: BeautifulSoup = BeautifulSoup(html, "html.parser")
    links = soup.find_all("a")
    links_list: list[str] = []

    for link in links:
        try:
            links_list.append(urljoin(base_url, link.get("href")))
        except Exception as e:
            print(f"{str(e)}: {link.get('href')}")
    return links_list

def get_images_from_html(html: str, base_url: str) -> list[str]:
    soup: BeautifulSoup = BeautifulSoup(html, "html.parser")
    images = soup.find_all("img")
    images_list: list[str] = []

    for image in images:
        images_list.append(urljoin(base_url, image.get("src")))

    return images_list

def extract_page_data(html: str, page_url: str):
    page_data = {}
    page_data["url"] = page_url
    page_data["heading"] = get_heading_from_html(html)
    page_data["first_paragraph"] = get_first_paragraph_from_html(html)
    page_data["outgoing_links"] = get_urls_from_html(html, page_url)
    page_data["image_urls"] = get_images_from_html(html, page_url)
    return page_data

