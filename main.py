# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import urllib2
import csv
import datetime

import sys 
reload(sys) # Python2.5 初始化後會刪除 sys.setdefaultencoding 這個方法，我們需要重新載入
sys.setdefaultencoding('utf-8') 

col_names=['代號','名稱','成交','漲跌價','漲跌幅','法人買賣資料日期','外資連續買賣日數','外資連續買賣張數','外資買賣佔成交(%)','外資買賣佔發行量(%)','投信連續買賣日數','投信連續買賣張數','投信買賣佔成交(%)','投信買賣佔發行量(%)','自營連續買賣日數','自營連續買賣張數','自營買賣佔成交(%)','自營買賣佔發行量(%)','三大連續買賣日數','三大連續買賣張數','三大買賣佔成交(%)','三大買賣佔發行量(%)']

hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive',}

def write_csv(csv_list):
    now_time = datetime.datetime.utcnow()
    file_name = now_time.strftime('%Y%m%d')+'.csv'
    # 開啟輸出的 CSV 檔案
    with open(file_name, 'wb') as csvfile:
        # 建立 CSV 檔寫入器
        writer = csv.writer(csvfile)
        # 寫入一列資料
        writer.writerow(col_names)
        for csv_row_list in csv_list:
            # 寫入另外幾列資料
            writer.writerow(csv_row_list)

def get_html_data( url ):
    req = urllib2.Request(url, headers=hdr)
    try:
        page = urllib2.urlopen(req,timeout=30)
        html_data = page.read()
    except Exception as e:
        print(e)
        print 'retry html: '+url
        return get_html_data( url ) #retry
    return html_data

def scan_page(url):
    html_data = get_html_data( url )
    print('html_data')
    #Create the soup object from the HTML data
    soup = BeautifulSoup(html_data, "html.parser")

    row_list = soup.findAll("table",{ "id" : "tblStockList" })[0].findAll('tr')
    csv_list = []
    for each_row in row_list:
        if(each_row.get('id')):
            each_str = each_row.text
            td_list = each_row.findAll("td")
            col_list = []
            td_ind = 0
            for each_col in td_list:
                a_col = each_col.findAll('a')
                if(a_col):
                    target_col = a_col[0]
                else:
                    target_col = each_col
                ## 有幾個column可能是字串形式
                if(td_ind == 0 or td_ind == 1 or td_ind == 5):
                    col_str = target_col.text
                else:
                    ## 去除加號和千位數符號
                    target_float_str = target_col.text.replace('+','').replace(',','')
                    try:
                        ## 轉換成浮點數
                        col_str = float(target_float_str)
                    except Exception as e:
                        ## 有些空值 會轉換失敗
                        col_str = target_float_str
                col_list.append(col_str)
                td_ind = td_ind+1
            csv_list.append(col_list)
            print(col_list[0])
            # print(col_list[0].encode("utf8").decode("cp950", "ignore"))
    print('total_row_num:'+str(len(csv_list)))
    print('total_col_num:'+str(len(csv_list[0])))
    write_csv(csv_list)
    print('write csv ok')

if __name__ == "__main__":
    url = "http://goodinfo.tw/StockInfo/StockList.asp?MARKET_CAT=%E6%99%BA%E6%85%A7%E9%81%B8%E8%82%A1&INDUSTRY_CAT=%E4%B8%89%E5%A4%A7%E6%B3%95%E4%BA%BA%E9%80%A3%E8%B2%B7+%28%E6%97%A5%29&SHEET=%E6%B3%95%E4%BA%BA%E8%B2%B7%E8%B3%A3&SHEET2=%E9%80%A3%E8%B2%B7%E9%80%A3%E8%B3%A3%E7%B5%B1%E8%A8%88%28%E6%97%A5%29"
    scan_page(url)