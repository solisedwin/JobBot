
import scrapy

class SimplyHiredSpider(scrapy.Spider):
    
    name = "sh"
    allowed_domains = ['simplyhired.com']
            
    start_urls = []
    job_keywords = ['Junior Developer', 'Web developer', 'PHP developer']
    locations = ['Long Island, NY', 'New York, NY', '']
    


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
            yield scrapy.Request(url, callback = self.parse_url_identifer, meta = {'job': job_title})



    def parse_url_identifer(self, response):
        
        job = response.meta['job']

        """ All jobs in the united states, looking for remote work. Should I apply and request to work remotely? """
        if "&l=&" in response.url:

            xpath = "//a[@class='card-link' and contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),{job_title}) or contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'entry')]".format(job_title = job)
            if response.xpath(xpath).attrib['href'] != None:
                job_title_hrefs = response.xpath(xpath).attrib['href']    

                for href in job_title_hrefs:
                    job_info = 'https://www.simplyhired.com' + href
                    yield response.follow(job_info, callback = self.parse_job_information)



    def parse_job_information(self, response):
        print('#####')
        print(response.text)    













