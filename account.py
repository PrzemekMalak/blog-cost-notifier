import json

class account:
    def __init__(self, account_id=None, name=None, email=None):
        self.account_id = account_id
        self.name = name
        self.email = email
        self.cost = 0.0
        self.previous_cost = 0.0
        self.forecast = 0.0
        self.error = ''

    def __str__(self):
        return(json.dumps(vars(self)))


