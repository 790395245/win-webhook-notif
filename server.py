from flask import Flask, request
from flask_socketio import SocketIO
import logging

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 存储所有连接的客户端
connected_clients = set()

@app.route('/webhook', methods=['POST'])
def webhook():
    """接收webhook请求并转发给所有连接的客户端"""
    data = request.json
    logger.info(f"收到webhook请求: {data}")
    
    # 广播消息给所有连接的客户端
    socketio.emit('notification', data)
    return {'status': 'success'}, 200

@socketio.on('connect')
def handle_connect():
    """处理客户端连接"""
    client_id = request.sid
    connected_clients.add(client_id)
    logger.info(f"客户端已连接: {client_id}")

@socketio.on('disconnect')
def handle_disconnect():
    """处理客户端断开连接"""
    client_id = request.sid
    connected_clients.remove(client_id)
    logger.info(f"客户端已断开连接: {client_id}")

if __name__ == '__main__':
    logger.info("启动服务器...")
    socketio.run(app, host='0.0.0.0', port=59999, debug=True) 