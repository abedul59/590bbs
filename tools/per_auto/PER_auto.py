import pandas as pd
import requests
from bs4 import BeautifulSoup
import random
import datetime
import os
import time
import json
import io
import re
import sys

# ==============================================================================
# 設定與通用函式
# ==============================================================================

DASHBOARD_URL = "https://590bbs.vercel.app/macrowave?view=stock-dashboard"
UPLOAD_TARGETS = [
    ("原 Stock Dashboard", "https://stock-dashboard-nuxt.vercel.app/api/upload"),
    ("590bbs 總大六大指標和本益比區間分析", "https://590bbs.vercel.app/api/stock-dashboard/upload"),
]
REQUEST_TIMEOUT = (10, 30)

my_UserAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'

TSEAll = ['1101','1102','1103','1104','1108','1109','1110','1201','1203','1210','1213','1215','1216','1217','1218','1219','1220','1225','1227','1229','1231','1232','1233','1234','1235','1236','1256','1301','1303','1304','1305','1307','1308','1309','1310','1312','1313','1314','1315','1316','1319','1321','1323','1324','1325','1326','1337','1338','1339','1340','1341','1402','1409','1410','1413','1414','1416','1417','1418','1419','1423','1432','1434','1435','1436','1437','1438','1439','1440','1441','1442','1443','1444','1445','1446','1447','1449','1451','1452','1453','1454','1455','1456','1457','1459','1460','1463','1464','1465','1466','1467','1468','1470','1471','1472','1473','1474','1475','1476','1477','1503','1504','1506','1507','1512','1513','1514','1515','1516','1517','1519','1521','1522','1524','1525','1526','1527','1528','1529','1530','1531','1532','1533','1535','1536','1537','1538','1539','1540','1541','1558','1560','1568','1582','1583','1587','1589','1590','1592','1598','1603','1604','1605','1608','1609','1611','1612','1614','1615','1616','1617','1618','1626','1701','1702','1707','1708','1709','1710','1711','1712','1713','1714','1717','1718','1720','1721','1722','1723','1724','1725','1726','1727','1730','1731','1732','1733','1734','1735','1736','1737','1760','1762','1773','1776','1783','1786','1789','1795','1802','1805','1806','1808','1809','1810','1817','1903','1904','1905','1906','1907','1909','2002','2006','2007','2008','2009','2010','2012','2013','2014','2015','2017','2020','2022','2023','2024','2025','2027','2028','2029','2030','2031','2032','2033','2034','2038','2049','2059','2062','2069','2101','2102','2103','2104','2105','2106','2107','2108','2109','2114','2115','2201','2204','2206','2207','2208','2227','2228','2231','2233','2236','2239','2241','2243','2247','2301','2302','2303','2305','2308','2312','2313','2314','2316','2317','2321','2323','2324','2327','2328','2329','2330','2331','2332','2337','2338','2340','2342','2344','2345','2347','2348','2349','2351','2352','2353','2354','2355','2356','2357','2358','2359','2360','2362','2363','2364','2365','2367','2368','2369','2371','2373','2374','2375','2376','2377','2379','2380','2382','2383','2385','2387','2388','2390','2392','2393','2395','2397','2399','2401','2402','2404','2405','2406','2408','2409','2412','2413','2414','2415','2417','2419','2420','2421','2423','2424','2425','2426','2427','2428','2429','2430','2431','2433','2434','2436','2438','2439','2440','2441','2442','2443','2444','2448','2449','2450','2451','2453','2454','2455','2456','2457','2458','2459','2460','2461','2462','2464','2465','2466','2467','2468','2471','2472','2474','2476','2477','2478','2480','2481','2482','2483','2484','2485','2486','2488','2489','2491','2492','2493','2495','2496','2497','2498','2499','2501','2504','2505','2506','2509','2511','2514','2515','2516','2520','2524','2527','2528','2530','2534','2535','2536','2537','2538','2539','2540','2542','2543','2545','2546','2547','2548','2597','2601','2603','2605','2606','2607','2608','2609','2610','2611','2612','2613','2614','2615','2616','2617','2618','2630','2633','2634','2636','2637','2642','2701','2702','2704','2705','2706','2707','2712','2722','2723','2727','2731','2739','2748','2801','2809','2812','2816','2820','2823','2832','2834','2836','2838','2841','2845','2849','2850','2851','2852','2855','2867','2880','2881','2882','2883','2884','2885','2886','2887','2888','2889','2890','2891','2892','2897','2901','2903','2904','2905','2906','2908','2910','2911','2912','2913','2915','2923','2929','2936','2939','3002','3003','3004','3005','3006','3008','3010','3011','3013','3014','3015','3016','3017','3018','3019','3021','3022','3023','3024','3025','3026','3027','3028','3029','3030','3031','3032','3033','3034','3035','3036','3037','3038','3040','3041','3042','3043','3044','3045','3046','3047','3048','3049','3050','3051','3052','3054','3055','3056','3057','3058','3059','3060','3062','3090','3094','3130','3149','3164','3167','3189','3209','3229','3231','3257','3266','3296','3305','3308','3311','3312','3321','3338','3346','3356','3376','3380','3383','3406','3413','3416','3419','3432','3437','3443','3450','3454','3481','3494','3501','3504','3515','3518','3528','3530','3532','3533','3535','3536','3543','3545','3550','3557','3563','3576','3583','3588','3591','3593','3596','3605','3607','3617','3622','3645','3653','3661','3665','3669','3673','3679','3682','3686','3694','3698','3701','3702','3703','3704','3705','3706','3708','3711','3712','4104','4106','4108','4119','4133','4137','4141','4142','4148','4155','4164','4190','4306','4414','4426','4438','4439','4526','4532','4536','4540','4545','4551','4552','4555','4557','4560','4562','4564','4566','4571','4572','4576','4581','4720','4722','4725','4737','4739','4746','4755','4763','4764','4766','4807','4904','4906','4912','4915','4916','4919','4927','4930','4934','4935','4938','4942','4943','4952','4956','4958','4960','4961','4967','4968','4976','4977','4989','4994','4999','5007','5203','5215','5225','5234','5243','5258','5264','5269','5283','5284','5285','5288','5305','5388','5434','5469','5471','5484','5515','5519','5521','5522','5525','5531','5533','5534','5538','5546','5607','5608','5706','5871','5876','5880','5906','5907','6005','6024','6108','6112','6115','6116','6117','6120','6128','6131','6133','6136','6139','6141','6142','6152','6153','6155','6164','6165','6166','6168','6172','6176','6177','6183','6184','6189','6191','6192','6196','6197','6201','6202','6205','6206','6209','6213','6214','6215','6216','6224','6225','6226','6230','6235','6239','6243','6251','6257','6269','6271','6277','6278','6281','6282','6283','6285','6288','6289','6405','6409','6412','6414','6415','6416','6431','6442','6443','6449','6451','6456','6464','6477','6491','6504','6505','6525','6531','6533','6541','6552','6558','6573','6579','6581','6582','6591','6592','6598','6605','6625','6641','6655','6666','6668','6669','6670','6671','6672','6674','6698','6706','6715','6754','8011','8016','8021','8028','8033','8039','8046','8070','8072','8081','8101','8103','8104','8105','8110','8112','8114','8131','8150','8163','8201','8210','8213','8215','8222','8249','8261','8271','8341','8367','8374','8404','8411','8422','8427','8429','8442','8443','8454','8462','8463','8464','8466','8467','8473','8478','8480','8481','8482','8488','8499','8926','8940','8996','9105','912000','912398','9802','9902','9904','9905','9906','9907','9908','9910','9911','9912','9914','9917','9918','9919','9921','9924','9925','9926','9927','9928','9929','9930','9931','9933','9934','9935','9937','9938','9939','9940','9941','9942','9943','9944','9945','9946','9955','9958']
OTCAll = ['1240','1258','1259','1264','1268','1333','1336','1565','1569','1570','1580','1584','1586','1591','1593','1595','1597','1599','1742','1752','1777','1781','1784','1785','1788','1796','1799','1813','1815','2035','2061','2063','2064','2065','2066','2067','2070','2221','2230','2235','2596','2640','2641','2643','2718','2719','2724','2726','2729','2732','2734','2736','2740','2743','2745','2752','2754','2916','2924','2926','2928','2937','3064','3066','3067','3071','3073','3078','3081','3083','3085','3086','3088','3089','3092','3093','3095','3105','3114','3115','3118','3122','3128','3131','3141','3144','3147','3152','3162','3163','3169','3171','3176','3178','3188','3191','3202','3205','3206','3207','3211','3213','3217','3218','3219','3221','3224','3226','3227','3228','3230','3232','3234','3236','3252','3259','3260','3264','3265','3268','3272','3276','3284','3285','3287','3288','3289','3290','3293','3294','3297','3303','3306','3310','3313','3317','3322','3323','3324','3325','3332','3339','3354','3360','3362','3363','3372','3373','3374','3379','3388','3390','3402','3426','3434','3438','3441','3444','3455','3465','3466','3479','3483','3484','3489','3490','3491','3492','3498','3499','3508','3511','3512','3516','3520','3521','3522','3523','3526','3527','3529','3531','3537','3540','3541','3546','3548','3551','3552','3555','3556','3558','3564','3567','3570','3577','3580','3581','3587','3594','3597','3609','3611','3615','3623','3624','3625','3628','3629','3630','3631','3632','3642','3646','3652','3663','3664','3666','3672','3675','3680','3684','3685','3687','3689','3691','3693','3707','3709','3710','3713','4102','4105','4107','4109','4111','4113','4114','4116','4120','4121','4123','4126','4127','4128','4129','4130','4131','4138','4139','4147','4152','4153','4154','4157','4160','4161','4162','4163','4167','4168','4171','4173','4174','4175','4183','4188','4192','4198','4205','4207','4303','4304','4305','4401','4402','4406','4413','4416','4417','4419','4420','4429','4430','4432','4433','4502','4503','4506','4510','4513','4523','4527','4528','4529','4530','4533','4534','4535','4538','4541','4542','4543','4549','4550','4554','4556','4561','4563','4568','4580','4609','4702','4706','4707','4711','4712','4714','4716','4721','4726','4728','4729','4735','4736','4741','4743','4744','4745','4747','4754','4760','4767','4803','4804','4806','4903','4905','4907','4908','4909','4911','4924','4931','4933','4939','4944','4946','4950','4953','4966','4971','4972','4973','4974','4979','4987','4991','4995','5009','5011','5013','5014','5015','5016','5102','5201','5202','5205','5206','5209','5210','5211','5212','5213','5220','5223','5227','5230','5245','5251','5263','5272','5274','5276','5278','5281','5287','5289','5291','5299','5301','5302','5304','5306','5309','5310','5312','5314','5315','5321','5324','5328','5340','5344','5345','5347','5348','5351','5353','5355','5356','5364','5371','5381','5383','5386','5392','5398','5403','5410','5425','5426','5432','5438','5439','5443','5450','5452','5455','5457','5460','5464','5465','5468','5474','5475','5478','5481','5483','5487','5488','5489','5490','5493','5498','5508','5511','5512','5514','5516','5520','5523','5529','5530','5536','5543','5601','5603','5604','5609','5701','5703','5704','5820','5864','5878','5902','5903','5904','5905','6015','6016','6020','6021','6023','6026','6101','6103','6104','6109','6111','6113','6114','6118','6121','6122','6123','6124','6125','6126','6127','6129','6130','6134','6138','6140','6143','6144','6146','6147','6148','6150','6151','6154','6156','6158','6160','6161','6163','6167','6169','6170','6171','6173','6174','6175','6179','6180','6182','6185','6186','6187','6188','6190','6194','6195','6198','6199','6203','6204','6207','6208','6210','6212','6217','6218','6219','6220','6221','6222','6223','6227','6228','6229','6231','6233','6234','6236','6237','6240','6241','6242','6244','6245','6246','6247','6248','6259','6261','6263','6264','6265','6266','6270','6274','6275','6276','6279','6284','6287','6290','6291','6292','6294','6404','6411','6417','6418','6419','6425','6426','6432','6435','6438','6441','6446','6457','6461','6462','6465','6469','6470','6472','6482','6485','6486','6488','6492','6494','6496','6499','6506','6508','6509','6510','6512','6514','6516','6523','6527','6530','6532','6535','6538','6542','6547','6548','6556','6560','6561','6568','6569','6570','6574','6576','6577','6578','6588','6589','6590','6593','6594','6596','6603','6609','6612','6613','6615','6616','6624','6629','6640','6642','6643','6649','6654','6662','6664','6667','6679','6680','6683','6690','6697','6703','6716','6732','6803','7402','7556','8024','8027','8032','8034','8038','8040','8042','8043','8044','8047','8048','8049','8050','8054','8059','8064','8066','8067','8068','8069','8071','8074','8076','8077','8080','8083','8084','8085','8086','8087','8088','8089','8091','8092','8093','8096','8097','8099','8107','8109','8111','8121','8147','8155','8171','8176','8182','8183','8234','8240','8255','8277','8279','8284','8289','8291','8299','8342','8349','8354','8358','8383','8390','8401','8403','8406','8409','8410','8415','8416','8418','8420','8421','8423','8424','8426','8431','8432','8433','8435','8436','8437','8440','8444','8446','8450','8455','8472','8476','8477','8489','8905','8906','8908','8916','8917','8921','8923','8924','8927','8928','8929','8930','8931','8932','8933','8934','8935','8936','8937','8938','8941','8942','9949','9950','9951','9960','9962']

