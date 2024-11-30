from jira import JIRA
# from jira.client import ResultList
# from jira.resources import Issue

class JiraClient():
    def __new__(self, server, email, api_token):
        return JIRA(
            server = (f"https://{server}"),
            basic_auth = (email, api_token)
        )
