
# Changelog

## 2015-02-13 - v0.2

- Better output formatting
- Colored output formatting if "ansi" module is available
- Progressbar for sub task progress based on resolved/close state
- Added command aliases:
	- Query issues (jql): search, query
	- Show issue details (get): show, issue

## 2015-02-14 - v0.3

- Assign issues to the current user using "assignme" (alias "tome")
- Made filter/query display limit configurable by a switch: -l/--limit
- Raised the default for that limit from 10 to 50
- Fixed encoding bug in comment listing
- Fixed date rendering in comment listing

## 2015-02-21 - v0.4

- Highlight username and parent issue in query result list
- Show author in comment listing
- Mark edited comments with "*"
- Improved progressbar rendering in issue result list
	- Do not distinguish between resolved and closed
	- Render last done segment with "~" if the undone issues can't be rendered to a char
- Fixed error when showing subtasks in card
- Fixed multiline text rendering for description and comment: respect newlines when wrapping text
