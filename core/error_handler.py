import time

import core.config as mem

from core.colors import bad

def connection_refused():
	if mem.var['stable']:
		print('%s Hit rate limit, stabilizing the connection'  % bad)
		mem.var['kill'] = False
		time.sleep(30)
		return 'retry'
	print('%s Target has rate limiting in place, please use --stable switch' % bad)
	return 'kill'

def error_handler(response, factors):
	if type(response) != str and response.status_code in (400, 503, 429):
		if response.status_code == 400:
			if factors['same_code'] != 400:
				mem.var['kill'] = True
				print('%s Server recieved a bad request. Try decreasing the chunk size with -c option'  % bad)
				return 'kill'
			else:
				return 'ok'
		elif response.status_code == 503:
			mem.var['kill'] = True
			print('%s Target is unable to process requests, try --stable switch' % bad)
			return 'kill'
		elif response.status_code == 429:
			return connection_refused()
	else:
		if 'Timeout' in response:
			if mem.var['timeout'] > 20:
				mem.var['kill'] = True
				print('%s Connection timed out, unable to increase timeout further')
				return 'kill'
			else:
				print('%s Connection timed out, increased timeout by 5 seconds'  % bad)
				mem.var['timeout'] += 5
				return 'retry'
		elif 'ConnectionRefused' in response:
			return connection_refused()
		elif type(response) == str:
			return 'kill'
	return 'ok'
