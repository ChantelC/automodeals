# -*- coding: utf-8 -*-

'''The following function should ONLY be called from within the automodeals root directory.
This is largely due to the error logging functionality in case of exception during liters string parsing.
Said logging functionality is hard coded for error directory within automodeals and is NOT an absolute path.'''

from bs4 import BeautifulSoup # if this isn't installed, use pip install beautifulsoup4
import requests
import re
import pandas as pd
import numpy as np
from datetime import datetime
import time
import progressbar # if this isn't installed, use pip install progressbar2
import random
from itertools import cycle
import os
from generateProxies import generateProxies
from removeduplicates import removeduplicates

def carscraper(**kwargs):
    '''VARIABLE INPUTS:
    url: should be of the form "https://cars.ksl.com/search/newUsed/Used;Certified/perPage/96/page/0"
    rooturl: should be something like "https://cars.ksl.com"
    prev_links: a set of the full URL for each listing in the repository
    use_proxy: a boolean or binary to indicate if a proxy should be used
    curr_proxy: a string indicating the current proxy IP from last function call
    proxydict: a dictionary of proxy IPs and associated user-agents to cycle through
    refreshmin: the number of minutes to wait before updating the proxy pool
    
    ***NOTE: This function is meant to work with a pool of proxy IPs and various spoofed user-agents'''
    
    # Need to spoof a user-agent in order to get past crawler block
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
    
    the following were pulled manually on 3/12/20 from https://www.whatismybrowser.com/guides/the-latest-user-agent/
    user_agents = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
                   'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
                   'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
                   'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/74.0',
                   'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:61.0) Gecko/20100101 Firefox/74.0',
                   'Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/74.0',
                   'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0 Safari/605.1.15',
                   'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36 Edg/80.0.361.62',
                   'Mozilla/5.0 (Windows NT 10.0; Trident/7.0; rv:11.0) like Gecko']
    
    
    # Parse the kwargs

    
    if 'url' in kwargs.keys():
        if isinstance(kwargs['url'],str):
            url = kwargs['url']
        else:
            raise TypeError(f'Expected string for url but got {type(kwargs["url"])}.')
    else:
        raise ValueError('url is a required input for carscraper().')
        
    if 'rooturl' in kwargs.keys():
        if isinstance(kwargs['rooturl'],str):
            rooturl = kwargs['rooturl']
        else:
            raise TypeError(f'Expected string for rooturl but got {type(kwargs["rooturl"])}.')
    else:
        raise ValueError('rooturl is a required input for carscraper().')
        
    if 'prev_links' in kwargs.keys():
        if isinstance(kwargs['prev_links'],set):
            prev_links = kwargs['prev_links']
        else:
            raise TypeError(f'Expected set for prev_links but got {type(kwargs["prev_links"])}.')
    else:
        prev_links = set() # make a dummy set to check links against
        
    if 'use_proxy' in kwargs.keys():
        if isinstance(kwargs['use_proxy'],int) or isinstance(kwargs['use_proxy'],bool):
            use_proxy = kwargs['use_proxy']
        else:
            raise TypeError(f'Expected int or bool for use_proxy but got {type(kwargs["use_proxy"])}.')
    else:
        # default is to NOT use proxy
        use_proxy = False


    # Try and scrape the current search page without a proxy each time carscraper is called (just in case IP has been un-blocked)
    resp = requests.get(url, headers = {'User-Agent': user_agent})
    
    if resp.status_code == 403:
        print('Congrats! your current IP is blocked (still). Switching to a proxy.')
		print()
        use_proxy = True
    else:
        use_proxy = False

    if use_proxy:
        # The following inputs are only useful when using a proxy
        
        if 'proxydict' in kwargs.keys():
            if isinstance(kwargs['proxydict'],dict):
                proxydict = kwargs['proxydict']
            else:
                print(f'Expected dict type for proxydict but got {type(kwargs["proxydict"])}. Generating new proxydict...')
                newproxies = generateProxies()
                proxydict = {i:random.choice(user_agents) for i in newproxies}
        else:
            print('No proxydict found. Generating...')
            newproxies = generateProxies()
            proxydict = {i:random.choice(user_agents) for i in newproxies}

        if 'refreshmin' in kwargs.keys():
            if isinstance(kwargs['refreshmin'],int) or isinstance(kwargs['refreshmin'],float):
                refreshmin = kwargs['refreshmin']
            else:
                refreshmin = 15
                print(f'Expected int or float for refreshmin but got {type(kwargs["refreshmin"])}. Set to default value of {refreshmin}.')
        else:
            refreshmin = 15
            print(f'No refreshmin found. Set to default value of {refreshmin}.')
        
        tstart = time.time() # set a start time to use for refreshing proxy list (if needed)    

        if 'currproxy' in kwargs.keys():
            if isinstance(kwargs['currproxy'],str):
                currproxy = kwargs['currproxy']
            else:
                proxy_pool = cycle(proxydict) # make a pool of proxies 
                currproxy = next(proxy_pool) # grab the next proxy in cycle
        else:
            proxy_pool = cycle(proxydict) # make a pool of proxies 
            currproxy = next(proxy_pool) # grab the next proxy in cycle                


        chkproxy = 1
        while chkproxy:
            if (time.time() - tstart) > 60*refreshmin: # check if it's been more than refreshmin minutes since proxy_pool updated
                print('Refreshing proxy pool...')

                tstart = time.time() # reset start time

                currproxies = set(proxydict.keys())
                newproxies = generateProxies()
                newproxies = newproxies.difference(currproxies)

                if newproxies:
                    newdict = {i:random.choice(user_agents) for i in newproxies}
                    proxydict.update(newdict)
                    proxy_pool = cycle(proxydict)
                    currproxy = next(proxy_pool)
                    print('Proxy pool updated!')

            try:
                resp = requests.get(url,proxies={"http":currproxy, "https":currproxy},headers={'User-Agent': proxydict[currproxy]}, timeout=20)
                if resp.status_code == 403:
                    # congrats, your proxy IP just got blocked!
                    chkproxy = 1
                else:
                    # proxy was successful
                    chkproxy = 0
            except:
                prevproxy = currproxy
                currproxy = next(proxy_pool)
                print(f'Proxy error for {prevproxy}! Next up is {currproxy}')

        
    html = resp.content
    pgsoup = BeautifulSoup(html, "html.parser")
    
    # Check if there are additional pages of results
    if pgsoup.find("a", {"title" : "Go forward 1 page"}):
        moreresults = 1
    else:
        moreresults = 0
    
    links = pgsoup.select("div.title > a.link") # grab all 96 (or up to 96) links
	
    # Check to make sure all links are new on this search page
    fulllinks = set()
    for link in links:
	
	    # We're going to want to strip the "?ad_cid=[number]" from the end of these links as they're not needed to load the page properly
        # Regular expressions should come in handy here
        cutidx = re.search('(\?ad_cid=.+)',link['href']).start()
        currlink = link['href'][:cutidx]

        # Generate full link for the current listing
        fulllink = '/'.join([rooturl.rstrip('/'), currlink.lstrip('/')])
        fulllinks.add(fulllink)
    
    # Check against full set from repo
    fulllinks = fulllinks.difference(prev_links)
    if not fulllinks:
        print('Exiting carscraper function')
        if use_proxy:
            # order of return below is curr_cars, moreresults, currproxy, proxydict, use_proxy
            return None, 0, None, None, use_proxy
        else:
            # order of return below is curr_cars, moreresults, use_proxy
            return None, 0, use_proxy

    # Loop through links and scrape data for each new listing
    all_cars = []
    with progressbar.ProgressBar(max_value=len(fulllinks)) as bar:
        for idx, fulllink in enumerate(fulllinks): # *** only load first x results for now to avoid ban before implementing spoofing

            # Reset all fields to None before next loop
            price=year=make=model=body=mileage=title_type=city=state=seller=None
            trim=ext_color=int_color=transmission=liters=cylinders=fuel_type=n_doors=ext_condition=int_condition=drive_type=None

            # Try to load the page without a proxy first, if it worked for the main search page, above
            if not use_proxy:
                resp = requests.get(fulllink, headers = {'User-Agent': user_agent})
                if resp.status_code == 403:
                    print('Congrats! your current IP is blocked (still). Switching to a proxy.')
                    use_proxy = True

            if use_proxy:
                chkproxy = 1
                while chkproxy:
                    if (time.time() - tstart) > 60*refreshmin: # check if it's been more than refreshmin minutes since proxy_pool updated
                        print('Refreshing proxy pool...')

                        tstart = time.time() # reset start time

                        currproxies = set(proxydict.keys())
                        newproxies = generateProxies()
                        newproxies = newproxies.difference(currproxies)

                        if newproxies:
                            newdict = {i:random.choice(user_agents) for i in newproxies}
                            proxydict.update(newdict)
                            proxy_pool = cycle(proxydict)
                            currproxy = next(proxy_pool)
                            print('Proxy pool updated!')

                    try:
                        resp = requests.get(fulllink,proxies={"http":currproxy, "https":currproxy},headers={'User-Agent': proxydict[currproxy]}, timeout=20)
                        if resp.status_code == 403:
                            # congrats, your proxy IP just got blocked!
                            chkproxy = 1
                        else:
                            # proxy was successful
                            chkproxy = 0
                    except:
                        prevproxy = currproxy
                        currproxy = next(proxy_pool)
                        print(f'Proxy error for {prevproxy}! Next up is {currproxy}')

            
            lsthtml = resp.content
            lstsoup = BeautifulSoup(lsthtml, "html.parser")
            
            # Check if link is still good (i.e. listing is still active)
            if lstsoup.title.text.strip().lower() == 'not found':
                print('Bad link. Skipping...')
                bar.update(idx)
            else:

                # Get timestamp <-- no longer works as of March 17, 2020 due to removal of frontend js calculation of display date
