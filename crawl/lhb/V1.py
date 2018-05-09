from bs4 import BeautifulSoup
import requests
import os
import xlwt
import re
from commonUse import judge_date,getHtmlPage_GBK
import time

start_url="http://data.eastmoney.com/stock/lhb.html"
today = judge_date()

isExists = os.path.exists(os.path.join("D:\lhb",today))
if not isExists:
    print(u"创建名为",today,u"文件夹")
    os.makedirs(os.path.join("D:\lhb",today))
    os.chdir(os.path.join("D:\lhb",today))
else:
    os.chdir(os.path.join("D:\lhb", today))

yyb_dict = {"上海溧阳路": "孙哥", "上海瑞金南路": "孙哥", "上海古北路": "孙哥", "上海淮海中路": "孙哥","中信证券股份有限公司上海牡丹江路证券营业部":"孙哥",
            "中信证券股份有限公司上海分公司": "孙哥","光大证券股份有限公司宁波解放南路证券营业部": "赵一万",
            "绍兴解放北路": "赵一万", "中国银河证券股份有限公司绍兴": "赵一万", "中国银河证券股份有限公司北京阜成路": "赵一万",
            "湘财证券股份有限公司上海陆家嘴": "赵一万", "华泰证券股份有限公司永嘉阳光大道": "赵一万",
            "佛山绿景路证券营业部": "佛山", "佛山季华六路证券营业部": "佛山", "佛山普澜二路证券营业部": "佛山",
            "华鑫证券有限责任公司上海宛平南路": "炒股养家", "华鑫证券有限责任公司宁波沧海路": "炒股养家", "华鑫证券有限责任公司上海松江": "炒股养家",
            '招商证券股份有限公司深圳蛇口': "乔帮主", '海通证券股份有限公司北京阜外大街证券营业部': "刺客", '国泰君安证券股份有限公司南京太平南路': "作手新一",
            '方正证券股份有限公司上海保定路证券营业部': "神秘游资","光大证券股份有限公司深圳金田路证券营业部": "神秘游资","国元证券股份有限公司上海虹桥路证券营业部": "神秘游资",
            "中泰证券股份有限公司深圳欢乐海岸证券营业部":"神秘游资"
            }

def detect_famous_yyb(input_list,stock_name,state):
    detected_yyb = [key for key in yyb_dict.keys() for yyb in input_list if key in yyb]
    detected_yz = set([yyb_dict[yyb] for yyb in detected_yyb])
    if len(detected_yz) >= 2:
        print("提示：多家知名游资 " + state + " " + stock_name+" "+str(detected_yz))
        for item in detected_yyb:
            output = open(yyb_dict[item] + ".txt", "a")
            output.write("%s %s %s" %(item,state,stock_name)+"\n")
    elif len(detected_yz) == 1:
        for item in detected_yyb:
            output = open(yyb_dict[item] + ".txt", "a")
            output.write("%s %s %s" % (item, state, stock_name) + "\n")
            print("%s(%s) %s %s" % (item,yyb_dict[item],state,stock_name))
    else:
        pass

def operate_reason(percent,color,average_cost,closing_price):
    if color == 'red' and float(percent) >= 9.9:
        if float(closing_price)/float(average_cost)-1 < 0.01:
            return "打板"
        elif float(closing_price)/float(average_cost)-1 < 0.03:
            return "追板"
        else:
            return "低吸"
    else:
        return
    
stock_item = getHtmlPage_GBK(start_url).find_all("span",class_="wname")

