from pymongo import MongoClient
import tushare as ts
import time
from selenium import webdriver
from functions_basedOn_ts import getConZtNum
from commonFunctions import judge_date
from dateutil.parser import parse
import datetime

"""
使用类的继承，简化
StockConceptMongo()
SubNewStockMongo()
StockXsjjMongo()
StockTfpMongo()
StockGszMongo()
StockYjMongo()
TodayZtMongo()
TodayConceptMongo()
"""

class StockConceptMongo():
    """
    用于更新股票概念，在crawlConcept中使用
    """
    def __init__(self,timeout=300):
        self.client = MongoClient()
        self.db = self.client["stock"]
        self.collection = self.db["stockConcept"]
        self.timeout = timeout

    def find_one(self,stockCode):
        return self.collection.find_one({"stockCode":stockCode})

    def update(self,stockCode,stockName,conceptField,concept):
        self.collection.update({"stockCode":stockCode},
                               {"$set":{"stockName":stockName},"$addToSet":{conceptField:concept}},
                               upsert=True)


class SubNewStockMongo():
    """
    获得距今delta之内的新股数据，并删除过期的，同时在stockConcept_mongo中做出相应更新
    统计开板高度，提醒今日开板
    """

    def __init__(self,name="newstock",delta=180,timeout=300):
        self.client = MongoClient()
        self.db = self.client["stock"]
        self.collection = self.db[name]
        self.conceptCollcetion = self.db["stockConcept"]
        self.delta = delta
        self.now = datetime.datetime.now()
        self.timeout = timeout
        self.continueCrawl = True
        self.url = "http://data.10jqka.com.cn/ipo/xgsr/"

    def todayRise(self,df):
        stockList= []
        for item in self.collection.find():
            stockList.append(item["stockCode"])
        filter = df.ix[stockList]
        aveChange = str(round(filter["changepercent"].sum()/len(stockList),2))+"%"
        print("开板近端次新的今日涨幅: %s" %(aveChange))
        return aveChange

    def find_one(self,stockCode):
        if self.collection.find_one({"stockCode":stockCode}):
            return True
        else:
            return False

    def update(self):
        browser = webdriver.Firefox()
        browser.get(self.url)
        while self.continueCrawl:
            button = browser.find_elements_by_xpath('//div[@class="m-page J-ajax-page"]/a')[-2]
            self.crawl_page(browser)
            button.click()
            time.sleep(5)
        browser.close()
        self.dailyCheck()

    def crawl_page(self,browser):
        tr_list = browser.find_elements_by_xpath('//table[@class="m-table J-ajax-table"]/tbody/tr')
        for tr in tr_list:
            td_list = tr.find_elements_by_xpath("td")
            stockCode = td_list[1].text.strip()
            stockName  =td_list[2].text.strip()
            ttm = td_list[3].text
            issue_price = td_list[4].text
            if self.getStock(ttm):
                if not self.find_one(stockCode):
                    print("出现新股：%s\t%s，于%s上市" % (stockCode, stockName, ttm))
                    self.collection.update({"stockCode": stockCode},
                                            {"$set": {"stockName":stockName,"ttm":ttm,"issue_price":issue_price,"kb":False}},
                                            upsert=True)
                if self.collection.find_one({"stockCode":stockCode,"kb":False}):
                    kbgd = self.get_KbGd(stockCode)
                    if kbgd == 0:
                        self.collection.update({"stockCode": stockCode},
                                                {"$set": {"stockName":stockName,"ttm":ttm,"issue_price":issue_price,"kb":False}},
                                                upsert=True)
                    else:
                        self.collection.update({"stockCode": stockCode},
                                                {"$set": {"stockName":stockName,"ttm":ttm,"issue_price":issue_price,"kb":True,"kbgd":kbgd}},
                                                upsert=True)
                        self.conceptCollcetion.update({"stockCode":stockCode},
                                                      {"$addToSet":{"jqkConcept":"开板近端次新"}},
                                                        upsert=True)
                        print("%s %s今天开板，开板高度%s" %(stockCode,stockName,kbgd))
                else:
                    pass
            else:
                self.continueCrawl = False
                break

    def dailyCheck(self):
        for item in self.collection.find():
            if not self.getStock(item["ttm"]):
                stockCode = item["stockCode"]
                self.collection.delete_one(item)
                self.conceptCollcetion.update({"stockCode":stockCode},{"$pull":{"jqkConcept":"开板近端次新"}})
                print("%s上市日期已超过%s，因此剔除" %(stockCode,self.delta))
            else:
                pass

    def getStock(self,ttm):
        timedelta = self.now - parse(ttm)
        if timedelta.days < self.delta:
            return True
        else:
            return False

    def get_KbGd(self,stockCode):
        df = ts.get_k_data(stockCode)
        kbgd = 1
        marketTime = len(df.index)
        if marketTime == 1:
            return 0
        else:
            for nu in range(marketTime-1):
                slice = df.ix[nu+1]
                if slice["open"] == slice["close"] == slice["high"] == slice["low"]:
                    kbgd += 1
                else:
                    break
        if kbgd == marketTime:
            return 0
        else:
            return kbgd


