import requests

def bt_api(method, endpoint, data):
    headers = {}
    headers["clientid"] = "26bfc822b0e67a564e4f22e0e8d6c5016c4664f7d46a96b3737a9ed8e35fa95d"
    headers["apikey"] = "1veN6i3DbnkCwCcJfsKLq7mYCmu6vejn"
    headers["accept"] = "application/json"
    headers["language"] = "ES"
    headers["Content-Type"] = "application/json"
    url = "http://btcanales.dlya.corp:3007/"
    url = url + endpoint
    if method == "post":
        response = requests.post(url, headers=headers, json=data)
    elif method == "get":
        response = requests.get(url, headers=headers, json=data)
    print(response.json())
    return response.json()