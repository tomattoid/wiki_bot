import aiohttp
import asyncio
from bs4 import BeautifulSoup as bs
from fuzzywuzzy import process
from data_parser import read_pages, BASE_URL, HEADERS

data_from_file = read_pages()

class Parent:
    def __init__(self, name):
        self._name = name
        self._title = ""
        self._category = ""
        self._url = ""
        self._blocks = []
        self._img = None
        self.define_base_info()
        self.execute_parsing()
    
    def define_base_info(self):
        titles = []
        for elem in data_from_file:
            titles.append(elem["Title"])
        best_match = process.extractOne(self._name, titles)[0]
        for elem in data_from_file:
            if elem["Title"] == best_match:
                self._url = elem["Link"]
                self._title = elem["Title"]
                self._category = elem["Category"]

    def get_blocks(self):
        return self._blocks

    def get_url(self):
        return self._url
    
    def get_category(self):
        return self._category
    
    def get_name(self):
        return self._name
    
    def get_title(self):
        return self._title
    
    def get_img(self):
        return self._img
    
    def set_name(self, new_name):
        self._name = new_name
        self.define_url_title()
    
    def execute_parsing(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.parse_info())
    
    async def parse_info(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(BASE_URL + self._url, headers=HEADERS) as response:
                r = await aiohttp.StreamReader.read(response.content)
                soup = bs(r, "html.parser")
                img = soup.find("img", {"class": "pi-image-thumbnail"})
                if not img:
                    img = soup.find("img", {"class": "thumbimage"})
                self._img = img.get("src") if img else None
                headers = soup.find("div", {"class": "mw-parser-output"}).find_all("h2")
                page_cut = soup.find("div", {"class": "mw-parser-output"})
                self._blocks = ["" for _ in headers]
                self._blocks.append("")
                description_div = soup.find("div", {"class": "io"})
                if description_div:
                    self._blocks.append("")
                    description = description_div.find_all("i")
                    description_str = f"<b><u><i>{self._title}</i></u></b>\n\n<b>Описание:</b>\n"
                    for text in description:
                        description_str += "<i>" + text.text.strip() + "</i> "
                else:
                    description_str = f"<b><i><u>{self._title}</u></i></b>"
                self._blocks[0] = description_str
                for header in range(len(headers)):
                    if headers[header].get("id") != "Галерея" and headers[header]("id") != "Ссылки":
                        page_cut = headers[header].find_all_next()
                        str = self.parse_block(page_cut, headers[header].text)
                        self._blocks[header+1] = str
    
    def parse_block(self, page_cut, header):
        str = "<b>" + header + "</b>\n"
        for tag in page_cut:
            if tag.name == "h2" or tag.name == "table" or tag.name == "div":
                break
            elif tag.name == "li" and tag.name != "ul":
                str += "- " + tag.text + "\n"
            elif tag.name == "a" or tag.name == "ul" or tag.name == "b":
                continue
            elif tag.name == "h3":
                str += "<b>" + tag.text + "</b>\n"
            else:
                str += tag.text + " "
        return str

