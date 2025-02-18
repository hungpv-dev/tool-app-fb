from sql.newsfeed import NewFeedModel
from sql.errors import Error
from sql.account_cookies import AccountCookies
import uuid
from tools.driver import Browser
import json
import unicodedata
from time import sleep
from helpers.login import HandleLogin
from urllib.parse import urlparse, parse_qs
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from helpers.fb import clean_url_keep_params
from tools.types import push,types
from helpers.modal import clickOk
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from helpers.time import convert_to_db_format
from bot import send
import logging
from helpers.modal import closeModal,openProfile
from selenium.common.exceptions import NoSuchElementException
from helpers.global_value import get_global_theard_event
global_theard_event = get_global_theard_event()

from main.newsfeed import get_newsfeed_process_instance

newsfeed_process_instance = get_newsfeed_process_instance()

from sql.system import System
system_instance = System()

def updateSystemMessage(system,message):
    if system:
        system_instance.push_message(system.get('id'),message)

def handleCrawlNewFeedVie(account, managerDriver ,dirextension = None, stop_event=None,system_account=None):
    process = newsfeed_process_instance.show(account.get('id'))
    newfeed_instance = NewFeedModel()
    error_instance = Error()
    account_cookie_instance = AccountCookies()
    manager = managerDriver.get('manager')
    browser = managerDriver.get('browser')
    init = True
    sendNoti = 500
    pageLinkPost = f"/posts/"
    pageLinkStory = "https://www.facebook.com/permalink.php"
    # newfeed_instance.setProxy(account.get('proxy'))
    loginInstance = HandleLogin(browser,account,newsfeed_process_instance)
    sendNotiInfo = False
    while not stop_event.is_set() and not global_theard_event.is_set():
        if account is None:
            break
        try:
            if not init:
                manager = Browser(f"/newsfeed/{str(account.get('id'))}/{str(uuid.uuid4())}",dirextension)
                browser = manager.start()
                loginInstance = HandleLogin(browser,account,newsfeed_process_instance)
                loginInstance.setAccount()
                try:
                    loginInstance.login()
                except Exception as e:
                    print('Looxi: {e}')
            else:
                init = False
                
            while not stop_event.is_set() and not global_theard_event.is_set():
                if account is None:
                    break
                if browser is None or not browser.service.is_connectable():
                    manager = Browser(f"/newsfeed/home/{account['id']}", dirextension)
                    browser = manager.start()
                    try:
                        loginInstance = HandleLogin(browser,account,newsfeed_process_instance)
                        loginInstance.login()
                    except Exception as e:
                        print('Looxi: {e}')

                try:
                    clickOk(browser)
                    profile_button = browser.find_element(By.XPATH, push['openProfile'])
                    loginInstance.updateStatusAcount(account.get('id'),3)
                except NoSuchElementException as e:
                    sendNotiInfo = True
                    newsfeed_process_instance.update_process(account.get('id'),'Đăng nhập thất bại, chờ 1p...')
                    print(f'{account.get("name")} login thất bại, đợi 1p...')
                    logging.error(f'{account.get("name")} login thất bại, đợi 1p...')
                    if sendNoti >= 500:
                        if account.get("name"):
                            send(f"Tài khoản {account.get('name')} không thể đăng nhập!")
                        sendNoti = 0
                    sleep(60)
                    sendNoti += 60
                    try:
                        loginInstance.setAccount()
                        loginInstance.login()
                    except Exception as e:
                        print('Looxi: {e}')
                    continue
                
                if sendNotiInfo:
                    send(f"Tài khoản {account.get('name')} đăng nhập thành công!")
                    sendNotiInfo = False
                sendNoti = 500
                newsfeed_process_instance.update_process(account.get('id'),'Đăng nhập thành công')

                browser.get('https://facebook.com/home.php')
                if process['status_vie'] == 1:
                    sleep(60)
                    process = newsfeed_process_instance.show(account.get('id'))
                    continue

                clickOk(browser)
                sleep(1)
                closeModal(1,browser)
                sleep(1)
                
                browser.execute_script("document.body.style.zoom='0.2';")
                sleep(3)
                listId = set() 
                # log_newsfeed(account,f"====================Thực thi cào fanpage {name}=====================")
                while not stop_event.is_set() and not global_theard_event.is_set() and process['status_vie'] == 2: 
                    if account is None:
                        break
                    # updateSystemMessage(system_account,'Bắt đầu cào vie')
                    try:
                        clickOk(browser)
                        profile_button = browser.find_element(By.XPATH, push['openProfile'])
                        loginInstance.updateStatusAcount(account.get('id'),3)
                    except NoSuchElementException as e:
                        sendNotiInfo = True
                        newsfeed_process_instance.update_process(account.get('id'),'Không thể đăng nhập')
                        if sendNoti >= 500:
                            if account.get("name"):
                                send(f"Tài khoản {account.get('name')} không thể đăng nhập!")
                            sendNoti = 0

                        while not stop_event.is_set() and not global_theard_event.is_set():
                            if account is None:
                                break
                            checkLogin = loginInstance.loginFacebook(sendNoti)
                            if checkLogin == False:
                                # updateSystemMessage(system_account,'Login thất bại')
                                sendNoti += 60
                                newsfeed_process_instance.update_process(account.get('id'),'Đăng nhập thất bại, chờ 1p...')
                                print('Đợi 1p rồi thử login lại!')
                                sleep(60)
                            else:
                                # if account.get("name"):
                                #     send(f"Tài khoản {account.get('name')} bắt đầu cào newsfeed!")
                                break
                        sleep(2)
                    except Exception as e:
                        raise e
                        
                    sendNoti = 500
                    newsfeed_process_instance.update_process(account.get('id'),'Đăng nhập thành công')
                    if sendNotiInfo:
                        send(f"Tài khoản {account.get('name')} đăng nhập thành công!")
                        sendNotiInfo = False
                    actions = ActionChains(browser)
                    
                    listPosts = browser.find_elements(By.XPATH, types['list_posts']) 
                    
                    for p in listPosts:
                        try:
                            idAreaPost = p.get_attribute('aria-posinset')
                            if idAreaPost not in listId:
                                listId.add(idAreaPost)
                                links = p.find_elements(By.XPATH, ".//a")
                                for link in links:
                                    if link.is_displayed() and link.size['width'] > 0 and link.size['height'] > 0:
                                        actions.move_to_element(link).perform()
                                        href = link.get_attribute('href')
                                        href = clean_url_keep_params(href)
                                        time = link.text.strip()
                                        converTime = convert_to_db_format(time)
                                        post_id = ''
                                        if any(substring in href for substring in [pageLinkPost, pageLinkStory]) or converTime:
                                            if pageLinkPost in href:
                                                post_id = href.replace(pageLinkPost, '').split('?')[0]
                                                post_id = post_id.split('/')[-1]
                                            elif pageLinkStory in href:
                                                parsed_url = urlparse(href)
                                                query_params = parse_qs(parsed_url.query)
                                                post_id = query_params.get('story_fbid', [None])[0]
                                            if post_id == '': continue

                                            account_cookie_instance.updateCount(account['latest_cookie']['id'], 'counts')
                                            data = {
                                                'post_fb_id': post_id,
                                                'post_fb_link': clean_url_keep_params(href),
                                                'status': 1,
                                                'cookie_id': account['latest_cookie']['id'],
                                                'account_id': account.get('id'),
                                            }
                                            res = newfeed_instance.insert(data)
                                            print(f"{account.get('name')}: {data.get('post_fb_link')}")
                                            newsfeed_process_instance.update_process(account.get('id'),'Lưu được 1 đường dẫn bài viết')
                                            # log_newsfeed(account, f"* +1 đường dẫn * {str(res.get('data', {}).get('id', 'Không có id'))}")

                        except Exception as e:
                            print("Phần tử đã không còn tồn tại, tìm lại phần tử.")
                            continue
                
                    if len(listId) >= 20:
                        browser.refresh() 
                        browser.get('https://facebook.com/home.php')
                        sleep(2)  
                        listId.clear() 
                        browser.execute_script("document.body.style.zoom='0.2';")
                        sleep(3)
                        print('Load lại trang!')
                    else:
                        browser.execute_script("window.scrollBy(0, 500);")
                    sleep(5)
                    process = newsfeed_process_instance.show(account.get('id'))
                # updateSystemMessage(system_account,'Tắt cào vie')
                sleep(30)
        except Exception as e:
            browser.quit()
            manager.cleanup()
            print(f'Lỗi cào vie: {e}')
            logging.error(f'Lỗi cào vie: {e}')
            print('Lỗi khi lướt vie')
            sleep(30)
        finally:
            manager = None
            browser = None
            

