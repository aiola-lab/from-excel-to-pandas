#!/usr/bin/env python
# coding: utf-8

# # Reading Data from External API
# 
# Often you want to add external data to your analysis. External data can be retrieved from API (Application Programable Interface) that is provided by various services such as CRM (Customer Relationship Management) systems. You can import HTML directly into Excel using _"Import"_.
# 
# In this notebook, we will learn how to use pandas _from_dict_ to load data from these external API

# ## Loading API data
# 
# We will load a few tables from simple API as well as complex ones

# In[1]:


import warnings
warnings.filterwarnings('ignore')


# In[2]:


import pandas as pd
import numpy as np


# ## Loading from simple API
# 
# If you have a simple API with no authentication, you can pass the URL of the requests library that we used in our previous toturial for loading HTML
# 
# For this excercise we will use the API of the Wikipedia page views. We will use it to test the idea that people who are thinking to buy stocks, are going to the wikipedia page of that stock, and therefore, if we see an increase in the views of a page, we will see an increase in the price of that share. 
# 
# We will check the format of the API call from the [technical page](https://www.mediawiki.org/wiki/API:Tutorial). We see the we need to plug the name of stock ticker, and we will use the f-string syntax that is replacing the {page} (or any other variable in curly brackets) with the value of the variable (for example, _AMZN_).

# In[3]:


page = 'AMZN'

page_views_api_url = f'https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/all-agents/{page}/daily/2020030100/2020033000'

import requests
response = requests.get(page_views_api_url)
response


# We can use two methods to extract the data that we want from the JSON format. The first is using _json_normalize_ and the second is using _from_dict_

# In[4]:


df = (
    pd
    .json_normalize(
        response.json(), 
        'items'
        )
)
df.head(5)


# In[31]:


page_view_data = (
    requests
    .get(page_views_api_url)
    .json()['items']
)
page_views_table = (
    pd
    .DataFrame
    .from_dict(page_view_data)
)
page_views_table.head(5)


# ## Simple Data Visualization
# 
# * Start with the page view table from the previous API call
# * Convert the timestamp column to date time format using the _%Y%m%d%H_ format
# * Extract the day of the month from the above timestamp
# * Plot the results
# * as bar chart with the day of the month as x and the number of views as y 
# * and title the graph as 'Page views for ...' with the name of the page
# 
# 

# In[32]:


(
    page_views_table
    .assign(timestamp = lambda x: pd.to_datetime(x.timestamp, format='%Y%m%d%H', errors='coerce'))
    .assign(day = lambda x: x.timestamp.dt.day)
    .plot
    .bar(
        x='day', y='views',
        title=f'Page views for {page}'
    )
);


# ## Loading the page views of all NASDAQ 100
# 
# We saw in the previous section how to load the values of a table from Wikipeia (or other HTML pages). Let's use it now to load all the NASDAQ 100 index companies to compare their page views.

# In[33]:


nasdaq_100_wikipedia_entry = 'https://en.wikipedia.org/wiki/NASDAQ-100'
nasdaq_100_tickers = (
    pd
    .read_html(
        nasdaq_100_wikipedia_entry, 
        match='Ticker'
    )
)


# In[34]:


nasdaq_100_tickers[0]


# Now we want to get all the views of each company on our list. We will define a simple function that will get the name of the company and return the views of this company's page.
# * Generate the URL of the wikipedia page view using the name of the company
# * Load the API response from above URL
# * Parse the JSON format of the response using the key 'items'
# * Return the newly create dataframe or an empty data frame if failed

# In[35]:


def get_views(company):
    company_page_url = f'https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/all-agents/{company.iat[0,0]}/daily/2020090100/2020093000'
    response = requests.get(company_page_url)
    try:
        df = (
            pd
            .json_normalize(
                response.json(), 
                'items'
            )
        )
    except:
        df = pd.DataFrame()
    
    return df


# Now we can apply the function above on each of the row from the nasdaq 100 tickets list:
# * Start with the first table from the nasdaq 100 list above
# * Group the ticker by the company name (in case we have multiple ticker to a company)
# * Apply the get view function on each of the company names and concat all the data frames together

