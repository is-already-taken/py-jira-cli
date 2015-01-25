import http
import json
import re
import dateutil.parser
import time

class JiraRestApi(object):

	# base_url = .../jira/rest
	def __init__(self, base_url, user_agent_prefix="PyJira"):
		self._base_url = base_url
		# also tells if this instance is authenticated
		self._auth_cookies = None

		self.http = http.Http(
			user_agent_prefix=user_agent_prefix,
			_curl_verbose=JiraRestApi._CURL_VERBOSE)

	def close(self):
		self.http.close()

	# get the auth cookies of a previous login()
	def get_auth_cookies(self):
		return self._auth_cookies

	# check auth by passed session cookies and
	# internally set the auth cookies
	def check_auth(self, auth_cookies):
		call = "/auth/1/session"

		(status, res, _cookies) = self.http.get(
			self._base_url + call,
			cookies=auth_cookies)

		if status == 401:
			return False

		self._auth_cookies = auth_cookies

		return True

	# login with username and password and internally set
	# the session cookies that can be returned with
	# get_auth_cookies() for use with relogin
	# using check_auth()
	def login(self, username, password):
		call = "/gadget/1.0/login"

		(status, res, cookies) = self.http.post(
			self._base_url + call, {
				"os_username": username,
				"os_password": password,
				"os_cookie": "true"
			})

		login_json = json.loads(res)

		successful = "loginSucceeded" in login_json and login_json["loginSucceeded"]

		auth_cookies = []

		if not successful:
			return False

		for cookie in cookies:
			# match both cookie names and value (everything thats not ";")
			match = re.match("^(JSESSIONID|crowd\.token_key)=([^;]+);?.*$", cookie)

			if match:
				# ignore this cooke with an empty value (really happened)
				if match.group(2) == "\"\"":
					continue

				auth_cookies.append(match.group(1) + "=" + match.group(2))

		self._auth_cookies = auth_cookies

		return True


	def search(self, jql, max_results=10, fields=["summary", "status"]):
		if self._auth_cookies == None:
			raise Exception("Not authenticated")

		req_json_str = json.dumps({
			"jql": jql,
			"fields": fields,
			"maxResults": max_results
		})

		call = "/api/2/search"

		(status, res, _cookies) = self.http.post(
			self._base_url + call,
			req_json_str,
			headers=["Content-Type: application/json"],
			cookies=self._auth_cookies)

		if status != 200:
			raise Exception("Non 200 (%d) for %s: %s" % (status, call, str(res)))

		return json.loads(res, "utf8")

	def get(self, key):
		if self._auth_cookies == None:
			raise Exception("Not authenticated")

		call = "/api/2/issue/%s" % (key)

		(status, res, _cookies) = self.http.get(
			self._base_url + call,
			headers=["Content-Type: application/json"],
			cookies=self._auth_cookies)

		if status != 200:
			raise Exception("Non 200 (%d) for %s: %s" % (status, call, str(res)))

		return json.loads(res, "utf8")

	def get_comments(self, key):
		if self._auth_cookies == None:
			raise Exception("Not authenticated")

		call = "/api/2/issue/%s/comment" % (key)

		(status, res, _cookies) = self.http.get(
			self._base_url + call,
			headers=["Content-Type: application/json"],
			cookies=self._auth_cookies)

		if status != 200:
			raise Exception("Non 200 (%d) for %s: %s" % (status, call, str(res)))

		return json.loads(res, "utf8")


	def add_comment(self, key, comment):
		if self._auth_cookies == None:
			raise Exception("Not authenticated")

		req_json_str = json.dumps({
			"body": comment
		})

		call = "/api/2/issue/%s/comment" % (key)

		(status, res, _cookies) = self.http.post(
			self._base_url + call,
			req_json_str,
			headers=["Content-Type: application/json"],
			cookies=self._auth_cookies)

		if status != 201:
			raise Exception("Non 201 (%d) for %s: %s" % (status, call, str(res)))

		return json.loads(res, "utf8")


	def assign(self, key, assignee):
		if self._auth_cookies == None:
			raise Exception("Not authenticated")

		req_json_str = json.dumps({
			"name": assignee
		})

		call = "/api/2/issue/%s/assignee" % (key)

		(status, res, _cookies) = self.http.put(
			self._base_url + call,
			req_json_str,
			headers=["Content-Type: application/json"],
			cookies=self._auth_cookies)

		if status != 204:
			raise Exception("Non 204 (%d) for %s: %s" % (status, call, str(res)))

	def get_assignees(self, username_fragment):
		if self._auth_cookies == None:
			raise Exception("Not authenticated")

		call = "/api/2/user/search?username=%s" % (username_fragment)

		(status, res, _cookies) = self.http.get(
			self._base_url + call,
			headers=["Content-Type: application/json"],
			cookies=self._auth_cookies)

		if status != 200:
			raise Exception("Non 200 (%d) for %s: %s" % (status, call, str(res)))

		return json.loads(res, "utf8")