def get_headers():
    return {
        'Referer': 'https://tw.yahoo.com',
        'User-Agent': my_UserAgent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8'
    }

def build_source_urls(stock_id):
    """集中管理輸出 JSON 與網頁核對區使用的原始資料網址。"""
    return {
        'Revenue': f'https://djinfo.cathaysec.com.tw/z/zc/zch/zch_{stock_id}.djhtm',
        'FinancialRatios': f'https://djinfo.cathaysec.com.tw/z/zc/zcr/zcr_{stock_id}.djhtm',
        'QuarterlyIncome': f'https://djinfo.cathaysec.com.tw/z/zc/zcq/zcq_{stock_id}.djhtm',
        'QuarterlyCashFlow': f'https://djinfo.cathaysec.com.tw/z/zc/zc3/zc3_{stock_id}.djhtm',
        'AnnualEPS': f'https://djinfo.cathaysec.com.tw/z/zc/zcq/zcq0.djhtm?b=Y&a={stock_id}',
        'QuarterlyEPS': f'https://djinfo.cathaysec.com.tw/z/zc/zcq/zcq.djhtm?b=Y&a={stock_id}',
        'Capital': f'https://djinfo.cathaysec.com.tw/z/zc/zcp/zcpa_{stock_id}.djhtm',
        'TWSEAnnualPrice': f'https://www.twse.com.tw/exchangeReport/FMNPTK?response=html&stockNo={stock_id}',
        'TPEXAnnualPrice': 'https://www.tpex.org.tw/zh-tw/mainboard/trading/info/stock-year.html',
        'YahooQuote': f'https://tw.stock.yahoo.com/quote/{stock_id}',
    }

