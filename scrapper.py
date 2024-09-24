import csv
import logging
import os
import time
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

# Set up logging
logging.basicConfig(
    filename='scraper.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Set up Chrome options and binary location
options = webdriver.ChromeOptions()
options.binary_location = os.getenv('CHROME_BINARY_PATH', '/home/yashwanth/chrome-linux64/chrome')
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# Set the correct path to Chromedriver
driver_path = os.getenv('CHROMEDRIVER_PATH', '/home/yashwanth/chromedriver-linux64/chromedriver')

# Set up the Chrome WebDriver
service = Service(executable_path=driver_path)
driver = webdriver.Chrome(service=service, options=options)

# Load the website
url = 'https://timesofindia.indiatimes.com/topic/hyderabad-drug-arrest/news'
driver.get(url)
logging.info(f'Loaded website: {url}')

# Scroll down and load more articles
while True:
    try:
        load_more_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Load More Articles')]")
        load_more_button.click()
        time.sleep(2)  # Wait for the new articles to load
    except NoSuchElementException:
        logging.info('No more "Load More Articles" button found, stopping scroll')
        break
    except Exception as e:
        logging.error(f'Error while loading more articles: {e}')
        break

# Parse the HTML content
html = driver.page_source
soup = BeautifulSoup(html, 'lxml')

# Close the browser
driver.quit()

# Find all articles based on the correct div class
articles = soup.find_all('div', class_='uwU81')

# Check if CSV exists to avoid duplicates
csv_file = Path('timesofindia.csv')
existing_headlines = set()
if csv_file.exists():
    with csv_file.open('r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            existing_headlines.add(row[0])  # Add existing headlines to set

# Open the CSV file to write the data
with csv_file.open('a', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)

    # Write the header if the file is new
    if not existing_headlines:
        writer.writerow(['Headline', 'Date', 'Description'])

    # Loop through each article and extract details
    for article in articles:
        # Extract the headline
        headline_tag = article.find('div', class_='fHv_i o58kM')
        headline = headline_tag.get_text().strip() if headline_tag else 'No headline'

        # Check if the headline already exists to avoid duplication
        if headline in existing_headlines:
            continue

        # Extract the date
        date_tag = article.find('div', class_='ZxBIG')
        date_raw = date_tag.get_text().strip() if date_tag else 'No date'

        # Format the date
        try:
            date_clean = date_raw.split(' / ')[1] if len(date_raw.split(' / ')) > 1 else date_raw
            date_clean = date_clean.split(',')[0].strip()
            if len(date_clean.split()) == 2:
                date_clean += f', {datetime.now().year}'
            date = datetime.strptime(date_clean, '%b %d, %Y').strftime('%b %d, %Y')
        except (IndexError, ValueError) as e:
            logging.error(f'Date parsing error: {e} (date_raw="{date_raw}")')
            date = date_raw

        # Extract the description
        description_tag = article.find('p', class_='oxXSK o58kM')
        description = description_tag.get_text().strip() if description_tag else 'No description'

        # Write the data to the CSV file if it passes the checks
        if headline not in existing_headlines:
            writer.writerow([headline, date, description])
            existing_headlines.add(headline)
            logging.info(f'Saved article: {headline}')

logging.info('Scraping complete. Data saved to "timesofindia.csv".')