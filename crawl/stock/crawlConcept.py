from stockMongo_class import StockConceptMongo,SubNewStockMongo
from selenium import webdriver
from commonFunctions import getHtmlPage_GBK
import time
import multiprocessing
from commonFunctions import myMail

"""
2018.5.31更新：
次新股的概念根据爬虫结果设定，不再更具jqk的结果，在stockConcept_mongo中单独设置
由于pymongo的key不能出现"."，对于工业4.0这种，必须把"."去掉

有待更新：概念黑名单，有些概念非常垃圾或者过时

2018.6.13 需要用scrapy重写一下，优化速度
"""

def startCrawl(conceptType,url):
    blackList = ["新股与次新股","首发新股","参股360","参股新三板","ST板块","万达私有化","债转股","杭州亚运会","马云概念","腾讯概念","王者荣耀","摘帽"]
    targetDict = {}
    soup = getHtmlPage_GBK(url)
    content = soup.find("div", class_="cate_inner").find_all("a")
    for item in content:
        conceptUrl = item["href"]
        conceptName = item.get_text().replace(".","")
        if conceptName not in blackList:
            targetDict[conceptName] = conceptUrl
        else:
            pass
    return targetDict

def crawl_page(conceptName,conceptUrl,conceptType):
    print("开始爬取%s" % (conceptName))
    browser = webdriver.Firefox()
    browser.get(conceptUrl)
    try:
        while browser.find_elements_by_xpath('//div[@id="m-page"]/a')[-1].text == "尾页":
            button = browser.find_elements_by_xpath('//div[@id="m-page"]/a')[-2]
            presentPage = browser.find_element_by_xpath('//div[@id="m-page"]/a[@class="cur"]').text
            crawl_stock(browser, conceptName,conceptType)
            print("%s 第%s页爬取结束" % (conceptName, presentPage))
            button.click()
            time.sleep(5)
        crawl_stock(browser, conceptName,conceptType)
        browser.close()
        print("%s爬取结束" % (conceptName))
    except:  # 只有一页
        crawl_stock(browser, conceptName,conceptType)
        browser.close()
        print("%s爬取结束" % (conceptUrl))

def crawl_stock(browser,conceptName,conceptType):
    locate = browser.find_elements_by_xpath('//div[@id="maincont"]//tbody/tr')
    for item in locate:
        stockCode = item.find_elements_by_xpath("td")[1].text
        stockName = item.find_elements_by_xpath("td")[2].text
        StockConceptMongo().update(stockCode, stockName, conceptType, conceptName)

if __name__ == "__main__":
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    conceptDict = {"regionConcept":"http://q.10jqka.com.cn/dy/",
                    "industryConcept":"http://q.10jqka.com.cn/thshy/",
                    "jqkConcept":"http://q.10jqka.com.cn/gn/"}
    for key,value in conceptDict.items():
        targetDict = startCrawl(key,value)
        for conceptName in targetDict:
            pool.apply_async(crawl_page, (conceptName, targetDict.get(conceptName), key,))
    pool.close()
    pool.join()
    subNewMongo = SubNewStockMongo(delta=180, name="newstock")
    subNewMongo.update()
    for item in subNewMongo.collection.find():
        stockCode = item["stockCode"]
        StockConceptMongo().collection.update({"stockCode": stockCode}, {"$set": {"subNewStock": True}})
    myMail("概念更新","已完成")


