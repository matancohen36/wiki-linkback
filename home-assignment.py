import sys
import urllib.request 
from pprint import pprint
from html.parser import HTMLParser 
from urllib.parse import urlparse, urljoin
from queue import Queue 
import threading
import time


DOMAIN = 'wikipedia.org'
NUMBER_OF_THREADS = 20



class WikiScrapper(HTMLParser):
    def __init__(self, content, filter_func = None):
        # Varible to be used to collect all links in content
        self._links = set()

        # Optional filter function that can be used to filter saved links.
        self._filter_func = filter_func 

        # Trigger super function to start the collection
        super().__init__()
        super().feed(content)
    
    @property
    def links(self):
        return self._links

    def feed(self, *args, **kwargs):
        # Reject feeding more data after collection is done
        # to avoid links of more then single page.
        assert False, "Should not use directly"

    def handle_starttag(self, tag, attrs):
        # overrides super method, called for each html tag.
        if tag != 'a':
            return 
        
        for key, value in attrs:
            if key != "href":
                continue
            
            # If filter functinon provided, skip value if returns false.
            if self._filter_func and not self._filter_func(value):
                break
            
            self._links.add(value)
            break

def is_wiki_page(link):
    # Filter function thats return true if the given link is Wikipedia valid link
    if not link.startswith("/wiki/"):
        return False

    #wiki had some non end links like "Special:" in their path that arent a link so i did that to prevent them.
    if ":" in link:
        return False
        
    return True
                
def extract_links(content, filter_func=None):
    #Extract the links using my wikiscrapper a AST parser 
    parser = WikiScrapper(content, filter_func)
    # taking only the links from my AST obj
    return parser.links

def get_links_from_url(url, filter_func=None):
    #Gets url source-code and extract all urls from it 
        with urllib.request.urlopen(url) as response:
            #Decoding the result into str
            page_data = response.read().decode("utf-8", errors = 'ignore' ) 
            return extract_links(page_data, filter_func)

def generate_absoulte_url(input_url, link): 
    #util function to format the links
    return urljoin(input_url, link)

def generate_relative_link(input_url):
    #gets input_url path 
    parsed_url = urlparse(input_url)
    return parsed_url.path

def measure(f):
    #measuring the time of the script 
    def wrapper(*args, **kwargs):
        start_time = time.time()
        res = f(*args, **kwargs)
        print("--- %s took %s seconds ---" % (f.__name__, time.time() - start_time))
        return res
    
    return wrapper

def worker_func(work_queue, results, filter_for_self_links):
    while not work_queue.empty():
        # gets the worker "task"from the queue url in that case.
        url = work_queue.get()
        # gets all links from curr url and filtering if there is linkback
        curr_url_links = get_links_from_url(url, filter_for_self_links)
        if len(curr_url_links):
            results.append(url)
        #finising the task
        work_queue.task_done()

@measure
def main(input_url):
    # making sure ur input is wikipedia only
    if DOMAIN not in urlparse(input_url).netloc :
        print('Please run it with wikipedia page')
        return

    output_urls=[]

    # Generate filter function for returning to self link
    relative_link = generate_relative_link(input_url).lower()
    filter_for_self_links = lambda x: x.lower() == relative_link
    
    # Get all of links from url webpage source code
    init_start_time = time.time()
    self_links = get_links_from_url(input_url, is_wiki_page)
    print("input_url links gathering took:%s seconds" % (time.time() - init_start_time))
    # Prepare work queue
    q = Queue()
    for link in self_links:
        # to prevent counting the original input url 
        if filter_for_self_links(link):
            continue
        #formatting the link to url before pushing into the workqueue
        url = generate_absoulte_url(input_url, link)
        q.put(url)

    # Launch threads to process work queue
    workers_procces_start_time = time.time()
    for i in range(NUMBER_OF_THREADS):
        worker = threading.Thread(target=worker_func, daemon=True,
                                  args=(q, output_urls, filter_for_self_links,))
        worker.start()

    # Wait for work queue to be empty.
    q.join()
    print("getting workers proccesed work took:%s seconds" % (time.time() - workers_procces_start_time))
    # Print results
    print("Done, All links from %s that link back are (Total of %d) and waiting for u in: %s_wiki_linkbacks.txt" % (input_url, len(output_urls) ,relative_link[6:] ))
    with open("%s_wiki_linkbacks.txt" % (relative_link[6:]), 'w') as f:
        f.writelines("%s\n" % url  for url in output_urls)
        #to get output by print just exclude from comment the lines below
    # print("Done, All links from %s that link back are (Total of %d):" % (input_url, len(output_urls)))
    # pprint(output_urls)


# # trigger main only if ran as execute
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: %s <inputLink>" % sys.argv[0])
        sys.exit(-1)
    #extract the input link
    main(sys.argv[1])