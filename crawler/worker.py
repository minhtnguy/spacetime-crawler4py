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
from nltk.corpus import stopwords
from urllib.parse import urlparse
from urllib.parse import urldefrag

longest_page_num_words = 0
longest_page_link = None
word_count = Counter()
unique_urls = 0

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
                print("Longest Page URL:")
                print("Longest Page Word Count:")
                print("50 Common words: ")
                print("Number of Unique URLs: ")

                break
            resp = download(tbd_url, self.config, self.logger)
            time.sleep(self.config.time_delay)
            if resp.status != 200 or resp.raw_response.content is None:
                continue
            self.longest_page(resp)
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")
            scraped_urls = scraper.scraper(tbd_url, resp)
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)

#     def longest_page(self, resp):
#         content = resp.raw_response.content
#         soup = BeautifulSoup(content, 'html.parser')
#         # remove html tags and extracts text
#         page_text = soup.get_text()

#         numWords = len(re.split('[^a-zA-Z0-9]', page_text))
#         if numWords > longest_page_num_words:
#             longest_page_num_words = numWords
#             longest_page_link = resp.url
    
#     def common_words(self, resp):
#         content = resp.raw_response.content
#         stopwords_list = set(stopwords.words('english'))

#         soup = BeautifulSoup(content, 'html.parser')
#         text = soup.get_text()
#         words = re.findall(r'\b\w+\b', text.lower())
#         # if word is is not in stopwords list, add to word_count
#         word_count.update(word for word in words if word not in stopwords_list)
        
    
#     def unique_urls(self, resp):
#     # for each url, find the first like url part, and if its unique add it to count.
#         content = resp.raw_response.content
#         unique_urls = set()
#         parsed = urlparse(content)
#         # remove fragment
#         url_without_fragment = urldefrag(content).content
#         unique_urls.add(url_without_fragment)

#     # finds subdomains in ics.uci.edu domain
# def count_subdomains(self, resp):
#     subdomains = {}
#     subdomain_count = []
#     content = resp.raw_response.content

#     parsed_url = urlparse(content)
#         # split domain into different parts
#     domain_parts = parsed_url.netloc.split('.')
#         # check if domain is in ics.uci.edu
#     if parsed_url.netloc.endswith('.ics.uci.edu'):
#             # extract first part of domain
#         subdomain = domain_parts[-4]
#         # add to set
#     if subdomain not in subdomains:
#             subdomains[subdomain] = set()
        
#         subdomains[subdomain].add(link)
        
#         # loop through each subdomain and count how many there are
#     for subdomain, links in subdomain.items():
#         pages_count = len(links)
#         subdomain_count.append(('http://{}.ics.uci.edu'.format(subdomain), pages_count))
            
#     return sorted(subdomain_count)

    