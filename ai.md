# AI 高级面试题完整整理

## 📋 目录

- [1. 机器学习基础](#1-机器学习基础)
  - [1.1 监督学习](#11-监督学习)
  - [1.2 无监督学习](#12-无监督学习)
  - [1.3 强化学习](#13-强化学习)
  - [1.4 模型评估与选择](#14-模型评估与选择)
- [2. 深度学习](#2-深度学习)
  - [2.1 神经网络基础](#21-神经网络基础)
  - [2.2 卷积神经网络](#22-卷积神经网络)
  - [2.3 循环神经网络](#23-循环神经网络)
  - [2.4 Transformer架构](#24-transformer架构)
- [3. 自然语言处理](#3-自然语言处理)
- [4. 计算机视觉](#4-计算机视觉)
- [5. 大模型与LLM](#5-大模型与llm)
- [6. AI工程实践](#6-ai工程实践)

---

## 1. 机器学习基础

### 1.1 监督学习

**Q: 解释偏差(Bias)和方差(Variance)的概念，以及它们之间的权衡？**

**理论解析：**
- **偏差(Bias)**：模型预测值与真实值之间的系统性误差
- **方差(Variance)**：模型在不同训练集上预测结果的变化程度
- **权衡关系**：总误差 = 偏差² + 方差 + 噪声

**实战代码示例：**
```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline

def bias_variance_analysis():
    """偏差-方差分析实战演示"""
    
    # 生成真实函数数据
    def true_function(x):
        return 1.5 * x**2 + 0.3 * x + 0.1
    
    # 生成训练数据
    np.random.seed(42)
    n_samples = 100
    X = np.random.uniform(-1, 1, n_samples).reshape(-1, 1)
    noise = np.random.normal(0, 0.1, n_samples)
    y = true_function(X.ravel()) + noise
    
    # 测试数据
    X_test = np.linspace(-1.2, 1.2, 100).reshape(-1, 1)
    y_test_true = true_function(X_test.ravel())
    
    # 不同复杂度的模型
    degrees = [1, 3, 9, 15]
    n_experiments = 100
    
    results = {}
    
    for degree in degrees:
        predictions = []
        
        # 多次实验来估计偏差和方差
        for i in range(n_experiments):
            # 重新采样训练数据
            indices = np.random.choice(len(X), size=len(X), replace=True)
            X_bootstrap = X[indices]
            y_bootstrap = y[indices]
            
            # 训练模型
            poly_model = Pipeline([
                ('poly', PolynomialFeatures(degree=degree)),
                ('linear', LinearRegression())
            ])
            
            poly_model.fit(X_bootstrap, y_bootstrap)
            pred = poly_model.predict(X_test)
            predictions.append(pred)
        
        predictions = np.array(predictions)
        
        # 计算偏差和方差
        mean_prediction = np.mean(predictions, axis=0)
        bias_squared = np.mean((mean_prediction - y_test_true)**2)
        variance = np.mean(np.var(predictions, axis=0))
        
        results[degree] = {
            'bias_squared': bias_squared,
            'variance': variance,
            'total_error': bias_squared + variance,
        }
        
        print(f"多项式度数 {degree}:")
        print(f"  偏差² = {bias_squared:.4f}")
        print(f"  方差 = {variance:.4f}")
        print(f"  总误差 = {bias_squared + variance:.4f}")
        print()
    
    return results

# 运行分析
results = bias_variance_analysis()
```

**Q: 什么是过拟合和欠拟合？如何检测和解决？**

**检测方法：**
1. **验证曲线**：观察训练误差和验证误差随参数变化的趋势
2. **学习曲线**：观察误差随训练样本数量变化的趋势
3. **交叉验证**：使用K折交叉验证评估模型泛化能力

**解决方案：**
- **过拟合**：正则化、早停、Dropout、数据增强
- **欠拟合**：增加模型复杂度、特征工程、减少正则化

### 1.2 无监督学习

**Q: 解释K-means聚类算法的原理和局限性？**

**K-means算法原理：**
1. 随机初始化K个聚类中心
2. 将每个点分配到最近的聚类中心
3. 更新聚类中心为该类所有点的均值
4. 重复2-3步直到收敛

**局限性：**
- 需要预先指定K值
- 对初始化敏感
- 假设聚类是球形的
- 对噪声和异常值敏感

**改进方法：**
```python
from sklearn.cluster import KMeans
import numpy as np

def improved_kmeans():
    """改进的K-means实现"""
    
    # K-means++初始化
    kmeans_plus = KMeans(n_clusters=3, init='k-means++', n_init=10)
    
    # 多次运行选择最佳结果
    best_inertia = float('inf')
    best_model = None
    
    for _ in range(20):
        kmeans = KMeans(n_clusters=3, random_state=None)
        kmeans.fit(X)
        if kmeans.inertia_ < best_inertia:
            best_inertia = kmeans.inertia_
            best_model = kmeans
    
    return best_model
```

### 1.3 强化学习

**Q: 解释Q-learning算法的原理？**

**Q-learning核心公式：**
```
Q(s,a) = Q(s,a) + α[r + γ·max(Q(s',a')) - Q(s,a)]
```

**关键概念：**
- **状态(State)**：环境的当前情况
- **动作(Action)**：智能体可以采取的行为
- **奖励(Reward)**：执行动作后获得的反馈
- **Q值**：在状态s下采取动作a的期望累积奖励

**简化实现：**
```python
class QLearning:
    def __init__(self, actions, lr=0.1, gamma=0.9, epsilon=0.1):
        self.actions = actions
        self.lr = lr
        self.gamma = gamma
        self.epsilon = epsilon
        self.q_table = {}
    
    def get_q_value(self, state, action):
        return self.q_table.get((state, action), 0.0)
    
    def update(self, state, action, reward, next_state):
        current_q = self.get_q_value(state, action)
        max_next_q = max([self.get_q_value(next_state, a) for a in self.actions])
        new_q = current_q + self.lr * (reward + self.gamma * max_next_q - current_q)
        self.q_table[(state, action)] = new_q
    
    def choose_action(self, state):
        if random.random() < self.epsilon:
            return random.choice(self.actions)
        else:
            q_values = [self.get_q_value(state, a) for a in self.actions]
            return self.actions[np.argmax(q_values)]
```

### 1.4 模型评估与选择

**Q: 解释交叉验证的种类和适用场景？**

**常见交叉验证方法：**

1. **K折交叉验证**：适用于一般情况
2. **分层K折**：适用于分类问题，保持类别比例
3. **留一法(LOOCV)**：适用于小数据集
4. **时间序列交叉验证**：适用于时序数据

```python
from sklearn.model_selection import (
    KFold, StratifiedKFold, LeaveOneOut, TimeSeriesSplit
)

def cross_validation_demo():
    """交叉验证方法演示"""
    
    # K折交叉验证
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    
    # 分层K折
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    # 时间序列交叉验证
    tscv = TimeSeriesSplit(n_splits=5)
    
    # 使用示例
    for train_idx, val_idx in kf.split(X):
        X_train, X_val = X[train_idx], X[val_idx]
        y_train, y_val = y[train_idx], y[val_idx]
        
        # 训练和评估模型
        model.fit(X_train, y_train)
        score = model.score(X_val, y_val)
```

## 2. 深度学习

### 2.1 神经网络基础

**Q: 解释反向传播算法的原理？**

**反向传播核心步骤：**
1. **前向传播**：计算输出和损失
2. **反向传播**：计算梯度
3. **参数更新**：使用梯度下降更新权重

**数学原理：**
```python
import numpy as np

class SimpleNeuralNetwork:
    def __init__(self, input_size, hidden_size, output_size):
        # 初始化权重
        self.W1 = np.random.randn(input_size, hidden_size) * 0.01
        self.b1 = np.zeros((1, hidden_size))
        self.W2 = np.random.randn(hidden_size, output_size) * 0.01
        self.b2 = np.zeros((1, output_size))
    
    def sigmoid(self, x):
        return 1 / (1 + np.exp(-np.clip(x, -250, 250)))
    
    def sigmoid_derivative(self, x):
        return x * (1 - x)
    
    def forward(self, X):
        self.z1 = np.dot(X, self.W1) + self.b1
        self.a1 = self.sigmoid(self.z1)
        self.z2 = np.dot(self.a1, self.W2) + self.b2
        self.a2 = self.sigmoid(self.z2)
        return self.a2
    
    def backward(self, X, y, output):
        m = X.shape[0]
        
        # 输出层梯度
        dz2 = output - y
        dW2 = (1/m) * np.dot(self.a1.T, dz2)
        db2 = (1/m) * np.sum(dz2, axis=0, keepdims=True)
        
        # 隐藏层梯度
        dz1 = np.dot(dz2, self.W2.T) * self.sigmoid_derivative(self.a1)
        dW1 = (1/m) * np.dot(X.T, dz1)
        db1 = (1/m) * np.sum(dz1, axis=0, keepdims=True)
        
        return dW1, db1, dW2, db2
    
    def update_parameters(self, dW1, db1, dW2, db2, learning_rate):
        self.W1 -= learning_rate * dW1
        self.b1 -= learning_rate * db1
        self.W2 -= learning_rate * dW2
        self.b2 -= learning_rate * db2
```

**Q: 常见的激活函数有哪些？各自的优缺点是什么？**

**激活函数对比：**

```python
import numpy as np
import matplotlib.pyplot as plt

def activation_functions():
    x = np.linspace(-5, 5, 100)
    
    # Sigmoid
    sigmoid = 1 / (1 + np.exp(-x))
    sigmoid_grad = sigmoid * (1 - sigmoid)
    
    # Tanh
    tanh = np.tanh(x)
    tanh_grad = 1 - tanh**2
    
    # ReLU
    relu = np.maximum(0, x)
    relu_grad = (x > 0).astype(float)
    
    # Leaky ReLU
    leaky_relu = np.where(x > 0, x, 0.01 * x)
    leaky_grad = np.where(x > 0, 1, 0.01)
    
    # ELU
    alpha = 1.0
    elu = np.where(x > 0, x, alpha * (np.exp(x) - 1))
    elu_grad = np.where(x > 0, 1, elu + alpha)
    
    return {
        'sigmoid': (sigmoid, sigmoid_grad),
        'tanh': (tanh, tanh_grad),
        'relu': (relu, relu_grad),
        'leaky_relu': (leaky_relu, leaky_grad),
        'elu': (elu, elu_grad)
    }
```

**激活函数特点：**
- **Sigmoid**：输出0-1，存在梯度消失问题
- **Tanh**：输出-1到1，比Sigmoid好但仍有梯度消失
- **ReLU**：解决梯度消失，但有神经元死亡问题
- **Leaky ReLU**：解决ReLU死亡问题
- **ELU**：结合ReLU和Sigmoid优点

### 2.2 卷积神经网络

**Q: 解释卷积层、池化层的作用和参数？**

**卷积层参数：**
- **卷积核大小**：通常3x3或5x5
- **步长(Stride)**：控制输出尺寸
- **填充(Padding)**：保持尺寸或减少边界效应
- **通道数**：特征图数量

**池化层作用：**
- 降维减少参数
- 提供平移不变性
- 扩大感受野

```python
import torch
import torch.nn as nn

class SimpleCNN(nn.Module):
    def __init__(self, num_classes=10):
        super(SimpleCNN, self).__init__()
        
        # 卷积块1
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, stride=1, padding=1)
        self.bn1 = nn.BatchNorm2d(32)
        self.relu1 = nn.ReLU(inplace=True)
        self.pool1 = nn.MaxPool2d(kernel_size=2, stride=2)
        
        # 卷积块2
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1)
        self.bn2 = nn.BatchNorm2d(64)
        self.relu2 = nn.ReLU(inplace=True)
        self.pool2 = nn.MaxPool2d(kernel_size=2, stride=2)
        
        # 全连接层
        self.fc = nn.Linear(64 * 8 * 8, num_classes)
        self.dropout = nn.Dropout(0.5)
    
    def forward(self, x):
        # 卷积块1
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu1(x)
        x = self.pool1(x)
        
        # 卷积块2
        x = self.conv2(x)
        x = self.bn2(x)
        x = self.relu2(x)
        x = self.pool2(x)
        
        # 展平
        x = x.view(x.size(0), -1)
        x = self.dropout(x)
        x = self.fc(x)
        
        return x
```

### 2.3 循环神经网络

**Q: LSTM和GRU的区别和优势？**

**LSTM特点：**
- 三个门：遗忘门、输入门、输出门
- 细胞状态和隐藏状态
- 有效解决长期依赖问题

**GRU特点：**
- 两个门：重置门、更新门
- 参数更少，训练更快
- 性能接近LSTM

```python
import torch
import torch.nn as nn

class LSTMModel(nn.Module):
    def __init__(self, vocab_size, embed_size, hidden_size, num_layers, num_classes):
        super(LSTMModel, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embed_size)
        self.lstm = nn.LSTM(embed_size, hidden_size, num_layers, 
                           batch_first=True, dropout=0.3)
        self.fc = nn.Linear(hidden_size, num_classes)
        self.dropout = nn.Dropout(0.5)
    
    def forward(self, x):
        embedded = self.embedding(x)
        lstm_out, (hidden, cell) = self.lstm(embedded)
        
        # 使用最后一个时间步的输出
        output = self.dropout(lstm_out[:, -1, :])
        output = self.fc(output)
        
        return output

class GRUModel(nn.Module):
    def __init__(self, vocab_size, embed_size, hidden_size, num_layers, num_classes):
        super(GRUModel, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embed_size)
        self.gru = nn.GRU(embed_size, hidden_size, num_layers, 
                         batch_first=True, dropout=0.3)
        self.fc = nn.Linear(hidden_size, num_classes)
        self.dropout = nn.Dropout(0.5)
    
    def forward(self, x):
        embedded = self.embedding(x)
        gru_out, hidden = self.gru(embedded)
        
        # 使用最后一个时间步的输出
        output = self.dropout(gru_out[:, -1, :])
        output = self.fc(output)
        
        return output
```

### 2.4 Transformer架构

**Q: 解释Transformer中的注意力机制？**

**自注意力机制原理：**
```
Attention(Q,K,V) = softmax(QK^T/√d_k)V
```

**多头注意力实现：**
```python
import torch
import torch.nn as nn
import math

class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, num_heads):
        super(MultiHeadAttention, self).__init__()
        assert d_model % num_heads == 0
        
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)
        
    def scaled_dot_product_attention(self, Q, K, V, mask=None):
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)
        
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)
        
        attention_weights = torch.softmax(scores, dim=-1)
        output = torch.matmul(attention_weights, V)
        
        return output, attention_weights
    
    def forward(self, query, key, value, mask=None):
        batch_size = query.size(0)
        
        # 线性变换
        Q = self.W_q(query)
        K = self.W_k(key)
        V = self.W_v(value)
        
        # 分割为多头
        Q = Q.view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        K = K.view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        V = V.view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        
        # 注意力计算
        attention_output, attention_weights = self.scaled_dot_product_attention(Q, K, V, mask)
        
        # 合并多头
        attention_output = attention_output.transpose(1, 2).contiguous().view(
            batch_size, -1, self.d_model)
        
        # 最终线性变换
        output = self.W_o(attention_output)
        
        return output, attention_weights
```

**Transformer优势：**
- 并行计算能力强
- 长距离依赖建模能力
- 可解释性好（注意力权重）
- 预训练效果好