import requests
from requests.auth import HTTPBasicAuth

# Thông tin WordPress
site_url = "https://wesunn.com"  # Thay bằng URL website của bạn
username = "hung2004"  # Thay bằng tài khoản WordPress của bạn
application_password = "NFj5 pv5y 41n6 22ye Qvmf oSNs"  # Thay bằng mật khẩu ứng dụng đã tạo

# Nội dung bài viết
data = {
    "title": "Bài viết tự động",
    "content": "Đây là nội dung bài viết được đăng tự động lên WordPress bằng Python cyar do_dev. 🚀",
    "status": "publish",  # Hoặc "draft" nếu muốn lưu nháp
}

# Gửi request POST để đăng bài
response = requests.post(
    f"{site_url}/wp-json/wp/v2/posts",
    json=data,
    auth=HTTPBasicAuth(username, application_password),
)

# Kiểm tra phản hồi
if response.status_code == 201:
    print("✅ Đăng bài thành công!")
    print("📌 Link bài viết:", response.json().get("link"))
else:
    print("❌ Lỗi khi đăng bài:", response.text)

