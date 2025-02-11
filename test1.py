# import requests
# from bs4 import BeautifulSoup

# # Bước 1: Tải HTML từ URL
# def fetch_html(url):
#     response = requests.get(url)
#     response.raise_for_status()
  
#     return response.text

# # Bước 2: Phân tích HTML và tìm thẻ <div> gần nhất chứa thẻ <p>
# def extract_div_with_p_tags(html):
#     soup = BeautifulSoup(html, 'html.parser')
#     div_blocks = []

#     # Lọc tất cả các thẻ <p> và tìm thẻ <div> gần nhất chứa thẻ <p>
#     for p in soup.find_all('p'):
#         div = p.find_parent('div')
#         if div:
#             div_blocks.append(div)
    
#     return div_blocks

# # Bước 3: Tìm thẻ <div> có chứa nhiều thẻ <p> nhất
# def find_div_with_most_p_tags(div_blocks):
#     if not div_blocks:
#         return None, 0  # Nếu không tìm thấy thẻ <div> nào có thẻ <p>
    
#     # Đếm số lượng thẻ <p> trong từng thẻ <div>
#     div_p_counts = [(div, len(div.find_all('p'))) for div in div_blocks]
    
#     # Sắp xếp các thẻ <div> theo số lượng thẻ <p> chứa trong đó
#     main_div, num_p_tags = max(div_p_counts, key=lambda x: x[1])
#     return main_div, num_p_tags

# # Bước 4: Lấy toàn bộ nội dung HTML bên trong thẻ <div> đã tìm được, trừ các thẻ <div> con
# def extract_relevant_tags(main_div):
#     relevant_html = ""
#     if main_div:
#         for tag in main_div.find_all(recursive=False):
#             if tag.name not in ['div', 'script']:
#                 relevant_html += str(tag)
#             elif tag.name == 'div':
#                 for sub_tag in tag.find_all(recursive=False):
#                     if sub_tag.name not in ['div', 'script']:
#                         relevant_html += str(sub_tag)
#     return relevant_html

# # Bước 5: Thực thi
# url = "https://news68.cafex.biz/blog/im-not-really-sure-greg-olsen-gives-damning-summation-of-houston-texans-embarrassing-christmas-day-outing-quynhlong"  # Thay bằng URL của bạn
# html = fetch_html(url)
# div_blocks = extract_div_with_p_tags(html)
# main_div, num_p_tags = find_div_with_most_p_tags(div_blocks)

# relevant_html = extract_relevant_tags(main_div)

# # In ra nội dung HTML bên trong thẻ <div> đã tìm được

import time
import threading

def dem():
    for i in range(10):
        print(i)
        time.sleep(1)


threading.Thread(target=dem).start()
sleep(2)
threading.Thread(target=dem).start()

