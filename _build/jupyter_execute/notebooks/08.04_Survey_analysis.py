#!/usr/bin/env python
# coding: utf-8

# # Survey Analysis
# 
# We often want to survey people on their views or reactions to possible events (design or promotion, for example). There are many survey tools that are good in designing the survey, presenting it on various forms, such as web or mobile, distributing it and collecting the responses. However, when it comes to analyzing the responses, you are left with fewer options, and most of them are out-dated (SPSS, for example).
# 
# In this notebook, we will explore how to analyze survey's responses, including statistical tests for reliability and research hypothesis. 
# 
# We will start with loading the CSV files that we exported from the survey system (Qualtrics, in this example).

# In[1]:


import pandas as pd


# In[2]:


survey_df = pd.read_csv('../data/survey_results.csv')


# ## Survery Overview
# 
# We can explore the number of questions and answers with _info_

# In[3]:


survey_df.info()


# ## Cliping outliers
# 
# We want to remove outliers to avoid issues from people answering too quick or too slow. Let's calculate the 0.05 and 0.95 percentiles of the data:

# In[4]:


(
    survey_df
    .loc[1:,['Duration (in seconds)']]
    .astype(int)
    .quantile([0.05, 0.95])
)


# And now we can clip the data to be above 90 and below 1,100

# In[5]:


valid_survey_df = (
    survey_df
    .loc[1:,:]
    .assign(duration = lambda x : pd.to_numeric(x['Duration (in seconds)']))
    .query("duration > 90 and duration < 1100")
)
valid_survey_df


# In[6]:


(
    valid_survey_df
    ['duration']
    .plot(
        kind='hist', 
        alpha=0.5, 
        title='Duration (in seconds) (between 0.05 and 0.95)'
    )
);


# ## Map of responders
# 
# Most of the survey tools are also reporting regarding the location of the responders with their location information. This survey also has this data in _LocationLongitude_ and _Locationlatitude_ columns. We can use the popular GeoPandas package to show them over the world map. 
# 
# * Create from GeoPandas
# * a geo-location data frame
# * based on the survey table above
# * Use the geometry information to draw points based on 
# * $x$ as location longitude, and
# * $y$ as location latitude

# In[7]:


import geopandas
import matplotlib.pyplot as plt

gdf = (
    geopandas
    .GeoDataFrame(
        valid_survey_df, 
        geometry=geopandas.points_from_xy(
            valid_survey_df.LocationLongitude, 
            valid_survey_df.LocationLatitude)
        )
)


# * Create a map of the world based on the built-in map from GeoPandas
# * Plot the background map with 
# * while background and
# * black lines
# * and the locations of the responders in red
# * Set the title of the map to "Survey Reponders Locations"

# In[8]:


world = (
    geopandas
    .read_file(
        geopandas
        .datasets
        .get_path('naturalearth_lowres')
    )
)

gdf.plot(
    ax=(
        world
        .plot(
            color='white', 
            edgecolor='black',
            figsize=(15,10)
        )
    ), 
    color='red',
    
).set_title("Survey Reponders Locations");


# ## Personality Score
# 
# The first part of the survey was a personality score that we need to analyze to build the score of each responder. We can find the psychology test format in a previous reserach:

# ## Mini-IPIP test questions
# 
# Based on: "The Mini-IPIP Scales: Tiny-Yet-Effective Measures of the Big Five Factors of Personality" 
# 
# {cite}`mini_ipip2006`
# 
# Appendix 20-Item Mini-IPIP
# 
# 
# | Item | Factor | Text |
# | --- | ---  | --- |
# | 1 | E | Am the life of the party. |
# | 2 | A | Sympathize with others’ feelings |
# | 3 | C | Get chores done right away. |
# | 4 | N | Have frequent mood swings. |
# | 5 | I | Have a vivid imagination. |
# | 6 | E | Don’t talk a lot. (R) |
# | 7 | A | Am not interested in other people’s problems. (R) |
# | 8 | C | Often forget to put things back in their proper place. (R)|
# | 9 | N |  Am relaxed most of the time. (R) |
# | 10 | I | Am not interested in abstract ideas. (R) |
# | 11 | E | Talk to a lot of different people at parties. |
# | 12 | A | Feel others’ emotions. |
# | 13 | C | Like order. |
# | 14 | N | Get upset easily. |
# | 15 | I | Have difficulty understanding abstract ideas. (R) |
# | 16 | E | Keep in the background. (R) |
# | 17 | A | Am not really interested in others. (R) |
# | 18 | C | Make a mess of things. (R) |
# | 19 | N | Seldom feel blue. (R) |
# | 20 | I | Do not have a good imagination. (R) |
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 

# First, let's get the questions that are written in the first line (index=0) of the table. We want the 20 questions from index 18 to index 38.

# In[9]:


