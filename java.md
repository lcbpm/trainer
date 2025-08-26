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

#### 1.4.1 JVM调优基础参数配置
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

#### 1.4.2 实战案例一：高并发电商系统GC调优

**问题背景：**
某电商平台在双11期间，用户下单时系统响应缓慢，平均响应时间从100ms增加到2秒以上。

**系统配置：**
- 8核16G内存服务器
- 日均订单量：100万+
- 峰值QPS：5000+

**初始JVM配置：**
```bash
-Xms8g -Xmx8g
-XX:+UseParallelGC
-XX:ParallelGCThreads=8
-XX:+PrintGCDetails
-XX:+PrintGCTimeStamps
```

**问题分析过程：**

1. **GC日志分析**
```bash
# GC日志显示频繁的Full GC
2023-11-11T10:15:30.123+0800: [Full GC (Ergonomics) 
[PSYoungGen: 0K->0K(2048000K)] 
[ParOldGen: 6291456K->6291456K(6291456K)] 
6291456K->6291456K(8339456K), 
[Metaspace: 89543K->89543K(1134592K)], 3.2156789 secs]

# 分析结果：
# 1. 老年代几乎满了（6G/6G）
# 2. Full GC耗时3.2秒
# 3. GC后老年代空间没有释放
```

2. **堆内存分析**
```bash
# 生成堆转储文件
jmap -dump:format=b,file=heap_dump.hprof 12345

# 使用MAT工具分析发现：
# - 订单缓存占用60%内存（约4.8G）
# - 大量订单对象没有及时释放
# - 存在内存泄漏风险
```

3. **代码问题定位**
```java
// 问题代码：订单缓存策略不当
@Service
public class OrderService {
    // 问题：使用static Map缓存，没有过期机制
    private static final Map<String, Order> ORDER_CACHE = new ConcurrentHashMap<>();
    
    public Order getOrder(String orderId) {
        Order order = ORDER_CACHE.get(orderId);
        if (order == null) {
            order = orderRepository.findById(orderId);
            ORDER_CACHE.put(orderId, order);  // 内存泄漏源头
        }
        return order;
    }
}
```

**优化方案：**

1. **代码优化**
```java
// 优化后：使用Caffeine缓存，支持过期和容量限制
@Service
public class OrderService {
    
    private final Cache<String, Order> orderCache = Caffeine.newBuilder()
            .maximumSize(50000)  // 最大缓存5万个订单
            .expireAfterWrite(Duration.ofHours(2))  // 2小时过期
            .expireAfterAccess(Duration.ofMinutes(30))  // 30分钟未访问过期
            .recordStats()  // 开启统计
            .build();
    
    public Order getOrder(String orderId) {
        return orderCache.get(orderId, key -> orderRepository.findById(key));
    }
    
    // 监控缓存效果
    @Scheduled(fixedRate = 60000)
    public void logCacheStats() {
        CacheStats stats = orderCache.stats();
        log.info("Order cache stats: hitRate={}, evictionCount={}, size={}",
            stats.hitRate(), stats.evictionCount(), orderCache.estimatedSize());
    }
}
```

2. **JVM参数优化**
```bash
# 优化后的JVM配置
-Xms8g -Xmx8g
-XX:+UseG1GC                    # 改用G1收集器
-XX:MaxGCPauseMillis=100       # 目标停顿时间100ms
-XX:G1HeapRegionSize=16m       # 设置Region大小
-XX:G1NewSizePercent=30        # 新生代最小比例
-XX:G1MaxNewSizePercent=50     # 新生代最大比例
-XX:+G1UseAdaptiveIHOP         # 自适应IHOP
-XX:G1MixedGCCountTarget=8     # 混合GC目标次数
-XX:+UnlockExperimentalVMOptions
-XX:+UseJVMCICompiler          # 开启JIT编译优化

# GC日志配置
-Xloggc:/var/log/gc/gc.log
-XX:+UseGCLogFileRotation
-XX:NumberOfGCLogFiles=5
-XX:GCLogFileSize=100M
-XX:+PrintGCDetails
-XX:+PrintGCTimeStamps
-XX:+PrintGCApplicationStoppedTime
```

**优化效果：**
- 平均GC停顿时间：从3.2秒降低到80ms
- 系统响应时间：从2秒降低到120ms
- 内存使用率：从95%降低到65%
- 系统吞吐量：提升40%

#### 1.4.3 实战案例二：大数据处理系统内存溢出优化

**问题背景：**
某数据分析系统处理大文件时频繁出现OOM，需要处理单个文件大小2-5GB的CSV数据。

**系统配置：**
- 32核64G内存服务器
- 处理文件：2-5GB CSV文件
- 数据行数：1000万+

**问题现象：**
```bash
java.lang.OutOfMemoryError: Java heap space
    at java.util.Arrays.copyOf(Arrays.java:3210)
    at java.util.ArrayList.grow(ArrayList.java:267)
    at java.util.ArrayList.ensureExplicitCapacity(ArrayList.java:241)
    at com.example.DataProcessor.processLargeFile(DataProcessor.java:45)
```

**原始代码问题：**
```java
// 问题代码：一次性加载整个文件到内存
@Service
public class DataProcessor {
    
    public void processLargeFile(String filePath) {
        try {
            // 问题1：一次性读取所有行到内存
            List<String> allLines = Files.readAllLines(Paths.get(filePath));
            
            List<ProcessedData> results = new ArrayList<>();
            for (String line : allLines) {
                ProcessedData data = processLine(line);
                results.add(data);  // 问题2：结果也全部保存在内存中
            }
            
            // 问题3：批量保存，占用更多内存
            dataRepository.saveAll(results);
            
        } catch (IOException e) {
            throw new RuntimeException("文件处理失败", e);
        }
    }
}
```

**内存分析：**
```bash
# 使用jmap分析内存占用
jmap -histo:live <pid> | head -20

# 分析结果显示：
# 1. String对象占用45% 内存
# 2. ArrayList占用25% 内存
# 3. ProcessedData对象占用20% 内存
# 4. 总内存占用超过分配的堆空间
```

**优化方案：**

