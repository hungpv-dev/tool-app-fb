import subprocess

def build_app():
    # Định nghĩa các tham số cần thiết
    script_name = "index.py"  # Tên file Python của bạn
    output_name = "asfytech"  # Tên file thực thi bạn muốn tạo
    icon_file = "app_icon.ico"  # Tên file icon của bạn (đảm bảo nó là định dạng .ico)

    # Tạo lệnh PyInstaller
    command = [
        "pyinstaller",
        "--clean",  # Tạo tệp thực thi duy nhất
        "--onefile",  # Tạo tệp thực thi duy nhất
        f"--name={output_name}",  # Đặt tên ứng dụng
        f"--icon={icon_file}",  # Đặt icon
        "--windowed",  # Không hiển thị terminal (dành cho GUI ứng dụng)
        script_name  # Tên file Python của bạn
    ]

    # Chạy lệnh PyInstaller
    try:
        subprocess.run(command, check=True)
        print(f"Ứng dụng đã được xây dựng thành công với tên {output_name}.")
    except subprocess.CalledProcessError as e:
        print(f"Lỗi khi xây dựng ứng dụng: {e}")

# Gọi hàm build_app()
if __name__ == "__main__":
    build_app()
