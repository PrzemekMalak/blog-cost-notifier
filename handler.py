import json
import os
import boto3

from account import account
from cost import get_all_costs

sns = boto3.client('sns')

def send_notifications(metrics):
    topic_arn = os.environ["SNS_TOPIC"]
    response = sns.publish(
            TopicArn=topic_arn,
            Message=json.dumps(metrics, indent=4)
        )

def send_alarm(metrics):
    topic_arn = os.environ["SNS_ALARM_TOPIC"]
    response = sns.publish(
            TopicArn=topic_arn,
            Message=json.dumps(metrics, indent=4)
        )


def handler(event, context):
    accounts = get_all_costs()
    metrics = []
    alarm = False
    for acc in accounts:
        if acc.previous_cost > 0 and acc.cost / acc.previous_cost >= 3:
            alarm = True
        d={
            'account_id': acc.account_id,
            'name': acc.name,
            'email': acc.email,
            'cost': acc.cost,
            'previous_cost': acc.previous_cost,
            'forecast': acc.forecast,
            'error': acc.error
        }
        metrics.append(d)
    print(metrics)
    if alarm:
        send_alarm(metrics)
    send_notifications(metrics)

if __name__ == "__main__":
    handler(None, None)