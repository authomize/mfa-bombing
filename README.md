# MFA Bombing Tools for Okta
This GitHub repository contains a couple of tools that
relate to MFA bombing with Okta, a cloud-based identity
and access management platform. MFA bombing is a form
of social engineering attack that involves sending a
large number of MFA prompts to a user until the user
gets fatigued by the prompts and approves one of them.
The goal of this attack is to gain access to sensitive
information or resources that require MFA for authentication.

## Disclaimer
This tool is intended for educational purposes only.
The author is not responsible for any misuse or damage caused by this tool.
Use at your own risk.

## Tools
This repository contains two tools:

* **MFA Bomber**: This tool bombards a user with MFA 
push prompts until the user approves one of them.
The tool works with Okta and requires a valid username and password.
* **MFA Bombing Tester**: This tool scans an Okta organization for all users with push MFA prompts configured and triggers them to see who approves. The tool interacts with the Okta API using a token, so it doesn't require a Chrome driver to function.

## How to Use

### Requirements
* Python 3.8 and up
* Okta API token (for the MFA tester)
* [Poetry](https://python-poetry.org/)

### MFA Bomber
To use the MFA Bomber tool, follow these steps:

1. Clone the repository to your local machine.
2. Install poetry: `pip install poetry`
3. Run the script with the following command: 
`poetry run python mfa_bomber.py <okta_domain> <username> <password>`.

Note - If you don't want to use poetry you can install dependencies manually using the `requirements.txt` file.

Note that the tool can take some time to run,
since it will wait for the user to approve the push,
and if it gets rejected, it'll wait some time and then retry.

### MFA Bombing Tester
To use the MFA Bombing Tester tool, follow these steps:

1. Clone the repository to your local machine.
2. Install poetry: `pip install poetry`
2. Create the file `config.yaml` with your Okta config (use `config.yaml.example` for reference)
3. Run using Poetry: 
```commandline
poetry run python mfa_bombing_tester.py [path/to/report.csv]
```

Note - If you don't want to use poetry you can install dependencies manually using the `requirements.txt` file.

The tool will scan your Okta organization for all users with push MFA prompts configured and trigger them to see who approves.
The tool will save the results to a file (defaults to `report.csv`).


## Future work
* Support more platforms (AzureAD, Google Workspace, PingIdentity)
