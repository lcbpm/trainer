from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
from datetime import datetime
import time
from concurrent.futures import ThreadPoolExecutor

# 创建线程池
thread_pool = ThreadPoolExecutor(max_workers=4)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins='*')

def process_task(task_id):
    """模拟耗时任务的处理函数"""
    time.sleep(2)  # 模拟耗时操作
    return {
        'task_id': task_id,
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'message': f'任务 {task_id} 已完成处理'
    }

@app.route('/api/time')
def get_server_time():
    time.sleep(2)  # 模拟耗时操作
    return jsonify({
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'message': '这是一个普通的HTTP请求响应'
    })

@app.route('/api/task/<int:task_id>')
def handle_task(task_id):
    """使用线程池处理任务的端点"""
    future = thread_pool.submit(process_task, task_id)
    result = future.result()
    return jsonify(result)

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>WebSocket 聊天室示例</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 20px; 
                max-width: 800px; 
                margin: 0 auto; 
                padding: 20px;
            }
            #chat-container {
                border: 1px solid #ccc;
                padding: 20px;
                margin-top: 20px;
                height: 400px;
                display: flex;
                flex-direction: column;
            }
            #messages {
                flex-grow: 1;
                overflow-y: auto;
                margin-bottom: 20px;
            }
            .message {
                margin: 5px 0;
                padding: 8px;
                background-color: #f0f0f0;
                border-radius: 4px;
            }
            .message .username {
                font-weight: bold;
                color: #2196F3;
                margin-right: 8px;
            }
            .message .time {
                color: #666;
                font-size: 0.9em;
                margin-right: 8px;
            }
            .input-container {
                display: flex;
                gap: 10px;
            }
            #message-input {
                flex-grow: 1;
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            button {
                padding: 8px 16px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }
            button:hover {
                background-color: #45a049;
            }
        </style>
    </head>
    <body>
        <h1>WebSocket 聊天室</h1>
        <div id="chat-container">
            <div id="messages"></div>
            <div class="input-container">
                <input type="text" id="username-input" placeholder="输入用户名..." style="width: 150px;" />
                <input type="text" id="message-input" placeholder="输入消息..." />
                <button onclick="sendMessage()">发送</button>
                <button onclick="getServerTime()">获取服务器时间</button>
                <button onclick="startTasks()">并发执行任务</button>
            </div>
        </div>

        <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
        <script>
            const socket = io();
            const messagesDiv = document.getElementById('messages');
            const messageInput = document.getElementById('message-input');
            const usernameInput = document.getElementById('username-input');
            
            // 设置默认用户名
            usernameInput.value = '用户' + Math.floor(Math.random() * 1000);

            function addMessage(data) {
                const messageElement = document.createElement('div');
                messageElement.className = data.type === 'http' ? 'message http-message' : 'message';
                
                if (typeof data === 'string') {
                    // 系统消息
                    messageElement.textContent = data;
                } else {
                    // 用户消息
                    const usernameSpan = document.createElement('span');
                    usernameSpan.className = 'username';
                    usernameSpan.textContent = data.username;
                    
                    const timeSpan = document.createElement('span');
                    timeSpan.className = 'time';
                    timeSpan.textContent = data.time;
                    
                    const messageSpan = document.createElement('span');
                    messageSpan.className = 'message-content';
                    messageSpan.textContent = data.message;
                    
                    messageElement.appendChild(usernameSpan);
                    messageElement.appendChild(timeSpan);
                    messageElement.appendChild(messageSpan);
                }
                
                messagesDiv.appendChild(messageElement);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }

            function sendMessage() {
                const message = messageInput.value.trim();
                if (message) {
                    const username = usernameInput.value.trim() || '匿名用户';
                    socket.emit('message', { username: username, message: message });
                    messageInput.value = '';
                }
            }

            messageInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });

            socket.on('connect', () => {
                addMessage('已连接到服务器');
            });

            socket.on('message', (data) => {
                addMessage(data);
            });

            socket.on('disconnect', () => {
                addMessage('与服务器断开连接');
            });

            async function getServerTime() {
                try {
                    const response = await fetch('/api/time');
                    const data = await response.json();
                    addMessage({
                        username: 'System',
                        time: data.time,
                        message: data.message
                    });
                } catch (error) {
                    addMessage('获取服务器时间失败：' + error.message);
                }
            }

            async function executeTask(taskId) {
                try {
                    const response = await fetch(`/api/task/${taskId}`);
                    const data = await response.json();
                    addMessage({
                        username: 'Task System',
                        time: data.time,
                        message: `任务 ${data.task_id}: ${data.message}`
                    });
                } catch (error) {
                    addMessage(`任务 ${taskId} 执行失败：${error.message}`);
                }
            }

            async function startTasks() {
                // 同时启动多个任务
                const tasks = [1, 2, 3, 4];
                const promises = tasks.map(taskId => executeTask(taskId));
                await Promise.all(promises);
            }
        </script>
    </body>
    </html>
    '''

@socketio.on('message')
def handle_message(data):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    emit('message', {
        'time': current_time,
        'username': data['username'],
        'message': data['message']
    }, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5001)