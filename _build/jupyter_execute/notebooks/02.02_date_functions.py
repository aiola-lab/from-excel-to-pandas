#!/usr/bin/env python
# coding: utf-8

# # Date Functions
# 
# In the previous section we created an advanced analysis with _merge_ and _groupby_ and other Pandas capabilities, which are harder to do in Excel. In this section, we will check the more traditional functions that are often used in Excel spreadsheet and we will see how to use them easily in Pandas.

# ## Date Functions
# 
# Let's review some common functions in Excel and their replacement in Pandas
# 
# ### TODAY
# 
# `=TODAY()`
# 
# Like many of the Pandas functions, most of the arguments are optional and the default values are often as expected. For example, the time stamp and even the date depends on the timezone needed. In the next example, we will specific the optional tz value to _'America/Chicago'_:

# You can see that the data includes columns such as _Seasons_ or _Functioning Day_, however, we might want to calculate such columns differently.

# In[1]:


import pandas as pd


# In[2]:


now = (
    pd
    .Timestamp
    .today(
        tz='America/Chicago'
    )
)
now


# ### DAY, MONTH, YEAR
# 
# We can apply all the various date functions from excel such as _DAY_, _MINUTE_, _HOUR_ etc.

# In[3]:


now.day, now.month, now.year


# ### DATE
# 
# we can create a date with given values such as day, month, and year
# 
# `=Date(2021,1,1)`
# 
# and in pandas:

# In[4]:


new_year = (
    pd
    .Timestamp(
        year=2021,
        month=1,
        day=1
    )
)
new_year


# ### NETWORKDAYS
# 
# A common function in business context is `=NETWORKDAYS()`, that calculates the number of working days between two dates. In Pandas we can use the following:

# In[5]:


import numpy as np 

(
    np
    .busday_count(
        new_year.date(), 
        now.date()
    )
)


# ### WORKDAY
# 
# The next useful function is `=WORKDAY(NUMBER)` that can be used when you want to get the date after a given number of working days

# In[6]:


new_year = pd.Timestamp("2021-01-01")
new_year.day_name()


# In[7]:


workday_100 = new_year + 100 * pd.offsets.BusinessDay()
workday_100


# The one hundred working day in 2021 is May 21st. 
# 
# Pandas has a wide range of options for date offsets, such as weeks, month-end, semi-month-end (15th day), querter, retail year (aka 52-53 week), and many [others](https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#dateoffset-objects).

# ## Real life example
# 
# ### Loading Data
# 
# As usual, let's load a dataset to work on. We will take another dataset that is used in machine learning education, "Bike Share". This is a data set about the demand of bike share service in Seoul. Please note that we need to modify the default encoding of _read_csv_ from 'UTF-8' to 'latin1'.

# In[8]:


bike_share_data = (
    pd
    .read_csv(
        'https://archive.ics.uci.edu/ml/machine-learning-databases/00560/SeoulBikeData.csv', 
        encoding='latin1'
    )
)
bike_share_data


# ### Date Columns Manipulations
# 
# We will start with creating a few columns based on the date column, such as day of the week and month. 
# * Start with the table we loaded above
# * Make sure that the Date column is in datetime format that we see (note the day before the month)
# * Calculate the day-of-week (DOW) of each row (to use the built-in functions we need to access the date accessor (_.dt_))
# * Calculate the month value of each row

# In[9]:


enriched_bike_share_data = (
    bike_share_data
    .assign(Date = pd.to_datetime(bike_share_data.Date, format='%d/%m/%Y', errors='coerce'))
    .assign(DOW = lambda x : x.Date.dt.day_name())
    .assign(month = lambda x : x.Date.dt.month)
)
enriched_bike_share_data


# ### Simple Data Visulizations
# 
# * Start with the enriched table above
# * Group the data by date column
# * Calculate the mean of values per each day
# * Plot the results with date as x and number of rented bike as y

# In[10]:


(
    enriched_bike_share_data
    .groupby('Date')
    .mean()
    .plot(y='Rented Bike Count')
);


# * Start with the enriched table above
# * Group the data by date column
# * Calculate the mean of values per each day
# * Plot the results 
# * with scatter plot with temp as x and number of rented bike as y

# In[11]:


(
    enriched_bike_share_data
    .groupby('Date')
    .mean()
    .plot
    .scatter(x='Temperature(°C)', y='Rented Bike Count')
);


# ### Analyzing Corrlations between the columns
# 
# * Start with the enriched table above
# * Group the data by date column
# * Calculate the mean of values per each day
# * Calculate the correlation values between the numeric values
# * Take the values that are related to the first column (_Rented Bike Count_), skip the first two rows (self correlation, and hour column)
# * Add style to the output
# * Highlight the maximum correlation value with green background
# * and Highlight the minimum correlation value with red background

# In[12]:


(
    enriched_bike_share_data
    .groupby('Date')
    .mean()
    .corr()
    .iloc[2:,[0]]
    .style
    .highlight_max(color='green')
    .highlight_min(color='red')
)


# We can see that the higher correlation is with the temperature (the higher the temperature, the more bikes are rented), and with the Snowfall (the more snowfall, the fewer bikes are reneted), which make sense. 

# In[ ]:




