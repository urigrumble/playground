import string
import urllib2
import threading
import time
import datetime
import json
import re
import xml.dom.minidom

class Interval(threading.Thread):
	"""Runs a function every X seconds."""
	def __init__(self, secs, func, event):
		"""secs is the time to wait between calls to func. event is used to signal the Interval to stop calling."""
		threading.Thread.__init__(self)
		self.secs = secs
		self.func = func
		self.stopped = event
	def run(self):
		print "Interval runnning"  
		while not self.stopped.wait(self.secs):
			self.func()
		print "Interval stopped"

class UrlWatcher:
	"""Watches a URL for changes in its contents. Fires a function when a change is observerd."""
	def __init__(self, url, secs, on_change, fire_on_first_poll = False):
		"""url is the URL to watch every secs. 
		on_change is a function to be called if a change is observed. 
		fire_on_first_poll indicates whether to call on_change when we first poll the URL.
		"""
		self.url = url
		self.on_change = on_change
		self.fire_on_first_poll = fire_on_first_poll
		self.content = ""
		self.stopFlag = threading.Event()
		self.interval = Interval(secs, self.poll, self.stopFlag)
	def start(self):
		print "UrlWatcher started"
		self.interval.start()
	def stop(self):
		self.stopFlag.set()
		print "UrlWatcher stopped"
	def poll(self):
		stream = urllib2.urlopen(self.url)
		new_content = stream.read()
		first_poll = self.content==""
		if first_poll:
			if self.fire_on_first_poll:
				self.on_change(self, self.content, new_content)
			else:
				print "x"
		elif (len(self.content) != len(new_content)):
			self.on_change(self, self.content, new_content)
		else:
			print "."
		self.content = new_content

def jsonp2json(str):
	"""Remove getXXX( prefix and ) suffix from str representing jsonp to get pure json."""
	return re.sub(r"get.*\(", "", str)[:-1]

def pretty_xml(str):
	myxml = xml.dom.minidom.parseString(str)
	return myxml.toprettyxml()

def pretty_json(str):
	return json.dumps(str, indent=4, separators=(',', ':'))

def dump_to_file(filepath, content):	
	""" Helper method to dump content into file. """
	file = open(filepath, 'w')
	file.write(content)
	file.close()

def target_change(watcher, old_content, new_content):
	global top_news_items
	global top_news_items_ids
	change = json.loads(jsonp2json(new_content))
	top_news_items_added = filter((lambda item: item[11]=='2848'), change['entriesAdd'])
	top_news_items_deleted = filter(lambda item: item[1] in top_news_items_ids, change['entriesDelete'])
	top_news_items_changed = filter(lambda item: item[1] in top_news_items_ids, change['entriesChange'])
	if top_news_items_added or top_news_items_deleted or top_news_items_changed:
		watcher.stop()
		print "Target changed on {0}. Prev size:{1}, Curr size:{2}".format(datetime.datetime.now(),len(old_content),len(new_content))
		dump_to_file("C:\\Users\\Uri\\Desktop\\getSItemsI.txt", pretty_json(item))

def source_change(watcher, old_content, new_content):
	global top_news_items
	global top_news_items_ids
	watcher.stop()
	print "Source changed on {0}. Prev size:{1}, Curr size:{2}".format(datetime.datetime.now(),len(old_content),len(new_content))
	dump_to_file("C:\\Users\\Uri\\Desktop\\original.xml", pretty_xml(new_content))
	''' Get all items from Rumble CDN '''
	all_items_str = jsonp2json(urllib2.urlopen("http://rumblenews.blob.core.windows.net/data2/370/getSItems.json").read())
	all_items = json.loads(all_items_str)
	''' We're only interested in the ids of items from the "Top News Channel", id: 2848 '''
	top_news_items = filter(lambda item: item[11]=='2848', all_items["entries"])
	top_news_items_ids = map(lambda item: item[1], top_news_items)
	dump_to_file("C:\\Users\\Uri\\Desktop\\getSItems.txt", "".join(pretty_json(item) for item in top_news_items))
	#str(item) for item in top_news_items))
	''' Start watching the incremental URL in the Rumble CDN for any changes to the top news items '''
	target_watcher = UrlWatcher("http://rumblenews.blob.core.windows.net/data2/370/getSItemsI.json", 5.0, target_change, True)
	target_watcher.start()

if __name__ == '__main__':
	top_news_items = ""
	top_news_items_ids = ""
	source_watcher = UrlWatcher("http://feeds.ydr.com/mngi/rss/CustomRssServlet/515/267602.xml", 5.0, source_change)
	source_watcher.start()
