import requests
import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom

def fetch_homeplus_epg():
    # 1. 基本設定
    url = "https://www.homeplus.net.tw/cable/program-list/get-program-data"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }
    
    # system_id 說明: 1-吉隆, 2-長德, 3-萬象, 4-麗冠... (此處以長德為例)
    payload = {
        "system_id": "2", 
        "category_id": "0"
    }

    try:
        response = requests.post(url, data=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"請求失敗: {e}")
        return

    # 2. 建立 XML 結構
    root = ET.Element("tv", {"generator-info-name": "Homeplus EPG Grabber"})

    # 3. 解析頻道與節目
    # 假設 data['list'] 包含了所有頻道
    channels = data.get('list', [])
    
    for channel_data in channels:
        chn_id = str(channel_data.get('channel_id'))
        chn_name = channel_data.get('chn_name')
        
        # 建立 <channel> 標籤
        channel_node = ET.SubElement(root, "channel", id=chn_id)
        ET.SubElement(channel_node, "display-name").text = chn_name

        # 獲取該頻道的節目表 (Home+ 的 JSON 結構中通常在 'programs' 內)
        programs = channel_data.get('programs', [])
        for prog in programs:
            # 轉換時間格式 (假設網站給的是 2024-05-20 08:00)
            # XMLTV 格式要求: YYYYMMDDHHMMSS +0800
            try:
                start_raw = prog.get('start_time') # 需根據實際 JSON 欄位調整
                end_raw = prog.get('end_time')
                
                start_dt = datetime.datetime.strptime(start_raw, "%Y-%m-%d %H:%M")
                end_dt = datetime.datetime.strptime(end_raw, "%Y-%m-%d %H:%M")
                
                start_fmt = start_dt.strftime("%Y%m%d%H%M%S +0800")
                end_fmt = end_dt.strftime("%Y%m%d%H%M%S +0800")

                prog_node = ET.SubElement(root, "programme", {
                    "start": start_fmt,
                    "stop": end_fmt,
                    "channel": chn_id
                })
                ET.SubElement(prog_node, "title", lang="zh").text = prog.get('program_name')
            except:
                continue

    # 4. 美化並儲存 XML
    xml_str = ET.tostring(root, encoding='utf-8')
    pretty_xml = minidom.parseString(xml_str).toprettyxml(indent="  ")
    
    with open("epg.xml", "w", encoding="utf-8") as f:
        f.write(pretty_xml)
    print("EPG 抓取完成，已存入 epg.xml")

if __name__ == "__main__":
    fetch_homeplus_epg()
