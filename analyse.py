import  csv
import jieba
import pygal
from PIL import Image
import numpy
from wordcloud import WordCloud


def getDataFromCsv():
    list=[]
    with open("bilibili.csv","r",encoding="utf-8") as f:
        reader = csv.reader(f)
        for i in reader:
           list.append(i)
        f.close()
    del list[0]
    return list

def getCnt(star):
    data = getDataFromCsv()
    cnt = 0
    for i in data:
        if i[1] == star : cnt += 1
        else: continue
    return cnt

def doStar():
    mp4 = getCnt("mp4")
    mp3 = getCnt("mp3")
    flv = getCnt("flv")
    # line = pygal.Line()
    line = pygal.Bar()
    # line = pygal.Pie()
    line._x_title = "格式"
    line._y_title = "个数"
    # line.x_labels=["mp4","mp3","flv"]
    line.y_labels=[0,1,2,3,4,5]
    # line.add("B站视频",[mp4,mp3,flv])
    line.add("mp4",mp4)
    line.add("mp3",mp3)
    line.add("flv",flv)
    line.render_to_file("柱状图.svg")

def getWordCloud():
    data = getDataFromCsv()
    str = ""
    for i in data:
        str += i[0]
    cutWord = " ".join(jieba.cut(str))
    bgImg = numpy.array(Image.open("haixing.jpg"))
    cloud = WordCloud(
        font_path="‪C:\Windows\Fonts\simhei.ttf",
        background_color="white",
        mask=bgImg
    ).generate(cutWord)
    cloud.to_file("hx.png")

if __name__ == '__main__':
    # print(getDataFromCsv())
    doStar()
    getWordCloud()
    print("词云生成成功!")