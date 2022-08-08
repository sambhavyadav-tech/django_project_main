from datetime import datetime
import re
from concurrent.futures import ThreadPoolExecutor,as_completed
from numpy.lib.function_base import piecewise
import requests
from bs4 import BeautifulSoup
import string
import nltk
from nltk.corpus import stopwords
from nltk import PorterStemmer
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import plotly.graph_objects as go
import pandas as pd
from plotly.offline import plot, iplot
from plotly.graph_objs import Scatter
import io
import base64
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
analyser = SentimentIntensityAnalyzer()

def Searchasin(asin):
    url="https://www.amazon.in/dp/"+asin
    # print(url)
    page=requests.get(url)#,cookies=cookie,headers=header)
    print(page.status_code)
    while page.status_code!=200:
        page=requests.get(url)
    return page

def Searchreviews(review_link):
    try:
        url="https://www.amazon.in"+review_link
        print(url)
        page=requests.get(url)#,cookies=cookie,headers=header)
        while page.status_code!=200:
            page=requests.get(url)
        return page
    except Exception as e:
        print('error',str(e),review_link)
        return 'error'

def getReviewsList(link,k):
    reviews=[]
    location=[]
    date=[]
    response=Searchreviews(link+'&pageNumber='+str(k))
    if str(type(response))!="<class 'str'>":
        soup=BeautifulSoup(response.content,'html.parser')
    else:
        return {'rev':reviews,'loc':location,'dat':date}    
    for enum,i in enumerate(soup.findAll("span",{'data-hook':"review-body"})):
        reviews.append(i.text)
        j=soup.findAll("span",attrs={'class':"a-size-base a-color-secondary review-date"})[enum]
        location.append(j.text.split()[2])
        date.append('-'.join(j.text.split()[4:]))
    return {'rev':reviews,'loc':location,'dat':date}

def deEmojify(inputString):
    return inputString.encode('ascii', 'ignore').decode('ascii') # A function to remove emojis from the reviews

def clean_text(text):
    # nltk.download("stopwords")
    STOPWORDS=stopwords.words("english") #stopwords are the most common unnecessary words. eg is, he, that, etc.
    ps=PorterStemmer()
   
    text=deEmojify(text) # remove emojis
    text_cleaned="".join([x for x in text if x not in string.punctuation]) # remove punctuation
   
    text_cleaned=re.sub(' +', ' ', text_cleaned) # remove extra white spaces
    text_cleaned=text_cleaned.lower() # converting to lowercase
    tokens=text_cleaned.split(" ")
    tokens=[token for token in tokens if token not in STOPWORDS] # Taking only those words which are not stopwords
    text_cleaned=" ".join([ps.stem(token) for token in tokens])
    return text_cleaned

def sentiment_analyzer_scores(sentence):
    score = analyser.polarity_scores(sentence)
    return score

def compound_score(text):
    comp=sentiment_analyzer_scores(text)
    return comp['compound'] # returns the compound score from the dictionary

def sentiment_category(score):
    if score >= 0.05:
        return "positive"
    elif score <= -0.05:
        return "negative"
    else:
        return "neutral"

def getAsinData(pId):
    response=Searchasin(pId)
    return response

def reviewPie(df):
    labels = ['Positive','Negative','Neutral']
    values = [df[df['review_category'] == 'positive']['review_category'].count(),
            df[df['review_category'] == 'negative']['review_category'].count(),
            df[df['review_category'] == 'neutral']['review_category'].count()]
    colors = ['green', 'red', 'yellow']
    # pull is given as a fraction of the pie radius
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, pull=[0.1, 0.1, 0.3])])
    fig.update_traces(hoverinfo='label+percent', textinfo='label+percent', textfont_size=15,
                    marker=dict(colors=colors, line=dict(color='#000000', width=1)))
    fig.update_layout(
        autosize=False,
        width=590,
        # height=500,
        margin=dict(
            l=50,
            r=50,
            b=0,
            t=30
        ),
        paper_bgcolor="white"
    )

    fig.update_layout(
        legend=dict(
            x=0.9,
            y=1,
            orientation="v",
            title_font_family="Times New Roman",
            font=dict(
                family="Roman",
                size=15,
                color="black"
            ),
            bgcolor="LightSteelBlue",
            bordercolor="white",
            borderwidth=1
        )
    )
    # fig.show()
    pie_div=plot(fig,output_type='div',include_plotlyjs=False)
    return {"pie_div":pie_div}
   
