#/user/bin/python
# -*- coding: utf-8 -*-
# ----------------------------
#     程序: 糗事百科爬虫
#     版本: 0.1
#     作者: qingbao.ho@gmail.com
#     日期: 2015-07-11
#     语言: Python 2.7.6
# ----------------------------

import urllib2
import re
import thread
import time

#处理页面标签类
class HTMLTool:
    #去除img标签,7位长空格
    removeImg = re.compile('<img.*?>| {7}|')
    #删除超链接标签
    removeAddr = re.compile('<a.*?>|</a>')
    #把换行的标签换为\n
    replaceLine = re.compile('<tr>|<div>|</div>|</p>')
    #将表格制表<td>替换为\t
    replaceTD= re.compile('<td>')
    #把段落开头换为\n加空两格
    replacePara = re.compile('<p.*?>')
    #将换行符或双换行符替换为\n
    replaceBR = re.compile('<br><br>|<br>')
    #将其余标签剔除
    removeExtraTag = re.compile('<.*?>')
    def replace(self, x):
        x = re.sub(self.removeImg,"",x)
        x = re.sub(self.removeAddr,"",x)
        x = re.sub(self.replaceLine,"\n",x)
        x = re.sub(self.replaceTD,"\t",x)
        x = re.sub(self.replacePara,"\n    ",x)
        x = re.sub(self.replaceBR,"\n",x)
        x = re.sub(self.removeExtraTag,"",x)
        #strip()将前后多余内容删除
        return x.strip()

class QSBK:
	def __init__(self):
		self.pageIndex = 1
		self.pages = []
		self.htmlTool = HTMLTool()
		self.enable = False

	def getPage(self, pageIndex):
		myUrl = 'http://www.qiushibaike.com/hot/page/' + str(pageIndex)
		user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.124 Safari/537.36'
		headers = {'User-Agent': user_agent}
		try:
			request = urllib2.Request(myUrl, headers=headers)
			response = urllib2.urlopen(request)
			content = response.read().decode('utf-8')

			pattern = re.compile('<div.*?class="author.*?>.*?<a.*?>(.*?)</a>.*?<div.*?class="content">(.*?)</div>' +
				'.*?<span.*?class="stats-vote">(.*?)</span>.*?<a.*?class="qiushi_comments".*?>(.*?)</a>', re.S)
			mItems = re.findall(pattern, content)
			items = []
			for item in mItems:
				author = self.htmlTool.replace(item[0])
				pattern = re.compile('(.*?)<!--(.*?)-->', re.S)
				cs = re.search(pattern, item[1])
				content = self.htmlTool.replace(cs.group(1))
				createTime = self.htmlTool.replace(cs.group(2))
				stats = self.htmlTool.replace(item[2]) + self.htmlTool.replace(item[3])
				items.append(author + ' ' + createTime + '\n' + content + '\n' + stats)
			return items
		except Exception, e:
			raise e


	def loadPage(self):
		while self.enable:
			if len(self.pages) < 2:
				try:
					myPage = self.getPage(str(self.pageIndex))
					self.pageIndex += 1
					self.pages.append(myPage)
				except Exception, e:
					print u'无法连接到糗事百科' + e
					if hasattr(e, 'reason'):
						print e.reason
			else:
				time.sleep(1)

	def showPage(self, pageItems, pageIndex):
		for item in pageItems:
			print u'第%d页' % pageIndex, item
			myInput = raw_input()
			if myInput == 'q':
				self.enable = False
				break

	def start(self):
		self.enable = True
		pageIndex = self.pageIndex

		print u'正在加载中，请稍候...'

		thread.start_new_thread(self.loadPage, ())

		while self.enable:
			if self.pages:
				nowPage = self.pages[0]
				del self.pages[0]
				self.showPage(nowPage, pageIndex)
				pageIndex += 1

print u'请按下回车浏览今日糗百内容'.encode('utf-8')
raw_input()
qsbk = QSBK()
qsbk.start()
