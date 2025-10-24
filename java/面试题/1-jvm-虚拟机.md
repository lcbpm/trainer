# 1. JVM 虚拟机

## 目录
- [1.1 内存结构](#11-内存结构)
- [1.2 垃圾回收](#12-垃圾回收)
- [1.3 类加载机制](#13-类加载机制)
- [1.4 JVM 调优实战](#14-jvm-调优实战)

---

## 1.1 内存结构
**Q: 详细说明JVM内存模型？**
- **堆内存（Heap）**：存储对象实例，分为新生代和老年代
  - 新生代：Eden区 + 2个Survivor区（S0, S1）
  - 老年代：长期存活的对象
- **方法区（Method Area）**：存储类的元数据信息，是线程共享的内存区域
  - **类信息**：类的版本、字段、方法、接口等描述信息
  - **运行时常量池**：编译期生成的字面量和符号引用
  - **静态变量**：类级别的变量（static变量）
  - **即时编译器编译后的代码**：JIT编译后的本地代码缓存
  - **字段信息**：字段的名称、类型、修饰符等
  - **方法信息**：方法的名称、返回类型、参数、异常信息等
- **程序计数器（PC Register）**：记录当前线程正在执行的字节码指令地址，提供程序执行位置信息
- **虚拟机栈（VM Stack）**：存储局部变量、操作数栈
- **本地方法栈（Native Method Stack）**：调用本地方法

**Q: 为什么内存模型要这样设计，而不是其他方式？**

### JVM内存模型设计原理深度分析

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
- **弱分代假说（Weak Generational Hypothesis）**：绝大多数对象都是"朝生夕死"的，即大部分新创建的对象会在很短时间内变成垃圾
- **强分代假说（Strong Generational Hypothesis）**：越"老"的对象越难死，即经历过多次垃圾收集仍然存活的对象，未来死亡的概率会越来越小

**通俗理解：**
- **弱分代假说**：就像人的一生，大部分想法、计划都是临时的，很快就会被遗忘或放弃
- **强分代假说**：能坚持下来的事物（如经典书籍、老品牌）往往具有更持久的生命力

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
// 方法区存储内容的简单理解
public class MethodAreaSimple {
    
    // 1. 静态变量（类级别的变量）
    private static int count = 0;
    private static String appName = "MyApp";
    
    // 2. 常量（编译时确定的值）
    public static final String VERSION = "1.0";
    public static final int MAX_SIZE = 100;
    
    // 3. 普通方法和字段的"说明书"信息
    private String name;  // 字段信息：名称、类型
    
    public void sayHello() {  // 方法信息：名称、参数、返回值
        System.out.println("Hello");
    }
    
    /*
     * 方法区主要存储4类信息：
     * 
     * 1. 类的基本信息：
     *    - 类名叫什么
     *    - 继承了哪个父类
     *    - 实现了哪些接口
     * 
     * 2. 静态变量：
     *    - static修饰的变量
     *    - 所有对象共享
     * 
     * 3. 常量池：
     *    - 字符串常量如"Hello"
     *    - 数字常量如100
     * 
     * 4. 方法和字段的"目录"：
     *    - 有哪些方法
     *    - 有哪些字段
     *    - 但具体的数据在堆里
     */
}

// 通俗理解：方法区就像图书馆的目录
class LibraryAnalogy {
    /*
     * 如果把JVM比作图书馆：
     * 
     * 方法区 = 图书馆的目录和管理信息
     * - 记录有哪些书（类）
     * - 每本书有多少页（方法）
     * - 书放在哪个位置（内存地址）
     * 
     * 堆内存 = 真正的书架和书本
     * - 存放具体的书（对象）
     * - 书的内容（对象的数据）
     * 
     * 栈内存 = 读者的阅读记录
     * - 正在读哪本书（调用哪个方法）
     * - 读到第几页（执行到哪一行）
     */
    
    // JDK 8的重要变化：从永久代到元空间
    /*
     * JDK 7及之前：永久代（PermGen）
     * - 大小固定，容易内存溢出
     * 
     * JDK 8及之后：元空间（Metaspace）  
     * - 大小可以动态调整
     * - 不容易内存溢出
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

#### 为什么栈采用连续内存分配？

**1. 像书本一样的顺序**
```java
public class SimpleStackExample {
    
    public void methodA() {
        int a = 10;        // 第1页：变量a
        methodB();         // 翻到第2页
    }  // 回到第1页
    
    public void methodB() {
        int b = 20;        // 第2页：变量b  
        methodC();         // 翻到第3页
    }  // 回到第2页
    
    public void methodC() {
        int c = 30;        // 第3页：变量c
    }  // 回到第2页
    
    /*
     * 就像看书一样：
     * - 按顺序往下翻页（方法调用）
     * - 按顺序往回翻页（方法返回）
     * - 页码连续，查找快速
     */
}
```

**2. 速度超快**
```java
public class FastAllocation {
    
    public void stackAllocation() {
        // 栈分配：像移动书签一样简单
        int a = 1;    // 书签往下移4格
        int b = 2;    // 书签再往下移4格
        int c = 3;    // 书签再往下移4格
        // 方法结束：书签直接回到原位置
    }
    
    public void heapAllocation() {
        // 堆分配：像在仓库里找空位放东西
        Integer a = new Integer(1);  // 需要在仓库里找空位
        Integer b = new Integer(2);  // 可能离得很远
        Integer c = new Integer(3);  // 需要管理员回收
    }
    
    /*
     * 栈分配 = 移动书签（超快）
     * 堆分配 = 仓库找位置（较慢）
     */
}
```

**3. 自动清理**
```java
public class AutoCleanup {
    
    public void demonstrateAutoCleanup() {
        {
            int x = 100;     // x放在栈上
            String s = "hi"; // s的地址放在栈上
        } // 出了括号，x和s自动消失
        
        /*
         * 栈内存的优势：
         * - 用完就自动清理
         * - 不需要垃圾回收
         * - 不会内存泄漏
         */
    }
}
```

**简单比喻：栈就像叠盘子**
```java
public class PlateStackAnalogy {
    /*
     * 栈内存 = 叠盘子：
     * 
     * 1. 新盘子放在最上面（新变量）
     * 2. 拿盘子从最上面拿（方法返回）
     * 3. 盘子叠得整整齐齐（连续内存）
     * 4. 拿走很简单（自动回收）
     * 
     * 为什么不乱放？
     * - 整齐：容易找到和管理
     * - 快速：直接在顶部操作
     * - 安全：不会弄错顺序
     */
}
```

**总结：连续分配的好处**
- **简单**：像移动书签一样容易
- **快速**：比堆分配快几百倍
- **整齐**：内存排列有序
- **自动**：用完自动清理

**6. 程序计数器：执行位置的"导航仪"**

程序计数器（PC Register）就像是程序执行的"导航仪"，时刻记录着当前执行到哪里了。

```java
// 程序计数器的核心作用演示
public class ProgramCounterDemo {
    
    public void demonstratePC() {
        int a = 1;        // PC记录：正在执行第1条指令
        int b = 2;        // PC更新：移动到第2条指令  
        int c = a + b;    // PC更新：移动到第3条指令
        
        if (c > 0) {      // PC记录：当前在判断语句
            System.out.println("正数");  // PC可能跳转到这里
        } else {
            System.out.println("非正数");  // 或者跳转到这里
        }
    }
    
    // 多线程环境：每个线程都有自己的"导航仪"
    public void multiThreadDemo() {
        Thread thread1 = new Thread(() -> {
            // 线程1的PC：独立记录线程1的执行位置
            for (int i = 0; i < 5; i++) {
                System.out.println("线程1执行第" + i + "次循环");
                // PC记录：当前循环的具体位置
            }
        });
        
        Thread thread2 = new Thread(() -> {
            // 线程2的PC：独立记录线程2的执行位置  
            for (int i = 0; i < 3; i++) {
                System.out.println("线程2执行第" + i + "次循环");
                // PC记录：与线程1完全独立的位置信息
            }
        });
        
        thread1.start();
        thread2.start();
    }
}
```

**程序计数器提供的关键执行信息：**

**1. 当前执行位置** 
```java
public class ExecutionPosition {
    public void showPosition() {
        System.out.println("第1行");    // PC = 指令地址1
        System.out.println("第2行");    // PC = 指令地址2  
        System.out.println("第3行");    // PC = 指令地址3
        
        // PC就像书签，告诉我们读到第几页了
    }
}
```

**2. 线程切换时的位置保存**
```java
public class ThreadSwitching {
    /*
     * 线程切换过程：
     * 
     * 线程A执行中 → PC记录位置100
     * ↓ 操作系统切换线程
     * 线程B开始执行 → PC切换到线程B的位置200  
     * ↓ 再次切换
     * 线程A恢复执行 → PC恢复到位置100，继续执行
     * 
     * 就像多本书同时阅读，每本书都有自己的书签位置
     */
}
```

**3. 异常发生时的位置定位**
```java
public class ExceptionLocation {
    public void demonstrateException() {
        try {
            int a = 10;
            int b = 0;
            int result = a / b;  // PC记录：异常发生在这个位置
        } catch (ArithmeticException e) {
            // PC提供信息：异常发生在第几行、第几个字节码指令
            System.out.println("异常位置信息: " + e.getStackTrace()[0]);
        }
    }
}
```

**4. 方法调用时的返回地址记录**
```java
public class MethodCall {
    public void caller() {
        System.out.println("调用前");     // PC = 地址A
        helper();                        // PC记录：调用helper后应该返回到地址B
        System.out.println("调用后");     // PC = 地址B (返回位置)
    }
    
    public void helper() {
        System.out.println("帮助方法");   // PC在helper方法内部
        // 方法结束时，PC知道要返回到caller的地址B
    }
}
```

**为什么程序计数器如此重要？**

1. **执行追踪**：像GPS一样，随时知道程序"走"到哪里了
2. **线程隔离**：每个线程有独立的执行路径，不会混乱
3. **异常定位**：出错时能准确找到出错的位置
4. **调试支持**：调试器通过PC知道程序执行到第几行
5. **性能分析**：分析工具通过PC统计各部分代码的执行时间

**通俗比喻：**
- 程序计数器就像是**阅读时的书签**，记录读到第几页
- 多线程就像**同时阅读多本书**，每本书都有自己的书签位置
- 线程切换就像**换书阅读**，每次都能找到上次读到的位置
- 异常处理就像**读错了字**，能快速找到错误发生在第几页第几行

**Q: 直接内存是什么？为什么要有它？**

直接内存（Direct Memory）是JVM堆外的内存区域，专门为了解决传统I/O操作中的性能瓶颈而设计的。

**直接内存的核心作用：**
1. **减少内存拷贝次数**：从3次拷贝减少到2次拷贝
2. **提高I/O性能**：避免Java堆与系统内核之间的数据转换
3. **突破堆内存限制**：不占用Java堆空间，独立管理
4. **支持零拷贝技术**：为高性能网络和文件操作提供基础

**7. 直接内存：性能优化的关键技术**

**内存拷贝次数的具体对比：**

```java
// 直接内存性能优势详解
public class DirectMemoryAdvantage {
    
    // 传统I/O操作：3次内存拷贝
    public void traditionalIO() throws IOException {
        FileInputStream fis = new FileInputStream("data.txt");
        byte[] buffer = new byte[1024];
        
        /*
         * 传统I/O数据流转（3次拷贝）：
         * 
         * 第1次拷贝：磁盘文件 → 操作系统内核缓冲区
         * 第2次拷贝：操作系统内核缓冲区 → JVM堆内存
         * 第3次拷贝：JVM堆内存 → 应用程序变量
         * 
         * 问题：每次拷贝都需要CPU参与，消耗大量资源
         */
        int bytesRead = fis.read(buffer);  // 触发：内核缓冲区 → JVM堆 → buffer变量
        processData(buffer);  // 应用程序处理数据
    }
    
    // 直接内存操作：2次拷贝（减少1次）
    public void directMemoryIO() throws IOException {
        FileChannel channel = FileChannel.open(Paths.get("data.txt"));
        ByteBuffer directBuffer = ByteBuffer.allocateDirect(1024);
        
        /*
         * 直接内存数据流转（2次拷贝）：
         * 
         * 第1次拷贝：磁盘文件 → 操作系统内核缓冲区
         * 第2次拷贝：操作系统内核缓冲区 → 直接内存
         * 
         * 省略了：JVM堆内存这一层拷贝
         * 直接内存可以被应用程序直接访问，无需额外拷贝
         */
        int bytesRead = channel.read(directBuffer);  // 直接：内核缓冲区 → 直接内存
        processDirectBuffer(directBuffer);  // 应用程序直接处理直接内存中的数据
    }
    
    // 零拷贝技术：最高性能（接近0次拷贝）
    public void zeroCopyTransfer() throws IOException {
        FileChannel source = FileChannel.open(Paths.get("source.txt"));
        FileChannel target = FileChannel.open(Paths.get("target.txt"), 
            StandardOpenOption.WRITE, StandardOpenOption.CREATE);
        
        /*
         * 零拷贝数据流转（几乎0次拷贝）：
         * 
         * 数据直接在内核空间传输，不经过用户空间
         * 磁盘 → 内核缓冲区 → 网络缓冲区/目标文件
         * 
         * CPU参与度极低，性能最优
         */
        source.transferTo(0, source.size(), target);  // DMA直接传输，CPU几乎不参与
    }
}
```

**性能对比测试：**

```java
// 实际性能测试对比
public class PerformanceComparison {
    
    @Test
    public void compareMemoryCopyPerformance() {
        // 测试数据：1GB文件
        String testFile = "1GB_test_file.dat";
        
        // 传统I/O性能
        long traditionalTime = measureTime(() -> {
            try (FileInputStream fis = new FileInputStream(testFile)) {
                byte[] buffer = new byte[8192];
                while (fis.read(buffer) != -1) {
                    // 模拟数据处理
                }
            }
        });
        
        // 直接内存I/O性能  
        long directTime = measureTime(() -> {
            try (FileChannel channel = FileChannel.open(Paths.get(testFile))) {
                ByteBuffer directBuffer = ByteBuffer.allocateDirect(8192);
                while (channel.read(directBuffer) != -1) {
                    directBuffer.flip();
                    // 模拟数据处理
                    directBuffer.clear();
                }
            }
        });
        
        /*
         * 典型测试结果：
         * 传统I/O：      2500ms (100%)
         * 直接内存I/O：  1800ms (72%)   → 性能提升28%
         * 零拷贝：       800ms  (32%)   → 性能提升68%
         */
        System.out.println("传统I/O用时: " + traditionalTime + "ms");
        System.out.println("直接内存用时: " + directTime + "ms");
        System.out.println("性能提升: " + ((traditionalTime - directTime) * 100 / traditionalTime) + "%");
    }
}
```

**为什么直接内存能减少拷贝？**

```java
// 内存拷贝原理解析
public class MemoryCopyPrinciple {
    
    /*
     * 传统I/O的问题根源：
     * 
     * 1. 用户空间与内核空间隔离
     *    - 应用程序运行在用户空间
     *    - 文件系统运行在内核空间
     *    - 两者不能直接交换数据
     * 
     * 2. JVM堆内存在用户空间
     *    - JVM堆属于用户空间内存
     *    - 内核无法直接访问JVM堆
     *    - 必须通过中间缓冲区转换
     * 
     * 3. 数据流转路径复杂
     *    - 内核读取文件到内核缓冲区
     *    - 内核缓冲区拷贝到JVM堆
     *    - JVM堆拷贝到应用程序变量
     */
    
    /*
     * 直接内存的解决方案：
     * 
     * 1. 绕过JVM堆
     *    - 直接内存不在JVM堆中
     *    - 减少了JVM堆这一层拷贝
     * 
     * 2. 操作系统可直接访问
     *    - 直接内存可被操作系统直接操作
     *    - 内核可以直接将数据放入直接内存
     * 
     * 3. 应用程序可直接访问
     *    - 应用程序可以直接访问直接内存
     *    - 无需经过JVM堆中转
     */
}
```

**直接内存的实际应用场景：**

```java
// 高性能网络编程
public class NettyDirectMemoryExample {
    
    // Netty框架大量使用直接内存
    public void nettyExample() {
        // 直接内存缓冲区
        ByteBuf directBuffer = Unpooled.directBuffer(1024);
        
        /*
         * 网络数据流转：
         * 网络 → 网卡 → 内核缓冲区 → 直接内存 → 应用程序
         * 
         * 省略了JVM堆这一层，提高网络I/O性能
         */
        
        // 写入数据到直接内存
        directBuffer.writeBytes("Hello Network".getBytes());
        
        // 网络发送时，直接从直接内存发送，无需拷贝到JVM堆
        channel.writeAndFlush(directBuffer);
    }
}

// 大文件处理
public class BigFileProcessing {
    
    public void processLargeFile(String filePath) throws IOException {
        try (FileChannel channel = FileChannel.open(Paths.get(filePath))) {
            // 分配大块直接内存
            ByteBuffer buffer = ByteBuffer.allocateDirect(1024 * 1024); // 1MB
            
            /*
             * 处理大文件的优势：
             * 1. 减少GC压力：直接内存不在JVM堆中
             * 2. 提高I/O性能：减少内存拷贝
             * 3. 降低延迟：避免堆内存分配和回收
             */
            
            while (channel.read(buffer) > 0) {
                buffer.flip();
                // 直接处理直接内存中的数据
                processBuffer(buffer);
                buffer.clear();
            }
        }
    }
}
```

**直接内存 vs JVM堆内存对比：**

| 特性 | JVM堆内存 | 直接内存 |
|------|-----------|----------|
| **位置** | JVM用户空间 | 操作系统空间 |
| **GC管理** | 自动垃圾回收 | 手动释放 |
| **I/O性能** | 需要拷贝转换 | 直接访问 |
| **内存拷贝** | 3次拷贝 | 2次拷贝 |
| **分配速度** | 快速 | 较慢 |
| **释放速度** | GC自动 | 需手动调用 |
| **适用场景** | 常规对象存储 | 高性能I/O |

**通俗理解：**
- **传统I/O**：就像**邮件转发**，信件要经过多个邮局（内核→JVM堆→应用程序）
- **直接内存**：就像**直达快递**，减少一个中转站（内核→直接内存→应用程序）
- **零拷贝**：就像**同城直达**，几乎不需要中转（内核直接处理）

**总结：直接内存的核心价值**
1. **性能提升**：减少1次内存拷贝，I/O性能提升20-30%
2. **降低延迟**：避免JVM堆分配，减少GC停顿
3. **扩展容量**：不占用JVM堆空间，可独立扩展
4. **支持零拷贝**：为高性能应用提供基础设施

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

## 1.2 垃圾回收
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

## 1.3 类加载机制
**Q: 双亲委派模型的原理？**
- 类加载器层次：Bootstrap → Extension → Application → Custom
- 向上委派：先让父加载器尝试加载
- 向下委派：父加载器无法加载时，子加载器加载
- 好处：保证类的唯一性，防止核心类被篡改

**Q: 为什么是双亲委派，而不是其他模型？**

### 双亲委派模型的设计动机

1. **安全性考虑**
   - 防止核心API被恶意替换
   - 确保Java核心类库的完整性
   - 避免自定义类覆盖系统类

2. **类的唯一性保证**
   - 同一个类只能被同一个类加载器加载一次
   - 避免类的重复加载
   - 保证JVM中类的一致性

### 其他可能的类加载模型对比

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

### 双亲委派模型的实现机制

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

### 双亲委派模型的优势验证

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
```