def timeSeriesGraph(lineDf):
    fig = go.Figure()

    # Add traces
    fig.add_trace(go.Scatter(x=lineDf.date, y=lineDf.review_count,
                        mode='lines',
                        name='time series',
                        marker_color='green'))

    # fig.add_trace(go.Scatter(x=lineDf['date'],
    #                 y=lineDf['review_count'],
    #                 name='count on date',mode='markers',marker_size=5,marker_color='black'
    #                 ))

    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        )
    )

    fig.update_layout(
        title='Customer Reviews Count Everyday',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            title='Date',
            titlefont_size=16,
            tickfont_size=10,
        ),
        yaxis=dict(
            title='Review Count Per Day',
            titlefont_size=16,
            tickfont_size=10,
        ))
    fig.update_layout(
        legend=dict(
            x=0.9,
            y=1,
            orientation="v",
            title_font_family="Times New Roman",
            font=dict(
                family="Roman",
                size=10,
                color="black"
            ),
            bgcolor="lightgreen",
            bordercolor="black",
            borderwidth=1
        )
    )

    # fig.show()
    timeSeries_div=plot(fig,output_type='div',include_plotlyjs=False)
    return {'timeSeries_div':timeSeries_div}

def positiveWc(df):
    wordcloud = WordCloud(height=2000, width=2000, background_color='yellow')
    wordcloud = wordcloud.generate(' '.join(df.loc[df['review_category']=='positive','cleaned_reviews'].tolist()[:10]))
    plt.imshow(wordcloud)
    plt.title("Most common words in positive comments")
    plt.axis('off')
    buf = io.BytesIO()
    plt.savefig(buf,format='png')
    buf.seek(0)
    buffer = b''.join(buf)
    b2 = base64.b64encode(buffer)
    plot_positive_wc_img=b2.decode('utf-8')
    return {'posWc':plot_positive_wc_img}

def negativeWc(df):
    wordcloud = WordCloud(height=2000, width=2000, background_color='red')
    wordcloud = wordcloud.generate(' '.join(df.loc[df['review_category']=='negative','cleaned_reviews'].tolist()[:10]))
    plt.imshow(wordcloud)
    plt.title("Most common words in negative comments")
    plt.axis('off')
    buf = io.BytesIO()
    plt.savefig(buf,format='png')
    buf.seek(0)
    buffer = b''.join(buf)
    b2 = base64.b64encode(buffer)
    plot_negative_wc_img=b2.decode('utf-8')
    return {'negWc':plot_negative_wc_img}

