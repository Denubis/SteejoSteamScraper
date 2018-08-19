# -*- coding: utf-8 -*-
import scrapy
import calendar
import time
import logging
from urllib.parse import urlparse, parse_qsl

DAYLEN=24*60*60

class SteamnewreleasesSpider(scrapy.Spider):
	name = 'steamNewReleases'
	allowed_domains = ['store.steampowered.com']
	enddate = calendar.timegm(time.gmtime())    

	


	# https://stackoverflow.com/a/15618520/263449
	def __init__(self, enddate=False):
		# scrapy crawl myspider -a enddate="Today"
		if enddate:
			self.enddate= dateparser.parse(enddate)
		self.startdate = self.enddate-DAYLEN
		self.start_urls = ['https://store.steampowered.com/news/posts/?feed=steam_release&enddate={}'.format(self.enddate)]
		startHumanTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.startdate))
		stopHumanTime =time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.enddate))

		logging.info("Getting approximate range from {} to {}.".format(startHumanTime, stopHumanTime))
		#self.start_urls = ['http://www.example.com/category/%s' % category]
		#super().__init__(**kwargs)  # python3
		#self.log(self.domain)  # system


	def parse(self, response):
		for r in response.xpath("//div[@class='newsPostBlock steam_release']"):
			print(r)
		#<a id="more_posts_url" href="https://store.steampowered.com/news/posts/?feed=steam_release&amp;enddate=1533657239" onclick="LoadMoreNews(); return false;">...</a>
		more_posts_url=response.xpath("//a[@id='more_posts_url']/@href")
		if more_posts_url:
			more_posts_url = more_posts_url.extract_first()
			args = urlparse(more_posts_url)
			query = parse_qsl(args.query)
			queryenddate=int(query[1][1])
			logging.info("This page terminates at {} ({})".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(queryenddate)), queryenddate))
			if queryenddate > self.startdate:
				logging.debug(queryenddate, self.startdate)
				yield scrapy.Request(more_posts_url, callback=self.parse)
			else:
				logging.debug("terminating recursion: {} {}".format(queryenddate, self.startdate))
