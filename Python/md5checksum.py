import os
import os.path
import hashlib
import glob
import codecs
import datetime
import time
import json

def md5sum(filename, blocksize=65536):
	hash = hashlib.md5()
	with open(filename, "rb") as f:
		for block in iter (lambda: f.read(blocksize), b""):
			hash.update(block)
	return hash.hexdigest()

cdnroot = "http:\/\/"
	
strtoday = datetime.date.today()
strdate = "%04d%02d%02d" % (strtoday.year, strtoday.month, strtoday.day)
outfile = codecs.open('registry.json', 'w', 'utf-8')

nowtime = time.localtime()
strtime = "%05d" % ((nowtime.tm_hour * 60 * 60) + (nowtime.tm_min * 60) + nowtime.tm_sec)
strdate = strdate + "." + strtime

outfile.write(u"{\n")
outfile.write('\t"version": "%s",\n' % strdate)
outfile.write('\t"root": "%s",\n' % cdnroot)
outfile.write('\t"files": [\n')

isfirst = True

folder = os.getcwd()
print 'Current folder : %s' % folder
for path, dirs, files in os.walk(folder):
	if files:
		for filename in files:
			if path == folder : continue
			
			fname = os.path.join(path, filename)
			fname = os.path.relpath(fname)
			fname = fname.replace("\\", "\/")
			
			d = md5sum(fname)
			s = os.path.getsize(fname)
			
			if isfirst == False :
				outfile.write(',\n')
			
			outfile.write('\t\t{\n')
			outfile.write('\t\t\t"digest": "%s",\n' % d)
			outfile.write('\t\t\t"file": "%s",\n' % fname)
			outfile.write('\t\t\t"size": %s\n' % s)
			outfile.write('\t\t}')
			
			isfirst = False
			
			print fname,s,md5sum(fname)


outfile.write('\n')
outfile.write('\t]\n')
outfile.write('}')

outfile.close()	

outfile = codecs.open('../config-aws-dev.json', 'r', 'utf-8')
js = json.loads(outfile.read())
outfile.close()

js['ios'][0]['resource']['version'] = strdate
js['android'][0]['resource']['version'] = strdate


outfile = codecs.open('../config-aws-dev.json', 'w', 'utf-8')
json.dump(js, outfile, indent=4, sort_keys=True)
outfile.close()
