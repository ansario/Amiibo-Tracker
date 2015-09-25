#!/usr/bin/env python
# -*- coding: utf-8 -*-

from amazonproduct import API
import time
import urllib, json
import mailchimp
import json

import sys

reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF-8')

amazonUS = API("XXXXXXXXXXXXXXXXXXXX", "XXXXXXXXXXXXXXXXXXXX", "us", "XXXXXXXXXXXXXXXXXXXX")
amazonCA = API("XXXXXXXXXXXXXXXXXXXX", "XXXXXXXXXXXXXXXXXXXX", "ca", "XXXXXXXXXXXXXXXXXXXX")
amazonUK = API("XXXXXXXXXXXXXXXXXXXX", "XXXXXXXXXXXXXXXXXXXX", "uk", "XXXXXXXXXXXXXXXXXXXX")
amazonDE = API("XXXXXXXXXXXXXXXXXXXX", "XXXXXXXXXXXXXXXXXXXX", "de", "XXXXXXXXXXXXXXXXXXXX")
amazonIT = API("XXXXXXXXXXXXXXXXXXXX", "XXXXXXXXXXXXXXXXXXXX", "it", "XXXXXXXXXXXXXXXXXXXX")
amazonFR = API("XXXXXXXXXXXXXXXXXXXX", "XXXXXXXXXXXXXXXXXXXX", "fr", "XXXXXXXXXXXXXXXXXXXX")
bestbuyUS = "http://api.remix.bestbuy.com/v1/products(search=amiibo&manufacturer=Nintendo)?format=json&show=sku,name,salePrice,onlineAvailability,url&apiKey=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX&pageSize=50"


def searchAmazon(API):
    hash_of_items = {}
    try:
        for item in API.item_search('VideoGames', Title='Amiibo', MerchantId="Amazon", Availability="Available"):

            product = item.ItemAttributes
            product_name = product.Title
            product_manufacturer = product.Manufacturer.text
            product_url = item.DetailPageURL.text

            if 'Nintendo' in product_manufacturer:
                hash_of_items.update({product_name: product_url})
    except:
        print "NAH"     
    return hash_of_items


def searchBestbuy(API):
    hash_of_items = {}

    response = urllib.urlopen(API)
    data = json.loads(response.read())

    for product in range(0, len(data['products'])):

        if 'amiibo' in data['products'][product]['name']:

            product_name = str(data['products'][product]['name'])
            product_availability = str(data['products'][product]['onlineAvailability'])
            product_url = str(data['products'][product]['url'])

            if product_availability:
                hash_of_items.update({product_name: product_url})


    return hash_of_items


def mail(mailingList, amiibo, retailer_site, retailer_site_url):
    key = 'XXXXXXXXXXXXXXXXXXXX'
    m = mailchimp.Mailchimp(key)

    m.campaigns.create("regular", options={
        'list_id': '19cdbd681f',
        'subject': "New " + amiibo + " on " +  retailer_site,
        "from_email": "no-reply-tracking@myamiibotracker.com",
        "from_name": "Amiibo Tracker",
        "to_name": "Amiibo Tracker",
        "auto_footer": False
    },
                       content={
                           'html': '<p>Hello *|FNAME|*, </p> <h3>We just found ' + amiibo + ' on ' + retailer_site + '! <br> <br> If you would like to view the product page for this amiibo, visit this direct link: <a href="' + retailer_site_url + '"> ' + retailer_site + '</a> </h3> <p> If there is anything we can do for you, please let us know by tweeting at us: <a href="http://twitter.com/amiibo_tracker">@amiibo_tracker</a>!<br> <p> As a reminder, you are subscribed to the following amiibo: <br> <br> <br><b> SSB Wave 1:</b> *|WAVE1|* <br><br><b> SSB Wave 2:</b> *|WAVE2|* <br> <br><b> SSB Wave 3:</b> *|WAVE3|* <br> <br><b> SSB Wave 4:</b> *|WAVE4|* <br> <br><b> SSB Wave 5:</b> *|WAVE5|* <br> <br><b> Retailers:</b> *|RETAILER|* <br> <br><b> SMB Wave 1:</b>: *|SMBWAVE1|* <br> <br><b> Splatoon Wave 1: </b> *|SPLATWAVE1|* <br> <br><b> Aggressive Tracking:</b> *|AGGRESSIVE|* </p> <p>If you would like to unsubscribe or change your subscription settings, please visit your <a href="http://myamiibotracker.com/my-account/?a=edit">profile page</a>.</p> <p> MyAmiiboTracker.com | Columbia, SC 29201 | <a href="http://myamiibotracker.com/contact/">Contact Us</a></p>',
                           'text': 'New Amiibo ' + amiibo + ' on ' + retailer_site + '! Link: ' + retailer_site_url
                       },
                       segment_opts={'saved_segment_id': str(mailingList)}
                       )

    campaigns = m.campaigns.list()
    for campaign in campaigns['data']:
        cid = campaign['id']
        try:
            m.campaigns.send(cid)
        except:
            print "LIST EMPTY"
        break

