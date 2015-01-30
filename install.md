# How to install and configure

## Install dependencies


Install PyCurl:

```
pip install pycurl
```

## Install

- Place the sources in any directory you like.
- Test the core sources:
```
python -m unittest jira_test
python -m unittest http_test
```
- Add the path to that directory to your `PATH`:
```
export PATH="${PATH}:/path/to/py-jira-cli"
```

## Configure

- Create a file named `.pyjirarc` in your home directory.
- Change its permissions to 0600 (user readable only)
- Save this config:

```
[store]
# file to store encrypted session data, e.g. .pyjirastore
path=<PATH RELATIVE TO .pyjirarc (HOME)>
# password to use to encrypt the session data (should be a multiple of 16 chars)
key=SOMESTRONGPASSWO

[jira]
# URL to the JIRA instance, ending on /rest
url=https://project.com/jira/rest
# your JIRA username
user=<USERNAME>

[filters]
# configure filters: <FILTERNAME>=<JQL>
created-week=project = ACME and created > startOfDay(-7) order by created
```

Note: the session data file `.pyjirastore` does only contain JIRA session cookies, not your password. If the session data is invalidated (forced or by timeout), the session data is no longer valid.


## Using it behind a proxy (firewall)

You can configure a proxy in two ways.

### curl environment variable

Define the following environment variable to your proxy (any of them is valid):

```
ALL_PROXY="socks5h://proxy.company.com:1080"
ALL_PROXY="https://proxy.company.com:3128"
HTTPS_PROXY="https://proxy.company.com:3128"
```

You may also define other valid curl Proxy config values. See also `man curl` (section 1)

### Via configuration

Add this to your `.pyjirarc`

```
[network]
proxy=socks5h://proxy.company.com:1080
```
