# -*- coding: utf-8 -*-
import scrapy
import calendar
import time
import logging
import dateparser
import datetime
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, parse_qsl

DAYLEN=24*60*60
# https://alexwlchan.net/2016/08/dealing-with-query-strings/
def set_query_field(url, field, value, replace=False):
    # Parse out the different parts of the URL.
    components = urlparse(url)
    query_pairs = parse_qsl(urlparse(url).query)

    if replace:
        query_pairs = [(f, v) for (f, v) in query_pairs if f != field]
    query_pairs.append((field, value))

    new_query_str = urlencode(query_pairs)

    # Finally, construct the new URL
    new_components = (
        components.scheme,
        components.netloc,
        components.path,
        components.params,
        new_query_str,
        components.fragment
    )
    return urlunparse(new_components)

class SteamnewreleasesSpider(scrapy.Spider):
	name = 'steamNewReleases'
	allowed_domains = ['store.steampowered.com']
	targetdate = datetime.date.today()  
	priorReleased = targetdate
	print(priorReleased)
	done = False




	# https://stackoverflow.com/a/15618520/263449
	def __init__(self, targetdate=False):
		# scrapy crawl myspider -a targetdate="Today"
		if targetdate:
			self.targetdate= dateparser.parse(targetdate)
		self.targetdate = datetime.datetime(self.targetdate.year, self.targetdate.month,self.targetdate.day)
		#self.startdate = self.enddate-DAYLEN
		self.start_urls = ['https://store.steampowered.com/search/results?sort_by=Released_DESC']
		#startHumanTime = time.strftime('%Y-%m-%d', time.localtime(self.startdate))
		targetHumanTime =self.targetdate.strftime('%Y-%m-%d')

		logging.info("Getting approximate range for day {}.".format(targetHumanTime))
		#self.start_urls = ['http://www.example.com/category/%s' % category]
		#super().__init__(**kwargs)  # python3
		#self.log(self.domain)  # system


	def parse(self, response):
		
		for r in response.xpath("//*[@id='search_result_container']/div[2]/a"):

			released = r.xpath("div[@class='responsive_search_name_combined']/div[@class='col search_released responsive_secondrow']/text()").extract_first()
			if released == self.priorReleased.strftime('%b %Y'):
				print("ew")
				released= self.priorReleased
			else: 
				released= dateparser.parse(released)
				self.priorReleased = released
			if released == self.targetdate:
				print(released)
			else:
				if released < self.targetdate:
					self.done = True
					
				print("no", released, self.targetdate, self.done)
		if not self.done:

			args = urlparse(response.request.url)
			query = parse_qs(args.query)
			if "page" in query:
				page = query['page'] +1
			else:
				page = 2
			
			targeturl = set_query_field(response.request.url, "page", page, replace=True)
			print(query, targeturl)
			yield scrapy.Request(targeturl, callback=self.parse)
		#<a id="more_posts_url" href="https://store.steampowered.com/news/posts/?feed=steam_release&amp;enddate=1533657239" onclick="LoadMoreNews(); return false;">...</a>
		# more_posts_url=response.xpath("//a[@id='more_posts_url']/@href")
		# if more_posts_url:
		# 	more_posts_url = more_posts_url.extract_first()
		# 	args = urlparse(more_posts_url)
		# 	query = parse_qsl(args.query)
		# 	queryenddate=int(query[1][1])
		# 	logging.info("This page terminates at {} ({})".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(queryenddate)), queryenddate))
		# 	# if queryenddate > self.startdate:
			# 	logging.debug(queryenddate, self.startdate)
			# 	yield scrapy.Request(more_posts_url, callback=self.parse)
			# else:
			# 	logging.debug("terminating recursion: {} {}".format(queryenddate, self.startdate))
