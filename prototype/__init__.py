from flask import Flask, request
from flask_cors import CORS
import datetime
import time
from flask import render_template
import requests
import random
import shutil
import re
import os
from google_images_download import google_images_download

app = Flask(__name__)
CORS(app)
def getRandomImage(path_dir):
    file_list = os.listdir(path_dir)
    #리스트 내에서 랜덤하게 하나의 요소를 뽑아낸내는 함수 random.choice()
    choiceList = random.choice(file_list)
    return path_dir + choiceList
def getRandomContentImage(file_list):
    #리스트 내에서 랜덤하게 하나의 요소를 뽑아낸내는 함수 random.choice()
    choiceList = random.choice(file_list)
    return choiceList

def createAIimage(keyword,content,style):
    result = requests.post(
        "https://api.deepai.org/api/neural-style",
        files={
            'style': open(style, 'rb'),
            'content': open(content, 'rb'),
        },
        headers={'api-key': '7b134cc2-6b1d-485c-a484-f4d14148af8e'}
    )
    result_url = result.json()["output_url"]
    #현재 시간을 통한 파일 생성
    now = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    #os.getcwd()을 통한 현재 파일 위치 조회 및 결과물 저장 폴더 지정
    make_result_file_path = os.getcwd() + '/results/' + now 
    #위치를 os.makedirs를 통해 결과물 생성
    os.makedirs(make_result_file_path)
    #Content 이미지 이름을 Keyword로 변경
    rename_url = os.getcwd() + '/downloads/'+ keyword+ '/'+ keyword + '.png'
    os.rename(content, rename_url)
    #다운받은 콘텐츠 사진 이동(Emilia, cat)
    shutil.move(rename_url,make_result_file_path)
    #기존 스타일 사진 복사
    shutil.copy(style, make_result_file_path)

    #API를 통해 리턴받은 사진을 로컬 파일을 통해 저장
    res = requests.get(result_url)
    f = open(make_result_file_path+'/result.jpg','wb')
    response = requests.get(result_url)
    f.write(response.content)
    f.close()
    #NFT 발행을 위해 메타데이터에 데이터 내용들을 적어야하는데 폴더 하나에 파일을 3개로 모아놨다(content,style,result) 3개가 모여있는 폴더 주소를 리턴함으로써 NFT 발행시 이미지 데이터에 접근 가능하도록 한다.
    return make_result_file_path

def createMetadata(content, style, ipfs):
    url = "https://metadata-api.klaytnapi.com/v1/metadata"
    payload = {
        "metadata": {
            "description": "AI NARTIST는 AI와 NFT와 Artist라는 단어가 합쳐진 말로 AI를 통해 NFT를 만드는 아티스트를 뜻한다. 구글에서 키워드를 통해 검색한 이미지 결과를 다운로드하여 ika9810이 엄선한 작품들의 스타일을 GAN을 활용하여 미술작품을 생성한다. 생성한 미술 작품은 ipfs에 업로드되며 작품이 생성될 때마다 깃허브에 커밋이 이루어진다.",
            "external_url": "https://github.com/ika9810/GAN-images-NFT", 
            "image": "", 
            "display_image_url":"",
            "content_image_url":"",
            "style_image_url":"",
            #이름은 content image와 style 이미지를 본따고 넘버를 메길 예정이다 ex) Emilia-vangogh#1
            "name": "",
            #Opensea에서 property 에 등록될 수 있는 형식으로 바꾸어 줬고, NFT의 생성일자도 birthday형식으로 지정했는데 이 때 unix timestamp형식이 필요해서 해당 형식에 맞게 진행하였다.
            "attributes": [{
                "display_type": "date",
                "trait_type": "Birthday",
                "value": str(time.time()),
            },
            {
                "trait_type": "Content Image",
                "value": grade
            },
            {
                "trait_type": "Style Image",
                "value": grade
            },
            ]
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
    url = "https://kip17-api.klaytnapi.com/v1/contract/0x0f77f06235bc791e973ce8c0af578b9cac64ee4b/token" #AI NARTIST
    
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
    return render_template('index.html')

@app.route("/test")
def test():
    #1.google_image_download를 통한 이미지 다운
    response = google_images_download.googleimagesdownload()
    keyword_list = ["Emilia","cat"] #구글에 검색할 키워드
    result_list = []
    for keyword in keyword_list:
        arguments = {"keywords":keyword, "limit":3, "print_urls":True}
        #이미지 다운 완료 path 
        paths = response.download(arguments)
        #2.DeepAI의 Neural Style API를 통해 AI 미술작품 생성 
        #createAIimage 함수를 통해 (content image url, style image url)에 해당하는 인자를 넣어준다. style image는 랜덤하게 초이스해서 넣어준다. content image 또한 getRandomContentImage을 통해 랜던하게 초이스해서 넣어준다.
        #리턴값으로 3장의 파일이 모두 들어있는 폴더의 위치를 받아서 result_list에 저장한다.

        #튜플 형식이다 따라서 안의 원소를 [0]으로 인덱싱 하면 json 형식이 나오는데 우리는 그 뒤 리스트가 필요하므로 [keyword]를 통해 뒤의 리스트를 반환한다
        content_path_dir = paths[0][keyword]
        style_path_dir = os.getcwd() + '/prototype/static/style/'
        result_list.append(createAIimage(keyword, getRandomContentImage(content_path_dir), getRandomImage(style_path_dir)))   
    #랜덤 초이스 후 남는 이미지 파일들이 존재하기 때문에 전부 삭제해주기 위해 dowloads 폴더 삭제
    shutil.rmtree(os.getcwd() + '/downloads/')
    #3.NFT 발행을 위한 Metadata 생성하기
    
    return render_template('index.html')

 
#pip3 show pinatapy-vourhey