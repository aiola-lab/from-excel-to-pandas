#!/usr/bin/env python
# coding: utf-8

# # Linear Programming (Optimization) 
# 
# In this example, we will use an common analysis that is used to optimize decision based on constrains, and it is based on the great blog post [How to Solve Optimization Problems with Python](https://towardsdatascience.com/how-to-solve-optimization-problems-with-python-9088bf8d48e5)

# In[1]:


import pandas as pd
import numpy as np


# ## Loading the data
# 
# We will get the data from HTML table that are available from [Rotoguru](http://rotoguru.net), that is gather stats data from fantasy league. We will focus on the data of the NBA players.

# In[2]:


data_url = 'http://rotoguru1.com/cgi-bin/hyday.pl?game=fd'
dfs = (
    pd
    .read_html(data_url)
)


# There are a few HTML table in the page, and after some scorlling we can see that the table with the players data is the 6th one (index=5):
# * Start with the dataframe at index 5 of the list of table from the HTML page above
# * Rename the column to be: Position, Name,FD Points, Salary, Team, Opp., Score, Min, Stats
# * Filter out rows with Position string longer than 2 characters (header lines)
# * Add a column called _Points_ with the float value of the points to be used as the target of the optimization 
# * Remove the dollar sign and commas (\[$,\]) from the Salary column and convert it to its integer value
# 

# In[3]:


all_players = (
    dfs[5]
    .rename(
        columns={
            0:'Position',
            1:'Name',
            2:'FD Points',
            3:'Salary',
            4:'Team',
            5:'Opp.',
            6:'Score',
            7:'Min',
            8:'Stats'
            }
    )
    .query('Position.str.len() <= 2')
    .assign(Points = lambda x : x['FD Points'].astype(float))
    .assign(Salary = lambda x : x.Salary.str.replace('[$,]','', regex=True).astype(int))
)
all_players


# ## Installing the LP Library
# 
# Many times you can find a python library that is implementing many of the fucntions that you need. This is another major benefit of Python over close tools such as Excel.

# In[4]:


pip install pulp


# ## Defining the problem variables
# 
# The most complicated part of the analysis is to understand how to map it into the domain of the algorithm. 
# 
# The current problem that we want to solve using Linear Programming (LP) is what is the best roaster of NBA players we want to choose for our fantasy league. The output is this case is the list of the players names. 
# 
# We will create a list of all the players and assign them either 1 (selected to the team) or 0 (not selected)
# * Create a Linear Programming variables
# * from a dictionary
# * with no prefix to the names
# * and index of $x_i$ as the player names
# * and the value is an Integer
# * that is either 0 (not selected)
# * or 1 (selected)

# In[5]:


from pulp import *

player_vars = (
    LpVariable
    .dicts(
        '', 
        list(all_players['Name']), 
        cat='Integer',
        lowBound=0, 
        upBound=1 
    )
)


# ### Problem target
# 
# In the fantasy league games, we want to maximize the number of points that the player that we choose will score in the next game. 
# 
# Let's start with defining the LP problem as a maximization problem:
# 

# In[6]:


total_score = LpProblem('Fantasy Points Problem', LpMaximize)


# ### Variable Dictionaries
# 
# The library is expecting to get a set of dictionaries each with the name of the player as the common index and the numeric value for each. We will do that for the Points (the target to maximize), the Positions (that we need to pick a couple of each position), and the Salaries (that we need to cap to a specific limit).

# In[7]:


points = (
    all_players
    .set_index('Name')
    .to_dict()
    ['Points']
)


# In[8]:


salaries = (
    all_players
    .set_index('Name')
    .to_dict()
    ['Salary']
)


# ### Linear Programming (LP) Definition
# 
# The LP problem is defined as a set of linear expressions of the form:
# 
# $𝑎_1𝑥_1+𝑎_2𝑥_2+𝑎_3𝑥_3+...𝑎_𝑛𝑥_𝑛 {<=,=,>=} 𝑏$
# 
# Where $x_1, x_2 ... x_n$ are the _decision_ variables we want to choose (the player names), and $a_1, a_2, ... a_n$ are the _objective_ and _constrains_ variables we have in our data.
# 
# First, we add the LP sum of the points where $a_i$ is the points each player scored, and $x_i$ is the player:
# 
# total score = $\sum p_i*x_i$
# 
# - $p_i$ - points scored by player$_i$
# - $ x_i = \begin{cases} 
#       1 & \text{if player in team} \\
#       0 & \text{if player not in team} 
#    \end{cases}
# $
# 
# 

# In[9]:


total_score += (
    lpSum(
        [
            points[player] * player_vars[player] 
            for player in player_vars
        ]
    )
)


# In a real application we will want to have the projected number of points and not the sum of past points, and we will calculated a forecasting model that can identify trends or recent injuries. But for this simple example, we will take that sum as a good estimator for their expected points in the next game. 
# 
# Second, we add the constrain the salaries where $a_i$ is the salary of each player, and $x_i$ is the player, and the constrain value for the sum of all the salaries of the players we choose not to exceed $60,000:
# 
# $\sum s_i*x_i <= 60,000$
# 
# - $s_i$ - salary of player$_i$
# - $ x_i = \begin{cases} 
#       1 & \text{if player in team} \\
#       0 & \text{if player not in team} 
#    \end{cases}
# $
# 

# In[10]:


total_score += (
    lpSum(
        [
            salaries[player] * player_vars[player] 
            for player in player_vars
        ]
    ) <= 60_000
)


# Last, we want to make sure that we have the right number of players in each position in the fantasy team. We will create a list of players for each of the positions: Point Guard (PG), Shooting Guard (SG), Small Forward (SF), Power Forward (PF), and Center (C)

# In[11]:


pg = (
    all_players
    .query("Position == 'PG'")
    ['Name']
    .to_list()
)
sg = (
    all_players
    .query("Position == 'SG'")
    ['Name']
    .to_list()
)
sf = (
    all_players
    .query("Position == 'SF'")
    ['Name']
    .to_list()
)
pf = (
    all_players
    .query("Position == 'PF'")
    ['Name']
    .to_list()
)
c = (
    all_players
    .query("Position == 'C'")
    ['Name']
    .to_list()
)


# And add the constrains to have exactly two PG, two SG, two SF, two PF and one C:
# 
# $\sum x_i = 2  , \text{if player is in PG, SG, SF, PF} \\
#  \sum x_i = 1 , \text{if player is in C} 
#  $
#  - $ x_i = \begin{cases} 
#       1 & \text{if player in team} \\
#       0 & \text{if player not in team} 
#    \end{cases}
# $

# In[12]:


# Set Constraints
total_score += lpSum([player_vars[player] for player in pg]) == 2
total_score += lpSum([player_vars[player] for player in sg]) == 2
total_score += lpSum([player_vars[player] for player in sf]) == 2
total_score += lpSum([player_vars[player] for player in pf]) == 2
total_score += lpSum([player_vars[player] for player in c]) == 1


# ### LP Solution
# 
# Finally, we can solve the set of linear expressions: 

# In[13]:


total_score.solve()


# And filter the list of the possible players to the ones that were selected (their variable value is 1):

# In[14]:


( 
    list(
        filter(
            lambda x : x.varValue == 1, 
            total_score.variables()
        )
    )
)


# The list of the players above is changing every week based on their recent performance, and we can execute this analysis every time before we define our fantasy team for the next round. 

# In[ ]:




