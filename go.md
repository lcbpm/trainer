# Go 高级面试题完整整理

## 📋 目录

- [1. 并发编程 (Concurrency)](#1-并发编程-concurrency)
  - [1.1 Goroutine 相关](#11-goroutine-相关)
  - [1.2 Channel 相关](#12-channel-相关)
  - [1.3 经典并发编程代码题](#13-经典并发编程代码题)
- [2. 内存管理](#2-内存管理)
  - [2.1 垃圾回收](#21-垃圾回收)
  - [2.2 内存逃逸](#22-内存逃逸)
  - [2.3 内存和性能优化实例](#23-内存和性能优化实例)
- [3. 类型系统](#3-类型系统)
  - [3.1 接口](#31-接口)
  - [3.2 反射](#32-反射)
  - [3.3 接口和类型系统代码题](#33-接口和类型系统代码题)
- [4. 并发安全](#4-并发安全)
  - [4.1 同步原语](#41-同步原语)
  - [4.2 原子操作](#42-原子操作)
  - [4.3 同步原语代码实例](#43-同步原语代码实例)
- [5. 性能优化](#5-性能优化)
  - [5.1 编译优化](#51-编译优化)
  - [5.2 代码优化](#52-代码优化)
  - [5.3 性能分析实战](#53-性能分析实战)
- [6. 错误处理](#6-错误处理)
  - [6.1 错误处理理论](#61-错误处理理论)
  - [6.2 错误处理实践](#62-错误处理实践)
- [7. 包管理和模块](#7-包管理和模块)
- [8. 网络编程](#8-网络编程)
  - [8.1 网络模型](#81-网络模型)
  - [8.2 Channel 高级使用模式](#82-channel-高级使用模式)
- [9. 测试](#9-测试)
- [10. 实际应用场景](#10-实际应用场景)

---

## 1. 并发编程 (Concurrency)

### 1.1 Goroutine 相关
**Q: 解释Goroutine的调度原理，GMP模型是什么？**
- G（Goroutine）：用户态轻量级线程
- M（Machine）：系统线程
- P（Processor）：逻辑处理器，管理G的执行
- 工作窃取算法（work-stealing）

#### GMP模型详细实战分析

**GMP模型核心组件：**
```go
// 模拟GMP模型的核心结构
type G struct {
    stack       []byte    // goroutine的栈空间
    stackguard0 uintptr   // 栈溢出检查
    m           *M        // 当前运行在哪个M上
    sched       gobuf     // 调度相关的寄存器
    status      uint32    // goroutine状态
}

type M struct {
    g0      *G     // 调度器goroutine
    curg    *G     // 当前正在运行的goroutine
    p       *P     // 关联的P
    nextp   *P     // 即将关联的P
    spinning bool  // 是否在自旋等待工作
}

type P struct {
    id       int32    // P的ID
    status   uint32   // P的状态
    runq     [256]*G  // 本地运行队列
    runqhead uint32   // 队列头
    runqtail uint32   // 队列尾
    runnext  *G       // 下一个要运行的G
}
```

**调度器工作流程实战示例：**
```go
package main

import (
    "fmt"
    "runtime"
    "sync"
    "time"
)

// 模拟CPU密集型任务
func cpuIntensiveTask(id int, wg *sync.WaitGroup) {
    defer wg.Done()
    
    // 模拟计算密集型任务
    for i := 0; i < 1000000; i++ {
        _ = i * i
    }
    
    fmt.Printf("Task %d completed on goroutine, P: %d\n", 
        id, runtime.NumCPU())
}

// 模拟I/O阻塞任务
func ioBlockingTask(id int, wg *sync.WaitGroup) {
    defer wg.Done()
    
    // 模拟I/O阻塞
    time.Sleep(100 * time.Millisecond)
    
    fmt.Printf("I/O Task %d completed\n", id)
}

// 演示工作窃取算法
func demonstrateWorkStealing() {
    // 设置GOMAXPROCS
    numCPU := runtime.NumCPU()
    runtime.GOMAXPROCS(numCPU)
    
    fmt.Printf("系统CPU核心数: %d\n", numCPU)
    fmt.Printf("当前GOMAXPROCS: %d\n", runtime.GOMAXPROCS(0))
    
    var wg sync.WaitGroup
    
    // 创建大量goroutine来观察负载均衡
    numTasks := 20
    
    start := time.Now()
    
    // 混合CPU密集型和I/O密集型任务
    for i := 0; i < numTasks; i++ {
        wg.Add(2)
        
        // CPU密集型任务
        go cpuIntensiveTask(i, &wg)
        
        // I/O密集型任务
        go ioBlockingTask(i, &wg)
    }
    
    wg.Wait()
    
    elapsed := time.Since(start)
    fmt.Printf("总执行时间: %v\n", elapsed)
    fmt.Printf("当前goroutine数量: %d\n", runtime.NumGoroutine())
}

// 监控goroutine调度情况
func monitorScheduler() {
    ticker := time.NewTicker(100 * time.Millisecond)
    defer ticker.Stop()
    
    for i := 0; i < 10; i++ {
        select {
        case <-ticker.C:
            var m runtime.MemStats
            runtime.ReadMemStats(&m)
            
            fmt.Printf("Goroutines: %d, OS Threads: %d\n", 
                runtime.NumGoroutine(), runtime.GOMAXPROCS(0))
        }
    }
}

func main() {
    fmt.Println("=== GMP模型调度演示 ===")
    
    // 启动监控
    go monitorScheduler()
    
    // 演示工作窃取
    demonstrateWorkStealing()
    
    time.Sleep(1 * time.Second)
}
```

**Q: Goroutine泄露的原因和如何检测？**
- 原因：无限循环、阻塞的channel操作、未正确关闭的资源
- 检测：runtime.NumGoroutine()、pprof工具

#### Goroutine泄露检测和防护实战

**常见泄露场景和解决方案：**
```go
package main

import (
    "context"
    "fmt"
    "runtime"
    "sync"
    "time"
)

// 场景1：无缓冲channel导致的泄露
func leakyChannelExample() {
    fmt.Println("\n=== 泄露案例：无缓冲channel ===")
    
    initialGoroutines := runtime.NumGoroutine()
    fmt.Printf("初始goroutine数量: %d\n", initialGoroutines)
    
    // 错误示例：goroutine会永远阻塞
    ch := make(chan int)
    
    for i := 0; i < 10; i++ {
        go func(id int) {
            // 这里会永远阻塞，因为没有接收者
            ch <- id
            fmt.Printf("Goroutine %d finished\n", id)
        }(i)
    }
    
    time.Sleep(100 * time.Millisecond)
    fmt.Printf("执行后goroutine数量: %d (泄露了 %d 个)\n", 
        runtime.NumGoroutine(), 
        runtime.NumGoroutine()-initialGoroutines)
}

// 场景1修复：使用context或缓冲channel
func fixedChannelExample() {
    fmt.Println("\n=== 修复方案：使用context控制 ===")
    
    initialGoroutines := runtime.NumGoroutine()
    ctx, cancel := context.WithTimeout(context.Background(), 200*time.Millisecond)
    defer cancel()
    
    ch := make(chan int)
    var wg sync.WaitGroup
    
    // 启动接收者
    wg.Add(1)
    go func() {
        defer wg.Done()
        for {
            select {
            case val := <-ch:
                fmt.Printf("接收到值: %d\n", val)
            case <-ctx.Done():
                fmt.Println("接收者退出")
                return
            }
        }
    }()
    
    // 启动发送者
    for i := 0; i < 5; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            select {
            case ch <- id:
                fmt.Printf("发送值 %d 成功\n", id)
            case <-ctx.Done():
                fmt.Printf("发送者 %d 退出\n", id)
            }
        }(i)
    }
    
    wg.Wait()
    fmt.Printf("最终goroutine数量: %d\n", runtime.NumGoroutine())
}

// 场景2：HTTP请求没有设置超时
func httpTimeoutExample() {
    fmt.Println("\n=== HTTP超时控制示例 ===")
    
    type HTTPClient struct {
        client *http.Client
    }
    
    // 正确的HTTP客户端配置
    httpClient := &HTTPClient{
        client: &http.Client{
            Timeout: 5 * time.Second,
            Transport: &http.Transport{
                MaxIdleConns:        100,
                MaxIdleConnsPerHost: 10,
                IdleConnTimeout:     90 * time.Second,
            },
        },
    }
    
    // 带context的请求
    func (h *HTTPClient) GetWithContext(ctx context.Context, url string) error {
        req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
        if err != nil {
            return err
        }
        
        resp, err := h.client.Do(req)
        if err != nil {
            return err
        }
        defer resp.Body.Close()
        
        return nil
    }
}

// Goroutine泄露检测工具
type GoroutineMonitor struct {
    baseline int
    mu       sync.RWMutex
}

func NewGoroutineMonitor() *GoroutineMonitor {
    return &GoroutineMonitor{
        baseline: runtime.NumGoroutine(),
    }
}

func (g *GoroutineMonitor) CheckLeak() bool {
    g.mu.RLock()
    defer g.mu.RUnlock()
    
    current := runtime.NumGoroutine()
    leaked := current - g.baseline
    
    if leaked > 0 {
        fmt.Printf("⚠️  检测到goroutine泄露: %d 个\n", leaked)
        return true
    }
    
    return false
}

func (g *GoroutineMonitor) UpdateBaseline() {
    g.mu.Lock()
    defer g.mu.Unlock()
    g.baseline = runtime.NumGoroutine()
}

// 自动goroutine泄露检测
func autoLeakDetection() {
    fmt.Println("\n=== 自动泄露检测 ===")
    
    monitor := NewGoroutineMonitor()
    
    // 定期检测
    ticker := time.NewTicker(1 * time.Second)
    defer ticker.Stop()
    
    done := make(chan bool)
    
    go func() {
        for {
            select {
            case <-ticker.C:
                if monitor.CheckLeak() {
                    // 发现泄露时可以触发告警、记录日志等
                    fmt.Println("触发泄露告警处理...")
                }
            case <-done:
                return
            }
        }
    }()
    
    // 模拟一些工作负载
    time.Sleep(3 * time.Second)
    done <- true
}

func main() {
    // 演示各种泄露场景
    leakyChannelExample()
    fixedChannelExample()
    autoLeakDetection()
}
```

### 1.2 Channel 相关
**Q: 有缓冲和无缓冲channel的区别？**
- 无缓冲：同步通信，发送和接收必须同时准备好
- 有缓冲：异步通信，可以存储一定数量的值

**Q: Channel的关闭规则和最佳实践？**
- 只有发送方关闭channel
- 关闭后仍可读取，但不能写入

#### Channel深度实战分析

**Channel底层原理和性能特性：**
```go
package main

import (
    "fmt"
    "sync"
    "time"
    "unsafe"
)

// Channel的底层结构简化示意
type hchan struct {
    qcount   uint           // 当前队列中的元素数量
    dataqsiz uint           // 缓冲区大小
    buf      unsafe.Pointer // 缓冲区数据指针
    elemsize uint16         // 元素大小
    sendx    uint           // 发送索引
    recvx    uint           // 接收索引
    recvq    waitq          // 等待接收的goroutine队列
    sendq    waitq          // 等待发送的goroutine队列
    lock     mutex          // 保护并发访问
}

// 演示无缓冲channel的同步特性
func demonstrateUnbufferedChannel() {
    fmt.Println("\n=== 无缓冲Channel同步特性 ===")
    
    ch := make(chan int)
    
    var wg sync.WaitGroup
    
    // 发送者
    wg.Add(1)
    go func() {
        defer wg.Done()
        for i := 0; i < 5; i++ {
            fmt.Printf("准备发送: %d\n", i)
            start := time.Now()
            ch <- i  // 在没有接收者时会阻塞
            fmt.Printf("发送完成: %d (耗时: %v)\n", i, time.Since(start))
        }
        close(ch)
    }()
    
    // 接收者（延迟启动）
    wg.Add(1)
    go func() {
        defer wg.Done()
        time.Sleep(100 * time.Millisecond) // 模拟延迟
        
        for val := range ch {
            fmt.Printf("接收到: %d\n", val)
            time.Sleep(50 * time.Millisecond) // 模拟处理时间
        }
    }()
    
    wg.Wait()
}

// 演示有缓冲channel的异步特性
func demonstrateBufferedChannel() {
    fmt.Println("\n=== 有缓冲Channel异步特性 ===")
    
    ch := make(chan int, 3) // 缓冲区大小为3
    
    var wg sync.WaitGroup
    
    // 发送者
    wg.Add(1)
    go func() {
        defer wg.Done()
        for i := 0; i < 6; i++ {
            start := time.Now()
            ch <- i
            fmt.Printf("发送: %d (耗时: %v, 缓冲区状态: %d/%d)\n", 
                i, time.Since(start), len(ch), cap(ch))
            time.Sleep(30 * time.Millisecond)
        }
        close(ch)
    }()
    
    // 接收者（延迟启动）
    wg.Add(1)
    go func() {
        defer wg.Done()
        time.Sleep(200 * time.Millisecond) // 让缓冲区先填满
        
        for val := range ch {
            fmt.Printf("接收: %d (缓冲区状态: %d/%d)\n", 
                val, len(ch), cap(ch))
            time.Sleep(80 * time.Millisecond)
        }
    }()
    
    wg.Wait()
}

// Channel的select多路复用
func demonstrateChannelSelect() {
    fmt.Println("\n=== Channel Select多路复用 ===")
    
    ch1 := make(chan string)
    ch2 := make(chan string)
    timeout := make(chan bool, 1)
    
    // 模拟不同速度的数据源
    go func() {
        time.Sleep(100 * time.Millisecond)
        ch1 <- "快速数据源"
    }()
    
    go func() {
        time.Sleep(300 * time.Millisecond)
        ch2 <- "慢速数据源"
    }()
    
    // 设置超时
    go func() {
        time.Sleep(200 * time.Millisecond)
        timeout <- true
    }()
    
    // 非阻塞select模式
    for i := 0; i < 5; i++ {
        select {
        case msg1 := <-ch1:
            fmt.Printf("从 ch1 接收: %s\n", msg1)
        case msg2 := <-ch2:
            fmt.Printf("从 ch2 接收: %s\n", msg2)
        case <-timeout:
            fmt.Println("超时，操作取消")
            return
        default:
            fmt.Printf("第 %d 次轮询: 暂无数据\n", i+1)
            time.Sleep(50 * time.Millisecond)
        }
    }
}

// 生产者-消费者模式的性能优化
func optimizedProducerConsumer() {
    fmt.Println("\n=== 优化的生产者-消费者模式 ===")
    
    const (
        numProducers = 3
        numConsumers = 2
        bufferSize   = 10
        numTasks     = 20
    )
    
    taskCh := make(chan int, bufferSize)
    resultCh := make(chan int, bufferSize)
    
    var wg sync.WaitGroup
    
    // 生产者
    for i := 0; i < numProducers; i++ {
        wg.Add(1)
        go func(producerID int) {
            defer wg.Done()
            for j := 0; j < numTasks/numProducers; j++ {
                task := producerID*100 + j
                taskCh <- task
                fmt.Printf("生产者 %d 生产任务: %d\n", producerID, task)
                time.Sleep(10 * time.Millisecond)
            }
        }(i)
    }
    
    // 关闭任务通道
    go func() {
        wg.Wait()
        close(taskCh)
    }()
    
    // 消费者
    var consumerWg sync.WaitGroup
    for i := 0; i < numConsumers; i++ {
        consumerWg.Add(1)
        go func(consumerID int) {
            defer consumerWg.Done()
            for task := range taskCh {
                // 模拟任务处理
                result := task * 2
                resultCh <- result
                fmt.Printf("消费者 %d 处理任务 %d -> 结果 %d\n", 
                    consumerID, task, result)
                time.Sleep(20 * time.Millisecond)
            }
        }(i)
    }
    
    // 关闭结果通道
    go func() {
        consumerWg.Wait()
        close(resultCh)
    }()
    
    // 结果收集器
    go func() {
        var results []int
        for result := range resultCh {
            results = append(results, result)
        }
        fmt.Printf("收集到 %d 个结果\n", len(results))
    }()
    
    // 等待所有生产者完成
    wg.Wait()
    
    // 等待所有消费者完成
    consumerWg.Wait()
}

// Channel关闭的最佳实践
func channelClosingBestPractices() {
    fmt.Println("\n=== Channel关闭最佳实践 ===")
    
    // 1. 只有发送方关闭channel
    // 2. 使用信号channel通知关闭
    // 3. 使用sync.Once确保只关闭一次
    
    dataCh := make(chan int, 5)
    stopCh := make(chan struct{})
    var closeOnce sync.Once
    
    // 发送者
    go func() {
        defer func() {
            closeOnce.Do(func() {
                close(dataCh)
                fmt.Println("数据通道已关闭")
            })
        }()
        
        for i := 0; i < 10; i++ {
            select {
            case dataCh <- i:
                fmt.Printf("发送数据: %d\n", i)
                time.Sleep(50 * time.Millisecond)
            case <-stopCh:
                fmt.Println("接收到停止信号，发送者退出")
                return
            }
        }
    }()
    
    // 接收者
    go func() {
        for {
            select {
            case data, ok := <-dataCh:
                if !ok {
                    fmt.Println("数据通道已关闭，接收者退出")
                    return
                }
                fmt.Printf("接收数据: %d\n", data)
                
                // 模拟一些情况下的提前退出
                if data == 3 {
                    fmt.Println("接收者提前退出")
                    close(stopCh)
                    return
                }
            }
        }
    }()
    
    time.Sleep(1 * time.Second)
}

func main() {
    demonstrateUnbufferedChannel()
    demonstrateBufferedChannel() 
    demonstrateChannelSelect()
    optimizedProducerConsumer()
    channelClosingBestPractices()
}
```
### 1.3 经典并发编程代码题

#### 生产者消费者模式
```go
// 实现一个线程安全的缓冲区
type Buffer struct {
    data chan int
    size int
}

func NewBuffer(size int) *Buffer {
    return &Buffer{
        data: make(chan int, size),
        size: size,
    }
}

func (b *Buffer) Put(item int) error {
    select {
    case b.data <- item:
        return nil
    default:
        return errors.New("buffer full")
    }
}

func (b *Buffer) Get() (int, error) {
    select {
    case item := <-b.data:
        return item, nil
    default:
        return 0, errors.New("buffer empty")
    }
}
```

#### Worker Pool 模式
```go
type WorkerPool struct {
    tasks    chan Task
    workers  int
    quit     chan bool
}

type Task func()

func NewWorkerPool(workers int) *WorkerPool {
    return &WorkerPool{
        tasks:   make(chan Task),
        workers: workers,
        quit:    make(chan bool),
    }
}

func (wp *WorkerPool) Start() {
    for i := 0; i < wp.workers; i++ {
        go wp.worker()
    }
}

func (wp *WorkerPool) worker() {
    for {
        select {
        case task := <-wp.tasks:
            task()
        case <-wp.quit:
            return
        }
    }
}
```



## 2. 内存管理

### 2.1 垃圾回收
**Q: Go的GC算法演进和三色标记法？**
- 三色标记：白色（未访问）、灰色（已访问未扫描）、黑色（已扫描）
- 写屏障技术减少STW时间
- 并发标记和清除

**Q: 如何优化GC性能？**
- 减少堆分配，使用对象池
- 控制对象生命周期

#### Go GC深度优化实战

**GC性能分析和调优：**
```go
package main

import (
    "fmt"
    "runtime"
    "runtime/debug"
    "sync"
    "time"
)

// GC性能监控器
type GCMonitor struct {
    stats []runtime.MemStats
    mu    sync.RWMutex
}

func NewGCMonitor() *GCMonitor {
    return &GCMonitor{
        stats: make([]runtime.MemStats, 0),
    }
}

func (g *GCMonitor) Snapshot() {
    var m runtime.MemStats
    runtime.ReadMemStats(&m)
    
    g.mu.Lock()
    g.stats = append(g.stats, m)
    g.mu.Unlock()
}

func (g *GCMonitor) PrintStats() {
    g.mu.RLock()
    defer g.mu.RUnlock()
    
    if len(g.stats) < 2 {
        return
    }
    
    latest := g.stats[len(g.stats)-1]
    previous := g.stats[len(g.stats)-2]
    
    fmt.Printf("\n=== GC性能统计 ===\n")
    fmt.Printf("堆内存使用: %.2f MB\n", float64(latest.HeapAlloc)/1024/1024)
    fmt.Printf("堆内存大小: %.2f MB\n", float64(latest.HeapSys)/1024/1024)
    fmt.Printf("GC次数: %d (增加 %d)\n", latest.NumGC, latest.NumGC-previous.NumGC)
    fmt.Printf("总暂停时间: %v\n", time.Duration(latest.PauseTotalNs))
    
    if latest.NumGC > previous.NumGC {
        // 计算平均暂停时间
        avgPause := time.Duration(latest.PauseTotalNs-previous.PauseTotalNs) / 
                   time.Duration(latest.NumGC-previous.NumGC)
        fmt.Printf("平均暂停时间: %v\n", avgPause)
    }
    
    fmt.Printf("对象数量: %d\n", latest.Mallocs-latest.Frees)
    fmt.Printf("堆对象数: %d\n", latest.HeapObjects)
}

// 模拟内存密集型应用
func memoryIntensiveApp(monitor *GCMonitor) {
    fmt.Println("\n=== 内存密集型应用模拟 ===")
    
    // 设置GC目标：堆内存占用达到100MB时触发GC
    debug.SetGCPercent(100)
    
    const numIterations = 10
    const allocSize = 10 * 1024 * 1024 // 10MB
    
    monitor.Snapshot()
    
    for i := 0; i < numIterations; i++ {
        // 分配大量内存
        data := make([]byte, allocSize)
        
        // 模拟一些操作
        for j := 0; j < len(data); j += 1024 {
            data[j] = byte(i)
        }
        
        // 模拟处理后释放
        if i%3 == 0 {
            runtime.GC() // 手动触发GC
        }
        
        monitor.Snapshot()
        
        // 模拟一些对象在长时间内保持引用
        if i%2 == 0 {
            _ = data // 保持引用，防止被GC
        }
    }
    
    monitor.PrintStats()
}

// 对象池优化示例
type BigObject struct {
    Data [1024]byte
    ID   int
    Used bool
}

type ObjectPool struct {
    pool sync.Pool
}

func NewObjectPool() *ObjectPool {
    return &ObjectPool{
        pool: sync.Pool{
            New: func() interface{} {
                return &BigObject{}
            },
        },
    }
}

func (p *ObjectPool) Get() *BigObject {
    obj := p.pool.Get().(*BigObject)
    obj.Used = true
    return obj
}

func (p *ObjectPool) Put(obj *BigObject) {
    obj.Used = false
    obj.ID = 0
    // 清理数据
    for i := range obj.Data {
        obj.Data[i] = 0
    }
    p.pool.Put(obj)
}

// 对比使用对象池和不使用对象池的性能
func compareObjectPoolPerformance(monitor *GCMonitor) {
    fmt.Println("\n=== 对象池性能对比 ===")
    
    const numOperations = 1000
    pool := NewObjectPool()
    
    // 不使用对象池
    fmt.Println("\n不使用对象池:")
    monitor.Snapshot()
    start := time.Now()
    
    for i := 0; i < numOperations; i++ {
        obj := &BigObject{ID: i}
        // 模拟使用
        obj.Data[0] = byte(i)
        _ = obj // 防止编译器优化
    }
    
    elapsed1 := time.Since(start)
    runtime.GC() // 强制GC
    monitor.Snapshot()
    monitor.PrintStats()
    
    // 使用对象池
    fmt.Println("\n使用对象池:")
    monitor.Snapshot()
    start = time.Now()
    
    for i := 0; i < numOperations; i++ {
        obj := pool.Get()
        obj.ID = i
        obj.Data[0] = byte(i)
        pool.Put(obj)
    }
    
    elapsed2 := time.Since(start)
    runtime.GC() // 强制GC
    monitor.Snapshot()
    monitor.PrintStats()
    
    fmt.Printf("\n性能对比:\n")
    fmt.Printf("不使用对象池: %v\n", elapsed1)
    fmt.Printf("使用对象池: %v\n", elapsed2)
    fmt.Printf("性能提升: %.2fx\n", float64(elapsed1)/float64(elapsed2))
}

// GC调优策略示例
func gcTuningStrategies() {
    fmt.Println("\n=== GC调优策略 ===")
    
    // 1. 调整GOGC参数
    originalGOGC := debug.SetGCPercent(-1) // 获取当前值
    debug.SetGCPercent(originalGOGC)      // 恢复
    
    fmt.Printf("当前GOGC设置: %d%%\n", originalGOGC)
    
    // 2. 手动控制GC时机
    fmt.Println("
手动GC控制示例:")
    
    // 在适当的时机手动触发GC
    type MemoryManager struct {
        allocatedSize int64
        threshold     int64
    }
    
    mm := &MemoryManager{
        threshold: 50 * 1024 * 1024, // 50MB阈值
    }
    
    for i := 0; i < 5; i++ {
        // 模拟内存分配
        data := make([]byte, 10*1024*1024) // 10MB
        mm.allocatedSize += int64(len(data))
        
        fmt.Printf("分配 %d MB, 总计 %d MB\n", 
            len(data)/1024/1024, mm.allocatedSize/1024/1024)
        
        // 达到阈值时手动触发GC
        if mm.allocatedSize > mm.threshold {
            fmt.Println("达到阈值，手动触发GC")
            runtime.GC()
            mm.allocatedSize = 0 // 重置计数器
        }
        
        _ = data // 防止编译器优化
    }
    
    // 3. 使用runtime/debug进行精细控制
    var gcStats debug.GCStats
    debug.ReadGCStats(&gcStats)
    
    fmt.Printf("\nGC统计信息:\n")
    fmt.Printf("GC次数: %d\n", gcStats.NumGC)
    fmt.Printf("上次GC时间: %v\n", gcStats.LastGC)
    if len(gcStats.Pause) > 0 {
        fmt.Printf("最近暂停时间: %v\n", gcStats.Pause[0])
    }
}

func main() {
    monitor := NewGCMonitor()
    
    // 执行各种性能测试
    memoryIntensiveApp(monitor)
    compareObjectPoolPerformance(monitor)
    gcTuningStrategies()
    
    // 最终统计
    fmt.Println("\n=== 最终内存状态 ===")
    monitor.Snapshot()
    monitor.PrintStats()
}
```

### 2.2 内存逃逸
**Q: 什么情况下会发生内存逃逸？**
- 指针作为返回值
- 接口类型的赋值
- 闭包引用外部变量
- slice/map动态扩容

#### 内存逃逸深度分析实战

**逃逸分析和优化技巧：**
```go
package main

import (
    "fmt"
    "runtime"
)

// 逃逸场景1：返回局部变量指针
func escapeScenario1() *int {
    x := 42
    return &x // x逃逸到堆上
}

// 优化方案：使用值返回
func optimizedScenario1() int {
    x := 42
    return x // x在栈上
}

// 逃逸场景2：闭包引用外部变量
func escapeScenario2() func() int {
    x := 42
    return func() int {
        return x // x因为被闭包引用而逃逸
    }
}

// 优化方案：避免闭包或传递参数
func optimizedScenario2(initialValue int) func() int {
    return func() int {
        return initialValue // initialValue作为参数传入
    }
}

// 逃逸场景3：接口赋值
func escapeScenario3() interface{} {
    x := 42
    return x // x逃逸到堆上，因为被包装成interface{}
}

// 优化方案：使用具体类型
func optimizedScenario3() int {
    x := 42
    return x // 直接返回具体类型
}

// 逃逸场景4：slice动态增长
func escapeScenario4() []int {
    var slice []int
    for i := 0; i < 1000; i++ {
        slice = append(slice, i) // slice可能多次重新分配
    }
    return slice
}

// 优化方案：预分配容量
func optimizedScenario4() []int {
    slice := make([]int, 0, 1000) // 预分配容量
    for i := 0; i < 1000; i++ {
        slice = append(slice, i)
    }
    return slice
}

// 逃逸分析工具函数
func analyzeEscape() {
    fmt.Println("\n=== 内存逃逸分析 ===")
    
    var m1, m2 runtime.MemStats
    
    // 测试逃逸场景
    runtime.ReadMemStats(&m1)
    
    const iterations = 1000
    
    // 测试逃逸情况
    fmt.Println("测试逃逸情况:")
    for i := 0; i < iterations; i++ {
        _ = escapeScenario1()
        _ = escapeScenario2()
        _ = escapeScenario3()
        _ = escapeScenario4()
    }
    
    runtime.ReadMemStats(&m2)
    fmt.Printf("堆分配增加: %d bytes\n", m2.HeapAlloc-m1.HeapAlloc)
    fmt.Printf("分配次数增加: %d\n", m2.Mallocs-m1.Mallocs)
    
    // 测试优化情况
    runtime.GC()
    runtime.ReadMemStats(&m1)
    
    fmt.Println("\n测试优化情况:")
    for i := 0; i < iterations; i++ {
        _ = optimizedScenario1()
        _ = optimizedScenario2(42)
        _ = optimizedScenario3()
        _ = optimizedScenario4()
    }
    
    runtime.ReadMemStats(&m2)
    fmt.Printf("堆分配增加: %d bytes\n", m2.HeapAlloc-m1.HeapAlloc)
    fmt.Printf("分配次数增加: %d\n", m2.Mallocs-m1.Mallocs)
}

// 高级逃逸分析技巧
func advancedEscapeAnalysis() {
    fmt.Println("\n=== 高级逃逸分析技巧 ===")
    
    // 1. 使用编译器标志分析逃逸
    fmt.Println("1. 使用编译器标志:")
    fmt.Println("   go build -gcflags='-m' main.go")
    fmt.Println("   可以显示哪些变量逃逸到堆上")
    
    // 2. 优化技巧示例
    fmt.Println("\n2. 常用优化技巧:")
    
    // 技巧1：使用对象池避免频繁分配
    type LargeStruct struct {
        Data [1024]byte
    }
    
    pool := sync.Pool{
        New: func() interface{} {
            return &LargeStruct{}
        },
    }
    
    obj := pool.Get().(*LargeStruct)
    // 使用obj...
    pool.Put(obj)
    
    fmt.Println("   - 使用sync.Pool避免频繁分配")
    
    // 技巧2：预分配slice容量
    const size = 1000
    slice := make([]int, 0, size) // 预分配容量
    for i := 0; i < size; i++ {
        slice = append(slice, i)
    }
    fmt.Println("   - 预分配slice容量避免重新分配")
    
    // 技巧3：使用栈上数组而非slice（小数据量）
    var stackArray [10]int
    for i := range stackArray {
        stackArray[i] = i
    }
    fmt.Println("   - 小数据量使用数组而非slice")
    
    _ = slice
    _ = stackArray
}

func main() {
    analyzeEscape()
    advancedEscapeAnalysis()
}
```
### 2.3 内存和性能优化实例

#### 避免内存逃逸
```go
// 错误示例 - 会发生逃逸
func badExample() *int {
    x := 42
    return &x  // x逃逸到堆上
}

// 正确示例 - 避免逃逸
func goodExample(result *int) {
    *result = 42  // 使用调用者提供的内存
}
```

#### 字符串拼接优化
```go
// 性能测试对比
func BenchmarkStringConcat(b *testing.B) {
    strs := []string{"hello", "world", "golang", "performance"}
    
    b.Run("Plus", func(b *testing.B) {
        for i := 0; i < b.N; i++ {
            result := ""
            for _, s := range strs {
                result += s
            }
        }
    })
    
    b.Run("Builder", func(b *testing.B) {
        for i := 0; i < b.N; i++ {
            var builder strings.Builder
            for _, s := range strs {
                builder.WriteString(s)
            }
            _ = builder.String()
        }
    })
}
```



### 2.2 内存逃逸
**Q: 什么情况下会发生内存逃逸？**
- 指针作为返回值
- 接口类型的赋值
- 闭包引用外部变量
- slice/map动态扩容

## 3. 类型系统

### 3.1 接口
**Q: 空接口interface{}的底层实现？**
- eface结构：_type和data指针
- 类型断言的性能考虑

**Q: 接口的动态类型和动态值？**
- 类型信息和值信息分别存储
- nil接口的判断机制

### 3.2 反射
**Q: 反射的性能影响和使用场景？**
- Type和Value的获取成本
### 3.3 接口和类型系统代码题

#### 空接口判断
```go
func isNil(x interface{}) bool {
    // 错误的nil判断
    return x == nil
}

func correctNilCheck(x interface{}) bool {
    // 正确的nil判断
    if x == nil {
        return true
    }
    
    v := reflect.ValueOf(x)
    switch v.Kind() {
    case reflect.Chan, reflect.Func, reflect.Interface, 
         reflect.Map, reflect.Ptr, reflect.Slice:
        return v.IsNil()
    default:
        return false
    }
}
```

#### 类型断言性能
```go
// 高频类型断言优化
func processValue(v interface{}) {
    // 使用type switch比多次类型断言效率更高
    switch val := v.(type) {
    case int:
        // 处理int
    case string:
        // 处理string
    case []byte:
        // 处理[]byte
    default:
        // 处理其他类型
    }
}
```



## 4. 并发安全

### 4.1 同步原语
**Q: sync.Mutex和sync.RWMutex的实现原理？**
- 互斥锁的公平性和性能权衡
- 读写锁的读者优先vs写者优先

**Q: sync.Once的实现机制？**
- 原子操作和双重检查
- 内存屏障的作用

### 4.2 原子操作
**Q: atomic包的使用场景和注意事项？**
- Compare-and-swap操作
- 内存对齐的重要性
### 4.3 同步原语代码实例

#### Once 的正确使用
```go
type Config struct {
    data map[string]string
    once sync.Once
}

func (c *Config) Load() {
    c.once.Do(func() {
        c.data = loadConfigFromFile()
    })
}

// 错误示例 - 每次都会执行
func (c *Config) BadLoad() {
    if c.data == nil {
        c.data = loadConfigFromFile()  // 竞态条件
    }
}
```

#### 读写锁的使用场景
```go
type Cache struct {
    mu    sync.RWMutex
    items map[string]interface{}
}

func (c *Cache) Get(key string) (interface{}, bool) {
    c.mu.RLock()
    defer c.mu.RUnlock()
    val, ok := c.items[key]
    return val, ok
}

func (c *Cache) Set(key string, value interface{}) {
    c.mu.Lock()
    defer c.mu.Unlock()
    if c.items == nil {
        c.items = make(map[string]interface{})
    }
    c.items[key] = value
}
```



## 5. 性能优化

### 5.1 编译优化
**Q: Go编译器的优化策略？**
- 内联优化
- 逃逸分析
- 死代码消除

**Q: 如何进行性能分析？**
- pprof工具使用
- CPU和内存profile
- trace分析

#### Go性能优化实战指南

**全面的性能分析和优化框架：**
```go
package main

import (
    "fmt"
    "log"
    "net/http"
    _ "net/http/pprof"
    "os"
    "runtime"
    "runtime/pprof"
    "runtime/trace"
    "sync"
    "time"
)

// 性能测试数据结构
type PerformanceTestData struct {
    Size     int
    Duration time.Duration
    Memory   uint64
    Allocs   uint64
}

// 性能测试器
type PerformanceTester struct {
    results []PerformanceTestData
    mu      sync.Mutex
}

func NewPerformanceTester() *PerformanceTester {
    return &PerformanceTester{
        results: make([]PerformanceTestData, 0),
    }
}

func (pt *PerformanceTester) Test(name string, size int, testFunc func()) {
    var m1, m2 runtime.MemStats
    runtime.GC()
    runtime.ReadMemStats(&m1)
    
    start := time.Now()
    testFunc()
    duration := time.Since(start)
    
    runtime.ReadMemStats(&m2)
    
    result := PerformanceTestData{
        Size:     size,
        Duration: duration,
        Memory:   m2.HeapAlloc - m1.HeapAlloc,
        Allocs:   m2.Mallocs - m1.Mallocs,
    }
    
    pt.mu.Lock()
    pt.results = append(pt.results, result)
    pt.mu.Unlock()
    
    fmt.Printf("%s (size=%d): %v, memory=%d bytes, allocs=%d\n", 
        name, size, duration, result.Memory, result.Allocs)
}

// 字符串拼接性能对比
func stringConcatenationBenchmark(pt *PerformanceTester) {
    fmt.Println("\n=== 字符串拼接性能对比 ===")
    
    sizes := []int{100, 1000, 10000}
    
    for _, size := range sizes {
        // 方法1：使用+操作符
        pt.Test("String+", size, func() {
            result := ""
            for i := 0; i < size; i++ {
                result += "a"
            }
        })
        
        // 方法2：使用strings.Builder
        pt.Test("strings.Builder", size, func() {
            var builder strings.Builder
            builder.Grow(size) // 预分配容量
            for i := 0; i < size; i++ {
                builder.WriteString("a")
            }
            _ = builder.String()
        })
        
        // 方法3：使用bytes.Buffer
        pt.Test("bytes.Buffer", size, func() {
            var buffer bytes.Buffer
            buffer.Grow(size) // 预分配容量
            for i := 0; i < size; i++ {
                buffer.WriteString("a")
            }
            _ = buffer.String()
        })
    }
}

// Slice操作性能对比
func sliceOperationBenchmark(pt *PerformanceTester) {
    fmt.Println("\n=== Slice操作性能对比 ===")
    
    sizes := []int{1000, 10000, 100000}
    
    for _, size := range sizes {
        // 方法1：没有预分配
        pt.Test("slice-no-prealloc", size, func() {
            var slice []int
            for i := 0; i < size; i++ {
                slice = append(slice, i)
            }
        })
        
        // 方法2：预分配容量
        pt.Test("slice-prealloc", size, func() {
            slice := make([]int, 0, size)
            for i := 0; i < size; i++ {
                slice = append(slice, i)
            }
        })
        
        // 方法3：直接分配并访问
        pt.Test("slice-direct", size, func() {
            slice := make([]int, size)
            for i := 0; i < size; i++ {
                slice[i] = i
            }
        })
    }
}

// Map操作性能对比
func mapOperationBenchmark(pt *PerformanceTester) {
    fmt.Println("\n=== Map操作性能对比 ===")
    
    sizes := []int{1000, 10000, 100000}
    
    for _, size := range sizes {
        // 方法1：普通map
        pt.Test("map-normal", size, func() {
            m := make(map[int]int)
            for i := 0; i < size; i++ {
                m[i] = i * 2
            }
        })
        
        // 方法2：预分配容量的map
        pt.Test("map-prealloc", size, func() {
            m := make(map[int]int, size)
            for i := 0; i < size; i++ {
                m[i] = i * 2
            }
        })
        
        // 方法3：使用sync.Map（高并发场景）
        pt.Test("sync.Map", size, func() {
            var m sync.Map
            for i := 0; i < size; i++ {
                m.Store(i, i*2)
            }
        })
    }
}

// CPU密集型任务性能测试
func cpuIntensiveBenchmark(pt *PerformanceTester) {
    fmt.Println("\n=== CPU密集型任务性能测试 ===")
    
    // 数学计算任务
    pt.Test("fibonacci-recursive", 35, func() {
        fibonacci(35)
    })
    
    pt.Test("fibonacci-iterative", 35, func() {
        fibonacciIterative(35)
    })
    
    // 并发任务
    pt.Test("parallel-computation", 1000000, func() {
        parallelSum(1000000)
    })
}

// 递归斐波那契数列
func fibonacci(n int) int {
    if n <= 1 {
        return n
    }
    return fibonacci(n-1) + fibonacci(n-2)
}

// 迭代斐波那契数列
func fibonacciIterative(n int) int {
    if n <= 1 {
        return n
    }
    a, b := 0, 1
    for i := 2; i <= n; i++ {
        a, b = b, a+b
    }
    return b
}

// 并行计算求和
func parallelSum(n int) int {
    numWorkers := runtime.NumCPU()
    chunkSize := n / numWorkers
    
    results := make(chan int, numWorkers)
    
    for i := 0; i < numWorkers; i++ {
        start := i * chunkSize
        end := start + chunkSize
        if i == numWorkers-1 {
            end = n
        }
        
        go func(start, end int) {
            sum := 0
            for j := start; j < end; j++ {
                sum += j
            }
            results <- sum
        }(start, end)
    }
    
    total := 0
    for i := 0; i < numWorkers; i++ {
        total += <-results
    }
    
    return total
}

// 启动pprof服务器
func startPprofServer() {
    go func() {
        fmt.Println("启动pprof服务器: http://localhost:6060/debug/pprof/")
        log.Println(http.ListenAndServe("localhost:6060", nil))
    }()
}

// CPU profile分析
func runCPUProfile() {
    fmt.Println("\n=== CPU Profile分析 ===")
    
    // 创建CPU profile文件
    f, err := os.Create("cpu.prof")
    if err != nil {
        log.Fatal(err)
    }
    defer f.Close()
    
    // 开始CPU profiling
    if err := pprof.StartCPUProfile(f); err != nil {
        log.Fatal(err)
    }
    defer pprof.StopCPUProfile()
    
    // 执行一些CPU密集型任务
    for i := 0; i < 1000000; i++ {
        fibonacci(20)
    }
    
    fmt.Println("CPU profile已保存到 cpu.prof")
    fmt.Println("使用以下命令分析:")
    fmt.Println("go tool pprof cpu.prof")
}

// Memory profile分析
func runMemoryProfile() {
    fmt.Println("\n=== Memory Profile分析 ===")
    
    // 执行一些内存密集型任务
    var data [][]byte
    for i := 0; i < 1000; i++ {
        data = append(data, make([]byte, 1024*1024)) // 1MB
    }
    
    // 创建memory profile文件
    f, err := os.Create("mem.prof")
    if err != nil {
        log.Fatal(err)
    }
    defer f.Close()
    
    runtime.GC() // 强制执行GC以获得准确的内存数据
    if err := pprof.WriteHeapProfile(f); err != nil {
        log.Fatal(err)
    }
    
    fmt.Println("Memory profile已保存到 mem.prof")
    fmt.Println("使用以下命令分析:")
    fmt.Println("go tool pprof mem.prof")
    
    _ = data // 防止编译器优化
}

// Trace分析
func runTraceAnalysis() {
    fmt.Println("\n=== Trace分析 ===")
    
    // 创建trace文件
    f, err := os.Create("trace.out")
    if err != nil {
        log.Fatal(err)
    }
    defer f.Close()
    
    // 开始跟踪
    if err := trace.Start(f); err != nil {
        log.Fatal(err)
    }
    defer trace.Stop()
    
    // 执行一些并发任务
    var wg sync.WaitGroup
    for i := 0; i < 10; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            for j := 0; j < 100000; j++ {
                _ = fibonacciIterative(20)
            }
        }(i)
    }
    wg.Wait()
    
    fmt.Println("Trace数据已保存到 trace.out")
    fmt.Println("使用以下命令分析:")
    fmt.Println("go tool trace trace.out")
}

### 5.2 代码优化
**Q: 字符串拼接的性能比较？**
- + 操作符 vs fmt.Sprintf vs strings.Builder

func main() {
    // 启动pprof服务器
    startPprofServer()
    
    // 等待服务器启动
    time.Sleep(1 * time.Second)
    
    // 创建性能测试器
    pt := NewPerformanceTester()
    
    // 执行各种性能测试
    stringConcatenationBenchmark(pt)
    sliceOperationBenchmark(pt)
    mapOperationBenchmark(pt)
    cpuIntensiveBenchmark(pt)
    
    // 执行性能分析
    runCPUProfile()
    runMemoryProfile()
    runTraceAnalysis()
    
    fmt.Println("\n性能分析完成！")
    fmt.Println("访问 http://localhost:6060/debug/pprof/ 查看实时性能数据")
    
    // 保持程序运行以便查看pprof
    select {}
}
```
### 5.3 性能分析实战

#### pprof 使用示例
```go
import (
    _ "net/http/pprof"
    "net/http"
    "log"
)

func main() {
    // 启动pprof服务
    go func() {
        log.Println(http.ListenAndServe("localhost:6060", nil))
    }()
    
    // 主程序逻辑
    runApplication()
}
```

#### 基准测试编写
```go
func BenchmarkSliceAppend(b *testing.B) {
    b.Run("WithoutPrealloc", func(b *testing.B) {
        for i := 0; i < b.N; i++ {
            var slice []int
            for j := 0; j < 1000; j++ {
                slice = append(slice, j)
            }
        }
    })
    
    b.Run("WithPrealloc", func(b *testing.B) {
        for i := 0; i < b.N; i++ {
            slice := make([]int, 0, 1000)
            for j := 0; j < 1000; j++ {
                slice = append(slice, j)
            }
        }
    })
}
```



## 6. 错误处理

**Q: error接口的设计哲学？**
- 显式错误处理vs异常机制
- errors.Is和errors.As的使用

**Q: 如何设计良好的错误处理？**
- 错误包装和上下文信息
### 6.2 错误处理实践

#### 错误包装
```go
func processFile(filename string) error {
    file, err := os.Open(filename)
    if err != nil {
        return fmt.Errorf("打开文件失败 %s: %w", filename, err)
    }
    defer file.Close()
    
    data, err := io.ReadAll(file)
    if err != nil {
        return fmt.Errorf("读取文件内容失败 %s: %w", filename, err)
    }
    
    if err := process(data); err != nil {
        return fmt.Errorf("处理数据失败: %w", err)
    }
    
    return nil
}
```

#### 自定义错误类型
```go
type ValidationError struct {
    Field string
    Value interface{}
    Tag   string
}

func (e ValidationError) Error() string {
    return fmt.Sprintf("验证失败: 字段 %s 值 %v 不满足规则 %s", 
        e.Field, e.Value, e.Tag)
}

func validate(data interface{}) error {
    // 验证逻辑
    return &ValidationError{
        Field: "email",
        Value: "invalid-email",
        Tag:   "email",
    }
}
```



## 7. 包管理和模块

**Q: Go Modules的工作原理？**
- go.mod和go.sum文件
- 语义化版本控制
- vendor机制

**Q: 包的可见性规则？**
- 首字母大小写的访问控制
- internal包的特殊性

## 8. 网络编程

**Q: Go的网络模型和epoll？**
- netpoller的实现
- 异步I/O的处理

**Q: Context的使用和传播？**
- 超时控制和取消机制

#### Go网络编程实战案例

**高性能TCP服务器实现：**
```go
package main

import (
    "context"
    "fmt"
    "log"
    "net"
    "sync"
    "time"
)

// TCP服务器
type TCPServer struct {
    address   string
    listener  net.Listener
    ctx       context.Context
    cancel    context.CancelFunc
    wg        sync.WaitGroup
}

func NewTCPServer(address string) *TCPServer {
    ctx, cancel := context.WithCancel(context.Background())
    return &TCPServer{
        address: address,
        ctx:     ctx,
        cancel:  cancel,
    }
}

func (s *TCPServer) Start() error {
    listener, err := net.Listen("tcp", s.address)
    if err != nil {
        return fmt.Errorf("启动TCP服务器失败: %w", err)
    }
    
    s.listener = listener
    log.Printf("TCP服务器启动，监听地址: %s", s.address)
    
    // 启动连接接受器
    s.wg.Add(1)
    go s.acceptConnections()
    
    return nil
}

func (s *TCPServer) acceptConnections() {
    defer s.wg.Done()
    
    for {
        // 设置接受超时
        if tcpListener, ok := s.listener.(*net.TCPListener); ok {
            tcpListener.SetDeadline(time.Now().Add(1 * time.Second))
        }
        
        conn, err := s.listener.Accept()
        if err != nil {
            select {
            case <-s.ctx.Done():
                return
            default:
                if netErr, ok := err.(net.Error); ok && netErr.Timeout() {
                    continue // 超时是正常的，继续等待
                }
                log.Printf("接受连接失败: %v", err)
                continue
            }
        }
        
        // 为每个连接启动一个goroutine
        s.wg.Add(1)
        go s.handleConnection(conn)
    }
}

func (s *TCPServer) handleConnection(conn net.Conn) {
    defer s.wg.Done()
    defer conn.Close()
    
    log.Printf("新连接来自: %s", conn.RemoteAddr())
    
    // 设置连接超时
    conn.SetReadDeadline(time.Now().Add(30 * time.Second))
    
    buffer := make([]byte, 1024)
    for {
        select {
        case <-s.ctx.Done():
            return
        default:
            n, err := conn.Read(buffer)
            if err != nil {
                log.Printf("读取数据失败: %v", err)
                return
            }
            
            // Echo服务器：将接收到的数据发送回去
            response := fmt.Sprintf("Echo: %s", string(buffer[:n]))
            _, err = conn.Write([]byte(response))
            if err != nil {
                log.Printf("发送响应失败: %v", err)
                return
            }
            
            // 更新读取超时
            conn.SetReadDeadline(time.Now().Add(30 * time.Second))
        }
    }
}

func (s *TCPServer) Stop() error {
    log.Println("停止TCP服务器...")
    
    s.cancel()
    
    if s.listener != nil {
        s.listener.Close()
    }
    
    // 等待所有goroutine结束
    done := make(chan struct{})
    go func() {
        s.wg.Wait()
        close(done)
    }()
    
    select {
    case <-done:
        log.Println("TCP服务器已停止")
    case <-time.After(5 * time.Second):
        log.Println("TCP服务器停止超时")
    }
    
    return nil
}

// Context使用示例
func demonstrateContext() {
    fmt.Println("\n=== Context使用示例 ===")
    
    // 1. 带超时的Context
    ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
    defer cancel()
    
    // 模拟一个可能超时的操作
    done := make(chan string, 1)
    go func() {
        time.Sleep(1 * time.Second) // 模拟工作
        done <- "工作完成"
    }()
    
    select {
    case result := <-done:
        fmt.Println("结果:", result)
    case <-ctx.Done():
        fmt.Println("操作超时:", ctx.Err())
    }
    
    // 2. 带取消的Context
    ctx2, cancel2 := context.WithCancel(context.Background())
    
    go func() {
        for {
            select {
            case <-ctx2.Done():
                fmt.Println("工作被取消")
                return
            default:
                fmt.Println("正在工作...")
                time.Sleep(500 * time.Millisecond)
            }
        }
    }()
    
    time.Sleep(1500 * time.Millisecond)
    cancel2() // 取消操作
    time.Sleep(100 * time.Millisecond)
}

func main() {
    // 演示Context使用
    demonstrateContext()
    
    // 启动TCP服务器
    server := NewTCPServer(":8080")
    
    if err := server.Start(); err != nil {
        log.Fatal(err)
    }
    
    // 运行一段时间后停止
    time.Sleep(10 * time.Second)
    server.Stop()
}
```
### 8.2 Channel 高级使用模式

#### 扇入扇出模式
```go
// 扇出 - 一个输入分发到多个worker
func fanOut(in <-chan int, workers int) []<-chan int {
    outs := make([]<-chan int, workers)
    for i := 0; i < workers; i++ {
        out := make(chan int)
        outs[i] = out
        
        go func(out chan<- int) {
            defer close(out)
            for val := range in {
                out <- process(val)
            }
        }(out)
    }
    return outs
}

// 扇入 - 多个输入合并到一个输出
func fanIn(ins ...<-chan int) <-chan int {
    out := make(chan int)
    var wg sync.WaitGroup
    
    for _, in := range ins {
        wg.Add(1)
        go func(in <-chan int) {
            defer wg.Done()
            for val := range in {
                out <- val
            }
        }(in)
    }
    
    go func() {
        wg.Wait()
        close(out)
    }()
    
    return out
}
```

#### 超时控制模式
```go
func timeoutOperation(timeout time.Duration) error {
    done := make(chan error, 1)
    
    go func() {
        // 执行耗时操作
        done <- longRunningOperation()
    }()
    
    select {
    case err := <-done:
        return err
    case <-time.After(timeout):
        return errors.New("操作超时")
    }
}
```



## 9. 测试

**Q: Go的测试框架特点？**
- 基准测试的编写
- 表驱动测试模式
- mock和依赖注入

**Q: 竞态条件检测？**
- go test -race
- 数据竞争的常见场景

## 10. 实际应用场景

**Q: 如何设计一个高并发的Web服务？**
- 连接池管理
- 限流和熔断
- 优雅关闭

**Q: 微服务架构中Go的优势？**
- 编译速度和部署便利性
- 内存占用和启动速度
- 生态系统支持