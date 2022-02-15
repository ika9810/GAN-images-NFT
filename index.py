import datetime
import time
import requests
import random
import shutil
import re
import os
import json
from google_images_download import google_images_download
from pinatapy import PinataPy

import time
import schedule

def readSlackAPIKEY():
    with open('/home/opc/GAN-images-NFT/keys/slack-api-key.json', 'r') as f:
        json_data = json.load(f)
    return json_data['GAN-API-KEY']
def post_slack_message(channel, text):
    myToken = readSlackAPIKEY()
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer " + myToken},
        data={"channel": channel,"text": text}
    )
    print(response.json())

def readAndwriteDB():
    #파일을 읽기 모드로 연다
    file = open( os.getcwd() + '/prototype/static/number_db.txt','r')
    #변수 x에 파일의 내용을 저장한다
    x = file.read()
    #파일을 적기모드로 다시 연다
    file = open( os.getcwd() + '/prototype/static/number_db.txt','w')
    #TypeError: write() argument must be str, not int 라는 에러 때문에 
    #다음 사용을 위해 1을 추가한다
    file.write(str(int(x)+1))
    #파일을 닫는다
    file.close()
    #처음 파일에 적혀있던 값을 불러온다
    return x
#pinata API를 활용한 파일을 IPFS에 업로드하는 합수
def pinFileToIPFS(data):
    #API KEY와 API Secret KEY를 인자로 pinata 선언
    pinata = PinataPy("76669b41b802b55940ee", "88a4a918c5a946cead6bf1e715165f92fddf2082c8f3c7ab9a59c739d10609f4")
    #pin_file_to_ipfs 호출
    result = pinata.pin_file_to_ipfs(data)
    return result

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

