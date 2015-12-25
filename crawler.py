#! /usr/bin/python3
import sys
import pickle
import re
from urllib.request import *
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time

def isCategoryUrl(url):
    return bool(re.match(r'.*-c-\d*\.html', str(url)))
    
def getIdFromUrl(url):
    match = re.match(r'.*-p-(\d*)\.html', str(url))
    if match:
        return match.group(1)
    
def buildItem(li):
    item = {}
    item['uri'] = str(li.find('span', class_='title').a.get('href'))
    item['id'] = getIdFromUrl(item['uri'])
    item['price'] = float(li.find('span', class_='price').get('oriprice'))
    item['date'] = datetime.now()
    return item
    
def getItems(soup):
    lista = soup.find('ul', class_='goodlist_1') 
    return [buildItem(item) for item in lista.find_all('li')]
    
def addItems(catalog, items):
    for item in items:
        if item['id'] in catalog and item['date'] - catalog[item['id']]['date'] > timedelta(hours=48):
            print("DEBUG: Updated item")
            catalog[item['id']]['price'] = item['price']
            if abs(catalog[item['id']]['price'] - item['price']) > item['price']*0.20:
                print("HIGH diference: " + str(item))
            if catalog[item['id']]['uri'] != item['uri']:
                print("url changed: " + item)
                catalog[item['id']]['uri'] = item['uri']
        else:
            #print("DEBUG: Inserted item "+ str(item))
            catalog[item['id']] = item

def main(argv):
    if len(argv) < 1:
        print("Error. Usage: crowler <catalog file>")
        sys.exit(2)

    try:
        catalog = pickle.load(open(argv[0], 'rb'))
    except:
        catalog = {}
    
    try:
        uri = 'http://www.banggood.com/'
        html = urlopen(uri).read()
        soup = BeautifulSoup(html, 'html.parser')
        categories_bulk = soup.find_all('a')
        # todas las categorias existentes
        categories = [x for x in categories_bulk if isCategoryUrl(x.get('href'))]
        
        # recorremos todos los items de categoria (paginados)
        for uri in categories:
            while (uri):
                print("DEBUG: " + str(uri))
                try:
                    html = urlopen(uri.get('href')).read()
                except:
                    time.sleep(5) # wait 5 seconds to retry
                    print("Error page: " + uri.get('href') + ". Retrying...")
                    continue # retry same url (infinite loop until page is on)
                soup = BeautifulSoup(html, 'html.parser')
                items = getItems(soup)
                addItems(catalog, items)
                uri = soup.find('a', title='Next page')
            print(len(catalog))
            time.sleep(20) 
            
    except:
        pickle.dump(catalog, open(argv[0], 'wb'))
        sys.exit(0)
        
    pickle.dump(catalog, open(argv[0], 'wb'))

if __name__ == "__main__":
   main(sys.argv[1:])
