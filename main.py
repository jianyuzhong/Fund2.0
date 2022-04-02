
from bussiness.Relevance import Analysis
from bussiness.spider import Spider
import time
from datetime import datetime

if __name__=='__main__':
    spider= Spider()
    analysis= Analysis(spider)
    analysis.a_f_scale_relevance()
    # analysis.draw_test()
    # analysis.draw_points_test()
    # spider.start()
    a=0