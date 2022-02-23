from django.shortcuts import render
from yahooquery import Ticker
import numpy as np
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from datetime import datetime
from datetime import timedelta
from fbprophet import Prophet
import fbprophet
from fbprophet.plot import plot
import matplotlib.pyplot as plt
from io import StringIO




# Create your views here.

def index(request):
    # View code here...
    return render(request, 'index.html')

def user_input(request):
    
    try:
        
        # Get the user input
        x = str(request.GET["x"])
        
        # It's absurd to define three tickers instead of one.
        # This is only for debugging purposes.

        # Long-Term Trend Analysis
        tickers = Ticker(x, asynchronous=True)
        df = tickers.history(period='10y', interval='1mo')['close'].tolist()
        perc_Change10 = ((df[len(df) - 1] - df[0]) / df[0]) * 100
        mean = np.nanmean(df)

        if perc_Change10 > 0:
            word = "up"
        else:
            word = "down"

        # Mid-Term Trend Analysis
        tickers5 = Ticker(x, asynchronous=True)
        df5 = tickers5.history(period='5y', interval='1mo')['close'].tolist()
        perc_Change5 = ((df5[len(df5) - 1] - df5[0]) / df5[0]) * 100
        mean5 = np.nanmean(df5)
  
        if perc_Change5 > 0:
            word5 = "up"
        else:
            ord5 = "down"

        # Short-Term Trend Analysis
        tickers1 = Ticker(x, asynchronous=True)
        df1 = tickers1.history(period='1y', interval='1d')['close'].tolist()
        perc_Change1 = ((df1[len(df1) - 1] - df1[0]) / df1[0]) * 100
        mean1 = np.nanmean(df1)
 
        if perc_Change1 > 0:
            word1 = "up"
        else:
            word1 = "down"  
                   
        # Calculate change in ROA year-to-year
        aapl = Ticker(x)
        y = aapl.balance_sheet()['TotalAssets'].tolist()
        y.reverse()

        aapl1 = Ticker(x)
        xx = aapl1.cash_flow(trailing=False)['NetIncome'].tolist()
        xx.reverse()

        roa_POST = (xx[0] / y[0])
        roa_PRE = (xx[1] / y[1])
        roa_Change = str(roa_POST - roa_PRE)
        goog = Ticker(x)
        y1 =  goog.balance_sheet()['CurrentAssets'].tolist()
        y1.reverse()
        
        googl1 = Ticker(x)
        x1 = googl1.balance_sheet()['CurrentLiabilities'].tolist()
        x1.reverse()
        currentRatio = (y1[0] / x1[0])  - (y1[1] / x1[1]) 
        
        
        def return_graph():

            tickers = Ticker(x, asynchronous=True)
            df = tickers.history(period='10y', interval='1d')
            model = Prophet(interval_width=0.95, daily_seasonality=True)
            df = df.reset_index()
            df[['ds', 'y']] = df[['date', 'close']]
            df = df.reset_index()
            model.fit(df)
            future = model.make_future_dataframe(periods = 365, freq='D')
            forecast = model.predict(future)
            fig1 = model.plot(forecast)
            plot(model, forecast, figsize=(7, 7))
            
            imgdata = StringIO()
            fig1.savefig(imgdata, format='svg')
            imgdata.seek(0)
            data = imgdata.getvalue()
            return data
 
        
        
        

    # return context
        context = {
                'long': "Over the past 10 years, "+ x+ " " + "has gone " + str(word)+ " " +  str(int(perc_Change10))+"%." +"\n" + " $100 invested then would fetch " + "$"+str(int(100 * perc_Change10))+". "+"The monthly stock return was " + "$"+str(int(mean)),
                'mid': "Over the past 5 years, "+ x+ " " + "has gone " + str(word5)+ " " +  str(int(perc_Change5))+"%" +"." + " $100 invested then would fetch " + "$"+str(int(100 * perc_Change5))+". "+"The monthly stock return was " + "$"+str(int(mean5)),
                'short': "Over the past year, "+ x+ " " + "has gone " + str(word1)+ " " +  str(int(perc_Change1))+"%" +"." + " $100 invested then would fetch " + "$"+str(int(100 * perc_Change1))+". "+"The monthly stock return was " + "$"+str(int(mean1)),
                'ROA': "ROA: "+ roa_Change[0:4]+"" + "\n" + "ROA measures how much money a company earns by putting its assets to use. A positive ROA indicates the company is doing a good job of increasing its profits",
                'Net': "Net income: " + str(round(xx[0])) + "\n Net income is the money a company makes, minus the money it spends. If net income is positive, the company has a higher probability of paying dividends to shareholders",
                'ratio': "Current ratio: " + str(currentRatio) + "\n A company with a current ratio of between 1.2 and 2 is typically considered good. The higher the current ratio, the more liquid a company is. However, if the current ratio is too high (i.e. above 2), it might be that the company is unable to use its current assets efficiently.",
                'graph': return_graph(),
       
        }

        return render(request, 'result.html' , context)
    
    # For debugging purposes 
    
    except UnboundLocalError:
        return JsonResponse({'message':"Bad Value",'explanation':"This error is used for debugging purposes.", 'comments':"Redirect URL"}, status=409)
    except KeyError:
        return JsonResponse({'message':"Bad Value",'explanation':"This error is used for debugging purposes.", 'comments':"Redirect URL"}, status=409)
        
    
        


        
