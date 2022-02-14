from importlib.resources import path
from google_images_download import google_images_download
import os

response = google_images_download.googleimagesdownload()
keyword_list = ["Emilia","cat"] #구글에 검색할 키워드
res_list = []
for i in range(len(keyword_list)):
    arguments = {"keywords":keyword_list[i], "limit":1, "print_urls":True}
    paths = response.download(arguments)
    res_list.append(paths[0][keyword_list[i]][0])
    break
keyword = "Emilia"
url = os.getcwd() + '/downloads/'+ keyword+ '/'
print(res_list[0].split(url)[1])