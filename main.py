import asyncio
import httpx
import re
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from datetime import datetime

# --- 配置區 ---
OUTPUT_FILE = "Full_TV_Wall.m3u8"
YOUTUBE_CHANNELS = {
    "台灣,#genre#": {
        "台灣地震監視": "https://www.youtube.com/@台灣地震監視/streams",
        "台灣颱風論壇": "https://www.youtube.com/@twtybbs2009/streams",		
        "台視新聞": "https://www.youtube.com/@TTV_NEWS/streams",
        "中視新聞": "https://www.youtube.com/@chinatvnews/streams",
        "中視新聞 HD": "https://www.youtube.com/@twctvnews/streams",
        "華視新聞": "https://www.youtube.com/@CtsTw/streams",
        "民視新聞網": "https://www.youtube.com/@FTV_News/streams",
        "公視": "https://www.youtube.com/@ptslivestream/streams",
        "公視新聞網": "https://www.youtube.com/@PNNPTS/streams",
        "公視台語台": "https://www.youtube.com/@ptstaigitai/streams",
        "TaiwanPlus": "https://www.youtube.com/@TaiwanPlusLive/streams",		
        "大愛電視": "https://www.youtube.com/@DaAiVideo/streams",
        "鏡新聞": "https://www.youtube.com/@mnews-tw/streams",
        "東森新聞": "https://www.youtube.com/@newsebc/streams",
        "三立iNEWS": "https://www.youtube.com/channel/UCoNYj9OFHZn3ACmmeRCPwbA",		
        "三立LIVE新聞": "https://www.youtube.com/@setnews/streams",
        "中天新聞CtiNews": "https://www.youtube.com/@中天新聞CtiNews/streams",
        "中天電視CtiTv": "https://www.youtube.com/@中天電視CtiTv/streams",
        "中天亞洲台": "https://www.youtube.com/@中天亞洲台CtiAsia/streams",	
        "TVBS NEWS": "https://www.youtube.com/@TVBSNEWS01/streams",
        "Focus全球新聞": "https://www.youtube.com/@tvbsfocus/streams",	
        "寰宇新聞": "https://www.youtube.com/@globalnewstw/streams",
        "寰宇全視界": "https://www.youtube.com/@globalvisiontalk/streams",		
        "udn video": "https://www.youtube.com/@udn-video/streams",
        "CNEWS匯流新聞網": "https://www.youtube.com/@CNEWS/streams",	
        "新唐人亞太電視台": "https://www.youtube.com/@NTDAPTV/streams",
        "八大民生新聞": "https://www.youtube.com/@gtvnews27/streams",		
        "原視新聞網 TITV News": "https://www.youtube.com/@TITVNews16/streams",
        "飛碟聯播網": "https://www.youtube.com/@921ufonetwork/streams",		
        "三大一台": "https://www.youtube.com/@SDTV55ch/streams",	
        "中天財經頻道": "https://www.youtube.com/@中天財經頻道CtiFinance/streams",	
        "東森財經股市": "https://www.youtube.com/@57ETFN/streams",	
        "寰宇財經新聞": "https://www.youtube.com/@globalmoneytv/streams",
        "非凡電視": "https://www.youtube.com/@ustv/streams",
        "非凡商業台": "https://www.youtube.com/@ustvbiz/streams",	
        "運通財經台": "https://www.youtube.com/@EFTV01/streams",
        "全球財經台2": "https://www.youtube.com/@全球財經台2/streams",	
        "AI主播倪珍Nikki 播新聞": "https://www.youtube.com/@NOWNEWS-AI-Anchor-Niki/streams",
        "BNE TV - 新西兰中文国际频道": "https://www.youtube.com/@BNETVNZ/streams",	
        "POP Radio聯播網": "https://www.youtube.com/@917POPRadio/streams",
        "LIVE NOW": "https://www.youtube.com/@LiveNow24H/streams",	
        "鳳凰衛視PhoenixTV": "https://www.youtube.com/@phoenixtvglobal/streams",
        "HOY 資訊台 × 有線新聞": "https://www.youtube.com/@HOYTVHK/streams",		
        "CCTV中文": "https://www.youtube.com/@CCTVCH/featured",
        "8world": "https://www.youtube.com/@8worldSG/streams"
    },
    "綜藝,#genre#": {
        "MIT台灣誌": "https://www.youtube.com/@ctvmit/streams",
        "大陸尋奇": "https://www.youtube.com/@ctvchinatv/streams",	
        "八大電視娛樂百分百": "https://www.youtube.com/@GTV100ENTERTAINMENT/streams",
        "三立娛樂星聞": "https://www.youtube.com/@star_setn/streams",	
        "中視經典綜藝": "https://www.youtube.com/@ctvent_classic/streams",
        "綜藝一級棒": "https://www.youtube.com/@NO1TVSHOW/streams",
        "小姐不熙娣": "https://www.youtube.com/@deegirlstalk/streams",
        "民視 超級冰冰Show": "https://www.youtube.com/@superbingbingshow/streams",
        "民視綜藝娛樂 Formosa TV Entertainments": "https://www.youtube.com/@FTV_Show/streams",			
        "木曜4超玩": "https://www.youtube.com/@Muyao4/streams",	
        "華視綜藝頻道": "https://www.youtube.com/@CTSSHOW/streams",
        "綜藝大熱門": "https://www.youtube.com/@HotDoorNight/streams",
        "綜藝玩很大": "https://www.youtube.com/@Mr.Player/streams",	
        "11點熱吵店": "https://www.youtube.com/@chopchopshow/streams",
        "飢餓遊戲": "https://www.youtube.com/@HungerGames123/streams",	
        "豬哥會社": "https://www.youtube.com/@FTV_ZhuGeClub/streams",
        "百變智多星": "https://www.youtube.com/@百變智多星/streams",	
        "東森綜合台": "https://www.youtube.com/@ettv32/streams",
        "中天娛樂頻道": "https://www.youtube.com/user/ctimulti",		
        "57怪奇物語": "https://www.youtube.com/@57StrangerThings/streams",
        "命運好好玩": "https://www.youtube.com/@eravideo004/streams",	
        "TVBS娛樂頭條": "https://www.youtube.com/@tvbsenews/streams",	
        "台灣啟示錄": "https://www.youtube.com/@ebcapocalypse/streams",
        "緯來日本台": "https://www.youtube.com/@VideolandJapan/streams",
        "我愛小明星大跟班": "https://www.youtube.com/@我愛小明星大跟班/streams",
        "明星下班路": "https://www.youtube.com/@gtvstaroad/videos",		
        "204檔案": "https://www.youtube.com/@204/streams",
        "WTO姐妹會": "https://www.youtube.com/@WTOSS/streams",	
        "好看娛樂": "https://www.youtube.com/@好看娛樂/streams",
        "超級夜總會": "https://www.youtube.com/@SuperNightClubCH29/videos",	
        "TVBS女人我最大": "https://www.youtube.com/@tvbsqueen/streams",
        "型男大主廚": "https://www.youtube.com/@twcookingshow/videos",
        "娛樂星動線": "https://www.youtube.com/@chinatimesent/streams",		
        "非凡大探索": "https://www.youtube.com/@ustvfoody/streams",
        "你好, 星期六 Hello Saturday Official": "https://youtube.com/@hellosaturdayofficial?si=--6KGPLtLMpXRMN5",	
        "BIF相信未來 官方頻道": "https://www.youtube.com/@BelieveinfutureTV/streams",
        "GTV 自由的旅行者": "https://www.youtube.com/@gtvfreedomtravelers/streams",
        "原視 TITV+": "https://www.youtube.com/@titv8932/videos",
		"寶島神很大": "https://www.youtube.com/@godBlessBaodao/streams",
        "Taste The World": "https://www.youtube.com/@TasteTheWorld66/videos",
        "現在宅知道": "https://www.youtube.com/@cbotaku/streams",
		"娱综星天地": "https://www.youtube.com/@娱综星天地/streams",
        "靖天電視台": "https://www.youtube.com/@goldentvdrama/streams",
        "靈異錯別字": "https://www.youtube.com/@靈異錯別字ctiwugei/streams",
        "綜藝一級棒": "https://www.youtube.com/@NO1TVSHOW/streams",		
        "下面一位": "https://www.youtube.com/@ytnextone_1/streams",		
        "公共電視-我們的島": "https://www.youtube.com/@ourislandTAIWAN/streams",
        "WeTV 綜藝經典": "https://www.youtube.com/@WeTV-ClassicVariety/videos",
        "爆梗TV": "https://www.youtube.com/@爆梗PunchlineTV/streams",
		"緯來新聞網": "https://www.youtube.com/@videolandnews/streams",
        "灿星官方频道": "https://www.youtube.com/@CanxingMediaOfficialChannel/streams",
        "陕西广播电视台官方频道": "https://www.youtube.com/@chinashaanxitvofficialchan2836/videos",		
        "北京廣播電視台生活頻道": "https://www.youtube.com/@Brtvofficialchannel/streams"		
        
    },
    "影劇,#genre#": {	
        "戲說台灣": "https://www.youtube.com/@TWStoryTV/streams",	
	    "CCTV纪录": "https://www.youtube.com/@CCTVDocumentary/streams",
	    "大愛劇場 DaAiDrama": "https://www.youtube.com/@DaAiDrama/streams",	
        "台視時光機": "https://www.youtube.com/@TTVClassic/streams",
        "中視經典戲劇": "https://www.youtube.com/@ctvdrama_classic/streams",
        "華視戲劇頻道": "https://www.youtube.com/@cts_drama/streams",
        "民視戲劇館": "https://www.youtube.com/@FTVDRAMA/streams",
        "四季線上4gTV": "https://www.youtube.com/@4gTV_online/streams",	
        "三立電視 SET TV": "https://www.youtube.com/@SETTV/streams",
        "三立華劇 SET Drama": "https://www.youtube.com/@SETdrama/streams",
        "三立台劇 SET Drama": "https://www.youtube.com/@setdramatw/streams",	
        "終極系列": "https://www.youtube.com/@KOONERETURN/streams",
        "TVBS劇在一起": "https://www.youtube.com/@tvbsdrama/streams",
        "TVBS戲劇-女兵日記 女力報到": "https://www.youtube.com/@tvbs-1587/streams",	
        "八大劇樂部": "https://www.youtube.com/@gtv-drama/streams",
        "GTV DRAMA English": "https://www.youtube.com/@gtvdramaenglish/streams",
        "萌萌愛追劇": "https://www.youtube.com/@mengmengaizhuijuminidrama/streams",	
        "龍華電視": "https://www.youtube.com/@ltv_tw/streams",
        "Vidol TV": "https://youtube.com/@vidoltv?si=wc0vxpCHtEVhigyf",		
        "緯來戲劇台": "https://www.youtube.com/@Vldrama43/streams",
        "緯來育樂台": "https://www.youtube.com/@maxtv71/videos",		
        "愛爾達綜合台": "https://www.youtube.com/@ELTAWORLD/streams",
        "愛爾達影劇台": "https://www.youtube.com/@eltadrama/streams",
        "VBL Series": "https://www.youtube.com/@variety_between_love/streams",
        "甄嬛传全集": "https://www.youtube.com/@LegendofConcubineZhenHuan/videos",		
        "精选大剧": "https://www.youtube.com/@精选大剧/videos",		
        "百纳经典独播剧场": "https://www.youtube.com/@BainationTVSeriesOfficial/streams",
        "华录百納熱播劇場": "https://www.youtube.com/@Baination/streams",	
        "iQIYI 爱奇艺": "https://www.youtube.com/@iQIYIofficial/streams",
        "iQIYI Show Giải Trí Vietnam": "https://www.youtube.com/@iQIYI_ShowGi%E1%BA%A3iTr%C3%ADVietnam/videos",		
        "iQIYI Indonesia": "https://www.youtube.com/@iQIYIIndonesia/streams",
        "爱奇艺大电影": "https://www.youtube.com/@iQIYIMOVIETHEATER/streams",
        "iQIYI 慢綜藝": "https://www.youtube.com/@iQIYILifeShow/streams",		
        "iQIYI 潮綜藝": "https://www.youtube.com/@iQIYISuperShow/streams",
        "iQIYI 爆笑宇宙": "https://www.youtube.com/@iQIYIHappyWorld/streams",		
        "MangoTV Shorts": "https://www.youtube.com/@MangoTVShorts/videos",
        "MangoTV English": "https://www.youtube.com/@MangoTVEnglishOfficial/videos",
        "MangoTV Malaysia": "https://www.youtube.com/@MangoTVMalaysia/streams",		
        "芒果TV古裝劇場": "https://www.youtube.com/@TVMangoTVCostume-yw1hj/videos",	
        "芒果TV青春剧场": "https://www.youtube.com/@MangoTVDramaOfficial/streams",	
        "芒果TV季风频道": "https://www.youtube.com/@MangoMonsoon/streams",	
        "芒果TV推理宇宙": "https://youtube.com/@mangotv-mystery?si=CRrdrZLRFBy4GXtQ",
        "芒果TV大電影劇場": "https://www.youtube.com/@MangoC-TheatreChannel/streams",
        "芒果TV心动": "https://www.youtube.com/@MangoTVSparkle/streams",	
        "CCTV电视剧": "https://www.youtube.com/@CCTVDrama/streams",	
        "SMG上海电视台官方频道": "https://www.youtube.com/@SMG-Official/streams",
        "SMG上海东方卫视欢乐频道": "https://www.youtube.com/@SMG-Comedy/streams",
        "SMG电视剧": "https://www.youtube.com/@SMGDrama/streams",
        "老广一起睇": "https://www.youtube.com/@老广一起睇/streams",		
        "安徽衛視官方頻道": "https://www.youtube.com/@chinaanhuitvofficialchanne8354/streams",	
        "中国东方卫视官方频道": "https://www.youtube.com/@SMGDragonTV/streams",
        "北京广播电视台官方频道": "https://www.youtube.com/@Brtvofficialchannel/streams",
        "贵州卫视官方频道": "https://www.youtube.com/@gztvofficial/streams",
        "喜剧大联盟": "https://www.youtube.com/@SuperComedyLeague/streams",
        "China Zone 古裝劇場": "https://www.youtube.com/@ChinaZoneCostume/streams",
        "China Zone 剧乐部": "https://www.youtube.com/@ChinaZoneDrama/streams",
        "China Zone 流金岁月": "https://www.youtube.com/@ChinaZone-ClassicDrama/streams",
        "China Zone梦想剧场": "https://www.youtube.com/@ChinaZone-DreamDrama/streams",		
        "欢娱影视官方频道": "https://www.youtube.com/@chinahuanyuent.officialchannel/streams",
        "乐视视频官方频道": "https://www.youtube.com/@letvdramas/streams",		
        "正午阳光官方频道": "https://www.youtube.com/@DaylightEntertainmentDrama/streams",		
        "超級影迷 正版電影免費看": "https://www.youtube.com/@MegaFilmLovers/streams",
        "電影想飛 正版電影免費看": "https://www.youtube.com/@moviesintheair/streams",
        "MadHouse 免費電影": "https://www.youtube.com/@MadHouseFreeMovie/streams",
        "FAST 免費電影": "https://www.youtube.com/@FASTMOVIE168/streams",		
        "SMG音乐频道": "https://www.youtube.com/@SMGMusic/streams"				
    },
    "少兒,#genre#": {
        "YOYOTV": "https://www.youtube.com/@yoyotvebc/streams",
        "momokids親子台": "https://www.youtube.com/@momokidsYT/streams",
        "Bebefinn 繁體中文 - 兒歌": "https://www.youtube.com/@Bebefinn繁體中文/streams",
        "寶貝多米-兒歌童謠-卡通動畫-經典故事": "https://www.youtube.com/@Domikids_CN/streams",
        "會說話的湯姆貓家族": "https://www.youtube.com/@TalkingFriendsCN/streams",
        "瑪莎與熊": "https://www.youtube.com/@MashaBearTAIWAN/streams",	
        "碰碰狐 鯊魚寶寶": "https://www.youtube.com/@Pinkfong繁體中文/streams",
        "碰碰狐 Pinkfong Baby Shark 儿歌·故事": "https://www.youtube.com/@Pinkfong简体中文/streams",	
        "寶寶巴士": "https://www.youtube.com/@BabyBusTC/streams",
        "Miliki Family - 繁體中文 - 兒歌": "https://www.youtube.com/@MilikiFamily_Chinese/streams",	
        "貝樂虎-幼兒動畫-早教启蒙": "https://www.youtube.com/@BarryTiger_Education_CN/streams",	
        "貝樂虎兒歌-童謠歌曲": "https://www.youtube.com/@barrytiger_kidssongs/streams",
        "貝樂虎-兒歌童謠-卡通動畫-經典故事": "https://www.youtube.com/@barrytiger_zh/streams",
        "小猪佩奇": "https://www.youtube.com/@PeppaPigChineseOfficial/streams",
        "Kids Songs - Giligilis": "https://www.youtube.com/@KidsSongs6868/streams",
        "超級汽車-卡通動畫": "https://www.youtube.com/@Supercar_Cartoon/streams",	
        "神奇鸡仔": "https://www.youtube.com/@como_cn/streams",
        "朱妮托尼 - 动画儿歌": "https://www.youtube.com/@JunyTonyCN/streams",	
        "Muse木棉花-TW": "https://www.youtube.com/@MuseTW/streams",	
        "Muse木棉花-闔家歡": "https://www.youtube.com/@Muse_Family/streams",
        "Ani-One中文官方動畫頻道": "https://www.youtube.com/@AniOneAnime/streams",
        "Lv.99 Animation Club": "https://www.youtube.com/@Lv.99AnimationClub/streams",
        "嘀嘀漫畫站": "https://www.youtube.com/@嘀嘀漫畫站DidiComic/streams",			
        "嗶哩嗶哩動畫Anime Made By Bilibili": "https://www.youtube.com/@MadeByBilibili/streams",	
        "回歸線娛樂": "https://www.youtube.com/@tropicsanime/streams",
        "愛奇藝國漫": "https://www.youtube.com/@iQIYIAnimation/streams",
        "艾瑪愛學習": "https://www.youtube.com/@EmmaLearning/streams",		
        "超人官方 YouTube 粵語頻道": "https://www.youtube.com/@ultraman_cantonese_official/streams"				
    },
    "體育,#genre#": {
        "愛爾達體育家族": "https://www.youtube.com/@ELTASPORTSHD/streams",
        "緯來體育台": "https://www.youtube.com/@vlsports/streams",
	    "公視體育": "https://www.youtube.com/@pts_sports/streams",
	    "getwin_sport": "https://www.youtube.com/@GetWinSport/streams",		
        "庫泊運動賽事": "https://www.youtube.com/@coopersport-live/streams",	
        "智林體育台": "https://www.youtube.com/@oursport_tv1/streams",
        "博斯體育台": "https://www.youtube.com/@Sportcasttw/streams",	
        "HOP Sports": "https://www.youtube.com/@HOPSports/streams",
        "DAZN 台灣": "https://www.youtube.com/@DAZNTaiwan/streams",	
        "動滋Sports": "https://www.youtube.com/@Sport_sa_taiwan/streams",
        "GoHoops": "https://www.youtube.com/@GoHoops/streams",
        "P.LEAGUE+": "https://www.youtube.com/@PLEAGUEofficial/streams",
        "TPBL": "https://www.youtube.com/@TPBL.Basketball/streams",		
        "CPBL 中華職棒": "https://www.youtube.com/@CPBL/streams",
        "CBC籃球聯盟": "https://www.youtube.com/@cbc726/streams",
        "MAX籃球聯盟": "https://www.youtube.com/@MAX-mv8mr/streams",		
        "TPVL 台灣職業排球聯盟": "https://www.youtube.com/@tpvl.official/streams",
        "籃海運動": "https://www.youtube.com/@pbe1772/streams",		
        "Body Sports  名衍行銷運動頻道": "https://www.youtube.com/@bodysports9644/streams",		
        "日本B聯盟": "https://www.youtube.com/@b.leagueinternational/streams",
        "MotoGP": "https://www.youtube.com/@motogp/streams",
        "The Savannah Bananas": "https://www.youtube.com/@TheSavannahBananas/streams",
        "WCW": "https://www.youtube.com/@WCW/streams",		
        "BattleBots": "https://www.youtube.com/@BattleBots/streams",
        "WWE": "https://www.youtube.com/@WWE/streams",
	    "WWE Vault": "https://www.youtube.com/@WWEVault/streams"   
    },
	"音樂,#genre#": {
	    "4kTQ-music": "https://www.youtube.com/@4kTQ-music/streams",	
	    "Eight无限": "https://www.youtube.com/@eight-audio/streams",
	    "相信音樂BinMusic": "https://www.youtube.com/@binmusictaipei/streams",
	    "周杰倫 Jay Chou": "https://www.youtube.com/@jaychou/streams",		
	    "Sony Music Entertainment Hong Kong": "https://www.youtube.com/@sonymusichk/streams",		
	    "Hot TV": "https://www.youtube.com/@hotfm976/streams",
	    "时间节拍 Melody": "https://www.youtube.com/@%E6%97%B6%E9%97%B4%E8%8A%82%E6%8B%8DMelody/streams",
	    "孤心旋律": "https://www.youtube.com/@GuXinXuanlu68/streams",		
	    "KKBOX 华语新歌周榜": "https://www.youtube.com/@KKBOX-baidu6868/streams",
	    "Douyin Chill": "https://www.youtube.com/@DouyinChill-xr2yk/streams",
	    "生活乐章": "https://www.youtube.com/@生活乐章/streams",	    
	    "抖音音樂台": "https://www.youtube.com/@douyinyinyuetai/streams",
	    "青春音乐铺": "https://www.youtube.com/@青春音乐铺/streams",
	    "水月琴音": "https://www.youtube.com/@Shuiyueqinyin/streams",	    
	    "Cherry 葵": "https://www.youtube.com/@Cherriexin/streams",
	    "Kanata Ch. 天音かなた": "https://www.youtube.com/@AmaneKanata/streams",		
	    "CMIX - Chill Mix": "https://www.youtube.com/@ChillMix-CMIX/streams",		
	    "「KING AMUSEMENT CREATIVE」公式チャンネル": "https://www.youtube.com/@KAC_official/streams",
	    "FOR FUN RADIO TIME Music channel": "https://www.youtube.com/@FORFUNRADIOTIME-Relax/streams",		
	    "Mellowbeat Seeker": "https://www.youtube.com/@mellowbeatseeker/streams",
	    "The Good Life Radio x Sensual Musique": "https://www.youtube.com/@TheGoodLiferadio/streams",	
        "Best of Mix": "https://www.youtube.com/@bestofmixlive/streams",
        "Rock FM": "https://www.youtube.com/@rockfm1/streams",
        "Radio Mix": "https://www.youtube.com/@liveradiomix/streams",
        "Too Music": "https://www.youtube.com/@toomusicc/streams",		
	    "Radio Hits Music": "https://www.youtube.com/@LiveMusicRadio/streams",
	    "Dark City Sounds": "https://www.youtube.com/@darkcitysounds/streams",
	    "Pop Japan Music": "https://www.youtube.com/@PopJapanMusic-du6su/streams",
	    "Tokyo Sound Rank": "https://www.youtube.com/@TokyoSoundRank98/streams",
	    "MEET48 Global": "https://www.youtube.com/@MEET48Global/streams",		
	    "KING AMUSEMENT CREATIVE": "https://www.youtube.com/@KAC_official/streams"		
    },	
    "政論,#genre#": {
        "壹電視NEXT TV": "https://www.youtube.com/@壹電視NEXTTV/streams",
        "庶民大頭家": "https://www.youtube.com/@庶民大頭家/streams",
        "TVBS 優選頻道": "https://www.youtube.com/@tvbschannel/streams",
        "街頭麥克風": "https://www.youtube.com/@street-mic/streams",
        "全球大視野": "https://www.youtube.com/@全球大視野Global_Vision/streams",
        "鄉民監察院": "https://www.youtube.com/@FTControlYuan/streams",		
        "民視讚夯": "https://www.youtube.com/@FTV_Forum/streams",
        "新台派上線": "https://www.youtube.com/@NewTaiwanonline/streams",	
        "94要客訴": "https://www.youtube.com/@94politics/streams",	
        "大新聞大爆卦": "https://www.youtube.com/@大新聞大爆卦HotNewsTalk/streams",	
        "新聞大白話": "https://www.youtube.com/@tvbstalk/streams",
        "國民大會": "https://www.youtube.com/@tvbscitizenclub/streams",	
        "中時新聞網": "https://www.youtube.com/@ChinaTimes/streams",
        "中天深喉嚨": "https://www.youtube.com/@ctitalkshow/streams",		
        "新聞挖挖哇！": "https://www.youtube.com/@newswawawa/streams",	
        "前進新台灣": "https://www.youtube.com/@SETTaiwanGo/streams",
        "哏傳媒": "https://www.youtube.com/@funseeTW/streams",
        "董事長開講": "https://www.youtube.com/@dongsshow/streams",
        "政經關不了": "https://www.youtube.com/@truevoiceoftaiwan/streams",			
        "57爆新聞": "https://www.youtube.com/@57BreakingNews/streams",
        "關鍵時刻": "https://www.youtube.com/@ebcCTime/streams",
		"郭正亮頻道": "https://www.youtube.com/@Guovision-TV/streams",
        "新聞龍捲風": "https://www.youtube.com/@新聞龍捲風NewsTornado/streams",		
        "頭條開講": "https://www.youtube.com/@頭條開講HeadlinesTalk/streams",		
	    "少康戰情室": "https://www.youtube.com/@tvbssituationroom/streams",
        "文茜的世界周報": "https://www.youtube.com/@tvbssisysworldnews/streams",
        "萬事通事務所": "https://www.youtube.com/@sciencewillwin/streams",		
        "中天深喉嚨": "https://www.youtube.com/@ctitalkshow/streams",
        "品觀點": "https://www.youtube.com/@pinviewmedia/streams",
        "52新聞聚樂部 ": "https://www.youtube.com/@52newsclub/streams",		
        "觀點": "https://www.youtube.com/@%E8%A7%80%E9%BB%9E/streams",		
        "金臨天下": "https://www.youtube.com/@tvbsmoney/streams"		
    },	
	"購物,#genre#": {
        "海豚多媒體": "https://www.youtube.com/@24811001/streams",
        "玉麟網路電視台": "https://www.youtube.com/@YuLinNetworkTelevision/streams",		
        "寶島文化台": "https://www.youtube.com/@bdtvbest/streams",
        "三聖電視台": "https://www.youtube.com/@tsimtv-01/streams",		
        "桐瑛台中電視臺": "https://www.youtube.com/@%E6%A1%90%E7%91%9B%E5%8F%B0%E4%B8%AD%E9%9B%BB%E8%A6%96%E8%87%BA/streams",
        "桐瑛虎尾電視臺": "https://www.youtube.com/@%E6%A1%90%E7%91%9B%E8%99%8E%E5%B0%BE%E9%9B%BB%E8%A6%96%E8%87%BA/streams",
        "桐瑛台南電視臺": "https://www.youtube.com/@%E6%A1%90%E7%91%9B%E5%8F%B0%E5%8D%97%E9%9B%BB%E8%A6%96%E8%87%BA/streams",		
        "momo購物一台": "https://www.youtube.com/@momoch4812/streams",
	    "momo購物二台": "https://www.youtube.com/@momoch3571/streams",
	    "ViVa TV美好家庭購物": "https://www.youtube.com/@ViVaTVtw/streams",
	    "Live東森購物台": "https://www.youtube.com/@HotsaleTV/streams"		
    },
    "國會,#genre#": {
        "國會頻道": "https://www.youtube.com/@parliamentarytv/streams"
    },
    "宗教,#genre#": {
        "淨土宗": "https://www.youtube.com/@plbtp/streams",
        "中華傳統文化教育中心": "https://www.youtube.com/@520wtv/streams",
        "修心時刻": "https://www.youtube.com/@Practicetime7/streams",
        "華藏衛視直播2台": "https://www.youtube.com/@hztv2212/streams",		
        "佛光山梵唄讚頌團": "https://www.youtube.com/@VG_MUSICAL/streams",
        "生命電視台": "https://www.youtube.com/@LIFETV_HaiTao/streams",		
        "遠東良友": "https://www.youtube.com/@febc/streams"		
    },
    "教育,#genre#": {	
        "龍騰高中聲": "https://www.youtube.com/@LTeduForStudent/streams",
        "Oziter茅": "https://www.youtube.com/@oziter/streams",		
        "ABC Learning English": "https://www.youtube.com/@ABCLearningEnglish/streams",		
        "學習粵語": "https://www.youtube.com/@CantoneseClass101/streams",
        "南非荷蘭語": "https://www.youtube.com/@AfrikaansPod101/streams",
        "學習印地語": "https://www.youtube.com/@hindipod101/streams",
        "學習菲律賓語": "https://www.youtube.com/@FilipinoPod101/streams",
        "學習烏爾都語": "https://www.youtube.com/@UrduPod101/streams",
        "學習德語": "https://www.youtube.com/@Germanpod101/streams",
        "學習土耳其語": "https://www.youtube.com/@TurkishClass101/streams",
        "學習阿拉伯語": "https://www.youtube.com/@ArabicPod101/streams",
        "學習瑞典語": "https://www.youtube.com/@SwedishPod101/streams",
        "學習挪威語": "https://www.youtube.com/@NorwegianClass101/streams",
        "學習希伯來語": "https://www.youtube.com/@HebrewPod101/streams",
        "學習希臘語": "https://www.youtube.com/@GreekPod101/streams",
        "學習波蘭語": "https://www.youtube.com/@PolishPod101/streams",
        "學習日文": "https://www.youtube.com/@JapanesePod101/streams",
        "學習中文": "https://www.youtube.com/@ChineseClass101/streams",
        "學習匈牙利語": "https://www.youtube.com/@HungarianPod101/streams",
        "學習芬蘭語": "https://www.youtube.com/@FinnishPod101/streams",
        "學習荷蘭語": "https://www.youtube.com/@DutchPod101/streams",
        "學習韓語": "https://www.youtube.com/@KoreanClass101/streams",
        "學習法語": "https://www.youtube.com/@frenchpod101/streams",		
        "學習波斯語": "https://www.youtube.com/@PersianPod101/streams"		
    },		
    "風景,#genre#": {
        "TW Live Cam": "https://www.youtube.com/@DanjiangBridge/streams",	
        "和平島公園即時影像": "https://www.youtube.com/@和平島公園即時影像/streams",
		"台北觀光即時影像": "https://www.youtube.com/@taipeitravelofficial/streams",
		"陽明山國家公園": "https://www.youtube.com/@ymsnpinfo/streams",
		"大新店有線電視": "https://www.youtube.com/@CGNEWS8888/streams",
		"新北旅客 New Taipei Tour": "https://www.youtube.com/@ntctour/streams",
		"紅樹林有線電視": "https://www.youtube.com/@紅樹林有線電視-h7k/streams",
		"necoast nsa": "https://www.youtube.com/@necoastnsa2903/streams",
		"野柳即時影像": "https://www.youtube.com/@野柳即時影像/streams",
		"遊桃園 Taoyuan Travel": "https://www.youtube.com/@TaoyuanTravel/streams",
		"雪霸國家公園 Shei-Pa National Park": "https://www.youtube.com/@spnp852/streams",
		"交通部觀光署-參山風管處": "https://www.youtube.com/@trimtnsa/streams",
		"大玩台中-臺中觀光旅遊局": "https://www.youtube.com/@大玩台中-臺中觀光旅/streams",
		"台灣即時影像監視器": "https://www.youtube.com/@twipcam/streams",
		"Amos YANG": "https://www.youtube.com/@feng52/streams",
		"國家森林遊樂區即時影像": "https://www.youtube.com/@fancarecreation/streams",
		"阿里山國家風景區管理處": "https://www.youtube.com/@Alishannsa/streams",
		"大台南新聞": "https://www.youtube.com/@大台南新聞南天地方新/streams",
		"內政部國家公園署台江國家公園管理處": "https://www.youtube.com/@taijiangnationalpark/streams",
		"高雄旅遊網": "https://www.youtube.com/@travelkhh/streams",
		"茂林國家風景區": "https://www.youtube.com/@茂林國家風景區/streams",
		"南喃夕語": "https://www.youtube.com/@thesouth.2022/streams",
		"ktnpworld": "https://www.youtube.com/@ktnpworld/streams",
		"斯爾本科技有限公司": "https://www.youtube.com/@Suburban-Security/streams",
		"花蓮縣政府觀光處七星潭風景區": "https://www.youtube.com/@花蓮縣政府觀光處七星/streams",
		"東部海岸國家風景管理處": "https://www.youtube.com/@eastcoastnsa0501/streams",
		"Amazing Taitung 台東就醬玩": "https://www.youtube.com/@taitungamazing7249/streams",
		"ervnsa": "https://www.youtube.com/@ervnsa/streams",
		"交通部觀光署澎湖國家風景區管理處": "https://www.youtube.com/@交通部觀光署澎湖國家/streams",		
		"樂遊金門": "https://www.youtube.com/@kinmentravel/streams",
		"馬祖國家風景區": "https://www.youtube.com/@matsunationalscenicarea9539/streams"		
    }
    # ... 您可以將之前的完整清單貼在此處
}

