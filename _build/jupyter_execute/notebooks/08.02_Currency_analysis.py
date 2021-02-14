#!/usr/bin/env python
# coding: utf-8

# # Currency Rate Analysis

# > Money often costs too much. --Ralph Waldo Emerson
# 
# A very used expression in our life, and if utilized just right, also very useful. 
# 
# In this notebook, we query a REST API to get the latest currency rates for many currencies. Using dynamic API compared to loading static files allows for updated data to be processed.

# ## Loading data using API
# 
# First of all, let's get our data.
# 
# In order to do so, let's start with installing all the needed libraries and get the right imports.

# In[1]:


pip install forex-python


# In[2]:


import pandas as pd
import numpy as np

from forex_python.converter import CurrencyRates
from datetime import datetime


# Let's get the data
# 
# In that case, the function here is given by the provider of this API, and for more methods, you can go to [forext-python usage page](https://forex-python.readthedocs.io/en/latest/usage.html)

# In[3]:


usd_rates = (
    CurrencyRates()
    .get_rates('USD')
)
usd_rates


# Let's turn it into something more readable and easier to manipulate, by converting its type from Dictionary to DataFrame, and give its columns proper informative names.

# In[4]:


usd_rates_df = (
    pd
    .DataFrame
    .from_dict(usd_rates, orient='index')
    .rename(columns={0 : 'Rate'})
)
usd_rates_df


# 

# This looks like a useful table to have if you work with multiple currencies in your organization
# 
# ### Getting rates for a specific date
# 
# We will use the date functionality from the API provider.
# * Call the currency API
# * Request exchange rates
# * for USD
# * for 2020-05-23

# In[5]:


usd_rate_on_date = (
   CurrencyRates()
    .get_rates(
        'USD',
        datetime(2020, 5, 23)
    )
)
usd_rate_on_date


# Now, try to use the functions showed prior in order to convert it into a dataframe.

# In[6]:


# Enter your code here


# And in case you wondered how to do so.

# In[7]:


usd_rate_on_date = (
    pd
    .DataFrame
    .from_dict(usd_rate_on_date, orient='index')
    .rename(columns={0 : 'Rate'})
)
usd_rate_on_date


# 

# ### Putting it all together
# 
# * Create a Dataframe
# * From dictionary
# * Taken from the currency rate API
# * for USD
# * based on string date of 2020-05-23
# * as a single column
# * rename the column to Rate 

# In[8]:


usd_rate_on_date = (
    pd
    .DataFrame
    .from_dict(
        CurrencyRates()
            .get_rates(
                'USD',
                datetime.strptime('2020-05-23', '%Y-%m-%d')
        ),
        orient='index')
    .rename(columns={0 : 'Rate'})
)
usd_rate_on_date


# ## Deal conversion
# 
# Now, let's create a calculator that get's the amount of money we got/payed and in which currency
# 
# * Call the API
# * For conversion rate
# * from USD
# * to EUR
# * of $100
# * on 2020-05-23 
# 
# 

# In[9]:


( 
    CurrencyRates()
    .convert(
            'USD',
            'EUR',
             100,
            datetime.strptime('2020-05-23', '%Y-%m-%d')
        )
)


# Now this data is useful while trying to calculate all sort of financial related data.

# ### Additional rates sources
# 
# And for cases when the wanted currency is not available through the API, there is always the option of scrapping it.
# 
# Here is example of scrapping ILS rate to USD from one of the popular financial websites in Israel.
# * Create dataframes from HTML tables in the newspaper currency website
# * Take the first table (index 0)
# * Take the value in cell 1,1

# In[10]:


(
    pd
    .read_html('https://www.globes.co.il/portal/instrument.aspx?instrumentid=10463')
    [0]
    .iloc[1,1]
)


# In this example we have scrapped the currency rate from a non-API based website for our use.<br>
# As for this example, this technique is relevent for many optional analysis.

# ## Analysis Use-case
# 
# Now, use case to show how useful descion based data regarding currency could be.
# 
# In order to show that, we will scrap a dataframe of the rates of the ILS-USD for the last almost full year.

# In[11]:


df = (
    pd
    .read_html('https://www.exchange-rates.org/history/ILS/USD/T')
    [0]
    .rename(columns = {0 : 'Date', 1: 'Day', 2 : 'Rate', 3 : 'Notes'})
    .assign(Rate = lambda x : x.Rate.str.replace('[^\d\.]','',regex=True).astype(float))
)
df


