import os

import pytesseract
import pyautogui

from PyPDF2 import PdfFileReader, PdfFileWriter, PdfFileMerger
import csv


def get_text_from_pdf_page(page):
    text = pytesseract.image_to_string(page)
    pyautogui.locateOnScreen("a.png", confidence=0.7)
    return text


def convert_pdf_to_text():
    pass


def convert_image_to_text():
    pass


def test():
    image = pyautogui.screenshot(region=(200, 200, 200, 200))
    image.save(os.getcwd() + "/a.png")
    # print(str(image.size))
    res = pyautogui.locateOnScreen(image, confidence=0.9)
    print(res)


if __name__ == '__main__':
    test()
