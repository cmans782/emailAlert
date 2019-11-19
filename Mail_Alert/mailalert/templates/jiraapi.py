# This code sample uses the 'requests' library:
# http://docs.python-requests.org
import requests
from requests.auth import HTTPBasicAuth
import json

url = "/rest/api/2/issue"

auth = HTTPBasicAuth("corey2232@gmail.com", "aqspGiDAokDGYkhkLYciAC11")

headers = {
   "Accept": "application/json",
   "Content-Type": "application/json"
}

payload = json.dumps( {
  "update": {
    "worklog": [
      {
        "add": {
          "timeSpent": "60m",
          "started": "2019-07-05T11:05:00.000+0000"
        }
      }
    ]
  },
  "fields": {
    "summary": "Main order flow broken",
    "parent": {
      "key": "PROJ-123"
    },
    "issuetype": {
      "id": "10000"
    },
    "components": [
      {
        "id": "10000"
      }
    ],
    "customfield_20000": "06/Jul/19 3:25 PM",
    "customfield_40000": "Occurs on all orders",
    "customfield_70000": [
      "jira-administrators",
      "jira-software-users"
    ],
    "project": {
      "id": "10000"
    },
    "description": "Order entry fails when selecting supplier.",
    "reporter": {
      "id": "5b10a2844c20165700ede21g"
    },
    "fixVersions": [
      {
        "id": "10001"
      }
    ],
    "customfield_10000": "09/Jun/19",
    "priority": {
      "id": "20000"
    },
    "labels": [
      "bugfix",
      "blitz_test"
    ],
    "timetracking": {
      "remainingEstimate": "5",
      "originalEstimate": "10"
    },
    "customfield_30000": [
      "10000",
      "10002"
    ],
    "customfield_80000": {
      "value": "red"
    },
    "security": {
      "id": "10000"
    },
    "environment": "UAT",
    "versions": [
      {
        "id": "10000"
      }
    ],
    "duedate": "2019-03-11T00:00:00.000Z",
    "customfield_60000": "jira-software-users",
    "customfield_50000": "Could impact day-to-day work.",
    "assignee": {
      "id": "5b109f2e9729b51b54dc274d"
    }
  }
} )

response = requests.request(
   "POST",
   url,
   data=payload,
   headers=headers,
   auth=auth
)

print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))