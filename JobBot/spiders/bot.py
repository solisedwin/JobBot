
from selenium.webdriver.firefox.options import Options
from selenium import webdriver

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException

from selenium.webdriver.firefox.options import Options

from selenium.webdriver.common.keys import Keys

class WebBot(object):
	"""docstring for WebBot"""
	def __init__(self, url_list = []):
		
		self.url_list = []
		options = Options()
		options.headless = False

		profile = webdriver.FirefoxProfile()
		profile.set_preference("general.useragent.override", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:63.0) Gecko/20100101 Firefox/63.0")

		driver = webdriver.Firefox(options = options , firefox_profile = profile)	
		driver.set_window_size(630, 590)
		self.driver = driver
		self.driver.get("https://www.simplyhired.com/")


	def open_urls(self):

		print('----- Opening urls  -----------')

		url_list_length = len(self.url_list)
		if url_list_length > 30:
			tab_limit = 30
		else:
			tab_limit = url_list_length

		for index in range(tab_limit):
			job_url = url_list_length[index]
			self.driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 't') 
			self.driver.get(job_url)	

