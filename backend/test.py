import requests

url = 'http://localhost:3333/upload'
file = {'file': open('../Interview/AMAZON COM INC | 8-K (February 02, 2023).html', 'rb')}
resp = requests.post(url=url, files=file) 
print(resp.json())