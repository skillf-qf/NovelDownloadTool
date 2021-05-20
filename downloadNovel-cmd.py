#!/usr/bin/env python
# coding=utf-8
'''
Author: skillf
Date: 2021-04-27 17:15:59
LastEditTime: 2021-04-29 15:06:20
FilePath: \\NovelDownloadTool\\downloadNovel-cmd.py
'''

import requests
from bs4 import BeautifulSoup
import time
import os.path
import shutil
import sys

pathSeparator = '\\'
currentRootDir = os.path.dirname(sys.argv[0])
downloadPath = currentRootDir + pathSeparator + 'Downloads'

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) \
        Chrome/55.0.2883.87 Safari/537.36"
}
#prefixion = 'https://www.37zww.net/0/893/'

def getUrl(url):
    # timeout(3,7)表示的连接时间是3秒，响应时间是7秒。
    #req = requests.get(url,headers=headers)
    req = requests.get(url,headers=headers,timeout=(3,7))
    #req.encoding = 'utf-8'
    req.encoding = 'gbk'
    html=req.text
    bs=BeautifulSoup(html,'lxml')
    return bs

def getNovelInfo(url):
    bs =  getUrl(url)
    title = bs.find_all(name='div',attrs={"id":"info"})[0].h1.text
    infos = bs.find_all(name='div',attrs={"id":"info"})[0].find_all('p')
    infoList = []
    infoList.append(title)
    # 网页源代码中的&nbsp; 的utf-8 编码是：\xc2 \xa0，转换为Unicode字符为：\xa0，
    # 当显示到DOS窗口上的时候，转换为GBK编码的字符串，
    # 但是\xa0这个Unicode字符没有对应的 GBK 编码的字符串，所以出现错误。
    # 因此必须转换成常规字符串，这里信息并不重要（\xa0在'：' 之前，而这里只保留 '：' 之后的信息）所以可以用' '空格替换，其他时候看情况处理。
    for info in infos:
        infoList.append(info.text.replace(u'\xa0', u' ').split('：')[1])

    sectionList = bs.findAll(name='div',attrs={"id":"list"})[0].find_all('dd')
    i = 0
    sectionInfo = {}
    for sibling in sectionList:
        if sibling.find('a') is not None:
            #print(sibling.find('a'))
            section = sibling.find('a').text
            #print(section)
            link = sibling.find('a')['href']
            sectionInfo[section] = url + link
    #for section,link in sectionInfo.items():
    #    print(section,' : ',link)
    # infoList : [小说名, 作者, 连载信息, 最新章节, 最新更新时间]
    # 比如：['乡村小神医', '赤焰神歌', '连载中', '第两千四百八十六章 破壳之战（大结局）', '2021-01-31 04:54']
    return infoList,sectionInfo

def singleSection(url,section_name):
    bs = getUrl(url)
    contentList = []
    #print(url)
    #print(bs.find_all(name='div',attrs={"id":"content"}))
    content = bs.find_all(name='div',attrs={"id":"content"})[0].text
    tempstr = content.replace(u'\xa0', u'x')
    contentList = tempstr.split('xxxx')
    #contentList = content.split('\xa0\xa0\xa0\xa0')
    newList = []
    newList.append(section_name)
    for i in contentList:
        newList.append('  '+i+'\n')

    newList.append('\n\n')
    #print(newList)
    #exit()
    return newList

