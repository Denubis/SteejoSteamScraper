# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import scrapy
from scrapy.pipelines.images import FilesPipeline
from scrapy.exceptions import DropItem
from pprint import pprint
import logging
import os
import re
#from scrapy import CsvItemExporter
# class SteamreleasescraperPipeline(object):


# 	def open_spider(self, spider):
# 		self.file = open('items.csv', 'w')
# 		self.exporter = CsvItemExporter(self.file, unicode)
# 		self.exporter.start_exporting()		

# 	def close_spider(self, spider):
# 		self.exporter.finish_exporting()

# 		self.file.close()

# 	def process_item(self, item, spider):
# 		self.exporter.export_item(item)

# 		#self.file.write(item)
# 		return item


class MyFilesPipeline(FilesPipeline):

	def item_completed(self, results, item, info):
		# iterate over the local file paths of all downloaded images
		for result in [x for ok, x in results if ok]:
			logging.debug("Result?!", result)
			path = result['path']
			logging.debug(("***", path, os.path.basename(path)))
			# # here we create the session-path where the files should be in the end
			# # you'll have to change this path creation depending on your needs
			targetHumanTime=item['released'].strftime('%Y-%m-%d')
			#newFilename = "{}/{}".format(targetHumanTime, re.sub("^[A-Za-z0-9-_:]+",'_', request.meta.get('filename','')))
			extension=re.search(".([a-z0-9]{3,4})\?t=([0-9]+)", path)
			target_path = os.path.join(targetHumanTime, "{}-{}.{}".format(re.sub("[^A-Za-z0-9-_]+",'_', item['title']), extension.group(2), extension.group(1)))
			
			logging.debug("Moving: {}->{}".format(path, target_path))
			#os.path.join(targetHumanTime, os.path.basename(path))

			# # try to move the file and raise exception if not possible
			os.rename(path, target_path)
			#	raise DropItem("Could not move image to target folder")

			# # here we'll write out the result with the new path,
			# # if there is a result field on the item (just like the original code does)
			# if self.FILES_RESULT_FIELD in item.fields:
			#  	result['path'] = target_path
			#  	item['files'].append(result)

		return item


	# def file_path(self, request, response=None, info=None):
		
	# 	newFilename = "{}/{}".format(targetHumanTime, re.sub("^[A-Za-z0-9-_:]+",'_', request.meta.get('filename','')))
	# 	pprint(("newpath", targetHumanTime, newFilename))
	# 	return newFilename

	# def get_media_requests(self, item, info):
	# 	if "file_urls" in item:
	# 		pprint(item)
	# 		for url in item['file_urls']:
				
	# 			meta = {'filename': item['title'], 'targetHumanTime': item['released']}
	# 			yield scrapy.Request(url=url, meta=meta)