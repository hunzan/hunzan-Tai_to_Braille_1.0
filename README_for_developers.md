# 🧑‍💻 開發者版本（README_for_developers.md）

這份說明是給程式開發者、教育工作者或想改作本工具的夥伴。

## 台羅轉台語點字工具  
**TaiLo Braille Converter**  
開發者：Lîm Akâu（林阿猴）、KimTsio（金蕉）

---

## 🔍 計畫簡介

這是一個輔助視障者學習台語拼音（台羅）與六點式點字對應的工具，支援點字即時轉換，可搭配 NVDA 螢幕報讀器使用。

---

## 💡 功能特點

- 不用數字調號標示聲調，直接台語台羅拼音輸入使用。
- 建議搭配電腦台語輸入法「信望愛台／客語輸入法」，直接輸入台羅拼音，更好用！  
  👉 下載：「[信望愛台／客語輸入法](https://taigi.fhl.net/TaigiIME/)」
- 將輸入的台羅拼音（無連字符）即時轉換為台語點字。
- 兩種介面版本：
  - tkinter（適合純視覺使用者）
  - wxPython（支援 NVDA 語音報讀）
- 字體大小可調整（限 wx 版）
- 對應表資料（音節 → 點字）以 JSON 格式整理，便於維護與擴充

---

## 🖥️ 可執行版本

在 GitHub Release 提供以下兩種版本（`.exe`）供下載使用：

### `tai_braille_Tk.exe`
- 使用 tkinter 介面
- **不支援 NVDA**
- 適合一般使用者、電腦具備放大輔助功能的低視力使用者

### `tai_braille_wx.exe`
- 使用 wxPython 介面
- **支援 NVDA 讀取**
- 適合一般使用者、電腦具備放大輔助功能的低視力使用者

---

## 📁 專案結構

TaiBraille/
├── app_wx.py # wxPython 版本主程式（支援 NVDA）
├── app_Tk.py # tkinter 版本主程式
├── DoulosSIL-Regular.ttf # 點字顯示字型
├── taivi.ico # 執行檔圖示
└── braille_data/ # 點字對應表資料夾
├── consonants.json
├── vowels_all.json
├── rushio_syllables.json
└── nasal_table.json


---

## ⚙️ 執行方式（開發者）

1. 確保已安裝 Python 3.10+
2. 安裝所需套件（如 `wxPython`、`tkinter`、`pyinstaller`）
3. 執行：

```bash
python app_Tk.py
# 或
python app_wx.py

pyinstaller --onefile --noconsole --icon=taivi.ico app_wx.py

🤝 合作與貢獻
歡迎任何對以下領域有興趣的夥伴加入協作：

台語拼音規則與點字對應優化

語音輸入／TTS 播報功能

網頁版／跨平台版本開發

使用者測試與回饋

📬 請來信聯絡我們，共同讓這份資源走得更遠。

📄 授權條款
免費供個人與教育用途使用

可做研究與非營利修改，請註明出處

禁止任何形式的商業使用

禁止未經授權的改作散布或販售

本專案雖參考開源精神，但基於社群保護原則，不採標準授權（MIT/GPL）

📬 聯絡資訊
林阿猴（Lîm Akâu）：定向行動訓練師、台語文推廣者

金蕉（KimTsio）：語言科技協作者

GitHub Repo：https://github.com/hunzan/hunzan-Tai_to_Braille_1.0