def handleCrawlNewFeed(account, name, dirextension = None,stop_event=None,system_account=None):
    try:
        newfeed_instance = NewFeedModel()
        error_instance = Error()
        account_cookie_instance = AccountCookies()
        account_id = account.get('id', 'default_id')
        print(f'Chuyển hướng tới fanpage: {name}')

        manager = None
        browser = None
        # newfeed_instance.setProxy(account.get('proxy'))
        sendNotiKey = True
        # sendNoti = True
        while not stop_event.is_set() and not global_theard_event.is_set():
            if account is None:
                break
            try:
                # while not stop_event.is_set() and not global_theard_event.is_set():
                    # try:
                manager = Browser(f"/newsfeed/{str(account_id)}/{str(uuid.uuid4())}",dirextension)
                browser = manager.start()
                sleep(5)
                    #     break
                    # except Exception as e:
                    #     sleep(30)
                
                loginInstance = HandleLogin(browser,account,newsfeed_process_instance)
                try:
                    browser.get('https://facebook.com/home.php')
                    sleep(1)
                    loginInstance.login()
                except Exception as e:
                    pass
                # while not stop_event.is_set() and not global_theard_event.is_set():
                #     checkLogin = loginInstance.loginFacebook(False)
                #     if checkLogin == False:
                #         updateSystemMessage(system_account,'Login thất bại')
                #         print('Đợi 1p rồi thử login lại!')
                #         sleep(60)
                #     else:
                #         account = loginInstance.getAccount()
                #         break
                # sleep(2)
                # loginInstance.updateStatusAcount(account.get('id'),3)
                
                try:
                    openProfile(browser,name)
                    sleep(10)
                except Exception as e:
                    print(f"Không thể chuyển hướng tới fanpage: {name}")
                
                sleep(2)
                closeModal(1,browser)
                pageLinkPost = f"/posts/"
                pageLinkStory = "https://www.facebook.com/permalink.php"
                
                browser.execute_script("document.body.style.zoom='0.2';")
                sleep(3)
                listId = set() 
                while not stop_event.is_set() and not global_theard_event.is_set(): 
                    if account is None:
                        break
                    if browser is None or not browser.service.is_connectable():
                        print("Trình duyệt đã bị đóng. Khởi chạy lại...")
                        manager = Browser(f"/newsfeed/{str(account_id)}/{str(uuid.uuid4())}", dirextension)
                        browser = manager.start()
                        browser.get('https://facebook.com/home.php')
                        try:
                            loginInstance = HandleLogin(browser,account)
                            loginInstance.login()
                        except Exception as e:
                            print('Looxi: {e}')
                    try:
                        clickOk(browser)
                        profile_button = browser.find_element(By.XPATH, push['openProfile'])
                        # loginInstance.updateStatusAcount(account.get('id'),3)
                    except NoSuchElementException as e:
                        logging.info(f"{name} chờ 3 phút để thử login lại")
                        print(f"{name} chờ 3 phút để thử login lại")
                        sleep(180)
                        browser.get('https://facebook.com/home.php')
                        sleep(1)
                        loginInstance = HandleLogin(browser,account)
                        loginInstance.setAccount()
                        try:
                            loginInstance.login()
                        except Exception as e:
                            print('Looxi: {e}')
                        try:
                            clickOk(browser)
                            profile_button = browser.find_element(By.XPATH, push['openProfile'])
                            try:
                                openProfile(browser,name)
                                sleep(10)
                            except Exception as e:
                                print(f"Không thể chuyển hướng tới fanpage: {name}")
                        except NoSuchElementException as e:
                            pass
                        continue
                        # if sendNoti:
                        #     send(f"Tài khoản {account.get('name')} không thể đăng nhập!")
                        #     sendNoti = False

                        # while not stop_event.is_set() and not global_theard_event.is_set():
                        #     checkLogin = loginInstance.loginFacebook(False)
                        #     if checkLogin == False:
                        #         updateSystemMessage(system_account,'Login thất bại')
                        #         print('Đợi 1p rồi thử login lại!')
                        #         sleep(60)
                        #     else:
                        #         send(f"Tài khoản {account.get('name')} ---- cào newsfeed: {name}!")
                        #         break
                        # sleep(2)
                    except Exception as e:
                        raise e
                        
                    # sendNoti = True
                    actions = ActionChains(browser)
                    
                    listPosts = browser.find_elements(By.XPATH, types['list_posts']) 
                    checkReload = True
                    for p in listPosts:
                        try:
                            idAreaPost = p.get_attribute('aria-posinset')
                            if idAreaPost not in listId:
                                checkReload = False
                                listId.add(idAreaPost)
                                links = p.find_elements(By.XPATH, ".//a")
                                for link in links:
                                    if link.is_displayed() and link.size['width'] > 0 and link.size['height'] > 0:
                                        actions.move_to_element(link).perform()
                                        href = link.get_attribute('href')
                                        href = clean_url_keep_params(href)
                                        time = link.text.strip()
                                        converTime = convert_to_db_format(time)
                                        post_id = ''
                                        if any(substring in href for substring in [pageLinkPost, pageLinkStory]) or converTime:
                                            if pageLinkPost in href:
                                                post_id = href.replace(pageLinkPost, '').split('?')[0]
                                                post_id = post_id.split('/')[-1]
                                            elif pageLinkStory in href:
                                                parsed_url = urlparse(href)
                                                query_params = parse_qs(parsed_url.query)
                                                post_id = query_params.get('story_fbid', [None])[0]
                                            if post_id == '': continue

                                            account_cookie_instance.updateCount(account['latest_cookie']['id'], 'counts')

                                            data = {
                                                'post_fb_id': post_id,
                                                'post_fb_link': clean_url_keep_params(href),
                                                'status': 1,
                                                'cookie_id': account['latest_cookie']['id'],
                                                'account_id': account.get('id'),
                                            }
                                            res = newfeed_instance.insert(data)

                                            if 'id' in res:
                                                sendNotiKey = True
                                            else:
                                                if sendNotiKey:
                                                    if account.get("name"):
                                                        send(f"{account.get('name')} không có từ khoá nào!")
                                                    sendNotiKey = False
                                                continue
                                                
                                            newsfeed_process_instance.update_process(account.get('id'),'Lưu được 1 đường dẫn bài viết')
                                            print(f"{name}: {data.get('post_fb_link')}")
                                            # log_newsfeed(account, f"* +1 đường dẫn * {str(res.get('data', {}).get('id', 'Không có id'))}")
                        except Exception as e:
                            print("Phần tử đã không còn tồn tại, tìm lại phần tử.")
                            continue
                
                    if len(listId) >= 20 or checkReload == True:
                        browser.refresh() 
                        browser.get('https://facebook.com/home.php')
                        sleep(2)  
                        listId.clear() 
                        browser.execute_script("document.body.style.zoom='0.2';")
                        sleep(3)
                        print('Load lại trang!')
                    else:
                        browser.execute_script("window.scrollBy(0, 500);")
                    sleep(5)
            except Exception as e:
                print(f"{name} link: {e}")
                logging.error(f"{name} link: {e}")
                sleep(30)
            finally:
                if browser:  # Kiểm tra lại trước khi gọi quit()
                    browser.quit()
                    browser = None
                if manager:
                    manager.cleanup()
                    manager = None
    except Exception as e:
        error_instance.insertContent(e)
    finally:
        print(f"==========================Đóng fanpage {name}=================================")
        logging.info(f"==========================Đóng fanpage {name}=================================")

