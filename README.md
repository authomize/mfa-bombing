# MFA Bombing Tools for Okta
This GitHub repository contains a couple of tools that relate to MFA bombing on accounts in Okta, MFA Bombing is also sometimes known as "MFA Fatigue Attack", "MFA Spamming", and other names... 

MFA bombing is a form of social engineering attack that involves sending a large number of MFA prompts to a user until the user gets fatigued by the prompts and approves one of them. The goal of this attack is to gain access to sensitive information or resources that require multi-factor authentication and the general assumption is that you have already compromised a user and a password. 

The repository includes a red-team tool focused on attacking a specific account in a black box scenario and a purple-team tool focused on testing your user's awareness and assuming either insider access or an initial level of privilege. 

You can assume that the tools could be used standalone after an threat actor gained access to valid credentials or in conjunction with performing #PassBleed attack on Okta - a cloud credential dumping attack allowing Okta app admins (insiders or compromised accounts) to gain access to the Okta username + clear text password for any account. [This tool provides an open source example of the #PassBleed attack](https://github.com/authomize/okta_scim_attack_tool).


## Disclaimer
This tool is intended only for educational purposes or for allowed red-team or purple-team activities only. 
Authomize or the authors and contributors are not responsible for any misuse or damage caused by this tool. Use at your own risk.


## Tools
This repository contains two tools:

* **MFA Bomber**: [Red Team] This tool bombards a user with MFA push prompts until the user approves one of them. The tool works with Okta and requires a valid username and password.
* **MFA Bombing Tester**: [Purple Team] This tool scans an Okta organization for all users with push MFA prompts configured and triggers them to see who approves. The tool interacts with the Okta API using a token, so it doesn't require a Chrome driver to function. 


## How to Use

### Requirements
* Python 3.8 and up
* Okta API token (for the MFA tester)
* [Poetry](https://python-poetry.org/)

### MFA Bomber
To use the MFA Bomber tool, follow these steps:

1. Clone the repository to your local machine.
2. Using poetry:
   1. Install poetry: `pip install poetry`
   2. Run using Poetry: 
    ```commandline
    poetry run python mfa_bomber.py <okta_domain> <username> "<password>"
    ```
   Note - it's best to put quotes around the password to account for the case where it contains special chars.
3. Without poetry (skip this if you used poetry):
   1. Install dependencies `pip install -r requirement.txt`
   2. Run:
    ```commandline
    poetry run python mfa_bomber.py <okta_domain> <username> <password>
    ```

Note that the tool can take some time to run,
since it will wait for the user to approve the push,
and if it gets rejected, it'll wait some time and then retry.

### MFA Bombing Tester
To use the MFA Bombing Tester tool, follow these steps:

1. Clone the repository to your local machine.
2. Create the file `config.yaml` with your Okta config (use `config.yaml.example` for reference)
3. Using poetry:
   1. Install poetry: `pip install poetry`
   2. Run using Poetry: 
    ```commandline
    poetry run python mfa_bombing_tester.py [path/to/report.csv]
    ```
4. Without poetry (skip this step if you used poetry):
   1. Install dependencies `pip install -r requirement.txt`
   2. Run: `python mfa_bombing_tester.py [path/to/report.csv]`

The tool will scan your Okta organization for all users with push MFA prompts configured and trigger them to see who approves.
The tool will save the results to a file (defaults to `report.csv`).


## Future work
* Support more platforms (AzureAD, Google Workspace, PingIdentity)
