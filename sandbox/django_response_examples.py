headers		= response.info()
data		= response.read()

response_url	= response.geturl()
response_date	= headers['date']
