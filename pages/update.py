import os
import time
import shutil
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import re
from sql.update import UpdateVersion
from main.root import get_frame
update_version = UpdateVersion()

def update_console(output, text_widget):
    """Hiển thị log tải xuống trên giao diện."""
    text_widget.config(state=tk.NORMAL)
    text_widget.insert(tk.END, output + "\n")
    text_widget.config(state=tk.DISABLED)
    text_widget.see(tk.END)  # Cuộn xuống dòng mới nhất

def download_update(text_widget):
    """Tải file từ Google Drive bằng gdown và cập nhật tiến trình."""
    new_file = "asfytech_new.exe"
    uv = update_version.get_version()
    if uv is None:
        return uv
    
    url = uv.get('name')
    # Trích xuất ID từ URL Google Drive
    match = re.search(r'd/([a-zA-Z0-9_-]+)', url) 
    if match:
        file_id = match.group(1)
        url = f'https://drive.google.com/uc?id={file_id}'

    try:
        # Kiểm tra xem Python có tồn tại không
        if shutil.which("python") is None and shutil.which("python3") is None:
            print("Lỗi: Hệ thống không có Python. Vui lòng cài đặt Python trước khi tiếp tục!")
            raise ValueError('Không tìm thấy Python')

        # Lấy phiên bản Python khả dụng
        python_cmd = shutil.which("python") or shutil.which("python3")
        # Kiểm tra pip
        if shutil.which("pip") is None:
            print("pip chưa được cài đặt, tiến hành cài đặt pip...")
            try:
                subprocess.run([python_cmd, "-m", "ensurepip", "--default-pip"], check=True)
                print("Cài đặt pip thành công.")
            except subprocess.CalledProcessError:
                print("Lỗi: Không thể cài đặt pip. Hãy cài đặt thủ công!")
                raise ValueError('Không thể tải PIP')

        # Kiểm tra gdown
        if shutil.which("gdown") is None:
            print("gdown chưa được cài đặt, tiến hành cài đặt...")
            subprocess.run(["pip", "install", "gdown"], check=True)
            print("Cài đặt gdown hoàn tất.")

        # Chạy gdown bằng subprocess để lấy tiến trình tải
        process = subprocess.Popen(
            ["gdown", url, "-O", new_file, "--fuzzy"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True
        )

        for line in process.stdout:
            output = line.strip()
            text_widget.after(0, update_console, output, text_widget)

        process.wait()

    except Exception as e:
        raise ValueError(f'Lỗi: {e}')
    
    return new_file

import psutil
def is_process_running(process_name):
    """Kiểm tra xem quá trình có đang chạy không."""
    try:
        # Kiểm tra xem tiến trình có đang chạy không bằng cách sử dụng tasklist (Windows)
        result = subprocess.run(['tasklist'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return process_name.lower() in result.stdout.lower()
    except Exception as e:
        print(f"Lỗi kiểm tra tiến trình: {e}")
        return False

def replace_and_restart(new_file):
    """Đóng ứng dụng cũ, thay thế file và khởi động lại."""
    old_file = "asfytech.exe"

    # Kiểm tra xem tiến trình cũ có đang chạy không
    if is_process_running(old_file):
        os.system(f"taskkill /f /im {old_file}")  # Đóng ứng dụng cũ

    while is_process_running(old_file):  # Chờ cho đến khi ứng dụng cũ hoàn toàn dừng
        time.sleep(1)

    # Thay thế file cũ bằng file mới
    shutil.move(new_file, old_file)
    
    # Thông báo cho người dùng
    messagebox.showinfo("Cập nhật", "Cập nhật hoàn tất. Ứng dụng sẽ khởi động lại.")

    # Khởi động lại ứng dụng mới
    print(f"Old file: {old_file}")
    subprocess.Popen([old_file])
    os._exit(0)

def replace_file_in_thread(new_file):
    """Tạo thread mới để thay thế file và khởi động lại ứng dụng."""
    # Tạo và chạy thread thay thế file
    thread = threading.Thread(target=replace_and_restart, args=(new_file,))
    thread.daemon = True  # Đảm bảo thread tự động kết thúc khi ứng dụng chính kết thúc
    thread.start()

def start_update(text_widget):
    """Chạy quá trình tải cập nhật trong một luồng riêng."""
    
    messagebox.showinfo("Cập nhật", "Vui lòng click ok và đợi 3p...")

    def run_download():
        try:
            new_file = download_update(text_widget)
            if new_file is None:
                messagebox.showinfo("Cập nhật", "Hiện không có bản cập nhật nào")
            if new_file:
                messagebox.showinfo("Cập nhật", "Cập nhật hoàn tất. Ứng dụng sẽ khởi động lại.")
                replace_file_in_thread(new_file)
        except Exception as e:
            messagebox.showinfo("Thất bại", "Đã xảy ra lỗi, vui lòng thử lại sau")


    threading.Thread(target=run_download, daemon=True).start()

def update_page():
    """Giao diện cập nhật phần mềm."""
    main_frame = get_frame()
    
    tk.Label(main_frame, text="Cập nhật phần mềm", font=("Segoe UI", 20, "bold")).pack(pady=20)
    
    # Thêm khu vực hiển thị log tải xuống
    log_label = tk.Label(main_frame, text="Nhật ký tải xuống:", font=("Segoe UI", 12))
    log_label.pack(pady=5)
    text_widget = tk.Text(main_frame, height=10, width=80, state=tk.DISABLED)
    text_widget.pack(pady=5)

    # Nút cập nhật
    update_button = ttk.Button(main_frame, text="Cập nhật", command=lambda: start_update(text_widget))
    update_button.pack(pady=10)

    # Nút quay lại
    from helpers.base import render
    back_button = ttk.Button(main_frame, text="Quay lại", command=lambda: render('home'))
    back_button.pack(pady=5)

    return main_frame

# def update_page():
#     pass