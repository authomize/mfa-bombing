import asyncio
from asyncio import sleep
from pathlib import Path
from time import time
from typing import List

import yaml
from fire import Fire
from okta import models
from okta.client import Client as OktaClient
import okta.api_response

class MFAChallenger:
    def __init__(self):
        with Path("config.yaml").open() as config_file:
            config = yaml.safe_load(config_file)

        okta_config = {
            'orgUrl': config['okta_domain'],
            'token': config['okta_token'],
        }
        print(f"Running MFA bombing tests on org {config['okta_domain']}."
              f" Searching for users with push notification factor configured.")
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
                    print(f"Still waiting for response or timeout from user {user.profile.email}"
                          f" (waited {round(time_passed)} seconds)")
                polling_factor_response: models.VerifyUserFactorResponse
                if polling_factor_response.factor_result != 'WAITING':
                    if polling_factor_response.factor_result == 'SUCCESS':
                        print(f"ALERT: User {user.profile.email} with id {user.id} approved the push notification")
                        return "User approved the challenge"
                    else:
                        # print(f"User {user.profile.email} didn't approve the push notification")
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

def mfa_bombing_tester(output_file_path="report.csv"):
    mfa_challenger = MFAChallenger()
    users, results = asyncio.run(mfa_challenger.search_and_challenge_users())
    with Path(output_file_path).open('w') as f:
        f.write("user_id,user_email,result\n")
        for user, result in zip(users, results):
            f.write(",".join([user.id, user.profile.email, result]))
            f.write("\n")


if __name__ == '__main__':
    Fire(mfa_bombing_tester)
