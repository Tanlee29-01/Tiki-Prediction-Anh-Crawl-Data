import re

def clean_text(text):
    if not text: return ""
    text = str(text).replace("\r\n"," ").replace("\n"," ")
    text = re.sub(r"\s+"," ", text).strip()
    return text.lower()