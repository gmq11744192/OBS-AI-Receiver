# UDP视频接收器 (UDP Video Receiver)

![语言](https://img.shields.io/badge/语言-Python-blue)
![许可证](https://img.shields.io/badge/许可证-MIT-green)

## 项目简介

UDP视频接收器是一个基于Python的应用程序，专门用于通过UDP协议接收视频流并实时显示。该应用程序使用FFmpeg处理视频流，并通过Tkinter构建了一个用户友好的界面，使用户可以轻松配置和查看视频流。

## 功能特点

- **实时视频接收**：通过UDP协议接收视频流并实时显示
- **自定义网络设置**：允许用户配置IP地址和端口号
- **自定义视频尺寸**：支持自定义视频宽度和高度设置
- **实时帧率显示**：实时计算并显示当前视频的帧率
- **友好的用户界面**：基于Tkinter构建的直观界面
- **窗口自动最大化**：程序启动时自动最大化窗口以提供最佳观看体验

## 技术栈

- **Python**：核心编程语言
- **Tkinter**：GUI界面库
- **OpenCV**：图像处理
- **FFmpeg**：视频流处理
- **NumPy**：数组操作和数据处理
- **PIL (Pillow)**：图像显示和处理

## 安装要求

运行此应用程序需要以下依赖项：

1. Python 3.6+
2. FFmpeg（需要在系统环境变量中可访问）
3. 以下Python库：
   - OpenCV (`cv2`)
   - Tkinter (`tkinter`)
   - NumPy (`numpy`)
   - Pillow (`PIL`)

## 安装步骤

1. 克隆此仓库：
   ```bash
   git clone https://github.com/你的用户名/UDP视频接收器.git
   cd UDP视频接收器
   ```

2. 安装所需的Python库：
   ```bash
   pip install opencv-python numpy pillow
   ```

3. 安装FFmpeg：
   - **Windows**：下载FFmpeg并将其添加到系统环境变量中
   - **Linux**：`sudo apt install ffmpeg`
   - **macOS**：`brew install ffmpeg`

## 使用方法

1. 运行应用程序：
   ```bash
   python main.py
   ```

2. 在应用界面中配置以下设置：
   - **IP地址**：输入接收UDP流的IP地址（默认为`0.0.0.0`表示接收所有可用网络接口的数据）
   - **端口**：输入UDP流的端口号（默认为`6060`）
   - **宽度**和**高度**：设置视频的分辨率

3. 点击"开始接收"按钮开始接收和显示视频流
4. 点击"停止接收"按钮停止接收

## 项目结构

```
UDP视频接收器/
│
└── main.py           # 主程序文件，包含应用程序逻辑和GUI
```

## 发送端配置示例

要使用FFmpeg向此应用程序发送视频流，可以使用以下命令：

```bash
ffmpeg -i 视频源文件或设备 -f mpegts -codec:v mpeg1video -s 宽x高 -b:v 1000k -bf 0 udp://目标IP:端口
```

例如：
```bash
ffmpeg -i video.mp4 -f mpegts -codec:v mpeg1video -s 256x256 -b:v 1000k -bf 0 udp://127.0.0.1:6060
```

## 许可证

此项目采用MIT许可证 - 详细信息请查看LICENSE文件

## 贡献

欢迎贡献！请随时提交问题或拉取请求。

## 联系方式

如有任何问题或建议，请通过GitHub Issues与我联系。 