def getIDNum(amiibo, retailer):
    
    json_data = open("amiibo.json")
    data = json.load(json_data)  

    print amiibo

    for x in data["amiibo"]:
        
        searching = str(amiibo).split(' ')
        
        names = str(x["name"]).split(',')
        names = [item.strip(' ') for item in names]
        cannot_include = str(x["cannot_include"]).split(',')
        cannot_include = [item.strip(' ') for item in cannot_include]

        for name in names:
            
            if name in amiibo and retailer in x["retailer"] and (len(cannot_include) == 1) and name:
            
                return x["id"]
            
            elif name in amiibo and retailer in x["retailer"] and (len(cannot_include) > 1) and name:
                FLAG = 1
                for cannot_include_string in cannot_include:
                    if cannot_include_string in searching:
                        FLAG = 0

                if FLAG:
                              
                 return x["id"]
            else:
                if retailer in x["retailer"] and "Unknown" in name and name:
                    return x["id"]

def doTheSearch(old_product_hash, new_product_hash, retailer):

    difference_hash = {}
    idNum = 0
    idName = ""
    idURL = ""
    # print "COMPARING " + str(old_product_hash) + " AGAINST " + str(new_product_hash)
    for key in new_product_hash.keys():
        if (not old_product_hash.has_key(key)):
            difference_hash.update({key : new_product_hash.get(key)})

    if difference_hash:
        for key in difference_hash:
            
            idName = str(key)
            idNum = getIDNum(idName, retailer)
            idURL = difference_hash.get(key)
            # print idNum
            
            try:
                mail(idNum, idName, retailer, idURL)
            except:
                print "NO"
            time.sleep(1)

            old_product_hash = new_product_hash




old_amazon_us_hash = searchAmazon(amazonUS)
time.sleep(2)
old_amazon_ca_hash = searchAmazon(amazonCA)
time.sleep(2)
old_amazon_uk_hash = searchAmazon(amazonUK)
time.sleep(2)
old_amazon_de_hash = searchAmazon(amazonDE)
time.sleep(2)
old_amazon_fr_hash = searchAmazon(amazonFR)
time.sleep(2)
old_amazon_it_hash = searchAmazon(amazonIT)
time.sleep(2)
try:
    old_bestbuy_us_hash = searchBestbuy(bestbuyUS)
except:
    print "BLAH"
time.sleep(2)



while(True):

    print "CHECKING AGAIN"
    new_amazon_us_hash = searchAmazon(amazonUS)
    time.sleep(2)
    new_amazon_ca_hash = searchAmazon(amazonCA)
    time.sleep(2)
    new_amazon_uk_hash = searchAmazon(amazonUK)
    time.sleep(2)
    new_amazon_de_hash = searchAmazon(amazonDE)
    time.sleep(2)

    new_amazon_fr_hash = searchAmazon(amazonFR)
    time.sleep(2)
    new_amazon_it_hash = searchAmazon(amazonIT)
    time.sleep(2)
    try:
        new_bestbuy_us_hash = searchBestbuy(bestbuyUS)
    except:
        print "BLAH"
    time.sleep(2)


    
    doTheSearch(old_amazon_us_hash, new_amazon_us_hash, "Amazon.com")
    doTheSearch(old_amazon_ca_hash, new_amazon_ca_hash, "Amazon.ca")
    doTheSearch(old_amazon_uk_hash, new_amazon_uk_hash, "Amazon.co.uk")
    doTheSearch(old_amazon_de_hash, new_amazon_de_hash, "Amazon.de")
    doTheSearch(old_amazon_fr_hash, new_amazon_fr_hash, "Amazon.fr")
    doTheSearch(old_amazon_it_hash, new_amazon_it_hash, "Amazon.it")
    doTheSearch(old_bestbuy_us_hash, new_bestbuy_us_hash, "Bestbuy.com")
        
   

    old_amazon_us_hash = new_amazon_us_hash
    old_amazon_ca_hash = new_amazon_ca_hash
    old_amazon_uk_hash = new_amazon_uk_hash
    old_amazon_de_hash = new_amazon_de_hash
    old_amazon_fr_hash = new_amazon_fr_hash
    old_amazon_it_hash = new_amazon_it_hash
    old_bestbuy_us_hash = new_bestbuy_us_hash




