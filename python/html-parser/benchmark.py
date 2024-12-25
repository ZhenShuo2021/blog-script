import time
import statistics

from bs4 import BeautifulSoup
from lxml import html
from selectolax.parser import HTMLParser


def read_html_file(filename):
    with open(filename, encoding="utf-8") as f:
        return f.read()


def parse_with_selectolax(html_content):
    tree = HTMLParser(html_content)
    products = []

    for item in tree.css("div.p-2.flex-1.flex"):
        product = {}

        name_elem = item.css_first("div.line-clamp-2")
        if name_elem:
            product["name"] = name_elem.text().strip()

        rating_elem = item.css_first("div.text-shopee-black87")
        if rating_elem and rating_elem.text().strip():
            product["rating"] = rating_elem.text().strip()

        price_elem = item.css_first(".font-medium")
        if price_elem:
            product["price"] = price_elem.text().strip()

        sales_elem = item.css_first("div.truncate.text-shopee-black87.text-xs.min-h-4")
        if sales_elem:
            product["monthly_sales"] = sales_elem.text().replace("月銷量", "").strip()

        if product:
            products.append(product)

    return products


def parse_with_lxml(html_content):
    tree = html.fromstring(html_content)
    products = []

    for item in tree.xpath('//div[@class="p-2 flex-1 flex flex-col justify-between"]'):
        product = {}

        name = item.xpath('.//div[@class="line-clamp-2 break-words min-h-[2.5rem] text-sm"]/text()')
        if name:
            product["name"] = name[0].strip()

        rating = item.xpath('.//div[@class="text-shopee-black87 text-xs/sp14 flex-none"]/text()')
        if rating:
            product["rating"] = rating[0].strip()

        price = item.xpath('.//span[@class="font-medium text-base/5 truncate"]/text()')
        if price:
            product["price"] = price[0].strip()

        sales = item.xpath('.//div[@class="truncate text-shopee-black87 text-xs min-h-4"]/text()')
        if sales:
            product["monthly_sales"] = sales[0].replace("月銷量", "").strip()

        if product:
            products.append(product)

    return products


def parse_with_lxml_css(html_content):
    tree = html.fromstring(html_content)
    products = []

    for item in tree.cssselect("div.p-2.flex-1.flex.flex-col.justify-between"):
        product = {}

        name = item.cssselect(r"div.line-clamp-2.break-words.min-h-\[2\.5rem\].text-sm")
        if name:
            product["name"] = name[0].text_content().strip()

        rating = item.cssselect(r"div.text-shopee-black87.text-xs\/sp14.flex-none")
        if rating:
            product["rating"] = rating[0].text_content().strip()

        price = item.cssselect(r"span.font-medium.text-base\/5.truncate")
        if price:
            product["price"] = price[0].text_content().strip()

        sales = item.cssselect("div.truncate.text-shopee-black87.text-xs.min-h-4")
        if sales:
            product["monthly_sales"] = sales[0].text_content().replace("月銷量", "").strip()

        if product:
            products.append(product)

    return products


def parse_with_bs4(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    products = []

    for item in soup.select("div.p-2.flex-1.flex"):
        product = {}

        name_elem = item.select_one("div.line-clamp-2")
        if name_elem:
            product["name"] = name_elem.text.strip()

        rating_elem = item.select_one(r"div.text-shopee-black87.text-xs\/sp14.flex-none")
        if rating_elem and rating_elem.text.strip():
            product["rating"] = rating_elem.text.strip()

        price_elem = item.select_one(r"span.text-base\/5.truncate")
        if price_elem:
            product["price"] = price_elem.text.strip()

        sales_elem = item.select_one("div.truncate.text-shopee-black87.text-xs")
        if sales_elem:
            product["monthly_sales"] = sales_elem.text.replace("月銷量", "").strip()

        if product:
            products.append(product)

    return products


def run_performance_test(html_content, iterations=20):
    results = {"selectolax": [], "lxml": [], "lxml_css": [], "bs4": []}

    # 測試 selectolax
    for _ in range(iterations):
        start_time = time.time()
        parse_with_selectolax(html_content)
        results["selectolax"].append(time.time() - start_time)

    # 測試 lxml
    for _ in range(iterations):
        start_time = time.time()
        parse_with_lxml(html_content)
        results["lxml"].append(time.time() - start_time)

    # 測試 lxml_css
    for _ in range(iterations):
        start_time = time.time()
        parse_with_lxml_css(html_content)
        results["lxml_css"].append(time.time() - start_time)

    # 測試 BeautifulSoup4
    for _ in range(iterations):
        start_time = time.time()
        parse_with_bs4(html_content)
        results["bs4"].append(time.time() - start_time)

    return {lib: statistics.mean(times) for lib, times in results.items()}


if __name__ == "__main__":
    html_content = read_html_file("example.html")
    results = run_performance_test(html_content, 100)

    # 輸出結果
    print("\n效能測試結果 (平均執行時間，單位：秒):")
    print("-" * 50)

    selectolax_time = results["selectolax"]
    for parser, avg_time in results.items():
        ratio = avg_time / selectolax_time
        print(f"{parser:15}: {avg_time:.6f} ({ratio:.2f}x)")

    # 驗證結果
    print("\n解析結果:")
    print("-" * 50)

    print("\nSelectolax 結果:")
    selectolax_results = parse_with_selectolax(html_content)
    print(selectolax_results[0] if selectolax_results else "No results")

    print("\nLXML 結果:")
    lxml_results = parse_with_lxml(html_content)
    print(lxml_results[0] if lxml_results else "No results")

    print("\nLXML_CSS 結果:")
    lxml_results = parse_with_lxml_css(html_content)
    print(lxml_results[0] if lxml_results else "No results")

    print("\nBeautifulSoup4 結果:")
    bs4_results = parse_with_bs4(html_content)
    print(bs4_results[0] if bs4_results else "No results")
