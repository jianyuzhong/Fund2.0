from concurrent.futures import ThreadPoolExecutor
import datetime 
from datetime import datetime, timedelta
import json,numpy,re,traceback
from matplotlib.pyplot import flag
from operator import le
from bs4 import BeautifulSoup
import time,requests,demjson,threading,pytz
from commonbaby.httpaccess import HttpAccess
from commonbaby.mslog import MsFileLogConfig,MsLogLevels,MsLogManager, msloglevel, mslogmanager
MsLogManager.static_initial(
    dft_lvl=MsLogLevels.INFO,msficfg=MsFileLogConfig(fi_dir=r"./_log")
)

from model.FundResult import FundResult

def obj_dict(obj):
    return obj.__dict__
class Spider():
    def __init__(self):
        self._logger=MsLogManager.get_logger("fund_spider")
    def start(self):
        url=f"http://fund.eastmoney.com/data/rankhandler.aspx?op=ph&dt=kf&ft=all&rs=&gs=0&sc=6yzf&st=desc&sd={time.strftime('%Y-%m-%d', time.localtime())}&ed={time.strftime('%Y-%m-%d', time.localtime())}&qdii=&tabSubtype=,,,,,&pi=1&pn=50&dx=1"
        payload={}
        headers = {
  'Host': 'fund.eastmoney.com',
  'Proxy-Connection': 'keep-alive',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
  'Accept': '*/*',
  'Referer': 'http://fund.eastmoney.com/data/fundranking.html',
  'Accept-Encoding': 'gzip, deflate',
  'Accept-Language': 'zh-CN,zh;q=0.9'
}
    #    response = requests.request("GET", url, headers=headers, data=payload)
        ha=HttpAccess(0,)
        response=ha.get(url=url,headers=headers)
        res=response.text
        front_len=len('var rankData =')
        res=res[front_len:]
        res=res[:-1]
        json_data=demjson.decode(res)   
        c_num=1
        max_page=json_data["allPages"]
        rowNumber=0
        f_result=[]
        while c_num<=max_page:
            url=f"http://fund.eastmoney.com/data/rankhandler.aspx?op=ph&dt=kf&ft=all&rs=&gs=0&sc=6yzf&st=desc&sd={time.strftime('%Y-%m-%d', time.localtime())}&ed={time.strftime('%Y-%m-%d', time.localtime())}&qdii=&tabSubtype=,,,,,&pi={c_num}&pn=50&dx=1"
            response=ha.get(url=url,headers=headers)
            res=response.text
            front_len=len('var rankData =')
            res=res[front_len:] 
            res=res[:-1]
            try:
                json_data=demjson.decode(res)   
            except Exception as ex:
                self._logger.error(f'url{url} json error {res}')
            # this.__get_single()
            with ThreadPoolExecutor(max_workers=5) as executor:
                for item in json_data["datas"]:
                    single_data= str(item).split(',')
                    try:
                        temp_data= self.__get_single__(single_data[0])
                        f_data= self.__compute__(temp_data)
                        f_data.m_experience=self.__get_m_experience__(single_data[0],f_data)
                        f_data.scale=self.__get_scale__(single_data[0])
                        f_result.append(f_data)
                        f_data.code=single_data[0]
                        f_data.name=single_data[1]
                        f_data.f_url=f'http://fundf10.eastmoney.com/jjjz_{single_data[0]}.html'
                        # ssss=json.dumps(f_result,cls=DecEncoder)
                        rowNumber+=1
                    except Exception as ex:
                        traceback.print_exc()
                        self._logger.error(f"get s_data error with messages {str(ex)}")
            self._logger.info(f'\n\nprogress {c_num}/{max_page}\n\n')
            c_num+=1
            time.sleep(1)
    def __get_single__(self,code:str,c_day:int=30):
        #日增长率
        result=[]
        # code=161815
        try:
            # s_data.code="000390"
            headers = {
  'Host': 'api.fund.eastmoney.com',
  'Connection': 'keep-alive',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
  'Accept': '*/*',
  'Referer': f'http://fundf10.eastmoney.com/jjjz_{code}.html',
  'Accept-Encoding': 'gzip, deflate',
  'Accept-Language': 'zh-CN,zh;q=0.9'
}
            url=f"http://api.fund.eastmoney.com/f10/lsjz?fundCode={code}&pageIndex=1&pageSize={c_day}&startDate=&endDate="
            ha=HttpAccess(0)
            res=ha.get(url=url,headers=headers)
            t=res.text
            json_data=demjson.decode(t)
            if json_data["ErrCode"]!=0:
                return None
            orgin_data=json_data["Data"]["LSJZList"]
            if isinstance(orgin_data,list):
                for item in orgin_data:
                    if len(str(item["JZZZL"]))>0:
                        result.append(float(item["JZZZL"]))
            #    result= list(map(lambda x:float(x["JZZZL"]),orgin_data))
            return result
        except Exception as ex:
            self._logger.error(f"get compare error{ex}")
    def __compute__(self,f_data:list):
        result=FundResult()
        f_len=len(f_data)
        if f_len==0:
            return None
        half_p=int(f_len/2)
        f_data.sort()
        result.max=f_data[f_len-1]
        result.min=f_data[0]
        total=sum(f_data)
        result.average=total/f_len
        total=0.0
        for item in f_data:
            total+=(item-result.average)*(item-result.average)
        result.variance=total/f_len   
        return result
    def __get_scale__(self,code:str):
        result=None
        try:
            url=f"http://fundf10.eastmoney.com/jjjz_{code}.html"
            headers = {
    'Host': 'fundf10.eastmoney.com',
    'Proxy-Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Referer': f'http://fund.eastmoney.com/{code}.html',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9'
    }
            ha=HttpAccess(0,)
            res=ha.get(url=url,headers=headers)
            i_soup=BeautifulSoup(res.text,'lxml')
            script_content=str(i_soup.select('label')[-3].select_one('span'))
            paire=re.compile(r'(  .*?)元',  re.MULTILINE|re.IGNORECASE)
            obj= paire.findall(script_content)
            if len(obj)>0 and len(str(obj[0]))>0:
                result=str(obj[0]).replace(' ','').replace('亿','')
        except Exception as ex:
            self._logger.error(f"get cguess error {ex}")
            if str(result).__contains__('x'):
                raise Exception("Invalid data!")
        return result
    def __get_m_experience__(self,code:str,f_data:FundResult):
        m_experience=0
        try:
            result=None
            url=f"http://fundf10.eastmoney.com/jjjl_{code}.html"
            headers = {
    'Host': 'fundf10.eastmoney.com',
    'Proxy-Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Referer': f'http://fund.eastmoney.com/{code}.html',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9'
    }
            ha=HttpAccess(0,)
            res=ha.get(url=url,headers=headers)
            i_soup=BeautifulSoup(res.text,'lxml')
            m_url=str(i_soup.select('table')[1].select('tr td')[2].find('a').attrs["href"])
            payload={}
            headers = {}
            response = requests.request("GET", m_url, headers=headers, data=payload)
            response.encoding='utf-8'
            m_soup=BeautifulSoup(response.text,'lxml')
            data=m_soup.select('[class="right jd"]')
            m_experience= data[0].select('span')[0].nextSibling
            f_data.m_url=m_url
        except Exception as ex:
            self._logger.error(f"get cguess error {ex}")
        # return self.__convert_to_days__(m_experience)
        return m_experience
    def __convert_to_days__(self,experience_str:str):
        if len(str(experience_str))==0:
            return 0
        res=0
        experience_str=experience_str.replace('天','')
        experience= experience_str.split('年又')
        if len(experience)>1:
            res=int(experience[0])*365+int(experience[1])
        else:
            res=int(experience_str)
        return res
    def get_fundlist_with_conditions(self,code:str,num:int=30,pageIndex:int=1,startDate:str='',endDate:str='',field:str='JZZZL'):
        #日增长率
        result=[]
        # code=161815
        try:
            # s_data.code="000390"
            headers = {
  'Host': 'api.fund.eastmoney.com',
  'Connection': 'keep-alive',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
  'Accept': '*/*',
  'Referer': f'http://fundf10.eastmoney.com/jjjz_{code}.html',
  'Accept-Encoding': 'gzip, deflate',
  'Accept-Language': 'zh-CN,zh;q=0.9'
}
            url=f"http://api.fund.eastmoney.com/f10/lsjz?fundCode={code}&pageIndex={pageIndex}&pageSize={num}&startDate={startDate}&endDate={endDate}"
            ha=HttpAccess(0)
            res=ha.get(url=url,headers=headers)
            t=res.text
            json_data=demjson.decode(t)
            if json_data["ErrCode"]!=0:
                return None
            orgin_data=json_data["Data"]["LSJZList"]
            if isinstance(orgin_data,list):
                for item in orgin_data:
                    if len(str(item[field]))>0:
                        result.append(float(item[field]))
            #    result= list(map(lambda x:float(x["JZZZL"]),orgin_data))
            return result
        except Exception as ex:
            self._logger.error(f"get compare error{ex}")
    def get_code_list(self,num=0):
                #日增长率
        result=[]
        # code=161815
        try:
            url=f"http://fund.eastmoney.com/data/rankhandler.aspx?op=ph&dt=kf&ft=all&rs=&gs=0&sc=6yzf&st=desc&sd={time.strftime('%Y-%m-%d', time.localtime())}&ed={time.strftime('%Y-%m-%d', time.localtime())}&qdii=&tabSubtype=,,,,,&pi=1&pn=50&dx=1"
            payload={}
            headers = {
    'Host': 'fund.eastmoney.com',
    'Proxy-Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
    'Accept': '*/*',
    'Referer': 'http://fund.eastmoney.com/data/fundranking.html',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9'
    }
        #    response = requests.request("GET", url, headers=headers, data=payload)
            ha=HttpAccess(0,)
            response=ha.get(url=url,headers=headers)
            res=response.text
            front_len=len('var rankData =')
            res=res[front_len:]
            res=res[:-1]
            json_data=demjson.decode(res)   
            c_num=1
            max_page=json_data["allPages"]
            rowNumber=0
            is_break=False
            while c_num<=max_page:
                url=f"http://fund.eastmoney.com/data/rankhandler.aspx?op=ph&dt=kf&ft=all&rs=&gs=0&sc=6yzf&st=desc&sd={time.strftime('%Y-%m-%d', time.localtime())}&ed={time.strftime('%Y-%m-%d', time.localtime())}&qdii=&tabSubtype=,,,,,&pi={c_num}&pn=50&dx=1"
                response=ha.get(url=url,headers=headers)
                res=response.text
                front_len=len('var rankData =')
                res=res[front_len:] 
                res=res[:-1]
                try:
                    json_data=demjson.decode(res)   
                    for item in json_data["datas"]:
                        single_data= str(item).split(',')
                        try:
                            yield single_data[0]
                            result.append(single_data[0])
                            rowNumber+=1
                            if num!=0 and rowNumber>=num:
                                is_break=True
                                break
                        except Exception as ex:
                            traceback.print_exc()
                            self._logger.error(f"get s_data error with messages {str(ex)}")
                except Exception as ex:
                    self._logger.error(f'url{url} json error {res}')
                if is_break:
                    break
        except Exception as ex:
            self._logger.error(f'{ex}')
        return result
    def get_scale_analysis_data(self):
        x=[]
        y=[]
        for code in self.get_code_list(100):
            x1=self.__get_scale__(code)
            if x.__contains__(float(x1)):
                continue
            x.append(float(x1))
            y1=self.__get_year_increase(code,datetime(2021,1,1),datetime(2021,12,31))
            y.append(y1)
        result=[]
        result.append(x)
        result.append(y)
        return result
    def __get_year_increase(self,code,year_start:datetime,year_end:datetime):
        start_date=(year_start+timedelta(days=15)).strftime('%Y-%m-%d')
        end_date=(year_end+timedelta(days=-15)).strftime('%Y-%m-%d')
        start_increase= self.get_fundlist_with_conditions(code,num=15,startDate=year_start.strftime('%Y-%m-%d'),endDate=start_date,field='LJJZ')
        end_increase= self.get_fundlist_with_conditions(code,num=15,startDate=end_date,endDate=year_end,field='LJJZ')
        if start_increase==None or end_increase==None:
            return None
        if len(start_increase)==0 or len(end_increase)==0:
            return None
        result=float(end_increase[0])-float(start_increase[-1])
        return result


