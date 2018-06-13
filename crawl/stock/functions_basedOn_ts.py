import tushare as ts
import datetime
import itertools

def getConZtNum(stockCode,period=20):
    """
    获取个股连续涨停数目
    MGD,竟然会出现某些股票当日数据不更新;TM还有的数据没有
    这个信息更新比较慢，需要交叉验证一下
    """
    today = datetime.datetime.now()
    preDay = today - datetime.timedelta(days=period)
    df = ts.get_k_data(stockCode, start=preDay.strftime('%Y-%m-%d'), end=today.strftime('%Y-%m-%d'))
    if df.empty:
        print("%s没有数据" %(stockCode))
        return 1
    else:
        closeList = list(df["close"])
        percentList = []
        for nu in range(len(closeList)-1):
            percent = (closeList[nu+1]/closeList[nu]-1)*100
            percentList.append(percent)
        reversedPercent = percentList[::-1]
        num = len([item for item in itertools.takewhile(lambda x: x > 9.9, reversedPercent)])
        if list(df["date"])[-1] == today.strftime('%Y-%m-%d'):
            pass
        else:
            num += 1
        return num





