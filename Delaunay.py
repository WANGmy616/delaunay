import tkinter
from tkinter import filedialog
import csv

# 根据两点坐标计算距离
def caldis(x1, y1, x2, y2):
    return ((x1-x2)**2+(y1-y2)**2)**0.5

# 输入三角形三个顶点，计算外接圆圆心及半径
def calcenter(x1, y1, x2, y2, x3, y3):
    y1=-y1  # 计算公式是根据平面直角坐标推算的，原点在左下角，但是计算机屏幕坐标原点在右上角，所以计算式y坐标取负
    y2=-y2
    y3=-y3
    if (y1 != y3 and y1 != y2 and y2 != y3) :  # 判断是否有y坐标相等，即三角形某边斜率为0的情况，避免出现坟分母为0的错误
        if(((x3-x1)/(y3-y1))-((x2-x1)/(y2-y1))) == 0:
            x2 = x2+1
        x = (((y1 + y3) / 2) + ((x1 + x3) / 2) * ((x3 - x1) / (y3 - y1)) - ((y1 + y2) / 2) - ((x1 + x2) / 2) *
             ((x2 - x1) / (y2 - y1))) / (((x3 - x1) / (y3 - y1)) - ((x2 - x1) / (y2 - y1)))
        y = -((x3 - x1) / (y3 - y1)) * x + ((y1 + y3) / 2) + (((x1 + x3) / 2) * ((x3 - x1) / (y3 - y1)))
        return (x, -y, caldis(x, y, x1, y1))
    elif (y1 == y3 and y1 != y2 and y2 != y3):  # 若存在斜率为0的边则计算可简化
        x=(x1+x3)/2
        y=-((x2-x1)/(y2-y1))*x+((y1+y2)/2)+((x2-x1)/(y2-y1))*((x1+x2)/2)
        return (x, -y, caldis(x, y, x1, y1))  # 返回值为元组（圆心横坐标x，圆心纵坐标y，外接圆半径r），计算出来的y值要返回屏幕坐标所以再次取负
    elif (y1 != y3 and y1 == y2 and y2 != y3):
        x = (x1 + x2) / 2
        y = -((x3 - x1) / (y3 - y1)) * x + ((y1 + y3) / 2) + ((x3 - x1) / (y3 - y1)) * ((x1 + x3) / 2)
        return (x, -y, caldis(x, y, x1, y1))
    elif (y1 != y3 and y1 != y2 and y2 == y3):
        x = (x3 + x2) / 2
        y = -((x3 - x1) / (y3 - y1)) * x + ((y1 + y3) / 2) + ((x3 - x1) / (y3 - y1)) * ((x1 + x3) / 2)
        return (x, -y, caldis(x, y, x1, y1))
    else:
        return None

class getTIN:   # 定义窗口及操作类
    def __init__(self):
        self.path = str()  # 坐标文件路径
        self.pointlist = []  # 存放所有点坐标的列表
        self.linelist = []  # 存放线的列表，每条线用两个点号表示连线
        self.tk=tkinter.Tk()  # 定义主窗口
        self.tk.title('MyTIN')
        self.tk.geometry('1200x720')
        self.shengzhang = tkinter.Button(self.tk, text='生长算法', width=15, command=self.drawTIN_shengzhang)
        self.shengzhang.place(x=1050, y=100)  # 定义按钮，关联到生长算法计算TIN的的函数
        self.readin = tkinter.Button(self.tk, text='读入坐标文件', width=15, command=self.getfile)
        self.readin.place(x=1050, y=50)
        self.can = tkinter.Canvas(self.tk, width=950, height=620, bg='white')
        self.can.place(x=50, y=50)

        self.tk.mainloop()

    def getfile(self):  # 选择坐标文件（*.csv），从文件中读入坐标存入pointlist列表并在绘图区展示出来
        self.path = filedialog.askopenfilename()
        f = open(self.path, 'r')
        fd = csv.reader(f)
        self.pointlist = list(fd)
        for i in range(0, len(self.pointlist)):
            self.can.create_oval(int(self.pointlist[i][0])-2, int(self.pointlist[i][1])-2, int(self.pointlist[i][0])+2,
                                 int(self.pointlist[i][1])+2, fill='black')
            self.can.create_text(int(self.pointlist[i][0])+7, int(self.pointlist[i][1])-7, text=str(i))

    def drawTIN_shengzhang(self):
        j = 1
        k = 0
        mindis = ((int(self.pointlist[0][0]) - int(self.pointlist[1][0])) ** 2 + (int(self.pointlist[0][1]) - int(self.pointlist[1][1])) ** 2) ** 0.5
        x = len(self.pointlist)
        for i in range(1, x):
            dis = ((int(self.pointlist[0][0]) - int(self.pointlist[i][0])) ** 2 + (int(self.pointlist[0][1]) - int(self.pointlist[i][1])) ** 2) ** 0.5
            if dis < mindis:
                mindis = dis
                j = i
        self.linelist.append((k, j))  # 首先计算出距起始点（点号为0）距离最短的点，以这两点的连线作为基线开始生长
        self.shengzhangjixian(k, j)

    def drawTIN(self):  # 根据线文件在绘图区绘制出TIN
        for i in self.linelist:
            self.can.create_line(self.pointlist[i[0]][0], self.pointlist[i[0]][1], self.pointlist[i[1]][0], self.pointlist[i[1]][1])

    def shengzhangjixian(self, i, j):  # 根据某一基线开始生长的函数
        x = len(self.pointlist)
        for k in range(0, x):  # 遍历没一个点，判断是否与基线构成D三角形
            n = 0  # n用于统计外接圆内的点数
            if ((k, i) not in self.linelist) and ((i, k) not in self.linelist) and ((j, k) not in self.linelist) and ((k, j) not in self.linelist):
                for y in range(0, x):  # 遍历每一个点，判断
                    if y == i or y == j or y == k:
                        continue
                    if(calcenter(int(self.pointlist[i][0]),int(self.pointlist[i][1]),int(self.pointlist[j][0]),int(self.pointlist[j][1]),int(self.pointlist[k][0]),int(self.pointlist[k][1]))==None):
                        continue
                    else:
                        xyr=calcenter(int(self.pointlist[i][0]),int(self.pointlist[i][1]),int(self.pointlist[j][0]),int(self.pointlist[j][1]),int(self.pointlist[k][0]),int(self.pointlist[k][1]))
                    if caldis(xyr[0],xyr[1],int(self.pointlist[y][0]),int(self.pointlist[y][1])) < xyr[2]: #判断点是否在外接圆内
                        n=n+1
                    else:
                        continue
            else:continue

            if n == 0:  # 判断是否为D三角形
                self.linelist.append((k, i))  # 将新生成的边的端点号加入线列表
                self.drawTIN()  # 调用绘制函数绘制TIN
                self.shengzhangjixian(k, i)  # 以生成的新边作为基线，迭代计算
                self.linelist.append((k, j))
                self.drawTIN()
                self.shengzhangjixian(k, j)
            else: continue


if __name__ == '__main__':
    MyTIN = getTIN()
