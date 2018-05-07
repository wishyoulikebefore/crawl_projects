"""
在之前的版本上，用pyquery替代bs4
事实证明pyquery比bs4爽多了
可以利用class的特定字段避免V1版本中“推荐电影或TV”格式的部分不同
利用特定字符“Views”排除tr节点中无关的首尾部分
"""

import requests
from bs4 import BeautifulSoup
import time
import random
import multiprocessing
from pyquery import PyQuery as pq

source_url = "http://pt.vm.fudan.edu.cn/index.php?board="
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
    "Connection": "keep-alive",
    "Cookie": "amlbcookie=02; iPlanetDirectoryPro=AQIC5wM2LY4SfcyLCu9DL7YdS2xd4Q8h0JnWA%2FQz6Zhq3T0%3D%40AAJTSQACMDI%3D%23; UM_distinctid=162f064c9e247a-0518159f6ce07-33677104-1fa400-162f064c9e41266; SMFCookie345=a%3A4%3A%7Bi%3A0%3Bs%3A6%3A%22114944%22%3Bi%3A1%3Bs%3A40%3A%22a0e45c977ad75e4e589ad5caf505ccc374c7ff40%22%3Bi%3A2%3Bi%3A1525764425%3Bi%3A3%3Bi%3A0%3B%7D; PHPSESSID=fnl4g5onff4t414o0j848fnuo4",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36"
}

def start_crawl(indexNu):
    start_url = source_url+str(indexNu)
    html_text = requests.get(start_url,headers=headers).text
    doc = pq(html_text)
    pageNum = doc(".pagelinks .navPages").text().split()[-2]
    forum = doc('.navigate_section .last span').text().split()[0]
    output = open("/Users/zty/Downloads/PT%s板块.txt" %(forum),"a")
    print("开始爬取%s板块，共%s页" %(forum,pageNum))
    output.write("共%s页\n" %(pageNum))
    crawl_forum(indexNu,pageNum,output)

def crawl_forum(indexNu,pageNum,output):
    for nu in range(int(pageNum)):
        offset = "%.*f" % (max(1, len(str(25 * nu))), int(indexNu) + 25 * nu / (10 ** len(str(25 * nu))))
        target_url = source_url + str(offset)
        html = requests.get(target_url, headers=headers)
        doc = pq(html.text)
        content = doc("#sp_main tbody tr:contains(Views)")
        for item in content.items():
            Name = item(".subject span a").text()
            linkUrl = item(".subject span a").attr("href")
            viewNum = item(".stats").text().split()[2]
            downloadSum = calDownloadTimes(linkUrl)
            output.write("%s\t%s\t%s\n" % (Name,viewNum,downloadSum))
            print("%s\t%s\t%s" % (Name,viewNum,downloadSum))
        time.sleep(1 + random.random())
    print("%s爬取结束" %(indexNu))
    output.close()

def calDownloadTimes(url):
    sum = 0
    html = requests.get(url, headers=headers)
    doc = pq(html.text)
    torrents = doc(".torrent_table td:nth-child(5)")
    for torrent in torrents.items():
        downloadTimes = torrent.text().split("/")[-1]
        sum += int(downloadTimes)
    return sum

if __name__ == "__main__":
    targetForum = [23.0, 24.0, 25.0, 17.0, 29.0, 28.0, 27.0]
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    for indexNu in targetForum:
        pool.apply_async(start_crawl,(indexNu,))
    pool.close()
    pool.join()
