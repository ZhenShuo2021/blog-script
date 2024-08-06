# Pixiv 後處理腳本
[Powerful Pixiv Downloader](https://github.com/xuejianxianzun/PixivBatchDownloader) 下載後的檔案處理腳本。  
解決 Powerful Pixiv Downloader 有標籤分類功能，把依照作品分類的檔案再細分成各個角色，還附加了一些小功能。

## 功能
📁 分類：將指定作品（如 IM BA）根據角色分類到不同資料夾  
🔄 同步：上傳到 NAS  
🔍 搜尋：到 danbooru 搜尋遺失的作品  
📊 檢視：作品標籤比例  

## 使用方法
1. 安裝套件：`pip install -r requirements.txt`，
2. 使用 Pixiv Downloader 下載完成後直接執行 main  

> [!CAUTION]  
> 下載資料夾中未指定的子資料夾不會處理，但是**檔案會全部被視為其他作品放進 others 資料夾**。

# 設定說明
照重要程度依序說明各個功能如何設定，最重要的是 conf.py。

### conf.py
1. BASE_PATHS: 設定本地下載資料夾以及遠端上傳資料夾位置
2. CATEGORIES: 設定大分類，也就是你在 Pixiv Downloader 設定的標籤，比如我設定成 *BA,IM,原神,其他,海夢*  
3. idolmaster_path_child: 指定的資料夾名稱會被移動到 IM 資料夾處理  
4. bluearchive_tags/idolmaster_tags: 設定角色資料夾及其翻譯對應，左邊標籤右邊資料夾名稱（翻譯），如果角色有多種標籤可以全部綁定到同一個資料夾中

### 分類
不需任何額外手動操作：
- 程式會查詢`idolmaster_path_child`關鍵字並且將對應資料夾放進`idolmaster_path`
- 沒歸類的資料夾會放進`other_path`，再依據作者名稱分類

> 預設標簽分隔符號","，可以把 `file_name.split(",")` 改成你的分隔符號

### 同步
不需要同步檔案 ➡️ 刪除 `sync_folders`  
不需要 log ➡️ 刪除 main 的 `merge_log` 以及 post_process 的 `f'--log-file={log_name}',`   

> rsync 日誌放在 gen 資料夾。如要調整rsync參數可參考[這裡](https://ysc.goalsoft.com.tw/blog-detail.php?target=back&no=49)。

### 搜尋遺失的作品🍺
根據你複製的文件尋找 danbooru 是否有對應檔案，並將結果輸出在 gen/pixiv_retrieve.txt。    
下載頁面不要關閉，右鍵檢查>右鍵class="beautify_scrollbar logContent">Copy>Copy outerHTML，把內容保存為 gen/pixiv.html

> 可以用 `gallery-dl -i pixiv_retrieve.txt` 一鍵下載遺失作品

### 檢視作品標籤比例
在 gen 資料夾生成 tag_stats.jpg 和 tag_stats.txt，可以看你平常都看了啥。  
修改 main 的 `process_files` 路徑以符合你的歸檔路徑。  

> 可能需要修改 `extract_tags` 函式以符合你的命名規則。  

# 個別檔案功能  
只要個別功能直接把 main 中不要的註解掉比較快，但每個檔案也可以獨立運行

> post_process: 檔案處理腳本，包含分類上傳以及合併log。搜尋 split 可修改自己的分界符號 (delimiter)  
> retrieve_artwork: 目前只找到 danbooru 支援 pixiv id 搜尋。找不到的可以在其他平台手動搜尋  
> tag_stats: 依據檔案名稱統計標籤，解析標籤方式在`extract_tags`定義，依照我的[命名規則](https://xuejianxianzun.github.io/PBDWiki/#/zh-tw/%E4%BE%BF%E6%8D%B7%E5%8A%9F%E8%83%BD?id=%e5%84%b2%e5%ad%98%e5%92%8c%e8%bc%89%e5%85%a5%e5%91%bd%e5%90%8d%e8%a6%8f%e5%89%87)完成 `{user}_{id}_{}_{tags_transl_only}`  