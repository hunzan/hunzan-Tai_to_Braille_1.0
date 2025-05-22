import sys
import os
import json
import wx
import wx.adv
import wx.richtext as rt

def resource_path(relative_path):
    # 專為 PyInstaller 打包後取得資源路徑
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# ✅ 使用 resource_path 讀特殊用字表
with open(resource_path('braille_data/special_cases.json'), 'r', encoding='utf-8') as f:
    special_cases = json.load(f)

# 統一用 resource_path 取得資料夾與字型、JSON 檔案的路徑
font_path = resource_path("DoulosSIL-Regular.ttf")

# 資料夾路徑
DATA_DIR = resource_path('braille_data')  # ✅ 注意：改用 resource_path 包住整個資料夾

# 各個 JSON 檔案路徑
CONSONANTS_FILE = os.path.join(DATA_DIR, 'consonants.json')
VOWELS_FILE     = os.path.join(DATA_DIR, 'vowels_all.json')
RUSHIO_FILE     = os.path.join(DATA_DIR, 'rushio_syllables.json')
NASAL_FILE      = os.path.join(DATA_DIR, 'nasal_table.json')
SPECIAL_FILE    = os.path.join(DATA_DIR, 'special_cases.json')  # ✅ 新增這行

# 載入 JSON 資料
def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

consonants = load_json(CONSONANTS_FILE)
vowels = load_json(VOWELS_FILE)
rushio = load_json(RUSHIO_FILE)
nasal = load_json(NASAL_FILE)
special_cases = load_json(SPECIAL_FILE)

def load_json(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"找不到檔案：{filepath}")
        return {}
    except json.JSONDecodeError:
        print(f"無法解析 JSON 格式：{filepath}")
        return {}

# 切音節
def split_syllables(word):
    # ✅ 若是特殊詞組，直接回傳其音節（不再拆解）
    if word.strip().lower() in special_cases:
        return special_cases[word.strip().lower()]

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
    # ✅ 若是整個特殊詞組，直接轉成對應的點字（不進一步拆解）
    if s in special_cases:
        braille = ''
        for part in special_cases[s]:
            braille += convert_syllable(part)
        return braille

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
        return rushio[s]["dots"]  # ✅ rushio 單獨音節轉譯

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
            # ✅ 新增：先檢查是否為特殊用字
            if word in special_cases:
                braille = special_cases[word]["dots"]
                result_words.append(braille)

            # ✅ 原有邏輯：檢查是否為特殊鼻化音（像 nn̄g）
            elif word in nasal:
                braille = "⠠" + nasal[word]["dots"]
                result_words.append(braille)

            # ✅ 正常轉換流程
            else:
                syllables = split_syllables(word)
                braille = ''.join(convert_syllable(s) for s in syllables)
                result_words.append(braille)

        result_lines.append(' '.join(result_words))

    return '\n'.join(result_lines)

