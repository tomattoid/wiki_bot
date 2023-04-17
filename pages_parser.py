import aiohttp
import asyncio
from bs4 import BeautifulSoup as bs
from fuzzywuzzy import process
from data_parser import read_pages, BASE_URL, HEADERS
import re

data_from_file = read_pages()

class Page:
    def __init__(self, name):
        self._name = name
        self._title = ""
        self._category = ""
        self._url = ""
        self._blocks = [""]
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
                aside = soup.find("aside", {"role": "region"})
                if not aside:
                    headers_below = soup.find("div", {"class": "mw-parser-output"}).find_all_next("h2")
                    page_cut = soup.find("div", {"class": "mw-parser-output"})
                    self._blocks[0] = self.parse_block(page_cut)
                else:
                    headers_below = aside.find_all_next("h2")
                    self._blocks[0] = "<b><i><u>" + self._title + "</u></i></b>\n\n"
                headers_above = soup.find("div", {"class": "license-description"}).find_all_previous("h2")
                headers = []
                for element in headers_below:
                    if element in headers_above:
                        headers.append(element)
                self._blocks += ["" for _ in headers]    
                self._blocks.append("")    
                description_div = soup.find("div", {"class": "io"})
                if description_div:
                    self._blocks.append("")
                    description = description_div.find_all("i")
                    description_str = "<b>Описание:</b>\n"
                    for text in description:
                        description_str += "<i>" + text.text.strip() + "</i> "
                else:
                    description_str = ""
                self._blocks[0] += description_str
                for header in range(len(headers)):
                    if headers[header].get("id") != "Галерея" and headers[header]("id") != "Ссылки" and headers[header].text != "Содержание":
                        page_cut = headers[header].find_all_next()
                        str = self.parse_block(page_cut, headers[header].text)
                        self._blocks[header+2] = str
    
    def parse_block(self, page_cut, header=""):
        str = "<b>" + header + ":</b>\n" if header else ""
        for tag in page_cut:
            tmp = tag.text.strip() if tag.text else ""
            tmp = tmp.replace('<', '&lt;')
            tmp = tmp.replace('<', '&gt;')
            tmp = tmp.replace('<', '&amp;')
            if tag.name == "h2" or tag.name == "table" or tag.name == "div" or tag.parent.name == "aside":
                break
            elif tag.name == "li" and tag.name != "ul":
                str += "- " + tmp + "\n\n"
            elif tag.name == "a" or tag.name == "ul" or tag.name == "b" or tag.name == "sup" or tag.name == "span":
                continue
            elif tag.name == "h3":
                str += "<b><u>" + tmp + "</u></b>\n"
            else:
                str = str + tmp + " " if tmp else str
        str = re.sub(r'\[[^]]*\]', '', str)
        return str if str != "<b>" + header + ":</b>\n" else ""

