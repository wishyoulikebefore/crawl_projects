import os
from stockMongo import stockConcept_mongo
from selenium import webdriver
from commonUse import getHtmlPage_GBK,judge_date
import time
import multiprocessing

def startCrawl(conceptType,url):
    """
    jqkConcept：http://q.10jqka.com.cn/gn/

    regionConcept：http://q.10jqka.com.cn/dy/
    industryConcept：http://q.10jqka.com.cn/thshy/
    """
    targetDict = {}
    soup = getHtmlPage_GBK(url)
    content = soup.find("div", class_="cate_inner").find_all("a")
    for item in content:
        conceptUrl = item["href"]
        conceptName = item.get_text()
        targetDict[conceptName] = conceptUrl
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
        stockConcept_mongo().updateConcept(stockCode, stockName, conceptType, conceptName)

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
