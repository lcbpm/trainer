# 9. Redis

## 📋 目录

- [9.1 Go-Redis客户端](#91-go-redis客户端)
- [9.2 连接池与性能优化](#92-连接池与性能优化)
- [9.3 分布式锁与缓存](#93-分布式锁与缓存)
  - [9.3.1 分布式锁实现方式综述](#931-分布式锁实现方式综述)
  - [9.3.2 Redis分布式锁实战实现](#932-redis分布式锁实战实现)
  - [9.3.3 高级分布式锁特性](#933-高级分布式锁特性)
  - [9.3.4 不同分布式锁比较](#934-不同分布式锁比较)
  - [9.3.5 分布式锁最佳实践](#935-分布式锁最佳实践)
  - [9.3.6 缓存策略与模式](#936-缓存策略与模式)
  - [9.3.7 Redis分布式锁的缺陷与改进方案](#937-redis分布式锁的缺陷与改进方案)
    - [9.3.7.1 SET EXPIRE原子性问题](#9371-set-expire原子性问题)
    - [9.3.7.2 续期失败的复杂性问题](#9372-续期失败的复杂性问题)
    - [9.3.7.3 网络分区和脑裂问题](#9373-网络分区和脑裂问题)
    - [9.3.7.4 时钟漂移问题](#9374-时钟漂移问题)
    - [9.3.7.5 锁重入性问题](#9375-锁重入性问题)
    - [9.3.7.6 性能优化建议](#9376-性能优化建议)

---

### 9.1 Go-Redis客户端

**Q: 在Go中如何连接和操作Redis？**

#### 基本连接和操作

```go
package main

import (
    "context"
    "fmt"
    "log"
    "time"
    
    "github.com/go-redis/redis/v8"
)

// Redis服务结构体
type RedisService struct {
    client *redis.Client
    ctx    context.Context
}

// 初始化Redis客户端
func NewRedisService() *RedisService {
    rdb := redis.NewClient(&redis.Options{
        Addr:     "localhost:6379",
        Password: "",
        DB:       0,
        PoolSize: 10,
        
        // 超时配置
        DialTimeout:  5 * time.Second,
        ReadTimeout:  3 * time.Second,
        WriteTimeout: 3 * time.Second,
    })
    
    return &RedisService{
        client: rdb,
        ctx:    context.Background(),
    }
}

// 基本操作示例
func (r *RedisService) BasicOperations() {
    // String操作
    r.client.Set(r.ctx, "key1", "value1", time.Hour)
    val, _ := r.client.Get(r.ctx, "key1").Result()
    fmt.Printf("key1: %s\n", val)
    
    // Hash操作 - 用户信息
    userKey := "user:1001"
    r.client.HMSet(r.ctx, userKey, map[string]interface{}{
        "name": "张三",
        "age":  25,
    })
    
    // List操作 - 消息队列
    r.client.LPush(r.ctx, "messages", "msg1", "msg2")
    msg, _ := r.client.RPop(r.ctx, "messages").Result()
    fmt.Printf("Message: %s\n", msg)
    
    // Set操作 - 标签系统
    r.client.SAdd(r.ctx, "tags", "golang", "redis")
    
    // Sorted Set操作 - 排行榜
    r.client.ZAdd(r.ctx, "leaderboard", &redis.Z{
        Score: 1000, Member: "player1",
    })
}
```

### 9.2 连接池与性能优化

**Q: 如何优化Go中Redis的性能？**

#### Pipeline批量操作

```go
// 批量操作优化
func (r *RedisService) BatchOperations(data map[string]string) error {
    pipe := r.client.Pipeline()
    
    // 批量添加命令
    for key, value := range data {
        pipe.Set(r.ctx, key, value, time.Hour)
    }
    
    // 执行所有命令
    _, err := pipe.Exec(r.ctx)
    return err
}

// 连接池监控
func (r *RedisService) MonitorPool() {
    stats := r.client.PoolStats()
    log.Printf("Pool Stats - Hits: %d, Misses: %d, TotalConns: %d",
        stats.Hits, stats.Misses, stats.TotalConns)
}
```

### 9.3 分布式锁与缓存

#### 9.3.1 分布式锁实现方式综述

分布式锁是分布式系统中确保多个进程或线程不会同时访问共享资源的重要机制。Go语言中有多种分布式锁的实现方式：

**1. 基于Redis的分布式锁**
- 利用Redis的原子操作特性
- 支持锁过期时间，避免死锁
- 实现简单，性能较好

**2. 基于Etcd的分布式锁**
- 利用Etcd的租约(Lease)机制
- 强一致性保证
- 支持锁的续约和监听

**3. 基于Zookeeper的分布式锁**
- 利用ZooKeeper的临时顺序节点
- 提供锁排队机制
- 强一致性但性能相对较低

**4. 基于数据库的分布式锁**
- 利用数据库的唯一约束或行级锁
- 持久性好但性能较差

#### 9.3.2 Redis分布式锁实战实现

**基础Redis分布式锁实现：**
```go
package main

import (
    "context"
    "crypto/rand"
    "encoding/hex"
    "errors"
    "fmt"
    "log"
    "sync"
    "time"

    "github.com/go-redis/redis/v8"
)

// RedisLock Redis分布式锁结构体
type RedisLock struct {
    client     *redis.Client
    key        string        // 锁的键名
    value      string        // 锁的值（随机字符串）
    expiration time.Duration // 锁的过期时间
    mu         sync.Mutex    // 本地锁，保护并发操作
}

// NewRedisLock 创建新的Redis分布式锁
func NewRedisLock(client *redis.Client, key string, expiration time.Duration) *RedisLock {
    return &RedisLock{
        client:     client,
        key:        key,
        value:      generateRandomValue(),
        expiration: expiration,
    }
}

// 生成随机值，用于标识锁的所有者
func generateRandomValue() string {
    bytes := make([]byte, 16)
    if _, err := rand.Read(bytes); err != nil {
        return fmt.Sprintf("%d", time.Now().UnixNano())
    }
    return hex.EncodeToString(bytes)
}

// Lock 获取锁
func (r *RedisLock) Lock(ctx context.Context) error {
    r.mu.Lock()
    defer r.mu.Unlock()

    // 使用SET NX EX命令原子性地设置锁
    result, err := r.client.SetNX(ctx, r.key, r.value, r.expiration).Result()
    if err != nil {
        return fmt.Errorf("获取锁失败: %w", err)
    }

    if !result {
        return errors.New("锁已被其他进程持有")
    }

    return nil
}

// TryLock 尝试获取锁（非阻塞）
func (r *RedisLock) TryLock(ctx context.Context) bool {
    return r.Lock(ctx) == nil
}

// LockWithTimeout 带超时的获取锁
func (r *RedisLock) LockWithTimeout(ctx context.Context, timeout time.Duration) error {
    deadline := time.Now().Add(timeout)
    ticker := time.NewTicker(50 * time.Millisecond)
    defer ticker.Stop()

    for {
        select {
        case <-ctx.Done():
            return ctx.Err()
        case <-ticker.C:
            if time.Now().After(deadline) {
                return errors.New("获取锁超时")
            }

            if r.TryLock(ctx) {
                return nil
            }
        }
    }
}

// Unlock 释放锁
func (r *RedisLock) Unlock(ctx context.Context) error {
    r.mu.Lock()
    defer r.mu.Unlock()

    // 使用Lua脚本保证原子性释放锁
    script := `
        if redis.call("GET", KEYS[1]) == ARGV[1] then
            return redis.call("DEL", KEYS[1])
        else
            return 0
        end
    `

    result, err := r.client.Eval(ctx, script, []string{r.key}, r.value).Result()
    if err != nil {
        return fmt.Errorf("释放锁失败: %w", err)
    }

    if result.(int64) == 0 {
        return errors.New("锁不存在或不属于当前进程")
    }

    return nil
}

// Renew 续约锁的过期时间
func (r *RedisLock) Renew(ctx context.Context) error {
    r.mu.Lock()
    defer r.mu.Unlock()

    script := `
        if redis.call("GET", KEYS[1]) == ARGV[1] then
            return redis.call("EXPIRE", KEYS[1], ARGV[2])
        else
            return 0
        end
    `

    result, err := r.client.Eval(ctx, script, []string{r.key}, r.value, int64(r.expiration.Seconds())).Result()
    if err != nil {
        return fmt.Errorf("续约锁失败: %w", err)
    }

    if result.(int64) == 0 {
        return errors.New("锁不存在或不属于当前进程")
    }

    return nil
}

// IsLocked 检查锁是否被当前进程持有
func (r *RedisLock) IsLocked(ctx context.Context) (bool, error) {
    r.mu.Lock()
    defer r.mu.Unlock()

    value, err := r.client.Get(ctx, r.key).Result()
    if err != nil {
        if err == redis.Nil {
            return false, nil
        }
        return false, err
    }

    return value == r.value, nil
}

// GetTTL 获取锁的剩余时间
func (r *RedisLock) GetTTL(ctx context.Context) (time.Duration, error) {
    ttl, err := r.client.TTL(ctx, r.key).Result()
    if err != nil {
        return 0, err
    }

**高级Redis分布式锁实现（包含自动续约）：**
```go
// AdvancedRedisLock 高级Redis分布式锁，支持自动续约
type AdvancedRedisLock struct {
    *RedisLock
    autoRenew     bool
    renewInterval time.Duration
    stopRenew     chan struct{}
    renewMutex    sync.Mutex
}

// NewAdvancedRedisLock 创建高级Redis分布式锁
func NewAdvancedRedisLock(client *redis.Client, key string, expiration time.Duration) *AdvancedRedisLock {
    return &AdvancedRedisLock{
        RedisLock:     NewRedisLock(client, key, expiration),
        renewInterval: expiration / 3, // 续约间隔为过期时间的1/3
        stopRenew:     make(chan struct{}),
    }
}

// LockWithAutoRenew 获取锁并启动自动续约
func (a *AdvancedRedisLock) LockWithAutoRenew(ctx context.Context) error {
    if err := a.RedisLock.Lock(ctx); err != nil {
        return err
    }

    a.renewMutex.Lock()
    a.autoRenew = true
    a.renewMutex.Unlock()

    // 启动自动续约协程
    go a.autoRenewRoutine(ctx)

    return nil
}

// autoRenewRoutine 自动续约协程
func (a *AdvancedRedisLock) autoRenewRoutine(ctx context.Context) {
    ticker := time.NewTicker(a.renewInterval)
    defer ticker.Stop()

    for {
        select {
        case <-ctx.Done():
            return
        case <-a.stopRenew:
            return
        case <-ticker.C:
            a.renewMutex.Lock()
            if !a.autoRenew {
                a.renewMutex.Unlock()
                return
            }
            a.renewMutex.Unlock()

            if err := a.RedisLock.Renew(ctx); err != nil {
                log.Printf("自动续约锁失败: %v", err)
                return
            }
        }
    }
}

// Unlock 释放锁并停止自动续约
func (a *AdvancedRedisLock) Unlock(ctx context.Context) error {
    a.renewMutex.Lock()
    a.autoRenew = false
    a.renewMutex.Unlock()

    select {
    case a.stopRenew <- struct{}{}:
    default:
    }

    return a.RedisLock.Unlock(ctx)
}

// RedisLockManager 锁管理器
type RedisLockManager struct {
    client *redis.Client
    locks  map[string]*AdvancedRedisLock
    mu     sync.RWMutex
}

// NewRedisLockManager 创建锁管理器
func NewRedisLockManager(client *redis.Client) *RedisLockManager {
    return &RedisLockManager{
        client: client,
        locks:  make(map[string]*AdvancedRedisLock),
    }
}

// GetLock 获取或创建锁
func (m *RedisLockManager) GetLock(key string, expiration time.Duration) *AdvancedRedisLock {
    m.mu.Lock()
    defer m.mu.Unlock()

    if lock, exists := m.locks[key]; exists {
        return lock
    }

    lock := NewAdvancedRedisLock(m.client, key, expiration)
    m.locks[key] = lock
    return lock
}

// ReleaseLock 释放锁并从管理器中移除
func (m *RedisLockManager) ReleaseLock(ctx context.Context, key string) error {
    m.mu.Lock()
    lock, exists := m.locks[key]
    if exists {
        delete(m.locks, key)
    }
    m.mu.Unlock()

    if exists {
        return lock.Unlock(ctx)
    }
    return nil
}
```

#### 9.3.3 Etcd分布式锁实现

**基于Etcd的分布式锁实现：**
```go
package main

import (
    "context"
    "fmt"
    "log"
    "sync"
    "time"

    clientv3 "go.etcd.io/etcd/client/v3"
    "go.etcd.io/etcd/client/v3/concurrency"
)

// EtcdLock 基于Etcd的分布式锁
type EtcdLock struct {
    client  *clientv3.Client
    session *concurrency.Session
    mutex   *concurrency.Mutex
    key     string
    ttl     int
    mu      sync.Mutex
}

// NewEtcdLock 创建新的Etcd分布式锁
func NewEtcdLock(endpoints []string, key string, ttl int) (*EtcdLock, error) {
    client, err := clientv3.New(clientv3.Config{
        Endpoints:   endpoints,
        DialTimeout: 5 * time.Second,
    })
    if err != nil {
        return nil, fmt.Errorf("创建Etcd客户端失败: %w", err)
    }

    return &EtcdLock{
        client: client,
        key:    key,
        ttl:    ttl,
    }, nil
}

// Lock 获取锁
func (e *EtcdLock) Lock(ctx context.Context) error {
    e.mu.Lock()
    defer e.mu.Unlock()

    // 创建会话（带租约）
    session, err := concurrency.NewSession(e.client, concurrency.WithTTL(e.ttl))
    if err != nil {
        return fmt.Errorf("创建会话失败: %w", err)
    }
    e.session = session

    // 创建互斥锁
    e.mutex = concurrency.NewMutex(session, e.key)

    // 获取锁
    if err := e.mutex.Lock(ctx); err != nil {
        session.Close()
        return fmt.Errorf("获取锁失败: %w", err)
    }

    return nil
}

// TryLock 尝试获取锁（非阻塞）
func (e *EtcdLock) TryLock(ctx context.Context) error {
    e.mu.Lock()
    defer e.mu.Unlock()

    session, err := concurrency.NewSession(e.client, concurrency.WithTTL(e.ttl))
    if err != nil {
        return fmt.Errorf("创建会话失败: %w", err)
    }
    e.session = session

    e.mutex = concurrency.NewMutex(session, e.key)

    // 尝试获取锁（带超时）
    tryCtx, cancel := context.WithTimeout(ctx, 100*time.Millisecond)
    defer cancel()

    if err := e.mutex.Lock(tryCtx); err != nil {
        session.Close()
        if tryCtx.Err() == context.DeadlineExceeded {
            return fmt.Errorf("锁已被占用")
        }
        return fmt.Errorf("获取锁失败: %w", err)
    }

    return nil
}

// Unlock 释放锁
func (e *EtcdLock) Unlock(ctx context.Context) error {
    e.mu.Lock()
    defer e.mu.Unlock()

    if e.mutex == nil {
        return fmt.Errorf("锁未被持有")
    }

    err := e.mutex.Unlock(ctx)
    if err != nil {
        return fmt.Errorf("释放锁失败: %w", err)
    }

    if e.session != nil {
        e.session.Close()
        e.session = nil
    }
    e.mutex = nil

    return nil
}

// Close 关闭锁对象
func (e *EtcdLock) Close() error {
    if e.session != nil {
        e.session.Close()
    }
    return e.client.Close()
}

// KeepAlive 保持租约活跃
func (e *EtcdLock) KeepAlive(ctx context.Context) error {
    if e.session == nil {
        return fmt.Errorf("会话未初始化")
    }

    ch, kaerr := e.client.KeepAlive(ctx, e.session.Lease())
    if kaerr != nil {
        return fmt.Errorf("保持租约活跃失败: %w", kaerr)
    }

    go func() {
        for ka := range ch {
            log.Printf("租约续约成功: %v", ka)
        }
    }()

    return nil
}
```

#### 9.3.4 数据库分布式锁实现

**基于MySQL的分布式锁实现：**
```go
package main

import (
    "context"
    "database/sql"
    "errors"
    "fmt"
    "time"

    _ "github.com/go-sql-driver/mysql"
)

// MySQLLock 基于MySQL的分布式锁
type MySQLLock struct {
    db        *sql.DB
    lockName  string
    timeout   time.Duration
    conn      *sql.Conn // 专用连接，保持锁的会话
}

// NewMySQLLock 创建新的MySQL分布式锁
func NewMySQLLock(dsn, lockName string, timeout time.Duration) (*MySQLLock, error) {
    db, err := sql.Open("mysql", dsn)
    if err != nil {
        return nil, fmt.Errorf("连接数据库失败: %w", err)
    }

    return &MySQLLock{
        db:       db,
        lockName: lockName,
        timeout:  timeout,
    }, nil
}

// Lock 获取锁（使用MySQL的GET_LOCK函数）
func (m *MySQLLock) Lock(ctx context.Context) error {
    conn, err := m.db.Conn(ctx)
    if err != nil {
        return fmt.Errorf("获取数据库连接失败: %w", err)
    }
    m.conn = conn

    query := "SELECT GET_LOCK(?, ?)"
    var result sql.NullInt64
    
    err = conn.QueryRowContext(ctx, query, m.lockName, int(m.timeout.Seconds())).Scan(&result)
    if err != nil {
        conn.Close()
        return fmt.Errorf("执行GET_LOCK失败: %w", err)
    }

    if !result.Valid || result.Int64 != 1 {
        conn.Close()
        return errors.New("获取锁失败或超时")
    }

    return nil
}
```

#### 9.3.5 分布式锁实战示例

**统一的分布式锁接口：**
```go
// DistributedLock 分布式锁接口
type DistributedLock interface {
    Lock(ctx context.Context) error
    TryLock(ctx context.Context) error
    Unlock(ctx context.Context) error
}

// LockManager 锁管理器接口
type LockManager interface {
    NewLock(key string, opts ...LockOption) DistributedLock

}

// LockOption 锁配置选项
type LockOption func(*LockConfig)

type LockConfig struct {
    TTL         time.Duration
    RetryDelay  time.Duration
    MaxRetries  int
    AutoRenew   bool
}

// WithTTL 设置锁的TTL
func WithTTL(ttl time.Duration) LockOption {
    return func(c *LockConfig) {
        c.TTL = ttl
    }
}

// WithRetry 设置重试参数
func WithRetry(delay time.Duration, maxRetries int) LockOption {
    return func(c *LockConfig) {
        c.RetryDelay = delay
        c.MaxRetries = maxRetries
    }
}

// WithAutoRenew 设置自动续约
func WithAutoRenew(enable bool) LockOption {
    return func(c *LockConfig) {
        c.AutoRenew = enable
    }
}
```

**实战应用示例：**
```go
func main() {
    ctx := context.Background()
    
    // 1. Redis分布式锁示例
    rdb := redis.NewClient(&redis.Options{
        Addr: "localhost:6379",
    })
    
    redisLock := NewAdvancedRedisLock(rdb, "order:12345", 30*time.Second)
    
    if err := redisLock.LockWithAutoRenew(ctx); err != nil {
        log.Printf("Redis锁获取失败: %v", err)
        return
    }
    defer redisLock.Unlock(ctx)
    
    fmt.Println("执行业务逻辑...")
    time.Sleep(5 * time.Second)
    
    // 2. 不同类型锁的性能比较
    performanceBenchmark()
}

func performanceBenchmark() {
    fmt.Println("\n=== 分布式锁性能比较 ===")
    
    ctx := context.Background()
    iterations := 100
    
    // Redis锁性能测试
    rdb := redis.NewClient(&redis.Options{Addr: "localhost:6379"})
    
    start := time.Now()
    for i := 0; i < iterations; i++ {
        lock := NewRedisLock(rdb, fmt.Sprintf("bench:redis:%d", i), 10*time.Second)
        lock.Lock(ctx)
        lock.Unlock(ctx)
    }
    redisTime := time.Since(start)
    
    fmt.Printf("Redis锁 %d 次操作耗时: %v (%.2fms/op)\n", 
        iterations, redisTime, float64(redisTime.Nanoseconds())/float64(iterations)/1e6)
}
```

**Q: 如何在Go中实现基于Redis的分布式锁？**

#### 分布式锁实现

```go
// 分布式锁
type DistributedLock struct {
    client     *redis.Client
    key        string
    value      string
    expiration time.Duration
    ctx        context.Context
}

func NewDistributedLock(client *redis.Client, key string) *DistributedLock {
    return &DistributedLock{
        client:     client,
        key:        key,
        value:      generateUUID(), // 随机值
        expiration: 30 * time.Second,
        ctx:        context.Background(),
    }
}

// 获取锁
func (l *DistributedLock) Lock() error {
    success, err := l.client.SetNX(l.ctx, l.key, l.value, l.expiration).Result()
    if err != nil {
        return err
    }
    if !success {
        return fmt.Errorf("锁已被其他进程获取")
    }
    return nil
}

// 释放锁（Lua脚本保证原子性）
func (l *DistributedLock) Unlock() error {
    script := `
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
    `
    
    result, err := l.client.Eval(l.ctx, script, []string{l.key}, l.value).Result()
    if err != nil {
        return err
    }
    
    if result.(int64) == 0 {
        return fmt.Errorf("锁不存在或不属于当前进程")
    }
    return nil
}

// 使用示例
func ExampleLock() {
    client := redis.NewClient(&redis.Options{Addr: "localhost:6379"})
    lock := NewDistributedLock(client, "resource:lock")
    
    if err := lock.Lock(); err != nil {
        log.Printf("获取锁失败: %v", err)
        return
    }
    defer lock.Unlock()
    
    // 执行业务逻辑
    fmt.Println("正在执行业务逻辑...")
    time.Sleep(2 * time.Second)
}
```

#### 缓存模式

```go
// 缓存服务
type CacheService struct {
    client *redis.Client
    ctx    context.Context
}

// 获取或设置缓存
func (c *CacheService) GetOrSet(key string, fetchFunc func() (string, error)) (string, error) {
    // 先从缓存获取
    val, err := c.client.Get(c.ctx, key).Result()
    if err == nil {
        return val, nil
    }
    
    if err != redis.Nil {
        return "", err
    }
    
    // 缓存未命中，从数据源获取
    data, err := fetchFunc()
    if err != nil {
        return "", err
    }
    
    // 设置缓存（加随机时间防止雪崩）
    ttl := time.Hour + time.Duration(rand.Intn(300))*time.Second
    c.client.Set(c.ctx, key, data, ttl)
    
    return data, nil
}

// 布隆过滤器简单实现
type BloomFilter struct {
    client *redis.Client
    key    string
}

func (bf *BloomFilter) Add(item string) error {
    hash1 := bf.hash1(item)
    hash2 := bf.hash2(item)
    
    pipe := bf.client.Pipeline()
    pipe.SetBit(context.Background(), bf.key, int64(hash1), 1)
    pipe.SetBit(context.Background(), bf.key, int64(hash2), 1)
    _, err := pipe.Exec(context.Background())
    
    return err
}

func (bf *BloomFilter) Contains(item string) (bool, error) {
    hash1 := bf.hash1(item)
    hash2 := bf.hash2(item)
    
    pipe := bf.client.Pipeline()
    cmd1 := pipe.GetBit(context.Background(), bf.key, int64(hash1))
    cmd2 := pipe.GetBit(context.Background(), bf.key, int64(hash2))
    _, err := pipe.Exec(context.Background())
    
    if err != nil {
        return false, err
    }
    
    return cmd1.Val() == 1 && cmd2.Val() == 1, nil
}

func (bf *BloomFilter) hash1(s string) uint32 {
    // FNV-1a hash
    hash := uint32(2166136261)
    for _, c := range []byte(s) {
        hash ^= uint32(c)
        hash *= 16777619
    }
    return hash % 1000000
}

func (bf *BloomFilter) hash2(s string) uint32 {
    // Simple hash
    hash := uint32(0)
    for _, c := range []byte(s) {
        hash = hash*31 + uint32(c)
    }
    return hash % 1000000
}
```

#### 集群支持

```go
// Redis集群客户端
func NewRedisClusterClient() *redis.ClusterClient {
    return redis.NewClusterClient(&redis.ClusterOptions{
        Addrs: []string{
            "127.0.0.1:7000",
            "127.0.0.1:7001",
            "127.0.0.1:7002",
        },
        PoolSize:     10,
        MaxRedirects: 3,
        DialTimeout:  5 * time.Second,
    })
}

// 集群操作示例
func (r *RedisService) ClusterOperations() {
    // 使用HashTag确保相关key在同一节点
    userId := "1001"
    
    // 使用{}包围的部分作为Hash Tag
    profileKey := fmt.Sprintf("user:{%s}:profile", userId)
    settingsKey := fmt.Sprintf("user:{%s}:settings", userId)
    
    r.client.HMSet(r.ctx, profileKey, map[string]interface{}{
        "name": "张三",
        "age":  25,
    })
    
    r.client.HMSet(r.ctx, settingsKey, map[string]interface{}{
        "theme":    "dark",
        "language": "zh-CN",
    })
}

func generateUUID() string {
    return fmt.Sprintf("%d-%d", time.Now().UnixNano(), rand.Intn(10000))
}
```

**常见问题和最佳实践**：

1. **连接池优化**：合理设置 PoolSize、MinIdleConns
2. **错误处理**：区分 redis.Nil 和其他错误
3. **批量操作**：使用 Pipeline 提高性能
4. **超时控制**：合理设置各种超时参数
5. **缓存策略**：防止穿透、击穿、雪崩

#### 9.3.7 Redis分布式锁的缺陷与改进方案

##### 9.3.7.1 SET EXPIRE原子性问题

早期实现中SET和EXPIRE分离操作可能导致死锁：
```go
// 有问题的实现
func (r *RedisLock) BadLock() error {
    // 步骤1：设置键值
    success := r.client.SetNX(r.ctx, r.key, r.value, 0)
    if !success.Val() {
        return errors.New("获取锁失败")
    }
    
    // 步骤2：设置过期时间（如果这里失败，锁永不过期！）
    _, err := r.client.Expire(r.ctx, r.key, r.expiration).Result()
    if err != nil {
        // 已经设置了锁，但过期时间设置失败 - 造成死锁！
        return fmt.Errorf("设置过期时间失败: %w", err)
    }
    
    return nil
}

// 正确的原子操作实现
func (r *RedisLock) GoodLock() error {
    // SET key value EX seconds NX - 原子操作
    result := r.client.SetNX(r.ctx, r.key, r.value, r.expiration)
    if !result.Val() {
        return errors.New("锁已被占用")
    }
    return nil
}
```

##### 9.3.7.2 续期失败的复杂性问题

```go
// 续期失败处理机制
type RenewFailureHandler struct {
    renewFails    int
    maxFails      int
    isValid       bool
    mutex         sync.RWMutex
}

func (r *RenewFailureHandler) HandleRenewFailure(lockKey string, err error) {
    r.mutex.Lock()
    defer r.mutex.Unlock()
    
    r.renewFails++
    log.Warnf("锁续期失败，失败次数: %d, 锁: %s, 错误: %v", r.renewFails, lockKey, err)
    
    if r.renewFails >= r.maxFails {
        r.isValid = false
        log.Errorf("锁续期连续失败%d次，标记锁为无效: %s", r.maxFails, lockKey)
        
        // 通知业务层停止使用锁
        r.notifyLockInvalid(lockKey)
    }
}

func (r *RenewFailureHandler) IsLockValid() bool {
    r.mutex.RLock()
    defer r.mutex.RUnlock()
    return r.isValid
}

func (r *RenewFailureHandler) notifyLockInvalid(lockKey string) {
    // 发送告警或通知
    // 可以通过监听器模式通知业务层
}

// 改进的续期实现
func (r *RedisLock) SafeRenew() error {
    script := `
        if redis.call('GET', KEYS[1]) == ARGV[1] then
            return redis.call('EXPIRE', KEYS[1], ARGV[2])
        else
            return 0
        end
    `
    
    // 添加续期超时控制
    ctx, cancel := context.WithTimeout(r.ctx, 2*time.Second)
    defer cancel()
    
    result, err := r.client.Eval(ctx, script, []string{r.key}, r.value, int64(r.expiration.Seconds())).Result()
    if err != nil {
        return fmt.Errorf("续期操作失败: %w", err)
    }
    
    if result.(int64) == 0 {
        return errors.New("续期失败：锁不存在或不属于当前进程")
    }
    
    return nil
}
```

##### 9.3.7.3 网络分区和脑裂问题

```go
// Redlock算法解决脑裂问题
type RedlockManager struct {
    clients []*redis.Client
    quorum  int
}

func NewRedlockManager(endpoints []string) *RedlockManager {
    clients := make([]*redis.Client, len(endpoints))
    for i, endpoint := range endpoints {
        clients[i] = redis.NewClient(&redis.Options{
            Addr: endpoint,
        })
    }
    
    return &RedlockManager{
        clients: clients,
        quorum:  len(clients)/2 + 1,
    }
}

func (r *RedlockManager) AcquireLock(key, value string, expiry time.Duration) bool {
    successCount := 0
    startTime := time.Now()
    
    // 在多个Redis实例上获取锁
    for _, client := range r.clients {
        ctx, cancel := context.WithTimeout(context.Background(), time.Second)
        if client.SetNX(ctx, key, value, expiry).Val() {
            successCount++
        }
        cancel()
    }
    
    // 检查是否达到法定人数
    elapsedTime := time.Since(startTime)
    validTime := expiry - elapsedTime - 100*time.Millisecond
    
    if successCount >= r.quorum && validTime > 0 {
        return true
    }
    
    // 获取失败，释放已获得的锁
    r.ReleaseLock(key, value)
    return false
}

func (r *RedlockManager) ReleaseLock(key, value string) {
    script := `
        if redis.call('GET', KEYS[1]) == ARGV[1] then
            return redis.call('DEL', KEYS[1])
        else
            return 0
        end
    `
    
    for _, client := range r.clients {
        ctx, cancel := context.WithTimeout(context.Background(), time.Second)
        client.Eval(ctx, script, []string{key}, value)
        cancel()
    }
}
```

##### 9.3.7.4 时钟漂移问题

```go
// 考虑时钟漂移的安全锁
type ClockSafeLock struct {
    *RedisLock
    clockDrift time.Duration
}

func NewClockSafeLock(client *redis.Client, key string, expiration time.Duration) *ClockSafeLock {
    return &ClockSafeLock{
        RedisLock:  NewRedisLock(client, key, expiration),
        clockDrift: 2 * time.Second, // 容忍2秒时钟漂移
    }
}

func (c *ClockSafeLock) SafeLock() error {
    // 减少锁有效期以应对时钟漂移
    safeExpiry := c.expiration - c.clockDrift*2
    if safeExpiry <= 0 {
        return errors.New("锁有效期太短，无法容忍时钟漂移")
    }
    
    result := c.client.SetNX(c.ctx, c.key, c.value, safeExpiry)
    if !result.Val() {
        return errors.New("锁已被占用")
    }
    return nil
}

// 时钟同步检查
func (c *ClockSafeLock) CheckClockSync() error {
    // 可以通过NTP服务检查时钟同步状态
    localTime := time.Now().Unix()
    
    // 从Redis获取服务器时间（Redis TIME命令）
    timeResult, err := c.client.Time(c.ctx).Result()
    if err != nil {
        return fmt.Errorf("获取Redis服务器时间失败: %w", err)
    }
    
    redisTime := timeResult.Unix()
    timeDiff := abs(localTime - redisTime)
    
    if timeDiff > int64(c.clockDrift.Seconds()) {
        return fmt.Errorf("时钟漂移过大: %d秒", timeDiff)
    }
    
    return nil
}

func abs(x int64) int64 {
    if x < 0 {
        return -x
    }
    return x
}
```

##### 9.3.7.5 锁重入性问题

```go
// 可重入Redis锁实现
type ReentrantRedisLock struct {
    *RedisLock
    holdCount int
    mutex     sync.Mutex
}

func (r *ReentrantRedisLock) ReentrantLock() error {
    r.mutex.Lock()
    defer r.mutex.Unlock()
    
    if r.holdCount > 0 {
        // 已经持有锁，增加计数
        r.holdCount++
        return nil
    }
    
    // 第一次获取锁
    if err := r.RedisLock.Lock(); err != nil {
        return err
    }
    
    r.holdCount = 1
    return nil
}

func (r *ReentrantRedisLock) ReentrantUnlock() error {
    r.mutex.Lock()
    defer r.mutex.Unlock()
    
    if r.holdCount <= 0 {
        return errors.New("未持有锁")
    }
    
    r.holdCount--
    if r.holdCount == 0 {
        // 完全释放锁
        return r.RedisLock.Unlock()
    }
    
    return nil
}
```

##### 9.3.7.6 性能优化建议

```go
// 高性能Redis锁实现
type HighPerformanceRedisLock struct {
    *RedisLock
    pipeline redis.Pipeliner
    pool     *sync.Pool
}

func NewHighPerformanceRedisLock(client *redis.Client, key string, expiration time.Duration) *HighPerformanceRedisLock {
    return &HighPerformanceRedisLock{
        RedisLock: NewRedisLock(client, key, expiration),
        pool: &sync.Pool{
            New: func() interface{} {
                return make([]interface{}, 0, 2)
            },
        },
    }
}

// 批量操作优化
func (h *HighPerformanceRedisLock) BatchLock(keys []string) ([]bool, error) {
    pipe := h.client.Pipeline()
    defer pipe.Close()
    
    commands := make([]*redis.BoolCmd, len(keys))
    
    // 批量提交SET NX命令
    for i, key := range keys {
        commands[i] = pipe.SetNX(h.ctx, key, h.value, h.expiration)
    }
    
    _, err := pipe.Exec(h.ctx)
    if err != nil {
        return nil, err
    }
    
    // 收集结果
    results := make([]bool, len(keys))
    for i, cmd := range commands {
        results[i] = cmd.Val()
    }
    
    return results, nil
}
```

**最佳实践总结**：

1. **原子性操作**：始终使用SET NX EX等原子命令
2. **续期监控**：监控续期成功率，及时发现网络问题
3. **时钟同步**：确保各服务器时钟同步，或预留时钟漂移容忍度
4. **网络分区**：考虑使用Redlock算法应对脑裂问题
5. **异常处理**：完善的异常处理和降级机制
6. **监控告警**：建立完善的锁监控和告警机制
7. **性能权衡**：根据业务需求选择合适的一致性级别