1. **流式处理改造**
```java
// 优化后：使用流式处理，分批处理数据
@Service
public class DataProcessor {
    
    private static final int BATCH_SIZE = 1000;  // 批处理大小
    
    public void processLargeFile(String filePath) {
        try (Stream<String> lines = Files.lines(Paths.get(filePath))) {
            
            // 使用流式处理，分批处理
            lines.parallel()  // 并行处理提高效率
                 .map(this::processLine)
                 .collect(Collectors.groupingBy(
                     data -> data.hashCode() % BATCH_SIZE,  // 分组
                     Collectors.toList()))
                 .values()
                 .parallelStream()
                 .forEach(this::saveBatch);  // 分批保存
                 
        } catch (IOException e) {
            throw new RuntimeException("文件处理失败", e);
        }
    }
    
    private void saveBatch(List<ProcessedData> batch) {
        try {
            dataRepository.saveAll(batch);
            batch.clear();  // 及时清理内存
        } catch (Exception e) {
            log.error("批量保存失败", e);
        }
    }
    
    // 另一种方案：使用缓冲区分块读取
    public void processLargeFileWithBuffer(String filePath) {
        try (BufferedReader reader = Files.newBufferedReader(Paths.get(filePath))) {
            
            List<ProcessedData> batch = new ArrayList<>(BATCH_SIZE);
            String line;
            
            while ((line = reader.readLine()) != null) {
                ProcessedData data = processLine(line);
                batch.add(data);
                
                if (batch.size() >= BATCH_SIZE) {
                    saveBatch(batch);
                    batch = new ArrayList<>(BATCH_SIZE);  // 创建新批次
                }
            }
            
            // 处理最后一批数据
            if (!batch.isEmpty()) {
                saveBatch(batch);
            }
            
        } catch (IOException e) {
            throw new RuntimeException("文件处理失败", e);
        }
    }
}
```

2. **JVM参数调优**
```bash
# 针对大数据处理的JVM配置
-Xms32g -Xmx32g                  # 大内存配置
-XX:+UseG1GC
-XX:MaxGCPauseMillis=200
-XX:G1HeapRegionSize=32m          # 大region适合大对象
-XX:+G1UseAdaptiveIHOP
-XX:G1MixedGCLiveThresholdPercent=85

# 针对大对象的优化
-XX:G1HeapWastePercent=10
-XX:+UseLargePages                # 使用大页内存
-XX:LargePageSizeInBytes=2m

# 并行GC线程数（根据CPU核数调整）
-XX:ParallelGCThreads=16
-XX:ConcGCThreads=4

# 元空间配置（避免类加载OOM）
-XX:MetaspaceSize=512m
-XX:MaxMetaspaceSize=1g

# 直接内存配置（NIO使用）
-XX:MaxDirectMemorySize=8g

# 内存泄漏检测
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/var/log/heapdump/
```

3. **内存监控和告警**
```java
// 内存监控组件
@Component
public class MemoryMonitor {
    
    private final MeterRegistry meterRegistry;
    private final MemoryMXBean memoryMXBean;
    
    public MemoryMonitor(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
        this.memoryMXBean = ManagementFactory.getMemoryMXBean();
        registerMetrics();
    }
    
    private void registerMetrics() {
        // 注册内存使用率指标
        Gauge.builder("jvm.memory.heap.used.ratio")
            .description("堆内存使用率")
            .register(meterRegistry, this, MemoryMonitor::getHeapUsedRatio);
            
        // 注册GC指标
        ManagementFactory.getGarbageCollectorMXBeans()
            .forEach(gcBean -> {
                Gauge.builder("jvm.gc.collection.count")
                    .tag("gc", gcBean.getName())
                    .register(meterRegistry, gcBean, GarbageCollectorMXBean::getCollectionCount);
                    
                Gauge.builder("jvm.gc.collection.time")
                    .tag("gc", gcBean.getName())
                    .register(meterRegistry, gcBean, GarbageCollectorMXBean::getCollectionTime);
            });
    }
    
    private double getHeapUsedRatio() {
        MemoryUsage heapUsage = memoryMXBean.getHeapMemoryUsage();
        return (double) heapUsage.getUsed() / heapUsage.getMax();
    }
    
    // 内存告警
    @Scheduled(fixedRate = 30000)  // 30秒检查一次
    public void checkMemoryUsage() {
        double heapUsedRatio = getHeapUsedRatio();
        
        if (heapUsedRatio > 0.85) {
            log.warn("堆内存使用率过高: {:.2f}%", heapUsedRatio * 100);
            // 发送告警
            alertService.sendAlert("高内存使用率告警", 
                String.format("当前堆内存使用率: %.2f%%", heapUsedRatio * 100));
        }
    }
}
```

**优化效果：**
- 内存使用：从峰值60G降低到8G
- 处理速度：提升60%（并行处理）
- 稳定性：零OOM异常
- GC停顿：平均150ms

#### 1.4.4 实战案例三：微服务容器化JVM调优

**问题背景：**
某微服务在Kubernetes环境中运行，容器经常因为内存限制被kill（OOMKilled）。

**容器配置：**
```yaml
# Pod资源配置
resources:
  requests:
    memory: "2Gi"
    cpu: "1"
  limits:
    memory: "4Gi"
    cpu: "2"
```

**问题分析：**
```bash
# 查看容器被kill的原因
kubectl describe pod app-pod-xxx

# 显示：
# State: Terminated
# Reason: OOMKilled
# Exit Code: 137
```

**容器内存使用分析：**
```bash
# 容器内查看内存使用
cat /proc/meminfo
# 发现JVM堆内存只占用1.5G，但总内存使用接近4G

# 分析内存构成：
# JVM堆内存：1.5G
# JVM非堆内存：800M（元空间、代码缓存等）
# 直接内存：600M（NIO、Netty等使用）
# 操作系统缓存：500M
# 其他：600M
```

**根本原因：**
1. JVM堆内存设置不当，没有考虑容器内存限制
2. 非堆内存（元空间、直接内存）占用过多
3. 没有限制直接内存使用

**优化方案：**

1. **容器感知的JVM配置**
```bash
# 容器环境下的JVM配置
# 使用容器感知的内存设置
-XX:+UseContainerSupport          # 启用容器支持
-XX:MaxRAMPercentage=75.0         # 使用75%的容器内存作为堆内存
-XX:InitialRAMPercentage=50.0     # 初始堆内存为50%

# 或者明确指定内存大小
-Xms2g -Xmx3g                     # 为系统和其他组件预留1G内存

# 限制非堆内存
-XX:MetaspaceSize=256m
-XX:MaxMetaspaceSize=512m
-XX:MaxDirectMemorySize=512m
-XX:ReservedCodeCacheSize=128m

# G1收集器配置（适合容器环境）
-XX:+UseG1GC
-XX:MaxGCPauseMillis=100
-XX:G1HeapRegionSize=16m

# 容器环境下的GC优化
-XX:+UnlockExperimentalVMOptions
-XX:+UseCGroupMemoryLimitForHeap  # 使用cgroup内存限制
```

