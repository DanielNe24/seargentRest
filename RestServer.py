from flask import Flask, url_for, request
from amazon.api import AmazonAPI
from operator import itemgetter
from lxml import html
import re
import requests
import json
from random import shuffle
from flask_cors import CORS
from ebaysdk.finding import Connection as Finding

_token = 'AgAAAA**AQAAAA**aAAAAA**N+sxWQ**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6AElYWoAJKEpwmdj6x9nY+seQ**U4sDAA**AAMAAA**Nwx+CW2wjUp7dWuYW5Sss13HGQSoMITtqMxP6T/WEUALcgDiJIKsmj99aaGTMoaYGXjiDRvTNZeNPa0J3RqqiKabKH+/40Cun3+FIXIc65st82mc38/zptnMcWojjjFNJKX5DuhZZVo76fIvGAPwtlurFwjQ9DSBp/KVvgu08mo8CLon1eaTeKK4aRscop6KcM0o3fmQyTDm5T28i4lgU0elr+iLQzTB4kO7oWwHbfoYU5AjOC3Gix4yWYfv2Aa/D8fgEi7Izxx85EZhPFuOxYcP5+5V51bL7xuA5Y5M9xxXR6vvbKVpsF6+OIohyTdcgJ+NPXDLNFRE9oidHedY0hg/bke6SYF/xg5FQGZVe2xUxnhs/yyo+C/tmW/ieZ/QvqYAdxkAN+3f6H0wg/yiGANbA7ifGXSO92hxW1dQk8j98BAwhwf15PxKWhd+T1VtND0YaVBTxbARTSQXOT2Ye/+Sz30Ur1hPYJfCUfZ338ws5hWci7hRwxqWLaDCBaE0Raqb8UUwE9LfmGiISJQZb+o8k85Pri4O0o5hJyWd+inYLyN7yh0iMDCPZHOkTKNd+X1vXyFbHyJZRs6oBz/hEnsc/iZ0/9h9asU1SZIlOdz8BlcUUu3yrtEpWT5rLiRAuMp7j8mPOvEbCXXpB00yTZk+2YLZ3RW/6bmFGED46mqU+qcZF3i1k9nqiJHcStBGbIhZowxYNal1XjE72gea7kiWwSstRaxKKowGbOWhwc0XrevPchkdVnYNoGDdpqo/'
_appid = 'danielne-asindrop-PRD-245f6444c-0b329f66'
_devid = '81cbe858-14b1-46a8-b58d-8d5d5d173752'
_certid = 'PRD-45f6444c5133-3e3f-4dae-89de-94c6'
confFile = 'myebay.yaml'
api = Finding(appid=_appid, devid=_devid, certid=_certid, token=_token, debug=False, config_file=confFile) 
amazon = AmazonAPI('AKIAIX7PZUL6KS4WJHMA', '4m1PO6fmdGmoO4Fw0P4sfha9P6dVtVjsRYzaE+yA', 'asindroppe0b1-20')

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

def searchAmazon(searchFor,num) :
	Items = [];	
	print (searchFor)
	try:
		results = amazon.search_n( num , Keywords=searchFor , SearchIndex='All');	
		for product in	results:
			Items.append([product.title,float(product.price_and_currency[0]),product.large_image_url,"https://www.amazon.com/dp/" + product.asin]);
			
		print (Items)
		return Items
	except:
		return [];

def searchEbay(searchFor,num) :

	Items = []
	i = 0
	response = api.execute('findItemsAdvanced', {'keywords': searchFor})
	for itm in response.reply.searchResult.item:

		if i == num :
			return Items
		
		Items.append([itm.title, itm.sellingStatus.currentPrice.value, itm.galleryURL,  itm.viewItemURL])
		i+=1
	
 	return Items

def searchAliExpress(searchFor,num) :

	Items = [];
	URL = "https://www.aliexpress.com/wholesale?ltype=wholesale&d=y&origin=y&blanktest=0&SearchText=" + searchFor 
	page = requests.get(URL)
	tree = html.fromstring(page.content)
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
		items.extend(searchAmazon(search,4));
	if ebay == "true":
		items.extend(searchEbay(search,4))
	if aliexpress == "true":
		items.extend(searchAliExpress(search,4))
	
	itm = sorted(items, key=itemgetter(1))
	shuffle(itm)
	Response['items'] = itm;

	return json.dumps(Response)
	




if __name__ == '__main__':
    app.run()