import aiohttp
from bs4 import BeautifulSoup as bs
from fake_useragent import UserAgent
import json, os, asyncio

HOME_URL = "https://sekiro.fandom.com/ru/wiki/%D0%A1%D0%BB%D1%83%D0%B6%D0%B5%D0%B1%D0%BD%D0%B0%D1%8F:%D0%92%D1%81%D0%B5_%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D1%8B"
HOME_URL2 = "https://sekiro.fandom.com/ru/wiki/%D0%A1%D0%BB%D1%83%D0%B6%D0%B5%D0%B1%D0%BD%D0%B0%D1%8F:%D0%92%D1%81%D0%B5_%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D1%8B?from=%D0%9F%D0%BE%D1%81%D0%BB%D0%B5%D0%B4%D0%BD%D0%B8%D0%B9+%D1%83%D0%BA%D1%83%D1%81"
BASE_URL = "https://sekiro.fandom.com"
HEADERS = {"User-Agent": UserAgent().random}
filename = "data.json"


async def parse_all():
    pages = []
    valid_categories = ["Геймплей", "Инструменты для протеза", 
                        "Концовки", "Локации", "Лор", "Навыки", 
                        "Персонажи", "Предметы", "Противники"]
    async with aiohttp.ClientSession() as session:
        async with session.get(HOME_URL, headers=HEADERS) as response:
            r = await aiohttp.StreamReader.read(response.content)
            soup = bs(r, "html.parser")
            main_div = soup.find("ul", {"class": "mw-allpages-chunk"})
            pages += main_div.find_all("a")
        async with session.get(HOME_URL2, headers=HEADERS) as response:
            r = await aiohttp.StreamReader.read(response.content)
            soup = bs(r, "html.parser")
            main_div = soup.find("ul", {"class": "mw-allpages-chunk"})
            pages += main_div.find_all("a")
    formatted_pages = []
    category = ""
    async with aiohttp.ClientSession() as session:
        for page in pages:
            async with session.get(BASE_URL + page.get("href"), headers=HEADERS) as response:
                r = await aiohttp.StreamReader.read(response.content)
                soup = bs(r, "html.parser")
                category_tag1 = soup.find("a", {"data-tracking-label": "categories-top-more-0"})
                category_tag2 = soup.find("a", {"data-tracking-label": "categories-top-more-0"})
                if not category_tag1 and not category_tag2:
                    continue
                category1 = category_tag1.text
                category2 = category_tag2.text
                if category1 not in valid_categories:
                    if category2 not in valid_categories:
                        continue
                    else:
                        category = category2
                else:
                    category = category1
            page = {"Title": page.text, "Link": page.get("href"), "Category": category}
            formatted_pages.append(page)
    return formatted_pages

def read_pages():
    if os.path.isfile(filename):
        with open(filename, "r") as f:
            data = json.load(f)
            if data:
                return data
            else:
                return write_pages()
    else:
        return write_pages()

def write_pages():
    with open(filename, "w") as f:
            loop = asyncio.get_event_loop()
            pages = loop.run_until_complete(parse_all())
            json.dump(pages, fp=f, indent=4)
            return pages
