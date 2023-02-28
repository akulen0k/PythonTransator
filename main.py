from time import sleep
import keyboard
import pytesseract
import pyperclip
from googletrans import Translator
import tkinter as tk
from PIL import Image, ImageGrab


def get_text():
    im = ImageGrab.grabclipboard()
    if im is not None:
        text = pytesseract.image_to_string(im, lang='eng')
        return text
    keyboard.press_and_release('ctrl+c')
    sleep(0.01)
    text = pyperclip.paste()
    return text


def get_translate_lang(text):
    ru = 0
    eng = 0
    for i in text:
        if 'a' <= i <= 'z' or 'A' <= i <= 'Z':
            eng += 1
        elif 'а' <= i <= 'я' or 'А' <= i <= 'Я':
            ru += 1
    return ("ru", "en") if ru >= eng else ("en", "ru")


def get_cords():
    root = tk.Tk()
    abs_coord_x = root.winfo_pointerx() - root.winfo_rootx()
    abs_coord_y = root.winfo_pointery() - root.winfo_rooty()
    root.destroy()
    return abs_coord_x, abs_coord_y


def prepare_for_show(cords, text: str):
    size = len(text)
    char_size = (9, 21)
    max_row = 100

    cnt = 0
    for i in range(size):
        cnt += 1
        if text[i] == '\n':
            cnt = 0
        if cnt >= max_row and text[i] == ' ':
            text = text[:i] + '\n' + text[i:]
            cnt = 0
    rows = text.count('\n') + 1

    cnt = 0
    max_row = 0
    for i in range(size):
        cnt += 1
        max_row = max(max_row, cnt)
        if text[i] == '\n':
            cnt = 0

    cords = (max(cords[0] - round(char_size[0] * (size if rows == 1 else max_row) / 2), 0),
             max(cords[1] - char_size[1] * rows, 0),
             round(char_size[0] * (size if rows == 1 else max_row)),
             char_size[1] * rows)
    return text, cords


def show_text(text, cords):
    root = tk.Tk()
    root.wm_overrideredirect(True)
    root.geometry("{0}x{1}+{2}+{3}".format(cords[2], cords[3], cords[0], cords[1]))
    root.bind("<Button-1>", lambda evt: root.destroy())
    root.attributes('-topmost', True)

    l = tk.Label(text=text, font=("Courier", 11))
    l.pack(expand=True)
    root.mainloop()


def handle_text():
    text = get_text()
    cords = get_cords()

    if text is None or len(text) == 0:
        return
    if len(text) >= 500:
        ind = text.rfind(" ")
        if ind != -1:
            text = text[:ind]
        else:
            text = text[:500]

    to_lang = get_translate_lang(text)
    translator = Translator()
    text = translator.translate(text, src=to_lang[0], dest=to_lang[1]).text

    text, cords = prepare_for_show(cords, text)
    show_text(text, cords)


if __name__ == '__main__':
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    keyboard.add_hotkey('ctrl+x', handle_text)
    keyboard.wait('esc')
