#
# Build and search film database, sourced from en:wikipedia.
#
# The wonderful wikipedia corpus was obtained from 
# http://meta.wikimedia.org/wiki/Data_dumps, eg
# http://dumps.wikimedia.org/enwiki/20110115/.
#

from xml.sax import make_parser, handler
from xml.sax.handler import ContentHandler
from xml.sax import saxutils
from optparse import OptionParser
import os
import os.path
import re
import codecs
import time
import sys


dataDir = "data"

class MovieEntry:
	def __init__(self,title,year):
		self.title = title
		self.year = year

	def __str__(self):
		return self.title + " -- " + str(self.year)

class WikiDB:
	def __init__(self,sourceDir):
		self.sourceDir = sourceDir

	def loadAndSaveSubset(self,expr,outFile):
		print "load()"
		try:
			os.remove(outFile)
		except :
			None
		f = open(outFile,'w')
		f.write('<mediawiki>\n')
		f.close()
		parser = make_parser()
		for file in os.listdir(self.sourceDir):
			print "loading " + file
			parser.setContentHandler(WikiExprSubsetHandler(expr,outFile))
			parser.parse(os.path.join(self.sourceDir,file))
		f = open(outFile,'a+')
		f.write('</mediawiki>')
		f.close()

	def scanExpr(self,expr):
		print "scanExpr"
		parser = make_parser()
		for file in os.listdir(self.sourceDir):
			print "loading " + file
			parser.setContentHandler(WikiFilmHandler(expr))
			parser.parse(os.path.join(self.sourceDir,file))



class WikiExprSubsetHandler(ContentHandler):
	def __init__(self,expr,outFile):
		self.totalCt = 0
		self.ct = 0
		self.expr = expr
		self.inRevision = 0
		self.outFile = outFile
		self.outFileObj = codecs.open(outFile,encoding='utf-8',mode='a+')
		self.ctContent = ""
		self.exprFound = 0
		self.inTitle = 0
		self.ctTitle = ""
		self.matchingLine = ""


	def startElement(self,name,attrs):
		if name == "revision":
			self.totalCt += 1
			self.inRevision = 1
			if self.totalCt % 1000 == 0:
				print "Scanned: %d %s" % (self.totalCt,time.ctime())
		if name == "title":
			self.inTitle = 1


	def endElement(self,name):
		if name == "revision":
			if self.exprFound:
				self.outFileObj.write('<page>\n')
				self.outFileObj.write(' <title>')
				self.outFileObj.write(self.ctTitle)
				self.outFileObj.write(' </title>\n')
				self.outFileObj.write(' <matchingline>')
				self.outFileObj.write(self.matchingLine)
				self.outFileObj.write(' </matchingline>\n')
				self.outFileObj.write(' <revision>\n')
				self.outFileObj.write(saxutils.escape(self.ctContent))
				self.outFileObj.write('\n')
				self.outFileObj.write(' </revision>\n' )
				self.outFileObj.write('</page>\n')
				self.exprFound = 0
				self.ct += 1
			self.inRevision = 0
			self.ctContent = ""
			self.ctTitle = ""
			self.matchingLine = ""
		if name == "title":
			self.inTitle = 0

	def characters(self,content):
		if (self.inRevision):
			self.ctContent += content
			if not self.exprFound and re.search(self.expr,content) :
				self.exprFound = 1
				self.ct += 1
				self.matchingLine = content
				if self.ct % 10 == 0:
					print "Hits: %d" % self.ct
		if (self.inTitle):
			self.ctTitle = content


	def endDocument(self):
		print "end %d " % self.ct
		print "Hits: %d Scanned: %d" % (self.ct,self.totalCt)
		self.outFileObj.close()


class WikiFilmHandler(ContentHandler):
	def __init__(self,exprList):
		self.films = []
		self.totalCt = 0
		self.ct = 0
		self.exprList = []
		for expr in exprList:
			self.exprList.append(re.compile(expr,re.IGNORECASE))
		self.foundExpr = {}
		self.inRevision = 0
		self.ctFilm = None
		self.exprFound = 0
		self.inMatchingLine = 0
		self.inTitle = 0



	def startElement(self,name,attrs):
		if name == "revision":
			self.totalCt += 1
			self.inRevision = 1
			if self.totalCt % 1000 == 0:
				print "Scanned: %d %s" % (self.totalCt,time.ctime())
		if name == "matchingline":
			self.inMatchingLine = 1
		if name == "title":
			self.inTitle = 1

	def endElement(self,name):
		if name == "revision":
			if self.exprFound:
				self.exprFound = 0
				self.films.append(self.ctFilm)
			self.foundExpr = {}
			self.inRevision = 0
		if name == "matchingline":
			self.inMatchingLine = 0
		if name == "title":
			self.inTitle = 0

	def characters(self,content):
		if (self.inRevision and not self.exprFound):
			for expr in self.exprList:
				if not self.exprFound and expr.search(content) :
					self.foundExpr[expr] = 1
			if len(self.foundExpr) == len(self.exprList):
				self.ct += 1
				self.exprFound = 1
				if self.ct % 10 == 0:
					print "Hits: %d" % self.ct
		if (self.inTitle):
			self.ctTitle = content
		if (self.inMatchingLine):
			self.ctFilm = MovieEntry(self.ctTitle,0)
				


	def endDocument(self):
		for film in self.films:
			print film
		print "end %d " % self.ct
		print "Hits: %d Scanned: %d" % (self.ct,self.totalCt)


# <mediawiki>
#	<page><revision>...[Category:???? films]</revision>
#	<page>
# </mediawiki>
#

class WikiRunner:
	def __init__(self,wikiDir):
		self.wikiDir = wikiDir
		parser = OptionParser()
		parser.add_option("-r","--reload",help="Reload  from full wiki source",action="store_true",dest="reload")
		parser.add_option("-e","--expr",help="Reload  from full wiki source",action="append",dest="expr")
		(self.options,self.args) = parser.parse_args()

	def main(self):
		if self.options.reload:
			wdb = WikiDB(self.wikiDir)
			wdb.loadAndSaveSubset(r"Category\:[0-9]... films",os.path.join(dataDir,"filmsubset.xml"))
		if self.options.expr:
			wdb = WikiDB(dataDir)
			wdb.scanExpr(self.options.expr)


if __name__ == "__main__":
	WikiRunner("../wikipedia/wikipedia").main()


