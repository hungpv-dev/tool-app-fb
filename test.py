# from tools.facebooks.browser_post import Push
# from tools.driver import Browser
# from helpers.image import delete_image,download_image
# from helpers.fb import set_html_in_div
# from time import sleep
# from extensions.auth_proxy import create_proxy_extension
# from selenium.webdriver.common.by import By
# import requests
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.keys import Keys
# import os
# from sql.accounts import Account
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from helpers.login import HandleLogin
# account_instance = Account()
# import uuid
# from helpers.modal import closeModal
# import json
# from tools.types import push
# from tools.facebooks.crawl_content_post import CrawlContentPost
# from helpers.modal import openProfile

# class Test:
#     def post(self,id):
#         acc = account_instance.find(id)
#         if not acc: return

#         extension = create_proxy_extension(acc.get('proxy'))
#         manager = Browser(f'/test/{id}',extension,loadContent=True)
#         driver = manager.start(False)

#         loginInstance = HandleLogin(driver,acc)
#         checkLogin = loginInstance.loginFacebook()
#         if checkLogin == False: return
#         push_instance = Push(driver,acc,extension,manager)
#         # openProfile(driver,'Light Of Life')
#         # profile_button = WebDriverWait(driver, 10).until(
#         #     EC.presence_of_element_located((By.XPATH,  push['openProfile']))
#         # )
#         # profile_button.click()
#         # try:
#         #     allFanPage = WebDriverWait(driver, 10).until(
#         #         EC.presence_of_element_located((By.XPATH, push['allProfile']))
#         #     )
#         #     allFanPage.click()
#         # except Exception as e:
#         #     pass

#         # switchPage = WebDriverWait(driver, 10).until(
#         #     EC.presence_of_element_located((By.XPATH, push['switchPage']('Sports Daily')))
#         # )
#         # switchPage.click()
#         # sleep(10000)

#         driver.get('https://www.facebook.com/profile.php')
        
#         # swichNow = driver.find_element(By.XPATH, push['switchNow'])
#         # swichNow.click()

#         text = "What's on your mind?"
#         yourThink = driver.find_element(By.XPATH,f'//*[text()="{text}"]')
#         yourThink.click()
#         sleep(3)
#         input_element = driver.switch_to.active_element
#         form = input_element.find_element(By.XPATH,'./ancestor::form')


#         try:
#             your_text = "Son-in-law I sent him to my room, More details in 𝐜𝐨𝐦𝐦𝐞𝐧𝐭 See less 😉😉😉"
#             for char in your_text:
#                 input_element.send_keys(char)
#         except Exception as e:
#             print(e)







#         sleep(10000)


#         print('Đã dán hình ảnh')
#         images = [
#             'https://scontent-msp1-1.xx.fbcdn.net/v/t39.30808-6/473052870_630803815965318_4867811670978317300_n.jpg?stp=dst-jpg_s640x640_tt6&_nc_cat=101&ccb=1-7&_nc_sid=127cfc&_nc_ohc=4DiKJBKIJh0Q7kNvgERtSyP&_nc_zt=23&_nc_ht=scontent-msp1-1.xx&_nc_gid=A5fMgxIc0VzDgAvZUMKP9SE&oh=00_AYCY01AeglrWOODkf4vWsNO0S5QPsU9NtYz0TrI51jZ-FQ&oe=6785CB8E',
#             'https://scontent-msp1-1.xx.fbcdn.net/v/t39.30808-6/473052870_630803815965318_4867811670978317300_n.jpg?stp=dst-jpg_s640x640_tt6&_nc_cat=101&ccb=1-7&_nc_sid=127cfc&_nc_ohc=4DiKJBKIJh0Q7kNvgERtSyP&_nc_zt=23&_nc_ht=scontent-msp1-1.xx&_nc_gid=A5fMgxIc0VzDgAvZUMKP9SE&oh=00_AYCY01AeglrWOODkf4vWsNO0S5QPsU9NtYz0TrI51jZ-FQ&oe=6785CB8E'
#         ]

