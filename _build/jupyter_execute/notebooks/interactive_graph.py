#!/usr/bin/env python
# coding: utf-8

# # Testing Interactive Graphs to S3

# In[1]:


pip install plotly


# In[2]:


import plotly.express as px

fig =px.scatter(x=range(10), y=range(10))
fig.write_html("test.html")


# In[3]:


import boto3 

s3 = boto3.client('s3')
with open("test.html", "rb") as f:
    s3.upload_fileobj(f, 
    "revelio-public-files", 
    "interactive_graph/test.html",
    ExtraArgs={'ContentType': "text/html"} 
)


# In[4]:


response = s3.generate_presigned_url(ClientMethod='get_object',
                                                    Params={'Bucket': 'revelio-public-files',
                                                            'Key': 'interactive_graph/test.html'},
                                                    ExpiresIn=3600)
response


# In[5]:


s3.put_bucket_website(
     Bucket='revelio-public-files',
     WebsiteConfiguration={
     'ErrorDocument': {'Key': 'error.html'},
     'IndexDocument': {'Suffix': 'index.html'},
    }
 )


# In[ ]:




