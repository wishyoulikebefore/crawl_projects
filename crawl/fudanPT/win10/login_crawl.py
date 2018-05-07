"""
此脚本只支持单进程，添加多进程出问题，可能是因为requests.Session()的原因
"""
import requests
import time
import random
from pyquery import PyQuery as pq

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    "Connection": "keep - alive",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Host": "pt.vm.fudan.edu.cn",
    "Referer": "https://pt.vm.fudan.edu.cn/index.php?PHPSESSID=dofo49hvmhus41fov34prd5bc5&action=login"
    }

data = {"user":"10301020019@fudan.edu.cn",
        "passwrd":"1q2w3e4r",
        "cookielength":"1440",
        "hash_passwrd":"",
        }

post_url = "https://pt.vm.fudan.edu.cn/index.php?action=login2"
source_url = "http://pt.vm.fudan.edu.cn/index.php?board="

s = requests.Session()
response1 = s.post(post_url, data=data, headers=headers)

def start_crawl(indexNu):
    start_url = source_url+str(indexNu)
    html_text = s.get(start_url,headers=headers,cookies=response1.cookies).text
    doc = pq(html_text)
    pageNum = doc(".pagelinks .navPages").text().split()[-2]
    forum = doc('.navigate_section .last span').text().split()[0]
    output = open("D:/python/python学习手册/项目/复旦PT热门分析/PT%s板块.txt" %(forum),"a")
    print("开始爬取%s板块，共%s页" %(forum,pageNum))
    output.write("共%s页\n" %(pageNum))
    crawl_forum(indexNu,pageNum,output)

def crawl_forum(indexNu,pageNum,output):
    for nu in range(int(pageNum)):
        offset = "%.*f" % (max(1, len(str(25 * nu))), int(indexNu) + 25 * nu / (10 ** len(str(25 * nu))))
        target_url = source_url + str(offset)
        html = s.get(target_url, headers=headers,cookies=response1.cookies)
        doc = pq(html.text)
        content = doc("#sp_main tbody tr:contains(回复)")
        for item in content.items():
            Name = item(".subject span a").text()
            linkUrl = item(".subject span a").attr("href")
            viewNum = item(".stats").text().split("\n")[1]
            downloadSum = calDownloadTimes(linkUrl)
            output.write("%s\t%s\t%s\n" % (Name,viewNum,downloadSum))
            print("%s\t%s\t%s" % (Name,viewNum,downloadSum))
        time.sleep(1 + random.random())
    print("%s爬取结束" %(indexNu))
    output.close()

def calDownloadTimes(url):
    sum = 0
    html = s.get(url, headers=headers,cookies=response1.cookies)
    doc = pq(html.text)
    torrents = doc(".torrent_table td:nth-child(5)")
    for torrent in torrents.items():
        downloadTimes = torrent.text().split("/")[-1]
        sum += int(downloadTimes)
    return sum

if __name__ == "__main__":
    targetForum = [23.0, 24.0, 25.0, 17.0, 29.0, 28.0, 27.0]
    for nu in targetForum:
        start_crawl(nu)
