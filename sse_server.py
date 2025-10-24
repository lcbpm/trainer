from flask import Flask, Response
from datetime import datetime
import time
import json

app = Flask(__name__)

# 生成事件数据
def generate_events():
    while True:
        # 获取当前时间
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data = {
            'time': current_time,
            'message': f'服务器时间更新: {current_time}'
        }
        
        # 格式化SSE数据
        yield f'data: {json.dumps(data)}\n\n'
        time.sleep(1)  # 每秒发送一次更新

@app.route('/events')
def sse():
    return Response(
        generate_events(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*'
        }
    )

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>SSE 示例</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            #events { 
                border: 1px solid #ccc;
                padding: 10px;
                margin-top: 20px;
                height: 300px;
                overflow-y: auto;
            }
            .event {
                margin: 5px 0;
                padding: 5px;
                background-color: #f0f0f0;
                border-radius: 4px;
            }
        </style>
    </head>
    <body>
        <h1>服务器发送事件 (SSE) 示例</h1>
        <div id="events"></div>

        <script>
            const eventsDiv = document.getElementById('events');
            const eventSource = new EventSource('/events');

            eventSource.onmessage = function(event) {
                const data = JSON.parse(event.data);
                const eventElement = document.createElement('div');
                eventElement.className = 'event';
                eventElement.textContent = data.message;
                eventsDiv.insertBefore(eventElement, eventsDiv.firstChild);
            };

            eventSource.onerror = function(error) {
                console.error('EventSource failed:', error);
                eventSource.close();
            };
        </script>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True, port=5000)