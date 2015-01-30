
# PyJiraCli

JIRA CLI written in Python.

# Features

- Search for issues using JQL
- Show issue details
- Post and list comments
- Assign/unassign issues
- Store JQL as named filter
- Can be used via Socks proxies (utilizes libcurl)
- Session information stored encrypted


# Usage overview


```
# search by JQL
pyjiracli.py jql 'project = ACME and status = "In Progress"'

# search by stored filter filter
pyjiracli.py filter 'assigned-to-me-filter'

# get issue details
pyjiracli.py get ACME-42

# show comments
pyjiracli.py comments ACME-42

# comment on issue
pyjiracli.py comment ACME-42 "Ready for review: ..."

# assign issue to user by username (fragment)
pyjiracli.py assign ACME-42 "j.d"
pyjiracli.py assign ACME-42 "j.doe"

# unassign issue
pyjiracli.py unassign ACME-42

# get list of assignees applicable to username (fragment)
pyjiracli.py assignees "j.d"
pyjiracli.py assignees "j.doe"

```

# Status

Development of main featureset done.



# Install & configuration

[Installation and configuration](install.md)



# Requirements

- Python: PyCurl (tested with 7.19.0)
- JIRA with REST API enabled (tested with 6.x)
- Python: fudge 1.0.x (only for unittests)
- Python: mox 0.5.x (only for unittests)

# License

This project is licensed for you under the MIT license.

