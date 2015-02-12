
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


class CompositeStyledTest(unittest.TestCase):

	"""It should return the sum length of both strings"""
	def test_str_concat(self):
		# using strings.
		# any class implementing __str__() and __len__() should work
		comp = printer.CompositeStyled("123", "4567")

		self.assertEqual(str(comp), "1234567", "__str__() should concat A + B")

	"""It should return the concatenated strings """
	def test_sen_sum(self):
		# using strings.
		# any class implementing __str__() and __len__() should work
		comp = printer.CompositeStyled("123", "4567")

		self.assertEqual(len(comp), 7, "Sum length should be sum of A + B")



class StyledTest(unittest.TestCase):

	def setUp(self):
		# changing this during test: save original value
		self._orig_styled_use_color = printer.Styled.use_color
		self._orig_styled_fg = printer.Styled.fg
		self._orig_styled_bg = printer.Styled.bg
		self._orig_styled_reset = printer.Styled.reset

	def tearDown(self):
		printer.Styled.use_color = self._orig_styled_use_color
		printer.Styled.fg = self._orig_styled_fg
		printer.Styled.bg = self._orig_styled_bg
		printer.Styled.reset = self._orig_styled_reset


	def test_no_color_str_and_len(self):
		printer.Styled.use_color = False

		styled = printer.Styled("1234")

		self.assertEqual(str(styled), "1234", "__str__() returns raw string")
		self.assertEqual(len(styled), 4, "len() returns raw string's length")

	def test_no_color_concat_to_str(self):
		printer.Styled.use_color = False

		styled = printer.Styled("1234")

		concated = styled + "ABC"

		self.assertEqual(str(concated), "1234ABC", "__str__() returns raw string")
		self.assertEqual(len(concated), 7, "len() returns both string raw length")
		self.assertEqual(type(concated), printer.CompositeStyled, "Styled() + str() returns CompositeStyled")

	def test_no_color_concat_to_styled(self):
		printer.Styled.use_color = False

		styled = printer.Styled("1234")

		concated = styled + printer.Styled("9876")

		self.assertEqual(str(concated), "12349876", "__str__() returns raw string")
		self.assertEqual(len(concated), 8, "len() returns both string raw length")
		self.assertEqual(type(concated), printer.CompositeStyled, "Styled() + str() returns CompositeStyled")

	def test_using_color_str_and_len(self):
		printer.Styled.use_color = True
		printer.Styled.fg = {"red": "[R]"}
		printer.Styled.bg = {"green": "[G]"}
		printer.Styled.reset = "[_]"

		styled = printer.Styled("1234", fore=printer.Styled.fg["red"], back=printer.Styled.bg["green"])

		self.assertEqual(str(styled), "[R][G]1234[_]", "__str__() returns raw string")
		self.assertEqual(len(styled), 4, "len() returns raw string's length")

	def test_using_color_concat_to_str(self):
		printer.Styled.use_color = True
		printer.Styled.fg = {"red": "[R]", "yellow": "[Y]"}
		printer.Styled.bg = {"green": "[G]", "blue": "[B]"}
		printer.Styled.reset = "[_]"

		styled = printer.Styled("1234", fore=printer.Styled.fg["red"], back=printer.Styled.bg["green"])

		concated = styled + "ABC"

		self.assertEqual(str(concated), "[R][G]1234[_]ABC", "__str__() returns raw string")
		self.assertEqual(len(concated), 7, "len() returns both string raw length")
		self.assertEqual(type(concated), printer.CompositeStyled, "Styled() + str() returns CompositeStyled")

	def test_using_color_concat_to_styled(self):
		printer.Styled.use_color = True
		printer.Styled.fg = {"red": "[R]", "yellow": "[Y]"}
		printer.Styled.bg = {"green": "[G]", "blue": "[B]"}
		printer.Styled.reset = "[_]"

		styled = printer.Styled("1234", fore=printer.Styled.fg["red"], back=printer.Styled.bg["green"])

		concated = styled + printer.Styled("9876", fore=printer.Styled.fg["yellow"], back=printer.Styled.bg["blue"])

		self.assertEqual(str(concated), "[R][G]1234[_][Y][B]9876[_]", "__str__() returns raw string")
		self.assertEqual(len(concated), 8, "len() returns both string raw length")
		self.assertEqual(type(concated), printer.CompositeStyled, "Styled() + str() returns CompositeStyled")