(
    survey_df
    .iloc[0,18:38]
)


# Let's check how the results look like in the table:

# In[10]:


survey_df.E1


# We see that we have five personality traits that we are measuring with these questions: E, A, C, N, I.
# * Create a variable for each personality trait above
# * Convert each question to its relevant trait by taking the numertic score at the last character of the question as an Integer, and add it to the relevant trait score. Note that some of the scores are reversed and you need to add the reversed score (6 - score, for a 1-5 score as we have here)

# In[11]:


survey_ipip_df = (
    valid_survey_df
    .assign(E = 0)
    .assign(A = 0)
    .assign(C = 0)
    .assign(N = 0)
    .assign(I = 0)
    .assign(E = lambda x : x.E + x.E1.str[-1:].astype(int))
    .assign(A = lambda x : x.A + x.A2.str[-1:].astype(int))
    .assign(C = lambda x : x.C + x.C3.str[-1:].astype(int))
    .assign(N = lambda x : x.N + x.N4.str[-1:].astype(int))
    .assign(I = lambda x : x.I + x.I5.str[-1:].astype(int))
    .assign(E = lambda x : x.E + 6 - x.E6R.str[-1:].astype(int))
    .assign(A = lambda x : x.A + 6 - x.A7R.str[-1:].astype(int))
    .assign(C = lambda x : x.C + 6 - x.C8R.str[-1:].astype(int))
    .assign(N = lambda x : x.N + 6 - x.N9R.str[-1:].astype(int))
    .assign(I = lambda x : x.I + 6 - x.I10R.str[-1:].astype(int))
    .assign(E = lambda x : x.E + x.E11.str[-1:].astype(int))
    .assign(A = lambda x : x.A + x.A12.str[-1:].astype(int))
    .assign(C = lambda x : x.C + x.C13.str[-1:].astype(int))
    .assign(N = lambda x : x.N + x.N14.str[-1:].astype(int))
    .assign(I = lambda x : x.I + 6 - x.I15R.str[-1:].astype(int))
    .assign(E = lambda x : x.E + 6 - x.E16R.str[-1:].astype(int))
    .assign(A = lambda x : x.A + 6 - x.A17R.str[-1:].astype(int))
    .assign(C = lambda x : x.C + 6 - x.C18R.str[-1:].astype(int))
    .assign(N = lambda x : x.N + 6 - x.N19R.str[-1:].astype(int))
    .assign(I = lambda x : x.I + 6 - x.I20R.str[-1:].astype(int))
    .assign(E = lambda x : x.E / 4)
    .assign(A = lambda x : x.A / 4)
    .assign(C = lambda x : x.C / 4)
    .assign(N = lambda x : x.N / 4)
    .assign(I = lambda x : x.I / 4)
)


# ### Personality Trait Visualization
# 
# We can show a quick histogram of one or two of the traits

# In[12]:


(
    survey_ipip_df
    .E
    .hist()
).set_title("Extraversion");


# In[13]:


(
    survey_ipip_df
    .I
    .hist()
).set_title("Openness to experience");


# ## Random Groups
# 
# Many tests are using split to random groups to check the effect of a treatment on one of the group, while using the other group as a control group (or any other similar test method). In the survey, the group will be visible with answers on some of the questions, while other groups will answer different questions. In this survey, there were two groups that were assigned randomaly question 71 or question 73.

# * Create a new column in the table called _group_
# * create the first condition to have an answer (not null) in Q71 column
# * create the second condition to have an answer in Q73 column
# * assign the group value to be _'Group A'_ for the first condition
# * assign the group value to be _'Group B'_ for the second condition
# * assign a default value _'Unknown'_ if none of the condition is mapped

# In[14]:


import numpy as np
survey_ipip_df['group'] = np.select(
    [
        survey_ipip_df['Q71_Page Submit'].notnull(), 
        survey_ipip_df['Q73_Page Submit'].notnull(), 
    ], 
    [
        'Group A', 
        'Group B'
    ], 
    default='Unknown'
)


# ## Research questions
# 
# The third part is the research questions part, where we want to test the impact of the treatment on the answers to these questions. From the list of columns in the table that we did in the beginning we see that these are starting with _'Expectation1'_, and ends with _'Offering3'_

# In[15]:


survey_questions = (
    survey_df
    .loc[0,'Expectation1':'Offering3']
)
survey_questions


# * Convert all the values of these questions to numeric values based on the last characters ([-1:]) of the answer and set its type to be Interger

# In[16]:


numeric_survey_ipip_df = (
    survey_ipip_df
    .apply(lambda x: 
        x.str[-1:].astype(int) 
        if x.name.startswith('Expectation') 
        else x
    )
    .apply(lambda x: 
        x.str[-1:].astype(int) 
        if x.name.startswith('Trust') 
        else x
    )
    .apply(lambda x: 
        x.str[-1:].astype(int) 
        if x.name.startswith('Offering') 
        else x
    )
)


