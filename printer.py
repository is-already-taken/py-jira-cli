
import datetime
import math
from textwrap import wrap

"""
Align text into columns [("a", 10), ("b", 10), ("c", 20), ...]

cols is a list of (text, width) tupels
width is the screenwidth to fit into if the sum width is < width
"""
def _align(cols, width=80):
	if len(cols) < 2:
		return str(cols[0][0])

	# for c in cols:
	# 	print "%s ==> %d" % (c[0], len(c[0]))

	def pad_left(s, l):
		return " " * (l - len(s)) + str(s)

	def pad_right(s, l):
		return str(s) + " " * (l - len(s))

	def pad_center(s, l):
		d = (l - len(s))
		return " " * int(math.floor(float(d) / 2)) + str(s) + " " * int(math.ceil(float(d) / 2))

	# sum colum width
	sum_width = sum(map(lambda col: max(col[1], len(col[0])), cols))

	# need to add this to first column; ensure it's not negative
	diff = max(0,  width - sum_width)

	first = cols[0]
	s = pad_right(first[0], first[1]) + (" " * diff)

	mids = cols[1:-1]
	for mid in mids:
		s += pad_center(mid[0], mid[1])

	last = cols[-1]
	s += pad_left(last[0], last[1])

	return s

"""Concatenates two Styled instances"""
class CompositeStyled(object):

	def __init__(self, a, b):
		self._a = a
		self._b = b

	"""Return both stringified (styled) text fragments"""
	def __str__(self):
		return str(self._a) + str(self._b)

	"""Return sum of lengths of both Styled() or Styled() + string lengths"""
	def __len__(self):
		return len(self._a) + len(self._b)

"""Wrap string with styles if a coloring module is available. Provides the correct length when using len(...)"""
class Styled():
	def __init__(self, s, fore=None, back=None):
		self._str = s
		self._fg = fore if fore != None else None
		self._bg = back

	"""Return styled string if coloring is available"""
	def __str__(self):
		if not Styled.use_color or self._fg == None:
			# directly return string
			return str(self._str)

		# add fg color at least
		colors = [self._fg]

		# optionally add bg color
		if self._bg != None:
			colors.append(self._bg)

		# add string and reset
		colors.extend([self._str, Styled.reset])

		return "".join(map(str, colors))

	"""Get length of this styled text with stlying control chars excluded"""
	def __len__(self):
		return len(self._str)

	"""Handle Styled() + Styled() and Syyled() + "string" concatenation by wrapping both"""
	def __add__(self, other):
		return CompositeStyled(self, other if type(other) == Styled else Styled(other))


# define only colors used so far
Styled.fg = {
	"black": None,
	"red": None,
	"yellow": None,
	"green": None,
	"blue": None,
	"magenta": None,
	"brightgreen": None,
	"darkgrey": None,
	"grey": None,
	"white": None
}

Styled.bg = {
	"black": None,
	"red": None,
	"yellow": None,
	"green": None,
	"blue": None,
	"magenta": None,
	"brightgreen": None,
	"darkgrey": None,
	"grey": None,
	"white": None
}

Styled.reset = None


try:
	# try to import and set ansi colors

	from ansi.colour import fg, bg, fx

	# Store flag whether to use colors or not
	Styled.use_color = True

	Styled.fg["black"] = fg.black
	Styled.fg["red"] = fg.red
	Styled.fg["green"] = fg.green
	Styled.fg["blue"] = fg.blue
	Styled.fg["yellow"] = fg.yellow
	Styled.fg["brightgreen"] = fg.brightgreen
	Styled.fg["grey"] = fg.grey
	Styled.fg["darkgrey"] = fg.darkgrey
	Styled.fg["white"] = fg.white
	Styled.fg["brown"] = fg.brown

	Styled.bg["black"] = bg.black
	Styled.bg["red"] = bg.red
	Styled.bg["green"] = bg.green
	Styled.bg["blue"] = bg.blue
	Styled.bg["yellow"] = bg.yellow
	Styled.bg["brightgreen"] = bg.brightgreen
	Styled.bg["grey"] = bg.grey
	Styled.bg["darkgrey"] = bg.darkgrey
	Styled.bg["white"] = bg.white

	Styled.reset = fx.reset

except Exception as e:
	Styled.use_color = False


"""Standard printer that uses styling throug Styled (falls back to unstyled if not available)"""
class Printer(object):

	color_map = {
		"Open": [Styled.fg["white"], Styled.bg["blue"]],
		"Reopened": [Styled.fg["white"], Styled.bg["blue"]],
		"In Progress": [Styled.fg["yellow"], Styled.bg["black"]],
		"Resolved": [Styled.fg["brightgreen"], Styled.bg["black"]],
		"Closed": [Styled.fg["black"], Styled.bg["green"]]
	}

	me_assigned_color = [Styled.fg["blue"], Styled.bg["yellow"]]


	def __init__(self, width=80, me=None):
		self._me = me
		self._width = width


	def oneline(self, issue, color_key=True, show_subtasks=True):
		status = issue._status
		status_fg, status_bg = self.color_map[status]

		if status == "In Progress" and issue._assignee != None and issue._assignee == self._me:
			status_fg, status_bg = self.me_assigned_color

		s = "%s %s -- %s" % (
			Styled(issue._key, Styled.fg["white"]) if color_key else issue._key,
			Styled(status, status_fg, status_bg),
			issue._summary
		)

		if issue._parent != None:
			s += str(Styled(" ^", Styled.fg["brown"]) + Styled(issue._parent._key, Styled.fg["darkgrey"]))

		if issue._assignee != None:
			s += str(Styled(" @", Styled.fg["brown"]) + Styled(issue._assignee, Styled.fg["darkgrey"]))

		if len(issue._subtasks) != 0 and show_subtasks:
				s += str(Styled(" [%d Subtasks]" % (len(issue._subtasks)), Styled.fg["grey"]))

		return s

	def tree(self, issue):
		status = issue._status
		status_fg, status_bg = self.color_map[status]

		s = self.oneline(issue, show_subtasks=False)

		if len(issue._subtasks) > 0:
			s += " " + self._progress(issue._subtasks) + "\n"

		if len(issue._subtasks) != 0:
			for subtask in issue._subtasks[0:-1]:
				s += " |- " + self.oneline(subtask, color_key=False) + "\n"

			s += " `- " + self.oneline(issue._subtasks[-1], color_key=False) + "\n"

		return s

	"""Render progressbar for subtask list's closed/resolved progress"""
	def _progress(self, subtasks, length=10):
		overall = len(subtasks)

		done = len(filter(lambda issue: issue._status == "Resolved" or issue._status == "Closed", subtasks))
		undone = overall - done

		pct_done = int(math.floor((float(done) / overall) * length))
		pct_undone = int(math.floor((float(undone) / overall) * length))

		# array that composes the parts of the progress bar
		pct_parts = [pct_done, 1 if undone != pct_undone else 0, pct_undone]

		# zip part count and symbol together
		parts = zip(pct_parts, ["=", "~", " "])

		# map that tupel by multipying the symbol (1) with the count (0)
		parts = map(lambda x: x[1] * x[0], parts)

		# 1. zip segments and colors together
		# 2. wrap with Styled()
		parts = map(lambda x: str(Styled(x[0], x[1])), zip(parts, [Styled.fg["brightgreen"], Styled.fg["green"], None]))

		return "["+ "".join(parts) +"]"


	"""Print text formated as headline"""
	def _headline(self, text):
		return Styled(text, Styled.fg["darkgrey"], Styled.bg["black"])


	"""Print horizontal ruler line """
	def _ruler(self):
		return str(self._headline("-" * self._width))

	def _format_date(self, timestamp):
		return datetime.datetime.utcfromtimestamp(timestamp).strftime("%d.%m.%y %H:%M")

	def card(self, issue):
		status = issue._status

		# get color for status
		status_colors = self.color_map[status]

		# print KEY, TYPE, STATE header
		s = _align([
			(Styled(issue._key, Styled.fg["white"]), 10),
			(self._headline("Type: ") + issue._type, 20),
			(self._headline("Status: ") + Styled(status, status_colors[0], status_colors[1]), 20)
		], width=self._width) + "\n"

		s += self._ruler() + "\n"

		# UPDATED
		s += str(self._headline("Updated: ") + self._format_date(issue._updated)) + "\n"

		# RULER, PARET ISSUE
		if issue._parent != None:
			s +=  self._ruler() + "\n"
			s +=  str("Parent: %s" % (self.oneline(issue._parent))) + "\n"

		s +=  self._ruler() + "\n"

		# SUMMARY
		s +=  issue._summary + "\n"

		s +=  self._ruler() + "\n"

		# DESCCRIPTION
		s +=  "\n".join(wrap(issue._description, width=self._width)) + "\n"

		# RULER, SUBTASK LIST
		if len(issue._subtasks) > 0:
			s +=  self._ruler() + "\n"
			s +=  str(self._headline("Subtasks")) + "\n"
			s +=  "\n"
			s +=  "\n".join(["  - " + self.oneline(sub_task) for sub_task in issue._subtasks]) + "\n"

		return s


	def comments(self, comments):
		s = ""

		for comment in comments:
			date = self._format_date(comment._created)
			s += "--- %s %s" % (date, "-" * (self._width - len(date))) + "\n"
			s += comment._body + "\n"
			s += "\n"

		return s
