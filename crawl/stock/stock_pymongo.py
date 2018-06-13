from pymongo import MongoClient
import tushare as ts
import time
from selenium import webdriver
from functions_basedOn_ts import getConZtNum
from commonFunctions import judge_date
from dateutil.parser import parse
import datetime
from functions_basedOn_ts import get_KbGd

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

    def pull(self,stockCode,conceptType,concept):
        self.collection.update({"stockCode":stockCode},{"$pull":{conceptType:concept}})

    def update(self,stockCode,stockName,conceptType,concept):
        self.collection.update({"stockCode":stockCode},
                               {"$set":{"stockName":stockName},"$addToSet":{conceptType:concept}},
                               upsert=True)

class SubNewStockMongo():
    """
    获得距今delta之内的新股数据，并删除过期的，同时在stockConcept_mongo中做出相应更新
    统计开板高度，提醒今日开板
    """

    def __init__(self,name="newStock",timeout=300):
        self.client = MongoClient()
        self.db = self.client["stock"]
        self.collection = self.db[name]
        self.conceptCollcetion = self.db["stockConcept"]

    def todayRise(self,df):
        stockList= []
        for item in self.collection.find():
            stockList.append(item["stockCode"])
        filter = df.ix[stockList]
        aveChange = round(filter["changepercent"].sum()/len(stockList),2)
        print("开板近端次新的今日涨幅: %s" %(aveChange))
        return aveChange

    def find_one(self,stockCode):
        return self.collection.find_one({"stockCode":stockCode})

    def delete_one(self,stockCode):
        self.collection.delete_one({"stockCode":stockCode})

    def update(self,stockCode,stockName,ttm,issue_price):
        if not self.find_one(stockCode):
            print("出现新股：%s\t%s，于%s上市" % (stockCode, stockName, ttm))
            self.collection.update({"stockCode": stockCode},
                                   {"$set": {"stockName": stockName, "ttm": ttm, "issue_price": issue_price,"kb": False}},
                                    upsert=True)
        elif self.collection.find_one({"stockCode": stockCode, "kb": False}):
            kbgd = get_KbGd(stockCode)
            if kbgd == 0:
                self.collection.update({"stockCode": stockCode},
                                       {"$set": {"stockName": stockName, "ttm": ttm, "issue_price": issue_price,"kb": False}},
                                        upsert=True)
            else:
                self.collection.update({"stockCode": stockCode},
                                       {"$set": {"stockName": stockName, "ttm": ttm, "issue_price": issue_price,"kb": True, "kbgd": kbgd}},
                                        upsert=True)
                self.conceptCollcetion.update({"stockCode": stockCode},
                                              {"$addToSet": {"jqkConcept": "开板近端次新"}},
                                               upsert=True)
                print("%s %s今天开板，开板高度%s" % (stockCode, stockName, kbgd))
        else:
            pass

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

    def delete_one(self,stockCode):
        self.collection.delete_one({"stockCode":stockCode})

    def todayRise(self,df):
        stockList= []
        for item in self.collection.find():
            stockList.append(item["stockCode"])
        filter = df.ix[stockList]
        aveChange = round(filter["changepercent"].sum()/len(stockList),2)
        print("昨日涨停的今日涨幅: %s" % (aveChange))
        return aveChange

    def update(self,stockCode,stockName):
        """
        排除未开板的新股
        """
        if self.db["newStock"].find_one({"stockCode":stockCode,"kb":False}):
            pass
        else:
            if self.collection.find_one({"stockCode":stockCode}):
                self.collection.update({"stockCode":stockCode},
                                        {"$set":{"stockName":stockName,"today":self.today},"$inc":{"conZt":1}},
                                        upsert=True)
                conZt = self.collection.find_one({"stockCode":stockCode})["conZt"]
                print("%s %s连续%s天涨停" %(stockCode,stockName,conZt))
            else:
                num = max(getConZtNum(stockCode),1)
                self.collection.insert_one({"stockCode":stockCode,"stockName":stockName,"today":self.today,"conZt":num})

    def refresh(self):
        self.collection.delete_many({"today": {"$ne": self.today}})

    def trasnfer2concept(self):
        self.conceptCollcetion.update_many({"jqkConcept":{"$all":["昨日涨停"]}},{"$pull":{"jqkConcept":"昨日涨停"}})
        for item in self.collection.find({"today":self.today}):
            stockCode = item["stockCode"]
            stockName = item["stockName"]
            self.conceptCollcetion.update({"stockCode":stockCode},
                                          {"$set":{"stockName":stockName},"$addToSet":{"jqkConcept":"昨日涨停"}},
                                           upsert=True)

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

    def find_one(self,conceptType):
        return self.collection.find_one({"conceptType":conceptType})

    def update(self,conceptType,percentDict):
        self.collection.update({"conceptType":conceptType},
                               {"$set":{"percentDict":percentDict}},
                               upsert=True)


class XkhsMongo():
    """
    记录每周新开户数
    """

    def __init__(self,timeout=300):
        self.client = MongoClient()
        self.db = self.client["stock"]
        self.collection = self.db["xkhs"]
        self.timeout = timeout

    def find_one(self,period):
        return self.collection.find_one({"perido":period})

    def insert_one(self,period,num):
        self.collection.insert_one({"period":period,"xkhs":num})
