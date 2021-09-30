# Example posting a image URL:

import requests
r = requests.post(
    "https://api.deepai.org/api/fast-style-transfer",
    data={
        'content': 'YOUR_IMAGE_URL',
        'style': 'YOUR_IMAGE_URL',
    },
    headers={'api-key': '7b134cc2-6b1d-485c-a484-f4d14148af8e'}
)
print(r.json())


# Example posting a local image file:

import requests
r = requests.post(
    "https://api.deepai.org/api/fast-style-transfer",
    files={
        'content': open('/path/to/your/file.jpg', 'rb'),
        'style': open('/path/to/your/file.jpg', 'rb'),
    },
    headers={'api-key': '7b134cc2-6b1d-485c-a484-f4d14148af8e'}
)
print(r.json())

#reference : https://deepai.org/machine-learning-model/fast-style-transfer
