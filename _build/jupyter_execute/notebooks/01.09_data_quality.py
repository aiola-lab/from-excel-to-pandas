#!/usr/bin/env python
# coding: utf-8

# # Check for Data Quality

# In[1]:


get_ipython().system('pip install great_expectations')


# In[2]:


import great_expectations as ge


# In[3]:


facts_df = ge.read_csv("~/Downloads/d5d02a76721a486a98a744707a5ba53c.csv")


# In[4]:


facts_df.head()


# In[5]:


facts_df['חנות - פורמט'].unique()


# In[6]:


facts_df.expect_column_distinct_values_to_be_in_set('חנות - פורמט', ['חנויות נוחות', 'רשתות ארציות דיסקאונט', 'רשתות ארציות סופרמרקטים', 'שוק פרטי דיסקאונט', 'שוק פרטי מינימרקטים', 'שוק פרטי קטן'])


# In[7]:


facts_df.describe()


# In[8]:


facts_df.expect_column_max_to_be_between('מכירות במליוני שקלים',2,3)


# In[9]:


facts_df['שבוע'].unique()


# In[10]:


import pandas as pd
metadata_file = '7013a876be72492e95abc1697ce48f4f.xls'
metadata_df = pd.read_excel(f"~/Downloads/{metadata_file}")


# In[11]:


metadata_df.head()


# In[12]:


facts_df_with_date = (
    facts_df
    .assign(week_number = lambda x : x['שבוע'].str[:2])
    .assign(week_date = lambda x : pd.to_datetime(x['שבוע'].str[-10:], format='%d\%m\%Y', errors='coerce'))
)


# In[13]:


merged_df = (
    facts_df_with_date
    .query('week_number > "34"')
    .merge(metadata_df, on='פריט - ברקוד')
)


# In[14]:


merged_df.columns


# In[15]:


scaled_df = (
    merged_df
    .rename(columns={
        'שבוע':'week_desc',
        'חנות - פורמט':'format_name',
        'מכירות במליוני שקלים_x':'sales_in_m',
        'פריט - ברקוד':'item_id',
        'מכירות באלפי ליטרים':'volume_in_k',
        'מכירות בטונות':'weight_in_tons',
        'מכירות באלפי יחידות באריזה':'quantity_in_k',
        'מחיר ממוצע ליחידה': 'avg_price_units_in_package',
        'מחיר ממוצע לקילו': 'avg_price_weight',
        'מחיר ממוצע לליטר': 'avg_price_volume',
        'פריט - תת קטגוריה': 'public_sub_category',
        'פריט - קטגוריה': 'public_category',
        'פריט - מחלקה': 'public_class',
        'קטלוג פרטי - תת קטגוריה': 'private_sub_category',
        'קטלוג פרטי - קטגוריה': 'private_category',
        'שם פריט': 'item_name',
        'פריט - מותג': 'brand',
        'פריט - תת מותג': 'sub_brand',
        'פריט - ספק': 'supplier_name'
    })
    .assign(weight = lambda x : x.weight_in_tons*1000)
    .assign(volume = lambda x : x.volume_in_k*1000)
    .assign(sales = lambda x : x.sales_in_m*1000*1000)
    .assign(quantity_in_k=lambda x : pd.to_numeric(x.quantity_in_k, errors='coerce'))
    .assign(quantity = lambda x : x.quantity_in_k*1000)
    .assign(avg_price_volume=lambda x : pd.to_numeric(x.avg_price_volume, errors='coerce'))
    .assign(avg_price_weight=lambda x : pd.to_numeric(x.avg_price_weight, errors='coerce'))
    .assign(avg_price_units_in_package=lambda x : pd.to_numeric(x.avg_price_units_in_package, errors='coerce'))
)


# In[16]:


scaled_ge_df = ge.from_pandas(
    scaled_df
)


# In[17]:


scaled_ge_df.expect_column_mean_to_be_between('sales',1000,20000 )


# In[18]:


scaled_ge_df.describe()


# In[19]:


scaled_ge_df.hist(bins=50,figsize=(13.333,7.5))


# In[20]:


scaled_ge_df.info()


# In[21]:


scaled_ge_df.expect_column_median_to_be_between('quantity',800,1000)


# In[22]:


scaled_ge_df.expect_column_mean_to_be_between('volume',150000,200000,meta={"notes": "The scaling might fail"})


# In[23]:


scaled_ge_df.expect_column_mean_to_be_between('weight',150000,200000,meta={"notes": "The scaling might fail"})


# In[24]:


scaled_ge_df.expect_column_mean_to_be_between('avg_price_volume',4,35)


# In[25]:


scaled_ge_df.expect_column_mean_to_be_between('avg_price_weight',50,100)


# In[26]:


scaled_ge_df.expect_column_mean_to_be_between('avg_price_units_in_package',10,100)


# In[27]:


import io
f = io.BytesIO()
scaled_df.to_parquet(f)
    

