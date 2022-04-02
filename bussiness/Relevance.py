import matplotlib.pyplot as plt
from numpy import arange

from bussiness.spider import Spider

class Analysis():
    def __init__(self, _spider:Spider) :
        self.__spider:Spider=_spider
        pass
    def a_f_scale_relevance(self):
        x_y= self.__spider.get_scale_analysis_data()
        # plt.plot(x_y[0], x_y[1])
        plt.scatter(x_y[0], x_y[1])
        plt.xlabel('scale')
        plt.ylabel('price_increase')
        plt.title('datamodel_between_scale_and_price_increase_in_2021')
        plt.legend()
        plt.show()
        pass
    def draw_test(self):
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