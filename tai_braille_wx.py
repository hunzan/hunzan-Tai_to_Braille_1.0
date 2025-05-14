import json
import os
import wx

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
            if word in nasal:
                braille = "⠠" + nasal[word]["dots"]
                result_words.append(braille)
            else:
                syllables = split_syllables(word)
                braille = ''.join(convert_syllable(s) for s in syllables)
                result_words.append(braille)

        result_lines.append(' '.join(result_words))

    return '\n'.join(result_lines)

# wxPython GUI
class BrailleApp(wx.Frame):
    def __init__(self):
        super().__init__(None, title="台羅拼音轉台語點字", size=wx.Size(700, 600))

        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour("#FFFFE0"))  # ✅ 淺黃色背景

        vbox = wx.BoxSizer(wx.VERTICAL)

        # 🔹 字體大小範圍（初始值）
        self.text_font_size = 26  # 初始值
        self.label_font = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.text_font = wx.Font(self.text_font_size, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Cambria Math")

        # 🔹 標籤
        input_label = wx.StaticText(panel, label="請輸入台羅拼音（不要加連字符）")
        input_label.SetFont(self.label_font)
        vbox.Add(input_label, flag=wx.LEFT | wx.TOP, border=10)

        # 🔹 輸入框
        self.input_text = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_RICH2, size=wx.Size(650, 150))
        self.input_text.SetFont(self.text_font)
        vbox.Add(self.input_text, proportion=1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)

        # 🔹 輸出框
        output_label = wx.StaticText(panel, label="對應的台語點字")
        output_label.SetFont(self.label_font)
        vbox.Add(output_label, flag=wx.LEFT | wx.TOP, border=10)

        self.output_text = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2, size=wx.Size(650, 150))
        self.output_text.SetFont(self.text_font)
        vbox.Add(self.output_text, proportion=1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)

        # 🔹 滑桿：使用者可調整字體大小
        slider_label = wx.StaticText(panel, label="字體大小調整")
        vbox.Add(slider_label, flag=wx.LEFT | wx.TOP, border=10)

        self.slider = wx.Slider(panel, value=self.text_font_size, minValue=14, maxValue=40, style=wx.SL_HORIZONTAL)
        self.slider.Bind(wx.EVT_SLIDER, self.on_font_change)
        vbox.Add(self.slider, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)

        # 🔹 按鈕區
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        # 🔹 轉換按鈕
        convert_btn = wx.Button(panel, label="轉換", size=wx.Size(200, 50))
        convert_btn.SetFont(self.label_font)
        convert_btn.SetBackgroundColour(wx.Colour("#FFD700"))  # 金黃色背景
        convert_btn.SetForegroundColour(wx.Colour("#000000"))  # 黑色文字
        convert_btn.SetWindowStyle(wx.BORDER_DOUBLE)  # 加粗框線
        convert_btn.Bind(wx.EVT_BUTTON, self.show_braille)
        hbox.Add(convert_btn, proportion=1, flag=wx.RIGHT, border=20)

        # 🔹 清除按鈕
        clear_btn = wx.Button(panel, label="清除", size=wx.Size(200, 50))
        clear_btn.SetFont(self.label_font)
        clear_btn.SetBackgroundColour(wx.Colour("#87CEEB"))  # 天藍色背景
        clear_btn.SetForegroundColour(wx.Colour("#000000"))  # 黑色文字
        clear_btn.SetWindowStyle(wx.BORDER_DOUBLE)  # 加粗框線
        clear_btn.Bind(wx.EVT_BUTTON, self.clear_text)
        hbox.Add(clear_btn, proportion=1)

        # ✅ **重置字體大小按鈕**
        reset_font_btn = wx.Button(panel, label="重置字體大小", size=wx.Size(200, 50))
        reset_font_btn.SetFont(self.label_font)
        reset_font_btn.SetBackgroundColour(wx.Colour("#93FF93"))  # 淺綠色背景
        reset_font_btn.SetForegroundColour(wx.Colour("#000000"))  # 黑色文字
        reset_font_btn.SetWindowStyle(wx.BORDER_DOUBLE)
        reset_font_btn.Bind(wx.EVT_BUTTON, self.on_font_reset)  # 🔹 綁定按鈕事件
        hbox.Add(reset_font_btn, proportion=1, flag=wx.LEFT, border=20)

        vbox.Add(hbox, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=20)
        panel.SetSizer(vbox)

    def show_braille(self, event):
        text = self.input_text.GetValue()
        result = tl_to_braille(text)
        wx.CallAfter(self.output_text.SetValue, result)

    def clear_text(self, event):
        self.input_text.Clear()
        self.output_text.Clear()

    def on_font_change(self, event):
        """ 當滑桿移動時，改變輸入與輸出框的字體大小 """
        new_size = self.slider.GetValue()
        self.text_font = wx.Font(new_size, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.input_text.SetFont(self.text_font)
        self.output_text.SetFont(self.text_font)

    def on_font_reset(self, event):
        """ 按下按鈕時，重置字體大小到預設值 """
        self.text_font_size = 26  # 回到原始字體大小
        self.text_font = wx.Font(self.text_font_size, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.input_text.SetFont(self.text_font)
        self.output_text.SetFont(self.text_font)
        self.slider.SetValue(self.text_font_size)  # 同時更新滑桿數值

if __name__ == "__main__":
    app = wx.App()
    frame = BrailleApp()
    frame.Show()
    app.MainLoop()
