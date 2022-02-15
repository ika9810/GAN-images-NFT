import requests

def post_slack_message(channel, text):
    myToken = "YOUR-API-KEY"
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer " + myToken},
        data={"channel": channel,"text": text}
    )
    print(response.json())

 
#post_slack_message("#gan-image-nft","Hello bitch")     ['GAN-API-KEY']
import json
def readSlackAPIKEY():
    with open('/home/opc/GAN-images-NFT/keys/slack-api-key.json', 'r') as f:
        json_data = json.load(f)
    return json_data['GAN-API-KEY']
print(readSlackAPIKEY())