from django.shortcuts import render
from django.template import RequestContext
from plotly.offline import plot, iplot
from plotly.graph_objs import Scatter
import matplotlib.pyplot as plt
import io
import base64
import plotly.express as px
import traceback

# Import User Defined Modules
from . import productscrapper as ps
from . import reviewanalysis as ra

# Create your views here.
from django.http import HttpResponse, JsonResponse

def index(request):
    #return HttpResponse("Hello, world. You're at the polls index.")
    response =  render(request, 'product_reviewer_app/index.html')
   
    response.set_cookie('searchProdPageNo', 0)
    response.set_cookie('prodName', '')
    # return render(request, 'product_review/index.html')
    return response

def SearchPage(request):
    # set cookie for traversing to different pages
    prodPageNo=1

    # get search box data
    searchVal = request.GET['query']
    print(searchVal)
    if 'searchProdPageNo' in request.COOKIES and  'prodName' in request.COOKIES:
        if request.COOKIES['prodName']!=searchVal:
            prodPageNo = 1
        else:
            prodPageNo=int(request.COOKIES['searchProdPageNo'])
   
    # call the scrapper module function to get the list of products
    #params = {'products': "https://m.media-amazon.com/images/I/71KxuRv3-fL._AC_UL320_.jpg", 'search':srh}
    params = {'product': searchVal, 'searchResult':ps.getProductIdAndImage(searchVal,prodPageNo)}
    #print(params)

    # set cookie for traversing to different pages

    response =  render(request, 'product_reviewer_app/search.html', params)
   
    response.set_cookie('searchProdPageNo', int(prodPageNo)+1)
    response.set_cookie('prodName', searchVal)
    print(int(prodPageNo)+1)
    # return render(request, 'product_review/search.html', params)
    return response

def reviewAnalysis(request):
    try:
        # get pId
        pId = request.GET['id']
        # plot_overall_wc_img,pie_div,timeSeries_div,plot_positive_wc_img,plot_positive_wc_img,positive_comment,negative_comment=ra.getReviewCharts(pId)
        pie_div,timeSeries_div,positive_comment,negative_comment,plot_positive_wc_img,plot_negative_wc_img = ra.getReviewCharts(pId)
        return render(request, 'product_reviewer_app/chart.html', context={'plot_div': timeSeries_div,'pie_div':pie_div,'positive_comment':positive_comment,'negative_comment':negative_comment,'plot_positive_wc_img':plot_positive_wc_img,'plot_negative_wc_img':plot_negative_wc_img })
    except Exception as e:
        print(e)
        return 'Error'

def DisplayChart(request):
    try:

        x_data = [0,1,2,3]
        y_data = [x**2 for x in x_data]

        # Plot graph using ploty dash
        df = px.data.iris()
        fig = px.scatter(df, x="sepal_width", y="sepal_length", color="species",
                        size='petal_length', hover_data=['petal_width'])
        plot_div = plot(fig,output_type='div',include_plotlyjs=False)

        # Pie chart using plotly dash

        # This dataframe has 244 lines, but 4 distinct values for `day`
        df = px.data.tips()
        fig = px.pie(df, values='tip', names='day')
        pie_div=plot(fig,output_type='div',include_plotlyjs=False)
    
        # # graph using matplot lib
    
        # buf = io.BytesIO()
        # _=plt.bar(x_data, y_data, color="#6c3376", linewidth=3)
        # ax = plt.subplot()
        # ax.set_ylim(0,10)
        # ax.set_xlim(0,5)
        # plt.title("Cost of Living", fontsize=18, fontweight='bold', color='blue')
        # plt.xlabel("Year", fontsize=16)
        # plt.ylabel("Number of futurestud.io Tutorials", fontsize=16)
        # plt.legend(["First","Second"])

        # plt.savefig(buf,format='png')
        # buf.seek(0)
        # buffer = b''.join(buf)
        # b2 = base64.b64encode(buffer)
        # plot_div=b2.decode('utf-8')

        # return render(request, "index.html", context={'plot_div': plot_div})
        return render(request, 'product_reviewer_app/chart.html', context={'plot_div': plot_div,'pie_div':pie_div})
    except Exception as e:
        print(traceback.format_exc())
