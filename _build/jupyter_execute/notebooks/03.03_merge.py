#!/usr/bin/env python
# coding: utf-8

# # Merge/Join Tables (VLOOKUP)
# 
# The _merge_ function mimics the functionality of JOIN in SQL queries and replaces the VLOOKUP functionality in Excel. It is one of the most powerful and useful functions for dataframes in Pandas. The main idea is to:
# - **join** two (or more) dataframe table using similar keys in each of the tables. 
# - **enrich** tables with loopup data  
# - **validate** the match values of the key columns in the tables

# In[1]:


import pandas as pd


# ## Loading lookup data
# 
# For this example, we will take one of the common lookup data, zip code. The loopup is not trivial as there are a few tousands (more than 33,000 as you can see below) of values and a simple Excel file will struggle to do it efficently and quickly. 
# 
# We will start with loading the loopup data from [Simple Maps](https://simplemaps.com/data/us-zips), which I've downloaded to a public S3 bucket.

# In[2]:


url = 'https://mlguy-public.s3-eu-west-1.amazonaws.com/excel2pandas/chapter3/simplemaps_uszips_basicv1/uszips.csv'

import requests
from io import StringIO

response = requests.get(url)
response


# The CSV file is read through a URL and therefore, we need to convert the text of the response to a simple string as we get when we read a local file. For that we will use the StringIO functionality as follows:

# In[3]:


zip_lookup = (
    pd
    .read_csv(
        StringIO(
            response.text
        )
    )
)

zip_lookup


# ## Lookup Data Exploration
# 
# The table above shows us the type of data that we can get from enrichment based on the zip code, including city, state, latitude, longitude, population count and density.  
# 
# We can explore the values that we have in this table, before we start to use it for enrichment.

# ## Counting Values
# 
# The simplest aggregation function for each group is the _size_. How many zip codes do we have in each state?

# In[4]:


(
    zip_lookup
    .groupby('state_name')
    .size()
)


# ## Sorting Values
# 
# To sort the values is also simple with _sort_value()_ function, and see the population size of each state (based on the zip code lookup data):
# * Start with the zip lookup data above
# * Group the row by _state\_name_ and take only the _population_ values
# * Sum up all the population values for each zip code area in the state Group
# * Sort the states by the accumulated population value in descending order

# In[5]:


us_population_distribution = (
    zip_lookup
    .groupby('state_name')['population']
    .sum()
    .sort_values(ascending=False)
)

us_population_distribution


# ## Visualization of the data
# 

# In[6]:


(
    us_population_distribution
    .plot
    .bar(figsize=(13,5))
);


# ## Loading the main data
# 
# We will take the data about brewries in the US that we used in one of the previous lessson, and enrich it with the data from the zip codes table. We will load it from the local file after we retried the data from the API before. 

# In[7]:


breweries_data= pd.read_csv('../data/us_breweries.csv')


# In[8]:


breweries_data.head()


# We can see that the postal code is sometimes in the longer format (for example, _35222-1932_) compare to the zip codes that we have in our lookup table (for example, 35222). We will convert them to the shorter format by taking the first 5 characters ([:5]) of the string of the postal_code column.

# In[9]:


breweries_data_with_zip = (
    breweries_data
    .assign(zip_code = lambda x : x.postal_code.str[:5])
)


# In[10]:


breweries_data_with_zip.head()


# ## Joining the tables
# 
# The joining of the table is based on a joined key. In this case we want to use the 5-digits zip code as the lookup or join key. In the previous step with shorten the longer zip codes to the shorter 5 digits format, and now we will make sure that the lookup table also have it in the same format. 
# * Start with the zip loopup table
# * Add a column zip_code that is based on the value of the column _zip_
# * Convert the numeric value into string (_astype(str)_), 
# * Pad the string with zeros when the number is shorter than 5 digits (_zfill(5)_).

# In[11]:


zip_lookup_as_string = (
    zip_lookup
    .assign(
        zip_code = lambda x : x.zip
        .astype(str)
        .str
        .zfill(5)
    )
)


# The join itself is simple. 
# * Start with the breweries table that you want to enrich 
# * Join using _merge_ with the second zip loopup table 
# * Define the key column with the same name (zip_code), and we use it using the _on_ argument
# * Lastly, we want to have all breweries, even if we don't find the zip code in the lookup table. Therefore, we are using _LEFT_ join using the _how_ argument. 

# In[12]:


enriched_breweries_data = (
    breweries_data_with_zip
    .merge(
        zip_lookup_as_string, 
        on='zip_code', 
        how='left'
    )
)


# We have now many more columns as all the columns of both tables are joined to the enriched table. We will ask the Jupyter notebook to show us all the columns by removing the default maximum number of columns to display. 
# 
# In the table below we can see all the columns. If the same column name is found in both tables and it wasn't the column that was used for the join or merge, the column of first ("left") table will be appended with x (city_x, for example), and the column of the second ("right") table will be appended with y (city_y, for example).

# In[13]:


pd.set_option('display.max_columns', None)
enriched_breweries_data


# Now, that we have the enriched table, we can analyze the joined data and explore the different counties across the US:
# * Start with the enriched breweries data above
# * Group the breweries by county_name
# * For each group add the State ID 
# * count the number of breweries, 
# * sum up the populations of each zip code area in each group
# * and calculate the average population density in the county 
# * Sort that list by the population size

# In[14]:


(
    enriched_breweries_data
    .groupby('county_name')
    .agg(
        state=('state_id', 'min'), 
        brewry_count=('id', 'count'),
        population_sum=('population', 'sum'),
        density_average=('density', 'mean')
        )
    .sort_values(by='population_sum', ascending=False)
)


# We can see that _san Diego_ is the largest county in terms of population and also a beer county with 154 different brewries in it. 

# Let's change the sort key to find the counties with the most breweries

# In[15]:


(
    enriched_breweries_data
    .groupby('county_name')
    .agg(
        state=('state_id', 'min'), 
        brewry_count=('id', 'count'),
        population_sum=('population', 'sum'),
        density_average=('density', 'mean')
        )
    .sort_values(by='brewry_count', ascending=False)
)


# If you remember the map of the US that we saw in the previous section, it is now more clear the Cook county in IL is likely the dark area we saw in our hexbin visualization of the data, as a dense population of breweries. 
# 
# We can now ask ourselves where do we have the most brewries per population and add this column to our table

# In[16]:


(
    enriched_breweries_data
    .groupby('county_name')
    .agg(
        state=('state_id', 'min'), 
        brewry_count=('id', 'count'),
        population_sum=('population', 'sum'),
        density_average=('density', 'mean')
        )
    .assign(brewry_per_population = lambda x : x.brewry_count / x.population_sum * 1000)
    .sort_values(by='brewry_per_population', ascending=False)
)


# We can see, as it is often the case, that we have on the top and the bottom of the table counties with very few brewries. The top of the table of brewries per 1000 people is held by Keweenaw that was last on our previous table of counties by population. To avoid this, we can filter (using _query_) our table to counties that have more than 5 brewries.

# In[17]:


(
    enriched_breweries_data
    .groupby('county_name')
    .agg(
        state=('state_id', 'min'), 
        brewry_count=('id', 'count'),
        population_sum=('population', 'sum'),
        density_average=('density', 'mean')
        )
    .assign(brewry_per_population = lambda x : x.brewry_count / x.population_sum * 1000)
    .query("brewry_count > 5")
    .sort_values(by='brewry_per_population', ascending=False)
)


# And the winner is Schuyler county in New York, with 7 brewries and a 0.46 brewry for every 1,000 people

# ## Geographic Mapping
# 
# The merge that we did allows us now to have geo location information for all the breweries, including the ones that didn't have it in the original data set, as we have the geo location of the zip code area.  
# 
# We can also add layers on real maps using the library GeoPandas. Let's start with installing the library to our environment. 

# In[18]:


pip install geopandas


# We also need to install a library to handle geo coordinates

# In[19]:


pip install descartes


# We will import the library

# In[20]:


import geopandas


# * Create a data frame that is designed for geo data
# * Start with the enriched breweries data above
# * Define the geometry of the data from 
# * x as the longitude (_lng_ column)
# * y as the latitude (_lat_ column)

# In[21]:


gdf = (
    geopandas
    .GeoDataFrame(
    enriched_breweries_data, 
    geometry=geopandas
    .points_from_xy(
        enriched_breweries_data.lng, 
        enriched_breweries_data.lat)
    )
)


# Create a geo dataframe for the world map from the built-in dataset of GeoPandas library

# In[22]:


world = (
    geopandas
    .read_file(
        geopandas
        .datasets
        .get_path('naturalearth_lowres')
    )
)


# * Start with the world data frame
# * Filter it to use only the USA parts
# * Focus on the geometry boundaries of the map
# * Plot the map
# * using black color
# * and thin lines (0.2)
# * Now, plot the breweries data 
# * on the above map 
# * using red dots 
# * and one pixel for each

# In[23]:


# We restrict to USA
ax = (
    world
    [world.iso_a3 == 'USA']
    ['geometry']
    .boundary
    .plot(
        color='black', 
        edgecolor='black', 
        linewidth=0.2
    )
)

( 
    gdf
    .plot(
        ax=ax, 
        color='red',
        markersize = 1
    )
);


# This is a good start, but we can't really use it. Let's make it more usable to know where is the beer hub in the US.
# 
# * Create a 2D histogram based on the enriched breweries data 
# * using x as latitude (_lat_ column),
# * y as longtitude (_lng_ column),
# * and 1000 bins for the histogram
# * Focus only on the main land using its coordinates
# * Then, create a smooth heat map from the histogram 

# In[24]:


import numpy as np
from scipy import ndimage

heatmap, xedges, yedges = np.histogram2d(
    enriched_breweries_data['lat'], 
    enriched_breweries_data['lng'],
    bins=1000, 
    range=[
        [25, 50],  # North-South extent of US
        [-125, -65]  # East-West extent of US, 
    ]
)
extent = [yedges[0], yedges[-1], xedges[-1], xedges[0]]
logheatmap = np.log(heatmap)
logheatmap[np.isneginf(logheatmap)] = 0
logheatmap = ndimage.filters.gaussian_filter(logheatmap, 30, mode='nearest')  # smooth out peaks


# In[25]:


ax = (
    world
    [world.iso_a3 == 'USA']
    ['geometry']
    .boundary
    .plot(
        color='k', 
        edgecolor='black', 
        linewidth=0.5
    )
)

ax.imshow(logheatmap, cmap='coolwarm', extent=extent)
ax.invert_yaxis()
ax.set(xlim=[-125, -65], ylim=[25, 50]);


# We can clearly see the hubs in San Diego, New York, Illinois, and another one in Colorado.
