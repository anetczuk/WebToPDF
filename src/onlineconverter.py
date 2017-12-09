#!/usr/bin/python
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
import StringIO

import pycurl
import re
import io
import argparse
import urllib


if __name__ != '__main__':
    sys.exit(1)
    

parser = argparse.ArgumentParser(description='Convert webpage using online converter')
#parser.add_argument('--algorithm', "-a", action='store', required=False, default="NM", choices=["NM"], help='Algorithm: NMerge' )
parser.add_argument('--link', '-l', action='store', required=True, help='Website to convert' )
parser.add_argument('--output', '-o', action='store', required=True, help='Output file' )
 
 
args = parser.parse_args()


source_link = args.link
output_file = args.output



##
## only 30 pages per month
##
def web2pdfconvert(sourceUrl):
    quotedurl = urllib.quote(sourceUrl, safe='')    
    target_url = "https://www.web2pdfconvert.com/engine.aspx?cURL="  + quotedurl + "&lowquality=false&porient=portrait&infostamp=false&logostamp=true&allowplugins=false&allowscript=true&showpagenr=false&margintop=10&marginleft=5&marginbottom=10&marginright=5&psize=a4&userpass=&ownerpass=&allowcopy=true&allowedit=true&allowprint=true&title=&author=&subject=&keywords=&conversiondelay=1&printtype=false&nobackground=false&outline=false&ref=form"
    
    try:
        pdfBuffer = io.BytesIO()
        dataBuffer = StringIO.StringIO()
        
        c = pycurl.Curl()
        c.setopt(c.URL, target_url)
        c.setopt(c.WRITEDATA, dataBuffer)
        c.setopt(c.FOLLOWLOCATION, True)        ## follow redirects
        c.perform()
    #         except Exception as err:
    #             logging.exception("Unexpected exception")
    #             return ""
        
        bodyOutput = dataBuffer.getvalue()    
        # print "page:", bodyOutput
        
        
        linkregex = re.compile('<a[^>]*href=[\'|"](.*?)[\'"].*?id="fileLinkIcon"[^>]*>')
        links = linkregex.findall( bodyOutput )
        if len(links) < 1:
            print "page:", bodyOutput
            print "unable to convert website, no PDF to download"
            sys.exit(1)
        
    #     print "links:", links
            
        c.setopt(c.URL, links[0])
        c.setopt(c.WRITEDATA, pdfBuffer)
        c.perform()
    
        return pdfBuffer.getvalue()
    finally:
        c.close()
        dataBuffer.close()
        pdfBuffer.close()
    

##
## detects automation
##
def pdfmyurl(sourceUrl):    
    c = pycurl.Curl()
    try:
        pdfBuffer = io.BytesIO()

        post_params = [
            ('url', sourceUrl)
        ]
        resp_data = urllib.urlencode(post_params)
        
        c.setopt(c.URL, "http://pdfmyurl.com/index.php")
        c.setopt(c.WRITEDATA, pdfBuffer)
        c.setopt(c.FOLLOWLOCATION, True)        ## follow redirects
        c.setopt(pycurl.POSTFIELDS, resp_data)
        c.setopt(pycurl.POST, 1)
        c.perform()
    #         except Exception as err:
    #             logging.exception("Unexpected exception")
    #             return ""
        
        return pdfBuffer.getvalue()

    finally:
        c.close()
        pdfBuffer.close()
 

pdfData = web2pdfconvert(source_link)
# pdfData = pdfmyurl(source_link)

if pdfData == None:
    print "Unable to get data"
else:
    with open(output_file, 'wb') as f:
        f.write( pdfData )
    print "PDF downloaded"
