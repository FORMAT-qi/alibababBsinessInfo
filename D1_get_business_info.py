# -*- coding: utf-8 -*-

from selenium.webdriver import ChromeOptions
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import re
import time
from lxml import etree
import csv


# 完成登录 登陆
class Chrome_drive():
    def __init__(self):

        option = ChromeOptions()
        option.add_experimental_option('excludeSwitches', ['enable-automation'])
        option.add_experimental_option('useAutomationExtension', False)
        NoImage = {"profile.managed_default_content_settings.images": 2}  # 控制 没有图片
        option.add_experimental_option("prefs", NoImage)
        # option.add_argument(f'user-agent={ua.chrome}')  # 增加浏览器头部
        # chrome_options.add_argument(f"--proxy-server=http://{self.ip}")  # 增加IP地址。。
        # option.add_argument('--headless')  #无头模式 不弹出浏览器
        self.browser = webdriver.Chrome(executable_path="./chromedriver", options=option)
        self.browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': 'Object.defineProperty(navigator,"webdriver",{get:()=>undefined})'
        })  #去掉selenium的驱动设置

        self.browser.set_window_size(1200,768)
        self.wait = WebDriverWait(self.browser, 12)

    def get_login(self):
        url='https://passport.alibaba.com/icbu_login.htm'
        self.browser.get(url)
        #self.browser.maximize_window()  # 在这里登陆的中国大陆的邮编
        #这里进行人工登陆。
        k = input("输入1\n>")
        if 'Your Alibaba.com account is temporarily unavailable' in self.browser.page_source:
            self.browser.close()
        while k == 1:
            break
        self.browser.refresh()  # 刷新方法 refres
        return


    #获取判断网页文本的内容：
    def index_page(self,page,wd):
        """
        抓取索引页
        :param page: 页码
        """
        print('正在爬取第', page, '页')

        url = f'https://www.alibaba.com/trade/search?page={page}&keyword={wd}&f1=y&indexArea=company_en&viewType=L&n=38'
        js1 = f" window.open('{url}')"  # 执行打开新的标签页
        print(url)
        self.browser.execute_script(js1)  # 打开新的网页标签
            # 执行打开新一个标签页。
        self.browser.switch_to.window(self.browser.window_handles[-1])  # 此行代码用来定位当前页面窗口
        self.buffer()  # 网页滑动  成功切换
            #等待元素加载出来
        time.sleep(3)

        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#J-items-content')))
            #获取网页的源代码
        html =  self.browser.page_source

        self.get_products(wd,html)

        self.close_window()


    def buffer(self): #滑动网页的
        for i in range(33):
            time.sleep(0.5)
            self.browser.execute_script('window.scrollBy(0,380)', '')  # 向下滑行300像素。

    def close_window(self):
        length=self.browser.window_handles
        if  len(length) > 3:
            self.browser.switch_to.window(self.browser.window_handles[1])
            self.browser.close()
            time.sleep(1)
            self.browser.switch_to.window(self.browser.window_handles[-1])

    def get_products(self, wd, html_text):
        """
        提取商品数据
        """
        e = etree.HTML(html_text)
        item_main = e.xpath('//div[@id="J-items-content"]//div[@class="item-main"]')
        items = e.xpath('//div[@id="J-items-content"]//div[@class="item-main"]')
        print('公司数 ', len(items))
        for li in items:
            company_name = ''.join(li.xpath('./div[@class="top"]//h2[@class="title ellipsis"]/a/text()'))  # 公司名称
            company_phone_page = ''.join(li.xpath('./div[@class="top"]//a[@class="cd"]/@href'))  # 公司电话连接
            product = ''.join(li.xpath('.//div[@class="value ellipsis ph"]/text()'))  # 主要产品
            Attrs = li.xpath('.//div[@class="attrs"]//span[@class="ellipsis search"]/text()')
            length = len(Attrs)
            counctry = ''
            total_evenue = ''
            sell_adress = ''
            product_img = ''
            if length > 0:
                counctry = ''.join(Attrs[0])  # 国家
            if length > 1:
                total_evenue = ''.join(Attrs[1])  # Total 收入
            if length > 2:
                sell_adress = ''.join(Attrs[2])  # 主要销售地
            if length > 3:
                sell_adress += '、' + ''.join(Attrs[3])  # 主要销售地
            if length > 4:
                sell_adress += '、' + ''.join(Attrs[4])  # 主要销售地
            product_img_list = li.xpath('.//div[@class="product"]/div/a/img/@src')
            if len(product_img_list) > 0:
                product_img = ','.join(product_img_list)  # 产品图片
            self.browser.get(company_phone_page)
            phone = ''
            address = ''
            mobilePhone = ''
            try:
                if 'Your Alibaba.com account is temporarily unavailable' in self.browser.page_source:
                    self.browser.close()
                self.browser.find_element_by_xpath('//div[@class="sens-mask"]/a').click()
                phone = ''.join(re.findall('Telephone:</th><td>(.*?)</td>', self.browser.page_source, re.S))
                mobilePhone = ''.join(re.findall('Mobile Phone:</th><td>(.*?)</td>', self.browser.page_source, re.S))
                address = ''.join(re.findall('Address:</th><td>(.*?)</td>', self.browser.page_source, re.S))
            except:
                print("该公司没有电话")
            all_down = [wd, company_name, company_phone_page, product, counctry, phone, mobilePhone, address,
                        total_evenue, sell_adress, product_img]
            save_csv(all_down)
            print(company_name, company_phone_page, product, counctry, phone, mobilePhone, address, total_evenue,
                  sell_adress, product_img)


def save_csv(lise_line):
    file = csv.writer(open("./alibaba_com_img.csv", 'a', newline="", encoding="utf-8"))
    file.writerow(lise_line)

def main():
    """
    遍历每一页
    """
    run = Chrome_drive()
    run.get_login() #先登录
    wd ='henan'
    for i in range(1,32):
        run.index_page(i, wd)

if __name__ == '__main__':
    csv_title = 'wd,company_name,company_phone_page,product,counctry,phone,mobilePhone,address,total_evenue,sell_adress,product_img'.split(
        ',')
    save_csv(csv_title)
    main()