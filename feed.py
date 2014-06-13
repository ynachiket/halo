import requests
import json
from pprint import pprint
from time import sleep

def main():
	token = ''
	url = 'https://atom.prod.dfw1.us.ci.rackspace.net/monitoring/events?format=json&search=%2Bmonitoring.notification.send&direction=backward'
	headers = {
		'X-Auth-Token': token
	}

	while True:
		print url
		data = requests.get(url, headers=headers).json()

		if 'entries' in data['feed']:
			entries = data['feed']['entries']
			url = '%s&format=json' % data['feed']['links'][2].get('href')
		else:
			entries = None

		if entries and type(entries) is not list:
			entries = [entries, ]

		while entries:
			event = entries.pop()
			print event.get('published')
			
			try:
				payload = event.get('content').get('children')[0]
			except:
				continue

			try:
				request = requests.post(url='http://10.20.76.42:5000/webhook', data=payload, timeout=5)
			except:
				pass

		sleep(5)

if __name__ == '__main__':
	main()