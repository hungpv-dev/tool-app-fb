import os
import time
import requests
import shutil
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from main.root import get_frame

def download_update(url):
    """Tải xuống file cập nhật từ URL."""
    new_file = "app_new.exe"
    try:
        response = requests.get(url, stream=True)
        with open(new_file, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
        return new_file
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể tải file cập nhật: {e}")
        return None

def replace_and_restart(new_file):
    """Đóng ứng dụng, thay thế file và khởi động lại."""
    old_file = "app.exe"
    
    # Đóng ứng dụng cũ
    os.system(f"taskkill /f /im {old_file}")
    time.sleep(2)
    
    # Thay thế file cũ bằng file mới
    shutil.move(new_file, old_file)
    messagebox.showinfo("Cập nhật", "Cập nhật hoàn tất. Ứng dụng sẽ khởi động lại.")
    
    # Khởi động lại ứng dụng
    subprocess.Popen([old_file])
    os._exit(0)

def start_update(url_entry):
    """Xử lý quá trình tải và cập nhật khi nhấn nút."""
    url = url_entry.get()
    if not url:
        messagebox.showwarning("Cảnh báo", "Vui lòng nhập đường dẫn cập nhật.")
        return
    
    messagebox.showinfo("Cập nhật", "Đang tải bản cập nhật. Vui lòng đợi...")
    new_file = download_update(url)
    if new_file:
        replace_and_restart(new_file)

def update_page():
    """Giao diện cập nhật phần mềm."""
    main_frame = get_frame()
    
    # Tiêu đề
    tk.Label(main_frame, text="Cập nhật phần mềm", font=("Segoe UI", 20, "bold")).pack(pady=20)
    
    # Ô nhập URL
    tk.Label(main_frame, text="Nhập đường dẫn file cập nhật:", font=("Segoe UI", 12)).pack(pady=5)
    url_entry = ttk.Entry(main_frame, width=60)
    url_entry.pack(pady=5)
    
    # Nút cập nhật
    update_button = ttk.Button(main_frame, text="Cập nhật", command=lambda: start_update(url_entry))
    update_button.pack(pady=10)
    
    # Nút quay lại
    from helpers.base import render
    back_button = ttk.Button(main_frame, text="Quay lại", command=lambda: render('home'))
    back_button.pack(pady=5)
    
    return main_frame