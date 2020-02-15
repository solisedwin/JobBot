
import scrapy
import logging
import os


class SimplyHiredSpider(scrapy.Spider):
	
	name = "sh"
	allowed_domains = ['simplyhired.com']
			
	start_urls = []
	job_keywords = ['Junior Developer', 'Web developer', 'PHP developer']
	locations = ['Long Island, NY', 'New York, NY', '']
	
	logger = logging.basicConfig(level=logging.DEBUG,
					format='%(asctime)s %(levelname)s %(message)s',
					filename='scrapy.log',
					filemode='w')


	def generate_urls(self):
		# https://www.simplyhired.com/search?q=junior+developer&l=long+island%2C+ny&fdb=1
		base_url = 'https://www.simplyhired.com/search?q='

		for job in self.job_keywords:
			job = job.replace(' ', '+')
			for location in self.locations:

				""" Identifer for website. l means location, fdb means # of days, q means job title""" 

				location1 = location.replace(' ','+')
				url_location =  "&l=" + location1.replace(",","%2C")
				search_url = base_url + job + url_location  + "&fdb=1"

				#Add it to list of url we will crawl 
				self.start_urls.append(search_url)



	def start_requests(self):
		self.generate_urls()
		for url in self.start_urls:
			job_title = url[url.index('q=') : url.index('+')]
			yield scrapy.Request(url, callback = self.parse_search_page, meta = {'job': job_title})



	def parse_remote_page(self, response):

		job_title = response.meta['job']
		xpath = "//a[@class='card-link' and contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),{job_title})]".format(job_title = job_title)
		job_titles = response.xpath(xpath).extract()
		
		""" Found relevant matches to inputed job title """
		if job_titles and "&l=&" in response.url:
			""" Looks at all relevant jobs (based on keywords) in single page """
			for job in job_titles:
				job_info = 'https://www.simplyhired.com' + job.attrib['href']
				yield response.follow(job_info, callback = self.parse_remote_job_information)

		# We inputed a specific location, so we dont have to check for 'remote' keyword in page information
		elif job_titles and "&l=&" not in response.url:
			for job in job_titles:
				job_info = 'https://www.simplyhired.com' + job.attrib['href']			
				yield response.follow(job_info, callback = self.parse_job_information)
		else:
			pass

		""" Goes to the next page """
		tags = response.css("li.active + li > a");

		# No more pages to crawl for this job title search
		if not tags:
			pass
		else:
			for next_page_tag in tags:
				next_page_url = next_page_tag.attrib['href']
				print('Going to new page')
				yield response.follow(next_page_url ,callback = self.parse_remote_page, errback=self.errback_httpbin, meta = response.meta)



	def parse_job_information(self):
		pass



	def errback_httpbin(self, failure):
		# log all failures
		#self.logger.error(repr(failure))

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




	def parse_remote_job_information(self, response):
		print('##### Found a potential remote job ##############')    

		is_remote = response.xpath("contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),remote)")

		#Save job link and info to folder
		if is_remote:






