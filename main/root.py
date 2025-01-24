import tkinter as tk
import threading

# Biến giữ instance của root
root_instance = None
main_frame = None
global_theard_event = None

def create_app():
    """Tạo cửa sổ ứng dụng chính."""
    root = tk.Tk()
    root.title("Ứng dụng Quản lý")
    root.geometry("1400x600")  # Tăng chiều cao cửa sổ
    root.config(bg="#f0f2f5")  # Màu nền của Facebook (#f0f2f5)
    return root

def get_root():
    """Lấy instance của root."""
    global root_instance 
    # Nếu root chưa được khởi tạo, tạo mới
    if root_instance is None:
        root_instance = create_app()
    return root_instance

def get_frame():
    root = get_root()
    """Lấy instance của root."""
    global main_frame 
    # Nếu root chưa được khởi tạo, tạo mới
    if main_frame is None:
        main_frame = tk.Frame(root, bg="#f0f2f5")
        main_frame.pack(fill=tk.BOTH, expand=True)
    return main_frame

def get_global_theard_event():
    global global_theard_event 
    if global_theard_event is None:
        global_theard_event = threading.Event()
    return global_theard_event