# wxPython GUI
class BrailleApp(wx.Frame):
    def __init__(self):
        super().__init__(None, title="台羅拼音轉台語點字工具【蕉點１號】", size=wx.Size(700, 600))

        panel = wx.Panel(self)

        # 建立 sizer 與元件
        sizer = wx.BoxSizer(wx.VERTICAL)
        # sizer.Add(...) 放元件進來
        panel.SetSizer(sizer)
        sizer.Fit(panel)
        panel.Layout()

        wx.CallAfter(self.Maximize)  # 避免太早最大化，畫面錯亂
        self.Layout()
        self.Refresh()

        # 載入 .ico 檔
        icon_path = resource_path("taivi.ico")
        icon = wx.Icon(icon_path, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))

        font_path = os.path.join(base_path, "DoulosSIL-Regular.ttf")
        braille_data_path = os.path.join(base_path, "braille_data")

        # 嘗試載入自帶字型
        try:
            wx.Font.AddPrivateFont(font_path)
            self.font_name = "Doulos SIL"
        except:
            self.font_name = "Cambria Math"  # 備用字型（大部分系統都有）

        # 預設字體大小
        self.text_font_size = 26

        # 建立字型物件
        self.text_font = wx.Font(self.text_font_size, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName=self.font_name)
        self.label_font = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)

        panel.SetBackgroundColour(wx.Colour("#FFFFE0"))  # 淺黃色背景

        vbox = wx.BoxSizer(wx.VERTICAL)

        # 建立一個 static box（NVDA 可朗讀的說明文字）
        input_box = wx.StaticBox(panel, label="請輸入台羅拼音（有無連字符「-」均可）")
        font = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        input_box.SetFont(font)
        input_sizer = wx.StaticBoxSizer(input_box, wx.VERTICAL)

        # 外框 panel
        input_wrapper = wx.Panel(panel)
        input_wrapper.SetBackgroundColour(wx.Colour("#227700"))  # 深灰框線顏色

        # 輸入框
        self.input_text = wx.TextCtrl(input_wrapper, style=wx.TE_MULTILINE | wx.TE_PROCESS_TAB)
        self.input_text.SetFont(self.text_font)
        self.input_text.SetName("請輸入台羅拼音（有無連字符都可以）")
        self.input_text.SetHelpText("請輸入台羅拼音，有無連字符都可以")
        self.input_text.Bind(wx.EVT_CHAR_HOOK, self.on_input_tab)

        input_inner_sizer = wx.BoxSizer(wx.VERTICAL)
        input_inner_sizer.Add(self.input_text, proportion=1, flag=wx.EXPAND | wx.ALL, border=6)
        input_wrapper.SetSizer(input_inner_sizer)

        # 把外框加到 static box 裡
        input_sizer.Add(input_wrapper, proportion=1, flag=wx.EXPAND | wx.ALL, border=0)

        # 建立一個 static box（NVDA 可朗讀的說明文字）
        output_box = wx.StaticBox(panel, label="對應的台語點字")
        font = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        output_box.SetFont(font)
        output_sizer = wx.StaticBoxSizer(output_box, wx.VERTICAL)

        # 包裝輸出框的外層 panel
        output_wrapper = wx.Panel(panel)
        output_wrapper.SetBackgroundColour(wx.Colour("#880000"))

        # 輸出框
        self.output_text = wx.TextCtrl(output_wrapper, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2)
        self.output_text.SetFont(self.text_font)
        self.output_text.SetName("對應的台語點字")
        self.output_text.SetHelpText("這裡顯示對應的台語點字，唯讀不可編輯")

        # 模擬內邊框效果
        output_inner_sizer = wx.BoxSizer(wx.VERTICAL)
        output_inner_sizer.Add(self.output_text, proportion=1, flag=wx.EXPAND | wx.ALL, border=6)
        output_wrapper.SetSizer(output_inner_sizer)

        # 把 wrapper 加進 static box sizer
        output_sizer.Add(output_wrapper, proportion=1, flag=wx.EXPAND | wx.ALL, border=0)

        # 滑桿：字體大小調整
        slider_label = wx.StaticText(panel, label="字體大小調整")
        slider_label.SetFont(self.label_font)

        self.slider = wx.Slider(
            panel,
            value=self.text_font_size,
            minValue=20,
            maxValue=66,
            style=wx.SL_HORIZONTAL,
            size=(600, 40)  # 放大滑桿高度
        )
        self.slider.Bind(wx.EVT_SLIDER, self.on_font_change)

        # 按鈕區
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        # 按鈕：轉換
        self.convert_btn = wx.Button(panel, label="轉換", size=wx.Size(200, 50))
        self.convert_btn.SetFont(self.label_font)
        self.convert_btn.SetBackgroundColour(wx.Colour("#FFD700"))
        self.convert_btn.SetForegroundColour(wx.Colour("#000000"))
        self.convert_btn.SetWindowStyle(wx.BORDER_DOUBLE)
        self.convert_btn.Bind(wx.EVT_BUTTON, self.show_braille)
        hbox.Add(self.convert_btn, proportion=1, flag=wx.RIGHT, border=20)

        # 按鈕：清除
        self.clear_btn = wx.Button(panel, label="清除", size=wx.Size(200, 50))
        self.clear_btn.SetFont(self.label_font)
        self.clear_btn.SetBackgroundColour(wx.Colour("#87CEEB"))
        self.clear_btn.SetForegroundColour(wx.Colour("#000000"))
        self.clear_btn.SetWindowStyle(wx.BORDER_DOUBLE)
        self.clear_btn.Bind(wx.EVT_BUTTON, self.clear_text)
        hbox.Add(self.clear_btn, proportion=1)

        # 將原本「重置字體大小」改為「背景字體模式」
        self.bg_mode_btn = wx.Button(panel, label="背景字體模式", size=wx.Size(200, 50))
        self.bg_mode_btn.SetFont(self.label_font)
        self.bg_mode_btn.SetBackgroundColour(wx.Colour("#93FF93"))
        self.bg_mode_btn.SetForegroundColour(wx.Colour("#000000"))
        self.bg_mode_btn.SetWindowStyle(wx.BORDER_DOUBLE)
        self.bg_mode_btn.Bind(wx.EVT_BUTTON, self.toggle_bg_mode)
        hbox.Add(self.bg_mode_btn, proportion=1, flag=wx.LEFT, border=20)

        # 建立 footer 區塊
        footer_label = wx.StaticText(panel, label="© 2025 開發者：Lîm A-kâu（林阿猴）& Kim Chio（金蕉），供免費教學及學習使用。")
        footer_label.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

        # 設定給 NVDA 報讀的可存取資訊（這很關鍵）
        footer_label.SetName("程式資訊")
        footer_label.SetHelpText("© 2025 開發者：Lîm A-kâu（林阿猴）& Kim Chio（金蕉），供免費教學及學習使用。")

        panel.SetSizer(vbox)

        # 背景字體模式，0=白底黑字（預設）
        self.bg_mode = 0
        self.apply_bg_mode()

        self.Show()
        self.input_text.Refresh()
        self.input_text.Update()

        # **確保視窗顯示**
        self.Show()
        self.input_text.Refresh()
        self.input_text.Update()

        # 加入 vbox，照畫面順序
        vbox.Add(input_sizer, proportion=1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)
        vbox.Add(hbox, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=20)
        vbox.Add(output_sizer, proportion=1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)
        vbox.Add(slider_label, flag=wx.LEFT | wx.TOP, border=12)
        vbox.Add(self.slider, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)
        vbox.Add(footer_label, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)

    def show_braille(self, event):
        original_text = self.input_text.GetValue()
        clean_text = original_text.replace("-", "")
        result = tl_to_braille(clean_text)

        # 更新點字欄位
        wx.CallAfter(self.output_text.SetValue, result)

        # 自動複製到剪貼簿
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(result))
            wx.TheClipboard.Close()

            # 顯示提示訊息，NVDA 會朗讀這段訊息
            notification = wx.adv.NotificationMessage("提示", "已複製到剪貼簿")
            notification.Show(timeout=wx.adv.NotificationMessage.Timeout_Auto)

    def clear_text(self, event):
        self.input_text.Clear()
        self.output_text.Clear()

    def on_input_tab(self, event):
        key_code = event.GetKeyCode()
        if key_code == wx.WXK_TAB:
            # 若有 Shift，表示是 Shift+Tab（往前），可以改成跳到上一個元件
            if event.ShiftDown():
                self.slider.SetFocus()
            else:
                self.output_text.SetFocus()
        else:
            event.Skip()

    def on_font_change(self, event):
        new_size = self.slider.GetValue()
        self.text_font = wx.Font(new_size, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName=self.font_name)
        self.input_text.SetFont(self.text_font)
        self.output_text.SetFont(self.text_font)

    def toggle_bg_mode(self, event):
        self.bg_mode = (self.bg_mode + 1) % 4
        self.apply_bg_mode()

    def apply_bg_mode(self):
        # 設定背景色與文字顏色
        if self.bg_mode == 0:
            bg_color = wx.Colour(255, 255, 255)  # 白底
            fg_color = wx.Colour(0, 0, 0)  # 黑字
        elif self.bg_mode == 1:
            bg_color = wx.Colour(0, 0, 0)  # 黑底
            fg_color = wx.Colour(255, 255, 255)  # 白字
        elif self.bg_mode == 2:
            bg_color = wx.Colour(0, 0, 0)  # 黑底
            fg_color = wx.Colour(255, 255, 0)  # 黃字
        else:  # bg_mode == 3
            bg_color = wx.Colour(0, 77, 0)  # 深綠底
            fg_color = wx.Colour(255, 255, 255)  # 白字

        # **只設定輸入與輸出框的前景與背景**
        self.input_text.SetBackgroundColour(bg_color)
        self.input_text.SetForegroundColour(fg_color)

        self.output_text.SetBackgroundColour(bg_color)
        self.output_text.SetForegroundColour(fg_color)

        # 強制更新
        self.input_text.Refresh()
        self.output_text.Refresh()

if __name__ == "__main__":
    app = wx.App(False)
    frame = BrailleApp()
    frame.Show()
    app.MainLoop()