# ## Testing Reliability with Cronback-Alpha
# 
# A common test to check the reliability of the answers is to test them using Cronback-alpha test. We expect that all the questions that are related to _Trust_, for example, will have a high correlation, and therefore a cronbach-alpha score that is higher than 0.7.
# 
# First, let's install a python library with cronbach-alpha function in it. 

# In[17]:


pip install pingouin


# In[18]:


import pingouin as pg


# Now, let's take the set of questions for each variable (_Expectation_, _Trust_, and _Offering_ in this survey) and calculate their score:

# In[19]:


pg.cronbach_alpha(data=
    numeric_survey_ipip_df
    .loc[:,
        ['Expectation1','Expectation2','Expectation3']
    ]
)


# In[20]:


pg.cronbach_alpha(data=
    numeric_survey_ipip_df
    .loc[:,
        ['Trust1','Trust2','Trust5','Trust6','Trust7','Trust8','Trust9']
    ]
)


# In[21]:


pg.cronbach_alpha(data=
    numeric_survey_ipip_df
    .loc[:,
        ['Offering1','Offering2','Offering3']
    ]
)


# ### Calculate the research variables
# 
# Now that we see that the reliability of the question is good enough (>0.7), we can calculate the average score of each of these questions sets. We will use _eval_ function to do it:

# In[22]:


summary_numeric_survey_df = (
    numeric_survey_ipip_df
    .eval("Expectation = (Expectation1 + Expectation2 + Expectation3) / 3")
    .eval("Offering = (Offering1 + Offering2 + Offering3) / 3")
    .eval("Trust = (Trust1 + Trust2 + Trust5 + Trust6 + Trust7 + Trust8 + Trust9) / 7")
)


# In[23]:


(
    summary_numeric_survey_df
    .group
    .unique()
)


# In[24]:


(
    summary_numeric_survey_df
    [['Expectation','Expectation1','Expectation2','Expectation3','group']]
    .boxplot(by='group', figsize=(13,8))
);


# In[25]:


import seaborn as sns
### PLOT BUILD
fig, ax = plt.subplots(3, 2, figsize=(10,8))

for idx, attribute in enumerate(['Expectation','Trust','Offering']):
    for i,group in enumerate(sorted(summary_numeric_survey_df.group.unique())):
        sub_df = summary_numeric_survey_df.query('group == @group')
        sns.regplot(x=sub_df.E, y=sub_df[attribute], ax=ax[idx,i])
        ax[idx,i].set_title(group, loc='left')

fig.tight_layout()

plt.show()


# ## Anova 

# In[26]:


import statsmodels.api as sm
from statsmodels.formula.api import ols

for attribute in ['Expectation','Trust','Offering']:
    print(attribute)
    model = ols(
        f'{attribute} ~ C(group) * E', 
        data=summary_numeric_survey_df
        .loc[:,['E',attribute,'group']]
    ).fit()
    anova_table = sm.stats.anova_lm(model, typ=2)
    display(anova_table)
    display(summary_numeric_survey_df.anova(dv=attribute, between=['group','E']).round(3))


# In[27]:


import scipy.stats as stats
# stats f_oneway functions takes the groups as input and returns ANOVA F and p value
fvalue, pvalue = stats.f_oneway(summary_numeric_survey_df['E'],summary_numeric_survey_df['Trust'])
print(fvalue, pvalue)


# ## Graphs of all questions

# In[28]:


for q_num, q in survey_questions.iteritems():
    fig, ax = plt.subplots(1, 2)

    for i,group in enumerate(sorted(summary_numeric_survey_df.group.unique())):
        sub_df = summary_numeric_survey_df.query('group == @group')
        sns.regplot(x=sub_df['E'], y=sub_df[q_num], ax=ax[i])
        ax[i].set_title(group, loc='left')

    fig.suptitle(q)
    fig.tight_layout()
    fig.subplots_adjust(top=0.95)

    plt.show()
    plt.clf()
    plt.close()


# In[29]:


from scipy.stats import spearmanr
for q_num, q in survey_questions.iteritems():
    stat, p = spearmanr(
        (
            summary_numeric_survey_df
            .query('group == "Group A"')
            .iloc[:40,:]
            [q_num]
        ),
        (
            summary_numeric_survey_df
            .query('group == "Group B"')
            .iloc[:40,:]
            [q_num]
        )
    )
    print('stat=%.3f, p=%.3f' % (stat, p),q)


# ## SPSS Files
# 
# Pandas can also load SPSS files 

# In[30]:


#pip install pyreadstat


# In[31]:


#spss_df = pd.read_spss()


# In[32]:


#spss_df


# In[ ]:




