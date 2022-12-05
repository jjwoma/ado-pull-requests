import requests
import json
from requests.auth import HTTPBasicAuth
import pandas as pd

headers = {'Content-Type':'application/json'}
# username is purposely blank per ADO's auth scheme, leave it blank
username = ''
# this is the personal access token assigned to your user id, fill this one out
password = jj_ado_pat = ''
auth = HTTPBasicAuth(username, password)

# populate your organizations name here (dev.azure.com/<org name>)
org = ''

# this part gets all the project ID's associated with org.  only tested with org that has 60ish projects, so there might be a real limit above that which ADO is imposing on this query
project_api_url = f"https://dev.azure.com/{org}/_apis/projects?top=10000&api-version=6.0"
proj_array = []
prj_req = requests.get(project_api_url,auth=auth,headers=headers)
for item in prj_req.json()['value']:
    proj_array.append(item['name'])

# with the project array from above, loop through each one and build up prReview array
prReviews = []
for project in proj_array:

    total_records = 0
    
    page_size = 500
    skip = 0
    page = 0
    result = {"value":["init"]}

    voteMap = {
        -10: "rejected",
        -5:  "waiting for author",
        0:   "no vote",
        5:   "approved with suggestions",
        10:  "approved"
    }

    while len(result['value']) > 0:

        url = f"https://dev.azure.com/{org}/{project}/_apis/git/pullrequests?api-version=7.1-preview.1&$top={page_size}&$skip={skip}&searchCriteria.status={'all'}"
        skip += page_size
        r = requests.get(url,auth=auth,headers=headers)
        if r.status_code == 200:
            result = r.json()
        
        else:
            break
        
        for item in result['value']:
            for idx, x in enumerate(item['reviewers']):
                prReviews.append({
                    "reviewerName":  item['reviewers'][idx]['displayName'],
                    "reviewerEmail": item['reviewers'][idx]['uniqueName'],
                    "rewiewerVote":  voteMap[item['reviewers'][idx]['vote']],
                    "project":       project,
                    "repo":          item['repository']['name'],
                    "pullRequestId": item['pullRequestId'],
                    "createdBy":     item['createdBy']['displayName'],
                    "creationDate" : item['creationDate'],
                    "title":         item['title'],
                    "sourceBranch":  item['sourceRefName'],
                    "targetBranch":  item['targetRefName'],
                })
            
# Serializing json
json_object = json.dumps(prReviews, indent=4)

with open("C:\\users\\jjw\\desktop\\prReviews.json", "w") as outfile:
    outfile.write(json_object)