2. **内存监控改进**
```java
// 容器内存监控
@Component
public class ContainerMemoryMonitor {
    
    @Value("${spring.application.name}")
    private String applicationName;
    
    private final MeterRegistry meterRegistry;
    
    public ContainerMemoryMonitor(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
        registerContainerMetrics();
    }
    
    private void registerContainerMetrics() {
        // 监控容器内存使用
        Gauge.builder("container.memory.usage")
            .description("容器内存使用量")
            .register(meterRegistry, this, ContainerMemoryMonitor::getContainerMemoryUsage);
            
        // 监控JVM直接内存
        Gauge.builder("jvm.memory.direct.used")
            .description("直接内存使用量")
            .register(meterRegistry, this, ContainerMemoryMonitor::getDirectMemoryUsage);
    }
    
    private double getContainerMemoryUsage() {
        try {
            // 读取cgroup内存使用
            String usageStr = Files.readString(Paths.get("/sys/fs/cgroup/memory/memory.usage_in_bytes"));
            return Double.parseDouble(usageStr.trim());
        } catch (Exception e) {
            return -1;
        }
    }
    
    private double getDirectMemoryUsage() {
        try {
            Class<?> vmClass = Class.forName("sun.misc.VM");
            Method maxDirectMemoryMethod = vmClass.getMethod("maxDirectMemory");
            long maxDirectMemory = (Long) maxDirectMemoryMethod.invoke(null);
            
            // 通过JMX获取直接内存使用量
            List<MemoryPoolMXBean> memoryPools = ManagementFactory.getMemoryPoolMXBeans();
            return memoryPools.stream()
                .filter(pool -> pool.getName().contains("Direct"))
                .mapToLong(pool -> pool.getUsage().getUsed())
                .sum();
        } catch (Exception e) {
            return -1;
        }
    }
}
```

3. **优化后的Dockerfile**
```dockerfile
# 多阶段构建，减少镜像大小
FROM openjdk:11-jre-slim as runtime

# 添加JVM调优脚本
COPY jvm-opts.sh /opt/
RUN chmod +x /opt/jvm-opts.sh

# 设置JVM参数
ENV JAVA_OPTS="-XX:+UseContainerSupport -XX:MaxRAMPercentage=75.0 -XX:+UseG1GC"
ENV GC_OPTS="-XX:MaxGCPauseMillis=100 -XX:+PrintGCDetails -Xloggc:/var/log/gc.log"
ENV MEM_OPTS="-XX:MaxDirectMemorySize=512m -XX:MetaspaceSize=256m"

# 应用启动脚本
COPY app.jar /app/
CMD ["/opt/jvm-opts.sh"]
```

4. **JVM启动脚本**
```bash
#!/bin/bash
# jvm-opts.sh - 动态JVM参数配置

# 获取容器内存限制
CONTAINER_MEMORY=$(cat /sys/fs/cgroup/memory/memory.limit_in_bytes)
CONTAINER_MEMORY_MB=$((CONTAINER_MEMORY / 1024 / 1024))

# 动态计算JVM参数
if [ $CONTAINER_MEMORY_MB -lt 1024 ]; then
    # 小于1G内存的容器
    HEAP_SIZE="512m"
    NEW_SIZE="256m"
elif [ $CONTAINER_MEMORY_MB -lt 2048 ]; then
    # 1-2G内存的容器
    HEAP_SIZE="1g"
    NEW_SIZE="512m"
else
    # 大于2G内存的容器
    HEAP_PERCENT=75
    HEAP_SIZE="${HEAP_PERCENT}%"
fi

# 组装JVM参数
JVM_ARGS="
-Xms${HEAP_SIZE}
-Xmx${HEAP_SIZE}
-XX:+UseG1GC
-XX:MaxGCPauseMillis=100
-XX:+UseContainerSupport
-XX:MaxDirectMemorySize=256m
-XX:MetaspaceSize=128m
-XX:MaxMetaspaceSize=256m
-XX:+PrintGCDetails
-XX:+PrintGCTimeStamps
-Xloggc:/var/log/gc-%t.log
-XX:+UseGCLogFileRotation
-XX:NumberOfGCLogFiles=5
-XX:GCLogFileSize=10M
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/var/log/heapdump/
"

echo "Container Memory: ${CONTAINER_MEMORY_MB}MB"
echo "JVM Args: $JVM_ARGS"

# 启动应用
exec java $JVM_ARGS -jar /app/app.jar
```

**优化效果：**
- 容器稳定性：零OOMKilled事件
- 内存使用率：从95%降低到75%
- GC停顿时间：平均80ms
- 启动时间：减少20%

#### 1.4.5 JVM调优最佳实践总结

**1. 调优流程**
```
问题发现 → 现状分析 → 根因定位 → 方案制定 → 实施验证 → 持续监控
```

**2. 调优工具箱**
```bash
# 监控工具
jps          # 查看Java进程
jstat        # 查看GC统计信息
jmap         # 生成堆转储
jstack       # 生成线程转储
jinfo        # 查看和修改JVM参数

# 分析工具
MAT          # 内存分析工具
GCViewer     # GC日志分析
Arthas       # 在线诊断工具
JProfiler    # 性能分析工具
```

**3. 通用调优原则**
- **内存配置**：堆内存设置为系统内存的70-80%
- **GC选择**：低延迟场景选G1/ZGC，高吞吐选Parallel
- **监控告警**：建立完善的监控体系
- **分步优化**：一次只调整一个参数
- **压测验证**：充分的压力测试验证效果

**4. 不同场景的推荐配置**

```bash
# Web应用（低延迟优先）
-XX:+UseG1GC
-XX:MaxGCPauseMillis=100
-XX:G1HeapRegionSize=16m

# 批处理应用（高吞吐优先）
-XX:+UseParallelGC
-XX:ParallelGCThreads=8
-XX:+UseParallelOldGC

# 微服务（资源受限）
-XX:+UseContainerSupport
-XX:MaxRAMPercentage=75.0
-XX:+UseG1GC

# 大数据处理（大内存）
-XX:+UseG1GC
-XX:G1HeapRegionSize=32m
-XX:+UseLargePages
```

