#!/usr/bin/env python
# coding: utf-8

# # Creating a Pivot Table
# 
# Pivot Tables are one of the most used features in Excel. You can point to a large table of data and interactively group the data and calculate multiple statistics on each of the groups and sub groups. Pandas makes it easy to do similar functionalities using the _pivot_table_ function. There are multiple options to achieve similar and even more powerful calculations with other Pandas functions, which we will cover later, however, _pivot_table_ is the most straight comparison to the one in Excel, and therefore, we will start with it

# ## Loading Data
# 
# As always, we will start with loading some data set (using the great tutorial from [pbpython](https://pbpython.com/pandas-pivot-table-explained.html))

# In[1]:


import pandas as pd
# import numpy as np

sales_funnel = (
    pd
    .read_excel("https://pbpython.com/extras/sales-funnel.xlsx")
)

sales_funnel.head()


# ## Simple Pivot Table
# 
# The simplest usage is to define what will be the index of the pivot table, which is equivalent to _Rows_ in Excel pivot table. All the numeric values will be added automatically and their **average** will be calculated.

# In[2]:


(
    sales_funnel
    .pivot_table(index=["Name"])
)


# ## Multi-Index
# 
# We can define multiple columns as index and create a multi-index.

# In[3]:


(
    sales_funnel
    .pivot_table(index=["Manager","Rep"])
)


# ## Choosing Values
# 
# The _Account_ number is also a numeric column, however, it is not relevant for us to look at in the pivot table, and the same goes for the _Quantity_ column. Therefore, we can choose to take only the _Price_ column for our pivot table.

# In[4]:


(
    sales_funnel
    .pivot_table(
        index=["Manager","Rep"], 
        values=["Price"]
    )
)


# ## Chossing aggregation function
# 
# We want to see the sum of the sales of each sales rep and not the average size of the sales. Let's request to use the _sum_ as the aggregation function. Other functions are _mean_ (default), _median_ _count_, _min_, _max_, _var_, _std_, and _prod_

# In[5]:


(
    sales_funnel
    .pivot_table(
        index=["Manager","Rep"], 
        values=["Price"],
        aggfunc='sum'
    )
)


# ## Choosing Columns
# 
# The _Columns_ selection in Excel is similar to the one in pivot table in Pandas. We can add a breakdown of the sales per product, by adding it as the _Columns_ of the pivot table

# In[6]:


(
    sales_funnel
    .pivot_table(
        index=["Manager","Rep"], 
        values=["Price"],
        columns=["Product"],
        aggfunc='sum'
    )
)


# ## Removing Null (NaN) values
# 
# To make the table cleaner we can replace all the NaN values with 0

# In[7]:


(
    sales_funnel
    .pivot_table(
        index=["Manager","Rep"], 
        values=["Price"],
        columns=["Product"],
        aggfunc='sum',
        fill_value=0
    )
)


# We can add more values such as _Quantity_

# In[8]:


(
    sales_funnel
    .pivot_table(
        index=["Manager","Rep"], 
        values=["Price","Quantity"],
        columns=["Product"],
        aggfunc='sum',
        fill_value=0
    )
)


# ## Showing Totals
# 
# The default pivot table in Pandas is not showing the totals of the columns or rows, however, we can add it with _margins=True_. It will add _All_ both for the columns at the bottom and for the rows on the right.

# In[9]:


(
    sales_funnel
    .pivot_table(
        index=["Manager","Rep"], 
        values=["Price"],
        columns=["Product"],
        aggfunc='sum',
        fill_value=0,
        margins=True
    )
)


# ## Visualize the pivot table
# 
# we can see the values in a graph

# In[10]:


(
    sales_funnel
    .pivot_table(
        index=["Manager","Rep"], 
        values=["Price"],
        columns=["Product"],
        aggfunc='sum',
        fill_value=0
    )
    .plot(
        kind='bar', 
        rot=45
    )
);


# ## Multiple Aggregation Functions
# 
# You can define multiple Aggregation functions for a value or different Aggregation functions for different values. You can either pass an array of function or a dictionary for different columns.

# In[11]:


(
    sales_funnel
    .pivot_table(
        index=["Manager","Rep"], 
        values=["Price","Quantity"],
        columns=["Product"],
        aggfunc={ 
            "Price" :['sum','median'],
            "Quantity" : 'sum'
        },
        fill_value=0
    )
)


# ## Format the values
# 
# A pivot table is simply a dataframe in Pandas and you can format the values similar to the formating of any other dataframe. We will cover Styling in a dedicated section, however, here is a quick preview to formating the the _Price_ column as currency

# In[12]:


(
    sales_funnel
    .pivot_table(
        index=["Manager","Rep"], 
        values=["Price"],
        aggfunc='sum',
        fill_value=0
    )
    .style
    .format({'Price':'${0:,.0f}'})
)


# In[ ]:




