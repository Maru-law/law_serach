import requests
import xml.etree.ElementTree as ET
import json
import os

# 取得対象の法令リスト (法令ID)
LAW_LIST = {
    "minpo": "明治二十九年法律第八十九号",  # 民法
    "kenpo": "昭和二十一年憲法",            # 憲法
    "keihou": "明治四十年法律第四十五号"     # 刑法
}

BASE_URL = "https://elaws.e-gov.go.jp/api/1/lawdata/"

def parse_law_xml(law_id):
    response = requests.get(f"{BASE_URL}{law_id}")
    if response.status_code != 200:
        return None
    
    root = ET.fromstring(response.content)
    law_title = root.find(".//LawTitle").text
    
    # データ構造: { "t": タイトル, "a": { "条数": { "c": 見出し, "s": [本文] } } }
    law_data = {
        "t": law_title,
        "a": {}
    }

    for article in root.findall(".//Article"):
        num_node = article.find("ArticleTitle")
        if num_node is None: continue
        
        num = num_node.text.replace("第", "").replace("条", "")
        caption = article.find("ArticleCaption")
        caption_text = caption.text if caption is not None else ""
        
        sentences = []
        for sentence in article.findall(".//Sentence"):
            if sentence.text:
                sentences.append(sentence.text)
        
        law_data["a"][num] = {
            "c": caption_text,
            "s": sentences
        }
    
    return law_data

def save_optimized_json(name, data):
    os.makedirs("data", exist_ok=True)
    # 大きな法令（民法など）はここで分割ロジックを入れることも可能
    # 今回は1つの最適化されたJSONとして保存
    with open(f"data/{name}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))

if __name__ == "__main__":
    for name, law_id in LAW_LIST.items():
        print(f"Processing {name}...")
        data = parse_law_xml(law_id)
        if data:
            save_optimized_json(name, data)