PPV_API_URL = "https://ppv.to/api/streams"
PPV_HEADERS = [
    '#EXTVLCOPT:http-origin=https://ppv.to',
    '#EXTVLCOPT:http-referrer=https://ppv.to/',
    '#EXTVLCOPT:http-user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101 Firefox/143.0'
]

# --- 工具函式：YouTube 直播抓取 ---
async def fetch_yt_live(client, name, channel_url, category):
    try:
        live_url = channel_url.replace("/streams", "/live")
        resp = await client.get(live_url, timeout=10)
        match = re.search(r'\"videoDetails\":\{\"videoId\":\"(.*?)\"', resp.text)
        if match and '\"isLive\":true' in resp.text:
            v_id = match.group(1)
            logo = f"https://img.youtube.com/vi/{v_id}/hqdefault.jpg"
            m3u = f'#EXTINF:-1 tvg-id="{name}" tvg-logo="{logo}" group-title="電視牆 - {category}",{name}\n'
            m3u += f'https://www.youtube.com/watch?v={v_id}'
            return m3u
    except:
        pass
    return None

# --- 工具函式：PPV 串流抓取 (Playwright) ---
async def grab_ppv_m3u8(page, iframe_url):
    found = []
    page.on("response", lambda res: found.append(res.url) if ".m3u8" in res.url else None)
    try:
        await page.goto(iframe_url, timeout=20000, wait_until="domcontentloaded")
        await asyncio.sleep(5)
        await page.locator("body").click(force=True) # 觸發播放
        await asyncio.sleep(5)
    except:
        pass
    return list(set(found))

