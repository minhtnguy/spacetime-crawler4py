import re
import pickle
import nltk
nltk.download('stopwords')

from urllib.parse import urlparse
from urllib.parse import urljoin
from urllib.parse import parse_qs
from urllib.parse import urldefrag

from collections import Counter
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from simhash import Simhash, SimhashIndex

all_links = set()
simhash_index = SimhashIndex([], k=3)


def scraper(url, resp):
    new_links = extract_next_links(url, resp)
    return [link for link in new_links if is_valid(link)]


def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    global all_links, simhash_index

    new_links = []
    if resp.status == 200:
        content = resp.raw_response.content
        # if page is empty return empty list (no links to extract)
        if not content:
            return []
        
        soup = BeautifulSoup(content, 'html.parser')
        # remove html tags and extracts text
        page_text = soup.get_text()  
        
        
        simhash = Simhash(page_text)
        # check if page is similar to previously visited pages
        if simhash_index.get_near_dups(simhash):
            return []
        simhash_index.add(url, simhash)
        
        for link in soup.find_all('a'):
            link = link.get('href')
            # check if link is valid and has not been visted yet
            if link and is_valid(link) and link not in all_links:
                new_links.append(link)
                if urljoin(url, link) != resp.url:
                    print("Detected redirect from {} to {}".format(urljoin(url,link),resp.url))
                all_links.add(link) 

    return new_links


def is_valid(url):
    # Decide whether to crawl this url or not.
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        if not any(parsed.netloc.endswith(domain) for domain in [".ics.uci.edu", ".cs.uci.edu", ".informatics.uci.edu", ".stat.uci.edu"]):
            return False
        # if url contains unwanted paths (pages with no info)
        if re.search(r".*(/calendar|/mailto:http|/files/|/publications/|/papers/)", parsed.path.lower()):
            return False
        # checks if first 9 characters of url path matches /wp-json/
        if re.match(r"/wp-json/", parsed.path.lower()[0:9]):
            return False
        
        # will parse for action parameter, if paramteter is action to download is found, rejects URL
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        if "action" in params and "download" in params["action"]:
            return False
        
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print("TypeError for ", parsed)
        raise
 
# def main():
#     get_unique_urls = unique_urls()
#     print("Unique pages: ", get_unique_urls)
    
#     get_longest_page = longest_page()
#     print("Longest page: ", get_longest_page)
    
#     get_common_words = common_words()
#     print("50 most common words: ", get_common_words)
    
#     get_subdomains = count_subdomains()
#     print("Subdomains found: ", get_subdomains)
    
    
if __name__ == '__main__':
    main()