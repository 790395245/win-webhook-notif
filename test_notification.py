import requests
import json

def send_test_notification():
    # 服务器地址
    server_url = "http://127.0.0.1:59999"
    
    # 测试通知数据
    notification_data = {
        "title": "【测试】验证码",
        "message": "888888"
    }
    
    try:
        # 发送 POST 请求到正确的端点
        response = requests.post(
            f"{server_url}/webhook",
            json=notification_data,
            headers={"Content-Type": "application/json"}
        )
        
        # 检查响应
        if response.status_code == 200:
            print("通知发送成功！")
            print(f"服务器响应：{response.json()}")
        else:
            print(f"发送失败，状态码：{response.status_code}")
            print(f"错误信息：{response.text}")
            
    except Exception as e:
        print(f"发送通知时出错：{str(e)}")

if __name__ == "__main__":
    send_test_notification() 