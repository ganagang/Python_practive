# @filename: douban_music.py
# -*- coding: utf-8 -*-
# @Author: Li Gang
# @Date:   2019-03-17 18:51:01
# @Last Modified by:   Li Gang
# @Last Modified time: 2019-03-18 18:16:53
# 修改自 https://segmentfault.com/a/1190000015197060
# 使用MongoDb数据库：scrapy_db下的music_tbl表保存数据。没使用代理。
# 
# 
import requests
from lxml import etree
import re
import pymongo
import time
import random
from fake_useragent import UserAgent
ua =UserAgent()
song_id = 0
client = pymongo.MongoClient('localhost', 27017)
mydb = client['scrapy_db']
musictop = mydb['music_tbl']

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
}
headers = {'User-Agent': ua.random}   #使用随机的UA


# url是豆瓣音乐排行250的各页的网址之一
# 返回一个列表
def get_url_music(url):
    html = requests.get(url, headers=headers)
    selector = etree.HTML(html.text)
    music_hrefs = selector.xpath('//a[@class="nbg"]/@href')
    music_list = []
    for music_href in music_hrefs:
        music_list.append(get_music_info(music_href))
    return music_list

# 辅助函数，提取音乐的各项信息，如 日期，专辑等
# track_info is a string containing combined of each piece
# of info a song has. return a diction of each piece of info
def get_song_info(track_info):
    s_all = re.sub(r'[ ]{2,}','', track_info)
    s_all = re.sub(r'\n{2,}$', '\n',s_all, re.S)
    s_all = [i.replace('\xa0','') for i in s_all.split('\n') if i!='']
    s_all = ' '.join(s_all)
    pat = r'\s?(\w+:){1,1}'
    s1 = re.findall(pat, s_all)
    s2 = re.split('|'.join(s1), s_all)
    d ={}
    for t1,t2 in zip(s1,s2[1:]):
        d[t1.strip(':').strip()] = t2.strip()
    return d

# 把某曲目的内容解析（查询其url），并把结果插入数据库
# 返回字典形式的曲目基本信息
def get_music_info(url):    
    html = requests.get(url, headers=headers)
    #html = html.content.decode(html.encoding, errors='ignore').encode('utf-8').decode('utf-8')
    html = html.text
    selector = etree.HTML(html)
    info = {}
    global song_id
    info['_id'] = song_id
    song_id += 1
    title = selector.xpath('//*[@id="wrapper"]/h1/span/text()')[0]
    info['歌名'] = title.strip()
    score = selector.xpath('//*[@id="interest_sectl"]/div/div[2]/strong/text()')[0]
    info['评分'] = score
    node = selector.xpath('.//div[@id="info"]')[0]
    s_all = node.xpath('string(.)').strip()
    info.update(get_song_info(s_all))
    info['url'] = url
    print(info)
    musictop.insert_one(info)
    return info

if __name__ == '__main__':
    """
    # 这里要打开的话，就会从网址爬取前250首曲目
    urls = ['https://music.douban.com/top250?start={}'.format(str(i)) for i in range(0, 250, 25)]
    for url in urls:
        print(url)
        get_url_music(url)
        time.sleep(random.randrange(2,5))
    """
    # 下面是写好数据库后，从数据库提取信息来显示
    res =musictop.find() # .limit(10)
    for item in res:
        for k_str, v_str in item.items():
            print("【",k_str,"】:",v_str)
        print('-'*50)    
    
    print('done!')