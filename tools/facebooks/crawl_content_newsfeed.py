
from selenium.webdriver.common.by import By
from sql.pages import Page
from sql.errors import Error
from tools.types import push
from multiprocessing import Process
from sql.account_cookies import AccountCookies
from sql.accounts import Account
from threading import Thread, Event
from tools.facebooks.handle_craw_newsfeed import handleCrawlNewFeed,crawlNewFeed,handleCrawlNewFeedVie
from helpers.login import HandleLogin
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import logging
import uuid
from sql.system import System
from helpers.modal import openProfile,remove_notifications,clickOk
system_instance = System()
from bot import send
from helpers.system import create_notification
from main.newsfeed import get_newsfeed_process_instance
from helpers.global_value import get_global_theard_event
global_theard_event = get_global_theard_event()
newsfeed_process_instance = get_newsfeed_process_instance()

class CrawContentNewsfeed:
    def __init__(self, browser, account, dirextension, manager,system_account = None):
        self.browser = browser
        self.account = account
        self.dirextension = dirextension
        self.manager = manager
        self.system_account = system_account
        self.page_instance = Page()
        self.error_instance = Error()
        self.account_cookies = AccountCookies()
        self.account_instance = Account()

    def handle(self,stop_event):
        loginInstance = HandleLogin(self.browser,self.account,newsfeed_process_instance)
        sendNoti = 500
        newsfeed_process_instance.update_process(self.account.get('id'),'Bắt đầu đăng nhập')
        while not stop_event.is_set() and not global_theard_event.is_set():
            if self.account is None:
                break
            try:
                # log_newsfeed(self.account,f'* Bắt đầu ({self.account["name"]}) *')
                logging.info(f'==================Newsfeed ({self.account["name"]})================')
                print(f'==================Newsfeed ({self.account["name"]})================')
                checkLogin = loginInstance.loginFacebook(sendNoti)
                if checkLogin == False:
                    raise ValueError('Không thể login')
                sendNoti = 500
                account = loginInstance.getAccount()
                send(f"{self.account.get('name')}: đăng nhập thành công!")
                newsfeed_process_instance.update_process(self.account.get('id'),'Đăng nhập thành công')
                self.account = account
                loginInstance.updateStatusAcount(self.account['id'],3) # Đang lấy
                self.crawlNewFeed(account,stop_event) 
            except ValueError as e:
                logging.error(f"Lỗi khi xử lý lấy dữ liệu!: {e}")
                print(f"Lỗi khi xử lý lấy dữ liệu!: {e}")
                newsfeed_process_instance.update_process(self.account.get('id'),'Login thất bài, thử lại sau 1p...')
                # if self.system_account:
                #     system_instance.push_message(self.system_account.get('id'),'Đăng nhập thất bại!')
                self.error_instance.insertContent(e)
                if sendNoti >= 500:
                    if self.account.get("name"):
                        send(f"Tài khoản {self.account.get('name')} không thể đăng nhập!")
                        create_notification(f"Tài khoản {self.account.get('name')} không thể đăng nhập!")
                        sendNoti = 0

                if self.browser is None or not self.browser.service.is_connectable():
                    raise e
            except Exception as e:
                print(f'Lỗi: {e}')
                raise e
            finally:
                sendNoti += 60
                logging.error("Thử lại sau 1 phút...")
                print("Thử lại sau 1 phút...")
                sleep(60)

    def crawlNewFeed(self,account,stop_event):
        # log_newsfeed(account,f"**********************************")
        checker = PageChecker(self.browser, self.dirextension,self.manager,self.system_account)
        checker.run(account,stop_event)
        

def process_fanpage(account, name, dirextension, stop_event, managerDriver,system_account):
    logging.info(f"Đang xử lý fanpage: {name}")
    print(f"Đang xử lý fanpage: {name}")
    threads = [
        Thread(target=handleCrawlNewFeed, args=(account, name, dirextension, stop_event,system_account)),
        Thread(target=crawlNewFeed, args=(account, name, dirextension, stop_event,system_account)),
        Thread(target=crawlNewFeed, args=(account, name, dirextension, stop_event,system_account)),
    ]

    # Khởi chạy các thread
    for thread in threads:
        newsfeed_process_instance.update_task(account.get('id'),thread)
        thread.start()
        sleep(3)

    # Đợi tất cả các thread hoàn thành
    for thread in threads:
        thread.join()
    
    account_instance = Account()
    try:
        acc = account_instance.find(account.get('id'))
        if acc.get('status_login') == 3:
            account_instance.update_account(account.get('id'),{'status_login': 2})
    except Exception as e:
        print(e)

    sleep(5)
    newsfeed_process_instance.update_process(account.get('id'), f'Chương trình đã bị dừng...')
    logging.info(f"Hoàn thành xử lý fanpage: {name}")
    print(f"Hoàn thành xử lý fanpage: {name}")

class PageChecker:
    def __init__(self, browser, dirextension,manager,system_account):
        self.browser = browser
        self.system_account = system_account
        self.manager = manager
        self.error_instance = Error()
        self.dirextension = dirextension

    def run(self, account,stop_event):
        threads = []
        try:
            logging.info(f"Đang ở trang chủ!")
            print(f"Đang ở trang chủ!")
            # Tìm tất cả các page
            allPages = openProfile(self.browser)
            newsfeed_process_instance.update_process(account.get('id'),f'Lấy được: {len(allPages)} page')
            logging.info(f'Số fanpage để lướt: {len(allPages)}')
            print(f'Số fanpage để lướt: {len(allPages)}')
            newsfeed_process_instance.update_process(account.get('id'),f'Lấy được: {len(allPages)} page')

            managerDriver = {
                'manager': self.manager,
                'browser': self.browser,
            }

            if allPages: 
                for idx, page in enumerate(allPages):
                    if stop_event.is_set():
                        break
                    name = remove_notifications(page.text).strip()
                    logging.info(f'=================={name}================')
                    print(f'=================={name}================')
                    # Khởi tạo các process
                    thread = Thread(target=process_fanpage, args=(account, name, self.dirextension, stop_event, managerDriver, self.system_account))
                    threads.append(thread)
                    thread.start()
                    sleep(2)

                newsfeed_process_instance.update_process(account.get('id'), f'Xử lý: {len(allPages)} page')
                theardAccount = Thread(target=handleCrawlNewFeedVie, args=(account, managerDriver, self.dirextension, stop_event,self.system_account))
                theardAccount.start()
                threads.append(theardAccount)

                # if account.get("name"):
                #     send(f'{account.get("name")} cào newsfeed: {", ".join(names)}')
                for thread in threads:
                    thread.join()
            else: 
                newsfeed_process_instance.update_process(account.get('id'), f'Không sở hữu fanpage nào!')
        except Exception as e:
            raise e