# Java 高级面试题完整整理

## 📋 目录

- [1. JVM 虚拟机](#1-jvm-虚拟机)
  - [1.1 内存结构](#11-内存结构)
  - [1.2 垃圾回收](#12-垃圾回收)
  - [1.3 类加载机制](#13-类加载机制)
  - [1.4 JVM 调优实战](#14-jvm-调优实战)
- [2. 并发编程](#2-并发编程)
  - [2.1 线程基础](#21-线程基础)
  - [2.2 锁机制](#22-锁机制)
  - [2.3 并发工具类](#23-并发工具类)
  - [2.4 并发编程实战代码](#24-并发编程实战代码)
- [3. 集合框架](#3-集合框架)
  - [3.1 List 实现](#31-list-实现)
  - [3.2 Map 实现](#32-map-实现)
  - [3.3 集合性能优化](#33-集合性能优化)
- [4. Spring 框架](#4-spring-框架)
  - [4.1 IOC 容器](#41-ioc-容器)
  - [4.2 AOP 切面](#42-aop-切面)
  - [4.3 Spring Boot](#43-spring-boot)
  - [4.4 Spring 源码分析](#44-spring-源码分析)
- [5. 数据库](#5-数据库)
  - [5.1 MySQL 优化](#51-mysql-优化)
  - [5.2 事务机制](#52-事务机制)
  - [5.3 连接池](#53-连接池)
- [6. 分布式系统](#6-分布式系统)
  - [6.1 微服务架构](#61-微服务架构)
  - [6.2 分布式事务](#62-分布式事务)
  - [6.3 消息队列](#63-消息队列)
- [7. 性能优化](#7-性能优化)
  - [7.1 代码优化](#71-代码优化)
  - [7.2 JVM 性能调优](#72-jvm-性能调优)
- [8. 设计模式](#8-设计模式)
- [9. 网络编程](#9-网络编程)
- [10. 实际项目经验](#10-实际项目经验)

---

## 1. JVM 虚拟机

### 1.1 内存结构
**Q: 详细说明JVM内存模型？**
- **堆内存（Heap）**：存储对象实例，分为新生代和老年代
  - 新生代：Eden区 + 2个Survivor区（S0, S1）
  - 老年代：长期存活的对象
- **方法区（Method Area）**：存储类信息、常量、静态变量
- **程序计数器（PC Register）**：当前线程执行的字节码行号
- **虚拟机栈（VM Stack）**：存储局部变量、操作数栈
- **本地方法栈（Native Method Stack）**：调用本地方法

**Q: 为什么内存模型要这样设计，而不是其他方式？**

#### JVM内存模型设计原理深度分析

**1. 分代垃圾收集理论基础**
```java
// 对象生命周期分析
public class ObjectLifecycleDemo {
    
    // 短生命周期对象（大部分对象）
    public void createTemporaryObjects() {
        for (int i = 0; i < 1000000; i++) {
            String temp = "临时字符串" + i;  // 创建后很快就被回收
            List<Integer> list = new ArrayList<>();  // 局部变量，方法结束后可被回收
        }
    }
    
    // 长生命周期对象（少数对象）
    private static final Map<String, Object> cache = new HashMap<>();  // 静态变量，长期存在
    private final Logger logger = LoggerFactory.getLogger(getClass());  // 实例变量，随对象存在
}
```

**分代设计的科学依据：**
- **弱分代假说**：绝大多数对象都是朝生夕死的
- **强分代假说**：熬过越多次垃圾收集的对象就越难以消亡

**2. 为什么不是其他内存布局？**

```java
// 假设：如果采用单一内存区域（不分代）
public class SingleHeapModel {
    // 问题分析：
    // 1. GC效率低：每次都要扫描所有对象
    // 2. 内存碎片：长短对象混合存放
    // 3. 分配效率差：需要在整个堆中查找合适空间
    
    public void demonstrateProblem() {
        // 短命对象
        String temp1 = new String("temp1");
        String temp2 = new String("temp2");
        
        // 长命对象
        Object longLived = createLongLivedObject();
        
        // 在单一堆中，GC时需要扫描所有对象
        // 无法针对性优化短命对象的回收
    }
}
```

**3. 新生代三区设计（Eden + S0 + S1）的必要性**

```java
// 复制算法的实现原理
public class CopyingAlgorithmDemo {
    
    // Eden区：对象首次分配的区域
    // Survivor区：存活对象的中转站
    
    public void explainCopyingAlgorithm() {
        /*
         * 复制算法流程：
         * 1. 新对象在Eden区分配
         * 2. Eden区满时触发Minor GC
         * 3. 存活对象复制到Survivor区
         * 4. 清空Eden区和另一个Survivor区
         * 5. 交换两个Survivor区的角色
         */
    }
}
```

**为什么需要两个Survivor区？**
```java
// 单Survivor区的问题
public class SingleSurvivorProblem {
    /*
     * 如果只有一个Survivor区：
     * 1. 内存碎片问题：无法实现完整的复制算法
     * 2. 分配效率低：需要在碎片中找空间
     * 3. GC效率差：无法彻底清理内存
     */
}

// 双Survivor区的优势
public class DoubleSurvivorAdvantage {
    /*
     * 两个Survivor区的优势：
     * 1. 完整复制：确保内存紧凑无碎片
     * 2. 高效分配：始终有一块完整空间
     * 3. 清晰标记：存活对象年龄明确
     */
}
```

**4. 方法区独立设计的原因**

```java
// 方法区存储内容的特殊性
public class MethodAreaDesign {
    
    // 类元数据（需要长期保存）
    private static final String CLASS_NAME = "MethodAreaDesign";
    
    // 常量池（需要全局共享）
    public static final String CONSTANT = "全局常量";
    
    // 静态变量（生命周期与类相同）
    private static int staticVar = 100;
    
    /*
     * 为什么方法区要独立？
     * 1. 生命周期不同：类信息伴随应用全程
     * 2. 共享性质：多线程共享相同的类信息
     * 3. 回收策略：很少回收，主要是类卸载
     * 4. 访问模式：读多写少，适合不同的优化策略
     */
}
```

**5. 栈内存设计的合理性**

```java
// 虚拟机栈的设计原理
public class StackDesignPrinciple {
    
    public void methodA() {
        int localVar1 = 10;  // 局部变量存储在栈帧中
        String localVar2 = "hello";  // 引用存储在栈中，对象在堆中
        
        methodB(localVar1);  // 新栈帧压入
    }  // 栈帧弹出，局部变量自动回收
    
    private void methodB(int param) {
        int localVar3 = param * 2;
        // 每个方法都有独立的栈帧
    }
    
    /*
     * 栈设计优势：
     * 1. 自动管理：方法结束自动回收
     * 2. 线程隔离：每个线程独立栈空间
     * 3. 高效分配：栈顶指针移动即可
     * 4. 无碎片：连续内存分配
     */
}
```

**6. 程序计数器的必要性**

```java
// 程序计数器的作用
public class ProgramCounterDemo {
    
    public void demonstratePC() {
        int a = 1;        // PC指向这条指令
        int b = 2;        // PC移动到下一条指令
        int c = a + b;    // PC继续移动
        
        // 多线程环境下，每个线程需要独立的PC
        Thread thread1 = new Thread(() -> {
            // 线程1有自己的PC
            for (int i = 0; i < 100; i++) {
                System.out.println("Thread1: " + i);
            }
        });
        
        Thread thread2 = new Thread(() -> {
            // 线程2有自己的PC
            for (int i = 0; i < 100; i++) {
                System.out.println("Thread2: " + i);
            }
        });
    }
    
    /*
     * 为什么需要程序计数器？
     * 1. 线程切换：保存和恢复执行位置
     * 2. 分支跳转：记录下一条指令地址
     * 3. 异常处理：定位异常发生位置
     * 4. 调试支持：提供执行轨迹信息
     */
}
```

**Q: 直接内存是什么？有什么作用？**
- NIO操作使用的堆外内存
- 避免Java堆与Native堆之间的数据拷贝
- 不受Java堆大小限制，但受物理内存限制

**7. 直接内存设计的必要性**

```java
// 直接内存的优势对比
public class DirectMemoryComparison {
    
    // 传统I/O操作（多次拷贝）
    public void traditionalIO() throws IOException {
        FileInputStream fis = new FileInputStream("file.txt");
        byte[] buffer = new byte[1024];
        
        /*
         * 数据流转：
         * 磁盘 -> OS内核缓冲区 -> JVM堆内存 -> 应用程序
         * 问题：多次内存拷贝，性能低下
         */
        fis.read(buffer);  // 数据先复制到JVM堆，再返回
    }
    
    // NIO直接内存操作（零拷贝）
    public void directMemoryIO() throws IOException {
        FileChannel channel = FileChannel.open(Paths.get("file.txt"));
        ByteBuffer directBuffer = ByteBuffer.allocateDirect(1024);
        
        /*
         * 数据流转：
         * 磁盘 -> OS内核缓冲区 -> 直接内存 -> 应用程序
         * 优势：减少一次内存拷贝，提高性能
         */
        channel.read(directBuffer);  // 直接读取到直接内存
    }
}
```

**8. 内存模型设计的核心原则**

```java
// 内存区域职责划分原则
public class MemoryRegionPrinciples {
    
    /*
     * 1. 单一职责原则（SRP）
     * - 堆：只负责对象存储
     * - 栈：只负责方法调用和局部变量
     * - 方法区：只负责类元数据
     * - PC：只负责执行位置记录
     */
    
    /*
     * 2. 性能优先原则
     * - 快速分配：栈分配比堆分配快数百倍
     * - 高效回收：分代GC比全堆GC效率高
     * - 缓存友好：相关数据聚集存放
     */
    
    /*
     * 3. 线程安全原则
     * - 栈隔离：每个线程独立栈空间
     * - 堆共享：所有线程共享对象数据
     * - PC独立：支持并发执行
     */
}
```

**9. 与其他内存模型的对比**

```java
// 对比其他可能的内存模型
public class MemoryModelComparison {
    
    // 1. 如果采用C/C++式内存模型
    public class CStyleMemoryModel {
        /*
         * C/C++模式问题：
         * 1. 内存泄漏：程序员手动管理内存
         * 2. 野指针：访问已释放的内存
         * 3. 缓冲区溢出：数组越界访问
         * 4. 开发效率低：需要大量内存管理代码
         */
    }
    
    // 2. 如果采用纯垂圾回收模型
    public class PureGCModel {
        /*
         * 纯垃圾回收模式问题：
         * 1. GC停顿时间不可控
         * 2. 内存分配性能不稳定
         * 3. 难以预测GC行为
         * 4. 实时性要求难以满足
         */
    }
    
    // 3. JVM混合模式的优势
    public class HybridJVMModel {
        /*
         * JVM混合模式优势：
         * 1. 自动内存管理 + 手动优化空间
         * 2. 分代回收 + 栈自动管理
         * 3. 安全性 + 性能平衡
         * 4. 跨平台一致性
         */
    }
}
```

**10. 内存模型进化历史**

```java
// JVM内存模型的历史演变
public class MemoryModelEvolution {
    
    // JDK 1.0-1.2: 原始模型
    public class EarlyModel {
        /*
         * 早期设计：
         * - 简单的堆/栈分离
         * - 永久代（PermGen）概念
         * - 基本的分代GC
         */
    }
    
    // JDK 1.3-1.7: 成熟模型
    public class MatureModel {
        /*
         * 成熟阶段：
         * - 完善的分代回收
         * - 多种垃圾收集器
         * - JIT编译优化
         */
    }
    
    // JDK 1.8+: 现代模型
    public class ModernModel {
        /*
         * 现代设计：
         * - 移除PermGen，引入Metaspace
         * - G1/ZGC等低延迟收集器
         * - NUMA感知的内存管理
         * - 压缩指针技术
         */
    }
}
```

**总结：JVM内存模型设计的核心智慧**

1. **科学分区**：基于对象生命周期特性进行区域划分
2. **性能优先**：为不同类型的内存操作提供最优策略
3. **安全保障**：自动内存管理，避免常见的内存错误
4. **灵活可调**：提供丰富的调优参数和策略选择
5. **未来导向**：设计具有前瞻性，能够适应硕件发展

### 1.2 垃圾回收
**Q: 常见的垃圾收集器及其特点？**
- **Serial GC**：单线程，适合小型应用
- **Parallel GC**：多线程，适合吞吐量优先
- **CMS**：并发收集，低延迟
- **G1**：分区收集，平衡吞吐量和延迟
- **ZGC/Shenandoah**：超低延迟收集器

**Q: GC调优的策略和方法？**
- 监控GC频率和停顿时间
- 合理设置堆大小和分代比例
- 选择合适的垃圾收集器
- 优化代码减少对象创建

### 1.3 类加载机制
**Q: 双亲委派模型的原理？**
- 类加载器层次：Bootstrap → Extension → Application → Custom
- 向上委派：先让父加载器尝试加载
- 向下委派：父加载器无法加载时，子加载器加载
- 好处：保证类的唯一性，防止核心类被篡改

**Q: 为什么是双亲委派，而不是其他模型？**

#### 双亲委派模型的设计动机

1. **安全性考虑**
   - 防止核心API被恶意替换
   - 确保Java核心类库的完整性
   - 避免自定义类覆盖系统类

2. **类的唯一性保证**
   - 同一个类只能被同一个类加载器加载一次
   - 避免类的重复加载
   - 保证JVM中类的一致性

#### 其他可能的类加载模型对比

```java
// 1. 自底向上模型（如果采用这种模式）
public class BottomUpClassLoader extends ClassLoader {
    @Override
    protected Class<?> loadClass(String name, boolean resolve) {
        // 问题：子加载器先加载，可能导致安全问题
        Class<?> clazz = findLoadedClass(name);
        if (clazz == null) {
            try {
                // 先尝试自己加载
                clazz = findClass(name);
            } catch (ClassNotFoundException e) {
                // 失败后委派给父加载器
                clazz = getParent().loadClass(name);
            }
        }
        return clazz;
    }
}

// 问题分析：
// 1. 安全风险：恶意代码可以先加载java.lang.String等核心类
// 2. 类冲突：不同加载器可能加载相同的类，导致ClassCastException
// 3. 性能问题：重复加载相同的类
```

```java
// 2. 平级加载模型（如果采用这种模式）
public class PeerClassLoader extends ClassLoader {
    @Override
    protected Class<?> loadClass(String name, boolean resolve) {
        // 问题：所有加载器地位相同，无优先级
        Class<?> clazz = findLoadedClass(name);
        if (clazz == null) {
            // 随机选择一个加载器加载
            clazz = findClass(name);
        }
        return clazz;
    }
}

// 问题分析：
// 1. 无法保证核心类的优先级
// 2. 类加载顺序不确定
// 3. 难以实现类的层次化管理
```

#### 双亲委派模型的实现机制

```java
// JDK中ClassLoader的loadClass方法实现
public abstract class ClassLoader {
    
    protected Class<?> loadClass(String name, boolean resolve)
        throws ClassNotFoundException {
        
        synchronized (getClassLoadingLock(name)) {
            // 1. 首先检查类是否已经被加载
            Class<?> c = findLoadedClass(name);
            
            if (c == null) {
                long t0 = System.nanoTime();
                try {
                    // 2. 委派给父加载器
                    if (parent != null) {
                        c = parent.loadClass(name, false);
                    } else {
                        // 3. 父加载器为null，委派给启动类加载器
                        c = findBootstrapClassOrNull(name);
                    }
                } catch (ClassNotFoundException e) {
                    // 父加载器无法加载时，才尝试自己加载
                }
                
                if (c == null) {
                    // 4. 父加载器无法加载，自己尝试加载
                    long t1 = System.nanoTime();
                    c = findClass(name);
                }
            }
            
            if (resolve) {
                resolveClass(c);
            }
            return c;
        }
    }
}
```

#### 双亲委派模型的优势验证

```java
// 验证类的唯一性
public class ClassLoaderTest {
    
    public static void main(String[] args) throws Exception {
        // 测试：尝试自定义String类
        CustomClassLoader loader1 = new CustomClassLoader();
        CustomClassLoader loader2 = new CustomClassLoader();
        
        // 即使使用不同的类加载器，java.lang.String都会被Bootstrap ClassLoader加载
        Class<?> stringClass1 = loader1.loadClass("java.lang.String");
        Class<?> stringClass2 = loader2.loadClass("java.lang.String");
        
        System.out.println("String类是否相同: " + (stringClass1 == stringClass2));
        System.out.println("String类加载器: " + stringClass1.getClassLoader());
        
        // 输出：
        // String类是否相同: true
        // String类加载器: null (Bootstrap ClassLoader)
    }
}

class CustomClassLoader extends ClassLoader {
    // 自定义类加载器
}
```

#### 打破双亲委派的场景

```java
// 某些特殊场景需要打破双亲委派
public class BreakParentDelegation extends ClassLoader {
    
    @Override
    protected Class<?> loadClass(String name, boolean resolve)
        throws ClassNotFoundException {
        
        // 特殊情况：热部署、插件系统等
        if (needBreakParentDelegation(name)) {
            Class<?> clazz = findLoadedClass(name);
            if (clazz == null) {
                try {
                    // 直接自己加载，不委派给父加载器
                    clazz = findClass(name);
                } catch (ClassNotFoundException e) {
                    // 失败后再委派给父加载器
                    clazz = super.loadClass(name, resolve);
                }
            }
            return clazz;
        }
        
        // 其他情况遵循双亲委派
        return super.loadClass(name, resolve);
    }
    
    private boolean needBreakParentDelegation(String className) {
        // 判断是否需要打破双亲委派
        return className.startsWith("com.example.plugin.");
    }
}
```

#### 实际应用案例

```java
// Web应用中的类加载隔离
public class WebAppClassLoader extends ClassLoader {
    
    private String webAppPath;
    
    public WebAppClassLoader(String webAppPath, ClassLoader parent) {
        super(parent);
        this.webAppPath = webAppPath;
    }
    
    @Override
    protected Class<?> findClass(String name) throws ClassNotFoundException {
        // 从Web应用的WEB-INF/classes或WEB-INF/lib加载类
        byte[] classData = loadClassData(name);
        if (classData != null) {
            return defineClass(name, classData, 0, classData.length);
        }
        throw new ClassNotFoundException(name);
    }
    
    private byte[] loadClassData(String className) {
        // 从Web应用目录加载类文件
        String classFile = className.replace('.', '/') + ".class";
        String fullPath = webAppPath + "/WEB-INF/classes/" + classFile;
        
        try {
            return Files.readAllBytes(Paths.get(fullPath));
        } catch (IOException e) {
            return null;
        }
    }
}
```

**总结：为什么选择双亲委派模型？**

1. **安全性第一**：确保核心类不被恶意替换
2. **类的一致性**：保证同名类在JVM中的唯一性
3. **层次化管理**：清晰的类加载器层次结构
4. **性能优化**：避免重复加载，缓存已加载的类
5. **模块化支持**：为OSGi等模块化框架提供基础

双亲委派模型虽然有一定的局限性（如无法实现真正的热部署），但其设计充分考虑了Java平台的安全性和稳定性要求，是经过深思熟虑的设计选择。

### 1.4 JVM 调优实战
```bash
# 常用JVM参数
-Xms4g -Xmx4g                    # 堆内存大小
-XX:NewRatio=3                   # 新生代与老年代比例
-XX:SurvivorRatio=8              # Eden与Survivor比例
-XX:+UseG1GC                     # 使用G1垃圾收集器
-XX:MaxGCPauseMillis=200         # 最大GC停顿时间
-XX:+PrintGCDetails              # 打印GC详细信息
-XX:+HeapDumpOnOutOfMemoryError  # OOM时生成堆转储
```

## 2. 并发编程

### 2.1 线程基础
**Q: 线程的生命周期状态？**
- NEW：创建但未启动
- RUNNABLE：可运行状态（包含运行中和就绪）
- BLOCKED：阻塞等待锁
- WAITING：无限期等待
- TIMED_WAITING：有时限等待
- TERMINATED：终止

**Q: synchronized和volatile的区别？**
- synchronized：保证原子性、可见性、有序性
- volatile：只保证可见性和有序性，不保证原子性
- synchronized可以修饰方法和代码块
- volatile只能修饰变量

### 2.2 锁机制
**Q: ReentrantLock vs synchronized？**
- **功能对比**：
  - ReentrantLock：可中断、可超时、公平锁选择
  - synchronized：不可中断、不可超时、非公平
- **性能对比**：Java 6后synchronized优化，性能接近
- **使用场景**：复杂场景用ReentrantLock，简单场景用synchronized

**Q: AQS（AbstractQueuedSynchronizer）原理？**
- 基于FIFO队列的同步器框架
- 使用state变量表示同步状态
- 支持独占模式和共享模式
- ReentrantLock、CountDownLatch等基于AQS实现

### 2.3 并发工具类
**Q: 线程池的核心参数？**
```java
ThreadPoolExecutor(
    int corePoolSize,      // 核心线程数
    int maximumPoolSize,   // 最大线程数
    long keepAliveTime,    // 空闲线程存活时间
    TimeUnit unit,         // 时间单位
    BlockingQueue<Runnable> workQueue,  // 任务队列
    ThreadFactory threadFactory,        // 线程工厂
    RejectedExecutionHandler handler    // 拒绝策略
)
```

**Q: 常见的阻塞队列？**
- ArrayBlockingQueue：有界数组队列
- LinkedBlockingQueue：无界链表队列
- SynchronousQueue：不存储元素的队列
- PriorityBlockingQueue：优先级队列

### 2.4 并发编程实战代码

#### 生产者消费者模式
```java
public class ProducerConsumer {
    private final BlockingQueue<Integer> queue;
    private final int capacity;
    
    public ProducerConsumer(int capacity) {
        this.capacity = capacity;
        this.queue = new ArrayBlockingQueue<>(capacity);
    }
    
    public void produce() throws InterruptedException {
        int value = 0;
        while (true) {
            queue.put(value);
            System.out.println("Produced: " + value);
            value++;
            Thread.sleep(1000);
        }
    }
    
    public void consume() throws InterruptedException {
        while (true) {
            int value = queue.take();
            System.out.println("Consumed: " + value);
            Thread.sleep(1500);
        }
    }
}
```

#### 线程安全的单例模式
```java
public class Singleton {
    private static volatile Singleton instance;
    
    private Singleton() {}
    
    // 双重检查锁定
    public static Singleton getInstance() {
        if (instance == null) {
            synchronized (Singleton.class) {
                if (instance == null) {
                    instance = new Singleton();
                }
            }
        }
        return instance;
    }
}

// 更优雅的实现 - 枚举单例
public enum SingletonEnum {
    INSTANCE;
    
    public void doSomething() {
        // 业务逻辑
    }
}
```

#### 使用CompletableFuture进行异步编程
```java
public class AsyncExample {
    public CompletableFuture<String> processAsync(String input) {
        return CompletableFuture
            .supplyAsync(() -> {
                // 第一步处理
                return "processed-" + input;
            })
            .thenCompose(result -> 
                CompletableFuture.supplyAsync(() -> {
                    // 第二步处理
                    return result.toUpperCase();
                })
            )
            .thenApply(result -> {
                // 最终处理
                return "[" + result + "]";
            })
            .exceptionally(ex -> {
                // 异常处理
                return "Error: " + ex.getMessage();
            });
    }
}
```

## 3. 集合框架

### 3.1 List 实现
**Q: ArrayList vs LinkedList 性能对比？**
- **ArrayList**：
  - 随机访问O(1)，插入删除O(n)
  - 基于数组，内存连续，缓存友好
  - 适合读多写少场景
- **LinkedList**：
  - 随机访问O(n)，插入删除O(1)
  - 基于链表，内存不连续
  - 适合频繁插入删除场景

### 3.2 Map 实现
**Q: HashMap的底层实现原理？**
- **JDK 1.7**：数组 + 链表
- **JDK 1.8+**：数组 + 链表 + 红黑树
- 当链表长度 > 8且数组长度 > 64时转为红黑树
- 扩容机制：容量翻倍，重新hash分布

**Q: ConcurrentHashMap的实现原理？**
- **JDK 1.7**：分段锁（Segment）
- **JDK 1.8+**：CAS + synchronized
- 使用volatile保证可见性
- 支持高并发读写操作

### 3.3 集合性能优化
```java
// ArrayList预分配容量
List<String> list = new ArrayList<>(1000);

// HashMap预分配容量，避免扩容
Map<String, String> map = new HashMap<>(16);

// 使用StringBuilder进行字符串拼接
StringBuilder sb = new StringBuilder(100);
```

## 4. Spring 框架

### 4.1 IOC 容器
**Q: Spring IOC的实现原理？**
- 控制反转：对象创建控制权交给Spring
- 依赖注入：Spring负责注入对象依赖
- BeanFactory：基础容器接口
- ApplicationContext：高级容器，提供更多功能

**Q: Bean的生命周期？**
1. 实例化Bean
2. 设置Bean属性
3. 调用BeanNameAware、BeanFactoryAware等接口
4. 调用BeanPostProcessor的前置处理
5. 调用InitializingBean接口或init-method
6. 调用BeanPostProcessor的后置处理
7. Bean可以使用
8. 容器关闭时调用DisposableBean或destroy-method

### 4.2 AOP 切面
**Q: AOP的实现原理？**
- **JDK动态代理**：基于接口代理
- **CGLIB代理**：基于类继承代理
- Spring默认：有接口用JDK，无接口用CGLIB
- 切面执行顺序：Around → Before → 目标方法 → After → AfterReturning/AfterThrowing

### 4.3 Spring Boot
**Q: Spring Boot自动配置原理？**
- @SpringBootApplication包含@EnableAutoConfiguration
- 扫描META-INF/spring.factories文件
- 根据条件注解决定是否创建Bean
- @ConditionalOnClass、@ConditionalOnProperty等

### 4.4 Spring 源码分析
```java
// 简化的IOC容器实现示例
public class SimpleIOCContainer {
    private Map<String, Object> beanMap = new ConcurrentHashMap<>();
    
    public void registerBean(String name, Object bean) {
        beanMap.put(name, bean);
    }
    
    @SuppressWarnings("unchecked")
    public <T> T getBean(String name, Class<T> clazz) {
        Object bean = beanMap.get(name);
        if (bean == null) {
            throw new NoSuchBeanException("No bean named '" + name + "'");
        }
        return (T) bean;
    }
}
```

## 5. 数据库

### 5.1 MySQL 优化
**Q: SQL查询优化策略？**
- 创建合适的索引（B+树结构）
- 避免SELECT *，只查询需要的字段
- 使用LIMIT限制返回行数
- 避免在WHERE子句中使用函数
- 合理使用JOIN，小表驱动大表

**Q: 索引的类型和使用场景？**
- **主键索引**：唯一且非空
- **唯一索引**：值唯一但可为空
- **普通索引**：提高查询效率
- **组合索引**：多列组合，注意最左前缀原则
- **覆盖索引**：索引包含所需字段，避免回表

### 5.2 事务机制
**Q: 事务的ACID特性？**
- **原子性（Atomicity）**：全部成功或全部失败
- **一致性（Consistency）**：数据库状态一致
- **隔离性（Isolation）**：并发事务相互隔离
- **持久性（Durability）**：已提交事务永久保存

**Q: 事务隔离级别？**
- READ UNCOMMITTED：可能脏读
- READ COMMITTED：避免脏读，可能不可重复读
- REPEATABLE READ：避免脏读和不可重复读，可能幻读
- SERIALIZABLE：最高隔离级别，避免所有问题

### 5.3 连接池
```java
// HikariCP连接池配置示例
@Configuration
public class DataSourceConfig {
    
    @Bean
    @Primary
    public DataSource dataSource() {
        HikariConfig config = new HikariConfig();
        config.setJdbcUrl("jdbc:mysql://localhost:3306/test");
        config.setUsername("root");
        config.setPassword("password");
        config.setMaximumPoolSize(20);          // 最大连接数
        config.setMinimumIdle(5);               // 最小空闲连接
        config.setConnectionTimeout(30000);     // 连接超时时间
        config.setIdleTimeout(600000);          // 空闲连接超时时间
        return new HikariDataSource(config);
    }
}
```

## 6. 分布式系统

### 6.1 微服务架构
**Q: 微服务的优缺点？**
**优点**：
- 技术栈灵活
- 独立部署和扩展
- 故障隔离
- 团队独立开发

**缺点**：
- 分布式复杂性
- 服务间通信成本
- 数据一致性挑战
- 运维复杂度增加

### 6.2 分布式事务
**Q: 分布式事务解决方案？**
- **2PC（两阶段提交）**：强一致性，性能较差
- **TCC（Try-Confirm-Cancel）**：业务补偿机制
- **Saga模式**：长事务拆分，本地事务 + 补偿
- **最终一致性**：基于消息的异步处理

#### 分布式事务详细实现案例

**1. 2PC（两阶段提交）分布式实现示例**

```java
// 分布式事务协调器（运行在独立的协调器节点）
@RestController
@RequestMapping("/transaction-coordinator")
public class DistributedTransactionCoordinator {
    
    @Autowired
    private ParticipantRegistry participantRegistry;
    
    @Autowired
    private RestTemplate restTemplate;
    
    @Autowired
    private TransactionLogService transactionLogService;
    
    // 分布式事务入口
    @PostMapping("/execute")
    public ResponseEntity<TransactionResult> executeDistributedTransaction(
            @RequestBody DistributedTransactionRequest request) {
        
        String transactionId = UUID.randomUUID().toString();
        
        // 记录事务开始
        transactionLogService.logTransactionStart(transactionId, request);
        
        try {
            // 获取所有分布式服务节点
            List<ParticipantNode> participants = participantRegistry
                .getParticipants(request.getTransactionType());
            
            // 第一阶段：向所有分布式节点发送prepare请求
            boolean allPrepared = executeDistributedPreparePhase(transactionId, participants, request);
            
            if (allPrepared) {
                // 第二阶段：向所有节点发送commit请求
                boolean allCommitted = executeDistributedCommitPhase(transactionId, participants);
                transactionLogService.logTransactionCommit(transactionId);
                return ResponseEntity.ok(TransactionResult.success(transactionId));
            } else {
                // 第二阶段：向所有节点发送rollback请求
                executeDistributedRollbackPhase(transactionId, participants);
                transactionLogService.logTransactionRollback(transactionId);
                return ResponseEntity.ok(TransactionResult.failure(transactionId, "Prepare phase failed"));
            }
        } catch (Exception e) {
            // 异常情况下执行分布式回滚
            executeDistributedRollbackPhase(transactionId, 
                participantRegistry.getParticipants(request.getTransactionType()));
            transactionLogService.logTransactionError(transactionId, e.getMessage());
            return ResponseEntity.status(500)
                .body(TransactionResult.error(transactionId, e.getMessage()));
        }
    }
    
    // 分布式Prepare阶段
    private boolean executeDistributedPreparePhase(String transactionId, 
                                                   List<ParticipantNode> participants,
                                                   DistributedTransactionRequest request) {
        
        List<CompletableFuture<Boolean>> prepareFutures = new ArrayList<>();
        
        // 并发向所有分布式节点发送prepare请求
        for (ParticipantNode participant : participants) {
            CompletableFuture<Boolean> future = CompletableFuture.supplyAsync(() -> {
                try {
                    // 网络调用远程服务的prepare接口
                    String url = participant.getBaseUrl() + "/transaction/prepare";
                    PrepareRequest prepareRequest = new PrepareRequest(transactionId, request.getData());
                    
                    ResponseEntity<PrepareResponse> response = restTemplate.postForEntity(
                        url, prepareRequest, PrepareResponse.class);
                    
                    return response.getBody() != null && response.getBody().isSuccess();
                } catch (Exception e) {
                    log.error("Prepare failed for participant: {} at {}", 
                        participant.getServiceName(), participant.getBaseUrl(), e);
                    return false;
                }
            });
            prepareFutures.add(future);
        }
        
        // 等待所有远程调用完成
        try {
            return prepareFutures.stream()
                .map(CompletableFuture::join)
                .allMatch(result -> result);
        } catch (Exception e) {
            log.error("Prepare phase failed", e);
            return false;
        }
    }
    
    // 分布式Commit阶段
    private boolean executeDistributedCommitPhase(String transactionId, 
                                                 List<ParticipantNode> participants) {
        List<CompletableFuture<Boolean>> commitFutures = new ArrayList<>();
        
        for (ParticipantNode participant : participants) {
            CompletableFuture<Boolean> future = CompletableFuture.supplyAsync(() -> {
                try {
                    // 网络调用远程服务的commit接口
                    String url = participant.getBaseUrl() + "/transaction/commit";
                    CommitRequest commitRequest = new CommitRequest(transactionId);
                    
                    ResponseEntity<CommitResponse> response = restTemplate.postForEntity(
                        url, commitRequest, CommitResponse.class);
                    
                    return response.getBody() != null && response.getBody().isSuccess();
                } catch (Exception e) {
                    log.error("Commit failed for participant: {} at {}", 
                        participant.getServiceName(), participant.getBaseUrl(), e);
                    // commit失败需要重试机制
                    scheduleRetryCommit(participant, transactionId);
                    return false;
                }
            });
            commitFutures.add(future);
        }
        
        // 等待所有分布式节点commit完成
        try {
            return commitFutures.stream()
                .map(CompletableFuture::join)
                .allMatch(result -> result);
        } catch (Exception e) {
            log.error("Commit phase failed", e);
            return false;
        }
    }
    
    // 分布式Rollback阶段
    private void executeDistributedRollbackPhase(String transactionId, 
                                                List<ParticipantNode> participants) {
        // 并发向所有分布式节点发送rollback请求
        participants.parallelStream().forEach(participant -> {
            try {
                String url = participant.getBaseUrl() + "/transaction/rollback";
                RollbackRequest rollbackRequest = new RollbackRequest(transactionId);
                
                ResponseEntity<RollbackResponse> response = restTemplate.postForEntity(
                    url, rollbackRequest, RollbackResponse.class);
                
                if (response.getBody() == null || !response.getBody().isSuccess()) {
                    log.error("Rollback failed for participant: {} at {}", 
                        participant.getServiceName(), participant.getBaseUrl());
                }
            } catch (Exception e) {
                log.error("Rollback failed for participant: {} at {}", 
                    participant.getServiceName(), participant.getBaseUrl(), e);
            }
        });
    }
}

// 参与者节点信息（代表不同的分布式服务）
@Entity
@Table(name = "participant_nodes")
public class ParticipantNode {
    private String serviceId;
    private String serviceName;
    private String baseUrl;  // 远程服务地址，如：http://order-service:8081
    private String ipAddress;
    private int port;
    private boolean isActive;
    
    // getters and setters...
}

// 参与者注册中心（服务发现）
@Service
public class ParticipantRegistry {
    
    @Autowired
    private ParticipantNodeRepository nodeRepository;
    
    @Autowired
    private EurekaClient eurekaClient;  // 或者使用Consul、Nacos等
    
    public List<ParticipantNode> getParticipants(String transactionType) {
        // 根据事务类型获取相关的分布式服务节点
        switch (transactionType) {
            case "ORDER_TRANSACTION":
                return Arrays.asList(
                    findServiceNode("order-service"),
                    findServiceNode("inventory-service"),
                    findServiceNode("payment-service")
                );
            case "TRANSFER_TRANSACTION":
                return Arrays.asList(
                    findServiceNode("account-service"),
                    findServiceNode("audit-service")
                );
            default:
                return nodeRepository.findByIsActiveTrue();
        }
    }
    
    private ParticipantNode findServiceNode(String serviceName) {
        // 从服务注册中心获取服务实例
        List<InstanceInfo> instances = eurekaClient.getInstancesByVipAddress(serviceName, false);
        
        if (!instances.isEmpty()) {
            InstanceInfo instance = instances.get(0);  // 简化处理，实际可以负载均衡
            return new ParticipantNode()
                .setServiceName(serviceName)
                .setBaseUrl("http://" + instance.getHostName() + ":" + instance.getPort())
                .setIpAddress(instance.getIPAddr())
                .setPort(instance.getPort())
                .setActive(true);
        }
        
        throw new ServiceNotFoundException("Service not found: " + serviceName);
    }
}
```

```java
// 订单服务（独立的微服务，运行在不同的JVM/容器中）
@RestController
@RequestMapping("/transaction")
public class OrderServiceParticipant {
    
    @Autowired
    private OrderService orderService;
    
    @Autowired
    private TransactionResourceManager resourceManager;
    
    // 处理来自协调器的prepare请求
    @PostMapping("/prepare")
    public ResponseEntity<PrepareResponse> prepare(@RequestBody PrepareRequest request) {
        String transactionId = request.getTransactionId();
        
        try {
            log.info("[OrderService] Received prepare request for transaction: {}", transactionId);
            
            // 执行业务逻辑检查和资源预留
            OrderData orderData = (OrderData) request.getData();
            
            // 1. 验证订单数据
            if (!orderService.validateOrder(orderData)) {
                return ResponseEntity.ok(PrepareResponse.failure("订单数据无效"));
            }
            
            // 2. 预留资源（但不真正执行业务操作）
            boolean resourceReserved = resourceManager.reserveResources(transactionId, orderData);
            
            if (resourceReserved) {
                log.info("[OrderService] Prepare successful for transaction: {}", transactionId);
                return ResponseEntity.ok(PrepareResponse.success());
            } else {
                log.warn("[OrderService] Prepare failed - resource reservation failed for transaction: {}", transactionId);
                return ResponseEntity.ok(PrepareResponse.failure("资源预留失败"));
            }
            
        } catch (Exception e) {
            log.error("[OrderService] Prepare error for transaction: {}", transactionId, e);
            return ResponseEntity.ok(PrepareResponse.failure(e.getMessage()));
        }
    }
    
    // 处理来自协调器的commit请求
    @PostMapping("/commit")
    public ResponseEntity<CommitResponse> commit(@RequestBody CommitRequest request) {
        String transactionId = request.getTransactionId();
        
        try {
            log.info("[OrderService] Received commit request for transaction: {}", transactionId);
            
            // 执行真正的业务操作
            boolean committed = resourceManager.commitTransaction(transactionId);
            
            if (committed) {
                log.info("[OrderService] Commit successful for transaction: {}", transactionId);
                return ResponseEntity.ok(CommitResponse.success());
            } else {
                log.error("[OrderService] Commit failed for transaction: {}", transactionId);
                return ResponseEntity.ok(CommitResponse.failure("提交失败"));
            }
            
        } catch (Exception e) {
            log.error("[OrderService] Commit error for transaction: {}", transactionId, e);
            return ResponseEntity.ok(CommitResponse.failure(e.getMessage()));
        }
    }
    
    // 处理来自协调器的rollback请求
    @PostMapping("/rollback")
    public ResponseEntity<RollbackResponse> rollback(@RequestBody RollbackRequest request) {
        String transactionId = request.getTransactionId();
        
        try {
            log.info("[OrderService] Received rollback request for transaction: {}", transactionId);
            
            // 清理预留的资源
            boolean rolledBack = resourceManager.rollbackTransaction(transactionId);
            
            if (rolledBack) {
                log.info("[OrderService] Rollback successful for transaction: {}", transactionId);
                return ResponseEntity.ok(RollbackResponse.success());
            } else {
                log.warn("[OrderService] Rollback failed for transaction: {}", transactionId);
                return ResponseEntity.ok(RollbackResponse.failure("回滚失败"));
            }
            
        } catch (Exception e) {
            log.error("[OrderService] Rollback error for transaction: {}", transactionId, e);
            return ResponseEntity.ok(RollbackResponse.failure(e.getMessage()));
        }
    }
}

// 库存服务（另一个独立的微服务）
@RestController
@RequestMapping("/transaction")
public class InventoryServiceParticipant {
    
    @Autowired
    private InventoryService inventoryService;
    
    @PostMapping("/prepare")
    public ResponseEntity<PrepareResponse> prepare(@RequestBody PrepareRequest request) {
        String transactionId = request.getTransactionId();
        
        try {
            log.info("[InventoryService] Received prepare request for transaction: {}", transactionId);
            
            OrderData orderData = (OrderData) request.getData();
            
            // 检查库存是否充足
            boolean hasEnoughStock = inventoryService.checkStock(
                orderData.getProductId(), orderData.getQuantity());
            
            if (hasEnoughStock) {
                // 预留库存（锁定但不真正扣减）
                boolean reserved = inventoryService.reserveStock(
                    transactionId, orderData.getProductId(), orderData.getQuantity());
                
                if (reserved) {
                    log.info("[InventoryService] Prepare successful for transaction: {}", transactionId);
                    return ResponseEntity.ok(PrepareResponse.success());
                }
            }
            
            log.warn("[InventoryService] Prepare failed - insufficient stock for transaction: {}", transactionId);
            return ResponseEntity.ok(PrepareResponse.failure("库存不足"));
            
        } catch (Exception e) {
            log.error("[InventoryService] Prepare error for transaction: {}", transactionId, e);
            return ResponseEntity.ok(PrepareResponse.failure(e.getMessage()));
        }
    }
    
    @PostMapping("/commit")
    public ResponseEntity<CommitResponse> commit(@RequestBody CommitRequest request) {
        String transactionId = request.getTransactionId();
        
        try {
            log.info("[InventoryService] Received commit request for transaction: {}", transactionId);
            
            // 真正扣减库存
            boolean committed = inventoryService.confirmStockReduction(transactionId);
            
            if (committed) {
                log.info("[InventoryService] Commit successful for transaction: {}", transactionId);
                return ResponseEntity.ok(CommitResponse.success());
            } else {
                log.error("[InventoryService] Commit failed for transaction: {}", transactionId);
                return ResponseEntity.ok(CommitResponse.failure("库存扣减失败"));
            }
            
        } catch (Exception e) {
            log.error("[InventoryService] Commit error for transaction: {}", transactionId, e);
            return ResponseEntity.ok(CommitResponse.failure(e.getMessage()));
        }
    }
    
    @PostMapping("/rollback")
    public ResponseEntity<RollbackResponse> rollback(@RequestBody RollbackRequest request) {
        String transactionId = request.getTransactionId();
        
        try {
            log.info("[InventoryService] Received rollback request for transaction: {}", transactionId);
            
            // 释放预留的库存
            boolean rolledBack = inventoryService.releaseReservedStock(transactionId);
            
            if (rolledBack) {
                log.info("[InventoryService] Rollback successful for transaction: {}", transactionId);
                return ResponseEntity.ok(RollbackResponse.success());
            } else {
                log.warn("[InventoryService] Rollback failed for transaction: {}", transactionId);
                return ResponseEntity.ok(RollbackResponse.failure("库存释放失败"));
            }
            
        } catch (Exception e) {
            log.error("[InventoryService] Rollback error for transaction: {}", transactionId, e);
            return ResponseEntity.ok(RollbackResponse.failure(e.getMessage()));
        }
    }
}

// 支付服务（第三个独立的微服务）
@RestController
@RequestMapping("/transaction")
public class PaymentServiceParticipant {
    
    @Autowired
    private PaymentService paymentService;
    
    @PostMapping("/prepare")
    public ResponseEntity<PrepareResponse> prepare(@RequestBody PrepareRequest request) {
        String transactionId = request.getTransactionId();
        
        try {
            log.info("[PaymentService] Received prepare request for transaction: {}", transactionId);
            
            OrderData orderData = (OrderData) request.getData();
            
            // 检查账户余额
            boolean hasEnoughBalance = paymentService.checkBalance(
                orderData.getUserId(), orderData.getTotalAmount());
            
            if (hasEnoughBalance) {
                // 冻结资金（预留但不真正扣款）
                boolean frozen = paymentService.freezeAmount(
                    transactionId, orderData.getUserId(), orderData.getTotalAmount());
                
                if (frozen) {
                    log.info("[PaymentService] Prepare successful for transaction: {}", transactionId);
                    return ResponseEntity.ok(PrepareResponse.success());
                }
            }
            
            log.warn("[PaymentService] Prepare failed - insufficient balance for transaction: {}", transactionId);
            return ResponseEntity.ok(PrepareResponse.failure("余额不足"));
            
        } catch (Exception e) {
            log.error("[PaymentService] Prepare error for transaction: {}", transactionId, e);
            return ResponseEntity.ok(PrepareResponse.failure(e.getMessage()));
        }
    }
    
    @PostMapping("/commit")
    public ResponseEntity<CommitResponse> commit(@RequestBody CommitRequest request) {
        String transactionId = request.getTransactionId();
        
        try {
            log.info("[PaymentService] Received commit request for transaction: {}", transactionId);
            
            // 真正扣款
            boolean committed = paymentService.confirmPayment(transactionId);
            
            if (committed) {
                log.info("[PaymentService] Commit successful for transaction: {}", transactionId);
                return ResponseEntity.ok(CommitResponse.success());
            } else {
                log.error("[PaymentService] Commit failed for transaction: {}", transactionId);
                return ResponseEntity.ok(CommitResponse.failure("扣款失败"));
            }
            
        } catch (Exception e) {
            log.error("[PaymentService] Commit error for transaction: {}", transactionId, e);
            return ResponseEntity.ok(CommitResponse.failure(e.getMessage()));
        }
    }
    
    @PostMapping("/rollback")
    public ResponseEntity<RollbackResponse> rollback(@RequestBody RollbackRequest request) {
        String transactionId = request.getTransactionId();
        
        try {
            log.info("[PaymentService] Received rollback request for transaction: {}", transactionId);
            
            // 解冻资金
            boolean rolledBack = paymentService.unfreezeAmount(transactionId);
            
            if (rolledBack) {
                log.info("[PaymentService] Rollback successful for transaction: {}", transactionId);
                return ResponseEntity.ok(RollbackResponse.success());
            } else {
                log.warn("[PaymentService] Rollback failed for transaction: {}", transactionId);
                return ResponseEntity.ok(RollbackResponse.failure("资金解冻失败"));
            }
            
        } catch (Exception e) {
            log.error("[PaymentService] Rollback error for transaction: {}", transactionId, e);
            return ResponseEntity.ok(RollbackResponse.failure(e.getMessage()));
        }
    }
}
```

**真正的分布式特征体现：**

1. **网络通信**：协调器通过HTTP/RPC与远程服务通信
2. **服务发现**：使用Eureka等注册中心发现分布式服务节点
3. **独立部署**：每个参与者都是独立的微服务，运行在不同JVM/容器中
4. **网络异常处理**：处理网络超时、连接失败等分布式环境特有问题
5. **并发处理**：并发向多个远程服务发送请求
6. **服务地址管理**：维护各个分布式服务的网络地址

这样的实现才真正体现了分布式2PC的特点！

**2. TCC（Try-Confirm-Cancel）分布式模式实现**

```java
// TCC分布式事务管理器（独立服务）
@RestController
@RequestMapping("/tcc-coordinator")
public class DistributedTCCTransactionManager {
    
    @Autowired
    private TCCParticipantRegistry participantRegistry;
    
    @Autowired
    private RestTemplate restTemplate;
    
    @PostMapping("/execute")
    public ResponseEntity<TCCTransactionResult> executeTCCTransaction(
            @RequestBody TCCTransactionRequest request) {
        
        String transactionId = UUID.randomUUID().toString();
        
        try {
            // 获取分布式参与者服务
            List<TCCParticipantNode> participants = participantRegistry
                .getTCCParticipants(request.getBusinessType());
            
            // Try阶段：并发调用各个分布式服务
            boolean allTrySuccess = executeDistributedTryPhase(transactionId, participants, request);
            
            if (allTrySuccess) {
                // Confirm阶段
                boolean allConfirmed = executeDistributedConfirmPhase(transactionId, participants);
                return ResponseEntity.ok(TCCTransactionResult.success(transactionId));
            } else {
                // Cancel阶段
                executeDistributedCancelPhase(transactionId, participants);
                return ResponseEntity.ok(TCCTransactionResult.failure(transactionId, "Try phase failed"));
            }
        } catch (Exception e) {
            return ResponseEntity.status(500)
                .body(TCCTransactionResult.error(transactionId, e.getMessage()));
        }
    }
    
    // 分布式Try阶段
    private boolean executeDistributedTryPhase(String transactionId,
                                             List<TCCParticipantNode> participants,
                                             TCCTransactionRequest request) {
        
        List<CompletableFuture<Boolean>> tryFutures = new ArrayList<>();
        
        // 并发调用所有分布式服务的try接口
        for (TCCParticipantNode participant : participants) {
            CompletableFuture<Boolean> future = CompletableFuture.supplyAsync(() -> {
                try {
                    String url = participant.getBaseUrl() + "/tcc/try";
                    TCCTryRequest tryRequest = new TCCTryRequest(transactionId, request.getBusinessContext());
                    
                    ResponseEntity<TCCTryResponse> response = restTemplate.postForEntity(
                        url, tryRequest, TCCTryResponse.class);
                    
                    return response.getBody() != null && response.getBody().isSuccess();
                } catch (Exception e) {
                    log.error("[TCC-Coordinator] Try failed for participant: {} at {}", 
                        participant.getServiceName(), participant.getBaseUrl(), e);
                    return false;
                }
            });
            tryFutures.add(future);
        }
        
        return tryFutures.stream()
            .map(CompletableFuture::join)
            .allMatch(result -> result);
    }
    
    // 其他方法类似...
}

// 库存服务TCC实现（独立微服务）
@RestController
@RequestMapping("/tcc")
public class DistributedInventoryServiceTCC {
    
    @Autowired
    private InventoryService inventoryService;
    
    @PostMapping("/try")
    public ResponseEntity<TCCTryResponse> tryExecute(@RequestBody TCCTryRequest request) {
        String transactionId = request.getTransactionId();
        
        try {
            log.info("[InventoryService-TCC] Received try request for transaction: {}", transactionId);
            
            BusinessContext context = request.getBusinessContext();
            Long productId = context.getProductId();
            Integer quantity = context.getQuantity();
            
            // Try阶段：检查库存并冻结
            boolean hasStock = inventoryService.checkAvailableStock(productId, quantity);
            
            if (hasStock) {
                boolean frozen = inventoryService.freezeInventory(transactionId, productId, quantity);
                if (frozen) {
                    log.info("[InventoryService-TCC] Try successful for transaction: {}", transactionId);
                    return ResponseEntity.ok(TCCTryResponse.success("库存冻结成功"));
                }
            }
            
            return ResponseEntity.ok(TCCTryResponse.failure("库存不足"));
            
        } catch (Exception e) {
            log.error("[InventoryService-TCC] Try error for transaction: {}", transactionId, e);
            return ResponseEntity.status(500).body(TCCTryResponse.error(e.getMessage()));
        }
    }
    
    @PostMapping("/confirm")
    public ResponseEntity<TCCConfirmResponse> confirm(@RequestBody TCCConfirmRequest request) {
        // 确认扣减库存逻辑...
        return ResponseEntity.ok(TCCConfirmResponse.success());
    }
    
    @PostMapping("/cancel")
    public ResponseEntity<TCCCancelResponse> cancel(@RequestBody TCCCancelRequest request) {
        // 释放冻结库存逻辑...
        return ResponseEntity.ok(TCCCancelResponse.success());
    }
}
```

**3. Saga模式分布式实现**

```java
// Saga分布式编排器（独立服务）
@RestController
@RequestMapping("/saga-orchestrator")
public class DistributedSagaOrchestrator {
    
    @Autowired
    private SagaStepRegistry stepRegistry;
    
    @Autowired
    private RestTemplate restTemplate;
    
    @PostMapping("/execute")
    public ResponseEntity<SagaExecutionResult> executeSaga(@RequestBody SagaRequest request) {
        String sagaId = UUID.randomUUID().toString();
        
        try {
            // 获取分布式步骤定义
            List<DistributedSagaStep> steps = stepRegistry.getSagaSteps(request.getBusinessType());
            
            // 顺序执行所有分布式步骤
            for (int i = 0; i < steps.size(); i++) {
                DistributedSagaStep step = steps.get(i);
                
                try {
                    // 调用远程服务执行步骤
                    StepResult result = executeDistributedStep(sagaId, step, request.getSagaContext());
                    
                    if (!result.isSuccess()) {
                        // 步骤失败，执行分布式补偿
                        executeDistributedCompensation(sagaId, steps, i);
                        return ResponseEntity.ok(SagaExecutionResult.failure(sagaId, "Step failed"));
                    }
                } catch (Exception e) {
                    executeDistributedCompensation(sagaId, steps, i);
                    return ResponseEntity.status(500)
                        .body(SagaExecutionResult.error(sagaId, e.getMessage()));
                }
            }
            
            return ResponseEntity.ok(SagaExecutionResult.success(sagaId));
            
        } catch (Exception e) {
            return ResponseEntity.status(500)
                .body(SagaExecutionResult.error(sagaId, e.getMessage()));
        }
    }
    
    // 执行分布式步骤
    private StepResult executeDistributedStep(String sagaId, DistributedSagaStep step, SagaContext context) {
        try {
            String url = step.getServiceUrl() + step.getExecutionEndpoint();
            SagaStepRequest stepRequest = new SagaStepRequest(sagaId, context);
            
            ResponseEntity<SagaStepResponse> response = restTemplate.postForEntity(
                url, stepRequest, SagaStepResponse.class);
            
            return response.getBody() != null && response.getBody().isSuccess() ?
                StepResult.success(response.getBody().getData()) :
                StepResult.failure("Step execution failed");
            
        } catch (Exception e) {
            return StepResult.failure(e.getMessage());
        }
    }
    
    // 执行分布式补偿
    private void executeDistributedCompensation(String sagaId, List<DistributedSagaStep> steps, int failedStepIndex) {
        // 按相反顺序调用远程服务的补偿接口
        for (int i = failedStepIndex - 1; i >= 0; i--) {
            DistributedSagaStep step = steps.get(i);
            try {
                String url = step.getServiceUrl() + step.getCompensationEndpoint();
                SagaCompensationRequest compensationRequest = new SagaCompensationRequest(sagaId);
                
                restTemplate.postForEntity(url, compensationRequest, SagaCompensationResponse.class);
            } catch (Exception e) {
                log.error("Compensation failed for step: {} saga: {}", step.getStepName(), sagaId, e);
            }
        }
    }
}

// 订单服务Saga步骤（独立微服务）
@RestController
@RequestMapping("/saga")
public class OrderServiceSagaStep {
    
    @Autowired
    private OrderService orderService;
    
    @PostMapping("/create-order")
    public ResponseEntity<SagaStepResponse> createOrder(@RequestBody SagaStepRequest request) {
        try {
            SagaContext context = request.getContext();
            Order order = orderService.createOrder(context.getOrderRequest());
            
            return ResponseEntity.ok(SagaStepResponse.success(order.getId()));
        } catch (Exception e) {
            return ResponseEntity.ok(SagaStepResponse.failure(e.getMessage()));
        }
    }
    
    @PostMapping("/compensate-create-order")
    public ResponseEntity<SagaCompensationResponse> compensateCreateOrder(
            @RequestBody SagaCompensationRequest request) {
        try {
            // 补偿逻辑：取消订单
            Long orderId = getOrderIdFromSaga(request.getSagaId());
            if (orderId != null) {
                orderService.cancelOrder(orderId);
            }
            return ResponseEntity.ok(SagaCompensationResponse.success());
        } catch (Exception e) {
            return ResponseEntity.ok(SagaCompensationResponse.failure(e.getMessage()));
        }
    }
}
```

**4. 基于消息的分布式最终一致性**

```java
// 分布式事件发布服务（独立服务）
@RestController
@RequestMapping("/distributed-events")
public class DistributedEventPublisher {
    
    @Autowired
    private RabbitTemplate rabbitTemplate;
    
    @Autowired
    private OutboxEventRepository outboxRepository;
    
    // 本地事务 + 分布式消息发送（Outbox模式）
    @PostMapping("/create-order")
    @Transactional
    public ResponseEntity<EventPublishResult> createOrderWithDistributedEvents(
            @RequestBody CreateOrderRequest request) {
        
        try {
            // 1. 执行本地业务操作
            Order order = orderService.createOrder(request);
            
            // 2. 在同一事务中保存要发送的分布式事件
            List<OutboxEvent> events = createDistributedEvents(order);
            outboxRepository.saveAll(events);
            
            return ResponseEntity.ok(EventPublishResult.success(order.getId(), events.size()));
            
        } catch (Exception e) {
            return ResponseEntity.status(500)
                .body(EventPublishResult.error(e.getMessage()));
        }
    }
    
    // 创建分布式事件
    private List<OutboxEvent> createDistributedEvents(Order order) {
        List<OutboxEvent> events = new ArrayList<>();
        
        // 库存服务事件
        events.add(new OutboxEvent()
            .setEventType("ORDER_CREATED_FOR_INVENTORY")
            .setTargetService("inventory-service")
            .setRoutingKey("inventory.order.created")
            .setPayload(JsonUtils.toJson(new InventoryReservationEvent(order)))
            .setStatus(EventStatus.PENDING));
        
        // 支付服务事件
        events.add(new OutboxEvent()
            .setEventType("ORDER_CREATED_FOR_PAYMENT")
            .setTargetService("payment-service")
            .setRoutingKey("payment.order.created")
            .setPayload(JsonUtils.toJson(new PaymentProcessEvent(order)))
            .setStatus(EventStatus.PENDING));
        
        return events;
    }
    
    // 分布式事件发送器（定时任务）
    @Scheduled(fixedDelay = 2000)
    public void publishPendingDistributedEvents() {
        List<OutboxEvent> pendingEvents = outboxRepository
            .findByStatusOrderByCreatedTimeAsc(EventStatus.PENDING);
        
        for (OutboxEvent event : pendingEvents) {
            try {
                // 发送消息到对应的分布式服务队列
                rabbitTemplate.convertAndSend(
                    "distributed.transaction.exchange",
                    event.getRoutingKey(),
                    event.getPayload()
                );
                
                // 标记为已发送
                event.setStatus(EventStatus.SENT);
                outboxRepository.save(event);
                
            } catch (Exception e) {
                log.error("Failed to publish distributed event: eventId={}", event.getId(), e);
                event.setRetryCount(event.getRetryCount() + 1);
                if (event.getRetryCount() > 3) {
                    event.setStatus(EventStatus.FAILED);
                }
                outboxRepository.save(event);
            }
        }
    }
}

// 库存服务消息消费者（独立微服务）
@Component
public class DistributedInventoryMessageConsumer {
    
    @Autowired
    private InventoryService inventoryService;
    
    @RabbitListener(queues = "inventory.order.created.queue")
    public void handleOrderCreatedForInventory(@Payload String message) {
        try {
            InventoryReservationEvent event = JsonUtils.fromJson(message, InventoryReservationEvent.class);
            
            // 处理库存预留
            boolean reserved = inventoryService.reserveInventoryForOrder(
                event.getProductId(), event.getQuantity(), event.getOrderId());
            
            if (reserved) {
                // 成功后发送确认事件到订单服务
                publishInventoryReservedEvent(event.getOrderId());
            } else {
                // 库存不足，发送失败事件
                publishInventoryReservationFailedEvent(event.getOrderId());
            }
            
        } catch (Exception e) {
            log.error("Failed to handle order created event", e);
            // 实现重试或死信队列处理
            throw new MessageProcessingException("库存处理失败", e);
        }
    }
    
    private void publishInventoryReservedEvent(Long orderId) {
        // 发送库存预留成功事件到订单服务
    }
    
    private void publishInventoryReservationFailedEvent(Long orderId) {
        // 发送库存预留失败事件
    }
}
```

**分布式事务选择指南：**

| 模式 | 一致性 | 性能 | 复杂度 | 适用场景 |
|------|--------|------|--------|----------|
| 2PC | 强一致性 | 低 | 中等 | 金融、核心业务 |
| TCC | 强一致性 | 中等 | 高 | 对一致性要求高的业务 |
| Saga | 最终一致性 | 高 | 中等 | 长流程业务 |
| 消息队列 | 最终一致性 | 高 | 低 | 大部分业务场景 |

### 6.3 消息队列
**Q: 消息队列的作用？**
- 解耦：降低系统间依赖
- 异步：提高系统响应速度
- 削峰：处理突发流量
- 持久化：保证消息不丢失

## 7. 性能优化

### 7.1 代码优化
```java
// 字符串拼接优化
// 不推荐
String result = "";
for (String s : list) {
    result += s;  // 每次都创建新的String对象
}

// 推荐
StringBuilder sb = new StringBuilder();
for (String s : list) {
    sb.append(s);
}
String result = sb.toString();

// 集合初始化优化
List<String> list = new ArrayList<>(expectedSize);
Map<String, String> map = new HashMap<>(expectedSize);

// 避免装箱拆箱
// 不推荐
Integer count = 0;
for (int i = 0; i < 1000000; i++) {
    count += i;  // 频繁装箱拆箱
}

// 推荐
int count = 0;
for (int i = 0; i < 1000000; i++) {
    count += i;
}
```

### 7.2 JVM 性能调优
```java
// JVM性能监控工具使用
public class PerformanceMonitor {
    
    // 监控内存使用
    public void printMemoryInfo() {
        MemoryMXBean memoryMX = ManagementFactory.getMemoryMXBean();
        MemoryUsage heapUsage = memoryMX.getHeapMemoryUsage();
        
        System.out.println("堆内存使用情况:");
        System.out.println("已使用: " + heapUsage.getUsed() / 1024 / 1024 + "MB");
        System.out.println("最大值: " + heapUsage.getMax() / 1024 / 1024 + "MB");
    }
    
    // 监控GC情况
    public void printGCInfo() {
        List<GarbageCollectorMXBean> gcBeans = ManagementFactory.getGarbageCollectorMXBeans();
        for (GarbageCollectorMXBean gcBean : gcBeans) {
            System.out.println("GC名称: " + gcBean.getName());
            System.out.println("GC次数: " + gcBean.getCollectionCount());
            System.out.println("GC时间: " + gcBean.getCollectionTime() + "ms");
        }
    }
}
```

## 8. 设计模式

**Q: 常用设计模式的应用场景？**
- **单例模式**：Spring Bean默认作用域
- **工厂模式**：BeanFactory创建Bean
- **观察者模式**：Spring事件驱动
- **代理模式**：AOP实现
- **模板方法模式**：JdbcTemplate
- **策略模式**：不同算法实现

## 9. 网络编程

**Q: BIO vs NIO vs AIO？**
- **BIO（Blocking I/O）**：同步阻塞，一个连接一个线程
- **NIO（Non-blocking I/O）**：同步非阻塞，多路复用
- **AIO（Asynchronous I/O）**：异步非阻塞，回调处理

## 10. 实际项目经验

**Q: 如何设计高并发系统？**
1. **分层架构**：接入层、业务层、数据层
2. **负载均衡**：Nginx、LVS分发请求
3. **缓存策略**：Redis缓存热点数据
4. **数据库优化**：读写分离、分库分表
5. **异步处理**：消息队列处理耗时操作
6. **熔断降级**：Hystrix保护系统稳定性
7. **监控告警**：实时监控系统状态

**Q: 线上问题排查思路？**

### 10.1 监控指标分析案例

#### CPU使用率异常排查
```bash
# 1. 查看系统整体CPU使用情况
top -p `pgrep java`

# 2. 查看具体线程CPU使用情况
top -H -p <java_pid>

# 3. 将线程ID转换为16进制，在线程dump中查找
printf "%x\n" <thread_id>

# 4. 生成线程dump分析CPU占用高的线程
jstack <java_pid> > thread_dump.txt
```

#### 内存使用监控和分析
```java
// Java代码监控内存使用情况
public class MemoryMonitor {
    
    public static void printMemoryInfo() {
        MemoryMXBean memoryBean = ManagementFactory.getMemoryMXBean();
        MemoryUsage heapUsage = memoryBean.getHeapMemoryUsage();
        MemoryUsage nonHeapUsage = memoryBean.getNonHeapMemoryUsage();
        
        System.out.println("=== 堆内存使用情况 ===");
        System.out.println("已使用: " + (heapUsage.getUsed() / 1024 / 1024) + " MB");
        System.out.println("已提交: " + (heapUsage.getCommitted() / 1024 / 1024) + " MB");
        System.out.println("最大值: " + (heapUsage.getMax() / 1024 / 1024) + " MB");
        System.out.println("使用率: " + String.format("%.2f%%", 
            (double) heapUsage.getUsed() / heapUsage.getMax() * 100));
        
        System.out.println("\n=== 非堆内存使用情况 ===");
        System.out.println("已使用: " + (nonHeapUsage.getUsed() / 1024 / 1024) + " MB");
        System.out.println("已提交: " + (nonHeapUsage.getCommitted() / 1024 / 1024) + " MB");
    }
    
    // 监控GC情况
    public static void printGCInfo() {
        List<GarbageCollectorMXBean> gcBeans = ManagementFactory.getGarbageCollectorMXBeans();
        System.out.println("\n=== GC统计信息 ===");
        for (GarbageCollectorMXBean gcBean : gcBeans) {
            System.out.println("GC名称: " + gcBean.getName());
            System.out.println("GC次数: " + gcBean.getCollectionCount());
            System.out.println("GC总时间: " + gcBean.getCollectionTime() + "ms");
            System.out.println("平均GC时间: " + 
                (gcBean.getCollectionCount() > 0 ? 
                    gcBean.getCollectionTime() / gcBean.getCollectionCount() : 0) + "ms");
            System.out.println("---");
        }
    }
}
```

#### 网络和磁盘I/O监控
```bash
# 网络连接数监控
netstat -an | grep :8080 | wc -l  # 统计8080端口连接数
ss -s  # 查看socket统计信息

# 磁盘I/O监控
iostat -x 1  # 每秒显示磁盘I/O统计
lsof -p <java_pid>  # 查看进程打开的文件
```

### 10.2 分析堆栈案例

#### 死锁排查案例
```java
// 模拟死锁场景
public class DeadlockExample {
    private static final Object lock1 = new Object();
    private static final Object lock2 = new Object();
    
    public static void main(String[] args) {
        new Thread(() -> {
            synchronized (lock1) {
                System.out.println("Thread1: Holding lock1...");
                try { Thread.sleep(100); } catch (InterruptedException e) {}
                synchronized (lock2) {
                    System.out.println("Thread1: Holding lock1 & lock2...");
                }
            }
        }).start();
        
        new Thread(() -> {
            synchronized (lock2) {
                System.out.println("Thread2: Holding lock2...");
                try { Thread.sleep(100); } catch (InterruptedException e) {}
                synchronized (lock1) {
                    System.out.println("Thread2: Holding lock2 & lock1...");
                }
            }
        }).start();
    }
}
```

#### 死锁检测和分析
```bash
# 1. 生成线程dump
jstack <java_pid> > deadlock_analysis.txt

# 2. 或使用jcmd命令
jcmd <java_pid> Thread.print > thread_dump.txt

# 3. 使用VisualVM图形化分析
# 在VisualVM中查看Threads标签，可以直观看到死锁
```

#### 线程dump分析要点
```
# 在dump文件中查找关键信息：
# 1. 死锁检测结果
Found 2 deadlocks.

# 2. 线程状态
"Thread-1" #10 prio=5 os_prio=31 tid=0x... nid=0x... waiting for monitor entry
   java.lang.Thread.State: BLOCKED (on object monitor)

# 3. 锁等待链
waiting to lock <0x000000076ab62208> (a java.lang.Object)
locked <0x000000076ab62218> (a java.lang.Object)
```

#### 内存溢出堆dump分析
```bash
# 1. 生成堆dump（OOM时自动生成）
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/path/to/heapdump.hprof

# 2. 手动生成堆dump
jmap -dump:format=b,file=heap_dump.hprof <java_pid>

# 3. 使用MAT (Memory Analyzer Tool) 分析
# - 查看Histogram找到占用内存最多的对象
# - 查看Dominator Tree分析对象引用关系
# - 使用OQL查询特定对象
SELECT * FROM java.lang.String s WHERE s.count > 1000
```

### 10.3 性能分析实战案例

#### 使用Arthas进行在线诊断
```bash
# 1. 启动Arthas
java -jar arthas-boot.jar

# 2. 查看JVM信息
dashboard  # 实时数据面板
jvm        # JVM详细信息

# 3. 监控方法执行时间
monitor -c 5 com.example.UserService getUserById  # 每5秒统计一次

# 4. 查看方法调用堆栈
trace com.example.UserService getUserById  # 追踪方法调用链

# 5. 观察方法参数和返回值
watch com.example.UserService getUserById "{params,returnObj}" -x 2

# 6. 查看热点方法
profiler start  # 开始性能采样
profiler stop   # 停止并生成火焰图
```

#### JProfiler性能分析案例
```java
// 性能测试代码
public class PerformanceTest {
    
    // CPU密集型任务分析
    public void cpuIntensiveTask() {
        List<Integer> numbers = new ArrayList<>();
        for (int i = 0; i < 1000000; i++) {
            numbers.add(calculatePrime(i));  // 计算质数
        }
    }
    
    // 内存密集型任务分析
    public void memoryIntensiveTask() {
        List<String> strings = new ArrayList<>();
        for (int i = 0; i < 100000; i++) {
            strings.add("String_" + i + "_" + System.currentTimeMillis());
        }
    }
    
    // 分析要点：
    // 1. CPU采样：找出耗时最多的方法
    // 2. 内存分析：找出创建最多对象的地方
    // 3. 线程分析：找出阻塞时间最长的线程
    // 4. 数据库分析：找出最慢的SQL语句
}
```

#### 应用性能监控(APM)实战
```yaml
# application.yml - 集成Micrometer监控
management:
  endpoints:
    web:
      exposure:
        include: "*"
  metrics:
    export:
      prometheus:
        enabled: true
  endpoint:
    metrics:
      enabled: true
    prometheus:
      enabled: true
```

```java
// 自定义性能监控
@Component
public class PerformanceMonitor {
    
    private final MeterRegistry meterRegistry;
    
    @EventListener
    public void handleMethodExecution(MethodExecutionEvent event) {
        Timer timer = Timer.builder("method_execution_time")
                          .tag("class", event.getClassName())
                          .tag("method", event.getMethodName())
                          .register(meterRegistry);
        
        timer.record(event.getExecutionTime(), TimeUnit.MILLISECONDS);
    }
}
```

### 10.4 数据库分析实战案例

#### 慢查询日志分析
```sql
-- 1. 开启慢查询日志
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;  -- 超过2秒的查询记录
SET GLOBAL log_queries_not_using_indexes = 'ON';

-- 2. 分析慢查询
-- 使用mysqldumpslow工具
-- mysqldumpslow -s t -t 10 /path/to/slow.log
```

#### 执行计划分析案例
```sql
-- 问题SQL示例
SELECT u.username, p.title, c.content 
FROM users u 
JOIN posts p ON u.id = p.user_id 
JOIN comments c ON p.id = c.post_id 
WHERE u.created_time > '2023-01-01' 
AND p.status = 'published'
ORDER BY p.created_time DESC 
LIMIT 20;

-- 分析执行计划
EXPLAIN FORMAT=JSON SELECT ...;

-- 优化后的SQL
SELECT u.username, p.title, c.content 
FROM users u 
USE INDEX (idx_created_time)
JOIN posts p USE INDEX (idx_user_status) ON u.id = p.user_id 
JOIN comments c USE INDEX (idx_post_id) ON p.id = c.post_id 
WHERE u.created_time > '2023-01-01' 
AND p.status = 'published'
ORDER BY p.created_time DESC 
LIMIT 20;
```

#### 数据库连接池监控
```java
// HikariCP连接池监控
@Component
public class ConnectionPoolMonitor {
    
    @Autowired
    private HikariDataSource dataSource;
    
    @Scheduled(fixedRate = 30000)  // 每30秒监控一次
    public void monitorConnectionPool() {
        HikariPoolMXBean poolBean = dataSource.getHikariPoolMXBean();
        
        System.out.println("=== 连接池监控 ===");
        System.out.println("活跃连接数: " + poolBean.getActiveConnections());
        System.out.println("空闲连接数: " + poolBean.getIdleConnections());
        System.out.println("总连接数: " + poolBean.getTotalConnections());
        System.out.println("等待线程数: " + poolBean.getThreadsAwaitingConnection());
        
        // 连接池告警
        if (poolBean.getActiveConnections() > poolBean.getMaximumPoolSize() * 0.8) {
            System.out.println("WARNING: 连接池使用率超过80%");
        }
    }
}
```

#### SQL性能监控和分析
```java
// 使用p6spy监控SQL执行
@Configuration
public class SqlMonitorConfig {
    
    @Bean
    public SqlPerformanceInterceptor sqlInterceptor() {
        return new SqlPerformanceInterceptor();
    }
}

@Component
public class SqlPerformanceInterceptor {
    
    @Around("execution(* com.example.dao..*(..))")
    public Object monitorSql(ProceedingJoinPoint joinPoint) throws Throwable {
        long startTime = System.currentTimeMillis();
        
        try {
            Object result = joinPoint.proceed();
            long executionTime = System.currentTimeMillis() - startTime;
            
            if (executionTime > 1000) {  // 超过1秒的SQL
                System.out.println("慢SQL检测:");
                System.out.println("方法: " + joinPoint.getSignature().getName());
                System.out.println("执行时间: " + executionTime + "ms");
                System.out.println("参数: " + Arrays.toString(joinPoint.getArgs()));
            }
            
            return result;
        } catch (Exception e) {
            System.out.println("SQL执行异常: " + e.getMessage());
            throw e;
        }
    }
}
```

#### 数据库死锁分析
```sql
-- 查看当前锁等待情况
SELECT 
    r.trx_id waiting_trx_id,
    r.trx_mysql_thread_id waiting_thread,
    r.trx_query waiting_query,
    b.trx_id blocking_trx_id,
    b.trx_mysql_thread_id blocking_thread,
    b.trx_query blocking_query
FROM information_schema.innodb_lock_waits w
JOIN information_schema.innodb_trx b ON b.trx_id = w.blocking_trx_id
JOIN information_schema.innodb_trx r ON r.trx_id = w.requesting_trx_id;

-- 查看死锁日志
SHOW ENGINE INNODB STATUS;

-- 在死锁日志中关注：
-- 1. LATEST DETECTED DEADLOCK 部分
-- 2. 涉及的事务和SQL语句  
-- 3. 锁等待的表和索引
-- 4. 死锁的形成路径
```

### 10.5 综合问题排查实战流程

```java
// 问题排查工具类
@Component
public class TroubleshootingToolkit {
    
    private static final Logger logger = LoggerFactory.getLogger(TroubleshootingToolkit.class);
    
    // 1. 应用健康检查
    public HealthStatus checkApplicationHealth() {
        HealthStatus status = new HealthStatus();
        
        // 检查内存使用率
        MemoryUsage heapUsage = ManagementFactory.getMemoryMXBean().getHeapMemoryUsage();
        double memoryUsagePercent = (double) heapUsage.getUsed() / heapUsage.getMax() * 100;
        status.setMemoryUsage(memoryUsagePercent);
        
        // 检查线程数
        int threadCount = ManagementFactory.getThreadMXBean().getThreadCount();
        status.setThreadCount(threadCount);
        
        // 检查GC频率
        long totalGcTime = ManagementFactory.getGarbageCollectorMXBeans()
            .stream()
            .mapToLong(GarbageCollectorMXBean::getCollectionTime)
            .sum();
        status.setGcTime(totalGcTime);
        
        return status;
    }
    
    // 2. 生成问题报告
    public void generateTroubleshootingReport() {
        StringBuilder report = new StringBuilder();
        report.append("=== 应用问题排查报告 ===\n");
        report.append("生成时间: ").append(new Date()).append("\n\n");
        
        // 系统基本信息
        report.append("系统信息:\n");
        report.append("JVM版本: ").append(System.getProperty("java.version")).append("\n");
        report.append("操作系统: ").append(System.getProperty("os.name")).append("\n");
        
        // 应用健康状态
        HealthStatus health = checkApplicationHealth();
        report.append("\n应用状态:\n");
        report.append("内存使用率: ").append(String.format("%.2f%%", health.getMemoryUsage())).append("\n");
        report.append("线程数: ").append(health.getThreadCount()).append("\n");
        
        logger.info(report.toString());
    }
}

// 健康状态类
class HealthStatus {
    private double memoryUsage;
    private int threadCount;
    private long gcTime;
    
    // getters and setters...
}
```

**完整排查流程总结：**

1. **快速定位**：查看监控大盘，确定问题范围（CPU/内存/网络/数据库）
2. **日志分析**：检查应用日志和错误日志，寻找异常信息
3. **性能分析**：使用APM工具或Arthas分析方法执行时间
4. **资源分析**：生成thread dump和heap dump进行深入分析
5. **数据库分析**：检查慢查询和连接池状态
6. **网络分析**：检查网络连接和I/O状况
7. **代码审查**：结合业务代码分析可能的问题点
8. **修复验证**：实施修复方案并验证效果