import sys
import os
import os.path
import ConfigParser
import crypt
import getpass
import jira

# in $HOME
CONFIG_FILE=".pyjirarc"

DEFAULT_STORE_PATH = ".pyjirastore"

class PyJiraCli(object):

	def _fail(self, message):
		print message
		sys.exit(1)


	def _get_option(self, config, section, option, default=None):
		if not config.has_section(section):
			return default

		if not config.has_option(section, option):
			return default

		return config.get(section, option)

	def _read_config(self):
		pass

		home_path = os.getenv("HOME")
		config_path = os.path.join(home_path, CONFIG_FILE)

		if not os.path.exists(config_path):
			self._fail("Config %s not found in %s" % (CONFIG_FILE, home_path))

		config = ConfigParser.RawConfigParser()
		config.read(config_path)

		self.store = self._get_option(config, "store", "path", DEFAULT_STORE_PATH)
		self.store_pw = self._get_option(config, "store", "key")
		self.url = self._get_option(config, "jira", "url")
		self.username = self._get_option(config, "jira", "user")

		if self.store == None:
			self._fail("No session store configured.\nPlease add [store] with path=<relative to HOME>")

		self.store_path = os.path.join(home_path, self.store)

		if self.store_pw == None:
			self._fail("No session store password configured.\nPlease add [store] with key=<password>")

		if self.url == None:
			self._fail("Jira URL not configured.\nPlease add [jira] with url=https://<host>/path/ending/with/rest")

		self.url = self.url.rstrip("/")

		if self.username == None:
			self._fail("Jira username not configured.\nPlease add [jira] with user=<username>")

	def _load_session(self):
		c = crypt.Cryptor(self.store_pw)

		if not os.path.exists(self.store_path):
			return None
		else:
			with open(self.store_path, "r") as f:
				crypted_content = f.read().strip("\n")

				if crypted_content == "" or len(crypted_content.split(";")) == 0:
					return None

				serialized_session = c.decrypt(crypted_content)

				return serialized_session.split("; ")

	def _store_session(self):
		c = crypt.Cryptor(self.store_pw)

		with open(self.store_path, "w+") as f:
			if self._session != None:
				serialized_session = "; ".join(self._session)

				f.write(c.encrypt(serialized_session))
			else:
				f.write("")


	def _jira_check_auth(self):
		is_authenticated = self.jira.check_auth(self._session)

		if not is_authenticated:
			self._session = None

		return is_authenticated

	def _jira_auth(self):
		print "No session stored. Please authenticate as \"%s\"." % (self.username)

		try:
			jira_password = getpass.getpass("Password: ")
		except KeyboardInterrupt as e:
			print ""
			return False

		is_authenticated = self.jira.login(self.username, jira_password)

		if is_authenticated:
			self._session = self.jira.get_auth_cookies()

		return is_authenticated



	def _init(self):
		# jira.JiraRestApi._CURL_VERBOSE = True
		self.jira = jira.Jira(self.url, user_agent_prefix="PyJiraCLI")

		self._session = self._load_session()

		if self._session != None:
			# resets _session if not valid
			if not self._jira_check_auth():
				self._store_session()
				print "Stored session was no longer authenticated. Try to login ..."

		if self._session == None:
			if not self._jira_auth():
				self._fail("Failed to login.")
			else:
				self._store_session()

	def jql(self, jql, max_results=10):
		# summary, assignee, reporter, status, created, updated, description, parent, project, subtasks
		issues = self.jira.search(jql, max_results=max_results)
		# print "\n".join(str(issue) for issue in issues)
		for issue in issues:
			print issue
			if len(issue._subtasks) > 0:
				print "\n".join(" |- " + str(subtask) for subtask in issue._subtasks)

	def get(self, key):
		print self.jira.get(key)


	def comments(self, key):
		comments = self.jira.get_comments(key)
		print "\n\n".join([str(comment) for comment in comments])

	def comment(self, key, comment):
		self.jira.add_comment(key, comment)

	def assign(self, key, assignee):
		users = self.jira.get_assignees(assignee)

		if len(users) == 1:
			self._assign(key, users[0])
		elif len(users) == 0:
			print "No user found for \"%s\"" % (assignee)
		else:
			print "Multiple users found for \"%s\"" % (assignee)
			print "\n".join(str(user) for user in users)

			user_id = self._prompt("Choose a user ID: ")

			if user_id == None:
				print "Cancelled."
			else:
				self._assign(key, filter(lambda user: user._key == user_id, users)[0])

	def _assign(self, key, user):
		print "Assigning to %s (%s)" % (user._display_name, user._key)
		self.jira.assign(key, user._key)

	def _prompt(self, text):
		sys.stdout.write(text)

		try:
			s = sys.stdin.readline().rstrip("\n")
		except KeyboardInterrupt as e:
			return None

		if s != "":
			return s
		else:
			return None

	def unassign(self, key):
		self.jira.unassign(key)

	def get_assignees(self, username_fragement):
		users = self.jira.get_assignees(username_fragement)

		print "\n".join(str(user) for user in users)

	def run(self):
		if len(sys.argv) < 2:
			self._fail("Please specify a command")

		self._read_config()

		self._init()

		cmd = sys.argv[1]

		if cmd == "jql":
			self.jql(sys.argv[2])
		elif cmd == "get":
			self.get(sys.argv[2])
		elif cmd == "comments":
			self.comments(sys.argv[2])
		elif cmd == "comment":
			self.comment(sys.argv[2], sys.argv[3])
		elif cmd == "assign":
			self.assign(sys.argv[2], sys.argv[3])
		elif cmd == "unassign":
			self.unassign(sys.argv[2])
		elif cmd == "assignees":
			self.get_assignees(sys.argv[2])



if __name__ == "__main__":
	cli = PyJiraCli()
	cli.run()
