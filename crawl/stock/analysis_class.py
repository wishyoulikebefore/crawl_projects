from ts_mongo import *
import datetime
from stock_pymongo import *
from commonFunctions import *
import pandas as pd
import os
import random
import time

class AnalysisZt():

    """
    分析每日涨停股对应概念

    2018.5.31修改：
    由于去除了次新股，因此需要自行添加
    添加各板块的今日涨幅

    2018.6.6修改
    近端次新涨幅这个坑还没填，是用开板次新的平均涨幅来定嘛？（已解决）
    引出问题：是否要考虑市值，而非简单的平均

    2018.6.10
    与部分模块合并
    """

    def __init__(self,minZtNum=1,timeout=300):
        self.yesterdayZt_collection = YesterdayZtMongo()
        self.concept_collection = StockConceptMongo()
        self.newstock_collection = SubNewStockMongo()
        self.conceptRise_collection = TodayConceptMongo()
        self.today = judge_date()
        self.saveDir = "D:/python_stock/涨停概念分析"
        self.minZtNum = minZtNum
        self.conceptUrlDict = {"jqkConcept":"http://q.10jqka.com.cn/gn/",
                                "regionConcept":"http://q.10jqka.com.cn/dy/",
                                "industryConcept":"http://q.10jqka.com.cn/thshy/"
                                }
        self.conceptDict = {}

    def getConcept(self,stockCode,conceptType):
        return self.concept_collection.find_one(stockCode)[conceptType]

    def binaryTransform(self,modelList,inputList):
        """
        根据股票对应的概念列表和总列表，相应转换为0或1
        """
        returnList = []
        for item in modelList:
            if item in inputList:
                returnList.append(1)
            else:
                returnList.append(0)
        return returnList

    def getTodayRise(self,conceptType,modelList):
        todayRiseList = []
        for concept in modelList:
            todayRiseList.append(self.conceptRise_collection.find_one(conceptType)["percentDict"][concept])
        return todayRiseList

    def generateConceptFrame(self,conceptType,ZtDict):
        """
        根据输入的概念类型，构建对应的概念矩阵
        """
        modelList = self.conceptDict[conceptType]
        sumList = []
        stockNameList = []
        for key,value in ZtDict.items():
            stockCode = key
            stockNameList.append(value)
            try:
                """
                某些股票在某种概念类型为空
                """
                inputList = self.getConcept(stockCode,conceptType)
            except Exception as e:
                inputList = []
            outputList = self.binaryTransform(modelList,inputList)
            sumList.append(outputList)
        df = pd.DataFrame(sumList,index=stockNameList,columns=modelList).T
        df["共计"] = df.sum(axis=1)
        df["今日涨幅"] = self.getTodayRise(conceptType,modelList)
        df = df.sort_values(by="共计",ascending=False)
        print("%s热门概念前三:%s" %(conceptType,df.index[:3]))
        return df

    @conn_try_again
    def crawlRise(self,conceptUrl):
        conceptSoup = getHtmlPage_GBK(conceptUrl)
        try:
            percent = conceptSoup.find("div", class_="board-hq").find("p").get_text().split()[1]
        except Exception as e:
            percent = conceptSoup.find("div", class_="board-infos fr").find("dd").get_text()
        time.sleep(random.random())
        return percent

    def startCrawl(self,df):
        for conceptType,conceptUrl in self.conceptUrlDict.items():
            soup = getHtmlPage_GBK(conceptUrl)
            content = soup.find("div", class_="cate_inner").find_all("a")
            conceptList = []
            percentDict = {}
            blackList = ["新股与次新股","首发新股","参股360","参股新三板","ST板块","万达私有化","债转股","杭州亚运会","马云概念","腾讯概念","王者荣耀","摘帽"]
            for item in content:
                    conceptUrl = item["href"]
                    #pymongo中不支持"."，因此先做处理
                    conceptName = item.get_text().replace(".","")
                    if conceptName in blackList:
                        pass
                    else:
                        conceptList.append(conceptName)
                        print("开始爬取%s" % (conceptName))
                        percentDict[conceptName] = self.crawlRise(conceptUrl)
                        print("爬取完成%s" % (conceptName))
            if conceptType == "jqkConcept":
                percentDict["昨日涨停"] = self.yesterdayZt_collection.todayRise(df)
                conceptList.append("昨日涨停")
                percentDict["开板近端次新"] = self.newstock_collection.todayRise(df)
                conceptList.append("开板近端次新")
            self.conceptRise_collection.update(conceptType,percentDict)
            print("%s爬取完成" %(conceptType))
            self.conceptDict[conceptType] = conceptList

    def startAnalyse(self):
        isExists = os.path.exists(os.path.join(self.saveDir,self.today))
        if not isExists:
            print("创建文件夹")
            os.makedirs(os.path.join(self.saveDir,self.today))
            os.chdir(os.path.join(self.saveDir,self.today))
        else:
            os.chdir(os.path.join(self.saveDir,self.today))
        conceptTypeList = ["jqkConcept","regionConcept","industryConcept"]
        df = ts.get_today_all()
        df = df.set_index("code")
        self.startCrawl(df)
        ZtDict = getTodayZt(df)
        for conceptType in conceptTypeList:
            frame = self.generateConceptFrame(conceptType,ZtDict)
            frame.to_csv(conceptType+".csv",encoding="utf_8_sig")
        self.yesterdayZt_collection.refresh()
        self.yesterdayZt_collection.trasnfer2concept()

