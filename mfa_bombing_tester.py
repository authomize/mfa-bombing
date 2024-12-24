import asyncio
from asyncio import sleep
from pathlib import Path
from time import time
from typing import List
import argparse
import os

from okta import models
from okta.client import Client as OktaClient
import okta.api_response

class MFAChallenger:
    def __init__(self, okta_domain: str, okta_token: str):
        # Now the Okta domain and token come from command-line arguments
        print(f"Running MFA bombing tests on org {okta_domain}. "
              f"Searching for users with push notification factor configured.")
        okta_config = {
            'orgUrl': okta_domain,
            'token': okta_token,
        }
        self.okta_client = OktaClient(okta_config)

    async def challenge_user(self, user: models.User):
        factors, resp, err = await self.okta_client.list_factors(user.id)
        factors: List[models.PushUserFactor]  # type hinting
        push_factors = [factor for factor in factors if factor.factor_type == 'push']
        if len(push_factors) == 0:
            return "No push factors found"
        if len(push_factors) > 1:
            print(f"Warning: User {user.profile.email} has more than one push factor. "
                  f"The program will only challenge one of them.")
        for factor in push_factors:
            print(f"Found push factor for user {user.profile.email}. Challenging.")
            verify_factor_transaction, _, err = await self.okta_client.verify_factor(
                user.id, factor.id, models.VerifyFactorRequest(),
            )
            transaction_id = verify_factor_transaction.links['poll']['href'].split("/")[-1]
            start_time = time()
            while True:
                polling_factor_response, _, err = await self.okta_client.get_factor_transaction_status(
                    user.id,
                    factor.id,
                    transaction_id,
                )
                time_passed = time()-start_time
                if round(time_passed) % 20 == 0:
                    print(f"Still waiting for response or timeout from user {user.profile.email} "
                          f"(waited {round(time_passed)} seconds)")
                polling_factor_response: models.VerifyUserFactorResponse
                if polling_factor_response.factor_result != 'WAITING':
                    if polling_factor_response.factor_result == 'SUCCESS':
                        print(f"ALERT: User {user.profile.email} with id {user.id} approved the push notification")
                        return "User approved the challenge"
                    else:
                        return "User rejected the challenge"

                await sleep(1)

    async def search_and_challenge_users(self):
        users, resp, err = await self._get_users()
        tasks = [asyncio.create_task(self.challenge_user(user)) for user in users]
        results = await asyncio.gather(*tasks)
        return users, results

    async def _get_users(self):
        all_users = []
        
        users, resp, err = await self.okta_client.list_users(dict(limit=100, filter=f"status eq \"ACTIVE\""))
        all_users.extend(users)

        while resp.has_next():
            # Use anext() to get the next result from the async generator
            next_result = await anext(resp.get_next())
            users, next_resp, err = next_result
            all_users.extend(users)

        return all_users, resp, err

def mfa_bombing_tester(okta_domain: str, okta_token: str, output_file_path="report.csv"):
    mfa_challenger = MFAChallenger(okta_domain, okta_token)
    users, results = asyncio.run(mfa_challenger.search_and_challenge_users())
    with Path(output_file_path).open('w') as f:
        f.write("user_id,user_email,result\n")
        for user, result in zip(users, results):
            f.write(",".join([user.id, user.profile.email, result]))
            f.write("\n")


if __name__ == '__main__':
    # Set up argument parser to get values from command line
    parser = argparse.ArgumentParser(description="MFA Bombing Tester")
    parser.add_argument('--okta_domain', required=True, help="Okta Domain URL (e.g., https://your-org.okta.com)")
    parser.add_argument('--okta_token', required=True, help="Okta API Token")
    parser.add_argument('--output_file', default="report.csv", help="Path to save the output report (default: report.csv)")

    # Parse the command line arguments
    args = parser.parse_args()

    # Call the function with the command-line arguments
    mfa_bombing_tester(args.okta_domain, args.okta_token, args.output_file)
