import base64
import json
import requests
import logging
from requests import get as GET

class GitHubApiError(Exception):
    pass

class GitHub:

    def __init__(self, orgName, ownername, password):
        self.logger = logging.getLogger('GitHub')
        self.ownername = ownername
        self.password = password
        self.orgName = orgName
        self.repos = []       # contains the names of all repos
        self.teams = {}       # contains the names and ids of all teams
        self.teamMembers = {} # contains teams -> users mapping
        self.loadRepos()
        self.getTeams()

    def callApi(self, requestType, endpoint, followLink=False, data=None,
            json=None, **kwargs):
        url = "https://api.github.com/%s" % (endpoint)
        authPair = base64.b64encode("%s:%s" % (self.ownername, self.password))
        authHeaders = {
                "Authorization": "Basic %s" % (authPair),
                }

        responses = []
        while True:
            response = requestType(url, headers=authHeaders, data=data, json=json)
            if response.ok:
                responses.append(response)
                if followLink and "next" in response.links:
                    url = response.links["next"]
                else:
                    return responses
            else:
                raise GitHubApiError(response.content)

    def parseJson(self, payload):
        try:
            return json.loads(payload)
        except ValueError:
            raise GitHubApiError("Invalid JSON in response: %s" % (payload))

    # Loads all repos under course organization
    def loadRepos(self):
        self.repos = []
        endpoint = "orgs/%s/repos" % (self.orgName)
        responses = self.callApi(GET, endpoint, followLink=True)
        for response in responses:
            repos = self.parseJson(response.content)
            self.repos.extend(map(lambda repo: repo["name"], repos))

    # Gets all teams under course organization
    def getTeams(self):
        self.teams = {}
        self.teamMembers = {}
        url = "https://api.github.com/orgs/{org}/teams".format(
            org = self.orgName
            )
        base64string = base64.encodestring('%s:%s' % (self.ownername, self.password)).replace('\n', '')
        reqHeaders = { "Authorization": "Basic %s" % base64string }
        response = requests.get(url, headers = reqHeaders)
        resultsJson = json.loads(response.content)
        headers = response.headers
        for t in resultsJson:
            self.teams[t["name"]] = str(t["id"])
            self.getTeamMembers(t["name"])

        # Pagination
        if "Link" in headers:
            while "last" in headers["Link"]:
                url = headers["Link"].strip().split(';')[0].strip()[1:-1]
                response = requests.get(url, headers = reqHeaders)
                resultsJson = json.loads(result.content)
                headers = result.headers
                for t in resultsJson:
                    self.teams[t["name"]] =  str(t["id"] )
                    self.getTeamMembers(t["name"])

        return (self.teams, self.teamMembers)

    # Gets all team members in course organization
    def getTeamMembers(self, teamName):
        teamID = self.teams[teamName]
        self.teamMembers[teamID] = []
        url = "https://api.github.com/teams/{team}/members".format(
            team = teamID
            )
        base64string = base64.encodestring('%s:%s' % (self.ownername, self.password)).replace('\n', '')
        reqHeaders = { "Authorization": "Basic %s" % base64string }
        response = requests.get(url, headers = reqHeaders)
        resultsJson = json.loads(response.content)
        headers = response.headers
        for t in resultsJson:
            self.teamMembers[teamID].append(t["login"])

        # Pagination
        if "Link" in headers:
            while "last" in headers["Link"]:
                url = headers["Link"].strip().split(';')[0].strip()[1:-1]
                response = requests.get(url, headers = reqHeaders)
                resultsJson = json.loads(result.content)
                headers = result.headers
                for t in resultsJson:
                    self.teamMembers[teamID].append(t["login"])

        return self.teamMembers[teamID]

    # lists hooks for a repo
    def listHooks(self, repoName):
        try:
            url = "https://api.github.com/repos/{org}/{repo}/hooks".format(
                org = self.orgName,
                repo = repoName
                )
            base64string = base64.encodestring('%s:%s' % (self.ownername, self.password)).replace('\n', '')
            reqHeaders = { "Authorization": "Basic %s" % base64string }
            response = requests.get(url, headers = reqHeaders)
            resultsJson = json.loads(response.content)
            for hook in resultsJson:
                print repoName, json.dumps(hook, indent=4, sort_keys=True)
        except Exception as e:
            self.logger.exception(e)

    # gets email of a user
    def getEmail(self, username):
        try:
            url = "https://api.github.com/users/{user}".format(
                user = username
                )
            base64string = base64.encodestring('%s:%s' % (self.ownername, self.password)).replace('\n', '')
            reqHeaders = { "Authorization": "Basic %s" % base64string }
            response = requests.get(url, headers = reqHeaders)
            resultsJson = json.loads(response.content)
            return resultsJson["email"]
        except Exception as e:
            self.logger.exception(e)

    # Delete a repo. Does not delete teams or users.
    def deleteRepo(self, repoName):
        try:
            self.repos = []
            url = "https://api.github.com/repos/{org}/{repo}".format(
                org = self.orgName,
                repo = repoName
                )
            base64string = base64.encodestring('%s:%s' % (self.ownername, self.password)).replace('\n', '')
            reqHeaders = { "Authorization": "Basic %s" % base64string }
            response = requests.delete(url, headers = reqHeaders)
            return 0 if response.ok else -1
        except Exception as e:
            self.logger.exception(e)
            return -1

    # Deletes a team. To remove all members as well as a team, remove the members first, and then the team
    def deleteTeam(self, teamName):
        if teamName not in self.teams:
            return -2
        teamID = self.teams[teamName]
        try:
            url = "https://api.github.com/teams/{team}".format(
                team = teamID
                )
            base64string = base64.encodestring('%s:%s' % (self.ownername, self.password)).replace('\n', '')
            reqHeaders = { "Authorization": "Basic %s" % base64string }
            response = requests.delete(url, headers = reqHeaders)
            return 0 if response.ok else -1
        except Exception as e:
            self.logger.exception(e)
            return -1

    # Deletes a member from the organization
    def deleteMember(self, memberID):
        try:
            self.repos = []
            url = "https://api.github.com/orgs/{org}/members/{member}".format(
                org = self.orgName,
                member = memberID
                )
            base64string = base64.encodestring('%s:%s' % (self.ownername, self.password)).replace('\n', '')
            reqHeaders = { "Authorization": "Basic %s" % base64string }
            response = requests.delete(url, headers = reqHeaders)
            return 0 if response.ok else -1
        except Exception as e:
            self.logger.exception(e)
            return -1

    # Delete a repo, team and members from the organization
    # Note this also deletes a member from an organization
    def deleteRepoAndTeamAndMembers(self, repoName, teamName=None):
        if teamName == None:
            teamName = repoName
        self.deleteRepo(repoName)
        teamID = self.teams[repoName]
        for member in self.teamMembers[teamID]:
            self.deleteMember(member)
        self.deleteTeam(teamName)

    # Creates a repo
    def createRepo(self, repoName):
        try:
            postData = {
                "name": repoName,
                "private": True
                }
            url = "https://api.github.com/orgs/{org}/repos".format(
                org = self.orgName
                )
            base64string = base64.encodestring('%s:%s' % (self.ownername, self.password)).replace('\n', '')
            reqHeaders = { "Authorization": "Basic %s" % base64string }
            response = requests.post(url, data = json.dumps(postData), headers = reqHeaders)
            if response.ok:
                self.repos.append(repoName)
                return 0
            else:
                return -1
        except Exception as e:
            self.logger.exception(e)
            return -1

    # Creates a team
    def createTeam(self, repoName, teamName=None):
        if teamName == None:
            teamName = repoName
        try:
            postData = {
                "name": teamName,
                "repo_names": [self.orgName + "/" + repoName],
                "permission": "push"
                }
            url = "https://api.github.com/orgs/{org}/teams".format(
                org = self.orgName
                )
            base64string = base64.encodestring('%s:%s' % (self.ownername, self.password)).replace('\n', '')
            reqHeaders = { "Authorization": "Basic %s" % base64string }
            response = requests.post(url, data = json.dumps(postData), headers = reqHeaders)
            if response.ok:
                resultsJson = json.loads(response.content)
                self.teams[resultsJson["name"]] = str(resultsJson["id"])
                return 0
            else:
                import pdb; pdb.set_trace()
                return -1
        except Exception as e:
            self.logger.exception(e)
            return -1

    # Adds team members
    def addTeamMembers(self, teamName, members):
        teamID = self.teams[teamName]
        if teamID not in self.teamMembers:
            self.teamMembers[teamID] = []
        try:
            for member in members:
                member = member.strip()
                url = "https://api.github.com/teams/{team}/memberships/{member}".format(
                    team = teamID,
                    member = member
                    )
                base64string = base64.encodestring('%s:%s' % (self.ownername, self.password)).replace('\n', '')
                reqHeaders = {
                    "Authorization": "Basic %s" % base64string,
                    "Accept": "application/vnd.github.the-wasp-preview+json"
                    }
                response = requests.put(url, headers = reqHeaders)
                if response.ok:
                    self.teamMembers[teamID].append(str(member.strip()))
                else:
                    return -1
        except Exception as e:
            self.logger.exception(e)
            return -1
        return 0

    # Adds the jenkins hook to the repo
    def createHook(self, repoName, jenkinsHookURL):
        try:
            jenkinsHook = {
                "name": "jenkins",
                "config": {"url": jenkinsHookURL},
                "events": ["push"]
                }
            url = "https://api.github.com/repos/{org}/{repo}/hooks".format(
                org = self.orgName,
                repo = repoName
                )
            base64string = base64.encodestring('%s:%s' % (self.ownername, self.password)).replace('\n', '')
            reqHeaders = { "Authorization": "Basic %s" % base64string }
            response = requests.post(url, data = json.dumps(jenkinsHook), headers = reqHeaders)
            return 0 if response.ok else -1
        except Exception as e:
            self.logger.exception(e)

    # Creates everything -> a repo, a teamname (same as the repo unless otherwise specified), adds team members, and adds the jenkins hook
    def createEverything(self, repoName, members, hook, teamName=None):
        if teamName == None:
            teamName = repoName

        ret = self.createRepo(repoName)
        if ret != 0:
            self.logger.debug('Could not create repo: {0}'.format(repoName))
            return -1
        self.logger.debug('Created repo: {0}'.format(repoName))

        ret = self.createTeam(teamName)
        if ret != 0:
            self.logger.debug('Could not team: {0}'.format(teamName))
            return -1
        self.logger.debug('Created team: {0}'.format(teamName))

        ret = self.addTeamMembers(teamName, members)
        if ret != 0:
            self.logger.debug('Could not add team members: {0}'.format(members))
            return -1
        self.logger.debug('Added team members: {0}'.format(members))

        ret = self.createHook(repoName, hook)
        if ret != 0:
            self.logger.debug('Could not add hook: {0}'.format(hook))
            return -1
        self.logger.debug('Added hook: {0}'.format(hook))

        return 0

# disable logging for requests module
logging.getLogger('requests').setLevel(logging.WARNING)
