import sys
import json
import requests
import faker
import hashlib
from ratelimit import limits, sleep_and_retry


print(sys.version)

# random email generator // f.email()
f = faker.Faker()

@sleep_and_retry
@limits(calls=100, period=1)
def api_call(identifier, url, payload):

	r_session = requests.Session()

	user = ""
	password = ""
	headers = {
		"Content-Type": "application/json",
		"accept": "*/*"
	}


	r = r_session.post(
		url = url+identifier,
		auth = (user, password),
		headers = headers,
		json = payload
	)
	
	if r.status_code not in [200,201]:
		raise(r.text)
	else:
		print(r.status_code)



url = "https://api.relay42.com/v1/site-1268/profiles/7001/facts?forceInsert=false&partnerId="

data = [{
	"factName": "test",
	"factTtl": 99999999,
	"properties": {}
	}]

for i in range(1000):

	dummy_email = f.email()
	sha256_email = hashlib.sha256(dummy_email.encode('utf-8')).hexdigest()

	api_call(identifier=sha256_email, url=url, payload=data)