## 2. 并发编程

### 2.1 线程基础
**Q: 线程的生命周期状态及其转换？**

#### Java线程状态详解

**线程状态枚举（Thread.State）：**
- **NEW**：创建但未启动
- **RUNNABLE**：可运行状态（包含运行中和就绪）
- **BLOCKED**：阻塞等待锁
- **WAITING**：无限期等待
- **TIMED_WAITING**：有时限等待
- **TERMINATED**：终止

#### 线程状态转换详细分析

```java
// 线程状态转换演示代码
public class ThreadStateDemo {
    
    private static final Object lock = new Object();
    
    public static void main(String[] args) throws InterruptedException {
        
        // 1. NEW状态：线程创建但未启动
        Thread thread1 = new Thread(() -> {
            try {
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }, "Thread-1");
        
        System.out.println("1. 线程创建后状态: " + thread1.getState()); // NEW
        
        // 2. NEW → RUNNABLE：调用start()方法
        thread1.start();
        System.out.println("2. 调用start()后状态: " + thread1.getState()); // RUNNABLE
        
        // 3. 演示BLOCKED状态
        Thread thread2 = new Thread(() -> {
            synchronized (lock) {
                try {
                    Thread.sleep(2000);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }
        }, "Thread-2");
        
        Thread thread3 = new Thread(() -> {
            synchronized (lock) { // 等待thread2释放锁
                System.out.println("Thread-3获得锁");
            }
        }, "Thread-3");
        
        thread2.start();
        Thread.sleep(100); // 确保thread2先获得锁
        thread3.start();
        Thread.sleep(100);
        
        System.out.println("3. Thread-3等待锁状态: " + thread3.getState()); // BLOCKED
        
        // 4. 演示WAITING状态
        Thread thread4 = new Thread(() -> {
            synchronized (lock) {
                try {
                    lock.wait(); // 无限期等待
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }
        }, "Thread-4");
        
        thread4.start();
        Thread.sleep(100);
        System.out.println("4. Thread-4等待状态: " + thread4.getState()); // WAITING
        
        // 5. 演示TIMED_WAITING状态
        Thread thread5 = new Thread(() -> {
            try {
                Thread.sleep(5000); // 有时限等待
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }, "Thread-5");
        
        thread5.start();
        Thread.sleep(100);
        System.out.println("5. Thread-5定时等待状态: " + thread5.getState()); // TIMED_WAITING
        
        // 6. 等待所有线程结束，演示TERMINATED状态
        thread1.join();
        System.out.println("6. Thread-1结束后状态: " + thread1.getState()); // TERMINATED
        
        // 唤醒thread4
        synchronized (lock) {
            lock.notify();
        }
        
        // 等待其他线程结束
        thread2.join();
        thread3.join();
        thread4.join();
        thread5.join();
    }
}
```

#### 线程状态转换图解

```
简单的线程状态转换流程：

1. NEW（新建）
   ↓ [调用start()方法]
   
2. RUNNABLE（可运行）
   ↓ [根据不同情况转换到以下状态之一]
   
3a. BLOCKED（阻塞）        3b. WAITING（等待）        3c. TIMED_WAITING（限时等待）
    等待获取锁                 无限期等待                   有时间限制的等待
    ↓ [获得锁]                 ↓ [被唤醒]                   ↓ [超时或被唤醒]
    
4. 返回到 RUNNABLE（可运行）
   ↓ [线程执行完毕]
   
5. TERMINATED（终止）
```

**状态转换触发条件：**
- NEW → RUNNABLE：调用 `start()` 方法
- RUNNABLE → BLOCKED：等待获取 synchronized 锁
- RUNNABLE → WAITING：调用 `wait()`、`join()` 等方法
- RUNNABLE → TIMED_WAITING：调用 `sleep()`、`wait(timeout)` 等方法
- BLOCKED/WAITING/TIMED_WAITING → RUNNABLE：获得锁、被唤醒、超时等
- RUNNABLE → TERMINATED：线程执行完毕或异常终止

#### 各状态转换的具体触发条件

**1. NEW → RUNNABLE**
```java
Thread thread = new Thread(() -> {
    // 线程体
});
thread.start(); // 触发状态转换
```

**2. RUNNABLE → BLOCKED**
```java
// 线程尝试获取已被其他线程持有的synchronized锁
public synchronized void method() {
    // 如果锁被其他线程持有，当前线程进入BLOCKED状态
}

// 或者
synchronized(object) {
    // 同样的情况
}
```

**3. RUNNABLE → WAITING**
```java
// 以下操作会使线程进入WAITING状态：

// 1. Object.wait()（不带超时参数）
synchronized(obj) {
    obj.wait(); // 进入WAITING状态
}

// 2. Thread.join()（不带超时参数）
otherThread.join(); // 等待otherThread结束

// 3. LockSupport.park()
LockSupport.park(); // 线程暂停
```

**4. RUNNABLE → TIMED_WAITING**
```java
// 以下操作会使线程进入TIMED_WAITING状态：

// 1. Thread.sleep(long millis)
Thread.sleep(1000); // 休眠1秒

// 2. Object.wait(long timeout)
synchronized(obj) {
    obj.wait(1000); // 最多等待1秒
}

// 3. Thread.join(long millis)
otherThread.join(1000); // 最多等待1秒

// 4. LockSupport.parkNanos(long nanos)
LockSupport.parkNanos(1000000000L); // 暂停1秒

// 5. LockSupport.parkUntil(long deadline)
LockSupport.parkUntil(System.currentTimeMillis() + 1000);
```

**5. BLOCKED/WAITING/TIMED_WAITING → RUNNABLE**
```java
// 从BLOCKED到RUNNABLE
// 当线程获得锁时自动转换

// 从WAITING到RUNNABLE
synchronized(obj) {
    obj.notify();     // 唤醒一个等待线程
    obj.notifyAll();  // 唤醒所有等待线程
}
LockSupport.unpark(thread); // 唤醒被park的线程

// 从TIMED_WAITING到RUNNABLE
// 1. 超时自动唤醒
// 2. 被interrupt()中断
// 3. 被notify()/notifyAll()唤醒（如果是wait(timeout)）
// 4. 被unpark()唤醒（如果是parkNanos/parkUntil）
```

