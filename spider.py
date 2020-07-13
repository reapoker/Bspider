import requests, threading
import json, os, time, random
from lxml import etree
import subprocess
import csv

requests.packages.urllib3.disable_warnings()


def readList():
    res = []
    try:
        with open("videos.txt", 'r') as f:
            line = f.readline().strip()
            while line:
                if not line in res:
                    res.append(line)

                line = f.readline().strip()
    except:
        pass
    return res


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3970.5 Safari/537.36',
    'Referer': 'https://www.bilibili.com/'
}

list = []

def writeInto(dir):
    with open("bilibili.csv","a+",encoding="utf-8",newline="") as openFile:
        head = ["视频名称","格式","路径"]
        # 写入数据
        f = csv.writer(openFile)
        f.writerow(head)
        # 多条数据
        con = dir
        # print(con)
        f.writerows(con)
        # 关闭表格
        openFile.close()


def GetBiliVideo(homeurl, session=requests.session()):
    res = session.get(url=homeurl, headers=headers, verify=False)
    html = etree.HTML(res.content)
    videoinforms = str(html.xpath('//head/script[3]/text()')[0])[20:]
    videojson = json.loads(videoinforms)
    # 获取视频链接和音频链接
    VideoURL = videojson['data']['dash']['video'][0]['baseUrl']
    AudioURl = videojson['data']['dash']['audio'][0]['baseUrl']
    # print(videojson)
    # 获取视频资源的名称
    name = str(html.xpath("//h1/@title")[0]).strip().replace(" ", "")

    # 下载视频和音频
    dv = threading.Thread(target=BiliBiliDownload,
                          kwargs={"homeurl": homeurl, "url": VideoURL, "Video": True, "session": session, "name": name})
    av = threading.Thread(target=BiliBiliDownload,
                          kwargs={"homeurl": homeurl, "url": AudioURl, "Video": False, "session": session,
                                  "name": name})
    dv.start()
    av.start()
    dv.join()
    av.join()

    print("开始合并%s音视频" % name)

    avpath = "./%s/%s_audio.mp4" % (name, name)
    dvpath = "./%s/%s_video.mp4" % (name, name)
    outpath = "./%s/%s.mp4" % (name, name)
    # avpath = "H:\Python\Code\Bspider\%s\%s_audio.mp4" % (name, name)
    # dvpath = "H:\Python\Code\Bspider\%s\%s_video.mp4" % (name, name)
    # outpath = "H:\Python\Code\Bspider\%s\%s.mp4" % (name, name)

    CombineVideoAudio(avpath, dvpath, outpath)
    # CombineVideoAudio(os.listdir(avpath), os.listdir(dvpath), os.listdir(outpath))
    list.append((name,"mp4",outpath))



def BiliBiliDownload(homeurl, url, name, Video=True, session=requests.session()):
    headers.update({'Referer': homeurl})
    session.options(url=url, headers=headers, verify=False)

    path = "./%s" % name
    loop = True
    while loop:
        try:
            if not os.path.exists(path):
                os.mkdir(path)

            loop = False
        except Exception as e:
            print(e)
            time.sleep(random.randint(1, 100))

    _type = "音频"

    filetype = "audio"
    if Video:
        _type = "视频"
        filetype = "video"

    file = "%s/%s_%s.mp4" % (path, name, filetype)

    print("开始下载 %s%s 文件" % (name, _type))
    # 每次下载1M的数据
    begin = 0
    end = 1024 * 512 - 1
    flag = 0
    while True:
        headers.update({'Range': 'bytes=' + str(begin) + '-' + str(end)})
        res = session.get(url=url, headers=headers, verify=False)
        if res.status_code != 416:
            begin = end + 1
            end = end + 1024 * 512
        else:
            headers.update({'Range': str(end + 1) + '-'})
            res = session.get(url=url, headers=headers, verify=False)
            flag = 1
        with open(file, 'ab') as fp:
            fp.write(res.content)
            fp.flush()

        # data=data+res.content
        if flag == 1:
            fp.close()
            break
    print("文件 %s%s 下载完成" % (name, _type))


def CombineVideoAudio(videopath, audiopath, outpath):
    # print("ffmpeg.exe -i %s -i %s -vcodec copy -acodec copy %s" % (videopath, audiopath, outpath))
    try:
        subprocess.call("ffmpeg.exe -i %s -i %s -vcodec copy -acodec copy %s" % (videopath, audiopath, outpath), shell=True)
        os.remove(videopath)
        os.remove(audiopath)
        print("%s 音视频合并完成" % outpath)
    except:
        print("%s 音视频合成失败" % outpath)


if __name__ == '__main__':
    start = time.time()
    print("%s  欢迎使用bilibili视频下载器  %s" % ('=' * 10, '=' * 10))
    print()

    urls = readList()

    print("共有 %s 个视频待下载" % len(urls))

    threads = []

    for url in urls:
        threads.append(threading.Thread(target=GetBiliVideo, args=(url,)))

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    cost = time.time() - start

    print()
    print("所有视频下载完成，用时 %s ms" % cost)

    writeInto(list)