class StockXsjjMongo():

    def __init__(self,timeout=300):
        self.client = MongoClient()
        self.db = self.client["stock"]
        self.collection = self.db["xsjj"]
        self.timeout = timeout

    def find_one(self,stockCode,jjdate,percent):
        return self.collection.find_one({"stockCode":stockCode,"jjdate":jjdate,"percent":percent})

    def update(self,stockCode,stockName,jjdate,percent):
        self.collection.update({"stockCode":stockCode},
                               {"$set":{"stockName":stockName,"jjdate":jjdate,"percent":percent}},
                               upsert=True)

class StockTfpMongo():

    def __init__(self,timeout=300):
        self.client = MongoClient()
        self.db = self.client["stock"]
        self.collection = self.db["tfp"]
        self.timeout = timeout

    def find_one(self,stockCode):
        return self.collection.find_one({"stockCode":stockCode})

    def updateTp(self,stockCode,stockName,tpdate):
            if self.db["todayZt"].find_one({"stockCode":stockCode}):
                conZt = self.db["todayZt"].find_one({"stockCode":stockCode})["conZt"]
                self.collection.update({"stockCode":stockCode},
                                       {"$set":{"stockName":stockName,"tpdate":tpdate,"Zt":True,"conZt":conZt}},
                                        upsert=True)
                print("今日涨停股%s %s停牌，连续涨停%s天" %(stockCode,stockName,conZt))
            else:
                self.collection.update({"stockCode": stockCode},
                                       {"$set": {"stockName": stockName, "tpdate": tpdate,"Zt":False}},
                                       upsert=True)
                print("%s %s停牌" %(stockCode,stockName))

    def updateFp(self,stockCode,stockName):
        if self.collection.find_one({"stockCode":stockCode,"Zt":True}):
            conZt = self.find_one(stockCode)["conZt"]
            print("之前涨停股%s %s复牌，曾连续涨停%s天" %(stockCode,stockName,conZt))
        else:
            print("%s %s复牌" %(stockCode,stockName))
        self.collection.delete_one({"stockCode":stockCode})

class StockGszMongo():

    def __init__(self,timeout=300):
        self.client = MongoClient()
        self.db = self.client["stock"]
        self.collection = self.db["gsz"]
        self.timeout = timeout

    def find_one(self,stockCode,gsz):
        return self.collection.find_one({"stockCode":stockCode,"gsz":gsz})

    def update(self,stockCode,stockName,gsz,registday):
        if registday == "--":
            self.collection.update({"stockCode":stockCode},
                                    {"$set":{"stockName":stockName,"stockCode":stockCode,"gsz":gsz,"registday":""}},
                                    upsert=True)
            print("%s\t%s\t高送转\t%s，股权登记日暂缺" %(stockCode,stockName,gsz))
        else:
            self.collection.update({"stockCode": stockCode},
                                   {"$set": {"stockName": stockName, "stockCode": stockCode, "gsz":gsz,"registday": registday}},
                                   upsert=True)
            print("%s\t%s\t高送转\t%s，股权登记日为%s" % (stockCode, stockName, gsz, registday))

