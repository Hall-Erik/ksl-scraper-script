import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time

class Scraper:
    '''
    Class for scraping data and updating DB

    jobs dictionary should look like:
    {
    '/listing/1234': {
    'name': 'job',
    'url': '/listing/1234',
    'employer': 'IRS',
    'date_posted': '2018-11-27',
    },
    ...
    }
    '''

    def __init__(self):
        self.prefix = 'https://jobs.ksl.com'
        self.eng_url = "/search/keywords/software-engineer"
        self.dev_url = "/search/keywords/software-developer"
        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        # self.backend_url = 'http://192.168.1.66:5000/api/jobs/new'
        self.backend_url = 'https://career-scraper.herokuapp.com/api/jobs/new'
        self.jobs = {}
        self.page = 1
       
    def get_jobs(self, url):
        data = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(data.text, 'html.parser')
        names = []
        urls = []
        employers = []
        dates = []

        # print('Scraping page {}'.format(self.page))
        self.page += 1

        # Get name and url from anchor tags.
        for title in soup.find_all('h2', {'class': 'job-title'}):
            anchor = title.find('a')
            names.append(anchor.text.strip())
            urls.append(anchor.get('href'))

        # Get employer names
        for employer in soup.find_all('span', {'class': 'company-name'}):
            employers.append(employer.text.strip())
        
        # Get posting dates
        for date in soup.find_all('span', {'class': 'posted-time'}):
            d = datetime.strptime(date.text.strip(), 'Posted %b %d, %Y')
            d = d.strftime('%Y-%m-%d')
            dates.append(d)

        # Test that array sizes match
        if len(names) == len(urls) and len(urls) == len(employers) and len(employers) == len(dates):
            for i in range(len(names)):
                job = {
                    'name': names[i],
                    'employer': employers[i],
                    'url': urls[i],
                    'date_posted': dates[i],
                }
                self.jobs[urls[i]] = job

        # Now, fint 'next' anchor and rerun.
        next_page = soup.find('a', {'class': 'next link'})

        if next_page is not None:
            self.get_jobs(next_page.get('href'))

    def scrape(self):
        '''
        Loads jobs into memory
        '''
        self.get_jobs(self.prefix + self.eng_url)
        self.get_jobs(self.prefix + self.dev_url)

    def post_to_backend(self):
        resp = requests.post(self.backend_url, headers=self.headers, json=self.jobs)
        print(resp.status_code)
        print(resp.json())
        print()

def its_go_time():
    print(time.strftime("Starting at %A, %d. %B %Y %I:%M:%S %p"))
    s = Scraper()
    print('Scraping pages...')
    s.scrape()
    print('Posting to backend...')
    s.post_to_backend()
    print()

if __name__ == '__main__':
    its_go_time() 