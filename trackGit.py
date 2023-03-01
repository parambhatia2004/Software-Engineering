import json
import requests
from pandas.io.json import json_normalize
import pandas as pd
import numpy as np
import config

github_api = "https://api.github.com"
gh_session = requests.Session()
gh_session.auth = (config.GITHUB_USERNAME, config.GITHUB_TOKEN)


def commits_of_repo_github(repo, owner, api):
    commits = []
    next = True
    i = 1
    while next == True:
        url = api + '/repos/{}/{}/commits?page={}&per_page=100'.format(owner, repo, i)
        commit_pg = gh_session.get(url = url)
        # print('------------------')
        # print(commit_pg.headers)
        # print('------------------')
        commit_pg_list = [dict(item, **{'repo_name':'{}'.format(repo)}) for item in commit_pg.json()]    
        commit_pg_list = [dict(item, **{'owner':'{}'.format(owner)}) for item in commit_pg_list]
        commits = commits + commit_pg_list
        if 'Link' in commit_pg.headers:
            if 'rel="next"' not in commit_pg.headers['Link']:
                next = False
        i = i + 1
    return commits

def create_commits_df(repo, owner, api):
    commits_list = commits_of_repo_github(repo, owner, api)
    return json_normalize(commits_list)

commits = create_commits_df('chatApp-Param', 'parambhatia2004', github_api)
# pd.set_option('display.max_columns', None)
# print(commits.info())
#I want to see all columns


commits['date'] =  pd.to_datetime(commits['commit.committer.date'])
commits['date'] =  pd.to_datetime(commits['date'], utc=True)
commits['commit_date'] = commits['date'].dt.date
commits['commit_year'] = commits['date'].dt.year
commits['commit_hour'] = commits['date'].dt.hour

print(commits['author.login'].unique().size)
commits_by_hour = commits.groupby('commit_hour')[['sha']].count()
commits_by_hour = commits_by_hour.rename(columns = {'sha': 'commit_count'})

import chart_studio.plotly as py
import plotly.graph_objs as go
from plotly.offline import init_notebook_mode, plot, iplot
init_notebook_mode(connected=True)