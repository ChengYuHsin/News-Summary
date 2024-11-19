from urllib.parse import urlparse, parse_qs
import requests
from newspaper import Article
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
import time

# 常見的目標 URL 參數名稱
target_params = ['url', 'u', 'redirect', 'target', 'dest', 'destination', 'to', 'rurl', 'ru', 'q', 'link', 'fu', 'ffu']

# 模擬瀏覽器的 User-Agent
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
}

def get_real_url(url):
    print(f"\n# 解析實際網址：{url}")
    
    if 'mailto' in url:
        return None
     
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    
    # 嘗試找到真正的目標 URL
    for key in target_params:
        if key in query_params:
            real_url = query_params[key][0]
            return real_url
        
    if 'google' in url and 'alerts' in url:
        return None
            
    return url

def get_news(url):
    print(f"\n# 抓取新聞：{url}")
    try:
        # 優先使用 Article 解析
        article = Article(url)
        article.download()
        article.parse()
        
        # 如果解析內容和標題不為空，返回標題和內容
        if article.text.strip() and article.title.strip():
            return {'title': article.title, 'content': article.text}
        else:
            raise ValueError("Article 解析結果為空，嘗試使用 BeautifulSoup")
    except Exception as e:
        print(f"使用 Article 解析失敗，改用 BeautifulSoup")
        
        # 改用 BeautifulSoup 解析，並附加模擬的 headers
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            title = soup.title.string if soup.title else "無法獲取標題"
            paragraphs = soup.find_all(['p', 'article', 'div'])
            content = "\n".join([para.get_text() for para in paragraphs if para.get_text().strip() != ""])
            
            if content:
                return {'title': title, 'content': content}
            else:
                print("BeautifulSoup 無法解析，改用 Selenium")
                return get_news_via_selenium(url)
        except Exception as e:
            print(f"使用 BeautifulSoup 解析失敗，改用 Selenium")
            return get_news_via_selenium(url)

def get_news_via_selenium(url):
    try:
        # 設定 Firefox driver
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        
        driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)
        driver.get(url)
        time.sleep(3)  # 等待頁面加載
        
        # 使用 BeautifulSoup 解析內容
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        title = soup.title.string if soup.title else "無法獲取標題"
        paragraphs = soup.find_all(['p', 'article', 'div'])
        content = "\n".join([para.get_text() for para in paragraphs if para.get_text().strip() != ""])
        
        driver.quit()
        
        return {'title': title, 'content': content} if content else {'title': title, 'content': "無法解析此網站的內容。"}
    except Exception as e:
        print(f"Selenium 解析失敗")
        return {'title': "無法獲取標題", 'content': "解析文章失敗"}
