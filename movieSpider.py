#
# Download, search corpus of wikipedia movie titles and articles. 
# Actually not a very good way to do it, as it turns out. Better off 
# downloading the corpus, and searching that locally. An example of that
# I have used in anger is found in movie.py in the same directory.
# 
# If you're planning to do anything more serious than this with the 
# wonderful wikipedia corpus, a much better approach is to download the whole
# site from http://meta.wikimedia.org/wiki/Data_dumps, eg 
# http://dumps.wikimedia.org/enwiki/20110115/. This can even include full
# revision history. It's only about 700 Gb for all article content.
#
# If you are trying to write a wikibot that edits, you should check out
# http://sourceforge.net/projects/pywikipediabot/
#

import codecs
import os
import os.path
import string
import sys
import urllib
import urllib2
from HTMLParser import HTMLParser


wikiBaseUrl = "http://en.wikipedia.org/wiki/Category:"
wikiMainUrl = "http://en.wikipedia.org"
# eg http://en.wikipedia.org/wiki/Category:2008_films

# We only need to do this because we are ignoring the corpus, see above
headers = {}
headers['User-Agent'] = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.0.4) Gecko/20060508 Firefox/1.5.0.4'

dataDir = "data"

class MovieEntry:
	def __init__(self,title,url):
		self.title = title
		self.url = url


class FilmCorpusDownloader:
	def __init__(self,start,end):
		self.start = start
		self.end = end
		self.films = {}
		for year in range(self.start, self.end+1):
			self.films[year] = []
		self.oldUrls = []

	def download(self):
		for year in range(self.start, self.end+1):
			self.downloadYear(year)
 
	def downloadYear(self,year):
		yearUrl = wikiBaseUrl + str(year) + "_films"
		yearFile = os.path.join(dataDir,"film" + str(year))
		self.downloadPage(yearUrl,yearFile)
		self.extractIndex(year,yearFile)
		self.chainDownload(yearFile,2,year)

	def downloadPage(self,url,yearFile):
		print "downloadPage %s %s " % ( url, yearFile)
		req = urllib2.Request(url,headers=headers)
		remoteFile = codecs.getreader("utf-8")(urllib2.urlopen(req))
		yf = codecs.open(yearFile,'w',"utf-8")
		yf.write(remoteFile.read())
		yf.close()

	def extractIndex(self,year,yearFile):
		flagString = "Pages in category \"" + str(year) + "_films"
		indexHandler = IndexHandler(self,year)
		yf = codecs.open(yearFile,'r',"utf-8")
		indexHandler.feed(yf.read())
		yf.close()

	def chainDownload(self,yearFile,suffix,year):
		if not self.nextPageUrl or (self.nextPageUrl in self.oldUrls):
			return
		nextFile = yearFile + str(suffix)
		self.downloadPage(self.nextPageUrl,nextFile)
		self.oldUrls.append( self.nextPageUrl )
		self.nextPageUrl = 0
		self.extractIndex(year,nextFile)
		self.chainDownload(yearFile,suffix+1,year)

	def scanDownloadedData(self):
		for f in os.listdir(dataDir):
			year = int(f[4:8])
			self.extractIndex(year,os.path.join(dataDir,f))

	def addTitle(self,title,url,year):
		film = MovieEntry(title,url)
		self.films[year].append(film)

	def printAll(self):
		for year in range(self.start,self.end+1):
			print year
			for entry in self.films[year]:
				print entry.title

	def printSummary(self):
		for year in range(self.start,self.end+1):
			print "%d: %d" % (year,len(self.films[year]))

	def setNextPage(self,page):
		self.nextPageUrl = page
	
	def searchTitleString(self,s):
		s1 = string.lower(s)
		result = []
		for year in range(self.start,self.end+1):
			for film in self.films[year]:
				if string.lower(film.title).find(s1) != -1 :
					result.append(film)
		return result


class IndexHandler(HTMLParser):
	def __init__(self,fcd,year):
		HTMLParser.__init__(self)
		self.fcd = fcd
		self.year = year
		self.titleSection = 2

	def handle_starttag(self,name,attrs):
		if not self.titleSection: 
			return
		if name == "a":
			title = ""
			url = ""
			for attr in attrs:
				if attr[0] == 'title':
					title = attr[1]
				if attr[0] == 'href':
					url = attr[1]
			if  (url and title):
				if (title == "Category:" + str(self.year) + " films"):
					self.titleSection -= 1
					self.fcd.setNextPage(wikiMainUrl + url)
				else:
					self.fcd.addTitle(title,url,self.year)


	def handle_startendtag(self,name,attrs):
		if name == "a":
			print attrs




if __name__== "__main__":
	fcd = FilmCorpusDownloader(2005,2010)
	# fcd.download()
	fcd.scanDownloadedData()
	fcd.printSummary()
	for film in fcd.searchTitleString(sys.argv[1]):
		print film.title
	

