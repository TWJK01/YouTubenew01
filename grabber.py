import requests
import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os

def fetch_homeplus_epg():
    url = "https://www.homeplus.net.tw/cable/program-list/get-program-data"
    
    # 增加隨機化偽裝
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.homeplus.net.tw/cable/product-introduce/digital-tv/digital-program",
        "Origin": "https://www.homeplus.net.tw"
    }
    
    # 嘗試抓取 3 天份的資料
    root = ET.Element("tv", {"generator-info-name": "Homeplus-GitHub-Actions"})
    
    # 加入頻道定義（手動加入幾個核心頻道確保文件不為空）
    # ID 請參考官網，例如 19 是 Discovery
    target_channels = ["19", "20", "21", "26", "29"] 
    
    # 這裡抓取 system_id 2 (台北區)
    payload = {
        "system_id": "2",
        "category_id": "0",
        "query_date": datetime.datetime.now().strftime("%Y-%m-%d")
    }

    try:
        response = requests.post(url, data=payload, headers=headers, timeout=15)
        print(f"HTTP Status: {response.status_code}")
        
        # 如果被擋 IP (403)，則建立一個含有錯誤訊息的 EPG
        if response.status_code != 200:
            print("Access Denied by Home+ WAF")
            return

        json_data = response.json()
        channels = json_data.get('data', {}).get('list', [])

        if not channels:
            print("No data found in JSON")
            return

        for ch in channels:
            chn_id = f"HP.{ch.get('channel_id')}"
            chn_name = ch.get('chn_name')
            
            # Channel node
            c_node = ET.SubElement(root, "channel", id=chn_id)
            ET.SubElement(c_node, "display-name").text = chn_name
            
            for pg in ch.get('programs', []):
                start_dt = datetime.datetime.strptime(f"{pg['program_date']} {pg['start_time']}", "%Y-%m-%d %H:%M")
                end_dt = datetime.datetime.strptime(f"{pg['program_date']} {pg['end_time']}", "%Y-%m-%d %H:%M")
                if end_dt <= start_dt:
                    end_dt += datetime.timedelta(days=1)
                
                p_node = ET.SubElement(root, "programme", {
                    "start": start_dt.strftime("%Y%m%d%H%M%S +0800"),
                    "stop": end_dt.strftime("%Y%m%d%H%M%S +0800"),
                    "channel": chn_id
                })
                ET.SubElement(p_node, "title", lang="zh").text = pg.get('program_name')

        # 寫入檔案
        xml_str = ET.tostring(root, encoding='utf-8')
        pretty_xml = minidom.parseString(xml_str).toprettyxml(indent="  ")
        with open("epg.xml", "w", encoding="utf-8") as f:
            f.write(pretty_xml)
        print("epg.xml updated successfully")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fetch_homeplus_epg()
