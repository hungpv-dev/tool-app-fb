import os
import time
import shutil
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import re
import gdown
from main.root import get_frame

def update_console(output, text_widget):
    """Hiển thị log tải xuống trên giao diện."""
    text_widget.config(state=tk.NORMAL)
    text_widget.insert(tk.END, output + "\n")
    text_widget.config(state=tk.DISABLED)
    text_widget.see(tk.END)  # Cuộn xuống dòng mới nhất

def download_update(url, progress_var, progress_label, text_widget):
    """Tải file từ Google Drive bằng gdown và cập nhật tiến trình."""
    new_file = "asfytech_new.exe"
    
    # Trích xuất ID từ URL Google Drive
    match = re.search(r'd/([a-zA-Z0-9_-]+)', url) 
    if match:
        file_id = match.group(1)
        url = f'https://drive.google.com/uc?id={file_id}'

    try:
        # Chạy gdown bằng subprocess để lấy tiến trình tải
        process = subprocess.Popen(
            ["gdown", url, "-O", new_file, "--fuzzy"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True
        )

        for line in process.stdout:
            output = line.strip()
            text_widget.after(0, update_console, output, text_widget)

            # Đọc tiến trình từ output của gdown
            match = re.search(r'\[(\d+)%\]\s+([\d.]+)MB/([\d.]+)MB', output)
            if match:
                percent = int(match.group(1))
                downloaded_size = float(match.group(2))
                total_size = float(match.group(3))

                # Cập nhật tiến trình tải xuống
                progress_var.set(percent)
                progress_label.config(text=f"Đã tải: {downloaded_size:.1f}MB/{total_size:.1f}MB")

        process.wait()

    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể tải file cập nhật: {e}")
        return None
    
    return new_file

def replace_and_restart(new_file):
    """Đóng ứng dụng cũ, thay thế file và khởi động lại."""
    old_file = "asfytech.exe"
    
    os.system(f"taskkill /f /im {old_file}")
    time.sleep(2)

    shutil.move(new_file, old_file)
    messagebox.showinfo("Cập nhật", "Cập nhật hoàn tất. Ứng dụng sẽ khởi động lại.")

    subprocess.Popen([old_file])
    os._exit(0)

def start_update(url_entry, progress_var, progress_label, text_widget):
    """Chạy quá trình tải cập nhật trong một luồng riêng."""
    url = url_entry.get()
    if not url:
        messagebox.showwarning("Cảnh báo", "Vui lòng nhập đường dẫn cập nhật.")
        return
    
    messagebox.showinfo("Cập nhật", "Đang tải bản cập nhật. Vui lòng đợi...")

    def run_download():
        new_file = download_update(url, progress_var, progress_label, text_widget)
        if new_file:
            messagebox.showinfo("Cập nhật", "Cập nhật hoàn tất. Ứng dụng sẽ khởi động lại.")
            replace_and_restart(new_file)

    threading.Thread(target=run_download, daemon=True).start()

def update_page():
    """Giao diện cập nhật phần mềm."""
    main_frame = get_frame()
    
    tk.Label(main_frame, text="Cập nhật phần mềm", font=("Segoe UI", 20, "bold")).pack(pady=20)
    
    tk.Label(main_frame, text="Nhập đường dẫn file cập nhật:", font=("Segoe UI", 12)).pack(pady=5)
    url_entry = ttk.Entry(main_frame, width=60)
    url_entry.pack(pady=5)
    
    # Thanh tiến trình
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(main_frame, length=400, variable=progress_var)
    progress_bar.pack(pady=5)
    progress_label = tk.Label(main_frame, text="Chưa bắt đầu", font=("Segoe UI", 10))
    progress_label.pack()
    
    # Thêm khu vực hiển thị log tải xuống
    log_label = tk.Label(main_frame, text="Nhật ký tải xuống:", font=("Segoe UI", 12))
    log_label.pack(pady=5)
    text_widget = tk.Text(main_frame, height=10, width=80, state=tk.DISABLED)
    text_widget.pack(pady=5)

    # Nút cập nhật
    update_button = ttk.Button(main_frame, text="Cập nhật", command=lambda: start_update(url_entry, progress_var, progress_label, text_widget))
    update_button.pack(pady=10)

    # Nút quay lại
    from helpers.base import render
    back_button = ttk.Button(main_frame, text="Quay lại", command=lambda: render('home'))
    back_button.pack(pady=5)

    return main_frame