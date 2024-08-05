
# Pixiv 後處理腳本
[Powerful Pixiv Downloader](https://github.com/xuejianxianzun/PixivBatchDownloader) 下載後的檔案處理腳本。

## 解決了什麼問題
Powerful Pixiv Downloader 有標籤分類功能，把依照作品分類的檔案再細分成各個角色，還附加了一些小功能。

## 功能
1. 將指定作品（如 IM BA）根據角色分類到不同資料夾，其餘作品依照作者名稱分類資料夾。
2. 上傳到 NAS。
3. 到 danbooru 搜尋遺失的作品。
4. 檢視作品標籤比例

## 使用方法
使用 Pixiv Downloader 下載完成後直接執行 main  
下載資料夾中的原有的子資料夾不會處理，但是檔案會全部被視為其他作品放進 others 資料夾。

### conf.py
1. BASE_PATHS: 設定本地下載資料夾以及遠端上傳資料夾位置
2. CATEGORIES: 設定大分類，比如我設定成 *BA,IM,原神,其他,海夢* ，也就是你在 Pixiv Downloader 設定的標籤  
3. idolmaster_path_child: 指定的資料夾名稱會被移動到 IM 資料夾進行處理  
4. bluearchive_tags/idolmaster_tags: 設定角色資料夾及其翻譯對應，左邊標籤右邊資料夾名稱（翻譯），如果角色有多種標籤可以全部綁定到同一個資料夾中

### 分類
`idolmaster_path`和`other_path`不必手動新增：
- 程式會查詢`idolmaster_path_child`關鍵字並且將對應資料夾放進`idolmaster_path`
- 沒歸類的資料夾會放進`other_path`，再以作者名稱分類。

### 同步
不需要同步檔案 ➡️ 刪除 `sync_folders`  
不需要 log ➡️ 刪除 main 的 `merge_log` 以及 post_process 的 `f'--log-file={log_name}',`   

避免檔案傳輸意外，gen 資料夾生成了 rsync log。  
如要調整rsync參數，可參考[這裡](https://ysc.goalsoft.com.tw/blog-detail.php?target=back&no=49)。

### 搜尋遺失的作品🍺
此腳本根據你複製的文件尋找danbooru是否有對應檔案，並將結果輸出在 gen/pixiv_retrieve.txt。    
下載頁面不要關閉，右鍵檢查>右鍵class="beautify_scrollbar logContent">Copy>Copy outerHTML，把內容保存為 gen/pixiv.html

### 檢視作品標籤比例
在 gen 資料夾生成 tag_stats.jpg 和 tag_stats.txt，可以看你平常都看了啥。  
可能需要修改 `extract_tags` 函式以符合你的命名規則。  
不需要同步則需把 main 的 `BASE_PATHS["remote"]` 改成 local 才會在本地資料夾搜尋

### 個別檔案功能  
只要個別功能直接把 main 中不要的註解掉比較快，但每個檔案也可以獨立運行

**post_process**  
檔案處理腳本，包含分類上傳以及合併log。搜尋 split 可修改自己的分界符號 (delimiter)

**retrieve_artwork**  
使用方法如上述，可以用 `gallery-dl -i pixiv_retrieve.txt` 一鍵下載。找不到的會加上井字註解，可以在其他平台手動搜尋

**tag_stats**
依據檔案名稱統計標籤，解析標籤方式在`extract_tags`定義，依照我的[命名規則](https://xuejianxianzun.github.io/PBDWiki/#/zh-tw/%E4%BE%BF%E6%8D%B7%E5%8A%9F%E8%83%BD?id=%e5%84%b2%e5%ad%98%e5%92%8c%e8%bc%89%e5%85%a5%e5%91%bd%e5%90%8d%e8%a6%8f%e5%89%87)完成 `{user}_{id}_{}_{tags_transl_only}`