def fetch_soup(url, encoding='cp950'):
    try:
        r = requests.get(url, headers=get_headers(), timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        r.encoding = encoding
        return BeautifulSoup(r.text, 'html.parser')
    except requests.RequestException as exc:
        print(f"  - 讀取資料失敗 ({url}): {exc}")
        return None

def configure_working_directory():
    """讓雙擊 EXE、排程器與直接執行 Python 時都從程式所在目錄讀寫。"""
    program_path = sys.executable if getattr(sys, 'frozen', False) else __file__
    os.chdir(os.path.dirname(os.path.abspath(program_path)))

def safe_filename(value):
    """移除 Windows 檔名不允許的字元。"""
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', str(value)).strip(' .')
    return cleaned or "unknown"

def pause_console():
    if os.name == 'nt' and sys.stdin and sys.stdin.isatty():
        try:
            input("\n按 Enter 鍵結束...")
        except (EOFError, KeyboardInterrupt):
            pass

def upload_payload(payload, retries=3):
    """同步至所有後台；單一站台失敗不會阻擋其他站台。"""
    results = {}
    for target_name, upload_url in UPLOAD_TARGETS:
        last_error = "未知錯誤"
        for attempt in range(1, retries + 1):
            try:
                response = requests.post(
                    upload_url,
                    json=payload,
                    headers={'Content-Type': 'application/json'},
                    timeout=REQUEST_TIMEOUT,
                )
                response.raise_for_status()
                results[target_name] = True
                print(f"  - {target_name} 同步成功！")
                break
            except requests.RequestException as exc:
                last_error = str(exc)
                if attempt < retries:
                    print(f"  - {target_name} 第 {attempt} 次同步失敗，2 秒後重試: {exc}")
                    time.sleep(2)
        else:
            results[target_name] = False
            print(f"  - {target_name} 同步失敗（已重試 {retries} 次）: {last_error}")
    return results

def clean_float(val):
    try:
        raw = str(val).replace(',', '').replace('%', '').strip()
        if raw in ('-', '--', '', 'N/A', 'null', 'nan'): return 0.0
        is_negative = raw.startswith('(') and raw.endswith(')')
        raw = raw.strip('()')
        value = float(raw)
        return -value if is_negative else value
    except:
        return 0.0

RATING_SCORES = {'AA': 4, 'A': 3, 'BB': 2, 'B': 1, 'C': 0}

def split_row_values(row):
    return [value.strip() for value in row.get_text('\n').splitlines() if value.strip()]

def find_financial_series(soup, keywords, limit=8, excluded_keywords=()):
    """以欄名配對 MoneyDJ table-row，避免依固定列號造成資料錯位。"""
    rows = soup.find_all(class_='table-row') if soup else []
    if not rows:
        return []
    headers = split_row_values(rows[0])
    for row in rows[1:]:
        label = row.get_text(' ', strip=True)
        if all(keyword in label for keyword in keywords) and not any(keyword in label for keyword in excluded_keywords):
            values = split_row_values(row)
            count = min(limit, len(headers) - 1, len(values) - 1)
            return [(headers[index], clean_float(values[index])) for index in range(1, count + 1)]
    return []

def rate_revenue(values):
    recent = list(values[:6])
    if len(recent) < 6:
        return '不評分', '需要最近 6 個月營收年增率'
    average = sum(recent) / 6
    momentum = (recent[0] - recent[1]) / abs(recent[1]) if recent[1] else 0
    if average < 0 or recent[0] < 0:
        return 'C', '近 6 月平均或最新月營收年增率為負'
    if any(value < 0 for value in recent):
        return 'BB', '近 6 月曾出現負成長'
    if recent[0] < recent[1] < recent[2]:
        return 'B', '最近 3 個月營收年增率連續下降'
    if average > 25 and -0.5 <= momentum < 0:
        return 'A', '近 6 月平均逾 25%，最新月小幅放緩'
    if 10 <= average <= 25 and recent[0] >= recent[1]:
        return 'A', '近 6 月皆正成長、平均 10%～25% 且動能未降'
    if average > 25 and recent[0] >= recent[1]:
        return 'AA', '近 6 月皆正成長、平均逾 25% 且動能未降'
    return 'BB', '維持正成長，但未達 A 級條件'

def rate_operating_margin(values):
    recent = list(values[:4])
    if len(recent) < 4:
        return '不評分', '需要最近 4 季營業利益率'
    average = sum(recent) / 4
    changes = [
        (recent[index] - recent[index + 1]) / abs(recent[index + 1]) if recent[index + 1] else 0
        for index in range(3)
    ]
    if recent[0] < 0 or average < 0:
        return 'C', '最新季或近 4 季平均營業利益率為負'
    if average <= 5 or changes[0] <= -0.2:
        return 'B', '近 4 季平均不逾 5%，或最新季衰退逾 20%'
    if changes[1] <= -0.2 or changes[2] <= -0.2:
        return 'BB', '近 4 季曾出現單季衰退逾 20%'
    stable = all(recent[index] > recent[index + 1] * 0.8 for index in range(3))
    if average > 15 and stable:
        return 'AA', '近 4 季平均逾 15% 且維持穩定'
    if 10 <= average <= 15 and recent[0] > recent[1] and stable:
        return 'AA', '近 4 季平均 10%～15%、穩定且最新季上升'
    if (10 <= average <= 15 and stable) or (5 < average < 10 and recent[0] > recent[1] and stable):
        return 'A', '營業利益率維持穩定'
    return 'BB', '未達穩定成長條件'

def calculate_yoy(values):
    return [
        (values[index] - values[index + 4]) / abs(values[index + 4]) if values[index + 4] else 0
        for index in range(4)
    ] if len(values) >= 8 else []

def rate_net_income(values):
    yoy = calculate_yoy(values)
    if len(yoy) < 4:
        return '不評分', '需要最近 8 季稅後淨利', yoy
    negatives = sum(value < 0 for value in yoy)
    if yoy[0] < 0 and yoy[1] < 0:
        rating, reason = 'C', '最近 2 季稅後淨利年增率為負'
    elif (yoy[0] < yoy[1] < yoy[2] and yoy[0] < 0.5) or yoy[0] < 0 or negatives >= 2:
        rating, reason = 'B', '稅後淨利成長轉弱或近 4 季至少 2 季衰退'
    elif yoy[0] > 0 and yoy[1] > 0 and yoy[2] > 0 and yoy[0] > yoy[1]:
        rating, reason = 'AA', '近 3 季皆正成長且最新季加速'
    elif yoy[0] >= 0.5 and yoy[1] >= 0.5 and yoy[2] >= 0.5:
        rating, reason = 'AA', '近 3 季年增率皆達 50%'
    elif yoy[0] > 0 and yoy[1] > 0 and (yoy[0] - yoy[1]) / yoy[1] > -0.5:
        rating, reason = 'A', '近 2 季皆正成長且未大幅衰退'
    elif yoy[1] < 0 < yoy[0]:
        rating, reason = 'BB', '最新季由負轉正'
    else:
        rating, reason = 'BB', '仍為正成長但動能偏弱'
    return rating, reason, yoy

def rate_eps(values):
    if len(values) < 4:
        return '不評分', '需要最近 4 季 EPS', 0.0
    trailing_eps = round(sum(values[:4]), 2)
    if trailing_eps < 0:
        rating, reason = 'C', '近 4 季 EPS 累積虧損'
    elif values[0] < 0 or trailing_eps < 1:
        rating, reason = 'B', '最新季虧損或近 4 季 EPS 未滿 1 元'
    elif trailing_eps <= 3:
        rating, reason = 'BB', '近 4 季 EPS 為 1～3 元'
    elif trailing_eps <= 5:
        rating, reason = 'A', '近 4 季 EPS 為 3～5 元'
    else:
        rating, reason = 'AA', '近 4 季 EPS 超過 5 元'
    return rating, reason, trailing_eps

def rate_inventory_turnover(values):
    recent = list(values[:5])
    if len(recent) < 4 or any(value <= 0 for value in recent[:4]):
        return '不評分', '存貨週轉率不適用或資料不足', 0.0
    average = sum(recent[:4]) / 4
    changes = [(recent[index] - recent[index + 1]) / recent[index + 1] for index in range(3)]
    if changes[0] <= -0.2:
        rating, reason = 'C', '最新季存貨週轉率下降逾 20%'
    elif changes[1] <= -0.2 or changes[2] <= -0.2:
        rating, reason = 'B', '近 4 季曾出現單季下降逾 20%'
    elif changes[0] < 0 and changes[1] < 0 and (recent[0] - recent[2]) / recent[2] <= -0.2:
        rating, reason = 'BB', '連續 2 季下降且累計逾 20%'
    elif average >= 1.5 and all(change > -0.2 for change in changes):
        rating, reason = 'AA', '近 4 季穩定且平均週轉率達 1.5 次'
    elif all(change > -0.2 for change in changes):
        rating, reason = 'A', '近 4 季週轉率穩定'
    else:
        rating, reason = 'BB', '週轉率波動，未達穩定條件'
    return rating, reason, average

def rate_free_cash_flow(values):
    recent = list(values[:6])
    if len(recent) < 6:
        return '不評分', '需要最近 6 季自由現金流', 0.0, 0.0
    sum4, sum6 = sum(recent[:4]), sum(recent)
    if sum4 < 0 and sum6 < 0:
        rating, reason = 'C', '近 4 季與近 6 季自由現金流皆為負'
    elif sum4 < 0 <= sum6:
        rating, reason = 'B', '近 6 季為正，但近 4 季轉負'
    elif sum4 >= 0 > sum6:
        rating, reason = 'BB', '近 4 季轉正，但近 6 季仍為負'
    elif all(value > 0 for value in recent):
        rating, reason = 'AA', '連續 6 季自由現金流為正'
    else:
        rating, reason = 'A', '近 4 季與近 6 季自由現金流累積為正'
    return rating, reason, sum4, sum6

def average_rating(ratings):
    scores = [RATING_SCORES[rating] for rating in ratings if rating in RATING_SCORES]
    return round(sum(scores) / len(scores), 2) if scores else 0.0

def determine_forecast_year(current_year, current_month, target_month):
    """9 月起改用下一年度 forward EPS，回傳應估值的西元年度。"""
    try:
        effective_month = max(int(current_month), int(target_month))
    except (TypeError, ValueError):
        effective_month = int(current_month)
    return int(current_year) + (1 if effective_month >= 9 else 0)

def calculate_revenue_forecast(monthly_revenues, growth_rate, target_month, forecast_next_year):
    """先補齊本年度營收；若估值年度已切換，再外推下一年度營收。"""
    values = [clean_float(value) for value in list(monthly_revenues)[:12]]
    values.extend([0.0] * (12 - len(values)))
    month = min(12, max(1, int(target_month)))
    growth_factor = 1 + float(growth_rate)
    current_year_estimate = sum(values[:month]) + sum(values[month:12]) * growth_factor
    forecast_revenue = current_year_estimate * growth_factor if forecast_next_year else current_year_estimate
    return round(current_year_estimate, 4), round(forecast_revenue, 4)

def calculate_eps_forecast(revenue, net_margin, capital_stock):
    """EPS = 稅後淨利 ÷ 股數；億元口徑下需乘以 10。"""
    capital = clean_float(capital_stock)
    if capital <= 0:
        return 0.0
    return round(clean_float(revenue) * float(net_margin) / capital * 10, 2)

def get_stock_name_robust(stock_id):
    """強化版：多重備援機制抓取股票名稱"""
    stock_str = str(stock_id)
    headers = get_headers()
    try:
        url = f'https://djinfo.cathaysec.com.tw/z/zc/zca/zca_{stock_id}.djhtm'
        r = requests.get(url, headers=headers, timeout=5)
        r.encoding = 'cp950'
        soup = BeautifulSoup(r.text, 'html.parser')
        if soup and soup.title:
            txt = soup.title.string
            if txt and stock_str in txt:
                part1 = txt.split('-')[0].strip()
                name = part1.replace(stock_str, '').strip()
                if name and "個股基本資料" not in name: return name
    except: pass

    try:
        url_y = f'https://tw.stock.yahoo.com/quote/{stock_id}'
        r_y = requests.get(url_y, headers=headers, timeout=5)
        soup_y = BeautifulSoup(r_y.text, 'html.parser')
        if soup_y and soup_y.title:
            txt = soup_y.title.string
            if '(' in txt:
                name = txt.split('(')[0].strip()
                if name: return name
    except: pass

    return str(stock_id)

def get_latest_price(stock_id):
    """先取 Yahoo chart 即時/最近收盤價，再以舊站頁面作備援。"""
    suffixes = ('.TW',) if stock_id in TSEAll else ('.TWO', '.TW')
    for suffix in suffixes:
        try:
            response = requests.get(
                f'https://query1.finance.yahoo.com/v8/finance/chart/{stock_id}{suffix}',
                headers=get_headers(),
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            result = response.json().get('chart', {}).get('result') or []
            if result:
                meta = result[0].get('meta', {})
                price = clean_float(meta.get('regularMarketPrice') or meta.get('previousClose'))
                if price > 0:
                    return price
        except (requests.RequestException, ValueError, TypeError, AttributeError):
            pass

    try:
        response = requests.post(
            f'https://stock.wearn.com/a{stock_id}.html',
            headers=get_headers(),
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        for item in soup.find_all('ul'):
            if '成交價' in item.get_text(' ', strip=True):
                values = item.find_all('li')
                if values:
                    price = clean_float(values[0].get_text(strip=True))
                    if price > 0:
                        return price
    except requests.RequestException:
        pass
    return 0.0

# ==============================================================================
# 分析模組：六大指標 (前置，供PERsegx使用，以便抓取最新4Q資訊)
# ==============================================================================
def Stock6x_Analysis(stock_id):
    data = {'Name': get_stock_name_robust(stock_id)}
    sources = build_source_urls(stock_id)

    rev_result = {'Label': '營收年增率', 'Rating': '不評分', 'Data': [], 'Extra': {}}
    revenue_soup = fetch_soup(f'https://djinfo.cathaysec.com.tw/z/zc/zch/zch_{stock_id}.djhtm', 'cp950')
    try:
        if revenue_soup:
            dataframes = pd.read_html(io.StringIO(str(revenue_soup)))
            revenue_table = dataframes[2]
            revenue_growth = []
            for index in range(12):
                value = clean_float(revenue_table.iloc[6 + index, 4])
                revenue_growth.append(value)
                rev_result['Data'].append({
                    'Name': str(revenue_table.iloc[6 + index, 0]),
                    'Val': f"{value:.2f}%",
                })
            rating, reason = rate_revenue(revenue_growth)
            rev_result['Rating'] = rating
            rev_result['Reason'] = reason
            rev_result['Extra']['Avg6'] = f"{sum(revenue_growth[:6]) / 6:.2f}%"
            rev_result['Extra']['AccYoY'] = f"{clean_float(revenue_table.iloc[6, 6]):.2f}%"
    except (IndexError, ValueError, TypeError) as exc:
        rev_result['Reason'] = f"營收資料解析失敗：{exc}"
    data['Rev'] = rev_result
    data['Rev']['Formula'] = 'Avg6＝近6月YoY合計÷6；AA＝Avg6>25%且最新月未降，A＝Avg6 10%～25%且未降（或>25%僅小降），負成長依程度降為BB/C'
    data['Rev']['SourceURL'] = sources['Revenue']

    ratio_soup = fetch_soup(f'https://djinfo.cathaysec.com.tw/z/zc/zcr/zcr_{stock_id}.djhtm', 'cp950')
    operating_series = find_financial_series(ratio_soup, ('營業利益率',))
    operating_values = [value for _, value in operating_series]
    op_rating, op_reason = rate_operating_margin(operating_values)
    data['Op'] = {
        'Label': '營業利益率',
        'Rating': op_rating,
        'Reason': op_reason,
        'Data': [{'Name': name, 'Val': f"{value:.2f}%"} for name, value in operating_series],
        'Extra': {'Avg4': f"{sum(operating_values[:4]) / 4:.2f}%"} if len(operating_values) >= 4 else {},
        'Formula': 'Avg4＝近4季營益率÷4；季變動＝(本季－前季)÷|前季|；AA＝Avg4>15%且穩定，單季衰退≥20%依時點降為B/BB，負值為C',
        'SourceURL': sources['FinancialRatios'],
    }

    income_soup = fetch_soup(f'https://djinfo.cathaysec.com.tw/z/zc/zcq/zcq_{stock_id}.djhtm', 'cp950')
    net_series = find_financial_series(income_soup, ('稅後淨利',), excluded_keywords=('歸屬',))
    if not net_series:
        net_series = find_financial_series(income_soup, ('稅後淨利',))
    net_values = [value for _, value in net_series]
    net_rating, net_reason, net_yoy = rate_net_income(net_values)
    data['Net'] = {
        'Label': '稅後淨利年增率',
        'Rating': net_rating,
        'Reason': net_reason,
        'Data': [
            {
                'Name': name,
                'Val': f"{value:,.0f}",
                'YoY': f"{net_yoy[index] * 100:.2f}%" if index < len(net_yoy) else '-',
            }
            for index, (name, value) in enumerate(net_series)
        ],
        'Extra': {'LatestYoY': f"{net_yoy[0] * 100:.2f}%"} if net_yoy else {},
        'Formula': 'YoY＝(本季淨利－去年同季)÷|去年同季|；近3季正成長且最新加速為AA，連續衰退依程度為B/C',
        'SourceURL': sources['QuarterlyIncome'],
    }

    eps_series = find_financial_series(income_soup, ('每股盈餘',))
    if not eps_series:
        eps_series = find_financial_series(income_soup, ('EPS',))
    eps_values = [value for _, value in eps_series]
    eps_rating, eps_reason, trailing_eps = rate_eps(eps_values)
    data['EPS'] = {
        'Label': '近四季 EPS',
        'Rating': eps_rating,
        'Reason': eps_reason,
        'Data': [{'Name': name, 'Val': str(value)} for name, value in eps_series],
        'Extra': {'Trailing4Q': trailing_eps},
        'Formula': 'TTM EPS＝最近4季EPS合計；>5為AA、3～5為A、1～3為BB、<1或最新虧損為B、TTM虧損為C',
        'SourceURL': sources['QuarterlyIncome'],
    }

    inventory_series = find_financial_series(ratio_soup, ('存貨', '週轉'))
    if not inventory_series:
        inventory_series = find_financial_series(ratio_soup, ('存貨',))
    inventory_values = [value for _, value in inventory_series]
    inventory_rating, inventory_reason, inventory_average = rate_inventory_turnover(inventory_values)
    data['Inv'] = {
        'Label': '存貨週轉率',
        'Rating': inventory_rating,
        'Reason': inventory_reason,
        'Data': [{'Name': name, 'Val': str(value)} for name, value in inventory_series],
        'Extra': {'Avg4': round(inventory_average, 2)},
        'Formula': '季變動＝(本季週轉率－前季)÷前季；穩定且Avg4≥1.5為AA、穩定但<1.5為A，下降20%以上依時點為B/C',
        'SourceURL': sources['FinancialRatios'],
    }

    cash_soup = fetch_soup(f'https://djinfo.cathaysec.com.tw/z/zc/zc3/zc3_{stock_id}.djhtm', 'cp950')
    operating_cash = find_financial_series(cash_soup, ('營業活動', '現金'))
    if not operating_cash:
        operating_cash = find_financial_series(cash_soup, ('營運', '現金'))
    investing_cash = find_financial_series(cash_soup, ('投資活動', '現金'))
    cash_count = min(len(operating_cash), len(investing_cash))
    free_cash_series = [
        (operating_cash[index][0], operating_cash[index][1] + investing_cash[index][1])
        for index in range(cash_count)
    ]
    free_cash_values = [value for _, value in free_cash_series]
    cash_rating, cash_reason, cash_sum4, cash_sum6 = rate_free_cash_flow(free_cash_values)
    data['CF'] = {
        'Label': '自由現金流',
        'Rating': cash_rating,
        'Reason': cash_reason,
        'Data': [{'Name': name, 'Val': f"{value:,.0f}"} for name, value in free_cash_series],
        'Extra': {'Sum4': round(cash_sum4, 2), 'Sum6': round(cash_sum6, 2)},
        'Formula': '每季自由現金流＝營業現金流＋投資現金流；連6季正為AA，4季與6季累計皆正為A，轉正/轉負為BB/B，兩者皆負為C',
        'SourceURL': sources['QuarterlyCashFlow'],
    }

    ratings = [data[key]['Rating'] for key in ('Rev', 'Op', 'Net', 'EPS', 'Inv', 'CF')]
    data['Average'] = str(average_rating(ratings))
    data['ScoredCount'] = sum(rating in RATING_SCORES for rating in ratings)
    data['Scale'] = '0～4'
    data['Sources'] = sources
    return data

# ==============================================================================
# PERsegx (動態季別名稱與跨年度 forward EPS 估值)
# ==============================================================================
def PERsegx(stock_id, month_id, six_data):
    headers = get_headers()
    sources = build_source_urls(stock_id)

    now = datetime.datetime.now()
    current_year_ad = now.year
    current_year_roc = current_year_ad - 1911
    last_year_ad = current_year_ad - 1
    last_year_roc = current_year_roc - 1
    forecast_year_ad = determine_forecast_year(current_year_ad, now.month, month_id)
    forecast_year_roc = forecast_year_ad - 1911
    forecast_next_year = forecast_year_ad > current_year_ad

    deadline_date = datetime.datetime(current_year_ad, 3, 31)
    is_before_deadline = now < deadline_date

    H0=H1=H2=H3=H4=H5=H6=0.0; L0=L1=L2=L3=L4=L5=L6=0.0
    eps1=eps2=eps3=eps4=eps5=0.0; eps1N = "Unknown"
    xEPSList = []
    xYearSeasonTitleList = []
    PER_H1=PER_L1=PER_H2=PER_L2=PER_H3=PER_L3=PER_H4=PER_L4=PER_H5=PER_L5=0
    PER_H_average=PER_L_average=PER_H=PER_L=0

    use_estimation = True; detect_reason = "初始化"
    found_4Q_text = False; latest_quarter_str = "未偵測"

    stock_name = get_stock_name_robust(stock_id)

    # 1. 檢查財報狀態 (結合六大指標 EPS 最新季別進行確認)
    try:
        if len(six_data['EPS']['Data']) > 0:
            latest_quarter_str = six_data['EPS']['Data'][0]['Name']
            if f"{last_year_ad}.4Q" in latest_quarter_str:
                found_4Q_text = True
    except: pass

    if found_4Q_text:
        use_estimation = False; detect_reason = f"財報已發現 [{last_year_ad}.4Q]，採用實際值。"
    elif not is_before_deadline:
        use_estimation = True; detect_reason = "已過3/31但財報未見，強制估算。"
    else:
        use_estimation = True; detect_reason = "目前為3/31前，年報未公佈，採用估算。"

    # 2. 抓取股價 (TSE/OTC)
    if stock_id in TSEAll:  # 上市
        try:
            url = f'http://www.twse.com.tw/exchangeReport/FMNPTK?response=html&stockNo={stock_id}'
            r = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            r.raise_for_status()
            soup = BeautifulSoup(r.content, 'html.parser')
            tables = soup.find_all('table')
            if tables:
                dfs = pd.read_html(io.StringIO(str(tables[0])))
                if len(dfs) > 0 and len(dfs[0]) > 0:
                    df = dfs[0]
                    last_row_year = int(df.iloc[-1].iloc[0])
                    start_idx = -2 if last_row_year == current_year_roc else -1

                    if last_row_year == current_year_roc:
                        try:
                            H0 = clean_float(df.iloc[-1].iloc[4])
                            L0 = clean_float(df.iloc[-1].iloc[6])
                        except: pass
                    try:
                        if len(df) >= abs(start_idx):   r1 = df.iloc[start_idx];   H1=float(r1.iloc[4]); L1=float(r1.iloc[6])
                        if len(df) >= abs(start_idx-1): r2 = df.iloc[start_idx-1]; H2=float(r2.iloc[4]); L2=float(r2.iloc[6])
                        if len(df) >= abs(start_idx-2): r3 = df.iloc[start_idx-2]; H3=float(r3.iloc[4]); L3=float(r3.iloc[6])
                        if len(df) >= abs(start_idx-3): r4 = df.iloc[start_idx-3]; H4=float(r4.iloc[4]); L4=float(r4.iloc[6])
                        if len(df) >= abs(start_idx-4): r5 = df.iloc[start_idx-4]; H5=float(r5.iloc[4]); L5=float(r5.iloc[6])
                        if len(df) >= abs(start_idx-5): r6 = df.iloc[start_idx-5]; H6=float(r6.iloc[4]); L6=float(r6.iloc[6])
                    except: pass
        except: pass

    else:    # 上櫃
        try:
            tpex_url = "https://www.tpex.org.tw/www/zh-tw/statistics/yearlyStock"
            payload = {'code': stock_id, 'id': '', 'response': 'json'}
            api_headers = {'User-Agent': my_UserAgent, 'Origin': 'https://www.tpex.org.tw', 'Referer': 'https://www.tpex.org.tw/zh-tw/mainboard/trading/info/stock-year.html'}
            r_tpex = requests.post(tpex_url, data=payload, headers=api_headers, timeout=REQUEST_TIMEOUT)

            if r_tpex.status_code == 200:
                data = r_tpex.json()
                if 'tables' in data and len(data['tables']) > 0:
                    raw_data = data['tables'][0]['data']
                    df = pd.DataFrame(raw_data)
                    for col in [5, 7]:
                        df[col] = df[col].astype(str).str.replace(',', '').str.replace('--', '0')
                    df = df.sort_values(by=0, ascending=False).reset_index(drop=True)

                    first_year = int(df.iloc[0].iloc[0])
                    start_idx = 1 if first_year == current_year_roc else 0

                    if first_year == current_year_roc:
                        try:
                            H0 = clean_float(df.iloc[0].iloc[5])
                            L0 = clean_float(df.iloc[0].iloc[7])
                        except: pass
                    try:
                        if len(df) > start_idx:   r1 = df.iloc[start_idx];   H1 = float(r1.iloc[5]); L1 = float(r1.iloc[7])
                        if len(df) > start_idx+1: r2 = df.iloc[start_idx+1]; H2 = float(r2.iloc[5]); L2 = float(r2.iloc[7])
                        if len(df) > start_idx+2: r3 = df.iloc[start_idx+2]; H3 = float(r3.iloc[5]); L3 = float(r3.iloc[7])
                        if len(df) > start_idx+3: r4 = df.iloc[start_idx+3]; H4 = float(r4.iloc[5]); L4 = float(r4.iloc[7])
                        if len(df) > start_idx+4: r5 = df.iloc[start_idx+4]; H5 = float(r5.iloc[5]); L5 = float(r5.iloc[7])
                        if len(df) > start_idx+5: r6 = df.iloc[start_idx+5]; H6 = float(r6.iloc[5]); L6 = float(r6.iloc[7])
                    except: pass
        except: pass

    # 3. 取得歷年 EPS
    try:
        bank_url0 = 'https://djinfo.cathaysec.com.tw/z/zc/zcq/zcq0.djhtm?b=Y&a='
        url = bank_url0 + stock_id
        r = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        soup = BeautifulSoup(r.content, 'html.parser')
        table2 = soup.find_all(class_ = 'table-row')
        if table2:
            xYearSeasonTitle = table2[0].text.split("\n")
            xYearSeasonTitleList = [x for x in xYearSeasonTitle if x.strip()]
            xEPS = ""
            for row in table2:
                if "EPS" in row.text or "每股盈餘" in row.text:
                        xEPS = row.text; break
            if not xEPS: xEPS = table2[-1].text
            xEPSList = [x for x in xEPS.split("\n") if x.strip()]
            if len(xYearSeasonTitleList) > 2: eps1N = xYearSeasonTitleList[1]
    except: pass

    def safe_eps(val):
        try: return float(str(val).replace(',',''))
        except: return 0.0

    eps1 = safe_eps(xEPSList[2]) if len(xEPSList) > 2 else 0.0
    eps2 = safe_eps(xEPSList[3]) if len(xEPSList) > 3 else 0.0
    eps3 = safe_eps(xEPSList[4]) if len(xEPSList) > 4 else 0.0
    eps4 = safe_eps(xEPSList[5]) if len(xEPSList) > 5 else 0.0
    eps5 = safe_eps(xEPSList[6]) if len(xEPSList) > 6 else 0.0

    # 4. 季報 EPS (動態取得季別名稱)
    epsq1=epsq2=epsq3=0.0; epsq1N = "最新季"; epsq2N = "前一季"; epsq3N = "前二季";
    try:
        url_q = 'https://djinfo.cathaysec.com.tw/z/zc/zcq/zcq.djhtm?b=Y&a=' + stock_id
        r = requests.get(url_q, headers=headers, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        soup = BeautifulSoup(r.content, 'html.parser')
        table2 = soup.find_all(class_ = 'table-row')
        if len(table2) > 0:
            title_list = [x for x in table2[0].text.split("\n") if x.strip()]
            if len(title_list) > 1: epsq1N = title_list[1]
            if len(title_list) > 2: epsq2N = title_list[2]
            if len(title_list) > 3: epsq3N = title_list[3]

            xqEPSList = []
            for row in table2:
                if "EPS" in row.text or "每股盈餘" in row.text:
                    xqEPSList = [x for x in row.text.split("\n") if x.strip()]
                    break
            if not xqEPSList:
                xqEPSList = [x for x in table2[-1].text.split("\n") if x.strip()]

            if len(xqEPSList) > 1: epsq1 = safe_eps(xqEPSList[1])
            if len(xqEPSList) > 2: epsq2 = safe_eps(xqEPSList[2])
            if len(xqEPSList) > 3: epsq3 = safe_eps(xqEPSList[3])
    except: pass

    # 若 4Q 已出，強制把 eps1 替換為最新四季 EPS 加總 (確保數據最準確)
    if not use_estimation and found_4Q_text:
        try:
            eps_data = six_data['EPS']['Data']
            if len(eps_data) >= 4:
                eps1 = round(sum([float(x['Val']) for x in eps_data[:4]]), 2)
                eps1N = str(last_year_ad)
        except: pass

    # 5. PER 計算
    if eps1N == str(current_year_ad - 1):
        PER_H1 = round(H1/eps1,2) if eps1>0 else 0; PER_L1 = round(L1/eps1,2) if eps1>0 else 0
        PER_H2 = round(H2/eps2,2) if eps2>0 else 0; PER_L2 = round(L2/eps2,2) if eps2>0 else 0
        PER_H3 = round(H3/eps3,2) if eps3>0 else 0; PER_L3 = round(L3/eps3,2) if eps3>0 else 0
        PER_H4 = round(H4/eps4,2) if eps4>0 else 0; PER_L4 = round(L4/eps4,2) if eps4>0 else 0
        PER_H5 = round(H5/eps5,2) if eps5>0 else 0; PER_L5 = round(L5/eps5,2) if eps5>0 else 0
    else:
        PER_H1 = round(H2/eps1,2) if eps1>0 else 0; PER_L1 = round(L2/eps1,2) if eps1>0 else 0
        PER_H2 = round(H3/eps2,2) if eps2>0 else 0; PER_L2 = round(L3/eps2,2) if eps2>0 else 0
        PER_H3 = round(H4/eps3,2) if eps3>0 else 0; PER_L3 = round(L4/eps3,2) if eps3>0 else 0
        PER_H4 = round(H5/eps4,2) if eps4>0 else 0; PER_L4 = round(L5/eps4,2) if eps4>0 else 0
        PER_H5 = round(H6/eps5,2) if eps5>0 else 0; PER_L5 = round(L6/eps5,2) if eps5>0 else 0

    avgs_h = [x for x in [PER_H1, PER_H2, PER_H3, PER_H4, PER_H5] if x > 0]
    avgs_l = [x for x in [PER_L1, PER_L2, PER_L3, PER_L4, PER_L5] if x > 0]
    PER_H_average = round(sum(avgs_h)/len(avgs_h), 2) if avgs_h else 0
    PER_L_average = round(sum(avgs_l)/len(avgs_l), 2) if avgs_l else 0
    PER_H = min(PER_H_average, PER_H1) if PER_H1>0 else PER_H_average
    PER_L = min(PER_L_average, PER_L1) if PER_L1>0 else PER_L_average

    # 6. 營收與預估
    Rev_Predict = 0; Rev_Current_Year_Est = 0; RevYoY = 0; Q4_Rev_Actual = 0
    Rev_names = []; Rev_vals = []
    rYoY_names = []; rYoY_vals = []; RevYoY_Use = "0%"; RevYoY_Avg = "0%"

    try:
        url = f'https://djinfo.cathaysec.com.tw/z/zc/zch/zch_{stock_id}.djhtm'
        soup = fetch_soup(url, 'cp950')
        if soup:
            dfs = pd.read_html(io.StringIO(str(soup)))
            if len(dfs) > 2:
                df_rev = dfs[2]
                try: latest_yoy = clean_float(df_rev.iloc[6, 4]) / 100
                except: latest_yoy = 0

                yoy_sum = 0; count = 0
                for k in range(6):
                     try:
                        v = float(df_rev.iloc[6+k, 4].replace('%',''))/100
                        yoy_sum += v; count += 1
                     except: pass
                average_yoy = yoy_sum / count if count else latest_yoy
                RevYoY = min(latest_yoy, average_yoy)
                RevYoY_Use = f"{RevYoY*100:.2f}%"
                RevYoY_Avg = f"{average_yoy*100:.2f}%"

                vals = []
                for i in range(12):
                    nm = str(df_rev.iloc[6+i, 0])
                    try: v = float(df_rev.iloc[6+i, 1])/100000
                    except: v = 0
                    vals.append(v); Rev_names.append(nm); Rev_vals.append(round(v, 2))
                    if i < 6: rYoY_names.append(nm); rYoY_vals.append(df_rev.iloc[6+i, 4])

                temp_q4_sum = 0
                target_dates = [f"{last_year_roc}/10", f"{last_year_roc}/11", f"{last_year_roc}/12"]
                for i in range(12):
                    nm = str(df_rev.iloc[6+i, 0])
                    if any(t in nm for t in target_dates):
                        try: temp_q4_sum += float(df_rev.iloc[6+i, 1])/100000
                        except: pass
                Q4_Rev_Actual = round(temp_q4_sum, 2)

                Rev_Current_Year_Est, Rev_Predict = calculate_revenue_forecast(
                    vals,
                    RevYoY,
                    month_id,
                    forecast_next_year,
                )
    except: pass

    Net_Predict = 0; Net4Average = 0; Net_names = []; Net_vals = []
    try:
        url = f'https://djinfo.cathaysec.com.tw/z/zc/zcr/zcr_{stock_id}.djhtm'
        soup = fetch_soup(url, 'cp950')
        if soup:
            net_margin_series = find_financial_series(soup, ('稅後淨利率',), limit=4)
            for name, value in net_margin_series:
                Net_names.append(name)
                Net_vals.append(f"{value:.2f}%")
            if net_margin_series:
                Net4Average = sum(value for _, value in net_margin_series) / len(net_margin_series) / 100
        Net_Predict = round(Rev_Predict * Net4Average, 6)
    except: pass

    capital_stock = 0.0
    try:
        url = f'https://djinfo.cathaysec.com.tw/z/zc/zcp/zcpa_{stock_id}.djhtm'
        soup = fetch_soup(url, 'cp950')
        if soup:
            rows = soup.find_all(class_='table-row')
            if len(rows) > 14: capital_stock = clean_float(rows[-14].text.split('\n')[2]) / 100
    except: pass

    # 7. 估算完整年度 EPS，再用同一年度 EPS 計算本益比目標價
    Q4_Net_Predict = 0; Q4_EPS_Predict = 0; Total_EPS_Predict = 0
    if use_estimation:
        # 當最近年度 Q4 財報尚未出爐時，估算該年度全年 EPS。
        if Q4_Rev_Actual > 0: Q4_Net_Predict = Q4_Rev_Actual * Net4Average
        else: Q4_Net_Predict = (Rev_Predict * Net4Average) / 4

        if capital_stock > 0: Q4_EPS_Predict = round(Q4_Net_Predict / capital_stock * 10, 2)
        Total_EPS_Predict = round(epsq1 + epsq2 + epsq3 + Q4_EPS_Predict, 2)
        fallback_current_year_eps = Total_EPS_Predict
    else:
        # 最近年度 EPS 已公布，留作歷史本益比的實際基準。
        Q4_EPS_Predict = 0
        Total_EPS_Predict = eps1
        fallback_current_year_eps = round(eps1 * (1 + RevYoY), 2)

    current_year_eps_estimate = calculate_eps_forecast(Rev_Current_Year_Est, Net4Average, capital_stock)
    if current_year_eps_estimate <= 0:
        current_year_eps_estimate = fallback_current_year_eps
    current_year_pe_high = round(H0 / current_year_eps_estimate, 2) if H0 > 0 and current_year_eps_estimate > 0 else 0
    current_year_pe_low = round(L0 / current_year_eps_estimate, 2) if L0 > 0 and current_year_eps_estimate > 0 else 0

    # Predict_Rev、Predict_Net、Predict_EPS 必須屬於相同的 forecast_year。
    # 例如 2026 年 9 月後：先補齊 2026 營收，再外推 2027 營收與 EPS。
    Predict_EPS = calculate_eps_forecast(Rev_Predict, Net4Average, capital_stock)
    if Predict_EPS <= 0:
        Predict_EPS = current_year_eps_estimate
        if forecast_next_year:
            Predict_EPS = round(Predict_EPS * (1 + RevYoY), 2)

    Predict_high_price = round(Predict_EPS * PER_H, 2) if PER_H > 0 else 0
    Predict_low_price = round(Predict_EPS * PER_L, 2) if PER_L > 0 else 0

    yahoo_latest_tradePrice = get_latest_price(stock_id)

    New_up_profit = "0%"; New_down_loss = "0%"; risk_reward = 0
    if yahoo_latest_tradePrice > 0:
        up = (Predict_high_price - yahoo_latest_tradePrice) / yahoo_latest_tradePrice
        down = (Predict_low_price - yahoo_latest_tradePrice) / yahoo_latest_tradePrice
        New_up_profit = f"{up*100:.2f}%"; New_down_loss = f"{down*100:.2f}%"
        if down != 0: risk_reward = round(abs(up/down), 2)

    return {
        'Name': stock_name, 'H': [H1, H2, H3, H4, H5], 'L': [L1, L2, L3, L4, L5],
        'EPS': [eps1, eps2, eps3, eps4, eps5], 'PE_H': [PER_H1, PER_H2, PER_H3, PER_H4, PER_H5], 'PE_L': [PER_L1, PER_L2, PER_L3, PER_L4, PER_L5],
        'PE_Avg_H': PER_H_average, 'PE_Avg_L': PER_L_average, 'PE_Use_H': PER_H, 'PE_Use_L': PER_L,
        'Rev_Names': Rev_names, 'Rev_Vals': Rev_vals, 'YoY_Names': rYoY_names, 'YoY_Vals': rYoY_vals,
        'YoY_Avg': RevYoY_Avg, 'YoY_Use': RevYoY_Use, 'Net_Names': Net_names, 'Net_Vals': Net_vals, 'Net_Avg': f"{Net4Average*100:.2f}%",
        'Predict_Rev': Rev_Predict, 'Predict_Net': Net_Predict, 'Predict_EPS': Predict_EPS, 'Capital': capital_stock,
        'Forecast_Year': forecast_year_ad, 'Forecast_Year_ROC': forecast_year_roc,
        'Forecast_Base_Year': current_year_ad, 'Forecast_Base_Revenue': Rev_Current_Year_Est,
        'Forecast_Horizon': 'next_year' if forecast_next_year else 'current_year',
        'Forecast_Method': '預估營收 × 平均淨利率 ÷ 股本 × 10',
        'Target_H': Predict_high_price, 'Target_L': Predict_low_price,
        'Target_H_30': round(Predict_high_price*0.7, 2), 'Target_L_30': round(Predict_low_price*0.7, 2),
        'Now_Price': yahoo_latest_tradePrice, 'H0': H0, 'L0': L0, 'Profit': New_up_profit, 'Risk': New_down_loss, 'RR': risk_reward,
        'Current_Year_H': H0, 'Current_Year_L': L0, 'Current_Year_EPS_Est': current_year_eps_estimate,
        'Current_Year_PE_H': current_year_pe_high, 'Current_Year_PE_L': current_year_pe_low,
        'Profit_30': f"{(round(Predict_high_price*0.7, 2)-yahoo_latest_tradePrice)/yahoo_latest_tradePrice*100:.2f}%" if yahoo_latest_tradePrice else "0%",
        'Risk_30': f"{(round(Predict_low_price*0.7, 2)-yahoo_latest_tradePrice)/yahoo_latest_tradePrice*100:.2f}%" if yahoo_latest_tradePrice else "0%",
        'RR_30': 0, 'Current_Year': current_year_ad, 'Current_Year_ROC': current_year_roc,
        'eps1N': eps1N, 'EPS_Q1': epsq1, 'EPS_Q2': epsq2, 'EPS_Q3': epsq3,
        'epsq1N': epsq1N, 'epsq2N': epsq2N, 'epsq3N': epsq3N, # 輸出動態季別名稱
        'Q4_Rev_Actual': Q4_Rev_Actual, 'Q4_EPS_Est': Q4_EPS_Predict, 'Total_EPS_Est': Total_EPS_Predict,
        'Detect_Reason': detect_reason, 'Use_Estimation': use_estimation, 'Latest_Quarter_Str': latest_quarter_str, 'Is_Before_Deadline': is_before_deadline,
        'Date': now.strftime("%Y-%m-%d"), 'EPS1_Is_Est': use_estimation,
        'Sources': sources,
        'Formulas': {
            'RevenueYoY': '(本月營收－去年同月營收)÷去年同月營收×100%',
            'CurrentYearRevenue': '已公布月份合計＋未公布月份去年值×(1＋採用 YoY)',
            'ForecastRevenue': '完整年度基期營收×(1＋採用 YoY)',
            'ForecastEPS': '預估營收×近四季平均淨利率÷股本×10',
            'HistoricalPE': '年度最高／最低價÷該年度 EPS',
            'TargetPrice': '預估 EPS×採用歷史 PE',
        },
    }

# ==============================================================================
# 自動化排程處理腳本 (無GUI主程式)
# ==============================================================================
def process_stock(stock_id, target_month):
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] 開始分析股票: {stock_id}")

    six = Stock6x_Analysis(stock_id)
    per = PERsegx(stock_id, target_month, six)

    stock_name = per.get('Name', stock_id)
    today_str_hyphen = datetime.datetime.now().strftime("%Y-%m-%d")
    today_str_compact = datetime.datetime.now().strftime("%Y%m%d")

    payload = {
        str(stock_id): {
            "Meta": {
                "StockID": str(stock_id),
                "StockName": stock_name,
                "TargetMonth": str(target_month),
                "QueryDate": today_str_hyphen
            },
            "PER_Analysis": per,
            "Six_Indicators": six
        }
    }

    json_filename = safe_filename(f"{stock_id}_{stock_name}_{today_str_compact}.json")
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=4)
    print(f"  - 儲存本機 JSON 成功: {json_filename}")

    # 這裡印出重點更新資訊供您核對
    q1n, q2n, q3n = per.get('epsq1N', '最新季'), per.get('epsq2N', '前一季'), per.get('epsq3N', '前二季')
    print(f"  - 抓取季報: {q1n}={per['EPS_Q1']}, {q2n}={per['EPS_Q2']}, {q3n}={per['EPS_Q3']}")
    if not per['Use_Estimation']:
        print(f"  - 年報已出！最近年度 EPS={per['Total_EPS_Est']}")
    print(
        f"  - {per['Forecast_Year']} 年預估：營收={per['Predict_Rev']} 億，"
        f"EPS={per['Predict_EPS']}，目標價={per['Target_L']}～{per['Target_H']}"
    )

    upload_payload(payload)

def main():
    configure_working_directory()
    print("==================================================")
    print("      台股全方位分析 - 自動化排程系統 (無GUI版)   ")
    print("==================================================")
    print(f"儀表板網址：{DASHBOARD_URL}")

    csv_file = 'stock_id_settings.csv'

    if not os.path.exists(csv_file):
        print(f"[提示] 找不到檔案 {csv_file}，已自動幫您建立範例檔。")
        with open(csv_file, 'w', encoding='utf-8') as f:
            f.write("2330\n2317\n5347\n")
        print(f"請在 {csv_file} 中填入要分析的股票代號（一行一個）後，重新啟動程式。")
        pause_console()
        return

    stock_ids = []
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        for line in f:
            sid = line.split(',', 1)[0].strip()
            if sid and not sid.startswith('#') and sid.lower() not in ('stock_id', '股票代碼') and re.fullmatch(r'\d{4,6}', sid):
                stock_ids.append(sid)

    if not stock_ids:
        print("[錯誤] 名單為空，請確認 CSV 檔案。")
        pause_console()
        return

    try:
        target_month_input = input("\n請輸入要分析的基準月份 (例如: 1, 2, 12): ")
        target_month = int(target_month_input)
        if not 1 <= target_month <= 12:
            raise ValueError("月份必須介於 1 到 12")
    except (ValueError, EOFError):
        target_month = datetime.datetime.now().month
        print(f"輸入無效，預設使用當前月份: {target_month}")

    total = len(stock_ids)
    print(f"\n[*] 成功載入 {total} 檔股票，開始自動化分析程序...\n")

    for i, sid in enumerate(stock_ids):
        print(f"\n>>> 進度: [{i+1}/{total}]")
        try:
            process_stock(sid, target_month)
        except Exception as e:
            print(f"處理 {sid} 時發生不可預期的錯誤: {e}")

        if i < total - 1:
            wait_time = random.randint(40, 120)
            print(f"[*] 啟動防封鎖機制，隨機等待 {wait_time} 秒...")
            for remaining in range(wait_time, 0, -1):
                print(f"\r倒數 {remaining} 秒...", end="")
                time.sleep(1)
            print("\r" + " "*20 + "\r", end="")

    print("\n==================================================")
    print("🎉 所有股票處理與同步完畢！")
    print(f"請至儀表板查看：{DASHBOARD_URL}")
    pause_console()

if __name__ == "__main__":
    main()
