import imapclient
import mailparser
from bs4 import BeautifulSoup
import os
import dotenv
import pandas as pd
from datetime import datetime, timedelta
from utils.parse import get_real_url
import logging

dotenv.load_dotenv()

USER = os.environ.get('GMAIL')
PASSWORD = os.environ.get('PASSWORD')

logger = logging.getLogger(__name__)

def get_urls(subjects=["Google 快訊", "Google Alert"], start_date=datetime.now()-timedelta(days=0), end_date=datetime.now() + timedelta(days=1)):
    start_date_str = start_date.strftime('%Y/%m/%d')
    end_date_str = end_date.strftime('%Y/%m/%d')
    search_query = f'({" OR ".join([f"subject:\"{subject}\"" for subject in subjects])}) after:{start_date_str} before:{end_date_str}'
    logger.info(f"Gmail搜尋條件：{search_query}")

    url_list = []
    unique_urls = set()  # 用於儲存唯一的 real_url
    client = imapclient.IMAPClient('imap.gmail.com', ssl=True)
    client.login(USER, PASSWORD)
    select_info = client.select_folder('INBOX', readonly=True)
    UIDs = client.gmail_search(search_query)
    logger.info(f"搜尋完成，找到 {len(UIDs)} 封郵件。")

    for uid in UIDs:
        raw_message = client.fetch([uid], ['BODY.PEEK[]', 'RFC822.SIZE'])
        parsed_mail = mailparser.parse_from_bytes(raw_message[uid][b'BODY[]'])

        if parsed_mail.text_html:
            html_content = parsed_mail.text_html[0]
            soup = BeautifulSoup(html_content, 'html.parser')
            links = soup.find_all('a', href=True)
            hrefs = [link['href'] for link in links]
            hrefs = list(set(hrefs))

            if hrefs:
                logger.info(f"# 處理郵件 UID {uid} ")
                for href in hrefs:
                    real_url = get_real_url(href)
                    if real_url and real_url not in unique_urls:
                        unique_urls.add(real_url)
                        url_list.append({
                            '原始URL': href,
                            '實際URL': real_url
                        })
            else:
                logger.info("郵件中沒有找到任何網頁連結。")
        else:
            logger.info("郵件中沒有 HTML 內容。")

    client.logout()
    return url_list

if __name__ == "__main__":
    start_date = datetime(2024, 11, 1)  # 範例開始日期
    end_date = datetime(2024, 11, 3)    # 範例結束日期
    
    url_list = get_urls(start_date=start_date, end_date=end_date)
    df = pd.DataFrame(url_list)
    
    if not df.empty:
        logger.info("獲取的 URL 列表：\n%s", df.to_string())
