from flask import Flask, url_for, request
from amazon.api import AmazonAPI
from operator import itemgetter
from lxml import html
import re
import requests
import json
from random import shuffle
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

def searchAmazon(searchFor,num) :
	Items = [];	
	amazon = AmazonAPI('AKIAIZRREBI4D4525X5A', 'xXUIW6s6IxRUCus6nRG92hkA49v7CEVBmbkm3R1p', 'asindropper-20')
	try:
		results = amazon.search_n( num , Keywords=searchFor , SearchIndex='All');	
		for product in	results:
			Items.append([product.title,float(product.price_and_currency[0]),product.large_image_url,"https://www.amazon.com/dp/" + product.asin]);
			
		return Items
	except:
		return [];
def searchEbay(searchFor,num) :
 	
 	Items = [];	
	URL = "http://www.ebay.com/sch/i.html?_from=R40&_sacat=0&_nkw=" + searchFor + "&rt=nc"
	page = requests.get(URL)
	tree = html.fromstring(page.content)
	isRes =  tree.xpath('//span[@class="rcnt"]/text()')[0]
	if int(isRes.replace(",", "")) == 0:
		return Items;
	Titles = tree.xpath('//h3[@class="lvtitle"]//a[@class="vip"]/text()')
	items = re.findall('.*listingId="(.+?)\".*',page.content)
	prices = tree.xpath('//li[@class="lvprice prc"]//span[@class="bold"]/text()')    
	images = re.findall('.*src="(https://.+jpg)\".*',page.content)
	fixPrices = []

	i = 0
	for price in prices:
		if '.' in price :
			fixPrices.insert(i, price)
			i+=1

	i = 0
	for item in items: 
		if i == num:
			return Items

		Items.append([Titles[i],fixPrices[i].translate(None, '\t\n,$ '),images[i],"https://www.ebay.com/itm/" + item])
		i+=1

  
 	return Items

def searchAliExpress(searchFor,num) :

	Items = [];
	URL = "https://www.aliexpress.com/wholesale?ltype=wholesale&d=y&origin=y&blanktest=0&SearchText=" + searchFor 
	page = requests.get(URL)
	tree = html.fromstring(page.content)
	#isRes = tree.xpath('//strong[@class="search-count"]/text()')[0]
	#print (isRes)
	#if int(isRes.replace(",", "")) == 0:
	#	return Items;
	Titles = tree.xpath('//a[@class="history-item product "]/@title')
	itemsTmp = tree.xpath('//a[@class="history-item product "]/@href')
	items = []
	j = 0
	for i in itemsTmp :
		items.insert(j, re.search('([0-9]+)\.html', i).group(0))
		j+=1
	prices = tree.xpath('//span[@itemprop="price"]/text()')    
	images = re.findall('.*src="(.+jpg)\".*',page.content)

	print (items)

	i = 0
	for item in items: 
		
		if i == num:
			return Items
		
		Items.append([Titles[i],prices[i].translate(None, '\t\n,US$ '),images[i], item])
		i+=1
  
  
	return Items

@app.route('/app-api')
def api_article():
	
	Response = {}
	items = [];
	search = request.args.get('search');
	ebay = request.args.get('ebay');
	amazon = request.args.get('amazon');
	aliexpress = request.args.get('aliexpress');

	if amazon == "true":
		items.extend(searchAmazon(search,12));
	if ebay == "true":
		items.extend(searchEbay(search,11))
	if aliexpress == "true":
		items.extend(searchAliExpress(search,11))
	
	itm = sorted(items, key=itemgetter(1))
	shuffle(itm)
	Response['items'] = itm;

	return json.dumps(Response)
	




if __name__ == '__main__':
    app.run()