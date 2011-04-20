Extracts subsets of the wiki corpus using an expression, eg Category:???? films.
This takes about 7 hours at time of writing.

Usage: python movie.py -r


Searches extracted film subsets for word collision, eg 

python movie.py -e stripper -e zombie

ie, provides a brute force way of searching every film in wikipedia.