**6. RUNNABLE → TERMINATED**
```java
// 线程正常执行完毕
public void run() {
    // 执行线程任务
    return; // 线程结束，进入TERMINATED状态
}

// 线程因未捕获异常而终止
public void run() {
    throw new RuntimeException("异常"); // 线程异常终止
}
```

#### 实际应用中的状态监控

```java
// 线程状态监控工具类
public class ThreadStateMonitor {
    
    public static void monitorThreadState(Thread thread, String threadName) {
        Thread monitor = new Thread(() -> {
            while (thread.isAlive()) {
                Thread.State state = thread.getState();
                System.out.printf("[%s] %s 当前状态: %s%n", 
                    LocalTime.now(), threadName, state);
                
                try {
                    Thread.sleep(500); // 每500ms检查一次
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    break;
                }
            }
            System.out.printf("[%s] %s 最终状态: %s%n", 
                LocalTime.now(), threadName, thread.getState());
        });
        
        monitor.setDaemon(true);
        monitor.start();
    }
    
    // 获取线程详细信息
    public static void printThreadInfo(Thread thread) {
        System.out.println("===== 线程信息 =====");
        System.out.println("线程名称: " + thread.getName());
        System.out.println("线程ID: " + thread.getId());
        System.out.println("线程状态: " + thread.getState());
        System.out.println("是否存活: " + thread.isAlive());
        System.out.println("是否守护线程: " + thread.isDaemon());
        System.out.println("线程优先级: " + thread.getPriority());
        System.out.println("所属线程组: " + thread.getThreadGroup().getName());
        System.out.println("是否被中断: " + thread.isInterrupted());
    }
}
```

#### 线程状态转换的常见问题

**1. 为什么没有RUNNING状态？**
```java
// Java的RUNNABLE状态包含了操作系统层面的READY和RUNNING两种状态
// 这是因为JVM无法精确知道线程在操作系统层面的确切状态
public class RunnableStateExplanation {
    /*
     * RUNNABLE状态表示：
     * 1. 线程正在JVM中执行（对应OS的RUNNING）
     * 2. 线程等待操作系统分配CPU时间（对应OS的READY）
     * 3. 线程可能在等待操作系统资源，如I/O（仍然是RUNNABLE）
     */
}
```

**2. BLOCKED vs WAITING vs TIMED_WAITING 的区别**
```java
public class StateComparison {
    
    // BLOCKED：等待获取锁
    public void demonstrateBlocked() {
        Object lock = new Object();
        
        // 线程1获得锁
        new Thread(() -> {
            synchronized (lock) {
                try {
                    Thread.sleep(5000);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }
        }).start();
        
        // 线程2等待锁 - 进入BLOCKED状态
        new Thread(() -> {
            synchronized (lock) { // 在这里等待锁
                System.out.println("获得锁");
            }
        }).start();
    }
    
    // WAITING：主动等待唤醒
    public void demonstrateWaiting() {
        Object lock = new Object();
        
        new Thread(() -> {
            synchronized (lock) {
                try {
                    lock.wait(); // 主动进入WAITING状态
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }
        }).start();
    }
    
    // TIMED_WAITING：有时限的等待
    public void demonstrateTimedWaiting() {
        new Thread(() -> {
            try {
                Thread.sleep(1000); // 进入TIMED_WAITING状态
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }).start();
    }
}
```

**3. 中断对线程状态的影响**
```java
public class InterruptImpact {
    
    public void demonstrateInterrupt() {
        Thread sleepingThread = new Thread(() -> {
            try {
                System.out.println("线程开始休眠，状态: " + Thread.currentThread().getState());
                Thread.sleep(10000); // TIMED_WAITING状态
            } catch (InterruptedException e) {
                System.out.println("线程被中断，状态: " + Thread.currentThread().getState());
                Thread.currentThread().interrupt(); // 重新设置中断标志
                return;
            }
        });
        
        sleepingThread.start();
        
        // 2秒后中断线程
        try {
            Thread.sleep(2000);
            System.out.println("中断前线程状态: " + sleepingThread.getState());
            sleepingThread.interrupt(); // 中断休眠线程
            Thread.sleep(100);
            System.out.println("中断后线程状态: " + sleepingThread.getState());
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}
```

#### 线程状态转换的性能考虑

```java
// 线程状态转换的开销分析
public class StateTransitionPerformance {
    
    // 频繁的状态转换会影响性能
    public void demonstratePerformanceImpact() {
        long startTime = System.nanoTime();
        
        // 避免这样的代码：频繁的短时间sleep
        for (int i = 0; i < 1000; i++) {
            try {
                Thread.sleep(1); // 频繁的RUNNABLE → TIMED_WAITING → RUNNABLE
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
        
        long endTime = System.nanoTime();
        System.out.println("频繁状态转换耗时: " + (endTime - startTime) / 1000000 + "ms");
        
        // 更好的做法：减少状态转换
        startTime = System.nanoTime();
        try {
            Thread.sleep(1000); // 一次较长的sleep
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        endTime = System.nanoTime();
        System.out.println("单次状态转换耗时: " + (endTime - startTime) / 1000000 + "ms");
    }
}
```

#### 总结：线程状态转换最佳实践

1. **理解状态含义**：准确理解每种状态的含义和触发条件
2. **避免频繁转换**：减少不必要的状态转换以提高性能
3. **正确处理中断**：在可中断的操作中正确处理InterruptedException
4. **使用高级并发工具**：优先使用java.util.concurrent包中的工具类
5. **监控线程状态**：在调试时使用线程状态监控来诊断问题

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

#### 线程池状态详解

**线程池生命周期状态：**

```java
// ThreadPoolExecutor的内部状态定义
public class ThreadPoolExecutor extends AbstractExecutorService {
    
    // 线程池状态常量（使用AtomicInteger的高位存储）
    private static final int RUNNING    = -1 << COUNT_BITS;  // 运行状态
    private static final int SHUTDOWN   =  0 << COUNT_BITS;  // 关闭状态
    private static final int STOP       =  1 << COUNT_BITS;  // 停止状态
    private static final int TIDYING    =  2 << COUNT_BITS;  // 整理状态
    private static final int TERMINATED =  3 << COUNT_BITS;  // 终止状态
    
    // 状态和线程数量的复合字段
    private final AtomicInteger ctl = new AtomicInteger(ctlOf(RUNNING, 0));
}
```

