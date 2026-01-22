import requests
import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom

def fetch_homeplus_epg():
    # 1. 模擬真實瀏覽器的完整 Header
    url = "https://www.homeplus.net.tw/cable/program-list/get-program-data"
    headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
        "origin": "https://www.homeplus.net.tw",
        "referer": "https://www.homeplus.net.tw/cable/product-introduce/digital-tv/digital-program"
    }
    
    # 2. 修正參數：根據官網觀察，通常需要帶上當天日期
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    payload = {
        "system_id": "2", # 2 代表長德/萬象/麗冠 (台北區)
        "category_id": "0",
        "query_date": today # 加上日期參數
    }

    try:
        response = requests.post(url, data=payload, headers=headers)
        
        # 打印狀態碼，方便除錯
        print(f"Server Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"請求被拒絕，內容為: {response.text[:100]}")
            return

        data = response.json()
    except Exception as e:
        print(f"解析失敗: {e}")
        return

    # 3. 建立 XML 結構
    root = ET.Element("tv", {"generator-info-name": "Homeplus EPG Grabber"})

    # 4. 解析數據 (修正 Home+ JSON 實際路徑)
    # 根據中嘉 API 回傳結構，內容通常在 data['data']['list'] 裡
    channels = data.get('data', {}).get('list', [])
    
    if not channels:
        print("未抓取到頻道資料，請檢查 system_id 是否正確")
        return

    for channel_data in channels:
        chn_id = str(channel_data.get('channel_id'))
        chn_name = channel_data.get('chn_name')
        
        # 建立 <channel>
        channel_node = ET.SubElement(root, "channel", id=f"HP.{chn_id}")
        ET.SubElement(channel_node, "display-name").text = chn_name

        # 獲取節目清單
        programs = channel_data.get('programs', [])
        for prog in programs:
            try:
                # 取得時間 (Home+ 回傳格式通常為 "08:00")
                # 注意：需結合當天日期來組成 XMLTV 格式
                p_date = prog.get('program_date') # YYYY-MM-DD
                p_start = prog.get('start_time')  # HH:mm
                p_end = prog.get('end_time')      # HH:mm
                
                # 組合時間字串
                start_dt = datetime.datetime.strptime(f"{p_date} {p_start}", "%Y-%m-%d %H:%M")
                end_dt = datetime.datetime.strptime(f"{p_date} {p_end}", "%Y-%m-%d %H:%M")
                
                # 處理跨日問題 (如果結束時間小於開始時間，表示到了隔天)
                if end_dt <= start_dt:
                    end_dt += datetime.timedelta(days=1)

                start_fmt = start_dt.strftime("%Y%m%d%H%M%S +0800")
                end_fmt = end_dt.strftime("%Y%m%d%H%M%S +0800")

                prog_node = ET.SubElement(root, "programme", {
                    "start": start_fmt,
                    "stop": end_fmt,
                    "channel": f"HP.{chn_id}"
                })
                ET.SubElement(prog_node, "title", lang="zh").text = prog.get('program_name')
            except:
                continue

    # 5. 美化並儲存
    xml_str = ET.tostring(root, encoding='utf-8')
    pretty_xml = minidom.parseString(xml_str).toprettyxml(indent="  ")
    
    with open("epg.xml", "w", encoding="utf-8") as f:
        f.write