class StockYjMongo():

    def __init__(self,timeout=300):
        self.client = MongoClient()
        self.db = self.client["stock"]
        self.collection = self.db["yjyg"]
        self.timeout = timeout

    def find_one(self,stockCode,quarter,year):
        return self.collection.find_one({"stockCode":stockCode,"quarter":quarter,"year":year})

    def update(self,stockCode,stockName,forecast,quarter,year):
        self.collection.update({"stockCode":stockCode},
                               {"$set":{"stockName":stockName,"quarter":quarter,"year":year,"forecast":forecast}},
                               upsert=True)

class YesterdayZtMongo():
    """
    先利用昨日涨停股计算该该概念的今日涨幅
    再更新今日涨停股
    最后删除昨日涨停股
    """

    def __init__(self,timeout=300):
        self.client = MongoClient()
        self.db = self.client["stock"]
        self.collection = self.db["yesterdayZt"]
        self.conceptCollcetion = self.db["stockConcept"]
        self.timeout = timeout
        self.today = judge_date()

    def find_one(self,stockCode):
        return self.collection.find_one({"stockCode":stockCode})

    def todayRise(self,df):
        stockList= []
        for item in self.collection.find():
            stockList.append(item["stockCode"])
        filter = df.ix[stockList]
        aveChange = str(round(filter["changepercent"].sum()/len(stockList),2))+"%"
        print("昨日涨停的今日涨幅: %s" % (aveChange))
        return aveChange

    def update(self,stockCode,stockName):
        """
        排除未开板的新股
        """
        if self.db["newstock"].find_one({"stockCode":stockCode,"kb":False}):
            pass
        else:
            self.conceptCollcetion.update({"stockCode":stockCode},
                                          {"$addToSet":{"jqkConcept":"昨日涨停"}})
            if self.collection.find_one({"stockCode":stockCode}):
                self.collection.update({"stockCode":stockCode},
                                        {"$set":{"stockName":stockName,"today":self.today},"$inc":{"conZt":1}},
                                        upsert=True)
                conZt = self.collection.find_one({"stockCode":stockCode})["conZt"]
                print("%s %s连续%s天涨停" %(stockCode,stockName,conZt))
            else:
                num = max(getConZtNum(stockCode),1)
                self.collection.insert_one({"stockCode":stockCode,"stockName":stockName,"today":self.today,"conZt":num})

    def dailyCheck(self):
        for item in self.collection.find({"today":{"$ne":self.today}}):
            stockCode = item["stockCode"]
            self.collection.delete_one({"stockCode":stockCode})
            self.conceptCollcetion.update({"stockCode":stockCode},{"$pull":{"jqkConcept":"昨日涨停"}})

class TodayConceptMongo():
    """
    更新每日板块的涨幅
    查看昨日热门板块今日表现
    """

    def __init__(self,timeout=300):
        self.client = MongoClient()
        self.db = self.client["stock"]
        self.collection = self.db["todayConcept"]
        self.timeout = timeout
        self.today = judge_date()

    def find_one(self,conceptType):
        return self.collection.find_one({"conceptType":conceptType})

    def update(self,conceptType,percentDict):
        self.collection.update({"conceptType":conceptType},
                               {"$set":{"percentDict":percentDict,"today":self.today}},
                               upsert=True)

    def delete_many(self):
        self.collection.delete_many({"today":{"$ne":self.today}})


