import datetime
import time
from bs4 import BeautifulSoup
import requests
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.mime.multipart import MIMEMultipart

"""
支持功能：
1）判断最近的交易日：judge_date（）
2）requests+bs的组合
3）自动发送邮件：autoMail() myMail()
"""

def judge_date():
    """
    定位时间到最近的工作日，如周六周日定为周五
    """
    time = datetime.datetime.now()
    if time.hour <= 15:
        time = time- datetime.timedelta(days=1)
    if time.isoweekday() == 7:
        return (time - datetime.timedelta(days=2)).strftime('%Y-%m-%d')
    elif time.isoweekday() == 6:
        return (time - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    else:
        return time.strftime('%Y-%m-%d')


def conn_try_again(function,waittime=3):
    """
    重连：用作装饰器
    """
    retries = 3
    def wrapped(*args, **kwargs):
        nonlocal retries
        try:
            return function(*args, **kwargs)
        except Exception as E:
            if retries > 0:
                retries -= 1
                time.sleep(waittime)
                print("程序将在%s秒后重新运行" %(waittime))
                return wrapped(*args, **kwargs)
            else:
                raise Exception
    return wrapped


def getHtmlPage_GBK(url,cookies=None):
    user_agents = [
        'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
        'Opera/9.25 (Windows NT 5.1; U; en)',
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
        'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
        'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
        'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
        "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",
        "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 "
    ]
    random_user_agent = random.choice(user_agents)
    headers = {
        'User-Agent': random_user_agent,
        "Connection": "keep - alive",
        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
    if cookies == None:
        html = requests.get(url,headers=headers)
    else:
        html = requests.get(url,headers=headers,cookies=cookies)
    html.encoding = 'gbk'
    soup = BeautifulSoup(html.text, 'lxml')
    return soup


def getHtmlPage(url,cookies=None):
    user_agents = [
        'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
        'Opera/9.25 (Windows NT 5.1; U; en)',
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
        'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
        'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
        'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
        "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",
        "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 "
    ]
    random_user_agent = random.choice(user_agents)
    headers = {
        'User-Agent': random_user_agent,
        "Connection": "keep - alive",
        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
    if cookies == None:
        html = requests.get(url,headers=headers)
    else:
        html = requests.get(url,headers=headers,cookies=cookies)
    soup = BeautifulSoup(html.text, 'lxml')
    return soup


def getPage(url,cookies=None):
    user_agents = [
        'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
        'Opera/9.25 (Windows NT 5.1; U; en)',
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
        'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
        'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
        'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
        "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",
        "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 "
    ]
    random_user_agent = random.choice(user_agents)
    headers = {
        'User-Agent': random_user_agent,
        "Connection": "keep - alive",
        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
    if cookies == None:
        html = requests.get(url,headers=headers).text
    else:
        html = requests.get(url,headers=headers,cookies=cookies).text
    return html


def autoMail(subject,content):
    """
    只发送文字信息
    """
    msg_from = 'ttyyzuo@163.com'
    passwd = 'fd10yyer'  # 填入发送方邮箱的授权码
    msg_to = '983823942@qq.com'
    msg = MIMEText(content)
    msg['Subject'] = subject
    msg['From'] = msg_from
    msg['To'] = msg_to
    try:
        s = smtplib.SMTP_SSL("smtp.163.com", 465)
        s.login(msg_from, passwd)
        s.sendmail(msg_from, msg_to, msg.as_string())
        print("发送成功")
        s.quit()
    except smtplib.SMTPException:
        print("发送失败")


def myMail(subject,content,graphs=None,graphsName=None,files=None,filesName=None):
    """
    发送文字信息和附件，附件支持图片和文件
    待解决问题：中文名的乱码
    """
    msg_from = 'ttyyzuo@163.com'
    passwd = 'fd10yyer'  # 填入发送方邮箱的授权码
    msg_to = '983823942@qq.com'
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = msg_from
    msg['To'] = msg_to
    msg.attach(MIMEText(content, 'plain', 'utf-8'))

    if graphs:
        if len(graphs) != len(graphsName):
            return "图片列表与图片名列表长度不匹配"
        else:
            for graph, graphName in zip(graphs, graphsName):
                with open(graph, 'rb') as f:
                    mime = MIMEBase('image', 'png', filename=graphName)
                    mime.add_header('Content-Disposition', 'attachment', filename=graphName)
                    mime.add_header('Content-ID', '<0>')
                    mime.add_header('X-Attachment-Id', '0')
                    mime.set_payload(f.read())
                    encoders.encode_base64(mime)
                    msg.attach(mime)
    else:
        pass

    if files:
        if len(files) != len(filesName):
            return "文件列表和文件名列表长度不匹配"
        else:
            for file, fileName in zip(files, filesName):
                mime = MIMEText(open(file, 'rb').read(), 'base64', 'utf-8')
                mime["Content-Type"] = 'application/octet-stream'
                # 这里的filename可以任意写，写什么名字，邮件中显示什么名字
                mime["Content-Disposition"] = "attachment; filename=%s" % (fileName)
                msg.attach(mime)
    else:
        pass

    try:
        s = smtplib.SMTP_SSL("smtp.163.com", 465)
        s.login(msg_from, passwd)
        s.sendmail(msg_from, msg_to, msg.as_string())
        print("发送成功")
        s.quit()
    except smtplib.SMTPException:
        print("发送失败")

