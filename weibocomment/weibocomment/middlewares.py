# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import re
import time
import traceback

from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from weibo import APIClient


class WeibocommentDownloaderMiddleware(object):

    def __init__(self, settings, timeout=None):
        self.timeout = timeout
        self.settings = settings
        self.browser = webdriver.Chrome()
        self.wait = WebDriverWait(self.browser, self.timeout)
        login(self)

    @classmethod
    def from_crawler(cls, crawler):

        return cls(settings=crawler.settings, timeout=crawler.settings.get(
            'TIME_OUT'))

    def process_request(self, request, spider):

        page = request.meta.get('page')  # 用来判断还有多少页
        # search_url = request.url+'&page='+page
        # cookies = self.browser.get_cookies()

        try:
            self.browser.get(request.url)

            if page > 1:
                submit = self.wait.until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, '.next')))
                submit.click()

            ye = self.wait.until(EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, '.pagenum'), '第' + str(page) + '页'))
            print('第' + str(page) + '页' * 20 + str(ye))

            return HtmlResponse(url=request.url,
                                body=self.browser.page_source,
                                request=request, encoding='utf-8',
                                status=200)

        except Exception as e:
            print(traceback.print_exc())
            print('发生错误' * 10 + str(e))
            return HtmlResponse(url=request.url,
                                request=request, status=500)


def login(self):
    # 1.配置
    # 回调授权页面，用户完成授权后返回的页面
    APP_KEY = self.settings.get('APP_KEY')
    APP_SECRET = self.settings.get('APP_SECRET')
    CALLBACK_URL = self.settings.get('CALLBACK_URL')
    # 2.调用APIClient生成client实例
    client = APIClient(app_key=APP_KEY,
                       app_secret=APP_SECRET,
                       redirect_uri=CALLBACK_URL)
    # 3.得到授权页面的url
    url = client.get_authorize_url()

    # options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    # 调试浏览器,这里老是报错，尚未解决
    # options.add_argument('--remote-debugging-port=9222')
    # self.browser = webdriver.Chrome(options=options)

    self.browser.get(url)

    # time.sleep() 隐式等待一定要停一会，这里改成了显示的，暂时不需要。

    username = self.wait.until(
        EC.presence_of_element_located((By.ID, "userId")))
    username.send_keys('761472239@qq.com')
    password = self.wait.until(
        EC.presence_of_element_located((By.ID, "passwd")))
    password.send_keys('q3swj4..')
    time.sleep(2)
    # 最后登录
    self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                    ".WB_btn_login"))).click()

    # self.browser.find_element_by_id('userId').send_keys(
    #     '761472239@qq.com')
    # time.sleep(random.random())
    # self.browser.find_element_by_id('passwd').send_keys('q3swj4..')
    # time.sleep(1)
    # self.browser.find_element_by_css_selector('.WB_btn_login').click()

    # 授权验证
    time.sleep(2)
    # self.browser.find_element_by_class_name('.WB_btn_oauth').click()
    # if re.match('(.*?)?code', self.browser.current_url) == \
    #         'https://api.weibo.com/oauth2/default.html':
    #     self.browser.find_element_by_class_name('WB_btn_oauth').click()

    print(self.browser.current_url)
    code_url = self.browser.current_url
    code = re.search('code=(.*)', code_url).group(1)
    print('*' * 20 + code + '*' * 20)

    # 4.点击访问url，在浏览器端获得code
    # req = client.request_access_token(code)
    # client.set_access_token(req.get('access_token'), req.get('expires_in'))
    client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET,
                       redirect_uri=CALLBACK_URL)
    r = client.request_access_token(code)
    access_token = r.access_token
    expires_in = r.expires_in
    client.set_access_token(access_token, expires_in)
    self.browser.execute_script('window.open()')
    self.browser.switch_to_window(self.browser.window_handles[1])
