import json

import requests
import time
import pandas as pd
from config import *
import pymongo

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB2]


class Music163(object):
    def __init__(self):
        self.headers = {
            'Cookie': 'ail_psc_fingerprint=489a1ee9a8838699a1e50094226ee8a4; _iuqxldmzr_=32; _ntes_nnid=93e8a356b1355868c04b956990895dc3,1528856902905; _ntes_nuid=93e8a356b1355868c04b956990895dc3; usertrack=O2+gylssv1AZjDMaAwNwAg==; WM_TID=o%2BN0Am0Tj3zrdpaUwYpOvIIUhUu0DDpJ; Province=0530; City=0531; nts_mail_user=ytbfzd@163.com:-1:1; __f_=1537065092272; NNSSPID=2d4a0bd0bb7641e8b345ea0c28b13f07; P_INFO=liuyanjun00@163.com|1537171727|0|other|11&20|PL&1537108625&other#shd&null#10#0#0|&0|urs&mail163|liuyanjun00@163.com; __utmz=94650624.1537193819.4.2.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; JSESSIONID-WYYY=ldWHA1%2FVfjsC6CpwOdUY2uT5kKgPyJodZNQ%2F9pKUEWSOq7iGdRvBtBqwjIg%2FlZv2byFdEENVQmdn5SC%2F%5CjidN6SwrwK1wrQxs7DSZeVk0ica8flJ%2BvZ5XwqegGCB15k2w1DJZi%5Ckg%5C%2FzelH%5CO3gbp4YDrUUFtDKw0e9flvpkxyiwYSSy%3A1537231432828; __utma=94650624.1665018979.1537182135.1537193819.1537229634.5; __utmc=94650624; WM_NI=PwK44TRiLJVeuiUDWV2%2B92xNPB4%2FFGGvOObYXQsAcZr06B3lb07xuEZGJF1tO0ElsH9i6GpP1LA94F7xGt%2FA8IA1wlLeGs1wNn9L1pMvWBY1CHHr1%2BXUVOO71bJj34zEVXI%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6eeafc2739898ab83b83ea5b084d2e972f8f58dabcc6f9be9f8a2d033a99aa695db2af0fea7c3b92a94a985d5b76092b784abd56fb7b79ba5d65ef2f5f7d3fb46949efcd0c54d85aa81b0e1539c8fbda2e252b2f0faa3b268a2f0f999f84f9a9986a7b4808df08b8df244fbb7faa8f35cf3948fdab74ef5a88995ae4bfc978fd2f66890bb8994b47d8eb2f7adb47c8faa99a3dc3b81988893b4219c8b9ab0ce3df3be868bb240ba9b9ab9cc37e2a3; __utmb=94650624.11.10.1537229634',
            'Referer': 'https://music.163.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'
        }

        self.song_dict = {
            'id': [],
            'name': [],
            'album': [],
            'artists': [],
            'com_count': []
        }

    def get_song_info(self, response):
        page_data = response.json()['result']['songs']
        for data in page_data:
            self.song_dict['id'].append(data['id'])
            self.song_dict['name'].append(data['name'])
            self.song_dict['album'].append(data['album']['name'])
            self.song_dict['artists'].append(data['artists'][0]['name'])
            self.song_dict['com_count'].append(self.comment_count(str(data['id'])))

    def save_to_file(self):
        df = pd.DataFrame(self.song_dict)
        df = df.sort_index(axis=0, ascending=False, by='com_count')
        df.to_csv('douyin_songs_new.csv', index=False)
        # print(df)

    def save_to_mongoDB(product):
        try:
            if db[MONGO_TABLE2].insert(product):
                print('存储到MongoDB成功', product)
        except Exception:
            print('存储到MongoDB失败', product)

    def get_songs_list(self):
        url = r'http://music.163.com/api/search/pc'
        page = 0
        dispage = 30
        while True:
            data = {
                's': '抖音',
                'offset': str(page),
                'limit': str(dispage),
                'type': '1'
            }
            response = requests.post(url, headers=self.headers, data=data)
            if response.status_code == 200:
                if 'songs' in response.json()['result'].keys():
                    print('正在获取第%d页歌曲列表' % page)
                    self.get_song_info(response)
                else:
                    print('歌曲获取完毕')
                    break
            else:
                print('访问失败')
                break
            page += 30
            time.sleep(1)
        self.save_to_file()
        self.save_to_mongoDB(self.song_dict)

    def comment_count(self, song_id):
        url = "http://music.163.com/weapi/v1/resource/comments/R_SO_4_" + song_id + "?csrf_token="
        data = {
            "params": "nHfVBsNbW+WCrz7pAbdaq4uW2+4kADa+gNEfGWK7M5n36mWvsmGXsM2KzVUAeR62mhYlsSvc23I58Rf0dvg1Cglxuf5/l1wVRBCRROpjz9WuYSlWdiwXT/x45iud30RmjbTUsMSQuiehO6Ef3vHSdKWHma9pYm/eeYUF7IQ0hXI3HIz42NgwllBj4cy1XlOH",
            "encSecKey": "0587c5b45f3b0771db2b3fe449e7dd9640ab56f679d73a9189096283e776e7a9f749630c6e0fa3f947778f1588b9ec71bd779279006f352e5804036909d5d772c9572c64db575bcce675fcc9055614f1c955abb798eed602cb43945748d8b0a9ecf293cde0ef523e63c3115a1a12b7113be447fba7947090f0d98d2c37cff72a"
        }
        req = requests.post(url=url, headers=self.headers, data=data)
        req.encoding = "utf-8"
        comment = json.loads(req.text)
        return comment["total"]


def main():
    music = Music163()
    music.get_songs_list()


if __name__ == '__main__':
    main()
