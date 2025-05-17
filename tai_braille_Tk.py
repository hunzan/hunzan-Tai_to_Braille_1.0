import sys
import os
import json
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

def resource_path(relative_path):
    """取得資源檔的絕對路徑，兼容 PyInstaller 打包後的環境"""
    try:
        base_path = sys._MEIPASS  # PyInstaller 打包時臨時資料夾
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# 下面就用 resource_path 取得字型、json 檔的路徑
font_path = resource_path("DoulosSIL-Regular.ttf")
json_path = resource_path(os.path.join("braille_data", "consonants.json"))

# 資料夾與檔案路徑
DATA_DIR = os.path.join(os.path.dirname(__file__), 'braille_data')
CONSONANTS_FILE = os.path.join(DATA_DIR, 'consonants.json')
VOWELS_FILE = os.path.join(DATA_DIR, 'vowels_all.json')
RUSHIO_FILE = os.path.join(DATA_DIR, 'rushio_syllables.json')
NASAL_FILE = os.path.join(DATA_DIR, 'nasal_table.json')

# 載入 JSON 資料
def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

consonants = load_json(CONSONANTS_FILE)
vowels = load_json(VOWELS_FILE)
rushio = load_json(RUSHIO_FILE)
nasal = load_json(NASAL_FILE)

# 切音節
def split_syllables(word):
    result = []
    i = 0
    while i < len(word):
        match = None
        for c in sorted(consonants.keys(), key=lambda x: -len(x)):
            if word[i:].startswith(c):
                for v in sorted(vowels.keys(), key=lambda x: -len(x)):
                    if word[i+len(c):].startswith(v):
                        match = c + v
                        break
                for r in sorted(rushio.keys(), key=lambda x: -len(x)):
                    if word[i+len(c):].startswith(r):
                        match = c + r
                        break
                for n in sorted(nasal.keys(), key=lambda x: -len(x)):
                    if word[i+len(c):].startswith(n):
                        match = c + n
                        break
                if match:
                    result.append(match)
                    i += len(match)
                    break

        # ✅ 處理純 rushio 音節（無聲母）
        if not match:
            for r in sorted(rushio.keys(), key=lambda x: -len(x)):
                if word[i:].startswith(r):
                    result.append(r)
                    i += len(r)
                    match = True
                    break

        if not match:
            for v in sorted(vowels.keys(), key=lambda x: -len(x)):
                if word[i:].startswith(v):
                    result.append(v)
                    i += len(v)
                    match = True
                    break

        if not match:
            for n in sorted(nasal.keys(), key=lambda x: -len(x)):
                if word[i:].startswith(n):
                    result.append(n)
                    i += len(n)
                    match = True
                    break

        if not match:
            result.append('[錯誤]')
            break

    return result

# 單音節轉點字
def convert_syllable(s):
    if s in nasal:
        return "⠠" + nasal[s]["dots"]

    for c in sorted(consonants.keys(), key=lambda x: -len(x)):
        if s.startswith(c):
            rest = s[len(c):]
            if rest in vowels:
                return consonants[c]["dots"] + vowels[rest]["dots"]
            elif rest in rushio:
                return consonants[c]["dots"] + rushio[rest]["dots"]
            elif rest in nasal:
                return "⠠" + consonants[c]["dots"] + nasal[rest]["dots"]

    if s in rushio:
        return rushio[s]["dots"]  # ✅ 讓 rushio_syllables 可以單獨轉譯

    if s in vowels:
        return vowels[s]["dots"]

    return '[錯誤]'

# 主要轉換函式
def tl_to_braille(text):
    lines = text.strip().split('\n')
    result_lines = []

    for line in lines:
        words = line.strip().split(' ')
        result_words = []

        for word in words:
            # 將單詞中可能存在的連字符分開處理，但不加入點字
            word_clean = word.replace("-", "")  # 移除連字符後處理

            if word_clean in nasal:
                braille = "⠠" + nasal[word_clean]["dots"]
                result_words.append(braille)
            else:
                syllables = split_syllables(word_clean)
                braille = ''.join(convert_syllable(s) for s in syllables)
                result_words.append(braille)

        result_lines.append(' '.join(result_words))  # 每個詞之間空格

    return '\n'.join(result_lines)

# GUI 設計
def create_gui():
    window = tk.Tk()
    icon_path = os.path.join(os.path.dirname(__file__), "taivi.ico")
    if os.path.exists(icon_path):
        window.title("台羅拼音轉台語點字")
        window.geometry("700x600")
        window.iconbitmap(icon_path)
        window.configure(bg="#FFFFE0")
    else:
        print(f"⚠ 圖示檔案不存在: {icon_path}")

    font = ("Arial", 20)

    # 設定 grid 結構
    window.grid_rowconfigure(1, weight=1)  # 輸入欄位
    window.grid_rowconfigure(3, weight=1)  # 輸出欄位
    window.grid_columnconfigure(0, weight=1)

    # 說明標籤
    input_label = tk.Label(window, text="請輸入台羅拼音（系統會自動忽略連字符「-」）", font=("Arial", 16), bg="#FFFFE0", anchor="w")
    input_label.grid(row=0, column=0, sticky="we", padx=10, pady=(10, 0))

    input_text = ScrolledText(window, font=font, bg="white", bd=3, relief="solid",
                               highlightbackground="blue", highlightcolor="blue", highlightthickness=2)
    input_text.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

    output_label = tk.Label(window, text="對應的台語點字", font=("Arial", 16), bg="#FFFFE0", anchor="w")
    output_label.grid(row=2, column=0, sticky="we", padx=10, pady=(15, 0))

    output_text = ScrolledText(window, font=font, bg="white", bd=3, relief="solid",
                                highlightbackground="red", highlightcolor="red", highlightthickness=2)
    output_text.grid(row=3, column=0, sticky="nsew", padx=10, pady=5)

    # 功能按鈕區
    bottom_frame = tk.Frame(window, bg="#FFFFE0")
    bottom_frame.grid(row=4, column=0, pady=20)

    def show_braille():
        text = input_text.get("1.0", tk.END).strip()
        clean_text = text.replace("-", "")
        result = tl_to_braille(clean_text)
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, result)

    def clear_text():
        input_text.delete("1.0", tk.END)
        output_text.delete("1.0", tk.END)

    convert_btn = tk.Button(bottom_frame, text="轉換", font=font, command=show_braille, bg="#FFDEAD")
    convert_btn.pack(side="left", padx=40)

    clear_btn = tk.Button(bottom_frame, text="清除", font=font, command=clear_text, bg="#FFDAB9")
    clear_btn.pack(side="right", padx=40)

    window.mainloop()

if __name__ == '__main__':
    create_gui()