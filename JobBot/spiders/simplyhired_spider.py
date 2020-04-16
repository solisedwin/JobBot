
import scrapy
import logging
import os
import sys
from scrapy.exceptions import CloseSpider


"""
TODO:
- Looking at the same job. There might be an ID
for each job, save job IDS to a set

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
	job_keywords = ['junior developer', 'web developer', 'php developer', 'python developer']
	locations = ['Long Island, NY', 'New York, NY', '']

	ignore_jobs = {'CyberCoders', 'Revature','Jobot'}


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


	def generate_urls(self):

		# Ex: https://www.simplyhired.com/search?q=junior+developer&l=long+island%2C+ny&fdb=1
		base_url = 'https://www.simplyhired.com/search?q='

		for job in self.job_keywords:
			job = job.replace(' ', '+')
			for location in self.locations:

				""" Identifer for website. l means location, fdb means # of days, q means job title"""
				location1 = location.replace(' ','+')
				url_location =  "&l=" + location1.replace(",","%2C")
				search_url = base_url + job + url_location  + "&fdb=7"

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
						job_info_url = 'https://www.simplyhired.com' + href
						#job_info = 'https://www.simplyhired.com' + job.attrib['href']
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
				self.save_job(job_dir, file_name, url)
			elif "&l" in response.url:
				self.save_job(job_dir, file_name, url)
			else:
				pass


	def folder_file_information(self, response, company_name):
		job_title = response.meta['job_keyword'].replace(' ', '_')
		job_dir =  os.getcwd() +  "/jobs/" + job_title + '/'

		#company_name = response.xpath('//span[@class="company"]/text()').get()
		file_name = str(company_name).replace(' ','_')
		url = response.url
		return job_dir,file_name,url


	def save_job(self, job_dir, file_name, url):
		if not os.path.exists(job_dir):
			os.makedirs(job_dir)
		else:
			try:
				""" Make text and screen shot file  """
				f = open(job_dir + file_name + '.txt','w')
				f.write('Job URL: ' + str(url))
				f.close()
				print(bcolors.OKGREEN + "Found a perfect job!! Saved to " + job_dir + " folder !" + bcolors.ENDC)
				
			except Exception as e:
				self.logger.error('~~ Creating file error: %s', str(e))
				print(bcolors.FAIL + "~~ Error! Remote job couldnt be saved to folder " + bcolors.ENDC)