#                 tstamp = int(re.search('(\d+)',tstamps[idx].text).group(0))

                # Get post date
                poststr = lstsoup.select('h2.location')[0].text.strip()
                poststr = re.search(r'Posted\s([\w\s\d,]+)',poststr)
                poststr = poststr.group(1)
                postdate = datetime.strptime(poststr, '%B %d, %Y') # Convert to type to datetime
                
                # Check if date is newer than maxts (with some leniency for same day)
                # if datetime.timestamp(postdate) < maxts:
                    # print('************ Found end of new data ************')
                    # moreresults = 0
                    # break

                # Get listing price
                price = lstsoup.select('h3.price')[0].text.strip().replace('$','').replace(',','')

                # Get seller's location
                if lstsoup.select('h2.location > a'):
                    location = lstsoup.select('h2.location > a')[0].text.strip()
                    city, state = location.split(',')
                    city = city.strip()
                    state = state.strip()

                # Get seller type (dealer or owner)
                sellerstr = lstsoup.select('div.fsbo')[0].text.strip()
                if re.search('(Dealer)', sellerstr):
                    seller = 'Dealer'
                elif re.search('(Owner)', sellerstr):
                    seller = 'Owner'
                    
                # Get number of photos
                if lstsoup.select('div.slider-uninitialized > p'):
                    picstr = lstsoup.select('div.slider-uninitialized > p')[0].text.strip()
                    n_pics = int(re.search('(\d+)',picstr).group())
                else:
                    if lstsoup.find(id='widgetPhoto').p:
                        picstr = lstsoup.find(id='widgetPhoto').p.text.strip()
                        n_pics = int(re.search('(\d+)',picstr).group())
                    else:
                        n_pics = 0

                # Get table of car specs
                specs = lstsoup.select('ul.listing-specifications')

                for li in specs[0].find_all('li'):
                    lititle = li.select('span.title')[0].text.strip().strip(':')
                    livalue = li.select('span.value')[0].text.strip().strip(':')

                    if livalue.lower() == 'not specified':
                        livalue = None

                    # Now a bunch of if-else statements to determine which column to add data to
                    # There might be a more sophisticated way to do this, perhaps with a tuple or a dictionary?
                    if lititle.lower() == 'year':
                        if livalue:
                            year = int(livalue)
                        else:
                            year = livalue
                    elif lititle.lower() == 'make':
                        make = livalue
                    elif lititle.lower() == 'model':
                        model = livalue
                    elif lititle.lower() == 'body':
                        body = livalue
                    elif lititle.lower() == 'mileage':
                        if livalue:
                            mileage = int(livalue.replace(',',''))
                        else:
                            mileage = livalue
                    elif lititle.lower() == 'title type':
                        title_type = livalue

                    # Below this are non-required specs    
                    elif lititle.lower() == 'trim':
                        trim = livalue
                    elif lititle.lower() == 'exterior color':
                        if livalue:
                            ext_color = livalue.lower()
                        else:
                            ext_color = livalue
                    elif lititle.lower() == 'interior color':
                        if livalue:
                            int_color = livalue.lower()
                        else:
                            int_color = livalue
                    elif lititle.lower() == 'transmission':
                        transmission = livalue
                    elif lititle.lower() == 'liters':
                        try:
                            liters = float(livalue)
                        except:
                            if livalue:
                                try:
                                    str1 = re.search('^(.*?)L',livalue).group(0).strip().replace(' ','')
                                    if re.search('^(\D+)',str1):
                                        idxend = re.search('^(\D+)',str1).end()
                                        livalue = str1[idxend:-1]
                                        if re.search('(\D+)',livalue): # check if still other pollutants
                                            idxend = re.search('(\D+)',livalue).end()
                                            livalue = livalue[idxend:]
                                    else:
                                        livalue = str1[:-1]
                                    try:
                                        livalue = float(livalue)
                                    except:
                                        # save to error log
                                        err_df = pd.DataFrame({'timestamp':[datetime.fromtimestamp(time.time())], 'link':[fulllink], 'liters_str':[livalue]})

                                        # Check to see if liters_error_log already exists
                                        if os.path.isfile('errors/liters_error_log.csv'):
                                            # print('found file. appending to existing file')
                                            err_df.to_csv('errors/liters_error_log.csv', mode='a', index=False, header=False)
                                            # print()
                                            # print('saved in inner try-except')
                                        else:
                                            # print('no file found. creating new file')
                                            err_df.to_csv('errors/liters_error_log.csv', index=False)
                                except:
                                    # save to error log
                                    err_df = pd.DataFrame({'timestamp':[datetime.fromtimestamp(time.time())], 'link':[fulllink], 'liters_str':[livalue]})
                                    
                                    # Check to see if liters_error_log already exists
                                    if os.path.isfile('errors/liters_error_log.csv'):
                                        # print('found file. appending to existing file')
                                        err_df.to_csv('errors/liters_error_log.csv', mode='a', index=False, header=False)
                                        # print()
                                        # print('saved in outer try-except')
                                    else:
                                        # print('no file found. creating new file')
                                        err_df.to_csv('errors/liters_error_log.csv', index=False)                                   
                                    
