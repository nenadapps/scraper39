from bs4 import BeautifulSoup
import datetime
from random import randint
from random import shuffle
import requests
from time import sleep
import string

base_url = 'https://commonwealth-stamps.com'

def get_html(url):
    
    html_content = ''
    try:
        page = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        html_content = BeautifulSoup(page.content, "html.parser")
    except: 
        pass
    
    return html_content

def get_details(url):
    
    stamp = {}
    
    try:
        html = get_html(url)
    except:
        return stamp

    html_string = str(html)

    try:
        title = html.select('#content h2')[0].get_text().strip()
        title = title.replace('Browse By Country -', '').strip()
        title = title.replace('                  ',' ').strip()
        stamp['title'] = title
    except:
        stamp['title'] = None
        
    try:
        price_parts = html_string.split('<b>Price:</b>')
        price_parts2 = price_parts[1].split('<br/>')
        price = price_parts2[0].replace('£', '').replace(',', '').strip()
        stamp['price'] = price
    except: 
        stamp['price'] = None        
        
    try:
        sg_parts = html_string.split('<b>SG ')
        sg_parts2 = sg_parts[1].split('</b>')
        sg = sg_parts2[0].strip()
        stamp['sg'] = sg
    except:
        stamp['sg'] = None        

    try:
        raw_text_parts = html_string.split('<b>Price:</b>')
        raw_text_parts2 = raw_text_parts[0].split('>SG ' + sg + '</b>')
        raw_text = raw_text_parts2[-1].strip()
        raw_text = raw_text.replace('\r\n', ' ').replace('\t', ' ').replace('<br/>', '').strip()
        stamp['raw_text'] = raw_text.replace('"',"'")
    except Exception as e: 
        print(e)
        pass 
  
    
    stamp['currency'] = 'GBP'
    
    # image_urls should be a list
    images = []                    
    try:
        image_cont = html.select('.image-link')[0]
        img = base_url + image_cont.get('href')
        if img not in images:
                images.append(img)
    except:
        pass
    
    stamp['image_urls'] = images 
        
    # scrape date in format YYYY-MM-DD
    scrape_date = datetime.date.today().strftime('%Y-%m-%d')
    stamp['scrape_date'] = scrape_date

    stamp['url'] = url
    print(stamp)
    print('+++++++++++++')
    sleep(randint(25, 65))
           
    return stamp

def get_page_items(url):
    
    items = []
    next_url = ''

    try:
        html = get_html(url)
    except:
        return items, next_url

    try:
        for item_cont in html.select('.stamp-view a'):
            item_link = base_url + item_cont.get('href')
            item_text = item_cont.get_text()
            if (item_link not in items) and (item_text == 'More Info'):
                items.append(item_link)
    except:
        pass
    
    try:
        next_cont = html.select('.nextprevHolderRight a')[0]
        next_page = base_url + next_cont.get('href')
    except:
        pass
    
    shuffle(list(set(items)))
    
    return items, next_url

def get_categories(letter):
   
    url = 'https://commonwealth-stamps.com/browse/country.asp?c=' + letter
    
    items = []

    try:
        html = get_html(url)
    except:
        return items

    try:
        for item in html.select('a.setcount'):
            item_link = base_url + item.get('href')
            if item_link not in items: 
                items.append(item_link)
    except: 
        pass
    
    shuffle(list(set(items)))
    
    return items

for letter in list(string.ascii_uppercase):
    categories = get_categories(letter)
    for category in categories:
        while(category):
            page_items, category = get_page_items(category)
            for page_item in page_items:
                stamp = get_details(page_item)

