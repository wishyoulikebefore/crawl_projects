import os
from stockMongo import stockConcept_mongo
from selenium import webdriver
from commonUse import getHtmlPage_GBK,judge_date
import time

"""
class似乎不支持multiprocessing
"""

class crawlConcept_stock():

    def __init__(self,conceptType,url):
        self.conceptType = conceptType
        self.url = url
        self.output = open("%s.txt" %(conceptType), "a")
        self.targetDict = {}
        self.collection = stockConcept_mongo()

    def startCrawl(self):
        today = judge_date()
        fileName = "D:/python_stock/股票概念/%s/%s" %(self.conceptType,today)
        isExists = os.path.exists(fileName)
        if not isExists:
            print(u"创建文件夹")
            os.makedirs(fileName)
            os.chdir(fileName)
        else:
            os.chdir(fileName)
        soup = getHtmlPage_GBK(self.url)
        content = soup.find("div", class_="cate_inner").find_all("a")
        for item in content:
            conceptUrl = item["href"]
            conceptName = item.get_text()
            self.targetDict[conceptName] = conceptUrl

    def crawl_page(self,conceptName,conceptUrl):
        print("开始爬取%s" % (conceptName))
        self.output.write("%s\n" % (conceptName))
        browser = webdriver.Firefox()
        browser.get(conceptUrl)
        try:
            while browser.find_elements_by_xpath('//div[@id="m-page"]/a')[-1].text == "尾页":
                button = browser.find_elements_by_xpath('//div[@id="m-page"]/a')[-2]
                presentPage = browser.find_element_by_xpath('//div[@id="m-page"]/a[@class="cur"]').text
                self.crawl_stock(browser, conceptName)
                print("%s 第%s页爬取结束" % (conceptName, presentPage))
                button.click()
                time.sleep(5)
            self.crawl_stock(browser, conceptName)
            browser.close()
            self.output.write("\n\n")
            print("%s爬取结束" % (conceptName))
        except:  # 只有一页
            self.crawl_stock(browser, conceptName)
            browser.close()
            self.output.write("\n\n")
            print("%s爬取结束" % (conceptUrl))

    def crawl_stock(self,browser,conceptName):
        conceptFile = open(conceptName + ".txt", "a")
        locate = browser.find_elements_by_xpath('//div[@id="maincont"]//tbody/tr')
        try:
            presentPage = browser.find_element_by_xpath('//div[@id="m-page"]/a[@class="cur"]').text
        except:
            presentPage = 1
        record = open("%s_%s.txt" % (conceptName, presentPage), "a")
        try:
            record.write(browser.page_source)
        except:
            print("%s网页储存出现问题" % (conceptName))
        record.close()
        for item in locate:
            stockCode = item.find_elements_by_xpath("td")[1].text
            stockName = item.find_elements_by_xpath("td")[2].text
            self.collection.pushConcept(stockCode, stockName, self.conceptType, conceptName)
            self.output.write("%s\t%s\n" % (stockName, stockCode))
            conceptFile.write("%s\t%s\n" % (stockName, stockCode))
        conceptFile.close()
