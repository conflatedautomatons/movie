
import movie
import unittest


class TestFilmCorpusDownloader(unittest.TestCase):
	def setUp(self):
		self.fcd = movie.FilmCorpusDownloader(2007,2008)
		self.dataFile = "data/film2007"

	def testExtractIndex(self):
		self.fcd.extractIndex(2007,self.dataFile)
		self.fcd.printSummary()
		self.fail("Incomplete")


if __name__ == '__main__':
    unittest.main()

