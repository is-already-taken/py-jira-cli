
import pycurl
import urllib
import StringIO
import re

"""Facade for pycurl providing HTTP verb methods and simple interface."""
class Http(object):


	def __init__(self, proxy=None, no_check_certificate=False, _curl_verbose=False):
		self.c = pycurl.Curl()

		if proxy != None:
			self.c.setopt(pycurl.PROXY, proxy)

		if no_check_certificate:
			self.c.setopt(pycurl.SSL_VERIFYPEER, 0)

		self.c.setopt(pycurl.VERBOSE, 1 if _curl_verbose else 0)

	"""Generic HTTP verb method"""
	def method(self, method, url, data=None, headers=[], cookies=[]):

		#c.setopt(pycurl.URL, 'http://stackoverflow.com')
		self.c.setopt(pycurl.URL, url)

		if method == 'POST':
			if data == None:
				raise Exception("Canot post with None data")

			self.c.setopt(pycurl.POST, 1)

			# convert dict to URL encoded string
			if type(data) == dict:
				data = urllib.urlencode(data)

				headers.append("Content-Type: application/x-www-form-urlencoded; charset=UTF-8")

			self.c.setopt(pycurl.POSTFIELDSIZE, len(data))
			self.c.setopt(pycurl.POSTFIELDS, data)
		else:
			self.c.setopt(pycurl.HTTPGET, 1)

		# ["Content-Type: application/json"]
		self.c.setopt(pycurl.HTTPHEADER, headers)

		# "name=value; name=value"
		self.c.setopt(pycurl.COOKIE, "; ".join(cookies))

		set_cookies = []

		# closure to capture Set-Cookie
		def _write_header(header):
			match = re.match("^Set-Cookie: (.*)$", header)

			if match:
				set_cookies.append(match.group(1))

		# use closure to collect cookies sent from the server
		self.c.setopt(pycurl.HEADERFUNCTION, _write_header)

		buf = StringIO.StringIO()

		self.c.setopt(pycurl.WRITEFUNCTION, buf.write)

		try:
			self.c.perform()
		except pycurl.error as pe:
			raise HttpError(pe)

		status = self.c.getinfo(self.c.RESPONSE_CODE)

		return (status, buf.getvalue(), set_cookies)

	def close(self):
		self.c.close()

	"""Send HTTP POST passing data, headers and cookies."""
	def post(self, url, data, headers=[], cookies=[]):
		return self.method("POST", url, data, headers, cookies)

	"""Send HTTP GET passing headers and cookies."""
	def get(self, url, headers=[], cookies=[]):
		return self.method("GET", url, None, headers, cookies)


"""Wraps pycurl.error exceptions for HTTP errors"""
class HttpError(Exception):

	def __init__(self, pycurl_error):
		self.code = pycurl_error[0]
		self.message = pycurl_error[1]

	def __str__(self):
		return "%s (%d)" % (self.message, self.code)
