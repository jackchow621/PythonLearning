import datetime
import json
import time
from collections import Counter

import requests
from pyecharts import Bar, Geo, Style


def get_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'}
    html = requests.get(url, headers=headers)
    if html.status_code == 200:
        return html.content
    else:
        return None


def parse_data(html):
    json_data = json.loads(html)['cmts']
    comments = []
    try:
        for item in json_data:
            comment = {
                'nickName': item['nickName'],
                'cityName': item['cityName'] if 'cityName' in item else '',
                'content': item['content'].strip().replace('\n', ''),
                'score': item['score'],
                'startTime': item['startTime']
            }
            comments.append(comment)
        return comments
    except Exception as e:
        print(e)


def save():
    # start_time = datetime.datetime.strftime('%Y-%m-%d %H:%M:%S')
    # start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    start_time = "2018-11-09 20:45:58"
    end_time = '2018-11-09 00:00:00'
    while start_time > end_time:
        url = 'http://m.maoyan.com/mmdb/comments/movie/42964.json?_v_=yes&offset=15&startTime=' + start_time.replace(
            ' ', '%20')
        html = None
        try:
            html = get_data(url)
        except Exception as e:
            time.sleep(0.5)
            html = get_data(url)
        else:
            time.sleep(0.1)
        comments = parse_data(html)
        start_time = comments[14]['startTime']
        print(start_time)
        start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(seconds=-1)
        start_time = datetime.datetime.strftime(start_time, '%Y-%m-%d %H:%M:%S')
        for item in comments:
            print(item)
            with open('comments.txt', 'a', encoding='utf-8')as f:
                f.write(
                    item['nickName'] + '$' + item['cityName'] + '$' + item['content'] + '$' + str(item['score']) + '$' + item['startTime'] + '\n')


# 处理地名数据，解决坐标文件中找不到地名的问题
def handle(cities):
    # print(len(cities), len(set(cities)))

    # 获取坐标文件中所有地名
    data = None
    with open(
            'C:/Python/Python36/Lib/site-packages/pyecharts/datasets/city_coordinates.json',
            mode='r', encoding='utf-8') as f:
        data = json.loads(f.read())  # 将str转换为json

    # 循环判断处理
    data_new = data.copy()  # 拷贝所有地名数据
    for city in set(cities):  # 使用set去重
        # 处理地名为空的数据
        if city == '':
            while city in cities:
                cities.remove(city)
        count = 0
        for k in data.keys():
            count += 1
            if k == city:
                break
            if k.startswith(city):  # 处理简写的地名，如 达州市 简写为 达州
                # print(k, city)
                data_new[city] = data[k]
                break
            if k.startswith(city[0:-1]) and len(city) >= 3:  # 处理行政变更的地名，如县改区 或 县改市等
                data_new[city] = data[k]
                break
        # 处理不存在的地名
        if count == len(data):
            while city in cities:
                cities.remove(city)

    # print(len(data), len(data_new))

    # 写入覆盖坐标文件
    with open(
            'C:/Python/Python36/Lib/site-packages/pyecharts/datasets/city_coordinates.json',
            mode='w', encoding='utf-8') as f:
        f.write(json.dumps(data_new, ensure_ascii=False))  # 将json转换为str


def render():
    cities = []
    with open('comments.txt', mode='r', encoding='utf-8') as f:
        rows = f.readlines()
        for row in rows:
            print(row)
            if row.strip() != '' and row.find('$'):
                city = row.split('$')[1]
                if city != '':  # 去掉城市名为空的值
                    cities.append(city)

        # 对城市数据和坐标文件中的地名进行处理
    handle(cities)

    # 统计每个城市出现的次数
    # data = []
    # for city in set(cities):
    #     data.append((city, cities.count(city)))
    data = Counter(cities).most_common()  # 使用Counter类统计出现的次数，并转换为元组列表

    style = Style(title_color="#fff", title_pos="center",
                  width=1200, height=600, background_color="#404a59")

    geo = Geo('《毒液》观众位置分布', '数据来源：猫眼-Ryan采集', **style.init_style)
    attr, value = geo.cast(data)
    geo.add('', attr, value, visual_range=[0, 3500],
            visual_text_color='#fff', symbol_size=15,
            is_visualmap=True, is_piecewise=True, visual_split_number=10)
    geo.render('粉丝位置分布-地理坐标图.html')

    data_top20 = Counter(cities).most_common(20)
    bar = Bar('《毒液》观众来源排行TOP20', '数据来源：猫眼-Ryan采集', title_pos='center', width=1200, height=600)
    attr, value = bar.cast(data_top20)
    bar.add('', attr, value, is_visualmap=True, visual_range=[0, 3500], visual_text_color='#fff', is_more_utils=True,
            is_label_show=True)
    bar.render('观众来源排行-柱状图.html')


if __name__ == '__main__':
    # url = 'http://m.maoyan.com/mmdb/comments/movie/42964.json?_v_=yes&offset=15&startTime=2018-11-19%2019%3A36%3A43'
    # html = get_data(url)
    # results = parse_data(html)
    # save()
    render()