#         # Xử lý từng ảnh
#         for i, url in enumerate(images):
#             photo_video_element = form.find_element(By.XPATH, './/div[@aria-label="Photo/video"]')
#             photo_video_element.click()
#             listLinkTemps = []
#             try:
#                 # Bước 1: Tải ảnh về
#                 temp_image_path = download_image(url, temp_file=f"image_{i}_{uuid.uuid4()}.png")
#                 listLinkTemps.append(temp_image_path)
#                 sleep(3)

#                 # Bước 2: Tìm thẻ input và gửi file
#                 file_input = form.find_elements(By.XPATH, './/input[@type="file"]')[-1]
#                 file_input.send_keys(temp_image_path)

#                 sleep(3)  # Chờ ảnh được tải lên hoàn toàn
#             except Exception as e:
#                 print(f"Lỗi khi tải hoặc upload ảnh: {e}")

#         for file in listLinkTemps:
#             # Bước 3: Xóa file tạm sau khi gửi
#             delete_image(temp_image_path)
#         form.submit()
#         print("Đăng bài thành công")
#         driver.quit()
    
#     def crawl(self,id):
#         acc = account_instance.find(id)
#         if not acc: return
#         extension = create_proxy_extension(acc.get('proxy'))
#         manager = Browser(f'/test/{id}',extension,loadContent=True)
#         driver = manager.start(False)
#         sleep(3)
#         loginInstance = HandleLogin(driver,acc)
#         checkLogin = loginInstance.loginFacebook()
#         if checkLogin == False: return
#         crawl_instance = CrawlContentPost(driver)
#         up = {
#             'id': 'pfbid0MGw8R1PD4giDCnDJD5LTeQoDC5XXAHcf4aDxp7NEa6F1s8DE9ErKJVh2w26KWA22l',
#             'link': 'https://www.facebook.com/NBAonESPN/posts/pfbid0MGw8R1PD4giDCnDJD5LTeQoDC5XXAHcf4aDxp7NEa6F1s8DE9ErKJVh2w26KWA22l/',
#         }
#         print('Chuẩn bị')
#         sleep(10)
#         driver.get(up['link'])
#         sleep(1)
#         data = crawl_instance.crawlContentPost({},up,{
#             'newsfeed': 1,
#         },True)
#         sleep(2)
#         # crawl_instance.insertPostAndComment(data.get('post'),data.get('comments'), {})
#         # crawl_instance.shareCopyLink()
#         # crawl_instance.sharePostAndOpenNotify()
#         # icon = crawl_instance.likePost()
#         # data.get('post')['icon'] = icon
#         # closeModal(2,driver)
#         # sleep(1)
#         # crawl_instance.viewImages(data.get('post'))
#         print(json.dumps(data,indent=4))
#         sleep(100000)
#         driver.quit()



# # Đăng bài
# test = Test()
# # test.post(83)
# test.crawl(83)


# from helpers.modal import remove_notifications

# # text = "Pop Prince 200 notifications"
# # print(remove_notifications(text))

# # from helpers.fb import clean_url_keep_params,clean_facebook_url_redirect
# # href = 'https://www.facebook.com/permalink.php?story_fbid=pfbid0syVHGJi1vypbtjmAp5tKs181n5drr32aLP9jPLvzWe94Wn8sFBBTrkTJqBU9oPBJl&amp;id=61572025409861'
# # print(clean_url_keep_params(href))

# from bot import send

# send('Heello')


email = "whitebeargnw808574@hotmail.com"
pwdEmail = "vhE166nqFE"
server = "outlook.office365.com"
import win32com.client
outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
inbox = outlook.GetDefaultFolder(6) 
messages = inbox.Items
message = messages.GetLast()
body_content = message.body
print(body_content)