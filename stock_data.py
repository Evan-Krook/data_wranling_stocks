#Libraries
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import csv
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
    