from src.db.schema import *
import json
import requests

c = connection
me = c.Member.find_one({'login': 'ds'})
data = {'score': 13, 'assignment': 'hw1', 'submit': True, 'grader_login': 'ta', 'comments': 'tits!', 'login': 'ds'}
j = json.dumps(data)
h = {'content-type': 'application/json'}
aga = 'http://localhost:9001'
