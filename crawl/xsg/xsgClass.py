class crawl_Xsjj():

    def __init__(self,timeout=300):
        self.url = "http://data.10jqka.com.cn/market/xsjj/"
        self.today = judge_date()
        self.collection = stockXsjj_mongo()
        isExists = os.path.exists("D:/python_stock/限售解禁")
        if not isExists:
            print(u"创建名为限售解禁的文件夹")
            os.makedirs("D:/python_stock/限售解禁")
            os.chdir("D:/python_stock/限售解禁")
        else:
            os.chdir("D:/python_stock/限售解禁")
        self.output = open("%s_XSJJ.txt" % (self.today), "a")

    def startCrawl(self):
        browser = webdriver.Firefox()
        browser.get(self.url)
        while browser.find_elements_by_xpath('//div[@class="m-page J-ajax-page"]/a')[-1].text == "尾页":
            button = browser.find_elements_by_xpath('//div[@class="m-page J-ajax-page"]/a')[-2]
            presentPage = browser.find_element_by_xpath('//div[@class="m-page J-ajax-page"]/a[@class="cur"]').text
            self.crawl_page(browser)
            print("第%s页爬取结束" % (presentPage))
            button.click()
            time.sleep(5)
        self.crawl_page(browser)
        browser.close()
        print("爬取结束")

    def crawl_page(self,browser):
        try:
            presentPage = browser.find_element_by_xpath('//div[@class="m-page J-ajax-page"]/a[@class="cur"]').text
        except:
            presentPage = 1
        record = open("%s_%s.txt" % (self.today, presentPage),"a")
        record.write(browser.page_source)
        record.close()
        table = browser.find_elements_by_xpath('//table[@class="m-table J-ajax-table"]/tbody/tr')
        for tr in table:
            tdList = tr.find_elements_by_xpath("td")
            stockCode = tdList[1].text
            stockName = tdList[2].text
            jjdate = tdList[3].text
            percent = tdList[7].text
            self.output.write("%s\t%s\t%s\t%s\n" % (stockName, stockCode, jjdate, percent))
            if self.collection.find_one(stockCode,jjdate):
                print("%s已经插入" %(stockName))
            else:
                self.collection.update(stockCode,stockName,jjdate,percent)