#                                     print('couldn't parse liters info')
                            else:
                                liters = livalue
                    elif lititle.lower() == 'cylinders':
                        if livalue:
                            cylinders = int(livalue)
                        else:
                            cylinders = livalue
                    elif lititle.lower() == 'fuel type':
                        fuel_type = livalue
                    elif lititle.lower() == 'number of doors':
                        if livalue:
                            n_doors = int(livalue)
                        else:
                            n_doors = livalue
                    elif lititle.lower() == 'exterior condition':
                        ext_condition = livalue
                    elif lititle.lower() == 'interior condition':
                        int_condition = livalue
                    elif lititle.lower() == 'drive type':
                        drive_type = livalue
                    elif (lititle.lower() == 'vin'):
                        VIN = livalue
                    elif (lititle.lower() == 'stock number') | (lititle.lower() == 'dealer license'):
                        None # Don't want to save these
                    else:
                        None
                        print(f'Unmatched param {lititle}: {livalue}') # <-- could take advantage of some or all of these

                curr_car = pd.DataFrame({"post_date":[postdate],
                                         "lastpull_ts":[int(time.time())],
                                         "link":[fulllink],
                                         "price":[price],
                                         "year":[year],
                                         "make":[make],
                                         "model":[model],
                                         "body":[body],
                                         "mileage":[mileage],
                                         "title_type":[title_type],
                                         "city":[city],
                                         "state":[state],
                                         "seller":[seller],
                                         "trim":[trim],
                                         "ext_color":[ext_color],
                                         "int_color":[int_color],
                                         "transmission":[transmission],
                                         "liters":[liters],
                                         "cylinders":[cylinders],
                                         "fuel_type":[fuel_type],
                                         "n_doors":[n_doors],
                                         "ext_condition":[ext_condition],
                                         "int_condition":[int_condition],
                                         "drive_type":[drive_type],
                                         "VIN":[VIN],
                                         "n_pics":[n_pics]})
                try:
                    all_cars = pd.concat([all_cars, curr_car])
                except:
                    all_cars = curr_car

                bar.update(idx)

    if type(all_cars) is pd.core.frame.DataFrame: # make sure that some data was actually scraped
        all_cars = all_cars.reset_index()
        del all_cars['index']
        all_cars.fillna(value=np.nan, inplace=True)
    if use_proxy:
        return all_cars, moreresults, currproxy, proxydict, use_proxy
    else:
        return all_cars, moreresults, use_proxy