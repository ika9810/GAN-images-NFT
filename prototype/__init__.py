from flask import Flask, request
from flask_cors import CORS
import datetime
import time
from flask import render_template
import requests
import random
import re
import os
from google_images_download import google_images_download

app = Flask(__name__)
CORS(app)
def getRandomImage():
    path_dir = os.getcwd() + '/prototype/static/style/'
    file_list = os.listdir(path_dir)
    choiceList = random.choice(file_list)
    return path_dir + choiceList
def createAIimage(content,style):
    result = requests.post(
        "https://api.deepai.org/api/neural-style",
        files={
            'style': open(style, 'rb'),
            'content': open(content, 'rb'),
        },
        headers={'api-key': '7b134cc2-6b1d-485c-a484-f4d14148af8e'}
    )
    return result.json()

def createMetadata(grade, img):
    url = "https://metadata-api.klaytnapi.com/v1/metadata"
    payload = {
        "metadata": {
            "description": "Beef NFT는 AI 소고기 등급 판별기를 통해 발행된 NFT로 AI 기반으로 소고기 이미지를 통해 소고기의 등급을 판별한 후 판별된 등급을 NFT에 저장해 인증서를 발급한다.",
            "external_url": "https://beef.honeyvuitton.com/", 
            "image": "https://gateway.pinata.cloud/ipfs/QmXpEti7gYyd6aM3UXERr4v7QDkMg3mFJwyVkH3EagwU69?preview=1", 
            "name": "Beef NFT",
            #Opensea에서 property 에 등록될 수 있는 형식으로 바꾸어 줬고, NFT의 생성일자도 birthday형식으로 지정했는데 이 때 unix timestamp형식이 필요해서 해당 형식에 맞게 진행하였다.
            "attributes": [{
                "display_type": "date",
                "trait_type": "Birthday",
                "value": str(time.time()),
            },
            {
                "trait_type": "grade",
                "value": grade
            },]
        },
        # "filename": "test.json"
    }
    headers = {
        "x-chain-id": "1001",
        "Authorization": "Basic S0FTS0wyQlMxRDFJMUczREowRTdFUDhEOmptd2hlNkZrcXZLLWxheTUxWHJ5QktJVFJPaXE5MUtyRE9OMjFxR0Q=",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    # {
    # "contentType": "application/json",
    # "filename": "13126799-5d29-06f8-ea1d-ff5f5165ce35.json",
    # "uri": "https://metadata-store.klaytnapi.com/9c7de118-cf48-8ab5-f186-4ed29b9cf6b7/13126799-5d29-06f8-ea1d-ff5f5165ce35.json"
    # }     //KAS Medata API 메타데이터 생성 부분 리턴 형태

    return response.json()["uri"]

def mintNFT(uri, tokenID):
    #url = "https://kip17-api.klaytnapi.com/v1/contract/0xe3a390fdb12dafe2eb37d7829d11a18f37e59424/token" #beefcoin
    url = "https://kip17-api.klaytnapi.com/v1/contract/0xe966c58075372c9ddeb2d07080075f32d053f463/token" #maidcat
    

    payload = {
        "to": "0x24b2803c34b11740acd0cc35648e34163c5cba0c",
        "id": tokenID,
        "uri": uri,
    }
    headers = {
        "x-chain-id": "1001",
        "Authorization": "Basic S0FTS0wyQlMxRDFJMUczREowRTdFUDhEOmptd2hlNkZrcXZLLWxheTUxWHJ5QktJVFJPaXE5MUtyRE9OMjFxR0Q=",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    return response.json()

@app.route('/nftMint', methods = ['POST'])

def API():
    params = request.get_json()
    #print(params,type(params))
    if params["grade"]:
        metaURI = createMetadata(params["grade"],params["img"])
        #KAS에서 토큰을 발행할 때 토큰 아이디는 무조건 16진수여야 한다 현재시간을 일렬로 정수형만 추출해 16진수로 변환시켜서 호출한다.
        hex_tokenID = hex(int('0x'+re.sub(r'[^0-9]', '',str(datetime.datetime.now())),16))
        print(hex_tokenID)
        result = mintNFT(metaURI,hex_tokenID)
        print(result)
        return result
    else:
        return params

@app.route("/")
def intro():
    response = google_images_download.googleimagesdownload()
    keyword_list = ["Emilia","cat"] #구글에 검색할 키워드
    for i in range(len(keyword_list)):
        arguments = {"keywords":keyword_list[i], "limit":2, "print_urls":True}
        paths = response.download(arguments)
    return render_template('index.html')

@app.route("/getImage")
def getImage():
    response = google_images_download.googleimagesdownload()
    keyword_list = ["Emilia","cat"] #구글에 검색할 키워드
    open('./static/style')
    for i in range(len(keyword_list)):
        arguments = {"keywords":keyword_list[i], "limit":1, "print_urls":True}
        #이미지 다운 완료
        paths = response.download(arguments)
        
        createAIimage(paths[0][keyword_list[i]][0])
        
    
    return render_template('index.html')

@app.route("/test")
def test():
    response = google_images_download.googleimagesdownload()
    keyword_list = ["Emilia","cat"] #구글에 검색할 키워드
    result = []
    for i in range(len(keyword_list)):
        arguments = {"keywords":keyword_list[i], "limit":1, "print_urls":True}
        #이미지 다운 완료
        paths = response.download(arguments)
        
        result.append(createAIimage(paths[0][keyword_list[i]][0],getRandomImage()))
    return result[0]
    
    return render_template('index.html')

 
