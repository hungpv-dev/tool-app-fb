import uuid
from tools.driver import Browser
from time import sleep
from helpers.login import HandleLogin
from tools.types import push as pushType
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from sql.pagePosts import PagePosts
from sql.errors import Error
from helpers.modal import clickOk
from sql.account_cookies import AccountCookies
import logging
from bot import send
from helpers.global_value import get_global_theard_event
global_theard_event = get_global_theard_event()

from main.post import get_post_process_instance
post_process_instance = get_post_process_instance()

from sql.system import System
system_instance = System()

def updateSystemMessage(system,message):
    if system:
        system_instance.push_message(system.get('id'),message)

def push_page(page,account,dirextension,stop_event,system_account = None):
    from tools.facebooks.browser_post import Push
    error_instance = Error()
    name = page.get('name')
    page_post_instance = PagePosts()
    account_instance = AccountCookies()


    while not stop_event.is_set() and not global_theard_event.is_set():
        manager = None
        browser = None
        loginInstance = None
        try:
            while not stop_event.is_set() and not global_theard_event.is_set():
                try:
                    manager = Browser(f"/push/{account['id']}/{str(uuid.uuid4())}",dirextension,'chrome',False,loadContent=True)
                    browser = manager.start()
                    sleep(5)
                    break
                except Exception as e:
                    error_instance.insertContent(e)
                    logging.error('Không tạo được trình duyệt')
                    print('Không tạo được trình duyệt')
                    sleep(30)

            loginInstance = HandleLogin(browser,account)
            browser.get('https://facebook.com')
            loginInstance.login(False)

            sleep(2)
            push_instance = Push(browser,account,dirextension,manager)
            sleep(3)

            logging.error(f'Bắt đầu theo dõi page: {name}')
            print(f'Bắt đầu theo dõi page: {name}')
            updateSystemMessage(system_account,f'Bắt đầu đăng page: {name}')
            retry_count = {}
            while not stop_event.is_set() and not global_theard_event.is_set():
                if browser is None or not browser.service.is_connectable():
                    if browser:
                        browser.quit()
                    if manager:
                        manager.cleanup()
                    print("Trình duyệt đã bị đóng. Khởi chạy lại...")
                    manager = Browser(f"/push/{account['id']}/{str(uuid.uuid4())}", dirextension, loadContent=True)
                    browser = manager.start()
                    browser.get('https://facebook.com')
                    try:
                        loginInstance.setAccount()
                        loginInstance.login()
                    except Exception as e:
                        print('Looxi: {e}')

                cookie = account.get('latest_cookie')
                pageUP = page_post_instance.get_page_up({'page_id': page["id"],'account_id':account['id']})
                
                try:
                    profile_button = browser.find_element(By.XPATH, pushType['openProfile'])
                except NoSuchElementException as e:
                    try:
                        loginInstance.setAccount()
                        loginInstance.login()
                    except Exception as e:
                        print('Looxi: {e}')
                    print(f'{account.get("name")} login thất bại đợi 1p')
                    logging.error(f'{account.get("name")} login thất bại đợi 1p')
                    sleep(60)
                    continue
            
                if pageUP:
                    pot_id = pageUP.get('id')
                    if pot_id not in retry_count:
                        retry_count[pot_id] = 0
                    while retry_count[pot_id] < 3:
                        try:
                            post_process_instance.update_process(account.get('id'),f"Xử lý đăng bài: {pageUP['id']}")
                            res = account_instance.updateCount(cookie.get('id'),'counts')
                            name = push_instance.switchPage(page,stop_event)
                            profile_button = browser.find_element(By.XPATH, pushType['openProfile'])
                            push_instance.push(page,pageUP,name)
                            page_post_instance.update_status(pageUP['id'],{
                                'status':2,
                                'cookie_id': cookie['id']
                            })
                            awaitSleep = int(pageUP.get('await', 0)) * 60
                            logging.error(f'=====>{name}: cần đợi {pageUP.get("await", 0)}p để đăng bài tiếp theo!')
                            print(f'=====>{name}: cần đợi {pageUP.get("await", 0)}p để đăng bài tiếp theo!')
                            post_process_instance.update_process(account.get('id'),f"Đăng thành công bài {pageUP['id']}")
                            retry_count.pop(pot_id, None)
                            sleep(awaitSleep)
                            break
                        except NoSuchElementException as e:
                            page_post_instance.update_status(pageUP['id'], {'status': 1})
                            break
                        except Exception as e:
                            retry_count[pot_id] += 1
                            logging.error(e)
                            print(e)
                            error_instance.insertContent(e)
                            if retry_count[pot_id] >= 3:
                                page_post_instance.update_status(pageUP['id'],{
                                    'status': 4,
                                    'cookie_id': cookie['id']
                                })
                                logging.error(f"Bài viết {pot_id} đăng lỗi quá 3 lần. Bỏ qua.")
                                send(f'{account.get("name")} không đăng được bài viết')
                                break
                            sleep(5)
                else: 
                    logging.error('Chưa có bài viết nào trong hàng chờ, chờ 1p để tiếp tục....')
                    print('Chưa có bài viết nào trong hàng chờ, chờ 1p để tiếp tục....')
                    sleep(60)
        except Exception as e:
            error_instance.insertContent(e)
            logging.error(f'Lỗi khi theo dõi page: {e}')
            print(f'Lỗi khi theo dõi page: {e}')
        finally:
            logging.error('Lỗi khi đăng bài page,thử lại sau 30s')
            print('Lỗi khi đăng bài page,thử lại sau 30s')
            sleep(30)
            if browser:
                browser.quit()
                manager.cleanup()
            browser = None
            manager = None
    print('Dừng xử lý đăng bài page')
    


