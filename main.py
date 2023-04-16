import asyncio
from asyncio import sleep
from pathlib import Path
from typing import List

import yaml
from okta import models
from okta.client import Client as OktaClient


class MFAChallenger:
    def __init__(self):
        with Path("config.yaml").open() as config_file:
            config = yaml.safe_load(config_file)

        okta_config = {
            'orgUrl': config['okta_domain'],
            'token': config['okta_token'],
        }
        self.okta_client = OktaClient(okta_config)

    async def challenge_user(self, user: models.User):
        factors, resp, err = await self.okta_client.list_factors(user.id)
        factors: List[models.PushUserFactor]  # type hinting
        push_factors = [factor for factor in factors if factor.factor_type == 'push']
        for factor in push_factors:
            print(f"Found push factor for user {user.profile.email}. Challenging.")
            verify_factor_transaction, verify_factor_response, err = await self.okta_client.verify_factor(
                user.id, factor.id, models.VerifyFactorRequest(),
            )
            transaction_id = verify_factor_transaction.links['poll']['href'].split("/")[-1]
            while True:
                polling_factor_response, _, err = await self.okta_client.get_factor_transaction_status(
                    user.id,
                    factor.id,
                    transaction_id,
                )
                polling_factor_response: models.VerifyUserFactorResponse
                if polling_factor_response.factor_result != 'WAITING':
                    if polling_factor_response.factor_result == 'SUCCESS':
                        print(f"ALERT: User {user.profile.email} with id {user.id} approved the push notification")
                    else:
                        print(f"User {user.profile.email} didn't approve the push notification")
                    break

                await sleep(1)

    async def search_and_challenge_users(self):
        users, resp, err = await self.okta_client.list_users()
        for user in users:
            # print(user.profile.first_name, user.profile.last_name)
            await self.challenge_user(user)


if __name__ == '__main__':
    mfa_challenger = MFAChallenger()
    asyncio.run(mfa_challenger.search_and_challenge_users())
