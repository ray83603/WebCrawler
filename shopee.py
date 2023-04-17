import requests
import json
import pandas as pd
import time
from seleniumwire import webdriver # 需安裝：pip install selenium-wire
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import re
import random
import zlib
import pymysql


keyword = 'nike'
page = 2
ecode = 'utf-8-sig'


my_headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
    'if-none-match-': 'adbff-a770-4ef3-8f11-fa44a810333e'
    }    
# 55b03-6d83b58414a54cb5ffbe81099940f836

# 進入每個商品，抓取買家留言
def goods_comments(item_id, shop_id):
    url = 'https://shopee.tw/api/v4/item/get_ratings?filter=0&flag=1&itemid='+ str(item_id) + '&limit=50&offset=0&shopid=' + str(shop_id) + '&type=0'
    r = requests.get(url,headers = my_headers)
    st= r.text.replace("\\n","^n")
    st=st.replace("\\t","^t")
    st=st.replace("\\r","^r")
    
    gj=json.loads(st)
    return gj['data']['ratings']
    

# 進入每個商品，抓取賣家更細節的資料（商品文案）
# https://shopee.tw/api/v4/item/get?itemid=17652103038&shopid=36023817
def goods_detail(url, item_id, shop_id):
    
    driver.get(url) # 需要到那個頁面，才能度過防爬蟲機制
    time.sleep(random.randint(10,20))
    getPacket = ''
    for request in driver.requests:
        if request.response:
            # 挑出商品詳細資料的json封包
            if 'https://shopee.tw/api/v4/item/get?itemid=' + str(item_id) + '&shopid=' + str(shop_id) in request.url:
                # 解壓縮
                getPacket = zlib.decompress(
                    request.response.body,
                    16+zlib.MAX_WBITS
                    )
                break
    if getPacket != '':
        gj=json.loads(getPacket)
        return gj['data']
    else:
        return getPacket



# 自動下載ChromeDriver
service = ChromeService(executable_path=ChromeDriverManager().install())

# 關閉通知提醒
options = webdriver.ChromeOptions()
prefs = {"profile.default_content_setting_values.notifications" : 2}
options.add_experimental_option("prefs",prefs)
# 不載入圖片，提升爬蟲速度
# options.add_argument('blink-settings=imagesEnabled=false') 

# 開啟瀏覽器
driver = webdriver.Chrome(service=service, chrome_options=options)
time.sleep(random.randint(5,10))

# 開啟網頁
driver.get('https://shopee.tw/search?keyword=' + keyword )
time.sleep(random.randint(10,20))


print('---------- 開始進行爬蟲 ----------')
tStart = time.time()#計時開始

container_product = pd.DataFrame()      #準備水缸裝商品資訊
# container_comment = pd.DataFrame()      #準備水缸裝商品留言
for i in range(int(page)):

    # itemid = []
    # shopid =[]
    name = []
    link = []
    price = []
    img = []

    driver.get('https://shopee.tw/search?keyword=' + keyword + '&page=' + str(i))
    time.sleep(random.randint(5,10))
    # 滾動頁面
    for scroll in range(6):
        driver.execute_script('window.scrollBy(0,1000)')        #javascript語法
        time.sleep(random.randint(3,10))

    #取得商品內容
    for item, thename in zip(driver.find_elements(by=By.XPATH, value='//*[@data-sqe="link"]'), driver.find_elements(by=By.XPATH, value='//*[@data-sqe="name"]')):
        #商品ID、商家ID、商品連結
        getID = item.get_attribute('href')
        # theitemid = int((getID[getID.rfind('.')+1:getID.rfind('?')]))       #商品id
        # theshopid = int(getID[ getID[:getID.rfind('.')].rfind('.')+1 :getID.rfind('.')])       #店家id
        link.append(getID)
        # itemid.append(theitemid)
        # shopid.append(theshopid)
        
        
        #商品名稱
        getname = thename.text.split('\n')[0]
        name.append(getname)
        
        #價格
        thecontent = item.text
        thecontent = thecontent[(thecontent.find(getname)) + len(getname):]
        thecontent = thecontent.replace('萬','000')
        thecut = thecontent.split('\n')

        
    
        if bool(re.search('市|區|縣|鄉|海外|中國大陸', thecontent)): #有時會沒有商品地點資料
            if bool(re.search('已售出', thecontent)): #有時會沒銷售資料
                if '出售' in thecut[-3][1:]:
                    theprice = thecut[-4][1:]
                else:
                    theprice = thecut[-3][1:]

            else:
                theprice = thecut[-2][1:]
        else:
            if re.search('已售出', thecontent): #有時會沒銷售資料
                theprice = thecut[-2][1:]
            else:
                theprice = thecut[-1][1:]
                
        theprice = theprice.replace('$','')
        theprice = theprice.replace(',','')
        theprice = theprice.replace('售','')
        theprice = theprice.replace('出','')
        theprice = theprice.replace(' ','')
        if ' - ' in theprice:
            theprice = (int(theprice.split(' - ')[0]) +int(theprice.split(' - ')[1]))/2
        if '-' in theprice:
            theprice = (int(theprice.split('-')[0]) +int(theprice.split('-')[1]))/2
        # print(theprice)
        if theprice != (''):
            price.append(int(theprice))
    
    
    
    #商品圖片
    images = driver.find_elements(by=By.XPATH, value='//*[@class="_7DTxhh vc8g9F"]')
    for image in images:
        getImg = image.get_attribute('src')
        img.append(getImg)
    



    dic1 = {
            # '商品ID':itemid,
            # '賣家ID':shopid,
            '商品名稱':name
            }
    dic2 = {'商品連結':link}
    dic3 = {'價格':price}
    dic4 = {'圖片':img}
    print(dic1)
    print(dic2)
    print(dic3)
    print(dic4)

    #資料整合
    container_product = pd.concat([container_product,pd.DataFrame(dic1)], axis=0)
    # 暫時存檔紀錄
    container_product.to_csv('shopeeAPIData'+str(i+1)+'_Product.csv', encoding = ecode, index=False)
    # container_comment.to_csv('shopeeAPIData'+str(i+1)+'_Comment.csv', encoding = ecode, index=False)

    
    # time.sleep(random.randint(20,150)) 
# + str(len(container_comment))
container_product.to_csv(keyword +'_商品資料.csv', encoding = ecode, index=False)
# container_comment.to_csv(keyword +'_留言資料.csv', encoding = ecode, index=False)



driver.close() 

