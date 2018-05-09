import os
import time
from selenium import webdriver
from commonUse import getHtmlPage_GBK
import multiprocessing
from stockMongo import stockConcept_mongo
from commonUse import judge_date

"""
待解决问题：
1 加速：多进程+多线程
2 导入mongodb，定时检查更新
3.写成模块形式
"""

today = judge_date()
fileName = "D:/python_stock/股票概念/jqk概念/"+today
isExists = os.path.exists(fileName)
if not isExists:
    print(u"创建文件夹")
    os.makedirs(fileName)
    os.chdir(fileName)
else:
    os.chdir(fileName)

output = open("jqk概念.txt","a")
collection = stockConcept_mongo()
targetDict = {}

def startCrawl_jqkConcept():
    soup = getHtmlPage_GBK(url="http://q.10jqka.com.cn/gn")
    content = soup.find("div",class_="cate_inner").find_all("a")
    for item in content:
        conceptUrl = item["href"]
        conceptName = item.get_text()
        targetDict[conceptName] = conceptUrl

def crawl_page(conceptName,conceptUrl):
    print("开始爬取%s" %(conceptName))
    output.write("%s\n" %(conceptName))
    browser = webdriver.Firefox()
    browser.get(conceptUrl)
    try:
        while browser.find_elements_by_xpath('//div[@id="m-page"]/a')[-1].text == "尾页":
            button = browser.find_elements_by_xpath('//div[@id="m-page"]/a')[-2]
            presentPage = browser.find_element_by_xpath('//div[@id="m-page"]/a[@class="cur"]').text
            crawl_stock(browser,conceptName)
            print("%s 第%s页爬取结束" % (conceptName,presentPage))
            button.click()
            time.sleep(5)
        crawl_stock(browser,conceptName)
        browser.close()
        output.write("\n\n")
        print("%s爬取结束" %(conceptName))
    except:     #只有一页
        crawl_stock(browser,conceptName)
        browser.close()
        output.write("\n\n")
        print("%s爬取结束" %(conceptUrl))

def crawl_stock(browser,conceptName):
    conceptFile = open(conceptName + ".txt", "a")
    locate = browser.find_elements_by_xpath('//div[@id="maincont"]//tbody/tr')
    try:
        presentPage = browser.find_element_by_xpath('//div[@id="m-page"]/a[@class="cur"]').text
    except:
        presentPage = 1
    record  =open("%s_%s.txt" %(conceptName,presentPage),"a")
    try:
        record.write(browser.page_source)
    except:
        print("%s网页储存出现问题" %(conceptName))
    record.close()
    for item in locate:
        stockCode = item.find_elements_by_xpath("td")[1].text
        stockName = item.find_elements_by_xpath("td")[2].text
        collection.pushConcept(stockCode, stockName, "jqkConcept", conceptName)
        output.write("%s\t%s\n" %(stockName,stockCode))
        conceptFile.write("%s\t%s\n" %(stockName,stockCode))
    conceptFile.close()

if __name__ == "__main__":
    startCrawl_jqkConcept()
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    for conceptName in targetDict:
        pool.apply_async(crawl_page,(conceptName,targetDict.get(conceptName), ))
    pool.close()
    pool.join()


