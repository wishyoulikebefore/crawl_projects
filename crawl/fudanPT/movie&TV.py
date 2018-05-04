import requests
from bs4 import BeautifulSoup
import time
import random
import multiprocessing

source_url = "http://pt.vm.fudan.edu.cn/index.php?board="
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
    "Connection": "keep-alive",
    "Cookie": "amlbcookie=02; iPlanetDirectoryPro=AQIC5wM2LY4SfcyLCu9DL7YdS2xd4Q8h0JnWA%2FQz6Zhq3T0%3D%40AAJTSQACMDI%3D%23; UM_distinctid=162f064c9e247a-0518159f6ce07-33677104-1fa400-162f064c9e41266; SMFCookie345=a%3A4%3A%7Bi%3A0%3Bs%3A6%3A%22114944%22%3Bi%3A1%3Bs%3A40%3A%22a0e45c977ad75e4e589ad5caf505ccc374c7ff40%22%3Bi%3A2%3Bi%3A1525495916%3Bi%3A3%3Bi%3A0%3B%7D; PHPSESSID=rte56vmuso9jel6adlfssd60k1",
    "Host": "pt.vm.fudan.edu.cn",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36"
}
targetForum = [23.0,24.0,25.0,17.0,29.0,28.0,27.0]

def start_crawl(indexNu):
    start_url = source_url+str(indexNu)
    html_text = requests.get(start_url,headers=headers).text
    pageNum = BeautifulSoup(html_text,"lxml").find("div",class_="pagelinks").find_all("a")[-3].get_text()
    forum = BeautifulSoup(html_text,"lxml").find("div",class_="navigate_section").find_all("li")[-1].find("span").get_text()
    output = open("/Users/zty/Downloads/PT%s板块.txt" %(forum),"a")
    print("开始爬取%s板块，共%s页" %(forum,pageNum))
    output.write("共%s页\n" %(pageNum))
    crawl_forum(indexNu,pageNum,output)

def crawl_forum(indexNu,pageNum,output):
    for nu in range(int(pageNum)):
        offset = "%.*f" % (max(1, len(str(25 * nu))), int(indexNu) + 25 * nu / (10 ** len(str(25 * nu))))
        target_url = source_url + str(offset)
        html = requests.get(target_url, headers=headers)
        content = BeautifulSoup(html.text, "lxml").find("tbody").find_all("tr")
        for piece in content[1:-1]:
            try:
                sourceName = piece.find("strong").get_text()
                linkUrl = piece.find("strong").find("a")["href"]
                viewNum = piece.find(class_="stats stickybg").get_text().split("\n")[3].split()[0]
                downloadSum = calDownloadTimes(linkUrl)
                output.write("%s\t%s\t%s\n" % (sourceName, viewNum, downloadSum))
                print("%s\t%s\t%s" % (sourceName, viewNum, downloadSum))
            except:
                try:
                    sourceName = piece.find("span").get_text()
                    linkUrl = piece.find("span").find("a")["href"]
                    viewNum = piece.find(class_="stats windowbg").get_text().split("\n")[3].split()[0]
                    downloadSum = calDownloadTimes(linkUrl)
                    output.write("%s\t%s\t%s\n" % (sourceName, viewNum, downloadSum))
                    print("%s\t%s\t%s" % (sourceName, viewNum, downloadSum))
                except:
                    continue
        time.sleep(1 + random.random())
    print("%s爬取结束" %(indexNu))
    output.close()

def calDownloadTimes(url):
    sum = 0
    html = requests.get(url, headers=headers)
    torrents = BeautifulSoup(html.text, "lxml").find("div",class_="torrent_table").find("tbody").find_all("tr")
    for torrent in torrents:
        downloadTimes = torrent.find_all("td",class_="icon")[-1].get_text().split("/")[-1]
        sum += int(downloadTimes)
    return sum

if __name__ == "__main__":
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    for indexNu in targetForum:
        pool.apply_async(start_crawl,(indexNu,))
    pool.close()
    pool.join()
