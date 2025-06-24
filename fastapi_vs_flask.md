# FastAPI 与 Flask 主要区别

## 1. 协议支持（WSGI vs ASGI）

- **Flask**：基于 WSGI（Web Server Gateway Interface），只支持同步请求处理，不支持 WebSocket、HTTP/2 等现代协议。
- **FastAPI**：基于 ASGI（Asynchronous Server Gateway Interface），原生支持异步（async/await），支持 WebSocket、HTTP/2、高并发等现代特性。

---

## 2. 类型注解与自动文档

- **Flask**：不支持类型注解，参数校验和文档生成需手动实现或依赖第三方库。
- **FastAPI**：原生支持 Python 3.6+ 类型注解，自动参数校验，自动生成交互式 API 文档（Swagger UI、ReDoc）。

---

## 3. 异步支持

- **Flask**：主要为同步架构，异步支持较弱。
- **FastAPI**：原生支持异步编程（async/await），适合 IO 密集型和高并发场景。

---

## 4. 依赖注入

### FastAPI 原生依赖注入示例

```python
from fastapi import FastAPI, Depends

app = FastAPI()

# 定义一个依赖函数
def get_db():
    db = "数据库连接"
    try:
        yield db
    finally:
        print("关闭数据库连接")

# 在接口中通过 Depends 注入依赖
@app.get("/items/")
def read_items(db=Depends(get_db)):
    return {"db": db}
```

**说明：**
- `Depends(get_db)` 会自动调用 `get_db`，并把返回值注入到 `db` 参数。
- FastAPI 会自动管理依赖的生命周期（如 yield 前后逻辑）。

### Flask 手动实现依赖注入示例

```python
from flask import Flask, g

app = Flask(__name__)

# 手动管理依赖
def get_db():
    if 'db' not in g:
        g.db = "数据库连接"
    return g.db

@app.route("/items/")
def read_items():
    db = get_db()
    return {"db": db}
```

**说明：**
- 需要手动调用 `get_db()`，并用 Flask 的 `g` 对象管理资源。
- 没有自动的依赖注入和生命周期管理。

---

## 5. 社区生态与扩展性

- **Flask**：历史悠久，社区庞大，第三方插件丰富，适合快速开发和自定义。
- **FastAPI**：新兴框架，发展迅速，生态逐步完善，现代化特性多。

---

## 6. 适用场景

- **Flask**：适合中小型项目、传统 Web 应用、学习 Web 基础。
- **FastAPI**：适合高性能 API、需要自动文档、类型安全、异步支持的现代项目。

---

## 总结

| 特性         | Flask                | FastAPI                        |
|--------------|----------------------|--------------------------------|
| 协议         | WSGI（同步）         | ASGI（异步+同步）              |
| 类型注解     | 不支持               | 原生支持                       |
| 自动文档     | 需第三方库           | 原生支持                       |
| 异步支持     | 弱                   | 原生支持                       |
| 依赖注入     | 手动实现             | 原生支持                       |
| 社区生态     | 成熟、插件丰富       | 新兴、现代化                   |
| 适用场景     | 传统Web/小型API      | 高性能API/自动文档/异步场景     |