def crawlNewFeed(account,name,dirextension,stop_event=None,system_account=None):
    try:
        account_id = account.get('id', 'default_id')
        account_cookie_instance = AccountCookies()
        from tools.facebooks.crawl_content_post import CrawlContentPost
        newfeed_instance = NewFeedModel()
        # newfeed_instance.setProxy(account.get('proxy'))
        error_instance = Error()
        print(f'Chuyển hướng tới fanpage: {name}')
        manager = None
        browser = None
        while not stop_event.is_set() and not global_theard_event.is_set():
            if account is None:
                break
            try:
                manager = Browser(f"/newsfeed/{str(account_id)}/{str(uuid.uuid4())}",dirextension)
                browser = manager.start()
                sleep(5)
                
                loginInstance = HandleLogin(browser,account,newsfeed_process_instance)
                try:
                    browser.get('https://facebook.com/home.php')
                    sleep(1)
                    loginInstance.login()
                except Exception as e:
                    pass
                # while not stop_event.is_set() and not global_theard_event.is_set():
                #     checkLogin = loginInstance.loginFacebook(False)
                #     if checkLogin == False:
                #         updateSystemMessage(system_account,'Login thất bại')
                #         print('Đợi 1p rồi thử login lại!')
                #         sleep(60)
                #     else:
                #         account = loginInstance.getAccount()
                #         break

                # loginInstance.updateStatusAcount(account.get('id'),3)
                # sleep(2)
                try:
                    openProfile(browser,name)
                    sleep(10)
                except Exception as e:
                    print(f"Không thể chuyển hướng tới fanpage: {name}")

                crawl_instance = CrawlContentPost(browser)
                # log_newsfeed(account,f"==> Lưu bài viết <==")

                while not stop_event.is_set() and not global_theard_event.is_set():
                    if account is None:
                        break
                    if browser is None or not browser.service.is_connectable():
                        print("Trình duyệt đã bị đóng. Khởi chạy lại...")
                        manager = Browser(f"/newsfeed/{str(account_id)}/{str(uuid.uuid4())}", dirextension)
                        browser = manager.start()
                        browser.get('https://facebook.com/home.php')
                        try:
                            loginInstance = HandleLogin(browser,account)
                            loginInstance.login()
                        except Exception as e:
                            print('Looxi: {e}')
                    try:
                        clickOk(browser)
                        profile_button = browser.find_element(By.XPATH, push['openProfile'])
                    except NoSuchElementException as e:
                        logging.info(f"{name} chờ 3 phút để thử login lại")
                        print(f"{name} chờ 3 phút để thử login lại")
                        sleep(180)
                        browser.get('https://facebook.com/home.php')
                        sleep(1)
                        loginInstance = HandleLogin(browser,account)
                        loginInstance.setAccount()
                        try:
                            loginInstance.login()
                        except Exception as e:
                            print('Looxi: {e}')
                        try:
                            clickOk(browser)
                            profile_button = browser.find_element(By.XPATH, push['openProfile'])
                            try:
                                openProfile(browser,name)
                                sleep(10)
                            except Exception as e:
                                print(f"Không thể chuyển hướng tới fanpage: {name}")
                        except NoSuchElementException as e:
                            pass
                        continue
                    except Exception as e:
                        raise e

                    try:
                        up = newfeed_instance.first({'account_id': account['id']})
                        # log_newsfeed(account,'=> * sử lí lưu đb *')

                        if up is None:
                            print('Hiện chưa có bài viết nào cần lấy! chờ 1p để tiếp tục...')
                            sleep(60)
                            continue
                        
                        id = up['id']
                        link_up = clean_url_keep_params(up['post_fb_link'])
                        browser.get(link_up)
                        up['newfeed'] = 1
                        up['id'] = up['post_fb_id']
                        up['link'] = link_up
                        try:
                            data = crawl_instance.crawlContentPost({},up,{},newfeed=True)
                        except Exception as e:
                            newfeed_instance.destroy(id)
                            continue

                        check = False
                        post = data.get('post')
                        comments = data.get('comments')
                        try:
                            keywords = up.get('keywords') or []
                            post['keywords'] = keywords
                            
                            post_content_no_accents = remove_accents(post['content'].lower())
                            if any(remove_accents(keyword.lower()) in post_content_no_accents for keyword in keywords):
                                check = True

                            for cm in comments:
                                comment_content_no_accents = remove_accents(cm['content'].lower())
                                if any(remove_accents(keyword.lower()) in comment_content_no_accents for keyword in keywords):
                                    check = True

                            # if keywords is None or len(keywords) == 0:
                            #     if 'media' in post and 'images' in post['media'] and 'videos' in post['media']:
                            #         if len(post['media']['images']) > 0 or len(post['media']['videos']) > 0:
                            #             check = True
                        except Exception as e:
                            print('Lỗi khi check keywords')

                        # print(post.get('content'))
                        if check:
                            print('Đã lấy được 1 bài lưu db')
                            # crawl_instance.shareCopyLink() -> Copy đường dẫn
                            # crawl_instance.sharePostAndOpenNotify() -> Interested, Notifications, Save Post
                            # icon = crawl_instance.likePost() -> Random icon post
                            # post['icon'] = icon
                            closeModal(crawl_instance.index,browser)
                            sleep(1)
                            print(json.dumps({
                                'link': post.get('link_facebook'),
                                'icon': post.get('icon'),
                            },indent=4))
                            newsfeed_process_instance.update_process(account.get('id'),f'Lưu được 1 bài viết: {id}')
                            crawl_instance.viewImages(post)
                            crawl_instance.insertPostAndComment(post,comments,{},id)
                            account_cookie_instance.updateCount(account['latest_cookie']['id'], 'count_get')
                            # browser.get('https://facebook.com')
                        else:
                            newsfeed_process_instance.update_process(account.get('id'),f'{id} bài viết không chứa từ khoá')
                            print('Bài này k thỏa mã yêu cầu!')
                            newfeed_instance.destroy(id)
                        sleep(1)
                    except Exception as e:
                        newfeed_instance.destroy(id)
            except Exception as e:
                error_instance.insertContent(e)
                # log_newsfeed(account,'Lỗi khi cào lưu db, thử lại sau 30s')
                sleep(30)
            finally: 
                if browser:
                    browser.quit()
                    browser = None
                    manager.cleanup()
                    manager = None
    except Exception as e:
        print(f"{name} db: {e}")
        logging.error(f"{name} db: {e}")
        error_instance.insertContent(e)
    finally:
        print(f"========> Đóng cào lưu đb {name} <=============")
        logging.info(f"========> Đóng cào lưu đb {name} <=============")


     
def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])