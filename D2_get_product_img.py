# -*- coding: utf-8 -*-


import requests
import pandas as pd
def open_requests(img, img_name):
    img_url ='https:'+ img
    res=requests.get(img_url)
    with open(f"./downloads_picture/{img_name}", 'wb') as fn:
        fn.write(res.content)

df1=pd.read_csv('./alibaba_com_img.csv',)
for imgs in df1["product_img"]:
    imgList = str(imgs).split(',')
    if len(imgList) > 0:
        img = imgList[0]
        img_name = img[24:]
        print(img, img_name)
        open_requests(img, img_name)