#### 线程池状态转换图

```
线程池状态转换流程：

1. RUNNING（运行）
   - 接受新任务，处理队列中的任务
   ↓ [shutdown()方法]
   
2. SHUTDOWN（关闭）
   - 不接受新任务，但处理队列中的任务
   ↓ [shutdownNow()方法 或 队列为空且线程为0]
   
3. STOP（停止）
   - 不接受新任务，不处理队列任务，中断正在执行的任务
   ↓ [所有线程终止]
   
4. TIDYING（整理）
   - 所有任务已终止，线程池中的线程数为0
   ↓ [terminated()方法执行完毕]
   
5. TERMINATED（终止）
   - terminated()方法执行完毕
```

#### 线程池状态转换详细分析

**1. RUNNING → SHUTDOWN**
```java
public class ThreadPoolStateDemo {
    
    public void demonstrateShutdown() {
        ThreadPoolExecutor executor = new ThreadPoolExecutor(
            2, 4, 60L, TimeUnit.SECONDS,
            new LinkedBlockingQueue<>(10)
        );
        
        // 线程池初始状态为RUNNING
        System.out.println("初始状态: " + getPoolState(executor));
        
        // 提交一些任务
        for (int i = 0; i < 5; i++) {
            final int taskId = i;
            executor.submit(() -> {
                try {
                    Thread.sleep(2000);
                    System.out.println("任务 " + taskId + " 完成");
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    System.out.println("任务 " + taskId + " 被中断");
                }
            });
        }
        
        // 调用shutdown()，状态变为SHUTDOWN
        executor.shutdown();
        System.out.println("shutdown后状态: " + getPoolState(executor));
        
        // shutdown后仍会处理队列中的任务
        try {
            if (!executor.awaitTermination(5, TimeUnit.SECONDS)) {
                System.out.println("等待超时，强制关闭");
                executor.shutdownNow();
            }
        } catch (InterruptedException e) {
            executor.shutdownNow();
            Thread.currentThread().interrupt();
        }
        
        System.out.println("最终状态: " + getPoolState(executor));
    }
    
    // 获取线程池状态的工具方法
    private String getPoolState(ThreadPoolExecutor executor) {
        if (executor.isTerminated()) {
            return "TERMINATED";
        } else if (executor.isTerminating()) {
            return "TIDYING";
        } else if (executor.isShutdown()) {
            return "SHUTDOWN";
        } else {
            return "RUNNING";
        }
    }
}
```
```

**2. RUNNING → STOP**
```java
public void demonstrateShutdownNow() {
    ThreadPoolExecutor executor = new ThreadPoolExecutor(
        2, 4, 60L, TimeUnit.SECONDS,
        new LinkedBlockingQueue<>(10)
    );
    
    // 提交一些长时间任务
    for (int i = 0; i < 5; i++) {
        final int taskId = i;
        executor.submit(() -> {
            try {
                Thread.sleep(10000); // 模拟长时间任务
                System.out.println("任务 " + taskId + " 完成");
            } catch (InterruptedException e) {
                System.out.println("任务 " + taskId + " 被中断");
                Thread.currentThread().interrupt();
            }
        });
    }
    
    Thread.sleep(1000); // 让任务开始执行
    
    // 调用shutdownNow()，状态直接变为STOP
    List<Runnable> pendingTasks = executor.shutdownNow();
    System.out.println("被取消的任务数量: " + pendingTasks.size());
    System.out.println("shutdownNow后状态: " + getPoolState(executor));
}
```

#### 线程池状态监控和最佳实践

```java
// 线程池状态监控工具类
public class ThreadPoolMonitor {
    
    public void monitorThreadPoolState(ThreadPoolExecutor executor, String poolName) {
        ScheduledExecutorService monitor = Executors.newSingleThreadScheduledExecutor();
        
        monitor.scheduleAtFixedRate(() -> {
            System.out.printf("[%s] %s 线程池状态:%n", LocalTime.now(), poolName);
            System.out.printf("状态: %s%n", getDetailedPoolState(executor));
            System.out.printf("核心线程数: %d%n", executor.getCorePoolSize());
            System.out.printf("当前线程数: %d%n", executor.getPoolSize());
            System.out.printf("活跃线程数: %d%n", executor.getActiveCount());
            System.out.printf("队列任务数: %d%n", executor.getQueue().size());
            System.out.println("-".repeat(50));
            
            if (executor.isTerminated()) {
                monitor.shutdown();
            }
        }, 0, 2, TimeUnit.SECONDS);
    }
    
    private String getDetailedPoolState(ThreadPoolExecutor executor) {
        if (executor.isTerminated()) {
            return "TERMINATED - 线程池已完全终止";
        } else if (executor.isTerminating()) {
            return "TIDYING - 正在整理和终止";
        } else if (executor.isShutdown()) {
            return "SHUTDOWN - 不接受新任务，处理剩余任务";
        } else {
            return "RUNNING - 正常运行";
        }
    }
}
```

**线程池状态管理最佳实践：**
1. **始终检查线程池状态**：在提交任务前检查是否为RUNNING状态
2. **合理设置关闭超时时间**：给予足够时间完成正在执行的任务
3. **正确处理被拒绝的任务**：选择合适的拒绝策略
4. **实时监控线程池健康状态**：监控线程数、队列长度等指标
5. **优雅关闭线程池**：在应用关闭时避免数据丢失和资源泄漏

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

#### MySQL优化实战案例

#### 案例一：电商订单系统慢查询优化

**问题背景：**
某电商平台的订单查询接口响应时间从原来的100ms增加到5秒以上，严重影响用户体验。

**问题SQL：**
```sql
-- 原始问题SQL
SELECT o.order_id, o.order_amount, o.created_time, 
       u.username, u.phone, 
       p.product_name, p.price
FROM orders o 
JOIN users u ON o.user_id = u.user_id 
JOIN order_items oi ON o.order_id = oi.order_id 
JOIN products p ON oi.product_id = p.product_id 
WHERE o.created_time >= '2023-01-01' 
AND o.status = 'completed' 
AND u.city = '北京' 
ORDER BY o.created_time DESC 
LIMIT 20;
```

**问题分析：**
```sql
-- 查看执行计划
EXPLAIN FORMAT=JSON SELECT ...;

