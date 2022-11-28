import requests
import json
from requests.auth import HTTPBasicAuth
import pandas as pd

headers = {'Content-Type':'application/json'}
# username is purposely blank
username = ''
# this is the personal access token assigned to your user id
password = jj_ado_pat = ''
auth = HTTPBasicAuth(username, password)

org = ''
project = ''

total_records = 0
prReviews = []
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

with open("C:\\users\\yjw0120\\desktop\\prReviews.json", "w") as outfile:
    outfile.write(json_object)
