# get url title to produce the bookmark html file

import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# 讀取 HTML 書籤文件
with open('bookmarks.html', 'r', encoding='utf-8') as file:
    soup = BeautifulSoup(file, 'lxml')

# 找到所有的 <a> 標籤
links = soup.find_all('a')

# 正則表達式，匹配 "of" 之後的第一個單詞
artist_name_pattern = re.compile(r'of (\w+)')

# 遍歷所有的 <a> 標籤並更新標題
for link in links:
    url = link.get('href')
    if url:
        try:
            # 發送請求以獲取網頁內容
            response = requests.get(url)
            page_soup = BeautifulSoup(response.content, 'lxml')
            title = page_soup.title.string.strip() if page_soup.title else urlparse(url).netloc

            # 提取 artist name
            match = artist_name_pattern.search(title)
            if match:
                artist_name = match.group(1)
                link.string = artist_name
                print(f"Updated: {url} with artist name: {artist_name}")
            else:
                print(f"No artist name found for: {url}")

        except Exception as e:
            print(f"Error fetching {url}: {e}")

# 將更新的 HTML 寫回文件
with open('updated_bookmarks.html', 'w', encoding='utf-8') as file:
    file.write(str(soup))

print("Bookmarks updated successfully.")
