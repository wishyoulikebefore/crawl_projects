import os
import random
from selenium import webdriver
import time
import multiprocessing

isExists = os.path.exists("D:/python_stock/股票概念/行业分类")
if not isExists:
    print(u"创建文件夹")
    os.makedirs("D:/python_stock/股票概念/行业分类")
    os.chdir("D:/python_stock/股票概念/行业分类")
else:
    os.chdir("D:/python_stock/股票概念/行业分类")

output = open("行业分类概念.txt","a")
targetDict = {}

def startCrawl_industryConcept(url="http://q.10jqka.com.cn/thshy/"):
    browser = webdriver.PhantomJS()
    browser.get(url)
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
    browser = webdriver.Firefox()     #PhantomJS不行，可能是网站会识别无头浏览器
    browser.get(conceptUrl)
    try:
        while browser.find_elements_by_xpath('//div[@id="m-page"]/a')[-1].text == "尾页":
            button = browser.find_elements_by_xpath('//div[@id="m-page"]/a')[-2]
            presentPage = browser.find_element_by_xpath('//div[@id="m-page"]/a[@class="cur"]').text
            print("%s第%s页开始爬取" % (conceptName, presentPage))
            crawl_stock(browser,conceptName)
            print("%s第%s页爬取结束" % (conceptName,presentPage))
            button.click()
            time.sleep(5)
        crawl_stock(browser,conceptName)
        browser.close()
        output.write("\n\n")
        print("%s is over" %(conceptName))
    except:
        crawl_stock(browser,conceptName)
        browser.close()
        output.write("\n\n")
        print("%s is over" %(conceptName))

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
        stockIndex = item.find_elements_by_xpath("td")[1].text
        stockName = item.find_elements_by_xpath("td")[2].text
        output.write("%s\t%s\n" %(stockName,stockIndex))
        conceptFile.write("%s\t%s\n" %(stockName,stockIndex))

if __name__ == "__main__":
    startCrawl_industryConcept()
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    for conceptName in targetDict:
        pool.apply_async(crawl_concept,(targetDict.get(conceptName), conceptName,))
    pool.close()
    pool.join()