def browseTime(account):
    pagePosts_instance = PagePosts()
    listPosts = pagePosts_instance.get_post_time({'account_id': account['id']})
    return listPosts

def push_list(account, managerDriver, dirextension,stop_event,system_account = None):
    page_post_instance = PagePosts()
    error_instance = Error()
    from tools.facebooks.browser_post import Push
    init = True
    manager = managerDriver.get('manager')
    browser = managerDriver.get('browser')
    sendNoti = True
    while not stop_event.is_set() and not global_theard_event.is_set():
        retry_count = {}
        if not init:
            if browser:
                browser.quit()
            if manager:
                manager.cleanup()
            manager = Browser(f"/push/{account['id']}/{str(uuid.uuid4())}",dirextension,loadContent=True)
            browser = manager.start()
            loginInstance = HandleLogin(browser,account)
            loginInstance.setAccount()
            try:
                loginInstance.login()
            except Exception as e:
                print('Looxi: {e}')
        else:
            init = False

        try:
            sleep(3)
            push = Push(browser,account,dirextension,manager)
            loginInstance = HandleLogin(browser,account) 
            while not stop_event.is_set() and not global_theard_event.is_set():
                if browser is None or not browser.service.is_connectable():
                    if browser:
                        browser.quit()
                    if manager:
                        manager.cleanup()

                    print("Trình duyệt đã bị đóng. Khởi chạy lại...")
                    manager = Browser(f"/push/{account['id']}/{str(uuid.uuid4())}", dirextension, loadContent=True)
                    browser = manager.start()
                    browser.get('https://facebook.com')
                    loginInstance.setAccount()
                    try:
                        loginInstance.login()
                    except Exception as e:
                        print('Looxi: {e}')
                    
                try:
                    clickOk(browser)
                    profile_button = browser.find_element(By.XPATH, pushType['openProfile'])
                    loginInstance.updateStatusAcount(account.get('id'),4)
                except NoSuchElementException as e:
                    print(f'{account.get("name")} login thất bại, đợi 1p...')
                    logging.error(f'{account.get("name")} login thất bại, đợi 1p...')
                    loginInstance = HandleLogin(browser,account) 
                    while not stop_event.is_set() and not global_theard_event.is_set():
                        checkLogin = loginInstance.loginFacebook(sendNoti)
                        if checkLogin == False:
                            updateSystemMessage(system_account,'Login thất bại')
                            print('Đợi 1p rồi thử login lại!')
                            sleep(60)
                        else:
                            send(f"Tài khoản {account.get('name')} bắt đầu cào newsfeed!")
                            break
                    if sendNoti:
                        send(f"Tài khoản {account.get('name')} không thể đăng nhập!")
                        sendNoti = False
                    sleep(2)
                
                sendNoti = True
                
                # browser.get('https://facebook.com')
                posts = browseTime(account)
                logging.error(f"{account.get('name')} => đăng: {len(posts)} bài viết")
                print(f"{account.get('name')} => đăng: {len(posts)} bài viết")
                if len(posts) > 0:
                    for post in posts:
                        post_id = post['id']
                        # Khởi tạo bộ đếm retry nếu chưa có
                        if post_id not in retry_count:
                            retry_count[post_id] = 0

                        while retry_count[post_id] < 3:
                            try:
                                post_process_instance.update_process(account.get('id'),f"Xử lý đăng bài: {post['id']}")
                                page = post.get('page')
                                name = push.switchPage(page,stop_event)
                                updateSystemMessage(system_account,f'Bắt đầu đăng page: {name}')
                                profile_button = browser.find_element(By.XPATH, pushType['openProfile'])
                                push.push(page,post,name)
                                page_post_instance.update_status(post['id'],{
                                    'status': 2,
                                    'cookie_id': account['latest_cookie']['id']
                                })
                                post_process_instance.update_process(account.get('id'),f"Đăng thành công bài: {post['id']}")
                                sleep(2)
                                retry_count.pop(post_id, None)
                                sleep(300)
                                break
                            except NoSuchElementException as e:
                                page_post_instance.update_status(post['id'], {'status': 1})
                                break
                            except Exception as e:
                                retry_count[post_id] += 1
                                logging.error(e)
                                print(e)
                                error_instance.insertContent(e)
                                if retry_count[post_id] >= 3:
                                    page_post_instance.update_status(post['id'],{
                                        'status': 4,
                                        'cookie_id': account['latest_cookie']['id']
                                    })
                                    send(f'{account.get("name")} không đăng được bài viết')
                                    logging.error(f"Bài viết {post_id} đăng lỗi quá 3 lần. Bỏ qua.")
                                    break
                                logging.error(f"Lỗi đăng bài {post_id}. Thử lại sau 30s (lần thứ {retry_count[post_id]}).")
                                sleep(30)
                else:
                    logging.error('Không có bài nào cần đăng trong thời gian này, đợi 30s...')
                    print('Không có bài nào cần đăng trong thời gian này, đợi 30s...')
                    sleep(30)
        except Exception as e:
            error_instance.insertContent(e)
            logging.error(f'Lỗi khi xử lý đăng bài: {e}')
            print(f'Lỗi khi xử lý đăng bài: {e}')
        finally: 
            if browser:
                browser.quit()
                manager.cleanup()
            browser = None
            manager = None
            logging.error('Lỗi khi đăng bài time,thử lại sau 30s')
            print('Lỗi khi đăng bài time,thử lại sau 30s')
            sleep(30)
        
    print('Dừng xử lý đăng bài list')
    