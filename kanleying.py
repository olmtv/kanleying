# !/usr/bin/python3
# -*- coding: utf-8 -*-
# Time    : 2020/3/24 22:37
# Author  : Amd794
# Email   : 2952277346@qq.com
# Github  : https://github.com/Amd794


import os
from pprint import pprint

import pyquery
from PIL import Image, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True
from threading_download_images import get_response, download
import re
import subprocess
import platform as pf


class Util(object):
    @staticmethod
    def make_pdf(pdf_name, file_list):
        im_list = []

        im1 = Image.open(file_list[0])
        file_list.pop(0)
        for i in file_list:
            img = Image.open(i)
            if img.mode == "RGBA":
                img = img.convert('RGB')
                im_list.append(img)
            else:
                im_list.append(img)
        im1.save(pdf_name, "PDF", resolution=100.0, save_all=True, append_images=im_list)

    @staticmethod
    def render_to_html(html, title, imgs: list):
        chapter_num = len(Comic.detail_dicts)
        template_path = 'template.html'
        imgs_html = ''
        lis_html = ''
        for img in imgs:
            imgs_html += f'<img src="{img}" alt="" style="width: 100%">\n'
        for li in range(chapter_num):
            lis_html += f'''<li><a href="../{Comic.detail_dicts[li].get("a_title")}/{Comic.detail_dicts[li].get(
                "comic_title")}-{Comic.detail_dicts[li].get("a_title")}.html" rel="nofollow">{Comic.detail_dicts[
                li].get("a_title")}</a></li>\n'''
        with open(template_path, 'r', encoding='utf-8') as r:
            render_data = re.sub('{{title}}', title, r.read())
            render_data = re.sub('{{imgs}}', imgs_html, render_data)
            render_data = re.sub('{{lis_html}}', lis_html, render_data)
            render_data = re.sub('{{chapter_num}}', str(chapter_num), render_data)
        with open(html, 'w', encoding='utf-8') as w:
            w.write(render_data)

    @staticmethod
    def compress(target, source, pwd='', delete_source=False, ):
        """
            压缩加密，并删除原数据
            window系统调用rar程序

            linux等其他系统调用内置命令 zip -P123 tar source
            默认不删除原文件
        """
        if pwd: pwd = '-p' + pwd
        if pf.system() == "Windows":
            cmd = f'rar a {pwd} {target} {source} -zcomment.txt'
            p = subprocess.Popen(cmd, executable=r'D:/Sorfwares/WinRAR/WinRAR.exe')
            p.wait()
        else:
            cmd = f'zip a {pwd} {target} {source}'
            p = subprocess.Popen(cmd)
            p.wait()
            # os.system(" ".join(cmd))
        if delete_source:
            os.remove(source)


