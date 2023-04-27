import requests         
import json
import pymysql


count = 60
anchor = 0
country = 'tw'
country_language = 'zh-Hant'
query = 'jordan' # air force dunk airmax jordan
url = f'https://api.nike.com/cic/browse/v2?queryid=products&anonymousId=241B0FAA1AC3D3CB734EA4B24C8C910D&country={country}&endpoint=%2Fproduct_feed%2Frollup_threads%2Fv2%3Ffilter%3Dmarketplace({country})%26filter%3Dlanguage({country_language})%26filter%3DemployeePrice(true)%26searchTerms%3D{query}%26anchor%3D{anchor}%26consumerChannelId%3Dd9a5bc42-4b9c-4976-858a-f159cf99c647%26count%3D{count}&language={country_language}&localizedRangeStr=%7BlowestPrice%7D%E2%80%94%7BhighestPrice%7D'

html = requests.get(url=url)
output = json.loads(html.text)

# print(html.text)

# 利用迴圈抓取
for item in output['data']['products']['products']:
    
    
    titleList = []
    subtitleList = []
    imageUrlList = []
    priceList = []
    productUrlList = []

    titleName = item['title']
    subtitleName = item['subtitle']
    imageUrl = item['images'].get('portraitURL')
    priceName = item['price'].get('fullPrice')
    productUrl = 'https://www.nike.com/tw' + item['url'].replace('{','').replace('countryLang}', '')

    titleList.append(titleName)
    subtitleList.append(subtitleName)
    imageUrlList.append(imageUrl)
    priceList.append(priceName)
    productUrlList.append(productUrl)

    # print(priceList)

    titleLists_str = ','.join(titleList)
    imageUrlLists_str = ','.join(imageUrlList)
    priceLists_str = ''.join([str(_) for _ in priceList])
    productUrlLists_str = ','.join(productUrlList)
    subtitleLists_str = ','.join(subtitleList)
    # print(imageUrlLists_str)

    


    # #MySQL connect 
    db_settings = {
        "host" : "127.0.0.1",
        "port" : 3306,
        "user" : "root",
        "password" : "root",
        "db" : "NikeCrawler",
        "charset" : "utf8"
    }

    # Connection

    try :
        conn = pymysql.connect(**db_settings)

        with conn.cursor() as cursor:
            # sql = "INSERT INTO TestOne(name, price, img, source)VALUES(%s, %s, %s, %s)",
            #                (titleLists_str, imageUrlLists_str, priceList,  productUrlLists_str)
            cursor.execute("INSERT INTO Nike(name, price, img, source, subtitle)VALUES(%s, %s, %s, %s, %s)",
                           (titleLists_str, priceLists_str, imageUrlLists_str,  productUrlLists_str, subtitleLists_str))  #加入SQL
            conn.commit()
        

    except Exception as ex:
        print(ex)
    
