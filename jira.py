import http
import json
import re

class JiraRestApi(object):

	# base_url = .../jira/rest
	def __init__(self, base_url):
		self._base_url = base_url
		# also tells if this instance is authenticated
		self._auth_cookies = None

		self.http = http.Http(
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

JiraRestApi._CURL_VERBOSE = False



class Issue(object):

	def __init__(self, raw_obj):
		fields = raw_obj["fields"]
		self._key = raw_obj["key"].encode("utf8")
		self._status = fields["status"]["name"].encode("utf8")
		self._summary = fields["summary"].encode("utf8")

	def __str__(self):
		return "%s [%s] %s" % (self._key, self._status, self._summary)


class Jira(JiraRestApi):

	def search(self, jql, max_results=10, fields=["summary", "status"]):
		result = super(Jira, self).search(jql, max_results, fields)

		print "### " + json.dumps(str(result))

		items = []

		for item in result["issues"]:
			items.append(Issue(item))

		return items


	def get(self, key):
		return Issue(super(Jira, self).get(key))
