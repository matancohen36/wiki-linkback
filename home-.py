import sys
import urllib.request 
from pprint import pprint
from html.parser import HTMLParser 
from urllib.parse import urlparse, urljoin

class WikiScrapper(HTMLParser):
    def __init__(self, content, filter_func = None):  #setting the parser
        self._links = set()
        self._filter_func = filter_func 
        super().__init__()
        super().feed(content)
    
    @property
    def links(self):
        return self._links

    def feed(self, *args, **kwargs):
        assert False, "Should not use directly"

    def handle_starttag(self, tag, attrs):
        if tag != 'a':
            return # skip 

        for key, value in attrs:
            if key != "href":
                continue # Skip value

            if self._filter_func and not self._filter_func(value):
                return # Skip value
            
            self._links.add(value)
            return

def is_wiki_page(url):
    bad_links = ["/wiki/File:" , "/wiki/Special:" , "/wiki/Category:", "/wiki/Wikipedia:"]
    if not url.startswith("/wiki/"):
        return False
    
    for bad_link in bad_links:
        if url.startswith(bad_link):
            return False

    return True
                
def extract_links(content, filter_func=None):
    parser = WikiScrapper(content, filter_func)
    return parser.links

def get_links_from_url(url, filter_func=None): #method that fetching url and extract all urls from it 
    try:
        with urllib.request.urlopen(url) as response: #fetching the page
            data=response.read().decode("utf-8", errors = 'ignore' ) #decoding the resualt into str
            return extract_links(data, filter_func)
    except urllib.request.HTTPError as exception: #handeling errors
        print(exception)

def generate_absoulte_url(input_url, link): #util method to format the links
    return urljoin(input_url, link)

def generate_relative_link(input_url):
    parsed_url = urlparse(input_url)
    return parsed_url.path

def measure(f):
    def wrapper(*args, **kwargs):
        import time
        start_time = time.time()
        res = f(*args, **kwargs)
        print("--- %s took %s seconds ---" % (f.__name__, time.time() - start_time))
        return res
    
    return wrapper

@measure
def main(input_url):
    output_urls=[] 
    relative_link = generate_relative_link(input_url).lower()
    filter_for_self_links = lambda x: x.lower() == relative_link
    self_links = get_links_from_url(input_url, is_wiki_page)
    
    for link in self_links:
        url = generate_absoulte_url(input_url, link)
        curr_url_links = get_links_from_url(url, filter_for_self_links)
        if not len(curr_url_links):
            continue

        output_urls.append(url)

    print("Done, All links from %s that link back are:" % input_url)
    pprint(output_urls)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: %s <inputLink>" % sys.argv[0])
        sys.exit(-1)
    
    main(sys.argv[1])