# --- 主程式 ---
async def main():
    print(f"🚀 電視牆產生器啟動 | {datetime.now()}")
    all_entries = ["#EXTM3U"]

    # 1. 處理 YouTube 頻道 (速度快，使用 httpx)
    print("📺 正在抓取 YouTube 直播頻道...")
    async with httpx.AsyncClient(follow_redirects=True) as client:
        tasks = []
        for cat, channels in YOUTUBE_CHANNELS.items():
            for name, url in channels.items():
                tasks.append(fetch_yt_live(client, name, url, cat))
        
        yt_results = await asyncio.gather(*tasks)
        all_entries.extend([r for r in yt_results if r])

    # 2. 處理 PPV 體育頻道 (需要模擬瀏覽器)
    print("⚽ 正在抓取 PPV 體育串流 (啟動瀏覽器)...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 獲取 API 資料
        async with httpx.AsyncClient() as client:
            try:
                api_resp = await client.get(PPV_API_URL)
                streams_data = api_resp.json().get("streams", [])
            except:
                streams_data = []

        for cat_data in streams_data:
            cat_name = cat_data.get("category", "體育")
            for s in cat_data.get("streams", [])[:5]: # 範例限制前5個，避免過久
                name = s.get("name")
                iframe = s.get("iframe")
                print(f"  🔍 正在解析體育項目: {name}")
                
                m3u8_urls = await grab_ppv_m3u8(page, iframe)
                if m3u8_urls:
                    logo = s.get("poster") or ""
                    entry = f'#EXTINF:-1 tvg-id="{name}" tvg-logo="{logo}" group-title="體育 - {cat_name}",{name}\n'
                    for h in PPV_HEADERS: entry += h + "\n"
                    entry += m3u8_urls[0]
                    all_entries.append(entry)
        
        await browser.close()

    # 3. 儲存結果
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(all_entries))
    
    print(f"✅ 完成！清單已存至: {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
