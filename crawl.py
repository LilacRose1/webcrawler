from urllib.parse import SplitResult, urlsplit, urljoin
from bs4 import BeautifulSoup

def normalize_url(url:str) -> str:
    url_split: SplitResult = urlsplit(url)
    normal_url: str = f"{url_split.netloc.lower()}{url_split.path}"
    normal_url: str = normal_url.rstrip('/')
    return normal_url

def get_heading_from_html(html: str) -> str:
    soup: BeautifulSoup = BeautifulSoup(html, "html.parser")

    if soup.find('h1'):
        return soup.find('h1').get_text(strip=True)
    elif soup.find('h2'):
        return soup.find('h2').get_text(strip=True)
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
        links_list.append(urljoin(base_url, link.get("href")))

    return links_list

def get_images_from_html(html: str, base_url: str) -> list[str]:
    soup: BeautifulSoup = BeautifulSoup(html, "html.parser")
    images = soup.find_all("img")
    images_list: list[str] = []

    for image in images:
        images_list.append(urljoin(base_url, image.get("src")))

    return images_list

