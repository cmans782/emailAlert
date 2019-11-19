from jira import JIRA

def main():

   options = {'server': mailalert.atlassian.net}
   jira = JIRA(options, basic_auth=('corey2232@gmail.com', 'Gotitbsitw13'))
   issue = jira.issue('ESS-138581')

   print issue.fields.project.key
   print issue.fields.issuetype.name
   print issue.fields.reporter.displayName
   print issue.fields.summary
   print issue.fields.project.id


if __name__== "__main__" :
     main()