JiraRestApi._CURL_VERBOSE = False


class BasicIssue(object):

	def __init__(self, raw_obj):
		fields = raw_obj["fields"]
		self._key = raw_obj["key"].encode("utf8")
		self._summary = fields["summary"].encode("utf8")
		self._status = fields["status"]["name"].encode("utf8")
		self._type = fields["issuetype"]["name"].encode("utf8")

	def __str__(self):
		return  "%s [%s] %s" % (self._key, self._status, self._summary)

class Issue(BasicIssue):

	def __init__(self, raw_obj):
		fields = raw_obj["fields"]
		self._key = raw_obj["key"].encode("utf8")
		self._summary = fields["summary"].encode("utf8")
		self._status = fields["status"]["name"].encode("utf8")
		self._description = fields["description"].encode("utf8")
		self._type = fields["issuetype"]["name"].encode("utf8")

		if fields["assignee"] != None:
			self._assignee = fields["assignee"]["displayName"].encode("utf8")
		else:
			self._assignee = None

		_updated = fields["updated"]
		self._updated = time.mktime(dateutil.parser.parse(_updated).timetuple())

		if "parent" in fields and fields["parent"] != None:
			self._parent = BasicIssue(fields["parent"])
		else:
			self._parent = None

		if "subtasks" in fields and fields["subtasks"] != None:
			_subtasks = fields["subtasks"]
			_subtasks = map(lambda issue: BasicIssue(issue), _subtasks)
			self._subtasks = _subtasks
		else:
			self._subtasks = []



	def __str__(self):
		str_ =  "%s [%s] %s" % (self._key, self._status, self._summary)

		if self._parent != None:
			str_ += " ^" + self._parent._key

		if len(self._subtasks) != 0:
			str_ += " [%d Subtasks]" % (len(self._subtasks))

		if self._assignee != None:
			str_ += " @" + self._assignee

		return str_

class Comment(object):
	def __init__(self, raw_obj):
		self._body = raw_obj["body"]

		_created = raw_obj["created"]

		self._created = time.mktime(dateutil.parser.parse(_created).timetuple())

	def __str__(self):
		return "--- %d -------------------\n%s" % (self._created, self._body)

class User(object):
	def __init__(self, raw_obj):
		self._key = raw_obj["key"].encode("utf8")
		self._display_name = raw_obj["displayName"].encode("utf8")
		self._email = raw_obj["emailAddress"].encode("utf8")

	def __str__(self):
		return "%s %s (%s)" % (self._key.ljust(20), self._display_name, self._email)


class Jira(object):

	def __init__(self, base_url, user_agent_prefix="PyJira"):
		self.jira_api = JiraRestApi(base_url, user_agent_prefix=user_agent_prefix)


	def close(self):
		self.jira_api.close()


	# get the auth cookies of a previous login()
	def get_auth_cookies(self):
		return self.jira_api.get_auth_cookies()


	# check auth by passed session cookies and
	# internally set the auth cookies
	def check_auth(self, auth_cookies):
		return self.jira_api.check_auth(auth_cookies)


	# login
	def login(self, username, password):
		return self.jira_api.login(username, password)


	def search(self, jql, max_results=10, fields=["summary", "description", "assignee", "status", "issuetype", "updated", "parent", "subtasks"]):
		# fields: summary, description, issuetype, assignee, status, issuetype, updated, parent, subtasks#key, project, reporter, created

		result = self.jira_api.search(jql, max_results, fields)

		issues = result["issues"]

		items = []

		for item in issues:
			items.append(Issue(item))

		remaining = result["total"] - len(issues)

		return (items, remaining, result["maxResults"])


	def get(self, key):
		return Issue(self.jira_api.get(key))

	def get_comments(self, key):
		comments = self.jira_api.get_comments(key)
		comments = comments["comments"]

		return map(lambda comment: Comment(comment), comments)

	def add_comment(self, key, comment):
		self.jira_api.add_comment(key, comment)

	def assign(self, key, assignee):
		self.jira_api.assign(key, assignee)

	def unassign(self, key):
		self.jira_api.assign(key, None)

	def get_assignees(self, username_fragment):
		users = self.jira_api.get_assignees(username_fragment)

		return map(lambda user: User(user), users)
