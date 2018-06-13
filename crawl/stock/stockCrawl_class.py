import os
from stock_pymongo import *
from selenium import webdriver
from commonFunctions import getHtmlPage_GBK,judge_date
import time
import re
import xlwt
from selenium.webdriver.support.wait import WebDriverWait
from dateutil.parser import parse

"""
爬取龙虎榜：crawl_lhb
限售解禁：crawl_xsjj
停复牌：crawl_tfp()
高送转：crawl_Gsz()
板块涨幅：crawl_conceptRise()
"""

class CrawlLhb():

    def __init__(self,timeout=300):
        self.today = judge_date()
        self.collection = StockConceptMongo()
        self.url = "http://data.eastmoney.com/stock/lhb.html"
        self.yyb_dict = {"上海溧阳路": "孙哥", "上海瑞金南路": "孙哥", "上海古北路": "孙哥", "上海淮海中路": "孙哥","中信证券股份有限公司上海牡丹江路证券营业部":"孙哥",
            "中信证券股份有限公司上海分公司": "孙哥","光大证券股份有限公司宁波解放南路证券营业部": "赵一万",
            "绍兴解放北路": "赵一万", "中国银河证券股份有限公司绍兴": "赵一万", "中国银河证券股份有限公司北京阜成路": "赵一万",
            "湘财证券股份有限公司上海陆家嘴": "赵一万", "华泰证券股份有限公司永嘉阳光大道": "赵一万",
            "佛山绿景路证券营业部": "佛山", "佛山季华六路证券营业部": "佛山", "佛山普澜二路证券营业部": "佛山",
            "华鑫证券有限责任公司上海宛平南路": "炒股养家", "华鑫证券有限责任公司宁波沧海路": "炒股养家", "华鑫证券有限责任公司上海松江": "炒股养家",
            '招商证券股份有限公司深圳蛇口': "乔帮主", '海通证券股份有限公司北京阜外大街证券营业部': "刺客", '国泰君安证券股份有限公司南京太平南路': "作手新一",
            '方正证券股份有限公司上海保定路证券营业部': "神秘游资","光大证券股份有限公司深圳金田路证券营业部": "神秘游资","国元证券股份有限公司上海虹桥路证券营业部": "神秘游资",
            "中泰证券股份有限公司深圳欢乐海岸证券营业部":"神秘游资"
            }

    def startCrawl(self):
        isExists = os.path.exists(os.path.join("D:/lhb", self.today))
        if not isExists:
            print("创建名为%s文件夹" % (self.today))
            os.makedirs(os.path.join("D:/lhb", self.today))
            os.chdir(os.path.join("D:/lhb", self.today))
        else:
            os.chdir(os.path.join("D:/lhb", self.today))
        self.crawl_page()

    def crawl_page(self):
        stock_item = getHtmlPage_GBK(self.url).find_all("span", class_="wname")
        for stock in stock_item:
            stock_el = stock.find("a")
            stockName = stock_el["data_name"].replace("*", "")
            stockCode = stock_el["data_code"]
            print(self.collection.find_one(stockCode))
            isExists = os.path.exists(stockName + "_" + stockCode + ".xls")
            if not isExists:
                page_url = "http://data.eastmoney.com" + str(stock_el["href"])
                soup = getHtmlPage_GBK(page_url)
                try:
                    basic_info = soup.find("div", class_="data-tips")
                    lhb_reason = basic_info.find("div", class_="left con-br").get_text().split("：")[1]
                    zhangdie = re.sub(".*:", "", basic_info.find("div", class_="right").find("span")["style"])  # Green red
                    sum_part = basic_info.find("div", class_="right").get_text().replace(" ", "")
                    closing_price = float(re.findall(r"\d+.\d+", sum_part)[0])
                    fluctuate = float(re.findall(r"\d+.\d+", sum_part)[1])
                    total_cjl = float(re.findall(r"\d+.\d+", sum_part)[2])
                    total_cjje = float(re.findall(r"\d+.\d+", sum_part)[3])
                except Exception as e:
                    continue
                buy_part = soup.find("table", id="tab-2").find("tbody").find_all("tr")
                data = xlwt.Workbook()
                table = data.add_sheet("lhb", cell_overwrite_ok=True)
                table.write(0, 0, closing_price)
                if zhangdie == "red":
                    table.write(0, 1, "+" + str(fluctuate) + "%")
                else:
                    table.write(0, 1, "-" + str(fluctuate) + "%")
                table.write(0, 2, "成交量: " + str(total_cjl))
                table.write(0, 3, "成交金额: " + str(total_cjje))
                table.write(0, 4, "上榜理由: " + lhb_reason)
                table.write(2, 0, u"序号")
                table.write(2, 1, u"营业部")
                table.write(2, 2, u"买入金额")
                table.write(2, 3, u"买入比例")
                table.write(2, 4, u"卖出金额")
                table.write(2, 5, u"卖出比例")
                table.write(2, 6, u"净额")
                table.write(2, 7, u"买入成本")
                table.write(2, 8, u"卖出成本")
                table.write(2, 9, u"买入原因")
                table.write(3, 0, u"买入前五")
                print(u"开始爬取", stockName, u"：请等待")
                yyb_buy_list = []
                for yyb_index in range(len(buy_part)):
                    yyb = buy_part[yyb_index]
                    el = yyb.find_all("td")
                    order = el[0].get_text()
                    yyb_name = yyb.find("div", class_="sc-name").get_text().strip()
                    yyb_buy_list.append(yyb_name)
                    total_buy = el[2].get_text()
                    buy_proportion = el[3].get_text()
                    total_sell = el[4].get_text()
                    sell_proportion = el[5].get_text()
                    net_amount = el[6].get_text()
                    table.write(yyb_index + 4, 0, order)
                    table.write(yyb_index + 4, 1, yyb_name)
                    table.write(yyb_index + 4, 2, total_buy)
                    table.write(yyb_index + 4, 3, buy_proportion)
                    table.write(yyb_index + 4, 4, total_sell)
                    table.write(yyb_index + 4, 5, sell_proportion)
                    table.write(yyb_index + 4, 6, net_amount)
                    if buy_proportion != "-" and buy_proportion != "0.00%" and float(re.sub("%", "", buy_proportion)) > 0.05:
                        average_buy_cost = round(float(total_buy) / (float(buy_proportion.replace("%", "")) * total_cjl * 0.01),2)
                        table.write(yyb_index + 4, 7, average_buy_cost)
                        table.write(yyb_index + 4, 9, self.operate_reason(fluctuate, zhangdie, average_buy_cost, closing_price))
                    elif buy_proportion != "-" and float(re.sub("%", "", buy_proportion)) <= 0.05:
                        table.write(yyb_index + 4, 7, "买入比例过少")
                    else:
                        table.write(yyb_index + 4, 7, "-")
                    if sell_proportion != "-" and sell_proportion != "0.00%" and float(re.sub("%", "", sell_proportion)) > 0.05:
                        average_sell_cost = round(
                            float(total_sell) / (float(sell_proportion.replace("%", "")) * total_cjl * 0.01), 2)
                        table.write(yyb_index + 4, 8, average_sell_cost)
                    elif sell_proportion != "-" and float(re.sub("%", "", sell_proportion)) <= 0.05:
                        table.write(yyb_index + 4, 8, "卖出比例过少")
                    else:
                        table.write(yyb_index + 4, 8, "-")
                self.detect_famous_yyb(yyb_buy_list, stockName, "买")

                table.write(10, 0, u"卖出前五")
                if len(soup.find("table", id="tab-4").find("tbody").find_all("tr")) == 6:
                    sell_part = soup.find("table", id="tab-4").find("tbody").find_all("tr")[0:5]
                    yyb_sell_list = []
                    for yyb_index in range(len(sell_part)):
                        yyb = sell_part[yyb_index]
                        el = yyb.find_all("td")
                        order = el[0].get_text()
                        yyb_name = yyb.find("div", class_="sc-name").get_text().strip()
                        yyb_sell_list.append(yyb_name)
                        total_buy = el[2].get_text()
                        buy_proportion = el[3].get_text()
                        total_sell = el[4].get_text()
                        sell_proportion = el[5].get_text()
                        net_amount = el[6].get_text()
                        table.write(yyb_index + 11, 0, order)
                        table.write(yyb_index + 11, 1, yyb_name)
                        table.write(yyb_index + 11, 2, total_buy)
                        table.write(yyb_index + 11, 3, buy_proportion)
                        table.write(yyb_index + 11, 4, total_sell)
                        table.write(yyb_index + 11, 5, sell_proportion)
                        table.write(yyb_index + 11, 6, net_amount)
                        if buy_proportion != "-" and buy_proportion != "0.00%" and float(
                                re.sub("%", "", buy_proportion)) > 0.05:
                            table.write(yyb_index + 11, 7, round(
                                float(total_buy) / (float(buy_proportion.replace("%", "")) * total_cjl * 0.01), 2))
                        elif buy_proportion != "-" and float(re.sub("%", "", buy_proportion)) <= 0.05:
                            table.write(yyb_index + 11, 7, "买入比例过少")
                        else:
                            table.write(yyb_index + 11, 7, "-")
                        if sell_proportion != "-" and sell_proportion != "0.00%" and float(
                                re.sub("%", "", sell_proportion)) > 0.05:
                            table.write(yyb_index + 11, 8, round(
                                float(total_sell) / (float(sell_proportion.replace("%", "")) * total_cjl * 0.01), 2))
                        elif sell_proportion != "-" and float(re.sub("%", "", sell_proportion)) <= 0.05:
                            table.write(yyb_index + 11, 8, "卖出比例过少")
                        else:
                            table.write(yyb_index + 11, 8, "-")
                    self.detect_famous_yyb(yyb_sell_list, stockName, "卖")
                else:
                    pass
                data.save(stockName + "_" + stockCode + ".xls")
                print(stockName, u"爬取结束")
                time.sleep(2)
            else:
                print(u"已经存在", stockName)

    def detect_famous_yyb(self,input_list, stock_name, state):
        detected_yyb = [key for key in self.yyb_dict.keys() for yyb in input_list if key in yyb]
        detected_yz = set([self.yyb_dict[yyb] for yyb in detected_yyb])
        if len(detected_yz) >= 2:
            print("提示：多家知名游资 " + state + " " + stock_name + " " + str(detected_yz))
            for item in detected_yyb:
                output = open(self.yyb_dict[item] + ".txt", "a")
                output.write("%s\t%s\t%s\n" % (item, state, stock_name))
        elif len(detected_yz) == 1:
            for item in detected_yyb:
                output = open(self.yyb_dict[item] + ".txt", "a")
                output.write("%s\t%s\t%s\n" % (item, state, stock_name))
                print("%s(%s)\t%s\t%s" % (item, self.yyb_dict[item], state, stock_name))
        else:
            pass

    def operate_reason(self,percent, color, average_cost, closing_price):
        if color == 'red' and float(percent) >= 9.9:
            if float(closing_price) / float(average_cost) - 1 < 0.01:
                return "打板"
            elif float(closing_price) / float(average_cost) - 1 < 0.03:
                return "追板"
            else:
                return "低吸"
        else:
            return