for stock in stock_item:
    stock_el=stock.find("a")
    stock_name=stock_el["data_name"].replace("*","")
    stock_code=stock_el["data_code"]
    isExists = os.path.exists(stock_name+"_"+stock_code+".xls")
    if not isExists:
        page_url="http://data.eastmoney.com"+str(stock_el["href"])
        soup2=getHtmlPage_GBK(page_url)
        try:
            basic_info = soup2.find("div", class_="data-tips")
            lhb_reason = basic_info.find("div",class_="left con-br").get_text().split("：")[1]
            zhangdie=re.sub(".*:","",basic_info.find("div", class_="right").find("span")["style"])   #Green red
            sum_part=basic_info.find("div", class_="right").get_text().replace(" ", "")
            closing_price=float(re.findall(r"\d+.\d+",sum_part)[0])
            fluctuate=float(re.findall(r"\d+.\d+",sum_part)[1])
            total_cjl=float(re.findall(r"\d+.\d+",sum_part)[2])
            total_cjje=float(re.findall(r"\d+.\d+",sum_part)[3])
        except Exception as e:
            continue
        buy_part=soup2.find("table",id="tab-2").find("tbody").find_all("tr")
        data = xlwt.Workbook()
        table = data.add_sheet("lhb",cell_overwrite_ok = True)
        table.write(0, 0, closing_price)
        if zhangdie == "red":
            table.write(0,1,"+"+str(fluctuate)+"%")
        else:
            table.write(0, 1, "-"+str(fluctuate)+"%")
        table.write(0, 2, "成交量: "+str(total_cjl))
        table.write(0, 3, "成交金额: "+str(total_cjje))
        table.write(0, 4, "上榜理由: "+lhb_reason)
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
        print(u"开始爬取",stock_name,u"：请等待")
        yyb_buy_list=[]
        for yyb_index in range(len(buy_part)):
            yyb=buy_part[yyb_index]
            el=yyb.find_all("td")
            order=el[0].get_text()
            yyb_name=yyb.find("div",class_="sc-name").get_text().strip()
            yyb_buy_list.append(yyb_name)
            total_buy=el[2].get_text()
            buy_proportion=el[3].get_text()
            total_sell=el[4].get_text()
            sell_proportion=el[5].get_text()
            net_amount=el[6].get_text()
            table.write(yyb_index+4,0,order)
            table.write(yyb_index+4,1,yyb_name)
            table.write(yyb_index+4,2,total_buy)
            table.write(yyb_index+4,3,buy_proportion)
            table.write(yyb_index+4,4,total_sell)
            table.write(yyb_index+4,5,sell_proportion)
            table.write(yyb_index+4,6,net_amount)
            if buy_proportion != "-" and buy_proportion != "0.00%" and float(re.sub("%","",buy_proportion)) > 0.05:
                average_buy_cost=round(float(total_buy)/(float(buy_proportion.replace("%",""))*total_cjl*0.01),2)
                table.write(yyb_index+4,7,average_buy_cost)
                table.write(yyb_index+4,9,operate_reason(fluctuate, zhangdie, average_buy_cost, closing_price))
            elif buy_proportion != "-" and float(re.sub("%","",buy_proportion)) <= 0.05:
                table.write(yyb_index+4,7,"买入比例过少")
            else:
                table.write(yyb_index+4,7,"-")
            if sell_proportion != "-" and sell_proportion != "0.00%" and float(re.sub("%","",sell_proportion)) > 0.05:
                average_sell_cost=round(float(total_sell)/(float(sell_proportion.replace("%",""))*total_cjl*0.01),2)
                table.write(yyb_index+4,8,average_sell_cost)
            elif sell_proportion != "-" and float(re.sub("%", "", sell_proportion)) <= 0.05:
                table.write(yyb_index+4,8, "卖出比例过少")
            else:
                table.write(yyb_index+4,8,"-")
        detect_famous_yyb(yyb_buy_list,stock_name,"买")

        table.write(10,0,u"卖出前五")
        if len(soup2.find("table", id="tab-4").find("tbody").find_all("tr")) == 6:
            sell_part = soup2.find("table", id="tab-4").find("tbody").find_all("tr")[0:5]
            yyb_sell_list=[]
            for yyb_index in range(len(sell_part)):
                yyb = sell_part[yyb_index]
                el=yyb.find_all("td")
                order=el[0].get_text()
                yyb_name=yyb.find("div",class_="sc-name").get_text().strip()
                yyb_sell_list.append(yyb_name)
                total_buy=el[2].get_text()
                buy_proportion=el[3].get_text()
                total_sell=el[4].get_text()
                sell_proportion=el[5].get_text()
                net_amount=el[6].get_text()
                table.write(yyb_index+11,0,order)
                table.write(yyb_index+11,1,yyb_name)
                table.write(yyb_index+11,2,total_buy)
                table.write(yyb_index+11,3,buy_proportion)
                table.write(yyb_index+11,4,total_sell)
                table.write(yyb_index+11,5,sell_proportion)
                table.write(yyb_index+11,6,net_amount)
                if buy_proportion != "-" and buy_proportion != "0.00%" and float(re.sub("%","",buy_proportion)) > 0.05:
                    table.write(yyb_index+11,7,round(float(total_buy)/(float(buy_proportion.replace("%",""))*total_cjl*0.01),2))
                elif buy_proportion != "-" and float(re.sub("%", "", buy_proportion)) <= 0.05:
                    table.write(yyb_index+11,7, "买入比例过少")
                else:
                    table.write(yyb_index+11,7,"-")
                if sell_proportion != "-" and sell_proportion != "0.00%" and float(re.sub("%","",sell_proportion)) > 0.05:
                    table.write(yyb_index+11,8,round(float(total_sell)/(float(sell_proportion.replace("%",""))*total_cjl*0.01),2))
                elif sell_proportion != "-" and float(re.sub("%", "", sell_proportion)) <= 0.05:
                    table.write(yyb_index+11,8,"卖出比例过少")
                else:
                    table.write(yyb_index+11,8,"-")
            detect_famous_yyb(yyb_sell_list, stock_name, "卖")
        else:
            pass
        data.save(stock_name+"_"+stock_code+".xls")
        print(stock_name,u"爬取结束")
        time.sleep(2)
    else:
        print(u"已经存在",stock_name)




