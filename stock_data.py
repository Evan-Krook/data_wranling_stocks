# Libraries
import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from io import BytesIO
import csv
import os
### Need to insert a list of stock tickers and a filename that ends in .csv
def get_data(symbols, filename):
    stock_data = []
    for i in symbols:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'}
        url = f'https://finance.yahoo.com/quote/{i}'
        url_for_graph = f"https://finance.yahoo.com/chart/{i}/"
        r = requests.get(url, headers = headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        volume_text = soup.find('table', {'class': 'W(100%)'}).find_all(lambda tag: tag.name == 'td' and 'TD_VOLUME-value' in tag.get('data-test', ''))
        volume_cleaned = [volume.text.strip('[]') for volume in volume_text]
        avg_volume_text = soup.find('table', {'class': 'W(100%)'}).find_all(lambda tag: tag.name == 'td' and 'AVERAGE_VOLUME_3MONTH-value' in tag.get('data-test', ''))
        avg_volume_cleaned = [avg.text.strip('[]') for avg in avg_volume_text]
        yearly_range = soup.find('table', {'class': 'W(100%)'}).find_all(lambda tag: tag.name == 'td' and 'FIFTY_TWO_WK_RANGE-value' in tag.get('data-test', ''))
        yearly_range_cleaned = [r.text.strip('[]') for r in yearly_range]
        stock = {
        'Ticker': i,
        'Closing Price': soup.find('div', {'class':'D(ib) Mend(20px)'}).find_all('fin-streamer')[0].text,
        'Daily Price Change': soup.find('div', {'class':'D(ib) Mend(20px)'}).find_all('fin-streamer')[1].text,
        'Percentage Change': soup.find('div', {'class':'D(ib) Mend(20px)'}).find_all('fin-streamer')[2].text,
        'volume': ','.join(volume_cleaned),
        'Average 3 Month Volume': ','.join(avg_volume_cleaned),
        '52 Week Closing Price Range': ','.join(yearly_range_cleaned),
        'Graph Link': url_for_graph
        }
        stock_data.append(stock)
    df = pd.DataFrame(stock_data)
    df.set_index('Ticker', inplace=True)
    df.to_csv(filename, encoding='UTF-8', escapechar='\\', quotechar='"', quoting=csv.QUOTE_NONE)
    return df
# Symbol most be a string format of a stock ticker Ex: 'TSLA'
# timespan is one of 5 options: 'm1','m6','ytd','y1','y5','y10'
def historical_data(symbol, timespan):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'}
    url = f'https://www.nasdaq.com/market-activity/stocks/{symbol}/historical'
    options = Options()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    try:
        controls = driver.find_element(By.CLASS_NAME, "historical-data__controls")
        max_button = controls.find_element(By.XPATH, f'//button[@data-value="{timespan}"]')
        driver.execute_script("arguments[0].click();", max_button)
        download_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'historical-data__controls-button--download historical-download')]")))
        driver.execute_script("arguments[0].click();", download_button)
        time.sleep(5)
        downloads_folder = os.path.join(os.path.expanduser('~'), 'Downloads')
        csv_files = [file for file in os.listdir(downloads_folder) if file.endswith('.csv') and file.startswith('HistoricalData_')]
        if csv_files:
            most_recent_file = max(csv_files, key=lambda x: os.path.getmtime(os.path.join(downloads_folder, x)))
            csv_file_path = os.path.join(downloads_folder, most_recent_file)
            df = pd.read_csv(csv_file_path)
        return df
    finally:
        driver.quit()