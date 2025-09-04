# MyBatis 核心组件速查

## 核心组件概览

### 1. SqlSessionFactory
- 用于创建 SqlSession 的工厂
- 全局唯一，线程安全
- 通过 SqlSessionFactoryBuilder 创建

### 2. SqlSession
- 执行 SQL 语句的核心接口
- 管理事务、获取 Mapper
- 非线程安全，每次请求创建新实例

### 3. Mapper 接口
- 定义数据库操作方法的接口
- MyBatis 自动生成代理实现

### 4. Executor（执行器）
- SQL 执行引擎
- 类型：
  - SimpleExecutor：简单执行器
  - ReuseExecutor：可重用 Statement
  - BatchExecutor：批处理执行器

### 5. StatementHandler
- 封装 JDBC Statement 操作
- 负责 SQL 生成和结果集处理

### 6. ParameterHandler
- 处理 SQL 参数设置
- 将 Java 对象转换为 JDBC 参数

### 7. ResultSetHandler
- 处理结果集映射
- 将 JDBC ResultSet 转换为 Java 对象

### 8. TypeHandler
- 类型转换器
- Java 类型 ↔ JDBC 类型相互转换

### 9. MappedStatement
- 映射语句对象
- 封装 SQL 语句、参数映射、结果映射等信息

## 工作流程（简化版）

1. SqlSessionFactoryBuilder → SqlSessionFactory
2. SqlSessionFactory → SqlSession
3. SqlSession 获取 Mapper 代理对象
4. Mapper 方法调用 → SQL 执行 → 返回结果

## 核心特性

- **SQL 映射**：XML 或注解方式定义 SQL
- **动态代理**：自动生成 Mapper 接口实现
- **缓存机制**：一级缓存（SqlSession）+ 二级缓存（Mapper）
- **连接管理**：内置连接池管理
- **事务管理**：通过 SqlSession 管理事务