# Now let's check in which day of the week, does the rate of the ILS is "stronger", in accordance to the USD.<br>
# This data could be useful in order to maximize the rate when doing currency conversions on a regular basis.

# Now let's try to check for the days with the highest average rate of the ILS in comparing to the USD.
# 
# In order to do so, we will aggregate with Group-by, all of the values by the Day of the week, and check for the average (mean) value for each day.
# 
# Beside that, let's also orgnaize our data by some order, in order case descending.

# In[12]:


(
    df
    .groupby(['Day'])
    ['Rate']
    .mean()
    .sort_values(ascending=False)
)


# And the result is? Well, Sunday.<br>
# 
# Our guess is that its related to the fact that Sunday is weekend in the US and therefore, trade volumes are lower.
# 
# This, we assess, reduces the affect of the general trend.

# Another test, would be to do the same, but with the median value for each week day.

# In[13]:


(
    df
    .groupby(['Day'])
    ['Rate']
    .median()
    .sort_values(ascending=False)
)


# ### Analysis output
# 
# Bottom line, if you are converting ILS to USD, try doing it on Sunday. You will probably get the better rate. On the other hand, if you are trading USD to ILS, just don't do it on Sunday.
# 
# One more note, did you notice how we used and scrapped many types of websites, side by our API.
# 
# The reason? None of them was sufficient so we had to dig deeper. and thats OK.
# 
# So, one last tip from us to you, don't be afraid of looking for your data source.

# ## Data Visualization 
# 
# ### Line Chart
# 
# Now, let's try to better see and and possibly explorate, the results we just recieved.

# First, few actions needs to be done in prior.

# In[14]:


import matplotlib.pyplot as plt


# In[15]:


usd_to_ils_rates = (
    pd
    .read_html('https://www.exchange-rates.org/history/ILS/USD/T')
    [0]
    .rename(columns = {0 : 'Date', 1: 'Day', 2 : 'Rate', 3 : 'Notes'})
    .assign(Rate = lambda x : x.Rate.str.replace('[^\d\.]','',regex=True).astype(float))
    .assign(Date = lambda x : pd.to_datetime(x.Date))
    .set_index('Date')
)
usd_to_ils_rates


# In[16]:


(
    usd_to_ils_rates
    ['Rate']
    .plot(title='Exchange Rates: USD-ILS')
);


# ### Scatter Plot 
# 
# Now let's try something else, to demonstrate the differences between the days.

# In[17]:


(
    usd_to_ils_rates
    .plot
    .scatter(
        x='Day',
        y='Rate',
        c='Red',
        title='Exchange Rates: USD-ILS across the week days'
    )
);


# Something here looks odd. it appears there are less trading 'Sundays', which could be the reason for our former result.<br>
# Let's check it.

# In[18]:


(
    usd_to_ils_rates
    .groupby('Day')
    ['Rate']
    .count()
)


# Yep, totally true. therefore, let's check for the all the other days excluding Sunday.<br>
# Filtering the Dataframe to exclude Sundays.

# In[19]:


(
    usd_to_ils_rates
    .query('Day != "Sunday"')
    .plot
    .scatter(
        x='Day',
        y='Rate',
        c='Green',
        title='Exchange Rates: USD-ILS across the working days'
    )
);


# And based on the most lower points, we can now see that the lowest days occurs in the mid-of-the-week days.<br>

# ## Analyze Across Weeks using Groupby
# 
# Another cool way to possible be able to better identifiy the aforementioned trend, check the max & min weekly rate, and on which day did it happen.
# 
# First, let's set up our data in a way that will allow us to analyze it.

# And by a grouped table, which will show the day of each week which the highest, and later the lowest rate occured on.

# In[20]:


(
     usd_to_ils_rates
     .assign(Week = usd_to_ils_rates.index.week)
     .groupby(['Week'])
     ['Day', 'Rate']
     .max()
     .style
     .background_gradient(cmap='summer', subset=['Rate'])
)


# In[21]:


(
     usd_to_ils_rates
     .assign(Week = usd_to_ils_rates.index.week)
     .groupby(['Week'])
     ['Day', 'Rate']
     .min()
     .style
     .background_gradient(cmap='summer', subset=['Rate'])
)


# ### Analysis conclusion
# 
# And here is the answer for our question - which days are the best day to conduct a currency conversion between USD and ILS to maximize your profits: Wednsday for USD to ILS and Friday to ILS to USD

# In[ ]:




