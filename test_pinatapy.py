import requests
data = "./images/emilia/Emila_anime_2.png"
from pinatapy import PinataPy
pinata = PinataPy("76669b41b802b55940ee", "88a4a918c5a946cead6bf1e715165f92fddf2082c8f3c7ab9a59c739d10609f4")
result = pinata.pin_file_to_ipfs(data)
print(result)
#반환되는 형식
#{'IpfsHash': 'QmQHBQSYhouMoJN25HLBHXdpDPQNoxXDjdKgLsVyZJbFgc', 'PinSize': 1437097, 'Timestamp': '2022-02-14T18:33:09.802Z'}