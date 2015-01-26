
import unittest
from mock import patch, Mock, MagicMock
import fudge
from fudge.inspector import arg
import pycurl
import http
import mox

class HttpTest(unittest.TestCase):

	@fudge.patch("pycurl.Curl")
	@fudge.patch("StringIO.StringIO")
	def test_method_post(self, Curl_Mock, StringIO_Mock):
		(StringIO_Mock.expects_call()
			.returns_fake()
			.provides("write")
			.provides("getvalue").returns("RESPONSE DATA"))

		mock = (Curl_Mock.expects_call()
			.returns_fake())

		# the method under test will call a method that has
		# been passed via setopt(pycurl.WRITEFUNCTION, ...)
		# Intercept the call to define cookies that the
		# server would send
		def get_header_fn(option, value):
			if option == pycurl.HEADERFUNCTION:
				value("Set-Cookie: new-cookie=1")

		mock.expects('setopt').with_args(pycurl.VERBOSE, 0)
		mock.expects('setopt').with_args(pycurl.URL, "http://host/path")

		mock.expects('setopt').with_args(pycurl.POST, 1)
		mock.expects('setopt').with_args(pycurl.POSTFIELDSIZE, len("REQUEST DATA"))
		mock.expects('setopt').with_args(pycurl.POSTFIELDS, "REQUEST DATA")
		mock.expects('setopt').with_args(pycurl.HTTPHEADER, ["Hdr-A: 1", "Hdr-B: 2"])
		mock.expects('setopt').with_args(pycurl.COOKIE, "")
		mock.provides('setopt').calls(get_header_fn)
		mock.expects('setopt').with_args(pycurl.WRITEFUNCTION, arg.any())
		mock.expects('perform')
		mock.has_attr(RESPONSE_CODE="RESPONSE_CODE_MOCK")
		mock.provides('getinfo').calls(lambda _: 200)

		h = http.Http()

		(status, buf, cookies) = h.method("POST", "http://host/path", "REQUEST DATA", headers=["Hdr-A: 1", "Hdr-B: 2"])

		assert status == 200
		assert buf == "RESPONSE DATA"
		assert cookies == ["new-cookie=1"]



	@fudge.patch("pycurl.Curl")
	@fudge.patch("StringIO.StringIO")
	def test_method_post_dict_data(self, Curl_Mock, StringIO_Mock):
		(StringIO_Mock.expects_call()
			.returns_fake()
			.provides("write")
			.provides("getvalue").returns("RESPONSE DATA"))

		mock = (Curl_Mock.expects_call()
			.returns_fake())

		# the method under test will call a method that has
		# been passed via setopt(pycurl.WRITEFUNCTION, ...)
		# Intercept the call to define cookies that the
		# server would send
		def get_header_fn(option, value):
			if option == pycurl.HEADERFUNCTION:
				value("Set-Cookie: new-cookie=1")

		mock.expects('setopt').with_args(pycurl.VERBOSE, 0)
		mock.expects('setopt').with_args(pycurl.URL, "http://host/path")

		mock.expects('setopt').with_args(pycurl.POST, 1)
		mock.expects('setopt').with_args(pycurl.POSTFIELDSIZE, len("data1=A&data2=B"))
		mock.expects('setopt').with_args(pycurl.POSTFIELDS, "data1=A&data2=B")
		mock.expects('setopt').with_args(pycurl.HTTPHEADER, [
			"Hdr-A: 1",
			"Hdr-B: 2",
			"Content-Type: application/x-www-form-urlencoded; charset=UTF-8"
		])
		mock.expects('setopt').with_args(pycurl.COOKIE, "")
		mock.provides('setopt').calls(get_header_fn)
		mock.expects('setopt').with_args(pycurl.WRITEFUNCTION, arg.any())
		mock.expects('perform')
		mock.has_attr(RESPONSE_CODE="RESPONSE_CODE_MOCK")
		mock.provides('getinfo').calls(lambda _: 200)

		h = http.Http()

		(status, buf, cookies) = h.method("POST", "http://host/path", {"data1": "A", "data2": "B"}, headers=["Hdr-A: 1", "Hdr-B: 2"])

		assert status == 200
		assert buf == "RESPONSE DATA"
		assert cookies == ["new-cookie=1"]


	@fudge.patch("pycurl.Curl")
	@fudge.patch("StringIO.StringIO")
	def test_method_post_no_data(self, Curl_Mock, StringIO_Mock):
		mock = (Curl_Mock.expects_call()
			.returns_fake())

		mock.expects('setopt').with_args(pycurl.VERBOSE, 0)
		mock.expects('setopt').with_args(pycurl.URL, "http://host/path")

		h = http.Http()

		self.assertRaises(Exception, h.method, "POST", None)

	@fudge.patch("pycurl.Curl")
	@fudge.patch("StringIO.StringIO")
	def test_method_put(self, Curl_Mock, StringIO_Mock):
		(StringIO_Mock.expects_call()
			.returns_fake()
			.provides("write")
			.provides("getvalue").returns("RESPONSE DATA"))

		mock = (Curl_Mock.expects_call()
			.returns_fake())

		# the method under test will call a method that has
		# been passed via setopt(pycurl.WRITEFUNCTION, ...)
		# Intercept the call to define cookies that the
		# server would send
		def get_header_fn(option, value):
			if option == pycurl.HEADERFUNCTION:
				value("Set-Cookie: new-cookie=1")

		mock.expects('setopt').with_args(pycurl.VERBOSE, 0)
		mock.expects('setopt').with_args(pycurl.URL, "http://host/path")

		mock.expects('setopt').with_args(pycurl.CUSTOMREQUEST, "PUT")
		mock.expects('setopt').with_args(pycurl.POSTFIELDSIZE, len("REQUEST DATA"))
		mock.expects('setopt').with_args(pycurl.POSTFIELDS, "REQUEST DATA")
		mock.expects('setopt').with_args(pycurl.HTTPHEADER, ["Hdr-A: 1", "Hdr-B: 2"])
		mock.expects('setopt').with_args(pycurl.COOKIE, "")
		mock.provides('setopt').calls(get_header_fn)
		mock.expects('setopt').with_args(pycurl.WRITEFUNCTION, arg.any())
		mock.expects('perform')
		mock.has_attr(RESPONSE_CODE="RESPONSE_CODE_MOCK")
		mock.provides('getinfo').calls(lambda _: 200)

		h = http.Http()

		(status, buf, cookies) = h.method("PUT", "http://host/path", "REQUEST DATA", headers=["Hdr-A: 1", "Hdr-B: 2"])

		assert status == 200
		assert buf == "RESPONSE DATA"
		assert cookies == ["new-cookie=1"]



	@fudge.patch("pycurl.Curl")
	@fudge.patch("StringIO.StringIO")
	def test_method_put_dict_data(self, Curl_Mock, StringIO_Mock):
		(StringIO_Mock.expects_call()
			.returns_fake()
			.provides("write")
			.provides("getvalue").returns("RESPONSE DATA"))

		mock = (Curl_Mock.expects_call()
			.returns_fake())

		# the method under test will call a method that has
		# been passed via setopt(pycurl.WRITEFUNCTION, ...)
		# Intercept the call to define cookies that the
		# server would send
		def get_header_fn(option, value):
			if option == pycurl.HEADERFUNCTION:
				value("Set-Cookie: new-cookie=1")

		mock.expects('setopt').with_args(pycurl.VERBOSE, 0)
		mock.expects('setopt').with_args(pycurl.URL, "http://host/path")

		mock.expects('setopt').with_args(pycurl.CUSTOMREQUEST, "PUT")
		mock.expects('setopt').with_args(pycurl.POSTFIELDSIZE, len("data1=A&data2=B"))
		mock.expects('setopt').with_args(pycurl.POSTFIELDS, "data1=A&data2=B")
		mock.expects('setopt').with_args(pycurl.HTTPHEADER, [
			"Hdr-A: 1",
			"Hdr-B: 2",
			"Content-Type: application/x-www-form-urlencoded; charset=UTF-8"
		])
		mock.expects('setopt').with_args(pycurl.COOKIE, "")
		mock.provides('setopt').calls(get_header_fn)
		mock.expects('setopt').with_args(pycurl.WRITEFUNCTION, arg.any())
		mock.expects('perform')
		mock.has_attr(RESPONSE_CODE="RESPONSE_CODE_MOCK")
		mock.provides('getinfo').calls(lambda _: 200)

		h = http.Http()

		(status, buf, cookies) = h.method("PUT", "http://host/path", {"data1": "A", "data2": "B"}, headers=["Hdr-A: 1", "Hdr-B: 2"])

		assert status == 200
		assert buf == "RESPONSE DATA"
		assert cookies == ["new-cookie=1"]


	@fudge.patch("pycurl.Curl")
	@fudge.patch("StringIO.StringIO")
	def test_method_post_no_data(self, Curl_Mock, StringIO_Mock):
		mock = (Curl_Mock.expects_call()
			.returns_fake())

		mock.expects('setopt').with_args(pycurl.VERBOSE, 0)
		mock.expects('setopt').with_args(pycurl.URL, "http://host/path")

		h = http.Http()

		self.assertRaises(Exception, h.method, "PUT", None)



	@fudge.patch("pycurl.Curl")
	@fudge.patch("StringIO.StringIO")
	def test_method_get(self, Curl_Mock, StringIO_Mock):
		(StringIO_Mock.expects_call()
			.returns_fake()
			.provides("write")
			.provides("getvalue").returns("RESPONSE DATA"))

		mock = (Curl_Mock.expects_call()
			.returns_fake())

		# the method under test will call a method that has
		# been passed via setopt(pycurl.WRITEFUNCTION, ...)
		# Intercept the call to define cookies that the
		# server would send
		def get_header_fn(option, value):
			if option == pycurl.HEADERFUNCTION:
				value("Set-Cookie: new-cookie=1")

		mock.expects('setopt').with_args(pycurl.VERBOSE, 0)
		mock.expects('setopt').with_args(pycurl.URL, "http://host/path")

		mock.expects('setopt').with_args(pycurl.HTTPGET, 1)
		mock.expects('setopt').with_args(pycurl.HTTPHEADER, [
			"Hdr-A: 1",
			"Hdr-B: 2"
		])
		mock.expects('setopt').with_args(pycurl.COOKIE, "")
		mock.provides('setopt').calls(get_header_fn)
		mock.expects('setopt').with_args(pycurl.WRITEFUNCTION, arg.any())
		mock.expects('perform')
		mock.has_attr(RESPONSE_CODE="RESPONSE_CODE_MOCK")
		mock.provides('getinfo').calls(lambda _: 200)

		h = http.Http()

		(status, buf, cookies) = h.method("GET", "http://host/path", headers=["Hdr-A: 1", "Hdr-B: 2"])

		assert status == 200
		assert buf == "RESPONSE DATA"
		assert cookies == ["new-cookie=1"]


	@fudge.patch("pycurl.Curl")
	@fudge.patch("StringIO.StringIO")
	def test_method_raise_http_exception_on_perform_fail(self, Curl_Mock, StringIO_Mock):
		(StringIO_Mock.expects_call()
			.returns_fake()
			.provides("write")
			.provides("getvalue").returns("RESPONSE DATA"))

		mock = (Curl_Mock.expects_call()
			.returns_fake())

		def raise_perform_error():
			raise pycurl.error(42, "PyCURL Exception")

		mock.provides('setopt')
		mock.provides('perform').calls(raise_perform_error)
		mock.has_attr(RESPONSE_CODE="RESPONSE_CODE_MOCK")

		h = http.Http()

		self.assertRaises(http.HttpError, h.method, "GET", None)


	@fudge.patch("pycurl.Curl")
	@fudge.patch("StringIO.StringIO")
	def test_method_raise_original_exception_on_perform_fail(self, Curl_Mock, StringIO_Mock):
		(StringIO_Mock.expects_call()
			.returns_fake()
			.provides("write")
			.provides("getvalue").returns("RESPONSE DATA"))

		mock = (Curl_Mock.expects_call()
			.returns_fake())

		class CustomException(Exception):
			def __init__(self, msg):
				pass

		def raise_perform_error():
			raise CustomException("Custom exception")

		mock.provides('setopt')
		mock.provides('perform').calls(raise_perform_error)
		mock.has_attr(RESPONSE_CODE="RESPONSE_CODE_MOCK")

		h = http.Http()

		self.assertRaises(CustomException, h.method, "GET", None)


	def setUp(self):
		self.mox = mox.Mox()


	def tearDown(self):
		self.mox.UnsetStubs()


	def test_get(self):
		h = http.Http()

		self.mox.StubOutWithMock(h, "method")
		h.method("GET", "http://host/path", None, ["Hdr-A: 1"], ["cookie=abc"]).AndReturn( (200, "Response", ["set-cookie-a=1", "set-cookie-b=2"]) )

		self.mox.ReplayAll()

		h.get("http://host/path", ["Hdr-A: 1"], ["cookie=abc"])

		self.mox.VerifyAll()


	def test_post(self):
		h = http.Http()

		self.mox.StubOutWithMock(h, "method")
		h.method("POST", "http://host/path", "DATA", ["Hdr-A: 1"], ["cookie=abc"]).AndReturn( (200, "Response", ["set-cookie-a=1", "set-cookie-b=2"]) )

		self.mox.ReplayAll()

		h.post("http://host/path", "DATA", ["Hdr-A: 1"], ["cookie=abc"])

		self.mox.VerifyAll()


	def test_put(self):
		h = http.Http()

		self.mox.StubOutWithMock(h, "method")
		h.method("PUT", "http://host/path", "DATA", ["Hdr-A: 1"], ["cookie=abc"]).AndReturn( (200, "Response", ["set-cookie-a=1", "set-cookie-b=2"]) )

		self.mox.ReplayAll()

		h.put("http://host/path", "DATA", ["Hdr-A: 1"], ["cookie=abc"])

		self.mox.VerifyAll()
