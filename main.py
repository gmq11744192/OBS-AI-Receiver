import cv2
import tkinter as tk
from tkinter import ttk
import subprocess
import threading
import time
from collections import deque
import numpy as np
from PIL import Image, ImageTk


class VideoReceiver:
    def __init__(self, master):
        self.master = master
        self.frame_times = deque(maxlen=30)

        # 视频尺寸默认值
        self.width = 256
        self.height = 256

        # 视频处理状态
        self.running = False
        self.ffmpeg_process = None
        self.thread = None

        # 初始化界面
        self.setup_gui()

        # 启动UI更新
        self.update_ui()

        # 窗口居中
        self.center_window()

    def setup_gui(self):
        """创建可视化界面"""
        self.master.title("视频接收端")

        # 设置区域
        settings_frame = ttk.LabelFrame(self.master, text="设置")
        settings_frame.pack(fill=tk.X, padx=10, pady=5)

        # IP和端口设置
        network_frame = ttk.Frame(settings_frame)
        network_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(network_frame, text="IP地址:").grid(row=0, column=0, padx=5, pady=5)
        self.ip_var = tk.StringVar(value="0.0.0.0")
        ttk.Entry(network_frame, textvariable=self.ip_var, width=15).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(network_frame, text="端口:").grid(row=0, column=2, padx=5, pady=5)
        self.port_var = tk.StringVar(value="6060")
        ttk.Entry(network_frame, textvariable=self.port_var, width=6).grid(row=0, column=3, padx=5, pady=5)

        # 视频尺寸设置
        size_frame = ttk.Frame(settings_frame)
        size_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(size_frame, text="宽度:").grid(row=0, column=0, padx=5, pady=5)
        self.width_var = tk.StringVar(value="256")
        ttk.Entry(size_frame, textvariable=self.width_var, width=6).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(size_frame, text="高度:").grid(row=0, column=2, padx=5, pady=5)
        self.height_var = tk.StringVar(value="256")
        ttk.Entry(size_frame, textvariable=self.height_var, width=6).grid(row=0, column=3, padx=5, pady=5)

        # 控制按钮
        control_frame = ttk.Frame(settings_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        self.start_button = ttk.Button(control_frame, text="开始接收", command=self.start_receiving)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(control_frame, text="停止接收", command=self.stop_receiving, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # 视频显示容器（使用Frame作为容器）
        self.display_container = ttk.Frame(self.master)
        self.display_container.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # 视频显示区域
        self.video_frame = ttk.Label(self.display_container)
        self.video_frame.pack(expand=True)

        # 状态显示区域
        status_frame = ttk.Frame(self.master)
        status_frame.pack(fill=tk.X, padx=10, pady=5)

        self.lbl_fps = ttk.Label(status_frame, text="帧率: 0.00 fps")
        self.lbl_fps.pack(side=tk.LEFT, padx=5)

        self.lbl_status = ttk.Label(status_frame, text="状态: 未接收")
        self.lbl_status.pack(side=tk.RIGHT, padx=5)

    def center_window(self):
        """将窗口居中显示"""
        self.master.update_idletasks()
        width = self.master.winfo_width()
        height = self.master.winfo_height()
        x = (self.master.winfo_screenwidth() // 2) - (width // 2)
        y = (self.master.winfo_screenheight() // 2) - (height // 2)
        self.master.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def start_receiving(self):
        """开始接收视频"""
        try:
            # 获取用户输入的IP和端口
            ip = self.ip_var.get().strip()
            port = self.port_var.get().strip()

            # 验证IP和端口
            if not ip or not port.isdigit():
                raise ValueError("请输入有效的IP地址和端口号")

            # 构建UDP URL
            self.udp_url = f"udp://@{ip}:{port}"

            # 获取用户输入的尺寸
            self.width = int(self.width_var.get())
            self.height = int(self.height_var.get())

            if self.width <= 0 or self.height <= 0:
                raise ValueError("尺寸必须为正整数")

            # 调整窗口大小以适应视频
            self.adjust_window_size()

            # 启动FFmpeg进程
            self.start_ffmpeg()

            # 启动视频处理线程
            self.running = True
            self.thread = threading.Thread(target=self.process_video)
            self.thread.start()

            # 更新界面状态
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.lbl_status.config(text=f"状态: 正在接收 {self.udp_url}")

        except ValueError as e:
            self.lbl_status.config(text=f"错误: {str(e)}")
        except Exception as e:
            self.lbl_status.config(text=f"错误: {str(e)}")

    def adjust_window_size(self):
        """调整窗口大小以适应视频"""
        # 获取当前设置区域和状态栏高度
        self.master.update_idletasks()
        settings_height = self.master.winfo_height() - self.display_container.winfo_height()

        # 计算新窗口尺寸（为视频尺寸添加边距）
        new_width = max(self.width + 40, 400)  # 最小宽度400
        new_height = self.height + settings_height + 40

        # 设置窗口尺寸
        self.master.geometry(f"{new_width}x{new_height}")

        # 重新居中窗口
        self.center_window()

    def stop_receiving(self):
        """停止接收视频"""
        if self.running:
            self.running = False
            if self.ffmpeg_process:
                self.ffmpeg_process.terminate()
                self.ffmpeg_process = None

            # 等待线程结束
            if self.thread and self.thread.is_alive():
                self.thread.join(timeout=1.0)

            # 更新界面状态
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.lbl_status.config(text="状态: 已停止")

            # 清空历史数据
            self.frame_times.clear()

    def start_ffmpeg(self):
        """启动FFmpeg接收进程"""
        command = [
            'ffmpeg',
            '-i', self.udp_url,
            '-f', 'rawvideo',  # 输出原始视频流
            '-pix_fmt', 'bgr24',  # OpenCV兼容的像素格式
            '-vcodec', 'rawvideo',
            '-s', f'{self.width}x{self.height}',  # 使用用户指定的分辨率
            'pipe:1'  # 输出到标准输出
        ]
        print(f"启动FFmpeg命令: {' '.join(command)}")

        self.ffmpeg_process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            bufsize=10 ** 8
        )

    def process_video(self):
        """视频处理线程"""
        frame_size = self.width * self.height * 3

        while self.running:
            try:
                # 从FFmpeg读取原始视频帧
                raw_frame = self.ffmpeg_process.stdout.read(frame_size)
                if len(raw_frame) != frame_size:
                    continue

                # 转换帧格式
                frame = np.frombuffer(raw_frame, np.uint8).reshape(self.height, self.width, 3)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # 计算帧率
                current_time = time.time()
                self.frame_times.append(current_time)

                # 使用PIL处理图像显示
                image = Image.fromarray(frame)
                photo = ImageTk.PhotoImage(image=image)
                self.video_frame.configure(image=photo)
                self.video_frame.image = photo  # 保持引用以防止垃圾回收

                # 确保视频帧居中显示
                self.video_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

            except Exception as e:
                print(f"视频处理错误: {str(e)}")
                if not self.running:
                    break
                if self.ffmpeg_process and self.ffmpeg_process.poll() is not None:
                    print(f"FFmpeg进程已退出，退出码: {self.ffmpeg_process.returncode}")
                    self.running = False
                    break

    def update_ui(self):
        """更新界面数据"""
        # 计算帧率
        if len(self.frame_times) >= 2:
            fps = len(self.frame_times) / (self.frame_times[-1] - self.frame_times[0])
            self.lbl_fps.config(text=f"帧率: {fps:.2f} fps")
        else:
            self.lbl_fps.config(text="帧率: 0.00 fps")

        self.master.after(1000, self.update_ui)

    def stop(self):
        """停止接收并关闭程序"""
        self.stop_receiving()
        self.master.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    receiver = VideoReceiver(root)
    root.protocol("WM_DELETE_WINDOW", receiver.stop)
    root.mainloop()
