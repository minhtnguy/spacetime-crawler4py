from threading import Thread
import nltk
nltk.download('stopwords')
from collections import Counter
from inspect import getsource
from utils.download import download
from utils import get_logger
import scraper
import time
from bs4 import BeautifulSoup
import re

longest_page_num_words = 0
longest_page_link = None
word_count = 0

class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {-1}, "Do not use requests in scraper.py"
        assert {getsource(scraper).find(req) for req in {"from urllib.request import", "import urllib.request"}} == {-1}, "Do not use urllib.request in scraper.py"
        super().__init__(daemon=True)
        
    def run(self):
        while True:
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                print("Longest Page URL:", longest_page_link)
                print("Longest Page Word Count:", longest_page_num_words)
                print("50 Common words: ", word_count)
                break
            resp = download(tbd_url, self.config, self.logger)
            self.magic(resp)
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")
            scraped_urls = scraper.scraper(tbd_url, resp)
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)

    def longest_page(self, resp):
        if resp.status == 200 and resp.raw_response.content:
            content = resp.raw_response.content
            soup = BeautifulSoup(content, 'html.parser')
            # remove html tags and extracts text
            page_text = soup.get_text()

            numWords = len(re.split('[^a-zA-Z0-9]', page_text))
            if numWords > longest_page_num_words:
                longest_page_num_words = numWords
                longest_page_link = resp.url
    

    