class CrawlTfp():

    def __init__(self,timeout=300):
        self.collection = StockTfpMongo()
        self.today = judge_date()
        self.url="http://data.10jqka.com.cn/tradetips/tfpts/"
        self.endSignal = False

    def startCrawl(self):
        browser = webdriver.Firefox()
        browser.get(self.url)
        fp_button = browser.find_elements_by_xpath('//div[@class="table-tab J-ajax-board"]/a')[1]
        self.crawl_page(browser,"tp")
        fp_button.click()
        time.sleep(1)
        if not self.endSignal:
            self.crawl_page(browser,"fp")
        else:
            self.endSignal = False
            self.retry(browser)
        browser.close()

    def retry(self,browser):
        fp_button = browser.find_elements_by_xpath('//div[@class="table-tab J-ajax-board"]/a')[0]
        fp_button.click()
        fp_button = browser.find_elements_by_xpath('//div[@class="table-tab J-ajax-board"]/a')[1]
        self.crawl_page(browser,"tp")
        fp_button.click()
        time.sleep(1)
        if not self.endSignal:
            self.crawl_page(browser,"fp")

    def crawl_page(self,browser,tfp):
        targetInfo = browser.find_elements_by_xpath('//tbody/tr')
        for item in targetInfo:
            content = item.find_elements_by_xpath("td")
            if content[0].text == "今日无数据":
                if tfp == "tp":
                    print("今日无停牌股")
                else:
                    print("今日无复牌股")
                return
            elif self.today in content[4].text:
                #停复牌数据未更新，即table中显示XX股于“今日”开始停牌
                print("今日停复牌数据未更新")
                self.endSignal = True
                return
            else:
                stockCode = content[1].text
                stockName = content[2].text
                if tfp == "tp":
                    self.collection.updateTp(stockCode,stockName,self.today)
                else:
                    self.collection.updateFp(stockCode,stockName)

