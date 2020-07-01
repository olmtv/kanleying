# !/usr/bin/python3
# -*- coding: utf-8 -*-
# Time    : 2020/3/30 23:49
# Author  : Amd794
# Email   : 2952277346@qq.com
# Github  : https://github.com/Amd794

import os
import platform as pf
import subprocess

import requests
from PIL import Image, ImageFont, ImageDraw

requests.packages.urllib3.disable_warnings()


def create_img(text, img_save_path):
    font_size = 24
    liens = text.split('\n')
    im = Image.new("RGB", (len(text) * 12, len(liens) * (font_size + 5)), '#fff')
    dr = ImageDraw.Draw(im)
    font_path = r"C:\Windows\Fonts\STKAITI.TTF"
    font = ImageFont.truetype(font_path, font_size)
    dr.text((0, 0), text, font=font, fill="blue")
    im.save(img_save_path)


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


def try_download_error_img(error_file):
    fail_url = []
    with open(error_file) as f:
        images_url = f.read().split('\n')
        images_url = [i for i in images_url if i != '']
    for image_url in images_url:
        image_url, name = image_url.split(' ')

        response = requests.get(image_url, verify=False)
        with open(name, 'wb') as f:
            if response:
                f.write(response.content)
                print(f'成功{image_url}-{name}')
            else:
                f.close()
                fail_url.append(image_url + ' ' + name + '\n')
                print(f'失败{image_url}-{name}')
                create_img(f'温馨提示{image_url}-{name}已经失效', name)
    if fail_url:
        with open(error_file, 'w') as f:
            f.write(''.join(fail_url))
    else:
        print('全部完成')
        os.remove(error_file)


def compress(target, source, pwd='', delete_source=False, ):
    """
        压缩加密，并删除原数据
        window系统调用rar程序

        linux等其他系统调用内置命令 zip -P123 tar source
        默认不删除原文件
    """
    if pwd: pwd = '-p' + pwd
    if pf.system() == "Windows":
        cmd = f'rar a {pwd} {target} {source} -x*.rar -x*.py'
        p = subprocess.Popen(cmd, executable=r'D:/Sorfwares/WinRAR/WinRAR.exe')
        p.wait()
    else:
        cmd = f'zip a {pwd} {target} {source} -x*.rar -x*.py'
        p = subprocess.Popen(cmd)
        p.wait()
        # os.system(" ".join(cmd))
    if delete_source:
        os.remove(source)


if __name__ == '__main__':
    error_file = 'error_urls.txt'
    file_name = ''
    for imgFileName in os.listdir('.'):
        if imgFileName.endswith('pdf'):
            file_name = (os.path.splitext(imgFileName)[0])
    print(f'当前正常尝试修复---->{file_name}')
    try_download_error_img(error_file)

    suffix = ['jpg', 'png', 'gif', 'jpeg']
    file_list = ['./' + str(imgFileName) for imgFileName in os.listdir('.') if imgFileName.endswith(tuple(suffix))]
    file_list.sort(key=lambda x: int(os.path.basename(x).split('.')[0]))
    # print(file_list)
    make_pdf(file_name + '-重构' + '.pdf', file_list)
    os.remove(file_name + '.pdf')
    print(file_name + '-重构' + '.pdf' + '---->successful')
    compress(f'{file_name}.rar', '*', file_name)