def getReviewCharts(pId):
    print("getReviewCharts", datetime.now())
    # # response=Searchasin(pId)
    # link=''
    # response=None
    # # Get Asin Data for the product id
    # # while str(type(response))!="<class 'str'>":
    # #     response=getAsinData(pId)
    # response=Searchasin(pId)
    # print(response,type(response))
    # soup=BeautifulSoup(response.content,'html.parser')
    # link=soup.findAll("a",attrs={'data-hook':"see-all-reviews-link-foot"})[0]['href']
    # print(link)

    # # Get Reviews
    # reviews=[] # Store review data
    # location=[] # Store location data
    # date=[] # Store date data
    # # Get the no of pages for review
    # tasks=[]
    # executor=ThreadPoolExecutor(max_workers=100)

    # for k in range(10):# Number of pages
    #     tasks.append(executor.submit(getReviewsList,link,k))

    # for task in as_completed(tasks):
    #     revDict=task.result()
    #     reviews+=revDict['rev']
    #     location+=revDict['loc']
    #     date+=revDict['dat']

    # print('reviews Collected-----------------')
    # revData={'reviews':reviews,'country':location,'date':date} #converting the reviews list into a dictionary
    # review_data=pd.DataFrame.from_dict(revData) #converting this dictionary into a dataframe
    # # Store review into csv file
    # review_data.to_csv(r'D:\Django-Webapp\Django_Product_Reviewer\Product_Reviewer\product_review_app\scrapped_reviews\/'+str(pId)+'_reviews.csv',index=False)

    # df=review_data.copy() # Creating a copy of the original data
    # df['reviews']=df['reviews'].apply(lambda x:x.strip('\n')) # To remove '\n' from every review
    # df['cleaned_reviews']=df['reviews'].apply(lambda x:clean_text(x))

    # df['sentiment_score']=df['reviews'].apply(lambda x:compound_score(x)) # applying on the reviews column to get the score

    # df['review_category']=df['sentiment_score'].apply(lambda x:sentiment_category(x))

    # Read data from scrapped reviews csv file
    df=pd.read_csv(r'C:\Users\sambhav\OneDrive\Desktop\Django_Projects\Django_Projects\product_reviewer_app\scrapped_reviews\/'+str(pId)+'_reviews.csv')
    wcTasks=[]
    wcExecutor=ThreadPoolExecutor(max_workers=4)
    wcTasks.append(wcExecutor.submit(positiveWc,df))
    wcTasks.append(wcExecutor.submit(negativeWc,df))
   
    df.sort_values(by=['sentiment_score'],ascending=False).head() # To get top positive review

    positive_comment=list(df.sort_values(by=['sentiment_score'],ascending=False)[:1]['reviews'])[0]
    negative_comment=list(df.sort_values(by=['sentiment_score'],ascending=True)[:1]['reviews'])[0]

    pie_div=reviewPie(df)
    wcTasks.append(wcExecutor.submit(reviewPie,df))

    # Review count per day
    df.groupby(['date']).size()
    reviewCountDf=df.groupby(['date']).size()
    reviewCountDf=reviewCountDf.rename('review_count').reset_index()
    reviewCountDf['date'] = pd.to_datetime(reviewCountDf['date'])
    reviewCountDf=reviewCountDf.sort_values('date')

    timeSeries_div = timeSeriesGraph(reviewCountDf)
    wcTasks.append(wcExecutor.submit(timeSeriesGraph,reviewCountDf))
    print("task appended", datetime.now())
    wcResult={}
    for task in as_completed(wcTasks):
        wcResult=task.result()
        print(wcResult.keys())
        if 'posWc' in wcResult.keys():
            plot_positive_wc_img=wcResult['posWc']
        elif 'negWc' in wcResult.keys():
            plot_negative_wc_img=wcResult['negWc']
        elif 'pie_div' in wcResult.keys():
            pie_div=wcResult['pie_div']
        elif 'timeSeries_div' in wcResult.keys():
            timeSeries_div=wcResult['timeSeries_div']
    print("getReviewCharts completed ",datetime.now())
    return pie_div,timeSeries_div,positive_comment,negative_comment,plot_positive_wc_img,plot_negative_wc_img

def saveReviews(pId):
    print(datetime.now())
    # response=Searchasin(pId)
    link=''
    response=None
    # Get Asin Data for the product id
    # while str(type(response))!="<class 'str'>":
    #     response=getAsinData(pId)
    response=Searchasin(pId)
    print(response,type(response))
    soup=BeautifulSoup(response.content,'html.parser')
    link=soup.findAll("a",attrs={'data-hook':"see-all-reviews-link-foot"})[0]['href']
    print(link)

    # Get Reviews
    reviews=[] # Store review data
    location=[] # Store location data
    date=[] # Store date data
    # Get the no of pages for review
    tasks=[]
    executor=ThreadPoolExecutor(max_workers=100)

    for k in range(5):# Number of pages
        tasks.append(executor.submit(getReviewsList,link,k))

    for task in as_completed(tasks):
        revDict=task.result()
        reviews+=revDict['rev']
        location+=revDict['loc']
        date+=revDict['dat']

    print('reviews Collected-----------------')
    revData={'reviews':reviews,'country':location,'date':date} #converting the reviews list into a dictionary
    review_data=pd.DataFrame.from_dict(revData) #converting this dictionary into a dataframe
    # print(review_data.head())
    df=review_data.copy() # Creating a copy of the original data
    print("copied Dataframe")
    
    df['reviews']=df['reviews'].apply(lambda x:x.strip('\n')) # To remove '\n' from every review
    df['cleaned_reviews']=df['reviews'].apply(lambda x:clean_text(x))

    df['sentiment_score']=df['reviews'].apply(lambda x:compound_score(x)) # applying on the reviews column to get the score

    df['review_category']=df['sentiment_score'].apply(lambda x:sentiment_category(x))
    # print(df.head())
    # Store review into csv file
    df.to_csv(r'C:\Users\sambhav\OneDrive\Desktop\Django_Projects\Django_Projects\product_reviewer_app\scrapped_reviews\/'+str(pId)+'_reviews.csv',index=False)
    print('reviews saved for pid', pId)