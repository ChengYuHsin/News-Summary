from openai import OpenAI
import os
import time
import dotenv

# 加載環境變量
dotenv.load_dotenv()

def query(prompt, message, model):
    # 設置 API 金鑰
    client = OpenAI()
    client.api_key = os.getenv("OPENAI_API_KEY")
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": message}
        ],
        temperature=0.2,
    )
    
    return response.choices[0].message.content.strip()

def ask_gpt(prompt, message, model='gpt-4o-mini'):
    retries = 3
    wait_times = [20, 40, 60]  # 等待時間列表（秒）
    
    for attempt in range(retries):
        try:
            answer = query(prompt, message, model)
            return answer
        except Exception as e:
            if attempt < retries - 1:
                wait_time = wait_times[attempt]
                print(f"請求失敗，正在等待 {wait_time} 秒後重試...（第 {attempt + 1} 次重試）")
                time.sleep(wait_time)
            else:
                print("所有重試均失敗，返回空字符串。")
                return ""

# 範例使用
if __name__ == "__main__":
    prompt = "你是一個幫助用戶的助手，用繁體中文回答。"
    message = "你好。" * 200
    
    for i in range(20):
        answer = ask_gpt(prompt, message)
        print(answer)
