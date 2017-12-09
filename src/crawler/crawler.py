# MIT License
# 
# Copyright (c) 2017 Arkadiusz Netczuk <dev.arnet@gmail.com>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


#try:
    ## Python 3
    #from urllib.parse import urlparse, parse_qs
#except ImportError:
    ## Python 2
    #from urlparse import urlparse, parse_qs
    
from urlparse import urljoin
    

import pycurl
from StringIO import StringIO

import re               ## regexp



class VisitSet:
    
    def __init__(self):
        self.items_set = set()
        self.queue_list = []
    
    def add(self, item):
        if item not in self.items_set:
            #print( "adding %s" % item )
            self.items_set.add(item)
            self.queue_list.append(item)
        #else:
            #print( "skipping %s" % item )
            
    def add_list(self, aList):
        for item in aList:
            ##print item
            self.add( item )
            
    def items_size(self):
        return len( self.items_set )

    def queue_size(self):
        return len( self.queue_list )
    
    def next(self):
        if self.queue_size() ==0:
            return ''
        return self.queue_list.pop(0)

    def print_state(self):
        #print("state: none")
        print("links set:\n    %s" % ("\n    ".join(self.items_set)) )
    
#==========



class VisitList:
    
    def __init__(self):
        self.items_list = []
    
    
    def items(self):
        return self.items_list
    
    
    def items_size(self):
        return len( self.items_list )
    
    
    def is_in(self, item):
        return (item in self.items_list)
            
        
    def add_list(self, aList):
        for item in aList:
            self.add( item )
            
            
    def add(self, item):
        if item not in self.items_list:
            self.items_list.append(item)
        #else:
            #print( "skipping %s" % item )

    
    def print_state(self):
        #print("state: none")
        print("links set:\n    %s" % ("\n    ".join(self.items_list)) )

#==========

    
    
class WebCrawler:
    
    def __init__(self):
        self.search_url = ""
        
        ### Contains domain with path (without terminating slash), e.g.:
        ###      http://www.abc.com/aaa/bbb/ccc -> http://www.abc.com/aaa/bbb
        ###      http://www.abc.com/aaa/bbb/ccc.html -> http://www.abc.com/aaa/bbb
        #self.url_path = ""
        
        #self.url_query = ""
        
        self.extracted_list = VisitList()       ## found links
    
    
    def print_state(self):
        print("state url: %s" % self.search_url )
        self.extracted_list.print_state()
        #print("links set for [%s]:\n    %s" % (self.search_url, "\n    ".join(self.links_set)) )
        
        
    def crawl(self, url):
        self.crawl_deep(url, 1)
        
        
    def crawl_deep(self, url, depth):
        self.parse_request( url )
        
        if depth<0:
            return
        
        level_items = []
        first_url = self.join_url( '' )
        self.extracted_list.add( first_url )
        level_items.append( first_url )
        
        for level in range(0, depth):
            print( "\nNext level %s: items %s" % (level, len(level_items)) )
            
            next_level = []
            for visit in level_items:
                links = self.extract_links( visit )
                
                ##self.extracted_list.add_list( links )
                
                for item in links:
                    target_url = self.join_url( item ) 
                    if not self.extracted_list.is_in(target_url):
                        ##print( "Found: %s", target_url)
                        self.extracted_list.add( target_url )
                        next_level.append( target_url )
                #---
            #---
            
            if len(next_level) <= 0:
                ## no more elements
                print( "Done. No more links to visit" )
                break
            #---
            
            level_items = next_level
        #---
    #===
        
    def extracted(self):
        return self.extracted_list
    
    
    def join_url(self, url):
        hash_pos = url.find('#')
        if hash_pos<0:
            return urljoin( self.search_url, url ) 
        
        trimmed = url[:hash_pos]
        return urljoin( self.search_url, trimmed ) 
    #===
    
    
    def parse_request(self, url):
        if len(url) < 1:
            return 
        
        #print( "checking: %s" % url)
        self.search_url = url;
        http_pos = url.find("http")
        if http_pos != 0:
            self.search_url = "http://" + self.search_url
    #===            
    
    
    def extract_links(self, target_url):
        ##target_url = self.join_url( url )
        ##print("join %s & %s -> %s" % (self.search_url, url, target_url))
        print( "Visiting: %s" % target_url )
        
        sbuffer = StringIO()
        c = pycurl.Curl()
        c.setopt(c.URL, target_url)
        c.setopt(c.WRITEDATA, sbuffer)
        c.setopt(c.FOLLOWLOCATION, True)        ## follow redirects
        c.perform()
        c.close()

        bodyOutput = sbuffer.getvalue()
        body = bodyOutput.lower()
        
        # Body is a string in some encoding.
        # In Python 2, we can print it without knowing what the encoding is.
        ##print(body)
        
        ## urlparse - extract url components
        
        ##linkregex = re.compile('<a\s*href=[\'|"](.*?)[\'"].*?>')
        linkregex = re.compile('<a[^>]*href=[\'|"](.*?)[\'"].*?>')
        links = linkregex.findall( body )
        return links

#==========



if __name__ == "__main__":
    c = WebCrawler()
    c.printState()
