#!/usr/bin/env python
# coding: utf-8

# # Categories from numeric values
# 
# We often have a column with many numeric values and we want to group them to bins or buckets, such as age groups or value tiers. In Excel we can do it using: 
# 
# - Data Menu -> Data Analysis -> Histogram or Rank and Percentile
# - _VLOOKUP_ (`=LOOKUP(A1,{0,7,14,31,90,180,360},{"0-6","7-13","14-30","31-89","90-179","180-359",">360"})`, for example), or 
# - _IF_ (`=if(b2>30,"large",if(A1>20,"medium",if(A1>=10,"small",if(A1<10,"tiny",""))))`, for example)
# - _INDEX_ (`=INDEX({"Small","Medium","Large"},LARGE(IF(A1>{0,11,21},{1,2,3}),1))`, for example)
# 

# ## Cut Function
# 
# Since this is a common need, Pandas has a built-in function that makes it more flexible and accurate.

# In[1]:


import pandas as pd


# ## Real life example
# 
# ### Loading Data
# 
# As usual, let's load a dataset to work on. We will use the dataset that is used before, "Bike Share". This is a data set about the demand of bike share service in Seoul. Please note that we need to modify the default encoding of _read_csv_ from 'UTF-8' to 'latin1'.

# In[2]:


bike_share_data = (
    pd
    .read_csv(
        'https://archive.ics.uci.edu/ml/machine-learning-databases/00560/SeoulBikeData.csv', 
        encoding='latin1'
    )
)
bike_share_data


# ### Simple Data Visulizations
# 
# * Start with the table above
# * Create Histograms for numeric columns
# * Plot the histograms

# In[3]:


(
    bike_share_data
    [['Rented Bike Count']]
    .plot(
        kind='hist', 
        alpha=0.5, 
        title='Rented Bike Count'
    )
);


# In[4]:


(
    bike_share_data
    [['Temperature(°C)']]
    .plot(
        kind='hist', 
        alpha=0.5, 
        title='Temperature(°C)'
    )
);


# ### Creating bins with _Cut_
# 
# * Start with the table above
# * Focus on the temperature column
# * Create 5 bins

# In[5]:


(
    pd
    .cut(
        bike_share_data
        ['Temperature(°C)'], 
        5
    )  
)


# We see the interval fo each of the bins:
# `[(-17.857, -6.36] < (-6.36, 5.08] < (5.08, 16.52] < (16.52, 27.96] < (27.96, 39.4]]` that are in order and split to more or less equal sizes from temperature values perspective. Let's see how well they split the data:
# 
# * Split the temperature value into 5 bins
# * Count the number of records in each bins
# * Sort the value by the temperature range (the index of the series)
# 

# In[6]:


(
    pd
    .cut(
        bike_share_data
        ['Temperature(°C)'], 
        5
    )
    .value_counts()
    .sort_index()
)


# First, we see that the bins are in order when we sort them, and not by alphabetic order. More importanty, we see that they are not equal in size of records, and not based on any other meaningful split.
# 
# ### Setting the bins' limits
# 
# We can set the bing to be more meaningful by setting the limits specifically. As experts in bicycles, we know the temperature ranges that are suitable for different accessories and clothings. Let's fix the ranges based on this domain knowledge:
# 
# * Split the temperature value into 5 bins based on bicycle professional ranges
# * Count the number of records in each bins
# * Sort the value by the temperature range (the index of the series)
# 
# 

# In[7]:


(
    pd
    .cut(
        bike_share_data
        ['Temperature(°C)'], 
        bins=[-18, 0, 8, 16, 24, 40]
    )
    .value_counts()
    .sort_index()
)


# ### Adding meaningful labels
# 
# * Create a new column in the table for the temperature ranges
# * Split the temperature value into 5 bins based on bicycle professional ranges
# * Count the number of records in each bins
# * Add human readable labels to the regions
# * Sort the value by the temperature range (the index of the series)

# In[8]:


bike_share_data['temperature_range'] = (
    pd
    .cut(
        bike_share_data
        ['Temperature(°C)'], 
        bins=[-18, 0, 8, 16, 24, 40],
        labels=['Below Freezing', 'Freezing', 'Cold', 'Warm','Sizzling']
    )
    
)
(
    bike_share_data
    ['temperature_range']
    .value_counts()
    .sort_index()
)


# We see that the order is still the right order and not alphabetical, and the split is more balanced in number of records.
# 
# ### Boxplot for each bin
# 
# Now we can take every group of records and calculate and plot their box plot showing the mean and the different quantiles of the different groups.

# In[9]:


(
    bike_share_data
    [['Rented Bike Count','temperature_range']]
    .boxplot(by='temperature_range')
);


# ## What is wrong with Historgram
# 
# As much as historgrams are popular and simple to plot, they have many limitation:
# - It depends (too much) on the number of bins.
# - It depends (too much) on variable’s maximum and minimum.
# - It doesn’t allow to detect relevant values.
# - It doesn’t allow to discern continuous from discrete variables.
# - It makes it hard to compare distributions.
# 
# We will use a couple of other plot option to see the data distributions more accurately.
# 
# 

# ### Kernel Density Estimator (KDE)
# 
# This method is calculating and plotting the estimation of the data distribution, and it is part of the Pandas built-in functions:

# In[10]:


(
    bike_share_data
    ['Rented Bike Count']
    .plot
    .kde(
        title='Rented Bike Count',
        grid=True
    )
);


# In[11]:


(
    bike_share_data
    ['Temperature(°C)']
    .plot
    .kde(
        title='Temperature(°C)', 
        grid=True
    )
);


# ### Cumulative Distribution Function (CDF)
# 
# The second option is using counts of the different percentiles of the data and using a cumulative plot makes it easy to find the value of each percentile and calculate the percentage of data points between every given percentiles.

# In[12]:


from statsmodels.distributions.empirical_distribution import ECDF
import matplotlib.pyplot as plt


# In[15]:


ecdf = ECDF(bike_share_data['Temperature(°C)'])
plt.plot(ecdf.x, ecdf.y)
plt.grid(True)
plt.title('Temperature(°C)'); 


# In[16]:


ecdf = ECDF(bike_share_data['Rented Bike Count'])
plt.plot(ecdf.x, ecdf.y)
plt.grid(True)
plt.title('Rented Bike Count'); 


# ## Group by Quantiles using _qcut_
# 
# When using a target score such as grades or number of rentals, it makes sense to use the split using the Quantiles of the scores. 

# In[17]:


bike_share_data['usage_level'] = (
    pd
    .qcut(
        bike_share_data['Rented Bike Count'], 
        q=4,
        labels=['Low', 'Medium', 'High', 'Very High']
    )
)
(
    bike_share_data
    ['usage_level']
    .value_counts()
    .sort_index()
)


# In[18]:


(
    bike_share_data
    [['Temperature(°C)','usage_level']]
    .boxplot(by='usage_level')
);


# ### Heat map with the new value group
# 
# Now that we have the new value categories and we can create heat map to see the hours of the day that are the peak hours that can be used with higher price tiers.

# In[19]:


import seaborn as sns


# In[27]:


sns.heatmap(
    bike_share_data
    [['usage_level','Hour','Date']]
    .pivot_table(
        index='Hour', 
        columns='usage_level',
        aggfunc='count'
    )
    .droplevel(0, axis='columns'),
    cmap="YlOrRd"
);


# In[ ]:




