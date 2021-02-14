#!/usr/bin/env python
# coding: utf-8

# # Adding New Columns
# 
# In the second chapter we will learn how to add new columns to the tables based on a set of functions. This is similar to the Functions that are available in Excel with _=FUNC(A1)_

# We will start with loading a csv file that is hosted in data.world on the "Median Value Per Sq ft per zip code in the US"

# In[1]:


import pandas as pd


# In[2]:


us_median_sq_ft_value = (
    pd
    .read_csv('https://query.data.world/s/xrfy7fb7oq55gpzh6bvs6jtonv32lk')
)


# In[3]:


us_median_sq_ft_value.head()


# ## Constant Value
# 
# The simplest way to add a column is to put a constant value. Since we know that this data is only for USA we can add a column with the value _USA_ to a new column called _country_. We will be able to later merge this table with data from other countries and then this new column will be useful. 
# 
# For setting a value in a column we will use the [assign](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.assign.html) function of Pandas. You will need to scroll all the way to the right of the output to see the new _country_ column.

# In[4]:


(
    us_median_sq_ft_value
    .assign(country="USA")
)


# ## Excel Functions Equivalent
# 
# Most of the functions that you are used to use in Excel have a direct Equivalent in Pands. We will try a few of them in the following examples. We will only look at the _City_ column in the dataset.
# 
# For example: ```=TRIM('cell for trimming')``` can be replaced by _strip_. 
# We will:
# * Take only the _City_ column from the table 
# * Add a column that strips spaces from around the string (_str_) of the _City_ column
# * Show the head (first 5 lines) of the new sub-table

# In[5]:


(
    us_median_sq_ft_value[['City']]
    .assign(trimmed = us_median_sq_ft_value.City.str.strip())
    .head()
)


# or to remove spaces between words, you will need to run 'Find and Replace' option in Excel and in Pandas we can use the _replace_ function:
# * Take only the _City_ column from the table 
# * Add a column that is removes every space (' ') from the string of the _City_ column
# * Show the head of the new sub-table

# In[6]:


(
    us_median_sq_ft_value[['City']]
    .assign(no_space = us_median_sq_ft_value.City.str.replace(' ',''))
    .head()
)


# ### More Textual Functions
# 
# Another commonly used Excel functions are LEFT and RIGHT (```=LEFT(Cell, number of digits)```). In Pandas, we can use the '```:```', which is used for _until_ or _from_:
# * Take only the _City_ column from the table 
# * Add a column that takes the first 5 characters (=LEFT) from the string of the _City_ column
# * Add a column that takes the last 5 characters (=RIGHT) from the string of the _City_ column
# * Show the head of the new sub-table
# 

# In[7]:


(
    us_median_sq_ft_value[['City']]
    .assign(city_left = us_median_sq_ft_value.City.str[:5]) # until the 5th character
    .assign(city_right = us_median_sq_ft_value.City.str[-5:]) # from the 5th characters from the end (=right)
    .head()
)


# ## Using Lambda
# 
# Lambda is a bit confusing at first glance, however, it is used to define a the function that we want to apply on a each row or columns of the table. For example, let's define two new columns: one that is calculating the quantile of the region compare to all the regions, and one that is checking if the state is one of ['NY','NJ']
# 
# We will focus only on the _State_ and the last month in the data and add the two new columns to it.
# * Take only the _State_ and the values of the last period columns from the table 
# * Add a column that checks if the _State_ is either _'NY'_ or _'NJ'_
# * Add a column that calculates the ratio of the average price of the row to the maximum price (quantile)

# In[8]:


(
    us_median_sq_ft_value[['State','2017-09']]
    .assign(is_NY_or_NJ=lambda x : x.State.isin(['NY','NJ']))
    .assign(last_quantile=lambda x : x['2017-09']/max(x['2017-09']))    
)


# ## Multiple Data Sources
# 
# We can do a more complicated analysis that is based on additional external sources. For example, we want to calculate the differences between red states and blue states. We can then ask various questions regarding the impacts or correlation between the house prices and the election results and voting patterns. 
# 
# First we will load data regarding the voting in various states across the years. A quick internet search finds an interesting table in the following Wikipedia page. Since there are multiple tables on that page, we can filter them using the _match_ option, and using the word _Year_ as the filter.
# * Read the HTML tables in the wikipedia entry on the topic of red and blue states
# * retrive on the ones that have the word 'Year'

# In[9]:


red_blue_states_wikipedia_entry = 'https://en.wikipedia.org/wiki/Red_states_and_blue_states'
wikipedia_page_tables = (
    pd
    .read_html(
        red_blue_states_wikipedia_entry, 
        match='Year'
    )
)


# As we saw in the loading data from web site, the list can includes multiple tables. However, we filtered it and only have one table, and we can access it with the _[0]_ modifier.

# In[10]:


red_blue_states = wikipedia_page_tables[0]
red_blue_states.head()


# We will start with creating a new list of states that voted for a specific candidate in a specific electio. First, let's use Trump in the 2016 elections. 
# 
# We are using here a few new functions such as [rename](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.rename.html), [query](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.query.html) and [iloc](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.iloc.html), which we will discuss in more details in the next sections.

# In[11]:


red_candidate = 'Trump'


# We will:
# * Take the large table of the multiple elections results
# * Remove the complicated multi level header from the table (_droplevel_)
# * Filter to only states that have the name of the red candidate, we defined above, in the column of the election year (_2020_, for example). Note, we need to surround the name of the column with ` as it starts with a number
# * Take only the first column from the result table, which holds the name of the state (_iloc[:,0]_). 

# In[12]:


red_states_2020 = (
    red_blue_states
    .droplevel(1, axis=1) 
    .query("`2020` == @red_candidate")
    .iloc[:,0]
)
red_states_2020


# Now that we have the list of the red states of 2020, we need to match them to the states that we have in our house prices data set. We see that we have to match the short version in the data set with the long version in the red state list. 
# 
# We will use a another option to create a data frame using a Dictionary. It is not hard to find a list of mapping of states names and abbreviations. 

# In[13]:


us_state_abbrev = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'American Samoa': 'AS',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Guam': 'GU',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Northern Mariana Islands':'MP',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Puerto Rico': 'PR',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virgin Islands': 'VI',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY'
}


# and we can use the dictionary to create a table (DataFrame) from it:
# * Create a new dataframe table
# * Using the dictionary of the us state abbreviation above
# * with row for each entry
# * and name the column of the value 'Abbreviation' 

# In[14]:


us_state_abbrev_df = (
    pd
    .DataFrame
    .from_dict(us_state_abbrev, 
                orient='index',
                columns=['Abbreviation'])
)


# Before we continue, we can keep this table as file to be used in future analyses. We could also create this file in Excel and load it as we will do in the future with this file. 

# In[15]:


us_state_abbrev_df.to_csv('../data/us_state_abbrev.csv')


# Next, we will:
# * Start with the abbreviation list of all the US states
# * Take only the ones that also appear in the list of red states in the 2020 election
# * Take all the rows left, and the index column (country name) with the abbreviation column

# In[16]:


red_state_abbrev = (
    us_state_abbrev_df
    .loc[red_states_2020]
    .loc[:,'Abbreviation']
)
red_state_abbrev


# Finally:
# * Start with the table of the median value of sqr feet per zip code
# * Add a new column (_is_red_) that checks if the _State_ in each row is in the list of red states that we calculated above. 
# * Create two groups for red and blue states and the a value in the last period in the table (September 2017)
# * Calculate the average (_mean_) price for each of the two groups
# * Plot the two values
# * Title the graph with "Average square feet value between blue and red states"

# In[17]:


(
    us_median_sq_ft_value
    .assign(is_red=lambda x : x.State.isin(red_state_abbrev))
    .groupby('is_red')['2017-09']
    .mean()
    .plot
    .bar(title="Average square feet value between blue and red states")
);


# We can now see that the average value of square feet in the blue states (_is_red = False_) is about twice the average of red states (_is_red = True_)

# In[ ]:




