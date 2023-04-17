# MFA Bombing Tester

## Introduction
MFA (Multi-Factor Authentication) is a security measure
used to protect user accounts by requiring more than one
form of authentication. In this way, if one factor is
compromised (e.g. a password), the account can still be protected.
However, attackers can use a technique called MFA bombing to
bypass MFA and gain access to user accounts.

MFA bombing involves sending a large number of authentication
requests to a user's account, overwhelming the user and
tricking them into approving a fraudulent request. This
technique can be used to bypass MFA that uses push notifications.

To protect your users from MFA bombing, it's important to educate
them on the topic and encourage them to be cautious when
approving authentication requests.

## About the Tool
The MFA Bombing Tester is a tool that scans your Okta organization
for users with push authentication factor. When it finds one,
it sends a push notification to the user to make them click on it.
This helps you test your organization's resilience to MFA bombing
attacks and identify potential vulnerabilities.

The tool is written in Python and uses the Okta API to scan
your organization for push-enabled users. It then sends a push
notification to each user and waits for a response.
If a user clicks on the push notification, the tool reports
a successful authentication attempt. In the end a report is saved
to a CSV file containing the list of users along with the results
of the test for each one.


## How to Use the Tool

### Requirements
* Python 3.8 and up
* Okta API token
* [Poetry](https://python-poetry.org/)

### Running the tool

1. Clone the repo.
2. Create the file `config.yaml` with your Okta config (use `config.yaml.example` for reference)
3. Run using Poetry: 
```commandline
poetry run python mfa_bombing_tester.py [path/to/report.csv]
```
4. Read output report (default is to save to `report.csv`). 
It contains the columns user_id, user_email, and result.

If you don't want to use Poetry, you can use python but need to install the Okta SDK first
```commandline
pip install fire PyYAML okta
python mfa_bombing_tester.py [path/to/report.csv]
```


## Future work
* Support more platforms (AzureAD, Google Workspace, PingIdentity)