# In[36]:


nasdaq_100_views = (
    nasdaq_100_tickers[0]
    # .head(2)
    .groupby('Company')[['Company']]
    .apply(get_views)
)


# In[37]:


nasdaq_100_views


# We see that we have more than 2000 rows in the concatenated dataframe where each line is a view of a company in a specific day in the range of September 2020.
# 
# Let's look on one of the companies (for example, _Lululemon Atheletica_)

# In[38]:


nasdaq_100_views.loc['Lululemon Athletica']


# * Start with the page view table of all the nasdaq 100
# * Filter to include only the _Lululemon Athletica_ views
# * Convert the timestamp column to date time format using the _%Y%m%d%H_ format
# * Extract the day of the month from the above timestamp
# * Plot the results
# * as bar chart with the day of the month as x and the number of views as y 
# * and title the graph as 'Page views for ...' with the name of the focused company

# In[39]:


focused_company = 'Lululemon Athletica'
(
    nasdaq_100_views
    .loc[focused_company]
    .assign(timestamp=lambda x: pd.to_datetime(x.timestamp, format='%Y%m%d%H', errors='coerce'))
    .assign(day = lambda x: x.timestamp.dt.day)
    .plot
    .bar(
        x='day', y='views',
        title=f'Page views for {focused_company}'
    )
);


# ## Loading from complex API
# 
# Many times API are more complex, nevertheless, we can still extract the relevant data. 

# Let's get some stock data from [alphavantage.co](https://www.alphavantage.co)
# 
# This web service is providing useful investment information using an API, however, like many other API providers, it requires an API key to identify the request (and sometimes chanrge for it).
# 
# To allow secure execution of such API call, we will how to install a new python module and how to use it. The next cell is installing the module from [ipython secrets](https://ipython-secrets.readthedocs.io/en/latest/)

# In[40]:


pip install ipython-secrets


# Once we have the module to handle secrets installed, we can import it to the notebook and use it. The module will pop up the request for the user to enter the API key, which you can get from [alphavantage.co](https://www.alphavantage.co/support/#api-key). Next time you will execute the cell and the whole notebook, the API key will be retrieved from the keyring of the machine running the notebook.

# In[41]:


from ipython_secrets import *

ALPHAVANTAGE_API_KEY = get_secret('ALPHAVANTAGE_API_KEY')


# From the [API documentation](https://www.alphavantage.co/documentation/) we can learn how to extract time-series stock information of a specific symbol. Let's use Amazon (AMZN) for example. 

# In[42]:


symbol = 'AMZN'

request_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=1min&apikey={ALPHAVANTAGE_API_KEY}'


# In[43]:


df = (
    pd
    .read_json(request_url)
)


# In[44]:


df


# ## Extracting the relevant data
# 
# We see that the data that we are looking for (open, close, high and low prices and volume in each minute) is available in a column of the dataframe table. We will filter the table to include only the rows with the prices data and split it to separated columns.

# * Start with the dataframe table that was returned from the API call
# * Rename the long 'Time Series...' column name to short 'ts'
# * Filter out all the rows where 'ts' column has no value (_null_)
# * Take only the 'ts' column for all the row left
# * Parse each value in the column as a series of key-value pairs and create a column for each pair

# In[45]:


json_series = (
    df
    .rename(columns={'Time Series (1min)':'ts'})
    .query('ts.notnull()')
    .loc[:,'ts']
    .apply(pd.Series)
)


# In[46]:


json_series


# ## Quick Visualization
# 
# Now that we have the prices from the API we can plot them. 
# * Start with the parsed data table above
# * Convert the values to numeric form (_astype('float')_) 
# * Slice the table to include only the _high_ and _low_ values (_iloc_) 
# * Reverse the order of the time-series to be from oldest to newest (_iloc[::-1]_)
# * Plot the data
# * with the title of the ticker 
# * and with 45° rotation. 

# In[47]:


(
    json_series
    .astype('float')
    .loc[:,('2. high','3. low')]
    .iloc[::-1]
    .plot(
        title=symbol, 
        rot=45
    )
);


# In[ ]:




