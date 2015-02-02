import sys
import os
import os.path
import ConfigParser
import crypt
import getpass
import jira
import datetime
from textwrap import wrap
import argparse

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

		self.config = ConfigParser.RawConfigParser()
		self.config.read(config_path)

		self.store = self._get_option(self.config, "store", "path", DEFAULT_STORE_PATH)
		self.store_pw = self._get_option(self.config, "store", "key")
		self.proxy = self._get_option(self.config, "network", "proxy")
		self.url = self._get_option(self.config, "jira", "url")
		self.username = self._get_option(self.config, "jira", "user")

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
		self.jira = jira.Jira(self.url, user_agent_prefix="PyJiraCLI", proxy=self.proxy)

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

	def _query(self, query):
		# summary, assignee, reporter, status, created, updated, description, parent, project, subtasks

		(issues, remaining_results, limited_to) = self.jira.search(query)
		# print "\n".join(str(issue) for issue in issues)
		for issue in issues:
			print issue
			if len(issue._subtasks) > 0:
				print "\n".join(" |- " + str(subtask) for subtask in issue._subtasks)

		if remaining_results > 0:
			print "%d Issues remaining (limited to %d)" % (remaining_results, limited_to)

	def query(self, args):
		query = " ".join(args.query)

		self._query(query)

	def filter(self, args):
		jql = self._get_option(self.config, "filters", args.name, None)

		if jql == None:
			self._fail("Filter \"%s\" not found" % args.name)

		self._query(jql)

	def get(self, args):
		issue = self.jira.get(args.key)

		_formatted_date = datetime.datetime.utcfromtimestamp(issue._updated).strftime("%d.%m.%y %H:%M")

		print "%s\tType: %s\tStatus: %s" % (issue._key, issue._type, issue._status)
		print "-" * 80
		print "Updated: %s" % (_formatted_date)
		if issue._parent != None:
			print "-" * 80
			print "Parent: %s" % (str(issue._parent))
		print "-" * 80
		print issue._summary
		print "=" * 80
		print "\n".join(wrap(issue._description, width=80))
		if len(issue._subtasks) > 0:
			print "-" * 80
			print "Subtasks:"
			print "\n".join(["  - " + str(sub_task) for sub_task in issue._subtasks])


	def comments(self, args):
		comments = self.jira.get_comments(args.key)
		print "\n\n".join([str(comment) for comment in comments])

	def comment(self, args):
		self.jira.add_comment(args.key, " ".join(args.comment))

	def assign(self, args):
		users = self.jira.get_assignees(args.name)

		if len(users) == 1:
			self._assign(args.key, users[0])
		elif len(users) == 0:
			print "No user found for \"%s\"" % (args.name)
		else:
			print "Multiple users found for \"%s\"" % (args.name)
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

	def unassign(self, args):
		self.jira.unassign(args.key)

	def assignees(self, args):
		users = self.jira.get_assignees(args.username_fragement)

		print "\n".join(str(user) for user in users)

	def _parse_args(self):
		parser = argparse.ArgumentParser()
		subparsers = parser.add_subparsers(
			title='subcommands',
			description='valid subcommands',
			help='additional help')


	def run(self):
		parser = argparse.ArgumentParser(
			prog="pyjiracli",
			description="Interact with JIRA using the command line interface.",
			epilog="See %(prog)s COMMAND --help for detailed help on a command"
		)

		parser.add_argument(
			'-V','--version',
			action='version',
			version='%(prog)s 0.1')


		subparsers = parser.add_subparsers(
			title='COMMANDS')

		parser_add = subparsers.add_parser('jql', help="Query by JQL")
		parser_add.set_defaults(func=self.query)
		parser_add.add_argument(
			'query',
			nargs="+",
			type=str,
			help='JQL like "project = ACME and status = Open"')

		parser_get = subparsers.add_parser('get', help="Get issue details")
		parser_get.set_defaults(func=self.get)
		parser_get.add_argument(
			'key',
			type=str,
			help='Issue key like "ACME-123"')

		parser_filter = subparsers.add_parser('filter', help="Query by named filter")
		parser_filter.set_defaults(func=self.filter)
		parser_filter.add_argument(
			'name',
			type=str,
			help='Named query like "acme-status-open"')

		parser_comment = subparsers.add_parser('comment', help="Comment on issue")
		parser_comment.set_defaults(func=self.comment)
		parser_comment.add_argument(
			'key',
			type=str,
			help='Issue key like "ACME-123"')
		parser_comment.add_argument(
			'comment',
			nargs="+",
			type=str,
			help='Comment text like "Deployed application to *QA*"')

		parser_comments = subparsers.add_parser('comments', help="Show comments of issue")
		parser_comments.set_defaults(func=self.comments)
		parser_comments.add_argument(
			'key',
			type=str,
			help='Issue key like "ACME-123"')

		parser_assign = subparsers.add_parser('assign', help="Assign issue to someone")
		parser_assign.set_defaults(func=self.assign)
		parser_assign.add_argument(
			'key',
			type=str,
			help='Issue key like "ACME-123"')
		parser_assign.add_argument(
			'name',
			type=str,
			help='User name or name fragment like "j.d" or "j.doe" or "John"')

		parser_unassign = subparsers.add_parser('unassign', help="Unassign")
		parser_unassign.set_defaults(func=self.unassign)
		parser_unassign.add_argument(
			'key',
			type=str,
			help='Issue key like "ACME-123"')

		parser_assignees = subparsers.add_parser('assignees', help="List assignees by name fragment")
		parser_assignees.set_defaults(func=self.assignees)
		parser_assignees.add_argument(
			'username_fragement',
			type=str,
			help='User name or name fragment like "j.d" or "j.doe" or "John"')


		parsed = parser.parse_args(sys.argv[1:])

		self._read_config()
		self._init()

		# run configured subcommand with parsed args
		parsed.func(parsed)

if __name__ == "__main__":
	cli = PyJiraCli()
	cli.run()
