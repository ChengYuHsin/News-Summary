import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os
import dotenv
dotenv.load_dotenv()

recipient_email = os.environ.get('GMAIL')
subject = "新聞摘要"
body = "這是自動產生的Google快訊報告 Excel 檔案，請查收。"
file_path = "output/Google快訊-摘要.xlsx"
sender_email = os.environ.get('GMAIL')
sender_password = os.environ.get('PASSWORD')

def send_gmail(recipient_email=recipient_email, subject=subject, body=body, file_path=file_path):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    # 建立郵件主體
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = subject

    # 加入郵件內容
    msg.attach(MIMEText(body, "plain"))

    # 加入 Excel 附件
    with open(file_path, "rb") as file:
        part = MIMEApplication(file.read(), Name="news_data.xlsx")
        part["Content-Disposition"] = f'attachment; filename="news_data.xlsx"'
        msg.attach(part)

    # 發送郵件
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # 啟用 TLS 加密
            server.login(sender_email, sender_password)  # 登入 Gmail 帳戶
            server.sendmail(sender_email, recipient_email, msg.as_string())  # 發送郵件
        print("Email 已成功發送!")
    except Exception as e:
        print(f"發送失敗，錯誤訊息：{e}")

# 使用範例
if __name__ == "__main__":
    send_gmail()
