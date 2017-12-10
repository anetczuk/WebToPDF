## WebToPDF
Convert any webpage to PDF in two steps:
1. extract all desired links to file by calling *src/linkextractor.py*
2. call *src/convert.sh* on the links list

Features:
* crawling depthness,
* handle multiple webpages at once,
* join files by cropping unnecessary white space at end of each *last* page,
* support for JavaScript. 


### Link extractor
Link extractor is simple web crawler consists of Python scripts. It uses *curl* as backend to navigate through web pages. Links extraction is simply done by calling regular expression detecting *a* HTML tag.


### Converter
Converter uses Linux tools for converting HTML to PDF. It covnerts every link separately, then cropps each file and finally merges all PDFs to final file.
