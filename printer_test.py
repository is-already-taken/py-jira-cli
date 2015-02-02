
import unittest
import printer

class PrinterTest(unittest.TestCase):

	"""It should print the expected one column text"""
	def test_one_column(self):
		s = printer._align([("XYZ", 20)], width=80)

		self.assertEqual(len(s), 3, "overall width")
		self.assertEqual(s, "XYZ", "correct output")

	"""It should print the expected two column text"""
	def test_two_column(self):
		s = printer._align([("XYZ", 20), ("ABC", 10)], width=80)

		self.assertEqual(len(s), 80, "overall width")
		self.assertEqual(s, "XYZ" + (" " * 67) + (" " * 7) + "ABC", "correct output")

	"""It should print the expected three column text"""
	def test_three_column(self):
		s = printer._align([("XYZ", 20), ("PQR", 5), ("ABC", 10)], width=80)

		self.assertEqual(len(s), 80, "overall width")
		self.assertEqual(s, "XYZ" + (" " * 17) + (" " * 45) + " PQR " + (" " * 7) + "ABC", "correct output")

	"""It should print the expected four column text"""
	def test_four_column(self):
		s = printer._align([("XYZ", 20), ("PQR", 5), ("ABC", 10), ("123", 20)], width=80)

		self.assertEqual(len(s), 80, "overall width")
		self.assertEqual(s, "XYZ" + (" " * 17) + (" " * 25) + " PQR " + (" " * 3) + "ABC" + (" " * 4) + (" " * 17) + "123", "correct output")

	"""It should not exceed max column"""
	def test_do_not_exceed_max_col(self):
		s = printer._align([("EXEED TO EIGHTTEEN", 10), ("PQR", 5), ("ABC", 10)], width=80)

		self.assertEqual(len(s), 80, "overall width")
		self.assertEqual(s, "EXEED TO EIGHTTEEN" + (" " * 47) + " PQR " + (" " * 7) + "ABC", "correct output")

	"""It exceed max column, when all strings in sum exceed"""
	def test_do_not_exceed_max_col(self):
		s = printer._align([("EXEED TO EIGHTTEEN", 10), ("PQR", 5), ("ABC", 10)], width=25)

		self.assertEqual(len(s), 33, "overall width")
		self.assertEqual(s, "EXEED TO EIGHTTEEN" + " PQR " + (" " * 7) + "ABC", "correct output")


	#
	# Styled() is not tested, I havn't figured out how
	# to mock module import errors
	#
