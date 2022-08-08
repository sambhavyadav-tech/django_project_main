import re
import requests
import traceback
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

# Import user defined files
from . import reviewanalysis as ra

def getAmazonSearch(search_query):
    url="https://www.amazon.in/s?k="+search_query
    print(url)
    page=requests.get(url)#,cookies=cookie,headers=header)
    while page.status_code!=200:
        page=requests.get(url)
    return page

def getProductIdAndImage(searchVal, prodPageNo):
    try:

        data_asin=[]
        #response=getAmazonSearch('titan+men+watches')
        if int(prodPageNo) not in [0,1]:
            response=getAmazonSearch(searchVal+"&page="+str(prodPageNo))
        else:
            response=getAmazonSearch(searchVal)
        print(response)
        #res=response.content
        #print(type(res))
        #str(res)
        soup=BeautifulSoup(response.content,'html.parser')
        #print(soup)
        filterKeyList=['s-result-item s-asin sg-col-0-of-12 sg-col-16-of-20 sg-col s-widget-spacing-small sg-col-12-of-16','s-result-item s-asin sg-col-0-of-12 sg-col-16-of-20 sg-col sg-col-12-of-16','sg-col-4-of-12 s-result-item s-asin sg-col-4-of-16 sg-col sg-col-4-of-20']
        filterKey=""
        for filter in filterKeyList:
            if len(soup.find_all("div",attrs={"class":filter}))>1:
                filterKey = filter
        tasks=[]
        executor=ThreadPoolExecutor(max_workers=1024)

        for i in soup.find_all("div",attrs={"class":filterKey}):
            # print(i)
            # print(i['data-asin'])
            # print(re.findall('alt="(.+.jpg)" ',str(i))[0].split('" ')[0])
            # print(re.findall('alt="(.+.jpg)" ',str(i))[0].split('" ')[-1].strip('src="'))
            if re.findall('class="a-icon-alt">(.+ stars)',str(i)):
                pRatings =  re.findall('class="a-icon-alt">(.+ stars)',str(i))[0]
            else :
                pRatings = "NA"

            if re.findall('class="a-offscreen">₹(.+)',str(i)):
                pPrice = "₹"+re.findall('class="a-offscreen">₹(.+)',str(i))[0].split('<')[0]
            else : 
                pPrice = "NA"
            data_asin.append({

                "pName" : re.findall('alt="(.+.jpg)" ',str(i))[0].split('" ')[0],
                "pId" : i['data-asin'],
                'pImage' : re.findall('alt="(.+.jpg)" ',str(i))[0].split('" ')[-1].strip('src="'),
                'pRatings' : pRatings,
                "pPrice" : pPrice
            })
            tasks.append(executor.submit(ra.saveReviews,i['data-asin']))

        return data_asin
    except Exception as e:
        print('Error occurred due to'+str(e))
        print(str(traceback.format_exc()))
        return data_asin
