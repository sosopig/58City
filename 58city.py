import urllib
import urllib.request
import requests
import re
import json

from lxml import etree

import bs4
from bs4 import BeautifulSoup

# 城市选择  http://sh.58.com/chuzu/
'''
通过切换城市的html页面（http://www.58.com/changecity.html）匹配城市及对应的href,拼接成完整的城市出租页面
在检查元素中对应的html源代码city.html和下载下来的代码fullcity.html不一样，所以要根据fullcity.html来写正则表达式
'''
# 列表分类展示：默认上海出租;0代表个人房源；1代表经纪人房源   http://sh.58.com/chuzu    http://sh.58.com/chuzu/0/
'''
用if判断语句来匹配用户的选择的类别
'''
# 区域展示第一种url格式  http://sh.58.com/chuzu/?key=黄埔      http://sh.58.com/chuzu/0/?key=黄埔
# 区域展示第二种url格式  http://sh.58.com/baoshan/chuzu/0/    本项目用此方式
'''
通过对应的城市租房html页面（http://sh.58.com/chuzu/）的区域导航条获取对应的城市及href，拼接成完整的区域出租页面
'''

fullcity_url = 'http://www.58.com/changecity.html'

city_url = 'http://%s.58.com/chuzu/'

type_url = 'http://%s.58.com/chuzu/%s/'

# address_url1 = 'http://%s.58.com/chuzu/?key=%s'
address_url1 = 'http://%s.58.com%s/pn%d/'
address_url2 = 'http://%s.58.com%s%s/pn%d/'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
}

count = 0

request = urllib.request.Request(url=fullcity_url, headers=headers)
response = urllib.request.urlopen(request)
city_html = response.read().decode('utf-8')

# 下载查看代码和审查元素中是否一致，最终发现不一致，以fullcity.html为准
# with open('./58city/fullcities.html', mode='wb')as fp:
#     fp.write(city_html.encode('utf-8'))

'''
4个独立市，直辖市
var independentCityList = {
    "北京": "bj|1",
    "上海": "sh|2",
    "天津": "tj|18",
    "重庆": "cq|37"
}
'''

# 匹配fullcity中直辖市和全国省市的json数据
pattern = r'<script>([\s\S]*?)</script>'
city_data = re.findall(pattern=pattern, string=city_html)
city_json = city_data[0]
city_string = str(city_json)
cities_list = city_string.replace('\n', '').replace(' ', '').split('var')

# 将获取的数据转换成json格式/dict格式，以便于查找匹配数据
# independentCityList = {'北京': 'bj|1', '上海': 'sh|2', '天津': 'tj|18', '重庆': 'cq|37'}
independentCityList = json.loads(cities_list[2].split('=')[1])

cityList = json.loads(cities_list[3].split('=')[1], encoding='utf-8')


# 匹配相对应键的值中的城市字母缩写,正则匹配后注意数据类型
# str='suqian|138'
# pattern = (r'([a-z]+)|')
# print(re.match(pattern=pattern, string=str).group())

# 匹配省份城市
def city_match(province, city):
    if province in cityList:
        if city in cityList[province]:
            value = cityList[province][city]
            pattern = (r'([a-z]+)|')
            city_name = re.match(pattern=pattern, string=value).group()
            return city_name
        else:
            print('你输入的城市不在范围内！')
    else:
        if city in independentCityList:
            value = independentCityList[city]
            pattern = (r'([a-z]+)|')
            city_name = re.match(pattern=pattern, string=value).group()
            return city_name
        else:
            print('你输入的城市不在范围内！')


# 匹配查找类型
# def type_match(type):
#     if type == '0' or type == '1':
#         url = type_url % (city_name, type)
#     else:
#         url = city_url
#     return url


# 匹配区域的href
def addresshref_match(address):
    response = requests.get(url=city_url, headers=headers, verify=False)
    response.encoding = 'utf-8'
    city_content = response.text

    # 使用xpath匹配区域的href
    tree = etree.HTML(city_content)
    # print(etree.tostring(tree).decode('utf-8'))
    hrefs = tree.xpath('//dl[@class="secitem secitem_fist"]/dd/a/@href')

    # 匹配区域名称（都是中文）
    soup = BeautifulSoup(city_content, 'lxml')
    a = soup.select('dl[class="secitem secitem_fist"] > dd > a')
    pattern = u'[\u4e00-\u9fa5]+'
    addressList = re.findall(pattern=pattern, string=str(a))

    # 定义一个空字典，将区域的名称和href以键值对格式储存
    address_dict = {}
    for i in range(len(addressList)):
        address_dict[addressList[i]] = hrefs[i]

    # 判断输入的区域名称是否在字典中
    try:
        if address in address_dict:
            href = address_dict[address]
        else:
            href = address_dict['不限']
        return href
    except:
        print('城市与区域不匹配！')


# 根据类型细分区域的url
def address_type(href, p):
    if type == '0' or type == '1':
        address_url = address_url2 % (city_name, href, type, p)
    else:
        address_url = address_url1 % (city_name, href, p)
    return address_url



    # 匹配页面中跳转房源详情的href


