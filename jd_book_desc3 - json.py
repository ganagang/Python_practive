# @filename: jd_book_desc3.py
# -*- coding: utf-8 -*-
# @Author: Li Gang
# @Date:   2019-03-17 10:57:42
# @Last Modified by:   Li Gang
# @Last Modified time: 2019-03-17 12:14:29
# 京东图书无法从网页正确爬取，因为它要动态加载。智能通过javascript中返回的内容来爬取
import requests
from lxml import etree
import json
import re
class jd_book():
    def __init__(self,book_id=11461683):
        self._bookid = book_id
        u = r'http://dx.3.cn/desc/{}?cdn=2'
        self._url = u.format(book_id)
        self._pageurl = "http://item.jd.com/"+ str(book_id) +".html"
        self._html = self.transform()
        self._data = {"ID":book_id}
        self._data.update(self.book_detail_page())
        self._data.update(self.extract_info())        

    def book_detail_page(self):  # 从书籍销售主页爬取书籍主要资料（ISBN,出版时间等)
        s = self.get_html(self._pageurl)
        doc_root = etree.HTML(s)
        book_keywords = doc_root.xpath('//head/meta[@name="keywords"]/@content')
        self._booktitle = book_keywords[0].split(',')[0]
        section = doc_root.xpath('//*[@id="detail"]//ul[@class="p-parameter-list"]/li')
        d ={'书名':self._booktitle}
        for e in section:
            seg = ""            
            if e.xpath('.//a'): # for publisher, and brand
                l = e.xpath('./text()')   # LI 下的文本('出版社：'或'品牌：')
                publisher = e.xpath('.//a/text()') # str list,for publisher, and brand（a下的文本）
                #print(l,''.join(publisher))
                seg = l[0].strip() + publisher[0] if publisher else l[0].strip() 
            else:
                for i in e.xpath('./text()'):
                    seg += str(i)
            #d[x[0]] = x[1]
            tmp = seg.strip().split('：')
            d[tmp[0]] = tmp[1].strip().lstrip('，')        
        return d
         

    def get_html(self, url):
        """ get_html
        得到网页源代码，返回str格式
        @param: url
        @return: r.text <type 'unicode'> ：python中字符都是unicode形式
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64)"
            "AppleWebKit/537.36 (KHTML, like Gecko)"
            "Chrome/63.0.3239.26 Safari/537.36 Core/1.63.6721.400"
            "QQBrowser/10.2.2243.400"
        }
        try:
            r = requests.get(url, headers=headers, timeout=3)
            if r.encoding == 'ISO-8859-1':
                r.encoding = r.apparent_encoding
            r.raise_for_status
        except requests.exceptions.ConnectionError:
            print(r.status_code, " 连接错误！")
        except requests.exceptions.ConnectTimeout:
            print(r.status_code, " 连接超时！")
        return r.content.decode(r.encoding, errors='ignore')

    # 从网址返回的字串提取html block
    def transform(self):
        s = self.get_html(self._url)
        start_pos = s.find('{')
        end_pos = s.rfind(')')
        c = s[start_pos:end_pos]        
        self._html = json.loads(c)['content'].strip()
        return self._html

    # 提取html block中的各个要素（内容简介，目录，作者介绍等）
    def extract_info(self):
        doc_tree = etree.HTML(self._html)
        nodes = doc_tree.xpath('//div[contains(@id,"detail-tag-id-")]')

        d = {}
        for e in nodes:
            col_name = e.xpath('@text')[0]  
            print(col_name)
            g = e.xpath('.//*[@class = "book-detail-content"]') # 每栏下的具体内容提取（list,len=1)

            '''
            if g:
                print('-------------------------')                
                out = g[0].xpath("string(.)")
                print(out)
                out = re.sub(r'[\s]{1,}',' ', out)      # 换连续空格为1个空格
                out = re.sub(r'\n\s*\n','\n', out)            
            d[col_name] = out if g else ''
            '''
            #print(etree.tostring(g[0],encoding='utf-8').decode('utf-8')) 打印该block的HTML代码
            d[col_name] = str(g[0].xpath("string(.)")).strip(' ') if g else ' '  # 每栏下的具体内容提取
        return d
    def save_json(self,filename='temp.json'):
        with open(filename,'w') as f:
            s =bytes(json.dumps(book._data, indent=2),encoding='utf-8').decode('unicode_escape')
            f.write(s) 
    @property
    def html(self):
        return self._html
    
    def __str__(self):
        s = ""
        for k,v in self._data.items():
            s += k.center(50,'-')
            s += '\n'+ str(v)+'\n' if not isinstance(v, str) else '\n'+ v+'\n'
        return s

if __name__ == "__main__":
    bookid =  12512384   
    #bookid =  12466067

    #book  = jd_book(12512384)    
    book  = jd_book(bookid)
    
    book.save_json("book"+str(book._bookid)+".json")
    #print(book)


   
    