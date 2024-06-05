import requests
import base64
import json
from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import datetime
from dateutil import parser
from dateutil.relativedelta import relativedelta


class NewsScraper(ABC):
    def __init__(self, searchQuery, max_pages=2, api_url='http://localhost:5043/api/news', source="Unknown"):
        self.searchQuery = searchQuery
        self.max_pages = max_pages
        self.api_url = api_url
        self.source = source
        self.all_data = []
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)

    @abstractmethod
    def scrape(self):
        pass

    @staticmethod
    def parse_date(date_str):
        try:
            if 'ago' in date_str:
                number, unit = date_str.split()[:2]
                unit = unit.rstrip('s')
                if unit == "hr" or unit == "hrs":
                    unit = "hour"
                delta_args = {f"{unit}s": -int(number)}
                date = datetime.datetime.now() + relativedelta(**delta_args)
            else:
                date = parser.parse(date_str)
            return date.strftime('%Y-%m-%dT%H:%M:%S')
        except Exception as e:
            print(f"解析日期出错 '{date_str}': {e}")
            return None

    def download_image_as_base64(self, url):
        try:
            response = requests.get(url)
            return base64.b64encode(response.content).decode('utf-8')
        except Exception as e:
            print(f"Failed to download or encode image: {e}")
            return None

    def send_data(self):
        headers = {'Content-Type': 'application/json'}
        try:
            response = requests.post(self.api_url, json=self.all_data, headers=headers)
            print("Data to be sent:", json.dumps(self.all_data, indent=2))
            print(f"Response from sending data: {response.status_code}")
        except Exception as e:
            print("Failed to send data:", e)

    def close(self):
        self.driver.quit()

class BBCScraper(NewsScraper):
    def __init__(self, searchQuery, max_pages=2, api_url='http://localhost:5043/api/news'):
        super().__init__(searchQuery, max_pages, api_url, "BBC")
        self.clear_data()

    def clear_data(self):
        try:
            response = requests.delete(f'{self.api_url}/clear')
            print(f"Response from clearing data: {response.text}")
        except Exception as e:
            print(f"Failed to clear data: {e}")

    def scrape(self):
        url = f"https://www.bbc.com/search?q={self.searchQuery}&filter=news"
        self.driver.get(url)
        page_count = 0
        while page_count < self.max_pages:
            articles = self.driver.find_elements(By.CSS_SELECTOR, "div[data-testid='liverpool-card']")
            for article in articles:
                try:
                    images = article.find_elements(By.CSS_SELECTOR, "img")
                    image_data = self.download_image_as_base64(images[0].get_attribute('src')) if images else 'No images found'
                    date_text = article.find_element(By.CSS_SELECTOR, "span[data-testid='card-metadata-lastupdated']").text if article.find_elements(By.CSS_SELECTOR, "span[data-testid='card-metadata-lastupdated']") else 'No date found'
                    parsed_date = self.parse_date(date_text)

                    data = {
                        'source': self.source,
                        'date': parsed_date,
                        'title': article.find_element(By.CSS_SELECTOR, 'h2').text if article.find_elements(By.CSS_SELECTOR, 'h2') else 'No title found',
                        'summary': article.find_element(By.CSS_SELECTOR, 'p').text if article.find_elements(By.CSS_SELECTOR, 'p') else 'No summary found',
                        'link': article.find_element(By.CSS_SELECTOR, 'a').get_attribute('href') if article.find_elements(By.CSS_SELECTOR, 'a') else 'No link found',
                        'imageData': image_data,
                        'searchQuery': self.searchQuery
                    }
                    self.all_data.append(data)
                except Exception as e:
                    print("Some elements were not found on the page.", str(e))

            if page_count < self.max_pages:
                try:
                    next_page = self.driver.find_element(By.CSS_SELECTOR, "button[data-testid='pagination-next-button']")
                    next_page.click()
                    time.sleep(10)
                    page_count += 1
                except Exception as e:
                    print("Error navigating pages:", str(e))
                    break


class CNNScraper(NewsScraper):
    def __init__(self, searchQuery, max_pages=2, api_url='http://localhost:5043/api/news'):
        super().__init__(searchQuery, max_pages, api_url, source="CNN")

    def scrape(self):
        url = f"https://edition.cnn.com/search?q={self.searchQuery}&from=0&size=10&page=1&sort=newest&types=all&section="
        self.driver.get(url)
        time.sleep(5)
        page_count = 0
        while page_count < self.max_pages:
            articles = self.driver.find_elements(By.CSS_SELECTOR, "div[data-component-name='card']")
            for article in articles:
                image_element = article.find_element(By.CSS_SELECTOR, "img") if article.find_elements(By.CSS_SELECTOR, "img") else None
                image_data = self.download_image_as_base64(image_element.get_attribute('src')) if image_element else 'No images found'
                date_text = article.find_element(By.CSS_SELECTOR, ".container__date.container_list-images-with-description__date").text if article.find_elements(By.CSS_SELECTOR, ".container__date.container_list-images-with-description__date") else 'No date found'
                parsed_date = self.parse_date(date_text)

                data = {
                    'source': self.source,
                    'date': parsed_date,
                    'title': article.find_element(By.CSS_SELECTOR, "span[data-editable='headline']").text if article.find_elements(By.CSS_SELECTOR, "span[data-editable='headline']") else 'No title found',
                    'summary': article.find_element(By.CSS_SELECTOR, 'p').text if article.find_elements(By.CSS_SELECTOR, 'p') else 'No summary found',
                    'link': article.find_element(By.CSS_SELECTOR, 'a').get_attribute('href') if article.find_elements(By.CSS_SELECTOR, 'a') else 'No link found',
                    'imageData': image_data,
                    'searchQuery': self.searchQuery
                }
                self.all_data.append(data)

            if page_count < self.max_pages:
                try:
                    next_page = self.driver.find_element(By.CSS_SELECTOR, ".pagination-arrow.pagination-arrow-right.search__pagination-link.text-active")
                    next_page.click()
                    time.sleep(10)
                    page_count += 1
                except Exception as e:
                    print("CNN Error navigating pages:", str(e))
                    break
            else:
                print("CNN Reached page limit of", self.max_pages)
                break

bbc_scraper = BBCScraper('Carbon credit')
bbc_scraper.scrape()
bbc_scraper.send_data()
bbc_scraper.close()

cnn_scraper = CNNScraper('Carbon credit')
cnn_scraper.scrape()
cnn_scraper.send_data()
cnn_scraper.close()