-- 执行计划显示问题：
-- 1. orders表全表扫描（500万条记录）
-- 2. users表根据city字段过滤时没有使用索引
-- 3. JOIN操作使用了临时表和文件排序
-- 4. 最终扫描了数百万行数据才返回20条结果
```

**优化方案：**

**1. 索引优化**
```sql
-- 创建复合索引
CREATE INDEX idx_orders_time_status ON orders(created_time, status);
CREATE INDEX idx_users_city ON users(city);
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_products_id ON products(product_id);

-- 创建覆盖索引（避免回表）
CREATE INDEX idx_orders_covering ON orders(created_time, status, order_id, user_id, order_amount);
```

**2. SQL重写优化**
```sql
-- 优化后的SQL
SELECT o.order_id, o.order_amount, o.created_time, 
       u.username, u.phone, 
       p.product_name, p.price
FROM (
    -- 先通过索引快速定位订单
    SELECT order_id, user_id, order_amount, created_time
    FROM orders 
    WHERE created_time >= '2023-01-01' 
    AND status = 'completed'
    ORDER BY created_time DESC 
    LIMIT 20
) o
JOIN users u ON o.user_id = u.user_id AND u.city = '北京'
JOIN order_items oi ON o.order_id = oi.order_id 
JOIN products p ON oi.product_id = p.product_id;
```

**3. 进一步优化 - 分页查询**
```sql
-- 使用游标分页替代OFFSET
-- 第一页
SELECT * FROM (
    SELECT o.order_id, o.order_amount, o.created_time, 
           u.username, u.phone
    FROM orders o 
    JOIN users u ON o.user_id = u.user_id 
    WHERE o.created_time >= '2023-01-01' 
    AND o.status = 'completed'
    AND u.city = '北京'
    ORDER BY o.created_time DESC 
    LIMIT 20
) result;

-- 后续页（基于上一页最后一条记录的时间）
SELECT * FROM (
    SELECT o.order_id, o.order_amount, o.created_time, 
           u.username, u.phone
    FROM orders o 
    JOIN users u ON o.user_id = u.user_id 
    WHERE o.created_time >= '2023-01-01' 
    AND o.created_time < '2023-10-15 10:30:45'  -- 上一页最后一条记录的时间
    AND o.status = 'completed'
    AND u.city = '北京'
    ORDER BY o.created_time DESC 
    LIMIT 20
) result;
```

**优化效果：**
- 查询时间：从5秒降低到50ms
- 扫描行数：从500万行降低到100行
- CPU使用率：降低70%
- 并发能力：提升10倍

#### 案例二：用户画像系统索引设计优化

**业务场景：**
用户画像系统需要根据多个维度快速筛选用户，包括年龄、性别、地区、兴趣标签等。

**原始表结构：**
```sql
CREATE TABLE user_profiles (
    user_id BIGINT PRIMARY KEY,
    age INT,
    gender TINYINT,  -- 1:男 2:女
    province VARCHAR(20),
    city VARCHAR(50),
    interests TEXT,  -- 兴趣标签，逗号分隔
    last_login_time DATETIME,
    register_time DATETIME,
    user_level TINYINT,  -- 用户等级
    INDEX idx_age (age),
    INDEX idx_city (city)
);
```

**常见查询场景：**
```sql
-- 场景1：根据年龄和性别筛选
SELECT COUNT(*) FROM user_profiles 
WHERE age BETWEEN 25 AND 35 AND gender = 1;

-- 场景2：根据地区和用户等级筛选
SELECT user_id FROM user_profiles 
WHERE province = '北京' AND user_level >= 3 
ORDER BY last_login_time DESC LIMIT 100;

-- 场景3：根据兴趣标签筛选
SELECT user_id FROM user_profiles 
WHERE interests LIKE '%游戏%' AND age BETWEEN 18 AND 30;
```

**问题分析：**
1. 复合查询条件无法有效使用索引
2. TEXT字段的LIKE查询性能极差
3. 多维度组合查询导致索引失效

**优化方案：**

**1. 重新设计表结构**
```sql
-- 主表优化
CREATE TABLE user_profiles_optimized (
    user_id BIGINT PRIMARY KEY,
    age TINYINT,  -- 年龄范围编码：1(18-25), 2(26-35), 3(36-45), etc.
    gender TINYINT,
    province_code SMALLINT,  -- 省份编码
    city_code INT,           -- 城市编码
    last_login_time DATETIME,
    register_time DATETIME,
    user_level TINYINT,
    -- 复合索引设计
    INDEX idx_age_gender (age, gender),
    INDEX idx_province_level (province_code, user_level, last_login_time),
    INDEX idx_city_age (city_code, age),
    INDEX idx_login_time (last_login_time)
);

-- 兴趣标签单独表
CREATE TABLE user_interests (
    user_id BIGINT,
    interest_id INT,  -- 兴趣标签ID
    weight DECIMAL(3,2) DEFAULT 1.0,  -- 兴趣权重
    PRIMARY KEY (user_id, interest_id),
    INDEX idx_interest_user (interest_id, user_id)
);

-- 兴趣标签字典表
CREATE TABLE interest_dict (
    interest_id INT PRIMARY KEY,
    interest_name VARCHAR(50),
    category VARCHAR(20)
);
```

**2. 优化后的查询**
```sql
-- 优化场景1：年龄性别查询
SELECT COUNT(*) FROM user_profiles_optimized 
WHERE age IN (2, 3) AND gender = 1;  -- 使用复合索引

-- 优化场景2：地区等级查询
SELECT user_id FROM user_profiles_optimized 
WHERE province_code = 110000 AND user_level >= 3 
ORDER BY last_login_time DESC LIMIT 100;

-- 优化场景3：兴趣标签查询
SELECT up.user_id 
FROM user_profiles_optimized up
JOIN user_interests ui ON up.user_id = ui.user_id
JOIN interest_dict id ON ui.interest_id = id.interest_id
WHERE id.interest_name = '游戏' 
AND up.age IN (1, 2);  -- 18-35岁
```

**3. 分区表优化**
```sql
-- 按注册时间分区
CREATE TABLE user_profiles_partitioned (
    -- 字段定义同上
) PARTITION BY RANGE (YEAR(register_time)) (
    PARTITION p2020 VALUES LESS THAN (2021),
    PARTITION p2021 VALUES LESS THAN (2022),
    PARTITION p2022 VALUES LESS THAN (2023),
    PARTITION p2023 VALUES LESS THAN (2024),
    PARTITION p_future VALUES LESS THAN MAXVALUE
);
```

#### 案例三：高并发秒杀系统数据库优化

**业务场景：**
电商秒杀活动，1000个商品，100万用户同时抢购，要求系统能够承受高并发访问。

**原始方案问题：**
```sql
-- 原始的秒杀扣减库存SQL
UPDATE products 
SET stock = stock - 1 
WHERE product_id = 12345 AND stock > 0;

