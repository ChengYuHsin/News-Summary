import pandas as pd
import tiktoken

# 載入資料
df = pd.read_excel('output/news_data.xlsx')  # 從 Excel 檔案中讀取資料
tokenizer = tiktoken.encoding_for_model("gpt-4o-mini")  # 初始化 Tokenizer，根據 GPT-4o-mini 模型

# 定義計算 Token 數的函式
def count_tokens(text):
    """
    計算輸入文本的 Token 數。

    參數:
    - text: str，待處理的文本

    返回:
    - Token 數 (int)
    """
    if pd.isna(text):  # 處理 NaN 值，返回 0
        return 0
    return len(tokenizer.encode(text))  # 使用 Tokenizer 編碼並計算 Token 數

# 定義計算平均 Token 數的函式
def average_tokens(df, prompt_path="prompt/新聞統整.md"):
    """
    計算 "新聞" 和 "摘要" 欄位的平均 Token 數，並讀取 Prompt 的 Token 數。

    參數:
    - df: DataFrame，包含 "新聞" 和 "摘要" 欄位的數據
    - prompt_path: str，Prompt 檔案的路徑

    返回:
    - news_avg_token: 新聞的平均 Token 數
    - summary_avg_token: 摘要的平均 Token 數
    - prompt_token: Prompt 的 Token 數
    """
    # 計算每條 "新聞" 和 "摘要" 的 Token 數
    df['新聞_Token數'] = df['新聞'].apply(count_tokens)
    df['摘要_Token數'] = df['摘要'].apply(count_tokens)

    # 計算平均 Token 數
    news_avg_token = df['新聞_Token數'].mean()
    summary_avg_token = df['摘要_Token數'].mean()

    # 讀取 Prompt 檔案內容並計算其 Token 數
    with open(prompt_path, "r", encoding="utf-8") as file:
        prompt = file.read()  # 讀取 Prompt 檔案內容
    prompt_token = count_tokens(prompt)  # 計算 Prompt 的 Token 數

    return news_avg_token, summary_avg_token, prompt_token

# 定義計算成本的函式
def calculate_cost(n, input_cost_per_million=0.15, output_cost_per_million=0.60):
    """
    根據處理的新聞數量計算總成本（以 TWD 為單位）。

    參數:
    - n: int，處理的新聞數量
    - input_cost_per_million: float，每百萬輸入 Token 的成本 (默認為 $0.15)
    - output_cost_per_million: float，每百萬輸出 Token 的成本 (默認為 $0.60)

    返回:
    - total_cost_twd: float，總成本（以新台幣計算）
    """
    # 計算平均 Token 數，包括新聞、摘要和 Prompt
    news_avg_token, summary_avg_token, prompt_token = average_tokens(df)

    # 每次請求的輸入 Token 數（新聞 Token 數 + Prompt Token 數）
    input_tokens_per_request = news_avg_token + prompt_token
    # 每次請求的輸出 Token 數（摘要 Token 數）
    output_tokens_per_request = summary_avg_token

    # 打印 Token 計算結果
    print("input_tokens_per_request:", input_tokens_per_request)
    print("output_tokens_per_request:", output_tokens_per_request)

    # 計算總輸入和輸出 Token 數
    total_input_tokens = n * input_tokens_per_request  # 總輸入 Token 數
    total_output_tokens = n * output_tokens_per_request  # 總輸出 Token 數

    # 計算輸入和輸出成本
    input_cost = total_input_tokens * (input_cost_per_million / 1_000_000)  # 輸入成本
    output_cost = total_output_tokens * (output_cost_per_million / 1_000_000)  # 輸出成本

    # 計算總成本（以美元為單位）
    total_cost = input_cost + output_cost

    # 將總成本轉換為新台幣（假設匯率為 1 美元 = 30 新台幣）
    total_cost_twd = total_cost * 30

    return total_cost_twd

# 主程式
if __name__ == '__main__':
    total_cost = calculate_cost(3600)  # 設定處理 3600 條新聞
    print(f"Total cost: {total_cost:.2f} TWD")  # 打印總成本（以 TWD 為單位）
