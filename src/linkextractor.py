#!/usr/bin/python
#!/usr/bin/env python3
#
#
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


import sys
import argparse
import logging

from crawler.crawler import WebCrawler



## ============================= main section ===================================


if __name__ != '__main__':
    sys.exit(0)



parser = argparse.ArgumentParser(description='Extract links from web site')
#parser.add_argument('--algorithm', "-a", action='store', required=False, default="NM", choices=["NM"], help='Algorithm: NMerge' )
parser.add_argument('--link', '-l', action='store', required=True, help='Website to crawl' )
parser.add_argument('--depth', '-d', action='store', required=False, default=1, help='Crawl depth' )
parser.add_argument('--output', '-o', action='store', required=False, default="output.txt", help='Output file' )
 
 
args = parser.parse_args()
 

logging.basicConfig(level=logging.DEBUG)


print "Starting..." 


rootLink = args.link
depth = int(args.depth)
output = args.output

## http://www.deeplearningbook.org/

crawler = WebCrawler()


try:

    crawler.crawl_deep( rootLink, depth )        
    #crawler.print_state()

finally:
    print "Storing links..." 
    extracted = crawler.extracted().items()
    
    output_file = open(output, 'w')
    for item in extracted:
        output_file.write("%s\n" % item)
