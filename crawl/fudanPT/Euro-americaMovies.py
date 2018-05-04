import requests
from bs4 import BeautifulSoup
import time
import random

"""
欧美电影板块，每个板块有个编号，每一页是0.25递增，超过1后自动退一位，确保不干扰其它板块
"""

origin_url = "http://pt.vm.fudan.edu.cn/index.php?board="
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
    "Connection": "keep-alive",
    "Cookie": "amlbcookie=02; iPlanetDirectoryPro=AQIC5wM2LY4SfcyLCu9DL7YdS2xd4Q8h0JnWA%2FQz6Zhq3T0%3D%40AAJTSQACMDI%3D%23; UM_distinctid=162f064c9e247a-0518159f6ce07-33677104-1fa400-162f064c9e41266; SMFCookie345=a%3A4%3A%7Bi%3A0%3Bs%3A6%3A%22114944%22%3Bi%3A1%3Bs%3A40%3A%22a0e45c977ad75e4e589ad5caf505ccc374c7ff40%22%3Bi%3A2%3Bi%3A1525308207%3Bi%3A3%3Bi%3A0%3B%7D; PHPSESSID=91tlol90tgl3u72pfjicu7avr0",
    "Host": "pt.vm.fudan.edu.cn",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36"
}
output = open('/Users/zty/Downloads/PT欧美电影.txt',"a")

for nu in range(299):
    offset = "%.*f" %(max(1,len(str(25*nu))),24.0 + 25*nu/(10**len(str(25*nu))))
    target_url = origin_url+str(offset)
    html = requests.get(target_url,headers=headers)
    content = BeautifulSoup(html.text,"lxml").find("tbody").find_all("tr")
    for piece in content[1:]:
        try:
            movieName = piece.find("strong").get_text()
            viewNum = piece.find(class_="stats stickybg").get_text().split("\n")[3].split()[0]
        except:
            try:
                movieName = movieName = piece.find("span").get_text()
                viewNum = piece.find(class_="stats windowbg").get_text().split("\n")[3].split()[0]
            except:
                break
        output.write("%s\t%s\n" %(movieName,viewNum))
        if int(viewNum) > 5000:
            print(movieName)
            print(viewNum.strip())
    time.sleep(1+random.random())
