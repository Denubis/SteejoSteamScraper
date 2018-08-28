# -*- coding: utf-8 -*-
import scrapy
import calendar
import time
import logging
import dateparser
import datetime
from datetime import timedelta
import os
import shutil
from tzlocal import get_localzone


from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, parse_qsl
from SteamReleaseScraper.items import SteamreleasescraperItem
DAYLEN=24*60*60
VIDEOFORMAT="mp4-hd" # of "webm-hd", "webm", "mp4-hd", "mp4"

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
	tz = get_localzone() # local timezone 

	




	# https://stackoverflow.com/a/15618520/263449
	def __init__(self, targetdate=False):
		# scrapy crawl myspider -a targetdate="Today"
		if targetdate:
			self.targetdate= dateparser.parse(targetdate)

		self.targetdate = datetime.datetime(self.targetdate.year, self.targetdate.month,self.targetdate.day)
		self.targetdatetz = datetime.datetime(self.targetdate.year, self.targetdate.month,self.targetdate.day, tzinfo=self.tz)
		#self.startdate = self.enddate-DAYLEN
		self.start_urls = ['https://store.steampowered.com/search/results?sort_by=Released_DESC']
		#startHumanTime = time.strftime('%Y-%m-%d', time.localtime(self.startdate))
		self.targetHumanTime =self.targetdate.strftime('%Y-%m-%d')

		d = self.targetdatetz # or some other local date 

		self.utc_offset = d.utcoffset().total_seconds()
		self.cookies = {'mature_content': '1', 'timezoneOffset':self.utc_offset}
		

		os.makedirs(self.targetHumanTime, exist_ok=True)
		logging.info("Getting approximate range for day {}.".format(self.targetHumanTime))
		#self.start_urls = ['http://www.example.com/category/%s' % category]
		#super().__init__(**kwargs)  # python3
		#self.log(self.domain)  # system


	def start_requests(self):				

		print(self.cookies)
		for url in self.start_urls:
			yield scrapy.Request(url, cookies=self.cookies, callback=self.parse)

	def parse(self, response):

		print('cookie jar', response.meta)
		for r in response.xpath("//*[@id='search_result_container']/div[2]/a"):
			

			item = SteamreleasescraperItem()

			item["url"] = r.xpath("@href").extract_first()
			item["title"] = r.xpath("div//span[@class='title']/text()").extract_first()
			item["image"] = r.xpath("div//img/@src").extract_first()
			item["platform"] = r.xpath("div//p/span/@class").extract()
			item["price"] = r.xpath("normalize-space(div/div/div[@class='col search_price  responsive_secondrow']/text())").extract_first()
			released = r.xpath("div[@class='responsive_search_name_combined']/div[@class='col search_released responsive_secondrow']/text()").extract_first()
			if released == self.priorReleased.strftime('%b %Y'):
				print("ew")
				released= self.priorReleased
			else: 
				released= dateparser.parse(released)
				self.priorReleased = released


			if released == self.targetdate:
				print(released)
				#print(r.extract())
				item["released"] = released
				

				request = scrapy.Request(item["url"], cookies=self.cookies, callback=self.getTrailer)
				request.meta['item'] = item
				yield request
			else:
				if released and released < self.targetdate:
					self.done = True
					
				print("no", released, self.targetdate, self.done)


		if not self.done:

			args = urlparse(response.request.url)
			query = parse_qs(args.query)
			if "page" in query:
				logging.debug("On page {}, continuing.".format(query['page'][0]))
				page = int(query['page'][0]) +1
			else:
				page = 2
			
			targeturl = set_query_field(response.request.url, "page", page, replace=True)
			print(query, targeturl)
			yield scrapy.Request(targeturl, cookies=self.cookies, callback=self.parse)
	
	def getTrailer(self, response):
		item = response.meta['item']

		print(response.request.url)
		if "agecheck" in response.request.url:
			with open("{}/agecheck.txt".format(self.targetHumanTime), "a") as file:
				file.write(response.request.url)

		#trailer = response.xpath("//div[@data-webm-hd-source]/@data-webm-hd-source").extract()
		trailer = response.xpath("//div[@data-{0}-source]/@data-{0}-source".format(VIDEOFORMAT)).extract()
		if trailer:
			print(trailer)
			item['file_urls'] = trailer
		yield item

		
		# with open("aaa.html", "ab") as aaaa:
		# 	aaaa.write(response.body)

# <a href="https://store.steampowered.com/app/925621/Leder_Panzer__Im_your_biggest_fan_edition/?snr=1_7_7_230_150_1" 
#data-ds-appid="925621" onmouseover="GameHover( this, event, 'global_hover', {&quot;type&quot;:&quot;app&quot;,&quot;id&quot;:925621,&quot;public&quot;:1,&quot;v6&quot;:1} );" 
#onmouseout="HideGameHover( this, event, 'global_hover' )" class="search_result_row ds_collapse_flag ">
# 					<div class="col search_capsule"><img src="https://steamcdn-a.akamaihd.net/steam/apps/925621/capsule_sm_120.jpg?t=1534896114"></div>
# 					<div class="responsive_search_name_combined">
# 						<div class="col search_name ellipsis">
# 							<span class="title">Leder Panzer - I'm your biggest fan -edition</span>
# 							<p>
# 								<span class="platform_img win"></span><span class="platform_img linux"></span>							</p>
# 						</div>
# 						<div class="col search_released responsive_secondrow">21 Aug, 2018</div>
# 						<div class="col search_reviewscore responsive_secondrow">
# 													</div>


# 						<div class="col search_price_discount_combined responsive_secondrow">
# 							<div class="col search_discount responsive_secondrow">
								
# 							</div>
# 							<div class="col search_price  responsive_secondrow">
# 								$49.99							</div>
# 						</div>
# 					</div>


# 					<div style="clear: left;"></div>
# 				</a>
