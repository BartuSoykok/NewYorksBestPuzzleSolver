import re
import requests
from bs4 import BeautifulSoup
import BasicLogger
import Configs

BANNED_WORDS = Configs.get_setting('WORD', 'banned_words')

class Search:
    def __init__(self, clue_string, pattern=r'\b([a-zA-Z][a-zA-Z][a-zA-Z][a-zA-Z][a-zA-Z])[\.]?\b'):
        self.clue_string = clue_string.rstrip().lstrip()
        self.pattern = re.compile(pattern, re.IGNORECASE)

        # Output website
        if Configs.get_setting('SEARCH', 'show_parameters') == '1':
            BasicLogger.log("Clue:\t"+self.clue_string+"("+self.pattern.__str__()+")")
            print("Clue:\t", self.clue_string, "("+self.pattern.__str__()+")")

        self.word_freq = {}

    def googleSearch(self):
        from google import search
        return search(self.clue_string, lang='en', stop=1)

    def searchPage(self, target_page):
        # check for wikipedi if so use the 0wiki because its Turkey
        import urllib.parse
        parsed = urllib.parse.urlparse(target_page)
        if parsed.netloc == "en.wikipedia.org":
            parsed = parsed._replace(netloc="en.0wikipedia.org")
        elif parsed.netloc == "imgur.com":
            # Output website
            if Configs.get_setting('SEARCH', 'show_sites') == '1':
                BasicLogger.log("Can't check imgur.com in Turkey")
                print("Can't check imgur.com in Turkey")
            return
        elif "crossword" in parsed.netloc.lower() or "wordplays" in parsed.netloc.lower():
            # Output website
            if Configs.get_setting('SEARCH', 'show_sites') == '1':
                BasicLogger.log("Can't check crossword")
                print("Can't check crossword")
            return
        target_page = parsed.geturl()

        # Output website
        if Configs.get_setting('SEARCH', 'show_sites') == '1':
            BasicLogger.log("Checking for " + self.clue_string + ": " + target_page)
            print("Checking for", self.clue_string, ":", target_page)

        # Find words
        with requests.get(target_page) as response:
            if response.status_code == 200 and response.content != "\n":

                soup = BeautifulSoup(response.content)
                for elem in soup.findAll(['script', 'style', 'img']):
                    elem.extract()

                text = soup.get_text().upper()
                text = re.sub(r'&', 'AND', text)
                text = re.sub(r'_', ' ', text)
                text = re.sub(r'"', ' ', text)

                for word in self.pattern.findall(text):
                    word = re.sub(' ', '', word)
                    if word not in self.clue_string.upper() and word not in BANNED_WORDS:
                        if word not in self.word_freq:
                            self.word_freq[word] = 0
                        self.word_freq[word] += 1
            else:
                if Configs.get_setting('SEARCH', 'show_sites') == '1':
                    BasicLogger.log("Error code " + response.status_code)
                    print("Error code", response.status_code)



