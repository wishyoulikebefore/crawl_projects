import os
from stockMongo import stockConcept_mongo
from selenium import webdriver
import time
import multiprocessing
from commonUse import judge_date

today = judge_date()
fileName = "D:/python_stock/股票概念/行业概念/"+today
isExists = os.path.exists(fileName)
if not isExists:
    print(u"创建文件夹")
    os.makedirs(fileName)
    os.chdir(fileName)
else:
    os.chdir(fileName)

output = open("行业分类概念.txt","a")
targetDict = {}
collection = stockConcept_mongo()

def startCrawl_industryConcept():
    browser = webdriver.PhantomJS()
    browser.get("http://q.10jqka.com.cn/thshy/")
    button = browser.find_elements_by_xpath('//div[@class="m-pager"]/a')[-2]
    crawl_page(browser)
    button.click()
    crawl_page(browser)
    browser.close()

def crawl_page(browser):
    table = browser.find_elements_by_xpath('//div[@id="maincont"]//tbody/tr')
    for item in table:
        content = item.find_elements_by_xpath("td")[1]
        conceptName = content.text
        conceptUrl = content.find_element_by_xpath("a").get_attribute("href")
        targetDict[conceptName] = conceptUrl

def crawl_concept(conceptUrl,conceptName):
    print("开始爬取%s" %(conceptName))
    output.write("%s\n" % (conceptName))
    browser = webdriver.Firefox()     #PhantomJS不行，可能是网站会识别无头浏览器
    browser.get(conceptUrl)
    try:
        while browser.find_elements_by_xpath('//div[@id="m-page"]/a')[-1].text == "尾页":
            button = browser.find_elements_by_xpath('//div[@id="m-page"]/a')[-2]
            presentPage = browser.find_element_by_xpath('//div[@id="m-page"]/a[@class="cur"]').text
            crawl_stock(browser,conceptName)
            print("%s第%s页爬取结束" % (conceptName,presentPage))
            button.click()
            time.sleep(5)
        crawl_stock(browser,conceptName)
        browser.close()
        output.write("\n\n")
        print("%s爬取结束" %(conceptName))
    except:
        crawl_stock(browser,conceptName)
        browser.close()
        output.write("\n\n")
        print("%s爬取结束" %(conceptName))

def crawl_stock(browser,conceptName):
    conceptFile = open(conceptName+".txt","a")
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
        collection.pushConcept(stockCode,stockName,"industryConcept",conceptName)
        output.write("%s\t%s\n" %(stockName,stockCode))
        conceptFile.write("%s\t%s\n" %(stockName,stockCode))
    conceptFile.close()

if __name__ == "__main__":
    startCrawl_industryConcept()
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    for conceptName in targetDict:
        pool.apply_async(crawl_concept,(targetDict.get(conceptName), conceptName,))
    pool.close()
    pool.join()
