from urllib.parse import SplitResult, urlsplit, urljoin
from bs4 import BeautifulSoup
import requests
def normalize_url(url:str) -> str:
    url_split: SplitResult = urlsplit(url)
    normal_url: str = f"{url_split.netloc.lower()}{url_split.path}"
    normal_url: str = normal_url.rstrip('/')
    return normal_url.lower()

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
            print(f"{str(e)}: {link.get("href")}")
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

def get_html(url):
    try:
        response = requests.get(url, headers={"User-Agent": "BootCrawler/1.0"})
    except Exception as e:
        raise Exception(f"Error: {e}")
    if response.status_code >= 400:
        raise Exception("error communication with the server")
    elif "text/html" not in response.headers["content-type"]:
        raise Exception("content is not a html or text")

    return response.text

def crawl_page(base_url, 
               current_url: str | None = None, 
               page_data: dict[dict, str] | None = None):

    if current_url is None:
        current_url = base_url

    if page_data is None:
        page_data = {}

    if urlsplit(base_url).netloc.lower() != urlsplit(current_url).netloc.lower():
        return page_data

    normal_url = normalize_url(current_url)

    if normal_url in page_data.keys():
        return page_data

    try:
        html = get_html(current_url)
    except Exception as e:
        print(f"Error: {e}")

    data = extract_page_data(html, current_url)

    page_data[normal_url] = data

    for url in page_data[normal_url]["outgoing_links"]:
        page_data = crawl_page(base_url, url, page_data)

    return page_data













