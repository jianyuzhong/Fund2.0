import matplotlib.pyplot as plt
from numpy import arange
import numpy as np
from scipy.optimize import curve_fit

from bussiness.spider import Spider

    #自定义函数 e指数形式
def func(x, a, b,c):
    return a*x*x+b*x+c
class Analysis():
    """_summary_
    """
    def __init__(self, _spider:Spider) :
        """_summary_

        Args:
            _spider (Spider): 一个爬虫
        """
        self.__spider:Spider=_spider
        pass
    def a_f_scale_relevance(self):
        x_y= self.__spider.get_scale_analysis_data()
        # plt.plot(x_y[0], x_y[1])
        x=x_y[0]
        y=x_y[1]
        
        #也可使用yvals=np.polyval(f1, x)
        popt, pcov = curve_fit(func, x, y)
        a=popt[0]
        b=popt[1]
        c=popt[2]
        print('pcov is :\n',pcov)
        yvals=[func(item,a,b,c) for item in x] 
        # yvals = func(x,a,b,c)
        # plt.scatter(x, y)
        plt.scatter(x, yvals)
        # plt.plot(x, yvals,'r', label='polyfit')
        plt.xlabel('scale')
        plt.ylabel('price_increase')
        plt.title('datamodel_between_scale_and_price_increase_in_2021')
        plt.legend()
        plt.show()
        pass
    def draw_test(self):

        #定义x、y散点坐标
        x = [10,20,30,40,50,60,70,80]
        x = np.array(x)
        print('x is :\n',x)
        num = [174,236,305,334,349,351,342,323]
        y = np.array(num)
        print('y is :\n',y)
        #用3次多项式拟合
        f1 = np.polyfit(x, y, 3)
        print('f1 is :\n',f1)
        
        p1 = np.poly1d(f1)
        print('p1 is :\n',p1)
        
        #也可使用yvals=np.polyval(f1, x)
        yvals = p1(x)  #拟合y值
        print('yvals is :\n',yvals)
        #绘图
        plot1 = plt.plot(x, y, 's',label='original values')
        plot2 = plt.plot(x, yvals, 'r',label='polyfit values')
        plt.xlabel('x')
        plt.ylabel('y')
        plt.legend(loc=4) #指定legend的位置右下角
        plt.title('polyfitting')
        plt.show()


        # line 1 points
        x1 = [1,2,3]
        y1 = [2,4,1]
        # plotting the line 1 points
        plt.plot(x1, y1, label = "line 1")
        
        # line 2 points
        x2 = [1,2,3]
        y2 = [4,1,3]
        # plotting the line 2 points
        plt.plot(x2, y2, label = "line 2")
        
        # naming the x axis
        plt.xlabel('x - axis')
        # naming the y axis
        plt.ylabel('y - axis')
        # giving a title to my graph
        plt.title('Two lines on same graph!')
        
        # show a legend on the plot
        plt.legend()
        
        # function to show the plot
        plt.show()
    def draw_points_test(self):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        x_points = arange(0,9)
        y_points = arange(0,9)
        p = ax.plot(x_points, y_points, 'b')
        ax.set_xlabel('x-points')
        ax.set_ylabel('y-points')
        ax.set_title('Simple XY point plot')
        fig.show()
        pass