# HTML Parser Speed Test: BeautifulSoup4, LXML and Selectolax

This evaluation compares the performance of popular HTML parser libraries in Python. The test involves extracting product names, ratings, prices, and monthly sales from a Shopee page. To simulate the handling of very large HTML files, the `duplicate_div_main` function duplicates the `<div id="main">` section 100 times, creating a significantly larger document.

# Results

Testing Environment:

- Hardware: M1 MacBook Pro with 8GB RAM
- Test case: Shopee product page parsing
- Package version:
  - beautifulsoup4==4.12.3
  - cssselect==1.2.0
  - lxml==5.3.0
  - selectolax==0.3.27

```none
Start resolving the original HTML...
Execution time of the original HTML (seconds):
--------------------------------------------------
selectolax     : 0.005336 (1.00x)
lxml           : 0.023221 (4.35x)
lxml_css       : 0.045544 (8.53x)
bs4            : 0.127979 (23.98x)

Start resolving the large HTML...
Execution time of the large HTML (seconds):
--------------------------------------------------
selectolax     : 1.160970 (1.00x)
lxml           : 2.236277 (1.93x)
lxml_css       : 4.248061 (3.66x)
bs4            : 71.444133 (61.54x)
```

# Conclusion

lxml demonstrates strong performance and is sufficient for most use cases.

Selectolax offers approximately 4 times the speed of lxml but comes with limitations. Its lack of XPath support is a significant drawback, and it struggles with certain CSS syntax, such as class names containing brackets or slashes, which are increasingly common on modern websites. These limitations may impact its usability in more complex scenarios.

> Note: [html5-parser](https://github.com/kovidgoyal/html5-parser) was excluded due to its limited popularity and maintenance status.
