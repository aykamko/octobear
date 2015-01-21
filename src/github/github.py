import base64
import json
import requests
import logging
import re
from requests import get as GET, post as POST, delete as DELETE, put as PUT
from .. import config

class GitHubApiError(Exception):
    pass

class GitHub:

    def __init__(self, orgName, ownername, password):
        self.logger = logging.getLogger('GitHub')
        self.ownername = ownername
        self.password = password
        self.orgName = orgName

    def callApi(self, requestType, endpoint, followLink=False, **kwargs):
        url = "https://api.github.com/%s" % (endpoint)
        authPair = base64.b64encode("%s:%s" % (self.ownername, self.password))
        headers = {
                "Authorization": "Basic %s" % (authPair),
                }

        # Support for additional headers in kwargs. (Can override Authorization)
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
        kwargs['headers'] = headers

        responses = []
        while True:
            response = requestType(url, **kwargs)
            if response.ok:
                responses.append(response)
                if followLink and "next" in response.links:
                    url = response.links["next"]['url']
                else:
                    return responses
            else:
                raise GitHubApiError(response.content)

    def parseJson(self, response):
        try:
            return response.json()
        except ValueError:
            raise GitHubApiError("Invalid JSON in response: %s" % (response.content))

    # Sanity check to make sure functions are being used correctly
    def checkNumeric(self, number):
        if type(number) not in (int, str) or not str(number).isdigit():
            raise ValueError("Sanity check: %s should be an ID" % (number))

    # Usernames are untrusted user input, so check 'em
    def checkUsername(self, username):
        if not isinstance(username, basestring) or \
                re.match(r"[a-zA-Z0-9][a-zA-Z0-9\-]*$", username) is None:
            raise GitHubApiError("Invalid GitHub username: %s" % (username))

    def getTeamIDsByName(self):
        teamIDsByName = {}
        endpoint = "orgs/%s/teams" % (self.orgName)
        responses = self.callApi(GET, endpoint, followLink=True)
        for response in responses:
            teams = self.parseJson(response)
            for team in teams:
                teamName = team["name"]
                teamID = team["id"]
                teamIDsByName[teamName] = str(teamID)
        return teamIDsByName

    # Gets members of a team
    def getTeamMembers(self, teamID):
        self.checkNumeric(teamID)
        endpoint = "teams/%s/members" % (teamID)
        responses = self.callApi(GET, endpoint, followLink=True)

        usernames = []
        for response in responses:
            members = self.parseJson(response)
            usernames.extend([member["login"] for member in members])

        return usernames

    # Lists hooks for a repo (for debugging only)
    def listHooks(self, repoName):
        endpoint = "repos/%s/%s/hooks" % (self.orgName, repoName)
        responses = self.callApi(GET, endpoint, followLink=True)
        for response in responses:
            for hook in self.parseJson(response):
                print repoName, json.dumps(hook, indent=4, sort_keys=True)

    # Gets email of a user
    def getEmail(self, username):
        self.checkUsername(username)
        endpoint = "users/%s" % (username)
        response, = self.callApi(GET, endpoint)

        try:
            return self.parseJson(response)["email"]
        except (TypeError, KeyError) as e:
            raise GitHubApiError(e.message)

    def getTeamID(self, teamName):
        teamIDsByName = self.getTeamIDsByName()
        return teamIDsByName[teamName]

    # Delete a repo. Does not delete teams or users.
    def deleteRepo(self, repoName):
        endpoint = "repos/%s/%s" % (self.orgName, repoName)
        self.callApi(DELETE, endpoint)

    # Deletes a team. Make sure to remove the members first, and then the team!
    def deleteTeam(self, teamID):
        endpoint = "teams/%s" % (teamID)
        self.callApi(DELETE, endpoint)

    # Deletes a member from the organization
    def deleteMember(self, username):
        endpoint = "orgs/%s/members/%s" % (self.orgName, username)
        self.callApi(DELETE, endpoint)

    # Delete a repo, team, and members from the organization
    def deleteRepoAndTeamAndMembers(self, repoName, teamName=None):
        if teamName is None:
            teamName = repoName
        self.deleteRepo(repoName)
        teamID = self.getTeamID(teamName)
        for username in self.getTeamMembers(teamID):
            self.deleteMember(username)
        self.deleteTeam(teamID)

    # Creates a repo
    def createRepo(self, repoName):
        postData = {
                "name": repoName,
                "private": True
                }
        endpoint = "orgs/%s/repos" % (self.orgName)
        response, = self.callApi(POST, endpoint, json=postData)

        try:
            return self.parseJson(response)["id"]
        except (TypeError, KeyError) as e:
            raise GitHubApiError(e.message)

    # Creates a team
    def createTeam(self, repoName, teamName=None):
        if teamName == None:
            teamName = repoName
        postData = {
            "name": teamName,
            "repo_names": ["%s/%s" % (self.orgName, repoName)],
            "permission": "push",
            }
        endpoint = "orgs/%s/teams" % (self.orgName)
        response, = self.callApi(POST, endpoint, json=postData)

        try:
            return self.parseJson(response)["id"]
        except (TypeError, KeyError) as e:
            raise GitHubApiError(e.message)

    # Adds team members
    def addTeamMembers(self, teamID, members):
        self.checkNumeric(teamID)
        map(self.checkUsername, members)
        for member in members:
            endpoint = "teams/%s/memberships/%s" % (teamID, member)
            self.callApi(PUT, endpoint)

    # Adds the jenkins hook to the repo
    def createHook(self, repoName, jenkinsHookURL):
        postData = {
                "name": "jenkins",
                "config": {"url": jenkinsHookURL},
                "events": ["push"],
                }
        endpoint = "repos/%s/%s/hooks" % (self.orgName, repoName)
        self.callApi(POST, endpoint, json=postData)

    # Creates everything -> a repo, a teamname (same as the repo unless otherwise specified), adds team members, and adds the jenkins hook
    def createEverything(self, repoName, members, hook, teamName=None):
        if teamName == None:
            teamName = repoName

        repoID = self.createRepo(repoName)
        teamID = self.createTeam(teamName)

        self.addTeamMembers(teamID, members)
        self.createHook(repoName, hook)

# disable logging for requests module
logging.getLogger('requests').setLevel(logging.WARNING)
github = GitHub(config['gh_organization'], config['gh_user'], config['gh_pass'])