def room(address_url):
    response = requests.get(url=address_url, headers=headers, verify=False)
    info = response.text
    room_info = etree.HTML(info)
    # print(etree.tostring(room_info).decode('utf-8'))
    room_hrefs = room_info.xpath('//div[@class="img_list"]/a/@href')
    print(room_hrefs)
    for room_href in room_hrefs:
        response = requests.get(url='http:'+room_href, headers=headers, verify=False)
        response.encoding = 'utf-8'
        room = response.text
        room_detail = etree.HTML(room)

        roomsoup = BeautifulSoup(room, 'lxml')
        roomlist = roomsoup.select('ul[class="f14"] > li')

        # 匹配详情页的图片集
        '''
        <div class="basic-pic-list pr">
                <ul id="leftImg" class="pic-list-wrap pa" style="left: 0px;">
                    <li id="xtu_1" class="actives"
                        data-src="//pic3.58cdn.com.cn/anjuke_58/92aa559bf218bf4ba87099365e7eb1b5?w=640&amp;h=480&amp;crop=1">
                        <img data-src="//pic3.58cdn.com.cn/anjuke_58/92aa559bf218bf4ba87099365e7eb1b5?w=182&amp;h=150&amp;crop=1"
                             src="//pic3.58cdn.com.cn/anjuke_58/92aa559bf218bf4ba87099365e7eb1b5?w=182&amp;h=150&amp;crop=1">
                    </li>
                    ......
                </ul>
                ......
        </div>
        '''
        img_srcs = room_detail.xpath('//ul[@id="leftImg"]/li/img/@src')
        for src in img_srcs:
            load_image(src)

        # 匹配详情页的房源基础信息
        '''
        <div class="house-desc-item fl c_333">
                <div class="house-pay-way f16">
                    <span class="c_ff552e">
                        <b class="f36">3700</b> 元/月</span>&nbsp;&nbsp;&nbsp;&nbsp;
                    <span class="c_333">押一付三</span>
                    <!-- 增加 start -->
                    <!-- 增加 end -->
                </div>
                <ul class="f14">
                    <li><span class="c_888 mr_15">租赁方式：</span><span>整租</span>
                    </li>
                ......
                </ul>
        </div>
        '''
        items = []
        divs = room_detail.xpath('//div[contains(@class,"house-pay-way f16")]')
        for div in divs:
            item = {}
            try:
                prices = div.xpath('.//span/b/text()')[0]
                units = div.xpath('.//span[@class="c_ff552e"]/text()')[0]
                pays = div.xpath('.//span[@class="c_333"]/text()')[0]
                titles = prices + units + pays
                item['价格'] = titles
                items.append(item)
            except Exception as e:
                pass

        for li in roomlist:
            try:
                spans = li.select('span')
                key = spans[0].get_text()
                values = spans[1].get_text()
                pattern = r'(\w*?)\xa0\xa0\s*(\S*\w*)\s*(\S*\w*)'
                p = re.findall(pattern=pattern, string=values)
                for i in range(len(p)):
                    value = ''.join(p[i])
                    # print(keys)
                    # print(value)
                    item = {key: value}
                    items.append(item)
            except Exception as e:
                pass

        '''
        <div class="house-chat-phone">
            <i class="house-chat-icon house-chat-icon-phone-full"></i>
            <span class="house-chat-txt">13166402247</span>
        </div>
        '''
        try:
            item = {}
            photos = room_detail.xpath('//span[@class="house-chat-txt"]/text()')[0]
            item['联系电话'] = photos
            items.append(item)
        except:
            pass

        # print(items)
        '''
        [{'价格': '1660 元/月押一付一'}, {'租赁方式：': '合租 - 主卧 - 男女不限'}, {'房屋类型：': '3室1厅1卫                                \xa0\xa016                                平\xa0\xa0精装修 '}, {'朝向楼层：': '南\xa0\xa0中层/共23层'}, {'所在小区：': '长江西路1200-15...'}, {'所属区域：': '\n宝山\xa0\xa0\n                                                                                                    通河新村\n'}, {'详细地址：': '\n                                长江西路1200-1500号                            '}, {'联系电话': '13044104727'}]
        '''

        with open('./roomdetails.json', mode='a', encoding='utf-8')as fp:
            str = json.dumps(items, ensure_ascii=False)
            fp.write(str)
            print('租房详情保存成功!!!')






# 保存图片
def load_image(src):
    global count
    file_name = src.split('?')[0].rsplit('/')[-1]
    urllib.request.urlretrieve(url='https:' + src, filename='./house/%s' % (file_name))
    count += 1
    print('保存图片第%d张成功！' % (count))


if __name__ == '__main__':
    province = input('请输入要租房的省份（“直辖市”按回车键）：')
    city = input('请输入要租房的城市或直辖市：')
    type = input('请输入查找的类型（不输入：默认；0：个人房源；1：经纪人）：')
    address = input('请输入具体的区域名称(“不限”请按回车键)：')
    page = int(input('请输入查询的页数:'))

    city_name = city_match(province, city)

    city_url = city_url % (city_name)

    # type_url = type_match(type)

    href = addresshref_match(address)

    for p in range(1, page+1):
        address_url = address_type(href, p)
        print(city_url, address_url)
        roomdetails = room(address_url)



