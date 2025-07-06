import requests 
url = "https://opentdb.com/api.php?amount=10" 
reponse = requests.get(url) 
print(reponse.content.decode())