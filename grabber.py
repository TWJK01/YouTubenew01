import requests
import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom
import json

def fetch_homeplus_epg():
    # 嘗試不同的 system_id，2 通常是台北長德，1 是基隆吉隆
    system_id = "2"
    url = "https://www.homeplus.net.tw/cable/program-list/get-program-data"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.homeplus.net.tw/cable/product-introduce/digital-tv/digital-program",
        "Origin": "https://www.homeplus.net.tw"
    }
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    payload = {
        "system_id": system_id,
        "category_id": "0",
        "query_date": today
    }

    print(f"正在請求中嘉 API (日期: {today}, 系統ID: {system_id})...")

    try:
        response = requests.post(url, data=payload, headers=headers, timeout=20)
        print(f"HTTP 狀態碼: {response.status_code}")
        
        if response.status_code != 200:
            print(f"伺服器錯誤內容: {response.text[:200]}")
            return

        # 檢查是否為有效的 JSON
        try:
            res_json = response.json()
        except Exception as je:
            print(f"無法解析 JSON，原始回傳內容前 200 字: {response.text[:200]}")
            return

        # 中嘉 API 結構有時在 'data' 下，有時直接在根目錄
        data_body = res_json.get('data', res_json)
        channels = data_body.get('list', [])

        if not channels:
            print("API 回傳成功但頻道列表為空，可能是該 system_id 目前無資料或 IP 被限制。")
            # 打印出 JSON 鍵值幫助除錯
            print(f"JSON 根鍵值: {list(res_json.keys())}")
            return

        # 開始建立 XMLTV
        root = ET.Element("tv", {"generator-info-name": "Homeplus-EPG"})

        count = 0
        for ch in channels:
            chn_id = f"HP.{ch.get('channel_id')}"
            chn_name = ch.get('chn_name', 'Unknown')
            
            c_node = ET.SubElement(root, "channel", id=chn_id)
            ET.SubElement(c_node, "display-name").text = chn_name
            
            programs = ch.get('programs', [])
            for pg in programs:
                try:
                    p_date = pg.get('program_date')
                    p_start = pg.get('start_time')
                    p_end = pg.get('end_time')
                    
                    start_dt = datetime.datetime.strptime(f"{p_date} {p_start}", "%Y-%m-%d %H:%M")
                    end_dt = datetime.datetime.strptime(f"{p_date} {p_end}", "%Y-%m-%d %H:%M")
                    if end_dt <= start_dt:
                        end_dt += datetime.timedelta(days=1)
                    
                    p_node = ET.SubElement(root, "programme", {
                        "start": start_dt.strftime("%Y%m%d%H%M%S +0800"),
                        "stop": end_dt.strftime("%Y%m%d%H%M%S +0800"),
                        "channel": chn_id
                    })
                    ET.SubElement(p_node, "title", lang="zh").text = pg.get('program_name')
                    count += 1
                except:
                    continue

        # 美化並存檔
        xml_str = ET.tostring(root, encoding='utf-8')
        pretty_xml = minidom.parseString(xml_str).toprettyxml(indent="  ")
        with open("epg.xml", "w", encoding="utf-8") as f:
            f.write(pretty_xml)
        
        print(f"成功更新！共抓取 {len(channels)} 個頻道，{count} 個節目。")

    except Exception as e:
        print(f"發生未預期錯誤: {str(e)}")

if __name__ == "__main__":
    fetch_homeplus_epg()
