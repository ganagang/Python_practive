# @filename: ChuangYeBang.py
# -*- coding: utf-8 -*-
# @Author: Li Gang
# @Date:   2019-03-16 18:27:21
# @Last Modified by:   Li Gang
# @Last Modified time: 2019-03-17 11:01:39
from requests_html import HTMLSession
import requests
from lxml import etree
import os
""" 爬虫 创业邦 创业公司信息爬取
网页url = 'http://www.cyzone.cn/company/list-0-0-1-0-0/0'
爬取页面中的创业公司，融资阶段，创业领域，成立时间和创业公司的链接信息。
使用到requests, json, codecs, lxml等库
requests用于访问页面，获取页面的源代码
josn库用于写入json文件保存到本地
codecs库用于读写文件时编码问题
lxml用于解析网页源代码，获取信息
"""
import requests
import json
import codecs
from lxml import etree


class chuangYeBang:
    def __init__(self,url=""):
        self._url = url
        self._html_content = self.get_html(url)

    def get_html(self, url):
        """ get_html
        得到网页源代码，返回unicode格式

        @param: url
        @return: r.text <type 'unicode'>
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64)"
            "AppleWebKit/537.36 (KHTML, like Gecko)"
            "Chrome/63.0.3239.26 Safari/537.36 Core/1.63.6721.400"
            "QQBrowser/10.2.2243.400"
        }
        try:
            r = requests.get(url, headers=headers)
        except:
            print(r.status_code)
        return r.text

    def get_company_data(self, text):
        """ get_company_data
        得到网页信息
        eg: [{
            "companyUrl": "http://www.cyzone.cn/r/20180824/68979.html", 
            "stage": "天使轮", 
            "type": "硬件", 
            "time": "2014-12-19", 
            "companyName": "成都思科"
        }]
        @param: text 网页的源代码unicode格式源代码
        @return: list 一个页面所有的公司信息 列表中每一个元素为存入信息的字典
        """
        html = etree.HTML(text)  # 解析网页
        company_name_list = html.xpath(
            '//td[@class="table-company-tit"]/a/span/text()' # 所有公司名
        )
        # 得到带有class"table-company-tit"...属性的td标签下的a标签下的span标签的内容，返回为一个列表
        # 公司融资情况网页
        company_url_list = html.xpath(
            '//td[@class="table-company-tit"]/a/@href'
        )
        """
        得到带有..属性的td标签下的a标签中hred的内容
        为一个url
        <a href="http://www.cyzone.cn/r/20180823/68963.html" target="_blank">
        """        
        
        stage_list = html.xpath('//td[@class="table-stage"]/@data-stage')
        # 同上 不解释了 得到stage
        company_stage_list = []
        for company_stage in stage_list:
            company_stage = company_stage.strip(',') if company_stage else None
            company_stage_list.append(company_stage)
        print(company_stage_list)  # get stage list
        print(len(company_stage_list))
        # 所属行业
        company_type_list = html.xpath('//td[@class="table-type"]')
        type_list = []
        for company_type in company_type_list:
            company_type = company_type.xpath('./a/text()')[0] \
                if company_type.xpath('./a/text()') else None
            type_list.append(company_type)
        print(type_list)
        print(len(type_list))

        """
        遍历每个列表，取出列表对应的元素，组成我们需要的字典
        """
        ret_company_dict = {}
        print("一共 "+str(len(company_name_list)) + " 家公司，它们是：")
        maxlen = max(list(map(len,company_name_list)))
        company_time_list = html.xpath('//td[@class="table-time"]/text()')
        for n, u,s, t,d in zip(company_name_list, company_url_list,company_stage_list,type_list,company_time_list):
            u = str(u) if str(u).startswith('http') else "https://" + str(u)
            print(f'{n}', ' '*(maxlen+1-len(n)), u, "  ", s, "  ", t, "  ", d)
            single_company = {}
            single_company['companyUrl'] = u
            single_company['companyName'] = n
            single_company['type'] = t
            single_company['stage'] = s
            single_company['time'] = d
            tmp = u.split('/')[-1].split('.')[0]
            ret_company_dict[tmp] = single_company
        return ret_company_dict

    def write_in_json(self, data):
        """ write_in_json
        写入json文件
        codecs  # 用于编码，同一用utf-8格式编码
        json.dumps  # 方法用于将字典或者列表转换成json字符串格式，存入json文件
        indent=2  # json文件中显示的方法，显示为2字符的缩进
        .decode('unicode_escape')  # 在json文件中显示中文，不会显示utf-8编码，方便看。
        """
        json_data = bytes(json.dumps(data, indent=2),encoding='utf-8').decode('unicode_escape')
        with codecs.open('./chuangYeBang.json', 'w', 'utf-8') as fw:
            fw.write(json_data)

    def run(self):
        s = self.get_company_data(self._html_content)
        self.write_in_json(s)
        return s

class getCompanyInfo:
    """ 得到每个公司详细信息 """
    def __init__(self):
        pass

    def get_html_text(self, url):
        headers = {}
        r = requests.get(url, headers=headers)
        print(r.status_code)
        return r.text

    def get_company_info(self, text):
        pass


if __name__ == "__main__":
    url = 'http://www.cyzone.cn/company/list-0-0-1-0-0/0'
    cyb = chuangYeBang(url)
    data = cyb.run()
