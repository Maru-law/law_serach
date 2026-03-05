import os
import json
import requests
import xml.etree.ElementTree as ET

# 対象とする法令リスト (法令ID: 法令名)
LAW_LIST = {
    "321AC0000000003": "constitution",  # 日本国憲法
    "129AC0000000089": "civil_code",    # 民法
}

DATA_DIR = "data"
CHUNK_SIZE = 100  # 100条ごとにJSONを分割

def fetch_law_xml(law_id):
    url = f"https://elaws.e-gov.go.jp/api/1/lawdata/{law_id}"
    response = requests.get(url)
    return response.content

def parse_law_xml(xml_content):
    root = ET.fromstring(xml_content)
    articles = {}
    
    # 条文(Article)を全抽出
    for article in root.findall(".//Article"):
        num_tag = article.find("ArticleTitle")
        if num_tag is None or not num_tag.text:
            continue
        
        # 条文番号の正規化 (例: 第十条の二 -> 10_2) 
        # ※簡易化のためタイトルをそのままキーにするか、正規化ロジックを挟む
        title = num_tag.text.replace("第", "").replace("条", "")
        
        # 本文の抽出 (ParagraphSentence)
        sentences = [s.text for s in article.findall(".//ParagraphSentence/Sentence") if s.text]
        
        # 軽量化データ構造 (t: title, s: sentences)
        articles[title] = {
            "t": num_tag.text,
            "s": sentences
        }
    return articles

def save_optimized_json(law_name, data):
    law_path = os.path.join(DATA_DIR, law_name)
    os.makedirs(law_path, exist_ok=True)
    
    # 巨大な法令を分割して保存
    items = list(data.items())
    index_map = {}
    
    for i in range(0, len(items), CHUNK_SIZE):
        chunk = dict(items[i:i + CHUNK_SIZE])
        chunk_name = f"chunk_{i // CHUNK_SIZE}.json"
        
        with open(os.path.join(law_path, chunk_name), 'w', encoding='utf-8') as f:
            json.dump(chunk, f, ensure_ascii=False, separators=(',', ':'))
            
        # インデックス作成 (どの条文がどのファイルにあるか)
        for key in chunk.keys():
            index_map[key] = chunk_name
            
    # インデックスファイルの保存
    with open(os.path.join(law_path, "index.json"), 'w', encoding='utf-8') as f:
        json.dump(index_map, f, ensure_ascii=False, separators=(',', ':'))

if __name__ == "__main__":
    for law_id, law_name in LAW_LIST.items():
        print(f"Processing {law_name}...")
        xml = fetch_law_xml(law_id)
        data = parse_law_xml(xml)
        save_optimized_json(law_name, data)
    print("Done!")
