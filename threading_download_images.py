# !/usr/bin/python3
# -*- coding: utf-8 -*-
# Time    : 2020/3/28 19:22
# Author  : Amd794
# Email   : 2952277346@qq.com
# Github  : https://github.com/Amd794


import os
import threading

import requests
from fake_useragent import UserAgent

requests.packages.urllib3.disable_warnings()


#   todo 获取返回的response
def get_response(url, error_file_path='.', max_count=3, timeout=30, ua_type='random', name='', ):
    ua = UserAgent()

    header = {
        'User-Agent': getattr(ua, ua_type),
        # 'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Mobile Safari/537.36',
        'referer': url,
    }
    count = 0
    while count < max_count:
        try:
            response = requests.get(url=url, headers=header, verify=False, timeout=timeout)
            response.raise_for_status()  # 如果status_code不是200,产生异常requests.HTTPError
            response.encoding = 'utf-8'
            return response
        except requests.exceptions.RequestException:
            print(f'\033[22;33;m{url} {name}连接超时, 正在进行第{count + 1}次连接重试, {timeout}秒超时重连\033[m')
            count += 1
    else:
        print(f'\033[22;31;m{url}重试{max_count}次后依然连接失败, 放弃连接...\033[m')
        if not os.path.exists(error_file_path):
            os.makedirs(error_file_path)
        with open(os.path.join(error_file_path, 'error_urls.txt'), 'a') as f:
            f.write(url + ' ' + name + '\n')
        return None


# todo 多线程
def thread_run(threads_num, target, args: tuple):
    threads = []
    for _ in range(threads_num):
        t = threading.Thread(target=target, args=args)
        t.start()
        threads.append(t)
    for t in threads:
        t.join()


# todo 下载图片
def download_images(file_path, images: list):
    from PIL import Image, ImageFont, ImageDraw

    def create_img(text, img_save_path):
        font_size = 24
        liens = text.split('\n')
        im = Image.new("RGB", (len(text) * 12, len(liens) * (font_size + 5)), '#fff')
        dr = ImageDraw.Draw(im)
        font_path = r"C:\Windows\Fonts\STKAITI.TTF"
        font = ImageFont.truetype(font_path, font_size)
        dr.text((0, 0), text, font=font, fill="blue")
        im.save(img_save_path)

    while images:
        glock = threading.Lock()
        glock.acquire()
        image_url = images.pop()
        file_name = str(len(images)) + '.jpg'
        print(f'{threading.current_thread()}:正在下载{file_name} ---> {image_url}')
        glock.release()
        response = get_response(image_url, file_path, name=file_name)
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        with open(os.path.join(file_path, file_name), 'wb') as f:
            if response:
                f.write(response.content)
            else:
                f.close()
                create_img(f'温馨提示{image_url}已经失效', os.path.join(file_path, file_name))

    if 'error_urls.txt' in os.listdir(file_path):
        from shutil import copyfile
        copyfile('./try_to_fix.py', os.path.join(file_path, 'try_to_fix.py'))


def download(image_list: list, file_path=os.getcwd(), threads_num=5):
    thread_run(threads_num, download_images, (file_path, image_list,))


if __name__ == '__main__':
    imgs = ['h15719904026351411247.jpg?x-oss-process=image/quality,q_90',
            'https://cdn.dongmanmanhua.cn/15719904028051411242.jpg?x-oss-process=image/quality,q_90',
            'https://cdn.dongmanmanhua.cn/15719904029381411248.jpg?x-oss-process=image/quality,q_90',]
    download(imgs, f'./{os.path.basename(__file__).strip(".py")}/test/')