class Comic(Util):
    kanleying_type = {
        'detail_lis': '#chapterlistload li',
        'comic_title': '.banner_detail .info h1',
        'comic_pages': 'div.comicpage div',
    }
    mm820_type = {
        'detail_lis': '.chapter-list li',
        'comic_title': '.title-warper h1',
        'comic_pages': 'div.comiclist div',
    }
    rules_dict = {

        # https://www.kanleying.com/
        'kanleying': kanleying_type,


        # https://www.qinqinmh.com/
        'qinqinmh': kanleying_type,

        # https://www.feixuemh.com/
        'feixuemh': kanleying_type,

        # https://www.hanmanwo.net/
        'hanmanwo': kanleying_type,

        # https://www.bbdmw.com/
        'bbdmw': kanleying_type,

        # https://www.5wmh.com/
        '5wmh': mm820_type,

        # https://www.zuozuomanhua.com/
        'zuozuomanhua': mm820_type,

        # https://www.wooowooo.com/
        'wooowooo': mm820_type,

        # https://www.hanmzj.com/
        'hanmzj': mm820_type,

        # https://www.hanmanmi.net/
        'hanmanmi': mm820_type,

        # https://www.hmba.vip/
        'hmba': {
            'detail_lis': '#list dl dd:nth-child(n+4)',
            'comic_title': '.booktitle h1',
            'comic_pages': '#content p:nth-child(2n-1)',
        },
        # https://www.38te.com/
        '38te': {
            'detail_lis': 'ul#detail-list-select li',
            'comic_title': '.info h1',
            'comic_pages': '.comicpage div',
        },
        # https://www.dongmanmanhua.cn/
        'dongmanmanhua': {
            'detail_lis': 'ul#_listUl li',
            'comic_title': '.info h1',
            'comic_pages': '#_imageList > img',
        },
        # https://www.hanmanjie.com/
        'hanmanjie': {
            'detail_lis': '.list div',
            'comic_title': '.container .title',
            'comic_pages': '.read-article figure',
        },
        # https://www.manhuaniu.com/
        'manhuaniu': {
            'detail_lis': 'ul#chapter-list-1 li',
            'comic_title': '.book-title h1 span',
            'comic_pages': '.read-article figure',
        },
        # https://www.nxueli.com/
        'nxueli': {
            'detail_lis': 'ul#chapter-list-1 li',
            'comic_title': '.title h1',
        },
        # https://www.mh1234.com/
        'mh1234': {
            'detail_lis': '#chapter-list-1 li',
            'comic_title': '.title h1',
        },
        # https://www.90ff.com/
        '90ff': {
            'detail_lis': '#chapter-list-1 li',
            'comic_title': '.book-title h1',
        },
        # https://www.36mh.com/
        '36mh': {
            'detail_lis': '#chapter-list-4 li',
            'comic_title': '.book-title h1',
        },
        # https://www.18comic.biz/
        '18comic': {
            'detail_lis': '.btn-toolbar  a',
            'comic_title': '.panel-heading div',
            'comic_pages': '.panel-body .row div',
        },
        # https://m.happymh.com/
        'happymh': {
            'comic_title': '.mg-title',
            'comic_pages': '.scan-list div',
        },
    }
    detail_dicts = []
    current_host_key = ''

    @staticmethod
    def _happymh(response, comic_title):
        chapter_url = re.findall('"url":"(.*?)",', response.text)
        chapter_name = re.findall('"chapterName":"(.*?)",', response.text)
        for chapter in zip(chapter_name, chapter_url):
            name, url = chapter
            detail_dict = {
                'a_title': eval("'" + name + "'"),
                'a_href': url,
                'comic_title': comic_title,
            }
            Comic.detail_dicts.append(detail_dict)
        return Comic.detail_dicts[::-1]

    @staticmethod
    def get_detail_dicts(url, host_url, host_key) -> list:
        response = get_response(url)
        pq = pyquery.PyQuery(response.text)
        Comic.current_host_key = host_key
        rule = Comic.rules_dict.get(host_key, '')
        if not rule: raise KeyError('该网站还没/有适配')

        if Comic.current_host_key == 'happymh':
            comic_title = pq(rule.get('comic_title')).text()
            return Comic._happymh(response, comic_title)

        def detail_one_page(detail_url):
            response = get_response(detail_url)
            pq = pyquery.PyQuery(response.text)
            lis = pq(rule.get('detail_lis'))
            comic_title = pq(rule.get('comic_title')).text()
            if Comic.current_host_key == '18comic':
                if not lis.length:
                    detail_dict = {
                        'a_title': '共一话',
                        'a_href': host_url + pq('div.read-block a:first-child').attr('href').lstrip('/'),
                        'comic_title': comic_title,
                    }
                    Comic.detail_dicts.append(detail_dict)
                    return Comic.detail_dicts
                else:
                    print(f'该漫画共{len(lis)}章节')
            for li in lis:
                a_title = pyquery.PyQuery(li)('a').text()
                a_href = pyquery.PyQuery(li)('a').attr('href')
                for ch in r'\/:| <.･>?*"':
                    a_title = a_title.replace(ch, '･')  # 去除特殊字符
                    comic_title = comic_title.replace(ch, '･')  # 去除特殊字符
                if Comic.current_host_key == 'dongmanmanhua':
                    a_title = a_title.split('･')[0]
                detail_dict = {
                    'a_title': a_title,
                    'a_href': host_url + a_href.lstrip('/') if host_key not in a_href else a_href,
                    'comic_title': comic_title,
                }
                Comic.detail_dicts.append(detail_dict)

        detail_one_page(url)
        # 处理特殊情况 pyquery 好像不支持nth-child(n+3)这种类型过滤
        if Comic.current_host_key == 'hmba':
            Comic.detail_dicts = Comic.detail_dicts[9:]
        if Comic.current_host_key == 'dongmanmanhua':
            total_pages = len(pq('.paginate a'))
            for i in range(2, total_pages + 1):
                detail_one_page(url + f'&page={i}')
            Comic.detail_dicts.reverse()
        return Comic.detail_dicts

    # 该站点进行了分页处理, 需要特殊处理
    @staticmethod
    def _mm820(detail_url, pages: int):
        images_url = []
        for i in range(2, pages + 1):
            response = get_response(detail_url + f'?page={i}')
            pq = pyquery.PyQuery(response.text)
            divs = pq(Comic.rules_dict.get(Comic.current_host_key).get('comic_pages'))
            for div in divs:
                img_src = pyquery.PyQuery(div)('img').attr('data-original')
                if not img_src:
                    img_src = pyquery.PyQuery(div)('img').attr('src')
                images_url.append(img_src)
        return images_url

    @staticmethod
    def _cswhcs(pq):
        def is_next_url():
            next_url = ''
            fanye = pq('div.fanye')
            if '下一页' in fanye.text():
                next_url = pyquery.PyQuery(fanye)('a:nth-last-child(2)').attr('href')
            if next_url:
                next_url = 'https://cswhcs.com' + next_url
            else:
                next_url = None
            return next_url

        images_url = []
        next_url = is_next_url()
        while next_url:
            print(next_url)
            if next_url:
                response = get_response(next_url)
                pq = pyquery.PyQuery(response.text)
                divs = pq(Comic.rules_dict.get(Comic.current_host_key).get('comic_pages'))
                for div in divs:
                    img_src = pyquery.PyQuery(div)('img').attr('data-original')
                    if not img_src:
                        img_src = pyquery.PyQuery(div)('img').attr('src')
                    images_url.append(img_src)
                # 判断是否还有下一页
            next_url = is_next_url()
        return images_url

    @staticmethod
    def _dongmanmanhua(detail_url, ):
        images_url = []
        detail_url = 'https:' + detail_url
        response = get_response(detail_url)
        pq = pyquery.PyQuery(response.text)
        imgs = pq(Comic.rules_dict.get(Comic.current_host_key).get('comic_pages'))
        for img in imgs:
            image_url = pyquery.PyQuery(img).attr('data-url')
            images_url.append(image_url)
        return images_url

    @staticmethod
    def _nxueli(detail_url):
        response = get_response(detail_url)
        chapter_path_regix = 'chapterPath = "(.*?)"'
        chapter_images = eval(re.sub(r'\\', '', re.search('chapterImages = (\[.*?\])', response.text).group(1)))
        if Comic.current_host_key == 'nxueli':
            return ['https://images.nxueli.com' + i for i in chapter_images]
        elif Comic.current_host_key == '90ff':
            chapter_path = re.search(chapter_path_regix, response.text).group(1)
            return [f'http://90ff.bfdblg.com/{chapter_path}' + i for i in chapter_images]
        elif Comic.current_host_key == 'mh1234':
            chapter_path = re.search(chapter_path_regix, response.text).group(1)
            return [f'https://img.wszwhg.net/{chapter_path}' + i for i in chapter_images]
        elif Comic.current_host_key == '36mh':
            chapter_path = re.search(chapter_path_regix, response.text).group(1)
            return [f'https://img001.pkqiyi.com/{chapter_path}' + i for i in chapter_images]
        elif Comic.current_host_key == 'manhuaniu':
            return ['https://restp.dongqiniqin.com/' + i for i in chapter_images]

    @staticmethod
    def get_images_url(detail_dict: dict) -> dict:
        images_url = []
        nxueli_type = ('nxueli', '90ff', 'manhuaniu', '36mh', 'mh1234')
        cswhcs_type = ('cswhcs', 'kanleying', 'qinqinmh')
        mm820_type = ('mm820', 'hanmzj')

        detail_url = detail_dict.get('a_href')
        a_title = detail_dict.get('a_title')
        comic_title = detail_dict.get('comic_title')
        if Comic.current_host_key == 'dongmanmanhua':
            images_url = Comic._dongmanmanhua(detail_url)
            return {'images_url': images_url, 'a_title': a_title, 'comic_title': comic_title}

        elif Comic.current_host_key in nxueli_type:
            images_url = Comic._nxueli(detail_url)
            return {'images_url': images_url, 'a_title': a_title, 'comic_title': comic_title}
        elif Comic.current_host_key == 'happymh':
            response = get_response(detail_url)
            imgs_url = eval(re.search('var scans = (.*?);', response.text).group(1))
            imgs_url = [i for i in imgs_url if isinstance(i, dict)]
            for img_url in imgs_url:
                img_src = img_url['url']
                images_url.append(img_src)
            return {'images_url': images_url, 'a_title': a_title, 'comic_title': comic_title}
        response = get_response(detail_url)
        pq = pyquery.PyQuery(response.text)
        divs = pq(Comic.rules_dict.get(Comic.current_host_key).get('comic_pages'))
        for div in divs:
            img_src = pyquery.PyQuery(div)('img').attr('data-original')
            if not img_src:
                img_src = pyquery.PyQuery(div)('img').attr('src')
            images_url.append(img_src)
        #  处理特殊情况
        if Comic.current_host_key in cswhcs_type:
            images_url.extend(Comic._cswhcs(pq))
        if Comic.current_host_key in mm820_type:
            # 获取分页数
            pages = len(pq('.selectpage option'))
            images_url.extend(Comic._mm820(detail_url, pages))
        if Comic.current_host_key == '18comic':
            images_url = [img for img in images_url if img]

        return {'images_url': images_url, 'a_title': a_title, 'comic_title': comic_title}

    @staticmethod
    def download_images(images_dict):
        images_url = images_dict.get('images_url')
        a_title = images_dict.get('a_title').strip(' ')
        comic_title = images_dict.get('comic_title').strip(' ')
        print(f'开始下载{comic_title}-{a_title}\n')
        file_path = f'./{os.path.basename(__file__).strip(".py")}/{comic_title}/{a_title}/'
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        download(images_url, file_path, 10)
        suffix = ['jpg', 'png', 'gif', 'jpeg']
        file_list = sorted(
            [file_path + str(imgFileName) for imgFileName in os.listdir(file_path) if
             imgFileName.endswith(tuple(suffix))],
            key=lambda x: int(os.path.basename(x).split('.')[0])
        )
        file_name = f'{file_path}/{comic_title}-{a_title}'

        print(f'开始生成html{comic_title}-{a_title}\n')
        Comic.render_to_html(f'{file_name}.html', a_title,
                             [str(x) + '.jpg' for x in range(len(file_list))])

        print(f'开始生成PDF{comic_title}-{a_title}\n')
        Comic.make_pdf(f'{file_name}.pdf', file_list)

        comment = {
            'Website': 'https://amd794.com',
            'Password_1': '百度云',
            'Password_2': f'{comic_title}-{a_title}',
        }
        with open(f'{file_path}/Password.txt', 'w', encoding='utf-8') as f:
            f.write(str(comment))
        print(f'开始压缩文件{comic_title}-{a_title}\n')
        Comic.compress(f'{file_name}.rar', f'{file_path}/*', f'{comic_title}-{a_title}')


