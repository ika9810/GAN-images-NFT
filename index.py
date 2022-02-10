from importlib.resources import path
from google_images_download import google_images_download

response = google_images_download.googleimagesdownload()
keyword_list = ["Emilia","cat"] #구글에 검색할 키워드
for i in range(len(keyword_list)):
    arguments = {"keywords":keyword_list[i], "limit":1, "print_urls":True}
    paths = response.download(arguments)
    print(paths[0][keyword_list[i]][0])