def progressBar(section_info,current_count,content_length,start_time):
    """
    # show eg:
    Downloading: [■■------------------------------------------------]  4 % Time: 00:02:02 第一百一十一章 苗一刀
    """
    # 进度条长度
    scale = 25 
    #print(current_count)
    load = "■" * (current_count*scale// content_length)
    empty = "-" * (scale - current_count*scale//content_length)
    dr = current_count*scale//content_length*(100/scale)
    #elapsedTime = time.perf_counter() - start_time
    elapsedTime = timeTransfer(int("{:.0f}".format(time.perf_counter() - start_time)))
    # 多余的空格为了覆盖上一行预留的字符串
    # ^表示中间对齐 后面的数字表示位数. {:^10d} 中间对齐 (宽度为10)
    # ＂ <＂、＂>＂、＂^＂符号表示左对齐、右对齐、居中对齐
    # .nf 表示保留小数点位数,n表示小数点的位数 {:.2f} 3.14 保留小数点后两位
    # {:^3.0f} ： 宽度为 3，中间对齐默认空格填充，四舍五入
    #print("\rDownloading: [{}{}] {:^3.0f}% Time: {:0>2d}:{:0>2d}:{:0>2d}  正在下载：{}          ".format(load,empty,dr,elapsedTime[0],elapsedTime[1],elapsedTime[2],section_info),end="")
    print("\rDownloading: [{}{}] {:^3.0f}% Time: {:0>2d}:{:0>2d}:{:0>2d} {}          ".format(load,empty,dr,elapsedTime[0],elapsedTime[1],elapsedTime[2],section_info),end="")

def timeTransfer(t):
    h = t // 3600
    m = (t % 3600) // 60
    s = (t % 3600)% 60
    return(h,m,s)

def saveContent(novel_name,novel_author,content_list,save_status):
    # content_list: 0: section_name, [1:] : content
    savePath = downloadPath+ pathSeparator + novel_name
    if not os.path.exists(downloadPath):
        os.mkdir(downloadPath)

    if not save_status:
        if os.path.exists(savePath):
            shutil.rmtree(savePath)
            #print('rm',savePath, '\nDone.')
            time.sleep(1)
        os.mkdir(savePath)
    
    #print('正在下载：',content_list[0])
    file_name = savePath + pathSeparator + novel_name + '-' + 'by' + novel_author + '.txt'
    for line in content_list:
        with open(file_name, 'a+') as f:
            f.write(line)

def logFile(novel_name,wrong_location,error_text):
   
    savePath = downloadPath + pathSeparator + novel_name
    #print('正在下载：',content_list[0])
    log_name = savePath + pathSeparator + novel_name + '.log'
    gap = '=========================================='
    time_format = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    with open(log_name, 'a+') as f:
        f.write(gap + '\n' +time_format+' : ' + error_text + '\n    ' + wrong_location + '\n' + gap)

def showInfo(url):
    """
    # show eg:
    ==========================================
    正在下载：乡村小神医
    作    者：赤焰神歌
    状    态：连载中
    最新更新：第两千四百八十六章 破壳之战（大结局）
    最后更新：2021-01-31 04:54
    ==========================================
    """
    novel_info = getNovelInfo(url)
    novel_name = novel_info[0][0]
    novel_author = novel_info[0][1]
    novel_status = novel_info[0][2]
    novel_last_section = novel_info[0][3]
    novel_update_time = novel_info[0][4]
    novel_section = novel_info[1]
    #print('正在下载：',novel_name,'by',novel_author, '最新章节：{}'.format(novel_last_section))
    print('==========================================')
    print("正在下载：{}\n作    者：{}\n状    态：{}\n最新更新：{}\n最后更新：{}".format(novel_name,novel_author,novel_status,novel_last_section,novel_update_time))
    print('==========================================')
    return novel_name,novel_author,novel_section

def showBox(num,title,author,status,last_update_section,last_update_time):
    '''
    小说题目：乡村小神医
    作    者：赤焰神歌
    状    态：连载中
    最新更新：第两千四百八十六章 破壳之战（大结局）
    最后更新：2021-01-31 04:54

    '''
    print('小说编号： {}\n小说名称： {}\n作    者： {}\n状    态： {}\n最新章节： {}\n最后更新： {}'.format(num,title,author,status,last_update_section,last_update_time))
    print('==========================================')

def searchNovel(novel_name):
    urlBase = 'https://www.37zww.net/modules/article/search.php?searchtype=articlename&searchkey='
    s = str((novel_name.encode('gbk'))).replace('\\x','%').split('\'')[1]
    #print(type(s),':',s.upper())
    #print(urlBase + s.upper(),'\n')
    url = urlBase + s.upper()
    bs=getUrl(url)
    result = bs.find_all('meta')
    #result = bs.find_all('title')[0].text
    #print(result.find('三七中文网'))
    resultBox = bs.find_all(name='table',attrs={"class":"grid"}) #搜索框列表
    #print(resultBox)
    novelUrlList = []
    if resultBox:
        infoList = resultBox[0].find_all('tr')
        if len(infoList) > 1:
            print("总共搜到小说 {} 本".format(len(infoList)-1))
            print('==========================================')
            novelNum = 0
            for i in infoList[1:]:
                novelNum = novelNum + 1
                #sectionList = bs.findAll(name='div',attrs={"id":"list"})[0].find_all('dd')
                singleNovel = i.find_all('td')
                #print(i)

                novelName = singleNovel[0].text
                novelAuthor = singleNovel[2].text
                novelStatus = singleNovel[5].text
                novelLastSection = singleNovel[1].text
                novelUpdateTime = singleNovel[4].text
                
                novelUrl = singleNovel[0].find_all('a')[0]['href']
                novelUrlList.append(novelUrl)
                showBox(novelNum,novelName,novelAuthor,novelStatus,novelLastSection,novelUpdateTime)
            inputNum = int(input("请选择想要下载的小说编码："))
            url = novelUrlList[inputNum-1]
        else:
            #print(infoList)
            print("未搜到小说：",novel_name)
            url = ''
    else:
        #print(result)
        novelNum = 1
        novelName = result[11]['content']
        novelAuthor = result[10]['content']
        novelStatus = result[14]['content']
        novelLastSection = result[16]['content']
        novelUpdateTime = result[15]['content']        
        novelUrl = result[12]['content']
        novelUrlList.append(novelUrl)

        print("总共搜到小说 {} 本".format(novelNum))
        print('==========================================')
        showBox(novelNum,novelName,novelAuthor,novelStatus,novelLastSection,novelUpdateTime)
        inputNum = int(input("请选择想要下载的小说编码："))
        url = novelUrlList[inputNum-1]
    return url

def inputHandle():
    url_check = 0
    #inputStr = input("请输入你想要下载的小说网址或者文章名称：")
    while(not url_check):
        inputStr = input("请输入你想要下载的小说网址或者文章名称：")
        #print(url.find('https://www.37zww.net/'))
        if inputStr.find('https://www.37zww.net/') >= 0:
            url = inputStr
            if url:
                url_check = 1
        else:
            url = searchNovel(inputStr)
            if url:
                url_check = 1

    return url


if __name__ == '__main__':
    print("三七中文网 小说下载 downloadNovel-V1.2 程序已启动 (′▽`〃)\n")

    # 三七中文网 小说
    url = inputHandle()
    info = showInfo(url)
    novelName = info[0]
    novelAuthor = info[1]
    novelSections = info[2]
    saveStatus = 0
    currentCount = 0
    start = time.perf_counter()
    for section,link in novelSections.items():
        #print(section)
        currentCount = currentCount + 1
        try:
            content = singleSection(link,section)
        except IOError as e:
            print("Error: 网页请求失败：",e)
            print("小说下载失败：",section,link)
            logFile(novelName,repr(e),"小说下载失败：{} {}".format(section,link))
            try:
                print("Retry: 正在尝试重新下载 。。。",section)
                content = singleSection(link,section)
                print("Retry: 重新下载成功 ",section)
                logFile(novelName,repr(e),"重新下载成功 ：{} {}".format(section,link))
            except IOError as e:
                print("Error: 重试失败：",e)
                print("Error: 重试失败章节：",section,link)
                logFile(novelName,repr(e),"重新下载失败：{} {}".format(section,link))

        saveContent(novelName,novelAuthor,content,saveStatus)
        progressBar(section,currentCount,len(novelSections),start)
        saveStatus = 1
        #print(section,':',link)
        time.sleep(0.3)
        #break
    print("\n\n下载完成！\n\n")
    os.system('pause')