-- 问题：
-- 1. 高并发下行锁竞争激烈
-- 2. 大量UPDATE操作导致锁等待
-- 3. 数据库成为性能瓶颈
```

**数据库层面优化方案：**

**1. 表结构优化**
```sql
-- 秒杀商品表
CREATE TABLE seckill_products (
    product_id BIGINT PRIMARY KEY,
    total_stock INT NOT NULL,
    current_stock INT NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    version INT DEFAULT 0,  -- 乐观锁版本号
    INDEX idx_time (start_time, end_time)
) ENGINE=InnoDB;

-- 秒杀订单表（分库分表）
CREATE TABLE seckill_orders_0 (
    order_id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    order_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TINYINT DEFAULT 1,  -- 1:待支付 2:已支付 3:已取消
    INDEX idx_user_product (user_id, product_id),
    INDEX idx_product_time (product_id, order_time)
) ENGINE=InnoDB;

-- 创建多个分表
CREATE TABLE seckill_orders_1 LIKE seckill_orders_0;
CREATE TABLE seckill_orders_2 LIKE seckill_orders_0;
-- ... 创建更多分表
```

**2. 乐观锁实现**
```java
// Java代码实现乐观锁
@Service
public class SeckillService {
    
    @Autowired
    private SeckillProductMapper seckillProductMapper;
    
    @Transactional
    public boolean seckillProduct(Long productId, Long userId) {
        
        // 1. 查询商品信息（包含版本号）
        SeckillProduct product = seckillProductMapper.selectByIdWithVersion(productId);
        
        if (product == null || product.getCurrentStock() <= 0) {
            return false;
        }
        
        // 2. 使用乐观锁更新库存
        int updateCount = seckillProductMapper.updateStockWithVersion(
            productId, product.getVersion());
        
        if (updateCount == 0) {
            // 更新失败，说明版本号已变化（其他事务已修改）
            return false;
        }
        
        // 3. 创建订单（插入到分表）
        createSeckillOrder(productId, userId);
        
        return true;
    }
}
```

```sql
-- 对应的SQL实现
-- 查询商品信息
SELECT product_id, current_stock, version 
FROM seckill_products 
WHERE product_id = #{productId};

-- 乐观锁更新库存
UPDATE seckill_products 
SET current_stock = current_stock - 1, 
    version = version + 1 
WHERE product_id = #{productId} 
AND version = #{version} 
AND current_stock > 0;
```

**3. 预分配库存策略**
```sql
-- 库存分配表
CREATE TABLE stock_allocation (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    product_id BIGINT NOT NULL,
    batch_no INT NOT NULL,  -- 批次号
    allocated_stock INT NOT NULL,  -- 分配的库存数量
    used_stock INT DEFAULT 0,  -- 已使用的库存
    status TINYINT DEFAULT 1,  -- 1:可用 2:已用完
    INDEX idx_product_batch (product_id, batch_no)
) ENGINE=InnoDB;

-- 预先分配库存到不同批次
INSERT INTO stock_allocation (product_id, batch_no, allocated_stock) VALUES
(12345, 1, 200),
(12345, 2, 200),
(12345, 3, 200),
(12345, 4, 200),
(12345, 5, 200);

-- 秒杀时分批次扣减
UPDATE stock_allocation 
SET used_stock = used_stock + 1
WHERE product_id = 12345 
AND batch_no = #{batchNo}
AND used_stock < allocated_stock;
```

**4. 数据库参数优化**
```sql
-- MySQL配置优化
[mysqld]
# 连接相关
max_connections = 3000
max_connect_errors = 1000
connect_timeout = 10

# InnoDB优化
innodb_buffer_pool_size = 8G  # 设置为内存的70-80%
innodb_log_file_size = 1G
innodb_log_buffer_size = 32M
innodb_flush_log_at_trx_commit = 2  # 提高写入性能
innodb_thread_concurrency = 16

# 查询缓存
query_cache_size = 256M
query_cache_type = 1

# 临时表优化
tmp_table_size = 256M
max_heap_table_size = 256M
```

**优化效果：**
- QPS：从1000提升到10000
- 响应时间：从500ms降低到50ms
- 数据库CPU使用率：从90%降低到30%
- 锁等待时间：减少95%

#### MySQL性能监控和诊断

```sql
-- 慢查询监控
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 0.5;  -- 超过0.5秒记录
SET GLOBAL log_queries_not_using_indexes = 'ON';

-- 查看当前正在执行的查询
SELECT 
    id,
    user,
    host,
    db,
    command,
    time,
    state,
    LEFT(info, 100) as query_start
FROM information_schema.processlist 
WHERE time > 5 AND command != 'Sleep'
ORDER BY time DESC;

-- 分析表的索引使用情况
SELECT 
    table_schema,
    table_name,
    index_name,
    seq_in_index,
    column_name,
    cardinality
FROM information_schema.statistics 
WHERE table_schema = 'your_database'
ORDER BY table_name, index_name, seq_in_index;

-- 查看表的存储引擎和大小
SELECT 
    table_name,
    engine,
    table_rows,
    ROUND((data_length + index_length) / 1024 / 1024, 2) AS size_mb,
    ROUND(data_length / 1024 / 1024, 2) AS data_mb,
    ROUND(index_length / 1024 / 1024, 2) AS index_mb
FROM information_schema.tables 
WHERE table_schema = 'your_database'
ORDER BY (data_length + index_length) DESC;
```

**MySQL优化最佳实践总结：**
1. **索引设计**：根据查询模式设计复合索引，遵循最左前缀原则
2. **查询优化**：避免全表扫描，合理使用LIMIT，避免SELECT *
3. **表结构优化**：选择合适的数据类型，适当的表分区和分表
4. **并发控制**：使用乐观锁减少锁竞争，合理设置隔离级别
5. **配置调优**：根据硬件资源调整MySQL参数
6. **监控告警**：建立完善的慢查询监控和性能指标监控

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