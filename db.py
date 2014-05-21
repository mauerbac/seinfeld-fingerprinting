'''
Matt Auerbach
CS591
Final Project
Spring 2014

Sources: Matplotlib, Pylab, Numpy, Dejavu (https://github.com/worldveil/dejavu)

Run with Python 2.7

Db.py

'''

from itertools import izip_longest
import Queue

import MySQLdb
from MySQLdb.cursors import DictCursor


def connect():
	db = MySQLdb.connect(host="xxxxxx", # your host, usually localhost
	                     user="xxxxx", # your username
	                      passwd="xxxx", # your password
	                      db="xxxxx")

	return db

def lookup():
	global cur, db
	cur.execute("SELECT * FROM episodes")
	for row in cur.fetchall() :
		print row[0]

	close()

def insert(e_id,hashes):
	db= connect()
	cur = db.cursor()

	values = []
	sql= """
      INSERT IGNORE INTO %s (%s, %s, %s) values
            (UNHEX(%%s), %%s, %%s);
    """ % ("fingerprints", "hash", "episode_id", "offset")
	for hash, offset in hashes:
		values.append((hash, e_id, offset))
        
	#with db.cursor() as cur:
	for split_values in grouper(values, 1000):
		cur.executemany(sql, split_values)


	db.commit()
	print "inserted"
	close(db,cur)



def lookup(hashes):
	db= connect()
	cur = db.cursor()
	sql = """
        SELECT HEX(%s), %s, %s FROM %s WHERE %s IN (%%s);
    """ % ("hash", "episode_id", "offset",
           "fingerprints", "hash")
	mapper = {}

	for hash, offset in hashes:
		mapper[hash.upper()] = offset

    # Get an iteratable of all the hashes we need
	values = mapper.keys()
	count=0
	print "------here are the matches------"
	for split_values in grouper(values, 1000):
		# Create our IN part of the query
		query = sql
		query = query % ', '.join(['UNHEX(%s)'] * len(split_values))

		cur.execute(query, split_values)
		for hash, sid, offset in cur:
			print (sid,offset - mapper[hash])
			# (sid, db_offset - song_sampled_offset)
			yield (sid, offset - mapper[hash])
			count+=1
	print "number of matches"
	print count

	db.commit()
	print "db recognized"
	close(db,cur)

def songTOID(sid):
	db= connect()
	cur = db.cursor()

	sql="""
        SELECT %s FROM %s WHERE %s = %s
    """ % ("episode_name", "episodes","episode_id", sid)
	cur.execute(sql)

	song=cur.fetchone()


	db.commit()
	close(db,cur)

	return song


def close(db,cur):
	cur.close()
	db.close()

def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return (filter(None, values) for values
            in izip_longest(fillvalue=fillvalue, *args))




if __name__ == "__main__":	
	pass
