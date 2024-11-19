# Pricing.py 說明

### **程式設計目的**
這個程式的目的是根據提供的新聞與摘要資料，計算使用 GPT 模型（GPT-4o-mini）處理這些資料的成本。成本計算基於模型的輸入和輸出 Token 數，並根據處理的新聞數量 \( n \) 和定價模型來得出結果。

### **程式功能概述**
1. 計算每條新聞和摘要的 **Token 數**。
2. 計算整個資料的 **新聞和摘要平均 Token 數**。
3. 考慮額外的 Prompt Token 數（例如，設定的提示詞檔案）。
4. 根據新聞數量 \( n \)，計算總輸入和輸出的 Token 數。
5. 基於 GPT-4o-mini 的定價計算輸入和輸出的總成本。
6. 將總成本從美元轉換為新台幣，並輸出結果。

---

### **程式主要部分詳解**

#### **1. 載入資料**
```python
df = pd.read_excel('output/news_data.xlsx')
```
- 從 `news_data.xlsx` 中載入新聞與摘要資料。
- 資料的格式假設包含兩個欄位：`新聞` 和 `摘要`。

---

#### **2. 初始化 GPT 模型的 Tokenizer**
```python
tokenizer = tiktoken.encoding_for_model("gpt-4o-mini")
```
- 初始化專屬 GPT-4o-mini 模型的分詞工具（Tokenizer）。
- 該工具負責將文字轉換為 Token，這些 Token 是計算成本的基礎。

---

#### **3. 計算 Token 數**
```python
def count_tokens(text):
    if pd.isna(text):
        return 0
    return len(tokenizer.encode(text))
```
- **功能**：計算輸入文字的 Token 數，處理缺失值（NaN）並返回 `0`。
- **應用場景**：可對每條新聞、摘要和 Prompt 計算其 Token 數。

---

#### **4. 計算平均 Token 數**
```python
def average_tokens(df, prompt_path="prompt/新聞統整.md"):
```
- **功能**：計算以下內容的平均 Token 數：
  - **新聞的平均 Token 數**。
  - **摘要的平均 Token 數**。
  - **Prompt 的 Token 數**（從指定檔案中讀取）。
- **內部邏輯**：
  1. 遍歷 DataFrame 的 `新聞` 和 `摘要` 欄位，計算每列的 Token 數。
  2. 計算這些 Token 數的平均值。
  3. 從 `prompt_path` 路徑讀取 Prompt 檔案內容，計算其 Token 數。
- **返回值**：
  - `news_avg_token`: 新聞的平均 Token 數。
  - `summary_avg_token`: 摘要的平均 Token 數。
  - `prompt_token`: Prompt 的 Token 數。

---

#### **5. 計算總成本**
```python
def calculate_cost(n, input_cost_per_million=0.15, output_cost_per_million=0.60):
```
- **功能**：根據新聞數量 \( n \) 和模型定價計算處理成本。
- **步驟**：
  1. 呼叫 `average_tokens`，獲取新聞、摘要的平均 Token 數，以及 Prompt 的 Token 數。
  2. 計算每次請求的輸入和輸出 Token 數：
     - 輸入 Token 數 = 新聞平均 Token 數 + Prompt Token 數。
     - 輸出 Token 數 = 摘要平均 Token 數。
  3. 計算總輸入和輸出 Token 數：
     - 總輸入 Token 數 = \( n \times \text{輸入 Token 數} \)。
     - 總輸出 Token 數 = \( n \times \text{輸出 Token 數} \)。
  4. 根據定價公式計算成本：
     - 輸入成本 = 總輸入 Token 數 × 每百萬 Token 成本。
     - 輸出成本 = 總輸出 Token 數 × 每百萬 Token 成本。
     - 總成本 = 輸入成本 + 輸出成本。
  5. 將美元成本轉換為新台幣（假設匯率為 1 美元 = 30 新台幣）。

---

#### **6. 主程式**
```python
if __name__ == '__main__':
    total_cost = calculate_cost(3600)
    print(f"Total cost: {total_cost:.2f} TWD")
```
- **功能**：執行主程式並打印處理 3600 條新聞的總成本。
- **邏輯**：
  1. 呼叫 `calculate_cost`，設定新聞數量 \( n = 3600 \)。
  2. 打印總成本，保留小數點後兩位。

---

### **執行流程**
1. **資料讀取**：
   - 從 `news_data.xlsx` 載入新聞與摘要資料。
2. **平均 Token 計算**：
   - 計算新聞和摘要的平均 Token 數。
   - 計算 Prompt 的 Token 數。
3. **成本計算**：
   - 根據新聞數量 \( n \) 計算總輸入和輸出 Token 數。
   - 根據定價模型計算輸入和輸出的總成本。
   - 將美元成本轉換為新台幣。
4. **輸出結果**：
   - 打印處理 3600 條新聞的總成本。
