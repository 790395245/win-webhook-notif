# Win Webhook Notif
- Webhook转发到windows通知
- 手机验证码转发到电脑

## 简介

用于手机验证码转发到电脑自动复制填写。本项目有服务端和客户端。服务端部署在有公网ip或是可接受webhook请求的服务器上。客户端在windows电脑上运行。服务端会将webhook请求转发到客户端，客户端会弹出windows原生通知。

我将其用来转发手机验证码，配合安卓端[SmsForwarder](https://github.com/pppscn/SmsForwarder)使用。

通知会自动复制到剪贴板。

## 界面

![img1](https://blog.rz15.cn/wp-content/uploads/2025/06/企业微信截图_17496339625125.png)
![img2](https://blog.rz15.cn/wp-content/uploads/2025/06/企业微信截图_1749634036661.png)

## 使用说明

1. 服务端(默认端口59999)：
```bash
docker compose up -d
```

2. 客户端：
- 下载最新release可执行文件
- 双击运行，在终端输入服务端url，回车

## Windows开发说明

### Windows 开发环境配置

1. 安装Python：
   - 使用微软商店搜索并安装Python

2. 更改系统执行策略（PowerShell管理员运行）：
```powershell
Set-ExecutionPolicy -Scope LocalMachine -ExecutionPolicy RemoteSigned
```

3. 创建并激活虚拟环境：
```bash
# 创建虚拟环境
python -m venv webhook

# 激活虚拟环境
webhook\Scripts\activate
```

4. 配置pip镜像源（可选，推荐国内用户使用）：
```bash
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

5. 安装依赖：
```bash
pip install -r requirements.txt
```



## 许可证

MIT License