def main():
    url = input('漫画地址:').strip()
    try:
        host_key = re.match('https?://\w+\.(.*?)\.\w+/', url).group(1)  # kanleying
        host_url = re.match('https?://\w+\.(.*?)\.\w+/', url).group()  # https://www.kanleying.com/
    except AttributeError:
        host_key = re.match('https?://(.*?)\.\w+/', url).group(1)  # kanleying
        host_url = re.match('https?://(.*?)\.\w+/', url).group()  # https://kanleying.com/

    print(host_url, host_key)
    detail_dicts = Comic.get_detail_dicts(url, host_url, host_key)

    while True:
        # pprint(enumerate(detail_dicts, 1))
        index = input('>>>:')

        # 下载某章节之后所有章节
        if '>' in index:
            index = index.split('>')[-1]
            index = int(index)
            # pprint(detail_dicts[index:])
            for detail_dict in detail_dicts[index:]:
                images_url = Comic.get_images_url(detail_dict)
                Comic.download_images(images_url)
            continue

        # 下载全部
        elif index == '0':
            for detail_dict in detail_dicts:
                images_url = Comic.get_images_url(detail_dict)
                Comic.download_images(images_url)
            continue

        # 下载最新章节
        elif not index:
            detail_dict = detail_dicts.pop()
            images_url = Comic.get_images_url(detail_dict)
            Comic.download_images(images_url)
            continue

        # 下载某几章节 --> 2 6 9
        indexes = list(map(int, index.split(' ')))
        pprint(indexes)
        for i in indexes:
            detail_dict = detail_dicts[i - 1]
            images_url = Comic.get_images_url(detail_dict)
            Comic.download_images(images_url)


if __name__ == '__main__':
    main()
