# 
# 
# 

import unittest

from crawler import crawler



class VisitSetTest(unittest.TestCase):
    def setUp(self):
        # Called before the first testfunction is executed
        pass

    def tearDown(self):
        # Called after the last testfunction was executed
        pass
     
    def test_add_init(self):
        a_set = crawler.VisitSet()
        self.assertEqual(a_set.items_size(), 0)
        self.assertEqual(a_set.queue_size(), 0)
        
    def test_add_repeated(self):
        a_set = crawler.VisitSet()

        a_set.add("aaa")
        self.assertEqual(a_set.items_size(), 1)
        self.assertEqual(a_set.queue_size(), 1)
        
        a_set.add("aaa")
        self.assertEqual(a_set.items_size(), 1)
        self.assertEqual(a_set.queue_size(), 1)
        
    def test_add_two(self):
        a_set = crawler.VisitSet()
        
        a_set.add("aaa")
        a_set.add("bbb")
        self.assertEqual(a_set.items_size(), 2)
        self.assertEqual(a_set.queue_size(), 2)
        
    def test_next_empty(self):
        a_set = crawler.VisitSet()
        self.assertEqual(a_set.next(), "")
        self.assertEqual(a_set.items_size(), 0)
        self.assertEqual(a_set.queue_size(), 0)
        
    def test_next_normal(self):
        a_set = crawler.VisitSet()
        
        a_set.add("aaa")
        a_set.add("bbb")
        self.assertEqual(a_set.next(), "aaa")
        self.assertEqual(a_set.items_size(), 2)
        self.assertEqual(a_set.queue_size(), 1)
#======



class VisitListTest(unittest.TestCase):
    def setUp(self):
        # Called before the first testfunction is executed
        pass

    def tearDown(self):
        # Called after the last testfunction was executed
        pass
    
    def test_is_in_empty(self):
        vList = crawler.VisitList()
        self.assertEqual( vList.is_in("aaa"), False )
        
        
    def test_is_in_not(self):
        vList = crawler.VisitList()
        vList.add("aaa")
        vList.add("bbb")
        self.assertEqual( vList.is_in("ccc"), False )
        
        
    def test_is_in_exists(self):
        vList = crawler.VisitList()
        vList.add("aaa")
        vList.add("bbb")
        vList.add("ccc")
        self.assertEqual( vList.is_in("ccc"), True )
        
#======


    
class WebCrawlerTest(unittest.TestCase):
    def setUp(self):
        # Called before the first testfunction is executed
        pass

    def tearDown(self):
        # Called after the last testfunction was executed
        pass

#     def test_Crawler(self):
#         crawl = crawler.WebCrawler()
      
    def test_parse_request_empty(self):
        crawl = crawler.WebCrawler()
        crawl.parse_request( "" )
        self.assertEqual(crawl.search_url, "")
        #self.assertEqual(crawl.url_path, "")
        
    def test_parse_request_no_scheme(self):
        crawl = crawler.WebCrawler()
        crawl.parse_request( "www.google.com" )
        self.assertEqual( crawl.search_url, "http://www.google.com")
        #self.assertEqual( crawl.url_path, "http://www.google.com")
        
    def test_parse_request_slash(self):
        crawl = crawler.WebCrawler()
        crawl.parse_request( "www.google.com/" )
        self.assertEqual( crawl.search_url, "http://www.google.com/")
        #self.assertEqual( crawl.url_path, "http://www.google.com")
        
    def test_parse_request_main(self):
        crawl = crawler.WebCrawler()
        crawl.parse_request( "www.google.com/aaa" )
        self.assertEqual( crawl.search_url, "http://www.google.com/aaa")
        #self.assertEqual( crawl.url_path, "http://www.google.com")
        
    def test_parse_request_dir_slash(self):
        crawl = crawler.WebCrawler()
        crawl.parse_request( "http://www.google.com/aaa/" )
        self.assertEqual( crawl.search_url, "http://www.google.com/aaa/")
        #self.assertEqual( crawl.url_path, "http://www.google.com/aaa")
        
    def test_parse_request_deep(self):
        crawl = crawler.WebCrawler()
        crawl.parse_request( "http://www.google.com/aaa/bbb/ccc.html" )
        self.assertEqual( crawl.search_url, "http://www.google.com/aaa/bbb/ccc.html")
        #self.assertEqual( crawl.url_path, "http://www.google.com/aaa/bbb")
        
        
    def test_crawl(self):
        crawl = crawler.WebCrawler()
        crawl.crawl("www.google.com")
        self.assertGreater(crawl.extracted().items_size(), 12)
        
        
    def test_crawl_deep_negative(self):
        crawl = crawler.WebCrawler()
        crawl.crawl_deep("www.google.com", -1)
        self.assertEqual(crawl.extracted().items_size(), 0)
        
#     def test_crawl_deep_positive(self):
#         crawl = crawler.WebCrawler()
#         crawl.crawl_deep("www.google.com", 2)
#         self.assertGreater(crawl.extracted().items_size(), 800)


if __name__ == "__main__":
    unittest.main()
