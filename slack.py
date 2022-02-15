import requests
 
def post_slack_message(channel, text):
    myToken = "xoxb-1585926458247-3128170600080-YWdKnEkmFiYXIviJhwAcCNyJ"
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer " + myToken},
        data={"channel": channel,"text": text}
    )
    print(response.json())

 
post_slack_message("#gan-image-nft","Hello bitch")
