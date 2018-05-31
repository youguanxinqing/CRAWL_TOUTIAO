import requests
import time
import json
import re

url = "http://www.toutiao.com/search_content/"

headers = {
"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) \
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 \
Safari/537.36",
}

def get_start_data(offset):
    """
    图集链接
    """
    params = {
        "offset": offset,
        "format": "json",
        "keyword": "街拍",
        "autoload": "true",
        "count": "20",
        "cur_tab": "1",
        "from": "search_tab",
    }
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        return response.text
    except requests.HTTPError:
        print("连接错误")
        return None

def handle_start_data(html):
    """
    处理图集页面数据
    主要提取：标题，图片数，正文链接
    """
    data = json.loads(html)
    if data and "data" in data.keys():
        for item in data.get("data"):
            url = item.get("article_url")
            title = item.get("title")
            count = item.get("image_count")
            extractData = {
                "title" : title,
                "count" : count,
                "url" : url,
            }
            yield extractData

def come_in_link(data):
    """
    进入链接
    """
    if data["url"]:
        try:
            response = requests.get(data["url"], headers=headers)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            return response.text
        except requests.HTTPError:
            print("进入链接发生错误")
            return None

def handle_in_data(html, data):
    """
    处理正文里的数据
    """
    if html:
        # 正则，取出链接
        pattern = re.compile(r'gallery: JSON.parse\((.*?)\),', re.S)
        result = re.search(pattern, html)
        if result:
            imageLinks = []
            extractData = json.loads(json.loads(result.group(1)))
            for eData in extractData.get("sub_images"):
                imageLinks.append(eData.get("url"))

            data["images"] = imageLinks

            # print("test:", result.group(1))
        else:
            print("no have result")

        return data

def download_image(imageUrl):
    """
    下载图片
    """
    for url in imageUrl:
        try:
            image = requests.get(url).content
        except:
            pass
        with open("images/"+url[-10:]+".jpg", "wb") as ob:
            ob.write(image)
            print(url[-10:]+"下载成功！")


def main():
    # 设置偏移量
    for offset in [0, 20, 40, 60, 80]:
        html = get_start_data(offset)
        for data in handle_start_data(html):
            content = come_in_link(data)
            lastData = handle_in_data(content, data)
            if lastData:
                try:
                    download_image(lastData["images"])
                except KeyError:
                    print("{0}存在问题，略过".format(lastData))
                    continue


if __name__ == "__main__":
    main()

