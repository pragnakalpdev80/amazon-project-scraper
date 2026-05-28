import logging
import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

logging.basicConfig(filename="scrapper.log",
                    format='%(asctime)s %(levelname)s: %(message)s',
                    filemode='a')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

class AmazonProjectorScraper:
    """ 
    """
    def __init__(self):
        """Initializes the browser."""
        self.service = Service(ChromeDriverManager().install())
        self.options = Options()
        self.options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.265 Safari/537.36"
        )
        self.driver = webdriver.Chrome(service=self.service, options=self.options)
        self.driver.implicitly_wait(5)
    
    def open_url(self, url):
        """Opens the URL using this method."""
        self.driver.get(url=url)
        self.driver.maximize_window()

    def search(self, item):
        """Search Item using this method"""
        logger.info(f"Searching for {item}")
        search = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@class='nav-input nav-progressive-attribute']")))
        search.send_keys(item)
        item_url = search.send_keys(Keys.RETURN)
        self.driver.switch_to.frame(item_url)
    
    def filter_brand(self, brand_name):
        """Applies filter """
        try:
            see_more = self.driver.find_element(By.XPATH, "//a[@aria-label='See more, Brands']")
            time.sleep(1) 
            see_more.click()
            time.sleep(3)
        except NoSuchElementException:
            logger.error("See more option is not available.")

        try:
            filter_element = self.driver.find_element(By.LINK_TEXT, brand_name)
            time.sleep(1) 
            filter_element.click()
            time.sleep(3)
        except NoSuchElementException:
            logger.error(f"Brand {brand_name} not found")

    def filter_price(self, price):
        try:
            filter_element = self.driver.find_element(By.LINK_TEXT, price)
            time.sleep(1) 
            filter_element.click()
            time.sleep(3)
        except NoSuchElementException:
            logger.error(f"Filter range not found")

    def filter_review(self):
        try:
            filter_element = self.driver.find_element(By.XPATH, "//i[@class='a-icon a-icon-star-medium a-star-medium-4']")
            time.sleep(1) 
            filter_element.click()
            time.sleep(3)
        except NoSuchElementException:
            logger.error(f"Stars not found")

    def scrape_top_10(self):
        """Extracts details of the top 10 products from the search results."""
        logger.info("Extracting product data")
        extracted_data = []

        try:
            products = self.driver.find_elements(By.XPATH, "//div[@data-component-type='s-search-result']")
            items = 0

            for product in products:
                if items >= 10:
                    break

                try:
                    product_name = product.find_element(By.XPATH, ".//a/h2/span")
                    name = product_name.text 
                except Exception as exc:
                    name = False
                    logger.error(exc)
                
                try:
                    product_price = product.find_element(By.XPATH, ".//span[@class='a-price-whole']")
                    price = product_price.text
                except Exception as exc:
                    price = False
                    logger.error(exc)
                
                try:
                    product_rating = product.find_element(By.XPATH, ".//span[@class='a-size-small a-color-base']")
                    rating = product_rating.text
                except Exception as exc:
                    rating = False
                    logger.error(exc)
                
                try:
                    product_reviews = product.find_element(By.XPATH, ".//span[@class='a-size-mini puis-normal-weight-text s-underline-text']")
                    reviews = product_reviews.text
                except Exception as exc:
                    reviews = False
                    logger.error(exc)
                
                try:
                    product_url = product.find_element(By.XPATH, ".//a")
                    url = product_url.get_attribute("href")
                except Exception as exc:
                    url = False
                    logger.error(exc)
                
                if name:
                    extracted_data.append({
                        "Name":name,
                        "Price":price,
                        "Rating":rating,
                        "Reviews":reviews,
                        "URL":url
                    })
                    items+=1

        except Exception as exc:
            logger.error(exc)
        
        return extracted_data

    def save_to_csv(self, data, filename):
        try:
            fields = ["Name", "Price", "Rating", "Reviews", "URL"]
            with open(filename, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=fields)
                writer.writeheader()
                writer.writerows(data)

        except Exception as exc:
            logger.error(f"Failed to save data: {exc}")

    def close(self):
        """Closes the browser."""
        logger.info("Closing browser")
        self.driver.quit()


if __name__ == "__main__":
    logger.info("Automation Starting")
    automate = AmazonProjectorScraper()
    automate.open_url(url="https://www.amazon.in/")
    automate.search(item="Projectors")
    automate.filter_brand(brand_name="ZEBRONICS")
    automate.filter_brand(brand_name="Portronics")
    automate.filter_price(price="Up to ₹9,500")
    automate.filter_review()
    data = automate.scrape_top_10()
    automate.save_to_csv(data=data, filename="projectors.csv")
    automate.close()
    logger.info("Automation Completed")
    