class CrawlXsjj():

    def __init__(self,timeout=300):
        self.url = "http://data.10jqka.com.cn/market/xsjj/"
        self.collection = StockXsjjMongo()

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
        table = browser.find_elements_by_xpath('//table[@class="m-table J-ajax-table"]/tbody/tr')
        for tr in table:
            tdList = tr.find_elements_by_xpath("td")
            stockCode = tdList[1].text
            stockName = tdList[2].text
            jjdate = tdList[3].text
            percent = tdList[7].text
            if self.collection.find_one(stockCode,jjdate,percent):
                print("%s限售股信息已经插入" %(stockName))
            else:
                self.collection.update(stockCode,stockName,jjdate,percent)
                print("%s\t%s\t%s解禁\t%s"%(stockCode,stockName,jjdate,percent))

class CrawlGsz():     #高送转

    def __init__(self,timeout=300):
        self.url = "http://data.10jqka.com.cn/financial/sgpx/"
        self.collection = StockGszMongo()

    def startCrawl(self):
        browser = webdriver.Firefox()
        browser.get(self.url)
        while browser.find_elements_by_xpath('//div[@class="m-page J-ajax-page"]/a')[-1].text == "尾页":
            button = browser.find_elements_by_xpath('//div[@class="m-page J-ajax-page"]/a')[-2]
            presentPage = browser.find_element_by_xpath('//div[@class="m-page J-ajax-page"]/a[@class="cur"]').text
            self.crawl_page(browser)
            print("第%s页爬取结束" % (presentPage))
            button.click()
            time.sleep(3)
        self.crawl_page(browser)
        browser.close()
        print("爬取结束")

    def crawl_page(self,browser):
        table = browser.find_elements_by_xpath('//table[@class="m-table J-ajax-table J-canvas-table"]/tbody/tr')
        for tr in table:
            tdList = tr.find_elements_by_xpath("td")
            stockCode = tdList[1].text
            stockName = tdList[2].text
            gsz = tdList[8].text
            if gsz == "--":
                pass
            else:
                gsz = int(re.sub("\.\d+","",gsz))
                if gsz >= 7:
                    registday = tdList[11].text
                    self.collection.update(stockCode,stockName,gsz,registday)
                else:
                    pass




