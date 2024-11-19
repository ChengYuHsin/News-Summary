from utils.gmail import get_urls
from utils.parse import get_real_url, get_news
from utils.query import ask_gpt
from utils.send_file import send_gmail
import pandas as pd
import time
import re

# 定義函式以清理非法字符
def clean_illegal_characters(text):
    """
    清理非法字符（符合 openpyxl 限制的字符範圍），保留換行符。
    """
    if not isinstance(text, str):
        return text  # 如果不是字串，直接返回原值
    # 使用正則表達式移除非法字符（U+0000-U+0008 和 U+000B-U+000C 及 U+000E-U+001F）
    return re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", text)

# 讀取 prompt 文件
with open("prompt/新聞統整.md", "r", encoding="utf-8") as file:
    prompt = file.read()

# 獲取 URL 列表
urls = get_urls()
data = []

# 遍歷每個 URL，獲取新聞內容和標題
for url_dict in urls:
    url = url_dict.get('實際URL')
    
    if 'youtube' in url:
        continue
    
    print(f"正在處理 URL: {url}")  # 顯示當前處理的 URL
    news_info = get_news(url)
    
    # 添加標題和新聞內容到資料列表
    news_title = news_info.get('title', "無法獲取標題")
    news_content = news_info.get('content', "無法獲取內容")
    
    if news_content != "解析文章失敗":  # 排除失敗訊息
        data.append({'網址': url, '標題': news_title, '新聞': news_content})
    else:
        data.append({'網址': url, '標題': news_title, '新聞': news_content})

# 將資料轉換為 DataFrame
df = pd.DataFrame(data)

# 刪除重複的新聞內容，保留第一個出現的
df = df.drop_duplicates(subset='新聞', keep='first')

# 清理非法字符
df = df.applymap(clean_illegal_characters)

# 新增摘要列並加入延遲，防止 too many requests 錯誤
try:
    for index, row in df.iterrows():
        if row['新聞'] != "解析文章失敗":
            print(f"# 生成摘要: {row['網址']}")
            summary = ask_gpt(prompt, row['新聞'])
            df.loc[index, '摘要'] = summary
            time.sleep(5)
        else:
            df.loc[index, '摘要'] = "無法摘要"

except Exception as e:
    # 捕捉錯誤，儲存目前的資料至 Excel 並告知使用者
    file_path = "output/Google快訊-摘要(部分).xlsx"
    df.to_excel(file_path, index=False)
    send_gmail(subject="新聞摘要(部分)", body="因中途出錯，只產生部分Google快訊報告 Excel 檔案，請查收。", file_path=file_path)
    send_gmail(recipient_email="ryanchen0830b@gmail.com", subject="新聞摘要(部分)", body="因中途出錯，只產生部分Google快訊報告 Excel 檔案，請查收。", file_path=file_path)
    print(f"發生錯誤：{e}，已將部分資料儲存至 Google快訊-摘要(部分).xlsx")
else:
    # 如果無錯誤，儲存完整資料
    file_path = "output/Google快訊-摘要.xlsx"
    df.to_excel(file_path, index=False)
    send_gmail()
    send_gmail(recipient_email="ryanchen0830b@gmail.com")
    print("資料已成功儲存到 Google快訊-摘要.xlsx")