def createMetadata(data):
    # data = {
    #     "image_url": image_url,
    #     "display_image_url": display_image_url,
    #     "content_image_url": content_image_url,
    #     "style_image_url": style_image_url,
    #     "name": keyword+'-'+style_image+'#' + tokenID,
    #     "content" : keyword,
    #     "style" : style_image
    # }
    url = "https://metadata-api.klaytnapi.com/v1/metadata"
    payload = {
        "metadata": {
            "description": "AI NARTIST는 AI와 NFT와 Artist라는 단어가 합쳐진 말로 AI를 통해 NFT를 만드는 아티스트를 뜻한다. 구글에서 키워드를 통해 검색한 이미지 결과를 다운로드하여 ika9810이 엄선한 작품들의 스타일을 GAN을 활용하여 미술작품을 생성한다. 생성한 미술 작품은 ipfs에 업로드되며 작품이 생성될 때마다 깃허브에 커밋이 이루어진다.",
            "external_url": "https://github.com/ika9810/GAN-images-NFT", 
            "image": data["image_url"], 
            "display_image_url": data["display_image_url"],
            "content_image_url": data["content_image_url"],
            "style_image_url": data["style_image_url"],
            #이름은 content image와 style 이미지를 본따고 넘버를 메길 예정이다 ex) Emilia-vangogh#1
            "name": data["name"],
            #Opensea에서 property 에 등록될 수 있는 형식으로 바꾸어 줬고, NFT의 생성일자도 birthday형식으로 지정했는데 이 때 unix timestamp형식이 필요해서 해당 형식에 맞게 진행하였다.
            "attributes": [{
                "display_type": "date",
                "trait_type": "Birthday",
                "value": str(time.time()),
            },
            {
                "trait_type": "Content Image",
                "value": data["content"]
            },
            {
                "trait_type": "Style Image",
                "value": data["style"]
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
def Main():
    #1.google_image_download를 통한 이미지 다운
    response = google_images_download.googleimagesdownload()
    keyword_list = ["Emilia","cat"] #구글에 검색할 키워드
    result_list = []
    style_path_dir = os.getcwd() + '/prototype/static/style/'
    for keyword in keyword_list:
        arguments = {"keywords":keyword, "limit":1, "print_urls":True}
        #이미지 다운 완료 path 
        paths = response.download(arguments)
        #2.DeepAI의 Neural Style API를 통해 AI 미술작품 생성 
        #createAIimage 함수를 통해 (content image url, style image url)에 해당하는 인자를 넣어준다. style image는 랜덤하게 초이스해서 넣어준다. content image 또한 getRandomContentImage을 통해 랜던하게 초이스해서 넣어준다.
        #리턴값으로 3장의 파일이 모두 들어있는 폴더의 위치를 받아서 result_list에 저장한다.

        #튜플 형식이다 따라서 안의 원소를 [0]으로 인덱싱 하면 json 형식이 나오는데 우리는 그 뒤 리스트가 필요하므로 [keyword]를 통해 뒤의 리스트를 반환한다
        content_path_dir = paths[0][keyword]
        result_list.append(createAIimage(keyword, getRandomContentImage(content_path_dir), getRandomImage(style_path_dir)))   
    #랜덤 초이스 후 남는 이미지 파일들이 존재하기 때문에 전부 삭제해주기 위해 dowloads 폴더 삭제
    shutil.rmtree(os.getcwd() + '/downloads/')
    #3.NFT 발행을 위한 Metadata 생성하기

    #result_list에 각각 생성된 결과물 폴더 경로가 저장되어있다.
    os.listdir(style_path_dir)
    #키워드 개수에 따른 result_list안의 원소 파악하기
    for dir in result_list:
        print(dir)
        #각각의 키워드에 따른 결과 파악하기
        image_url=display_image_url=content_image_url=style_image_url=keyword=style_image=""
        tokenID = readAndwriteDB()
        for image in os.listdir(dir):
            #style image 판단하기
            if image in os.listdir(style_path_dir):
                style_image = image.split('.')[0]
                style_image_url = "https://raw.githubusercontent.com/ika9810/GAN-images-NFT/main/prototype/static/style/"+image
                print('style image', style_image,style_image_url)
            #result image 판단하기 -> ipfs로 변경
            elif image == 'result.jpg':
                print('result', dir + '/' +image)
                res = pinFileToIPFS(dir + '/' +image)
                image_url = 'ipfs://' + res['IpfsHash']
                display_image_url = "https://gateway.pinata.cloud/ipfs/" + res['IpfsHash']
                print('ipfs', res['IpfsHash'])
            #content image 판단하기
            else:
                keyword = image.split('.png')[0]
                dir.split('/results/')[1]
                content_image_url = "https://raw.githubusercontent.com/ika9810/GAN-images-NFT/main/results/"+ dir.split('/results/')[1] + '/' + image
                print('keyword',keyword, content_image_url)
        data = {
            "image_url": image_url,
            "display_image_url": display_image_url,
            "content_image_url": content_image_url,
            "style_image_url": style_image_url,
            "name": keyword+'-'+style_image+'#' + tokenID,
            "content" : keyword,
            "style" : style_image
        }
        print(data)
        nft_uri = createMetadata(data)
        result = mintNFT(nft_uri, hex(int(tokenID)))
        if result['status'] == 'Submitted':
            transactionHash = result['transactionHash']
            klayscope_main_title = '### Klaytnscope NFT Contract 조회\n'
            klayscope_main_link = "https://baobab.scope.klaytn.com/nft/0x0f77f06235bc791e973ce8c0af578b9cac64ee4b?tabId=nftTransfer\n\n"
            klayscope_title = '### Klaytnscope Transaction 조회\n'
            klayscope_link = "https://baobab.scope.klaytn.com/tx/"+transactionHash+"?tabId=nftTransfer\n\n"
            opensea_title = '### Opensea NFT 링크\n'
            opensea_link = "https://testnets.opensea.io/assets/baobab/0x0f77f06235bc791e973ce8c0af578b9cac64ee4b/"+ tokenID
            lines = [klayscope_main_title,klayscope_main_link,klayscope_title,klayscope_link,opensea_title,opensea_link]
            with open(dir + '/result.md', 'w') as result_file:    # hello.txt 파일을 쓰기 모드(w)로 열기
                result_file.writelines(lines)
            result_file.close()
            #
            post_slack_message("#gan-image-nft","https://github.com/ika9810/GAN-images-NFT/tree/main/results/" + dir.split('/results/')[1])
    return "Success"
Main()
# schedule.every(1).minutes.do(Main) #30분마다 실행
# # schedule.every().monday.at("00:10").do(printhello) #월요일 00:10분에 실행
# # schedule.every().day.at("10:30").do(job) #매일 10시30분에 
# #https://tre2man.tistory.com/188
# #실제 실행하게 하는 코드
# while True:
#     schedule.run_pending()
#     time.sleep(1)
#https://m.blog.naver.com/shino1025/221432633410
#crontab
#slack bot