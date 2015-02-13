
import unittest
from mock import patch, Mock, MagicMock
import fudge
import json
import jira

class JiraRestApiTest(unittest.TestCase):

	@fudge.patch("http.Http")
	def test_init_with_no_ua(self, Http_Mock):
		(Http_Mock.expects_call()
					.with_args(_curl_verbose=False, user_agent_prefix="PyJira", proxy=None)
					.returns_fake())

		jira.JiraRestApi("http://host/base")


	@fudge.patch("http.Http")
	def test_init_with_ua(self, Http_Mock):
		(Http_Mock.expects_call()
					.with_args(_curl_verbose=False, user_agent_prefix="PyJira", proxy=None)
					.returns_fake())

		jira.JiraRestApi("http://host/base")


	@fudge.patch("http.Http")
	def test_init_with_proxy(self, Http_Mock):
		(Http_Mock.expects_call()
					.with_args(_curl_verbose=False, user_agent_prefix="PyJira", proxy="socks://1.2.3.4:6789")
					.returns_fake())

		jira.JiraRestApi("http://host/base", proxy="socks://1.2.3.4:6789")


	@fudge.patch("http.Http")
	def test_close(self, Http_Mock):
		(Http_Mock.expects_call()
					.with_args(_curl_verbose=False, user_agent_prefix="Custom", proxy=None)
					.returns_fake()
					.expects('close'))

		api = jira.JiraRestApi("http://host/base", user_agent_prefix="Custom")
		api.close()


	@fudge.patch("http.Http")
	def test_get_auth_cookies_uninitialized(self, Http_Mock):
		(Http_Mock.expects_call()
					.with_args(_curl_verbose=False, user_agent_prefix="Custom", proxy=None)
					.returns_fake())

		api = jira.JiraRestApi("http://host/base", user_agent_prefix="Custom")

		assert api.get_auth_cookies() == None


	@fudge.patch("http.Http")
	def test_check_auth_successfully_authorized(self, Http_Mock):
		(Http_Mock.expects_call()
					.with_args(_curl_verbose=False, user_agent_prefix="PyJira", proxy=None)
					.returns_fake()
					.expects('get')
						.with_args("http://host/base/auth/1/session", cookies=["A", "B"])
						.returns( (200, "", ["a", "b"]) ))

		api = jira.JiraRestApi("http://host/base")

		# Return True on success
		assert api.check_auth(["A", "B"]) == True

		# Update the cookies sent from server
		assert api.get_auth_cookies() == ["A", "B"]


	@fudge.patch("http.Http")
	def test_check_auth_not_authorized(self, Http_Mock):
		(Http_Mock.expects_call()
					.with_args(_curl_verbose=False, user_agent_prefix="PyJira", proxy=None)
					.returns_fake()
					.provides('get')
						.with_args("http://host/base/auth/1/session", cookies=["A", "B"])
						.returns( (401, "", ["x", "y"]) ))

		api = jira.JiraRestApi("http://host/base")

		# Return True on success
		assert api.check_auth(["A", "B"]) == False

		# Return None cookies
		assert api.get_auth_cookies() == None


	@fudge.patch("http.Http")
	def test_login_sucessful(self, Http_Mock):
		request_form_json = {
			"os_username": "VALIDUSER",
			"os_password": "VALIDPASSWORD",
			"os_cookie": "true"
		}

		response_json_str = json.dumps({
			"loginSucceeded": True
		})

		response_cookies = [
			"JSESSIONID=1234; XXX",
			"crowd.token_key=ABCDE; YYY"
		]

		(Http_Mock.expects_call()
					.with_args(_curl_verbose=False, user_agent_prefix="PyJira", proxy=None)
					.returns_fake()
					.expects('post')
						.with_args("http://host/base/gadget/1.0/login", request_form_json)
						.returns( (200, response_json_str, response_cookies) ))



		api = jira.JiraRestApi("http://host/base")

		# Return True on success
		assert api.login("VALIDUSER", "VALIDPASSWORD") == True

		# Return new cookies
		assert api.get_auth_cookies() == ["JSESSIONID=1234", "crowd.token_key=ABCDE"]


	@fudge.patch("http.Http")
	def test_myself_unauthorized(self, Http_Mock):
		(Http_Mock.expects_call()
					.with_args(_curl_verbose=False, user_agent_prefix="PyJira", proxy=None)
					.returns_fake()
					.provides('get')
						.with_args(
							"http://host/base/api/2/myself",
							headers=["Content-Type: application/json"],
							cookies=["A", "B"])
						.returns( (111, "", []) ))

		api = jira.JiraRestApi("http://host/base")

		self.assertRaises(jira.JiraAuthException, api.myself)


	@fudge.patch("http.Http")
	def test_myself_successful(self, Http_Mock):
		response_json_str = json.dumps({
			"response": "json",
			"of": "myself"
		})

		(Http_Mock.expects_call()
					.with_args(_curl_verbose=False, user_agent_prefix="PyJira", proxy=None)
					.returns_fake()
					.expects('get')
						.with_args(
							"http://host/base/api/2/myself",
							headers=["Content-Type: application/json"],
							cookies=["A", "B"])
						.returns( (200, response_json_str, []) ))

		api = jira.JiraRestApi("http://host/base")

		# bypass authorization check
		# TODO find a way to easily "dummy check" auth here
		api._auth_cookies = ["A", "B"]

		assert api.myself() == {
			"response": "json",
			"of": "myself"
		}


	@fudge.patch("http.Http")
	def test_myself_unsuccessful(self, Http_Mock):
		response_json_str = json.dumps({
			"response": "json",
			"of": "myself"
		})

		(Http_Mock.expects_call()
					.with_args(_curl_verbose=False, user_agent_prefix="PyJira", proxy=None)
					.returns_fake()
					.expects('get')
						.with_args(
							"http://host/base/api/2/myself",
							headers=["Content-Type: application/json"],
							cookies=["A", "B"])
						.returns( (400, response_json_str, []) ))

		api = jira.JiraRestApi("http://host/base")

		# bypass authorization check
		# TODO find a way to easily "dummy check" auth here
		api._auth_cookies = ["A", "B"]

		self.assertRaises(jira.JiraStatusException, api.myself)


	@fudge.patch("http.Http")
	def test_login_sucessful(self, Http_Mock):
		request_form_json = {
			"os_username": "VALIDUSER",
			"os_password": "INVALIDPASSWORD",
			"os_cookie": "true"
		}

		response_json_str = json.dumps({
			"loginSucceeded": False
		})

		response_cookies = [
			"JSESSIONID=1234; XXX",
			"crowd.token_key=ABCDE; YYY"
		]

		(Http_Mock.expects_call()
					.with_args(_curl_verbose=False, user_agent_prefix="PyJira", proxy=None)
					.returns_fake()
					.expects('post')
						.with_args("http://host/base/gadget/1.0/login", request_form_json)
						.returns( (401, response_json_str, response_cookies) ))



		api = jira.JiraRestApi("http://host/base")

		# Return False on failure
		assert api.login("VALIDUSER", "INVALIDPASSWORD") == False

		# Return None cookies
		assert api.get_auth_cookies() != ["JSESSIONID=1234", "crowd.token_key=ABCDE"]


	@fudge.patch("http.Http")
	def test_search_unauthorized(self, Http_Mock):
		request_form_json = json.dumps({
			"jql": "SOME JQL WITH A = 1",
			"fields": ["summary", "status"],
			"maxResults": 10
		})

		(Http_Mock.expects_call()
					.with_args(_curl_verbose=False, user_agent_prefix="PyJira", proxy=None)
					.returns_fake()
					.provides('post')
						.with_args(
							"http://host/base/api/2/search",
							request_form_json,
							headers=["Content-Type: application/json"],
							cookies=["A", "B"])
						.returns( (111, "", []) ))

		api = jira.JiraRestApi("http://host/base")

		self.assertRaises(jira.JiraAuthException, api.search, "SOME JQL WITH A = 1")


	@fudge.patch("http.Http")
	def test_search_successful(self, Http_Mock):
		request_form_json = json.dumps({
			"jql": "SOME JQL WITH A = 1",
			"fields": ["summary", "status"],
			"maxResults": 10
		})

		response_json_str = json.dumps({
			"response": "json",
			"of": "search"
		})

		(Http_Mock.expects_call()
					.with_args(_curl_verbose=False, user_agent_prefix="PyJira", proxy=None)
					.returns_fake()
					.expects('post')
						.with_args(
							"http://host/base/api/2/search",
							request_form_json,
							headers=["Content-Type: application/json"],
							cookies=["A", "B"])
						.returns( (200, response_json_str, []) ))

		api = jira.JiraRestApi("http://host/base")

		# bypass authorization check
		# TODO find a way to easily "dummy check" auth here
		api._auth_cookies = ["A", "B"]

		assert api.search("SOME JQL WITH A = 1") == {
			"response": "json",
			"of": "search"
		}


	@fudge.patch("http.Http")
	def test_search_unsuccessful(self, Http_Mock):
		request_form_json = json.dumps({
			"jql": "SOME JQL WITH A = 1",
			"fields": ["summary", "status"],
			"maxResults": 10
		})

		response_json_str = json.dumps({
			"response": "json",
			"of": "search"
		})

		(Http_Mock.expects_call()
					.with_args(_curl_verbose=False, user_agent_prefix="PyJira", proxy=None)
					.returns_fake()
					.expects('post')
						.with_args(
							"http://host/base/api/2/search",
							request_form_json,
							headers=["Content-Type: application/json"],
							cookies=["A", "B"])
						.returns( (400, response_json_str, []) ))

		api = jira.JiraRestApi("http://host/base")

		# bypass authorization check
		# TODO find a way to easily "dummy check" auth here
		api._auth_cookies = ["A", "B"]

		self.assertRaises(jira.JiraStatusException, api.search, "SOME JQL WITH A = 1")


	@fudge.patch("http.Http")
	def test_get_unauthorized(self, Http_Mock):
		(Http_Mock.expects_call()
					.with_args(_curl_verbose=False, user_agent_prefix="PyJira", proxy=None)
					.returns_fake()
					.provides('get')
						.with_args(
							"http://host/base/api/2/issue/KEY-12345",
							headers=["Content-Type: application/json"],
							cookies=["A", "B"])
						.returns( (111, "", []) ))

		api = jira.JiraRestApi("http://host/base")

		self.assertRaises(jira.JiraAuthException, api.get, "KEY-12345")


	@fudge.patch("http.Http")
	def test_get_successful(self, Http_Mock):
		response_json_str = json.dumps({
			"response": "json",
			"of": "search"
		})

		(Http_Mock.expects_call()
					.with_args(_curl_verbose=False, user_agent_prefix="PyJira", proxy=None)
					.returns_fake()
					.expects('get')
						.with_args(
							"http://host/base/api/2/issue/KEY-12345",
							headers=["Content-Type: application/json"],
							cookies=["A", "B"])
						.returns( (200, response_json_str, []) ))

		api = jira.JiraRestApi("http://host/base")

		# bypass authorization check
		# TODO find a way to easily "dummy check" auth here
		api._auth_cookies = ["A", "B"]

		assert api.get("KEY-12345") == {
			"response": "json",
			"of": "search"
		}


	@fudge.patch("http.Http")
	def test_get_unsuccessful(self, Http_Mock):
		response_json_str = json.dumps({
			"response": "json",
			"of": "search"
		})

		(Http_Mock.expects_call()
					.with_args(_curl_verbose=False, user_agent_prefix="PyJira", proxy=None)
					.returns_fake()
					.expects('get')
						.with_args(
							"http://host/base/api/2/issue/KEY-12345",
							headers=["Content-Type: application/json"],
							cookies=["A", "B"])
						.returns( (400, response_json_str, []) ))

		api = jira.JiraRestApi("http://host/base")

		# bypass authorization check
		# TODO find a way to easily "dummy check" auth here
		api._auth_cookies = ["A", "B"]

		self.assertRaises(jira.JiraStatusException, api.get, "KEY-12345")


	@fudge.patch("http.Http")
	def test_get_comments_unauthorized(self, Http_Mock):
		(Http_Mock.expects_call()
					.with_args(_curl_verbose=False, user_agent_prefix="PyJira", proxy=None)
					.returns_fake()
					.provides('get')
						.with_args(
							"http://host/base/api/2/issue/KEY-12345/comment",
							headers=["Content-Type: application/json"],
							cookies=["A", "B"])
						.returns( (111, "", []) ))

		api = jira.JiraRestApi("http://host/base")

		self.assertRaises(jira.JiraAuthException, api.get_comments, "KEY-12345")


	@fudge.patch("http.Http")
	def test_get_comments_successful(self, Http_Mock):
		response_json_str = json.dumps({
			"response": "json",
			"of": "get_comments"
		})

		(Http_Mock.expects_call()
					.with_args(_curl_verbose=False, user_agent_prefix="PyJira", proxy=None)
					.returns_fake()
					.expects('get')
						.with_args(
							"http://host/base/api/2/issue/KEY-12345/comment",
							headers=["Content-Type: application/json"],
							cookies=["A", "B"])
						.returns( (200, response_json_str, []) ))

		api = jira.JiraRestApi("http://host/base")

		# bypass authorization check
		# TODO find a way to easily "dummy check" auth here
		api._auth_cookies = ["A", "B"]

		assert api.get_comments("KEY-12345") == {
			"response": "json",
			"of": "get_comments"
		}


	@fudge.patch("http.Http")
	def test_get_comments_unsuccessful(self, Http_Mock):
		response_json_str = json.dumps({
			"response": "json",
			"of": "get_comments"
		})

		(Http_Mock.expects_call()
					.with_args(_curl_verbose=False, user_agent_prefix="PyJira", proxy=None)
					.returns_fake()
					.expects('get')
						.with_args(
							"http://host/base/api/2/issue/KEY-12345/comment",
							headers=["Content-Type: application/json"],
							cookies=["A", "B"])
						.returns( (400, response_json_str, []) ))

		api = jira.JiraRestApi("http://host/base")

		# bypass authorization check
		# TODO find a way to easily "dummy check" auth here
		api._auth_cookies = ["A", "B"]

		self.assertRaises(jira.JiraStatusException, api.get_comments, "KEY-12345")


	@fudge.patch("http.Http")
	def test_add_comment_unauthorized(self, Http_Mock):
		request_form_json = {
			"body": "Some comment"
		}

		(Http_Mock.expects_call()
					.with_args(_curl_verbose=False, user_agent_prefix="PyJira", proxy=None)
					.returns_fake()
					.provides('post')
						.with_args(
							"http://host/base/api/2/issue/KEY-12345/comment",
							request_form_json,
							headers=["Content-Type: application/json"],
							cookies=["A", "B"])
						.returns( (111, "", []) ))

		api = jira.JiraRestApi("http://host/base")

		self.assertRaises(jira.JiraAuthException, api.add_comment, "KEY-12345", "Some commment")


	@fudge.patch("http.Http")
	def test_add_comment_successful(self, Http_Mock):
		request_form_json = json.dumps({
			"body": "Some comment"
		})

		response_json_str = json.dumps({
			"successfully": "created"
		})

		(Http_Mock.expects_call()
					.with_args(_curl_verbose=False, user_agent_prefix="PyJira", proxy=None)
					.returns_fake()
					.expects('post')
						.with_args(
							"http://host/base/api/2/issue/KEY-12345/comment",
							request_form_json,
							headers=["Content-Type: application/json"],
							cookies=["A", "B"])
						.returns( (201, response_json_str, []) ))

		api = jira.JiraRestApi("http://host/base")

		# bypass authorization check
		# TODO find a way to easily "dummy check" auth here
		api._auth_cookies = ["A", "B"]

		assert api.add_comment("KEY-12345", "Some comment") == {
			"successfully": "created"
		}


	@fudge.patch("http.Http")
	def test_add_comment_unsuccessful(self, Http_Mock):
		request_form_json = json.dumps({
			"body": "Some comment"
		})

		response_json_str = json.dumps({
			"error": "response json"
		})

		(Http_Mock.expects_call()
					.with_args(_curl_verbose=False, user_agent_prefix="PyJira", proxy=None)
					.returns_fake()
					.expects('post')
						.with_args(
							"http://host/base/api/2/issue/KEY-12345/comment",
							request_form_json,
							headers=["Content-Type: application/json"],
							cookies=["A", "B"])
						.returns( (400, response_json_str, []) ))

		api = jira.JiraRestApi("http://host/base")

		# bypass authorization check
		# TODO find a way to easily "dummy check" auth here
		api._auth_cookies = ["A", "B"]

		self.assertRaises(jira.JiraStatusException, api.add_comment, "KEY-12345", "Some comment")


	@fudge.patch("http.Http")
	def test_assign_unauthorized(self, Http_Mock):
		request_form_json = json.dumps({
			"name": "Some name"
		})

		(Http_Mock.expects_call()
					.with_args(_curl_verbose=False, user_agent_prefix="PyJira", proxy=None)
					.returns_fake()
					.provides('put')
						.with_args(
							"http://host/base/api/2/issue/KEY-12345/assignee",
							request_form_json,
							headers=["Content-Type: application/json"],
							cookies=["A", "B"])
						.returns( (111, "", []) ))

		api = jira.JiraRestApi("http://host/base")

		self.assertRaises(jira.JiraAuthException, api.assign, "KEY-12345", "Some name")


	@fudge.patch("http.Http")
	def test_assign_successful(self, Http_Mock):
		request_form_json = json.dumps({
			"name": "Some name"
		})

		(Http_Mock.expects_call()
					.with_args(_curl_verbose=False, user_agent_prefix="PyJira", proxy=None)
					.returns_fake()
					.expects('put')
						.with_args(
							"http://host/base/api/2/issue/KEY-12345/assignee",
							request_form_json,
							headers=["Content-Type: application/json"],
							cookies=["A", "B"])
						.returns( (204, "", []) ))

		api = jira.JiraRestApi("http://host/base")

		# bypass authorization check
		# TODO find a way to easily "dummy check" auth here
		api._auth_cookies = ["A", "B"]

		api.assign("KEY-12345", "Some name")


	@fudge.patch("http.Http")
	def test_assign_unsuccessful(self, Http_Mock):
		request_form_json = json.dumps({
			"name": "Some name"
		})

		response_json_str = json.dumps({
			"error": "response json"
		})

		(Http_Mock.expects_call()
					.with_args(_curl_verbose=False, user_agent_prefix="PyJira", proxy=None)
					.returns_fake()
					.expects('put')
						.with_args(
							"http://host/base/api/2/issue/KEY-12345/assignee",
							request_form_json,
							headers=["Content-Type: application/json"],
							cookies=["A", "B"])
						.returns( (400, response_json_str, []) ))

		api = jira.JiraRestApi("http://host/base")

		# bypass authorization check
		# TODO find a way to easily "dummy check" auth here
		api._auth_cookies = ["A", "B"]

		self.assertRaises(jira.JiraStatusException, api.assign, "KEY-12345", "Some name")


	@fudge.patch("http.Http")
	def test_get_assignees_unauthorized(self, Http_Mock):
		(Http_Mock.expects_call()
					.with_args(_curl_verbose=False, user_agent_prefix="PyJira", proxy=None)
					.returns_fake()
					.provides('get')
						.with_args(
							"http://host/base/api/2/user/search?username=Some name",
							headers=["Content-Type: application/json"],
							cookies=["A", "B"])
						.returns( (111, "", []) ))

		api = jira.JiraRestApi("http://host/base")

		self.assertRaises(jira.JiraAuthException, api.get_assignees, "Some name")


	@fudge.patch("http.Http")
	def test_get_assigneesget_assignees_successful(self, Http_Mock):
		response_json_str = json.dumps({
			"users": ["user1", "user2"]
		})

		(Http_Mock.expects_call()
					.with_args(_curl_verbose=False, user_agent_prefix="PyJira", proxy=None)
					.returns_fake()
					.expects('get')
						.with_args(
							"http://host/base/api/2/user/search?username=Some name",
							headers=["Content-Type: application/json"],
							cookies=["A", "B"])
						.returns( (200, response_json_str, []) ))

		api = jira.JiraRestApi("http://host/base")

		# bypass authorization check
		# TODO find a way to easily "dummy check" auth here
		api._auth_cookies = ["A", "B"]

		api.get_assignees("Some name")


	@fudge.patch("http.Http")
	def test_get_assignees_unsuccessful(self, Http_Mock):
		response_json_str = json.dumps({
			"error": "response json"
		})

		(Http_Mock.expects_call()
					.with_args(_curl_verbose=False, user_agent_prefix="PyJira", proxy=None)
					.returns_fake()
					.expects('get')
						.with_args(
							"http://host/base/api/2/user/search?username=Some name",
							headers=["Content-Type: application/json"],
							cookies=["A", "B"])
						.returns( (400, response_json_str, []) ))

		api = jira.JiraRestApi("http://host/base")

		# bypass authorization check
		# TODO find a way to easily "dummy check" auth here
		api._auth_cookies = ["A", "B"]

		self.assertRaises(jira.JiraStatusException, api.get_assignees, "Some name")





class JiraTest(unittest.TestCase):

	@fudge.patch("jira.JiraRestApi")
	def test_init_with_no_ua(self, JiraRestApi_Mock):
		(JiraRestApi_Mock.expects_call()
					.with_args("http://host/base", user_agent_prefix="PyJira", proxy=None)
					.returns_fake())

		jira.Jira("http://host/base")

	@fudge.patch("jira.JiraRestApi")
	def test_init_with_custom_ua(self, JiraRestApi_Mock):
		(JiraRestApi_Mock.expects_call()
					.with_args("http://host/base", user_agent_prefix="Custom", proxy=None)
					.returns_fake())

		jira.Jira("http://host/base", user_agent_prefix="Custom")



	@fudge.patch("jira.JiraRestApi")
	def test_close(self, JiraRestApi_Mock):
		(JiraRestApi_Mock.expects_call()
					.with_args("http://host/base", user_agent_prefix="PyJira", proxy=None)
					.returns_fake()
					.expects('close'))

		api = jira.Jira("http://host/base")

		api.close()


	@fudge.patch("jira.JiraRestApi")
	def test_get_auth_cookies(self, JiraRestApi_Mock):
		(JiraRestApi_Mock.expects_call()
					.with_args("http://host/base", user_agent_prefix="PyJira", proxy=None)
					.returns_fake()
					.expects('get_auth_cookies')
						.returns( ["A", "B"] ))

		api = jira.Jira("http://host/base")

		assert api.get_auth_cookies() == ["A", "B"]



	@fudge.patch("jira.JiraRestApi")
	def test_check_auth_success(self, JiraRestApi_Mock):
		(JiraRestApi_Mock.expects_call()
			.with_args("http://host/base", user_agent_prefix="PyJira", proxy=None)
			.returns_fake()
				.expects('check_auth')
					.with_args( ["a", "b"] )
					.returns(True))

		api = jira.Jira("http://host/base")

		assert api.check_auth(["a", "b"]) == True

	@fudge.patch("jira.JiraRestApi")
	def test_check_auth_fail(self, JiraRestApi_Mock):
		(JiraRestApi_Mock.expects_call()
			.with_args("http://host/base", user_agent_prefix="PyJira", proxy=None)
			.returns_fake()
				.expects('check_auth')
					.with_args( ["a", "b"] )
					.returns(False))


		api = jira.Jira("http://host/base")

		assert api.check_auth(["a", "b"]) == False



	@fudge.patch("jira.JiraRestApi")
	def test_login_success(self, JiraRestApi_Mock):
		(JiraRestApi_Mock.expects_call()
					.with_args("http://host/base", user_agent_prefix="PyJira", proxy=None)
					.returns_fake()
					.expects('login')
						.with_args("USERNAME", "PASSWORD")
						.returns(True))

		api = jira.Jira("http://host/base")

		assert api.login("USERNAME", "PASSWORD") == True


	@fudge.patch("jira.JiraRestApi")
	def test_login_fail(self, JiraRestApi_Mock):
		(JiraRestApi_Mock.expects_call()
					.with_args("http://host/base", user_agent_prefix="PyJira", proxy=None)
					.returns_fake()
					.expects('login')
						.with_args("USERNAME", "PASSWORD")
						.returns(False))

		api = jira.Jira("http://host/base")

		assert api.login("USERNAME", "PASSWORD") == False


	@fudge.patch("jira.JiraRestApi")
	def test_myself(self, JiraRestApi_Mock):
		myself_json = {
			"key": "u.name",
			"displayName": "User Name",
			"emailAddress": "u.name@acme.com"
		}

		(JiraRestApi_Mock.expects_call()
					.with_args("http://host/base", user_agent_prefix="PyJira", proxy=None)
					.returns_fake()
					.expects('myself')
						.returns(myself_json))

		api = jira.Jira("http://host/base")

		user = api.myself()

		assert user._key == "u.name"
		assert user._display_name == "User Name"
		assert user._email == "u.name@acme.com"

	def _test_search_prepare_data(self, count, max_results, total):
		issues = []

		for i in range(count):
			issues.append({"data": "data"})

		issues_json = {
			"issues": issues,
			"total": total,
			"maxResults": max_results
		}

		return issues_json

	# Mocking for the following tests
	def _test_search_prepare_mocks(self, JiraRestApi_Mock, Issue_Mock, jql, count, fields, issues_json):
		(Issue_Mock.expects_call()
					.with_arg_count(1)
					.returns_fake())

		(JiraRestApi_Mock.expects_call()
					.with_args("http://host/base", user_agent_prefix="PyJira", proxy=None)
					.returns_fake()
					.expects('search')
						.with_args(jql, count, fields)
						.returns(issues_json))

	@fudge.patch("jira.JiraRestApi")
	@fudge.patch("jira.Issue")
	def test_search_more_then_max(self, JiraRestApi_Mock, Issue_Mock):
		issues_json = self._test_search_prepare_data(count=10, max_results=10, total=21)

		self._test_search_prepare_mocks(
			JiraRestApi_Mock, Issue_Mock,
			"SOME JQL = 1",
			10,
			["summary", "description", "assignee", "status", "issuetype", "updated", "parent", "subtasks"],
			issues_json)

		api = jira.Jira("http://host/base")

		(issues, remaining, max_results) = api.search("SOME JQL = 1")

		assert len(issues) == 10
		assert remaining == 11
		assert max_results == 10

	@fudge.patch("jira.JiraRestApi")
	@fudge.patch("jira.Issue")
	def test_search_less_then_max(self, JiraRestApi_Mock, Issue_Mock):
		issues_json = self._test_search_prepare_data(count=3, max_results=10, total=3)

		self._test_search_prepare_mocks(
			JiraRestApi_Mock, Issue_Mock,
			"SOME JQL = 1",
			10,
			["summary", "description", "assignee", "status", "issuetype", "updated", "parent", "subtasks"],
			issues_json)

		api = jira.Jira("http://host/base")

		(issues, remaining, max_results) = api.search("SOME JQL = 1")

		assert len(issues) == 3
		assert remaining == 0
		assert max_results == 10

	@fudge.patch("jira.JiraRestApi")
	@fudge.patch("jira.Issue")
	def test_search_custom_max_results(self, JiraRestApi_Mock, Issue_Mock):
		issues_json = self._test_search_prepare_data(count=5, max_results=5, total=10)

		self._test_search_prepare_mocks(
			JiraRestApi_Mock, Issue_Mock,
			"SOME JQL = 1",
			5,
			["summary", "description", "assignee", "status", "issuetype", "updated", "parent", "subtasks"],
			issues_json)

		api = jira.Jira("http://host/base")

		(issues, remaining, max_results) = api.search("SOME JQL = 1", max_results=5)

		assert len(issues) == 5
		assert remaining == 5
		assert max_results == 5

	@fudge.patch("jira.JiraRestApi")
	@fudge.patch("jira.Issue")
	def test_search_custom_fields(self, JiraRestApi_Mock, Issue_Mock):
		issues_json = self._test_search_prepare_data(count=3, max_results=10, total=3)

		self._test_search_prepare_mocks(
			JiraRestApi_Mock, Issue_Mock,
			"SOME JQL = 1",
			10,
			["summary", "description"],
			issues_json)

		api = jira.Jira("http://host/base")

		(issues, remaining, max_results) = api.search("SOME JQL = 1", fields=["summary", "description"])

		assert len(issues) == 3
		assert remaining == 0
		assert max_results == 10




	@fudge.patch("jira.JiraRestApi")
	def test_get_parent(self, JiraRestApi_Mock):
		issue_json = {
			"key": "KEY-12345",
			"fields": {
				"summary": "Summary",
				"description": "Descrption",
				"assignee": {
					"name": "s.user",
					"displayName": "some user"
				},
				"status": {
					"name": "open"
				},
				"issuetype":  {
					"name": "bug"
				},
				"updated": "",
				"parent": {
					"key": "KEY-98765",
					"fields": {
						"summary": "Parent's summary",
						"status": {
							"name": "resolved"
						},
						"issuetype":  {
							"name": "task"
						}
					}
				}
			}
		}

		(JiraRestApi_Mock.expects_call()
					.with_args("http://host/base", user_agent_prefix="PyJira", proxy=None)
					.returns_fake()
					.expects('get')
						.with_args("KEY-12345")
						.returns(issue_json))

		api = jira.Jira("http://host/base")

		issue = api.get("KEY-12345")

		assert issue._key == "KEY-12345"
		assert issue._type == "bug"
		assert issue._status == "open"
		assert type(issue._assignee) == jira.User
		assert issue._assignee._display_name == "some user"
		assert issue._description == "Descrption"
		assert issue._summary == "Summary"
		assert issue._parent._key == "KEY-98765"
		assert issue._parent._type == "task"
		assert issue._parent._status == "resolved"
		assert issue._parent._summary == "Parent's summary"

	@fudge.patch("jira.JiraRestApi")
	def test_get_subtasks(self, JiraRestApi_Mock):
		issue_json = {
			"key": "KEY-12345",
			"fields": {
				"summary": "Summary",
				"description": "Descrption",
				"assignee": {
					"name": "s.user",
					"displayName": "some user"
				},
				"status": {
					"name": "open"
				},
				"issuetype":  {
					"name": "bug"
				},
				"updated": "2015-01-23T19:03:43.000+0100",
				"subtasks": [
					{
						"key": "KEY-777",
						"fields": {
							"summary": "Subtasks's summary",
							"status": {
								"name": "progress"
							},
							"issuetype":  {
								"name": "subtask"
							}
						}
					}
				]
			}
		}

		(JiraRestApi_Mock.expects_call()
					.with_args("http://host/base", user_agent_prefix="PyJira", proxy=None)
					.returns_fake()
					.expects('get')
						.with_args("KEY-12345")
						.returns(issue_json))

		api = jira.Jira("http://host/base")

		issue = api.get("KEY-12345")

		assert issue._key == "KEY-12345"
		assert issue._type == "bug"
		assert issue._status == "open"
		assert type(issue._assignee) == jira.User
		assert issue._assignee._display_name == "some user"
		assert issue._description == "Descrption"
		assert issue._summary == "Summary"
		assert int(issue._updated) == 1422036223
		assert issue._subtasks[0]._key == "KEY-777"
		assert issue._subtasks[0]._type == "subtask"
		assert issue._subtasks[0]._status == "progress"
		assert issue._subtasks[0]._summary == "Subtasks's summary"


	@fudge.patch("jira.JiraRestApi")
	def test_get_comments(self, JiraRestApi_Mock):
		comments_json = {
			"comments": [
				{"body": "Comment 1", "created": "2015-01-23T17:42:05.000+0100"},
				{"body": "Comment 2", "created": "2015-01-23T19:03:43.000+0100"}
			]
		}

		(JiraRestApi_Mock.expects_call()
					.with_args("http://host/base", user_agent_prefix="PyJira", proxy=None)
					.returns_fake()
					.expects('get_comments')
						.with_args("KEY-12345")
						.returns(comments_json))

		api = jira.Jira("http://host/base")

		comments = api.get_comments("KEY-12345")

		assert len(comments) == 2
		assert comments[0]._body == "Comment 1"
		assert int(comments[0]._created) == 1422031325
		assert comments[1]._body == "Comment 2"
		assert int(comments[1]._created) == 1422036223


	@fudge.patch("jira.JiraRestApi")
	def test_add_comment(self, JiraRestApi_Mock):
		(JiraRestApi_Mock.expects_call()
					.with_args("http://host/base", user_agent_prefix="PyJira", proxy=None)
					.returns_fake()
					.expects('add_comment')
						.with_args("KEY-12345", "New comment"))

		api = jira.Jira("http://host/base")

		api.add_comment("KEY-12345", "New comment")



	@fudge.patch("jira.JiraRestApi")
	def test_assign(self, JiraRestApi_Mock):
		(JiraRestApi_Mock.expects_call()
					.with_args("http://host/base", user_agent_prefix="PyJira", proxy=None)
					.returns_fake()
					.expects('assign')
						.with_args("KEY-12345", "user name"))

		api = jira.Jira("http://host/base")

		api.assign("KEY-12345", "user name")


	@fudge.patch("jira.JiraRestApi")
	def test_unassign(self, JiraRestApi_Mock):
		(JiraRestApi_Mock.expects_call()
					.with_args("http://host/base", user_agent_prefix="PyJira", proxy=None)
					.returns_fake()
					.expects('assign')
						.with_args("KEY-12345", None))

		api = jira.Jira("http://host/base")

		api.unassign("KEY-12345")


	@fudge.patch("jira.JiraRestApi")
	def test_get_assignees(self, JiraRestApi_Mock):
		assignees_json = [
			{"key": "user.name1", "displayName": "User Name 1", "emailAddress": "u1@acme.com"},
			{"key": "user.name2", "displayName": "User Name 2", "emailAddress": "u2@acme.com"}
		]

		(JiraRestApi_Mock.expects_call()
					.with_args("http://host/base", user_agent_prefix="PyJira", proxy=None)
					.returns_fake()
					.expects('get_assignees')
						.with_args("user na")
						.returns(assignees_json))

		api = jira.Jira("http://host/base")

		assignees = api.get_assignees("user na")

		assert len(assignees) == 2
		assert assignees[0]._key == "user.name1"
		assert assignees[0]._display_name == "User Name 1"
		assert assignees[0]._email == "u1@acme.com"
		assert assignees[1]._key == "user.name2"
		assert assignees[1]._display_name == "User Name 2"
		assert assignees[1]._email == "u2@acme.com"
