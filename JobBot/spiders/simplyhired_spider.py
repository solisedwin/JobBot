
import scrapy
import logging
import os
import sys
import json
from .bot import WebBot

"""
TODO:
- Add CRON TAB to run code everyday
- Add synonyms to words ?? (Entry level = Junior , UI/UX = Web)
"""

class bcolors:

	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'


class SimplyHiredSpider(scrapy.Spider):

	name = "sh"
	allowed_domains = ['simplyhired.com']

	start_urls = []

	visited_job_ids = set()

	logger = logging.basicConfig(level=logging.DEBUG,
					format='%(asctime)s %(levelname)s %(message)s',
					filename='scrapy.log',
					filemode='w')

	def errback_httpbin(self, failure):

		# in case you want to do something special for some errors,
		# you may need the failure's type:
		if failure.check(HttpError):
			# these exceptions come from HttpError spider middleware
			# you can get the non-200 response
			response = failure.value.response
			self.logger.error('HttpError on %s', response.url)

		elif failure.check(DNSLookupError):
			# this is the original request
			request = failure.request
			self.logger.error('DNSLookupError on %s', request.url)

		elif failure.check(TimeoutError, TCPTimedOutError):
			request = failure.request
			self.logger.error('TimeoutError on %s', request.url)
		else:
			self.logger.error('Unknown Error on %s', request.url)


	def read_json_keywords(self):
		with open('./JobBot/spiders/crawl_job_settings.json') as f:
			data = json.load(f)
			self.job_keywords = [keyword  for keyword in data['job_keywords']  ]
			self.job_locations = [location  for location in data['locations']  ]
			self.ignore_jobs = { ignore_job  for ignore_job in data['ignore_jobs']  }

		self.init_job_url_dict()



	def init_job_url_dict(self):
		
		#Intalize number of WebBots needed, corresponding to number of job keywords
		#job_keyword_length = len(self.job_keywords)
		self.job_urls_dict = dict()

		for job in self.job_keywords:
			if job not in self.job_urls_dict:
				self.job_urls_dict[job] = set()
		


	def generate_urls(self):

		self.read_json_keywords()

		# Ex: https://www.simplyhired.com/search?q=junior+developer&l=long+island%2C+ny&fdb=1
		base_url = 'https://www.simplyhired.com/search?q='

		for job in self.job_keywords:
			job += ' developer'
			job = job.replace(' ', '+')
			for location in self.job_locations:

				""" Identifer for website. l means location, fdb means # of days, q means job title"""
				location1 = location.replace(' ','+')
				url_location =  "&l=" + location1.replace(",","%2C")
				search_url = base_url + job + url_location  + "&fdb=1"

				#Add it to list of url we will crawl
				self.start_urls.append(search_url)


	def start_requests(self):
		self.generate_urls()

		for url in self.start_urls:
			job_title = url[url.index('q=') + 2 : url.index('+')]
			yield scrapy.Request(url, callback = self.parse_search_page, meta = {'job_title': job_title})


	def parse_search_page(self, response):

		try:
			jobs_posted = response.xpath("//span[contains(concat(' ',normalize-space(@class),' '),'CategoryPath-total')]").get()

			#Zero search results. Stop process and move on to the next job title/location
			if jobs_posted is not None:
				job_title = response.meta['job_title']

				""" Looks at all relevant jobs (based on keywords) in single page """
				job_titles_xpath = "//a[@class='card-link' and contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), '{job_keyword}')]/@href".format(job_keyword = job_title)
				job_titles = response.xpath(job_titles_xpath).getall()

				#Check if we found any matches in single page, with keyword search
				if job_titles:
					for href in job_titles:
						if href in self.visited_job_ids:
							continue
						else:
							self.visited_job_ids.add(href)
							job_info_url = 'https://www.simplyhired.com' + href
							yield response.follow(job_info_url, callback = self.parse_job_information, meta = {'job_keyword':job_title})


				""" Goes to the next page """
				tags = response.css("li.active + li > a");

				# No more pages to crawl for this job title search
				if not tags:
					pass
					#print(bcolors.HEADER + " All links are crawled for job " + str(response.url) +  bcolors.ENDC)
				else:
					for next_page_tag in tags:
						next_page_url = next_page_tag.attrib['href']
						yield response.follow(next_page_url ,callback = self.parse_search_page, errback=self.errback_httpbin, meta = response.meta)

		except Exception as e:
			print('~~ Exception: ' + str(e))



	def parse_job_information(self, response):
		company_name = str(response.xpath("//span[@class='company']/text()").extract_first())

		if company_name.strip() not in self.ignore_jobs:
			is_remote_work = int(response.xpath("contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'remote')").get())
			job_dir , file_name , url = self.folder_file_information(response, company_name)

			#Location not specified and remote work is availbale for job
			if "&l=" not in response.url and is_remote_work != 0:
				self.save_job(job_dir, file_name, url, response)
			elif "&l" in response.url:
				self.save_job(job_dir, file_name, url, response)
			else:
				pass


	def folder_file_information(self, response, company_name):
		job_title = response.meta['job_keyword'].replace(' ', '_')
		job_dir =  os.getcwd() +  "/jobs/" + job_title + '/'

		#company_name = response.xpath('//span[@class="company"]/text()').get()
		file_name = str(company_name).replace(' ','_')
		url = response.url
		return job_dir,file_name,url


	def save_job(self, job_dir, file_name, url, response):
		if not os.path.exists(job_dir):
			os.makedirs(job_dir)
		else:
			try:
				""" Make text and screen shot file  """
				f = open(job_dir + file_name + '.txt','w')
				f.write('Job URL: ' + str(url))
				f.close()
				print(bcolors.OKGREEN + "Found a perfect job!! Saved to " + job_dir + " folder !" + bcolors.ENDC)
				
				job_keyword = response.meta['job_keyword']

				if job_keyword in self.job_urls_dict:
					self.job_urls_dict[job_keyword].add(url)

			except Exception as e:
				self.logger.error('~~ Creating file error: %s', str(e))
				print(bcolors.FAIL + "~~ Error! Remote job couldnt be saved to folder " + bcolors.ENDC)


	def browser_view_jobs(self):

		print()
		print(self.job_urls_dict)

		for job_title in self.job_urls_dict:
			url_list = []
			for url in self.job_urls_dict[job_title]:
				url_list.append(url)
			
			web_bot = WebBot(url_list)
			web_bot.open_urls()


	def closed( self, reason ):
		self.browser_view_jobs()
