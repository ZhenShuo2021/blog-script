# Pixiv 後處理腳本
[Powerful Pixiv Downloader](https://github.com/xuejianxianzun/PixivBatchDownloader) 下載後的檔案處理腳本。  
後處理 Powerful Pixiv Downloader 標籤，把依照作品分類的檔案再細分成各個角色，比如 `原神` 和 `崩鐵` 想分為兩個資料夾儲存，並且再依據 `人物` 進行分類，此外還附加了一些小功能。

## 功能
📁 分類：將指定作品（如 IM BA）根據角色分類到不同資料夾  
🔄 同步：上傳到 NAS  
🔍 搜尋：到 danbooru 搜尋遺失的作品  
📊 檢視：作品標籤比例  

## 使用方法
1. 安裝套件：`pip install -r requirements.txt`
2. 使用 Powerful Pixiv Downloader 下載完成
3. 修改 config.toml 後執行 `main.py`  

- config.toml
    1. BASE_PATHS: 本地下載資料夾以及遠端上傳資料夾位置
    2. categories: 分類，也就是你在 Pixiv Downloader 設定的標籤，比如我設定成 *BA,IM,原神,其他,海夢*  
    3. children: 如果作品有多個分支可以設定 children，會把 children 資料夾的檔案全部移動到相同資料夾
    4. tags: 設定標籤及其翻譯對應，進一步依照標籤分類檔案，如果標籤有多種別名可以全部綁定到同一個資料夾
    5. tag_delimiter: 設定第一個標籤和標籤之間的分隔符號，依照[命名規則](https://xuejianxianzun.github.io/PBDWiki/#/zh-tw/%E4%BE%BF%E6%8D%B7%E5%8A%9F%E8%83%BD?id=%e5%84%b2%e5%ad%98%e5%92%8c%e8%bc%89%e5%85%a5%e5%91%bd%e5%90%8d%e8%a6%8f%e5%89%87)設定

> [!CAUTION]  
> 下載資料夾中未指定的子資料夾不會處理，但是**檔案會全部被視為其他作品放進 others 資料夾**。

# 進階設定
- 分類：可以在 `categorizer.py` 修改 `CustomCategorizer` 和 `get_categorizer` 自訂分類方式。
- 同步：`_run_rsync` 中修改 rsync 參數，參數可參考[這裡](https://ysc.goalsoft.com.tw/blog-detail.php?target=back&no=49)。
- 搜尋：根據文件尋找 danbooru 是否有對應作品，並將結果輸出在 data/pixiv_retrieve.txt。    
- 檢視：檢視作品標籤比例，在 data 資料夾生成 tag_stats.jpg 和 tag_stats.txt，可以看你平常都看了啥。  

> [!NOTE]  
> 搜尋的使用方法：Powerful Pixiv Downloader 下載後不要關閉，右鍵檢查>右鍵class="beautify_scrollbar logContent">Copy>Copy outerHTML，把內容儲存為 `data/pixiv.html`
>  可以用 `gallery-dl -i pixiv_retrieve.txt` 一鍵下載遺失作品

# 架構
```
.
├── README.md
├── requirements.txt
├── config
│   └── config.toml
├── data
│   ├── pixiv.log              # 系統日誌
│   ├── pixiv.html             # 下載記錄，用於取回檔案
│   ├── pixiv_retrieve.txt     # 檔案取回結果
│   ├── rsync_log.log          # 同步日誌
│   ├── tag_stats.jpg          # 標籤統計圓餅圖
│   └── tag_stats.txt          # 標籤統計結果
├── src
│   ├── categorizer.py         # 檔案分類
│   ├── logger.py              # 日誌
│   ├── main.py                # 主程式
│   ├── retriever.py           # 搜尋遺失作品
│   ├── synchronizer.py        # 同步到遠端儲存裝置
│   └── viewer.py              # 標籤統計
└── utils
    ├── file_utils.py          # 檔案移動工具
    └── string_utils.py        # 字串檢查工具
```