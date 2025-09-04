# Python 函数传参规则

## 📋 目录

- [1. 位置参数（Positional Arguments）](#1-位置参数positional-arguments)
- [2. 关键字参数（Keyword Arguments）](#2-关键字参数keyword-arguments)
- [3. 默认参数（Default Arguments）](#3-默认参数default-arguments)
- [4. 可变参数（Variable-length Arguments）](#4-可变参数variable-length-arguments)
- [5. 参数顺序规则](#5-参数顺序规则)
- [6. 解包传参](#6-解包传参)

---

## 1. 位置参数（Positional Arguments）
按照参数的位置顺序传递给函数。

```python
def func(a, b):
    print(a, b)

func(1, 2)  # 输出: 1 2
```

---

## 2. 关键字参数（Keyword Arguments）
通过参数名指定传递的值，顺序可以不一致。

```python
func(b=2, a=1)  # 输出: 1 2
```

---

## 3. 默认参数（Default Arguments）
为参数设置默认值，调用时可以省略。

```python
def func(a, b=10):
    print(a, b)

func(1)      # 输出: 1 10
func(1, 2)   # 输出: 1 2
```

---

## 4. 可变参数（Variable-length Arguments）
- `*args`：接收任意数量的位置参数，作为元组传入。
- `**kwargs`：接收任意数量的关键字参数，作为字典传入。

```python
def func(*args, **kwargs):
    print(args)
    print(kwargs)

func(1, 2, x=3, y=4)
# 输出:
# (1, 2)
# {'x': 3, 'y': 4}
```

---

## 5. 参数顺序规则
定义函数时，参数顺序一般为：

```
位置参数 → 默认参数 → *args → 关键字参数 → **kwargs
```

---

## 6. 解包传参
- 使用 `*` 可以将列表/元组解包为位置参数
- 使用 `**` 可以将字典解包为关键字参数

```python
args = (1, 2)
kwargs = {'b': 2, 'a': 1}

func(*args)
func(**kwargs)
```

---

如有具体传参场景或代码，欢迎补充！ 