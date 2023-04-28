import re
import pickle
from urllib.parse import urlparse

from collections import Counter
# from bs4 import BeautifulSoup
from nltk.corpus import stopwords


def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]


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

    try:
        getAll = resp.raw_response.content.decode("utf-8")

        # Gets all links within domain then defragments
        urls = re.findall(r'href=["\']?([^"\'>]+)', getAll) 

        domain_links = []
        for url in urls:
            parsed_url = urlparse(url)
            if parsed_url.scheme and parsed_url.netloc:  # Check if the URL has domain
                domain_links.append(parsed_url.geturl())  # Appends valid URL to list

        return domain_links

    except Exception as ex:
        print("Error in extract_next_links")
        return
    # create beautiful soup object
    # soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
    # links = []

    # # find all <a> tags to extract links
    # for link in soup.findAll('a', href='True'):
    #     href = link.get('href')

    #     # defragment the URLs (not sure if it goes here or in is_valid)
    #     href = href.split('#')[0]

    #     # check if link is valid
    #     if is_valid(href):
    #         links.append(href)

    # return links


def is_valid(url):
    # Decide whether to crawl this url or not.
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        if parsed.hostname not in set(["ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu"]):
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


# counts the number of words on a page, uses tokenizer logic (still need to figure out parameter)
def word_count(page):
    numWords = 0
    for word in re.split('[^a-zA-Z0-9]', page):
        word = word.lower()
        alpha_word = ""
        for letter in word:
            # if in alphabet
            if ord(letter) >= 97 and ord(letter) <= 122:
                alpha_word += letter
                # if a number
            if ord(letter) >= 48 and ord(letter) <= 57:
                alpha_word += letter
        numWords += 1
    return numWords


# finds the 50 most common words
def common_words(pages):
    stopwords = set(stopwords.words('english'))
    word_count = Counter()

    for page in pages:
        soup = BeautifulSoup(page, 'html.parser')
        text = soup.get_text()
        words = re.findall(r'\b\w+\b', text.lower())
        # if word is is not in stopwords list, add to word_count
        word_count.update(word for word in words if word not in stopwords)

    return [word for word, count in word_count.most_common(50)]

# find all unique urls
def unique_urls(url):
    #for each url, find the first like url part, and if its unique add it to count.
    list = []
    parsed = urlparse(url)
    checkurl = parsed.hostname

    if checkurl not in list:
        list.append(checkurl)

    return len(list)