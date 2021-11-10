import os
import boto3
import json
import botocore
import logging

from account import account
from days import last_day_of_current_month, first_day_of_current_month, first_day_of_next_month, today


logger = logging.getLogger()
logger.setLevel(logging.ERROR)

def get_accounts():
    accounts = []
    org = boto3.client('organizations')
    acc_paginator = org.get_paginator('list_accounts')
    page_iterator = acc_paginator.paginate()

    for page in page_iterator:        
        for acct in page['Accounts']:
            acc = account(acct['Id'], acct['Name'], acct['Email'])
            accounts.append(acc)

    return accounts

def get_total_cost_and_usage( accounts):
    account_metrics = get_cost_and_usage(accounts, first_day_of_current_month(), first_day_of_next_month())
    for metric in account_metrics:
        for x in accounts:
            if x.account_id == metric['Keys'][0]:
                x.cost = float(metric['Metrics']['NetUnblendedCost']['Amount'])
                break
    return accounts


def get_previous_cost_and_usage(accounts):
    account_metrics = get_cost_and_usage(accounts, first_day_of_current_month(), today())
    for metric in account_metrics:
        for x in accounts:
            if x.account_id == metric['Keys'][0]:
                x.previous_cost = float(metric['Metrics']['NetUnblendedCost']['Amount'])
                break

    accounts.sort(key=lambda x: x.cost, reverse=True)
    return accounts

def get_cost_and_usage(accounts, first_day, last_day):
    ce_client = boto3.client('ce')

    response = ce_client.get_cost_and_usage(
        TimePeriod={
            'Start': str(first_day),
            'End': str(last_day)
        },
        Granularity='MONTHLY',
        
        Metrics=[
            'NET_UNBLENDED_COST',
        ],
        GroupBy=[
            {
                'Type': 'DIMENSION',
                'Key': 'LINKED_ACCOUNT'
            },
        ]
    )

    metrics = response['ResultsByTime'][0]['Groups']
    return metrics

def get_cost_forecast(accounts):
    ce_client = boto3.client('ce')
    for account in accounts:
        get_cost_forecast_for_account(ce_client, account)
    return accounts


def get_cost_forecast_for_account(client, account):
    try:
        response = client.get_cost_forecast(
            TimePeriod={
                'Start': str(today()),
                'End': str(first_day_of_next_month())
            },
            Granularity='MONTHLY',
            Metric='NET_UNBLENDED_COST',
            Filter={
        
            'Dimensions': {
                'Key': 'LINKED_ACCOUNT',
                'Values': [
                    account.account_id,
                ],
                'MatchOptions': [
                    'EQUALS',
                ]
            }
            }
        )
        account.forecast = response['ForecastResultsByTime'][0]['MeanValue']
        logger.info(json.dumps(response))
    except botocore.exceptions.ClientError as error:
        logger.error(error)
        account.error = str(error)

def get_all_costs():
    accounts = get_accounts()
    accounts = get_total_cost_and_usage(accounts)
    accounts = get_previous_cost_and_usage(accounts)
    metrics = get_cost_forecast(accounts)
    return metrics
