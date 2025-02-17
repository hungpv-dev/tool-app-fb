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


# from sql.accounts import Account

# acc = Account().find(126)
# print(acc)

href = "https://l.facebook.com/l.php?u=https%3A%2F%2Fautulu.com%2Fviet%2Fpatrick-mahomes-broke-down-in-tears-after-a-9-year-old-girl-gave-him-a-secret-letter-during-the-game%2F%3Ffbclid%3DIwZXh0bgNhZW0CMTAAAR0mcXnNaa6Z79ICfiPjt8HuLNxRr9HehcfHDdGsU0yr4UuPO23OoUKGql8_aem_4s3BiKS-3VCdS3yV-UrJXA&h=AT1KmgpCdzFESSG7y_ak7mInsWb_Fx4fnw_gCZYsGiuIBFVplBKgmoLGRyh_eFaO9AqTz_a828tXl0VYfbxOS1TespCJWnUOi788HX-wg28kDG7DrGy6xcnq77liXRzypY5fgkqe0hhx9us6&__tn__=R]-R&c[0]=AT2SmTQ2JNDWBBP4XhyfC6hrBYaYbd6hh6AHUX1LZOkwFgyBpexrr4JArDeOATVKJitTAlZdPHoFtqGSCd4OfSlsMLj8AMPm96Qmg2SfOqJHZxc27i3cbmzzyGwJyEMyy61cEPY01mhKf5LPm4YzSWXLV-B_h-ZkebM7lo7OX1S_mQNqeMX6PJOi4cb8q-Y3Jre9Sw"
from helpers.fb import clean_url_keep_params,clean_facebook_url_redirect,convert_shorthand_to_number
print(clean_facebook_url_redirect(href))