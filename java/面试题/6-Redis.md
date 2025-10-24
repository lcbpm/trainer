# 6. Redis

## 目录
- [6.1 版本演进与特性](#61-版本演进与特性)
- [6.2 数据结构](#62-数据结构)
- [6.3 持久化机制](#63-持久化机制)
- [6.4 集群与高可用](#64-集群与高可用)
- [6.5 性能优化](#65-性能优化)
- [6.6 Redis集群原理](#66-redis集群原理)
- [6.7 ZSet底层数据结构](#67-zset底层数据结构)
  - [6.7.1 ZSet数据结构概述](#671-zset数据结构概述)
  - [6.7.2 跳跃表(Skip List)原理](#672-跳跃表skip-list原理)
  - [6.7.3 压缩列表(ziplist)实现](#673-压缩列表ziplist实现)
  - [6.7.4 ZSet内部编码选择](#674-zset内部编码选择)

---

## 6.1 版本演进与特性

**Q: Redis有哪些主要版本？各版本的核心特性是什么？**

### Redis版本时间线

**1.0版本（2009年）** - 基础功能
- 五种基本数据类型（String、List、Set、Hash、ZSet）
- 基本的GET/SET操作
- 单机模式

**2.0版本（2010年）** - 虚拟内存
- 虚拟内存支持（后续版本移除）
- Hash表优化
- 配置文件支持

**2.2版本（2010年）** - 持久化增强
- AOF（Append Only File）持久化
- VM（虚拟内存）性能提升

**2.4版本（2010年）** - 性能优化
- 内存优化
- 更多命令支持

**2.6版本（2012年）** - Lua脚本
``java
// Lua脚本示例
public class RedisLuaExample {
    public Long atomicIncrement(String key, long delta) {
        String luaScript = 
            "local current = redis.call('get', KEYS[1])" +
            "if current == false then" +
            "  current = 0" +
            "end" +
            "local result = current + ARGV[1]" +
            "redis.call('set', KEYS[1], result)" +
            "return result";
        
        return redisTemplate.execute(new DefaultRedisScript<>(luaScript, Long.class),
                Collections.singletonList(key), String.valueOf(delta));
    }
}
```

**2.8版本（2013年）** - 重要里程碑
- **分区容忍性**：支持Redis Sentinel
- **发布订阅优化**
- **位图操作**
- **HyperLogLog数据结构**

```java
// HyperLogLog使用示例
public class HyperLogLogExample {
    public void countUniqueUsers() {
        // 添加用户访问记录
        redisTemplate.opsForHyperLogLog().add("daily_users", "user1", "user2", "user3");
        
        // 估算独立用户数（内存消耗极小，准确率99%）
        Long uniqueCount = redisTemplate.opsForHyperLogLog().size("daily_users");
        System.out.println("今日独立用户数: " + uniqueCount);
    }
}
```

**3.0版本（2015年）** - 集群时代
- **Redis Cluster**：原生集群支持
- 16384个哈希槽
- 无中心架构
- 自动故障转移

```java
// Redis Cluster配置
@Configuration
public class RedisClusterConfig {
    @Bean
    public RedisConnectionFactory redisConnectionFactory() {
        RedisClusterConfiguration config = new RedisClusterConfiguration();
        config.clusterNode("127.0.0.1", 7000);
        config.clusterNode("127.0.0.1", 7001);
        config.clusterNode("127.0.0.1", 7002);
        
        return new LettuceConnectionFactory(config);
    }
}
```

**3.2版本（2016年）** - GEO地理位置
- **地理位置数据类型**
- GEO命令集合
- 位置查询和计算

```java
// GEO位置服务示例
public class GeoLocationService {
    public void addLocation(String key, String member, double longitude, double latitude) {
        redisTemplate.opsForGeo().add(key, new Point(longitude, latitude), member);
    }
    
    public List<String> findNearbyStores(double longitude, double latitude, double radius) {
        Circle circle = new Circle(new Point(longitude, latitude), new Distance(radius, Metrics.KILOMETERS));
        GeoResults<RedisGeoCommands.GeoLocation<String>> results = 
            redisTemplate.opsForGeo().radius("stores", circle);
        
        return results.getContent().stream()
            .map(result -> result.getContent().getName())
            .collect(Collectors.toList());
    }
}
```

**4.0版本（2017年）** - 模块化时代
- **模块系统**：支持动态加载模块
- **混合持久化**：RDB+AOF
- **PSYNC2.0**：部分重同步优化
- **非阻塞删除**：UNLINK命令
- **内存命令**：MEMORY命令

```java
// 混合持久化配置
public class RedisPersistenceConfig {
    // 在redis.conf中配置
    // aof-use-rdb-preamble yes  # 启用混合持久化
    
    public void configureHybridPersistence() {
        // RDB快照 + AOF增量日志
        // 恢复时先加载RDB，再重放AOF
        // 兼顾恢复速度和数据安全性
    }
}
```

**5.0版本（2018年）** - 流数据
- **Stream数据类型**：消息队列增强
- **消费者组**：类似Kafka的消费模型
- **HELP命令**：内置帮助系统
- **新的排序算法**
- **HyperLogLog优化**

```java
// Redis Stream消息队列
public class RedisStreamExample {
    public void produceMessage(String streamKey, Map<String, String> message) {
        MapRecord<String, Object, Object> record = MapRecord.create(streamKey, message);
        redisTemplate.opsForStream().add(record);
    }
    
    public void consumeMessages(String streamKey, String consumerGroup, String consumerName) {
        try {
            // 创建消费者组
            redisTemplate.opsForStream().createGroup(streamKey, consumerGroup, "0");
        } catch (Exception ignored) {
            // 消费者组已存在
        }
        
        // 消费消息
        List<MapRecord<String, Object, Object>> messages = redisTemplate.opsForStream()
            .read(Consumer.from(consumerGroup, consumerName),
                  StreamReadOptions.empty().count(10),
                  StreamOffset.create(streamKey, ReadOffset.lastConsumed()));
        
        for (MapRecord<String, Object, Object> message : messages) {
            System.out.println("消息ID: " + message.getId());
            System.out.println("消息内容: " + message.getValue());
            
            // 确认消息处理
            redisTemplate.opsForStream().acknowledge(streamKey, consumerGroup, message.getId());
        }
    }
}
```

**6.0版本（2020年）** - 多线程与权限
- **多线程I/O**：网络I/O多线程处理
- **客户端缓存**：服务端推送失效
- **ACL权限系统**：细粒度权限控制
- **RESP3协议**：新的通信协议
- **SSL支持**

```java
// ACL权限配置示例
public class RedisACLExample {
    // 在redis.conf或通过命令配置
    // ACL SETUSER alice >password ~cached:* +get +set
    // 用户alice只能访问cached:*的key，只能执行get和set命令
    
    public void configureSecurity() {
        // Java客户端连接时指定用户名密码
        RedisStandaloneConfiguration config = new RedisStandaloneConfiguration();
        config.setHostName("localhost");
        config.setPort(6379);
        config.setUsername("alice");
        config.setPassword("password");
    }
}
```

**6.2版本（2021年）** - 稳定增强
- **Lua调试器**
- **ACL改进**
- **支持TLS 1.3**
- **内存使用优化**

**7.0版本（2022年）** - 现代化架构
- **Redis Functions**：替代Lua脚本的新机制
- **ACL v2**：更强大的权限系统
- **命令自省**：运行时命令信息查询
- **Sharded发布订阅**
- **多部分AOF**：减少AOF重写成本

```java
// Redis Functions示例
public class RedisFunctionsExample {
    // 注册函数库
    public void registerFunction() {
        String functionCode = 
            "#!lua name=mylib\n" +
            "local function my_function(keys, args)\n" +
            "  return redis.call('GET', keys[1])\n" +
            "end\n" +
            "redis.register_function('my_function', my_function)";
        
        // 通过Redis命令加载函数
        // FUNCTION LOAD functionCode
    }
    
    public Object callFunction(String functionName, List<String> keys, Object... args) {
        // 调用注册的函数
        return redisTemplate.execute(connection -> {
            return connection.eval("return redis.call('FCALL', '" + functionName + "', 1, '" + keys.get(0) + "')", 
                                 ReturnType.VALUE, 0);
        });
    }
}
```

**7.2版本（2023年）** - 最新稳定版
- **性能优化**：更快的命令处理
- **内存优化**：更高效的内存使用
- **监控增强**：更详细的指标
- **Bug修复**：稳定性提升

### 版本选择建议

**生产环境推荐版本：**

1. **Redis 6.2.x**（当前主流）
   - 稳定性好，社区支持充分
   - 支持ACL、多线程I/O
   - 大多数云服务商支持

2. **Redis 7.0.x**（现代化选择）
   - 最新特性和性能优化
   - 适合新项目
   - Functions替代Lua脚本

3. **避免的版本：**
   - Redis 6.0.0-6.0.9（早期版本bug较多）
   - Redis 5.x以下（缺少重要特性）

```java
// 版本兼容性检查
public class RedisVersionCheck {
    public void checkRedisVersion() {
        Properties info = redisTemplate.execute(connection -> {
            return connection.info("server");
        });
        
        String version = info.getProperty("redis_version");
        System.out.println("Redis版本: " + version);
        
        // 根据版本启用不同特性
        if (version.startsWith("7.")) {
            // 使用Redis Functions
            System.out.println("支持Redis Functions");
        } else if (version.startsWith("6.")) {
            // 使用ACL和多线程I/O
            System.out.println("支持ACL和多线程I/O");
        } else if (version.startsWith("5.")) {
            // 使用Stream
            System.out.println("支持Stream数据类型");
        }
    }
}
```

### 升级最佳实践

```java
// Redis升级策略
public class RedisUpgradeStrategy {
    
    // 1. 小版本升级（如6.2.6 -> 6.2.7）
    public void minorUpgrade() {
        // 直接升级，通常向下兼容
        // 建议在测试环境先验证
    }
    
    // 2. 大版本升级（如5.x -> 6.x）
    public void majorUpgrade() {
        // 步骤：
        // 1. 测试环境验证兼容性
        // 2. 主从切换升级
        // 3. 渐进式灰度发布
        // 4. 监控关键指标
    }
    
    // 3. 跨大版本升级（如4.x -> 6.x）
    public void crossMajorUpgrade() {
        // 建议逐步升级：4.x -> 5.x -> 6.x
        // 每个版本充分测试后再升级下一版本
    }
}
```

## 6.2 数据结构

**Q: Redis支持哪些数据结构？各自的应用场景是什么？**

### 五种基本数据结构

**1. String（字符串）**
- **应用场景**：缓存、计数器、分布式锁、session存储
- **关键操作**：SET、GET、INCR、DECR、SETNX

```java
// 分布式锁实现
public boolean tryLock(String lockKey, String lockValue, int expireSeconds) {
    Boolean result = redisTemplate.opsForValue()
        .setIfAbsent(lockKey, lockValue, expireSeconds, TimeUnit.SECONDS);
    return Boolean.TRUE.equals(result);
}
```

**2. Hash（哈希表）**
- **应用场景**：用户信息存储、购物车、对象缓存
- **优势**：节省内存，适合存储结构化数据

**3. List（列表）**
- **应用场景**：消息队列、最近访问记录、分页数据
- **特点**：有序、可重复、支持两端操作

**4. Set（集合）**
- **应用场景**：去重、共同好友、标签系统、随机抽奖
- **特点**：无序、不重复、支持集合运算

**5. Sorted Set（有序集合）**
- **应用场景**：排行榜、延迟队列、热门搜索
- **特点**：有序、不重复、支持范围查询

## 6.3 持久化机制

**Q: Redis的RDB和AOF持久化机制有什么区别？**

| 特性 | RDB | AOF |
|------|-----|-----|
| 持久化方式 | 快照 | 日志 |
| 文件大小 | 小 | 大 |
| 恢复速度 | 快 | 慢 |
| 数据安全性 | 可能丢失数据 | 更安全 |
| 性能影响 | 小 | 较大 |

**混合持久化**：Redis 4.0+支持RDB+AOF混合模式，兼具两者优点。

## 6.4 集群与高可用

**Q: Redis哨兵模式和集群模式的区别？**

### 哨兵模式（Sentinel）
```java
@Configuration
public class RedisSentinelConfig {
    @Bean
    public RedisSentinelConfiguration sentinelConfiguration() {
        return new RedisSentinelConfiguration()
            .master("mymaster")
            .sentinel("127.0.0.1", 26379)
            .sentinel("127.0.0.1", 26380);
    }
}
```

**特点**：
- 自动故障转移
- 读写分离
- 数据不分片

### 集群模式（Cluster）
**特点**：
- 数据分片存储
- 高可用+高性能
- 16384个哈希槽

### Redis脑裂现象详解

**Q: 什么是Redis脑裂现象？如何产生的？如何解决？**

#### 脑裂现象概述

**脑裂（Split-Brain）**是指在主从架构的分布式系统中，由于网络分区导致出现多个节点都认为自己是主节点的情况，从而造成数据不一致。

**简单理解**：
```
网络问题 → 多个主节点 → 数据不一致
```

**脑裂三步骤**：
1. **网络分区**：Master与Sentinel之间网络中断
2. **误判故障**：Sentinel认为Master挂了，提升Slave为新Master  
3. **双主并存**：原Master还活着 + 新Master = 两个主节点同时工作

```java
// 脑裂核心问题演示
public class SplitBrainCoreIssue {
    
    public void explainSplitBrain() {
        /*
         * 正常状态：
         * Master(写) ← Slave1(读) ← Slave2(读)
         * ↑
         * Sentinel监控
         * 
         * 网络分区后：
         * 
         * 分区A: Master(继续工作) ← Client1写入数据A
         * 
         * 分区B: NewMaster(Slave1提升) ← Client2写入数据B
         *         ↑
         *         Sentinel(误以为原Master死了)
         * 
         * 结果：两个Master，数据A和数据B不一致！
         */
        
        System.out.println("脑裂核心问题：");
        System.out.println("1. 网络故障 → Sentinel与Master失联");
        System.out.println("2. 误判故障 → Sentinel提升Slave为新Master");
        System.out.println("3. 双主并存 → 原Master + 新Master = 数据冲突");
        System.out.println("4. 数据不一致 → 同一个key可能有不同的值");
    }
}
```

```java
// 脑裂场景演示
public class RedisSplitBrainDemo {
    
    /**
     * 脑裂发生的典型场景
     */
    public void demonstrateSplitBrainScenario() {
        /*
         * 初始状态：
         * Master(M) <- Slave1(S1) <- Slave2(S2)
         * Sentinel1, Sentinel2, Sentinel3 监控集群
         * 
         * 网络分区发生：
         * 分区A: Master(M) + Client1
         * 分区B: Slave1(S1) + Slave2(S2) + Sentinel1 + Sentinel2 + Sentinel3 + Client2
         * 
         * 问题：
         * 1. Sentinel认为Master挂了，将S1提升为新Master
         * 2. 但原Master(M)还在运行，仍然接受Client1的写入
         * 3. 现在有两个Master：M 和 S1，产生脑裂
         */
        
        System.out.println("脑裂场景分析：");
        System.out.println("1. 网络分区导致Master与Sentinel失联");
        System.out.println("2. Sentinel错误地认为Master已死，触发故障转移");
        System.out.println("3. 出现两个Master同时服务，数据不一致");
    }
    
    /**
     * 脑裂导致的数据问题
     */
    public void demonstrateDataInconsistency() {
        /*
         * 脑裂期间的写入操作：
         * 
         * 在原Master(M)上：
         * SET user:1001 "Alice_v1"  // Client1写入
         * SET user:1002 "Bob_v1"    // Client1写入
         * 
         * 在新Master(S1)上：
         * SET user:1001 "Alice_v2"  // Client2写入
         * SET user:1003 "Charlie"   // Client2写入
         * 
         * 网络恢复后的数据冲突：
         * - user:1001 有两个不同的值
         * - user:1002 只在原Master上存在
         * - user:1003 只在新Master上存在
         */
        
        System.out.println("数据不一致问题：");
        System.out.println("1. 同一key存在不同值");
        System.out.println("2. 部分数据只在一个Master上存在");
        System.out.println("3. 网络恢复后数据合并复杂");
    }
}
```

#### 脑裂产生的根本原因

```java
// 脑裂产生原因分析
public class SplitBrainCauses {
    
    /**
     * 1. 网络分区（最常见原因）
     */
    public void networkPartitionCause() {
        /*
         * 网络分区场景：
         * - 交换机故障
         * - 网络拥塞
         * - 防火墙规则变更
         * - 机房间网络中断
         * 
         * 导致：
         * - Master与Sentinel失联
         * - Sentinel无法正常心跳检测
         * - 误判Master已死
         */
    }
    
    /**
     * 2. 心跳检测超时设置不当
     */
    public void heartbeatTimeoutIssue() {
        /*
         * 超时设置过短的问题：
         * - down-after-milliseconds 设置过小
         * - 网络抖动就触发故障转移
         * - 增加脑裂风险
         * 
         * 超时设置过长的问题：
         * - 真正故障时恢复时间过长
         * - 影响可用性
         * 
         * 建议值：30000ms (30秒)
         */
    }
    
    /**
     * 3. Sentinel配置不当
     */
    public void sentinelConfigIssue() {
        /*
         * 常见配置问题：
         * - Sentinel数量为偶数（应该是奇数）
         * - quorum设置不合理
         * - Sentinel部署在同一网络分区
         * - 缺少failover-timeout配置
         */
    }
}
```

#### 脑裂解决方案

**方案1：min-slaves配置**

```java
// Redis主从配置防脑裂
public class PreventSplitBrainConfig {
    
    /**
     * 通过min-slaves配置防止脑裂
     */
    public void configureMinSlaves() {
        /*
         * 在redis.conf中配置：
         * min-slaves-to-write 1          # 至少需要1个slave连接
         * min-slaves-max-lag 10          # slave延迟不超过10秒
         * 
         * 工作原理：
         * - Master检查连接的slave数量和延迟
         * - 如果条件不满足，拒绝写操作
         * - 网络分区时，孤立的Master会拒绝写入
         * - 避免脑裂期间的数据丢失
         */
        
        System.out.println("min-slaves配置防脑裂：");
        System.out.println("1. Master需要至少1个Slave连接");
        System.out.println("2. Slave延迟不能超过设定值");
        System.out.println("3. 条件不满足时拒绝写操作");
    }
    
    /**
     * Spring Boot中的配置示例
     */
    @Configuration
    public static class RedisSentinelConfig {
        
        @Bean
        public RedisSentinelConfiguration sentinelConfiguration() {
            RedisSentinelConfiguration config = new RedisSentinelConfiguration()
                .master("mymaster")
                .sentinel("192.168.1.10", 26379)
                .sentinel("192.168.1.11", 26379)
                .sentinel("192.168.1.12", 26379);  // 奇数个Sentinel
            
            return config;
        }
        
        @Bean
        public LettuceConnectionFactory redisConnectionFactory() {
            return new LettuceConnectionFactory(sentinelConfiguration());
        }
    }
}
```

**方案2：Redlock算法（分布式锁场景）**

#### Redlock算法详解

**Q: 什么是Redlock？为什么需要Redlock？**

**Redlock核心概念**：
Redlock是Redis官方提出的分布式锁算法，通过在多个独立的Redis实例上获取锁来解决单点故障和脑裂问题。

**为什么需要Redlock？**
```java
// 传统单Redis锁的问题
public class SingleRedisLockProblem {
    
    public void demonstrateProblems() {
        /*
         * 传统单Redis分布式锁的问题：
         * 
         * 1. 单点故障：
         *    - Redis实例挂掉 → 所有锁都失效
         *    - 无法获取新锁，已获取的锁无法释放
         * 
         * 2. 脑裂问题：
         *    - 网络分区导致多个Master
         *    - 同一把锁可能被多个客户端获取
         * 
         * 3. 时钟漂移：
         *    - Redis服务器时钟不准
         *    - 锁过期时间不可靠
         * 
         * 示例场景：
         * Client1在Master1上获取锁 "order:123" 
         * 发生脑裂，出现Master2
         * Client2在Master2上也获取了锁 "order:123"
         * 结果：两个客户端都认为自己拥有锁！
         */
        
        System.out.println("单Redis锁的问题：");
        System.out.println("1. 单点故障 - Redis挂了锁就没了");
        System.out.println("2. 脑裂风险 - 多个Master可能导致重复加锁");
        System.out.println("3. 时钟依赖 - 依赖Redis服务器时钟准确性");
    }
}
```

**Redlock解决方案**：
``java
// Redlock算法原理
public class RedlockPrinciple {
    
    public void explainRedlock() {
        /*
         * Redlock算法核心思想：
         * 
         * 1. 多实例部署：
         *    - 部署N个完全独立的Redis实例（通常N=5）
         *    - 实例之间没有主从关系，完全独立
         *    - 分布在不同的机器/数据中心
         * 
         * 2. 过半数原则：
         *    - 必须在大多数实例（N/2+1）上成功获取锁
         *    - 5个实例需要在至少3个上获取成功
         *    - 即使2个实例故障，仍然可以正常工作
         * 
         * 3. 时间限制：
         *    - 获取锁的总时间不能超过锁的过期时间
         *    - 考虑网络延迟和时钟漂移
         *    - 确保锁的有效性
         * 
         * 4. 原子释放：
         *    - 使用Lua脚本确保释放操作的原子性
         *    - 只能释放自己加的锁
         */
        
        System.out.println("Redlock算法特点：");
        System.out.println("1. 多实例 - 5个独立Redis，无主从关系");
        System.out.println("2. 过半数 - 必须在3个以上实例获取成功");
        System.out.println("3. 时间窗口 - 考虑网络延迟和时钟漂移");
        System.out.println("4. 容错性 - 最多允许2个实例故障");
    }
}
```

**Redlock核心机制总结**：
``java
// Redlock两大核心机制
public class RedlockCoreMechanisms {
    
    /**
     * 机制1：投票半数过半 - 解决脑裂问题
     */
    public void votingMechanism() {
        /*
         * 问题：脑裂导致多Master，同一把锁被多次获取
         * 解决：投票机制 - 必须在大多数Redis实例上获取成功
         * 
         * 具体做法：
         * - 部署N个完全独立的Redis实例（通常N=5）
         * - 必须在 N/2+1 个实例上获取锁才算成功
         * - 5个实例需要在至少3个上成功
         * 
         * 为什么能防止脑裂？
         * - 即使发生网络分区，最多只有一方能获得大多数
         * - 例如：分区成 2:3，只有拥有3个实例的一方能获取锁
         */
        
        System.out.println("投票机制防脑裂：");
        System.out.println("问题：脑裂 → 多Master → 重复加锁");
        System.out.println("解决：投票 → 过半数 → 互斥性保证");
        System.out.println("具体：5个独立Redis，必须在3个以上获取成功");
        System.out.println("原理：网络分区时，最多只有一方能获得大多数");
    }
    
    /**
     * 机制2：时间容忍 - 解决时钟漂移问题
     */
    public void timeToleranceMechanism() {
        /*
         * 问题：时钟漂移导致锁过期时间不准确
         * 解决：时间容忍 - 计算有效时间窗口
         * 
         * 具体做法：
         * - 记录获取锁的开始时间
         * - 计算获取锁消耗的时间
         * - 检查有效时间 = 锁TTL - 获取耗时 - 容忍时间
         * - 只有在有效时间 > 0 时才认为获取成功
         * 
         * 容忍时间包括：
         * - 网络延迟（通常100ms）
         * - 时钟漂移（通常几十ms）
         * - Redis实例间的时间差异
         */
        
        System.out.println("时间容忍防时钟漂移：");
        System.out.println("问题：时钟漂移 → 过期时间不准 → 锁失效");
        System.out.println("解决：时间容忍 → 有效窗口 → 安全边界");
        System.out.println("具体：有效时间 = TTL - 获取耗时 - 容忍值");
        System.out.println("原理：留出安全边界应对网络延迟和时钟问题");
    }
    
    /**
     * 两大机制综合示例
     */
    public void combinedExample() {
        /*
         * 假设场景：
         * - 5个Redis实例：R1, R2, R3, R4, R5
         * - 锁过期时间：10秒
         * - 容忍时间：100ms
         * 
         * 正常情况：
         * - 在R1, R2, R3上获取成功（满足过半数）
         * - 总耗时200ms，有效时间 = 10000 - 200 - 100 = 9700ms > 0
         * - 锁获取成功！
         * 
         * 脑裂情况：
         * - 分区1：R1, R2 （只有2个，不过半）
         * - 分区2：R3, R4, R5（有3个，过半数）
         * - 只有分区2的客户端能获取锁！
         * 
         * 时钟漂移情况：
         * - 由于网络延迟，总耗时达刐9900ms
         * - 有效时间 = 10000 - 9900 - 100 = 0ms
         * - 不满足有效时间要求，获取失败！
         */
        
        System.out.println("综合机制实例：");
        System.out.println("正常：3/5获取成功 + 有效时间>0 = 锁成功");
        System.out.println("脑裂：只有2/5获取成功 = 锁失败（防脑裂）");
        System.out.println("漂移：耗时过长有效时间≤ 0 = 锁失败（防漂移）");
    }
}
```

**核心公式**：
``java
// Redlock核心公式
public class RedlockFormulas {
    
    /**
     * 核心公式1：防脑裂公式
     */
    public boolean preventSplitBrain(int successCount, int totalInstances) {
        // 投票过半数原则
        return successCount > totalInstances / 2;
        
        /*
         * 解释：
         * - 必须获得超过一半的投票
         * - 5个实例需要至少3个成功
         * - 保证一个时刻最多只有一个客户端能获得大多数
         */
    }
    
    /**
     * 核心公式2：防时钟漂移公式
     */
    public boolean preventClockDrift(long lockTTL, long elapsedTime, long toleranceTime) {
        // 时间容忍公式
        long validityTime = lockTTL - elapsedTime - toleranceTime;
        return validityTime > 0;
        
        /*
         * 解释：
         * - lockTTL: 锁的过期时间
         * - elapsedTime: 获取锁实际消耗的时间
         * - toleranceTime: 网络延迟和时钟漂移的容忍时间
         * - validityTime: 锁的实际有效时间
         */
    }
    
    /**
     * 综合判断：Redlock获取成功的条件
     */
    public boolean redlockSuccess(int successCount, int totalInstances, 
                                 long lockTTL, long elapsedTime, long toleranceTime) {
        // 同时满足两个条件
        return preventSplitBrain(successCount, totalInstances) && 
               preventClockDrift(lockTTL, elapsedTime, toleranceTime);
    }
    }
}
```

**Redlock算法步骤**：
``java
// Redlock算法详细步骤
public class RedlockSteps {
    
    public void redlockAlgorithmSteps() {
        /*
         * Redlock算法执行步骤：
         * 
         * 获取锁的步骤：
         * 1. 记录开始时间
         * 2. 依次在所有Redis实例上尝试获取锁
         *    - 使用相同的key和随机value
         *    - 设置较短的超时时间（相比锁的过期时间）
         * 3. 计算获取锁消耗的时间
         * 4. 检查是否满足条件：
         *    - 在大多数实例上获取成功
         *    - 总耗时 < 锁过期时间
         * 5. 如果满足条件，锁获取成功
         * 6. 如果不满足，释放所有已获取的锁
         * 
         * 释放锁的步骤：
         * 1. 在所有Redis实例上释放锁
         * 2. 不管之前是否获取成功
         * 3. 使用Lua脚本确保原子性
         */
    }
}
```

**Redlock vs 传统锁对比**：

| 特性 | 传统单Redis锁 | Redlock算法 |
|------|---------------|-------------|
| 可用性 | 单点故障风险 | 高可用，容忍部分实例故障 |
| 安全性 | 脑裂风险 | 过半数机制保证安全性 |
| 性能 | 高（单次操作） | 较低（需要多次操作） |
| 复杂度 | 简单 | 复杂，需要多实例管理 |
| 成本 | 低 | 高（需要多个Redis实例） |
| 适用场景 | 一般业务 | 关键业务，高可靠性要求 |

**什么时候使用Redlock？**
```java
// Redlock使用场景判断
public class RedlockUseCases {
    
    // ✅ 适合使用Redlock的场景
    public void suitableScenarios() {
        System.out.println("适合使用Redlock的场景：");
        System2.out.println("1. 金融交易 - 防止重复扣款");
        System.out.println("2. 库存扣减 - 防止超卖");
        System.out.println("3. 订单处理 - 防止重复创建订单");
        System.out.println("4. 定时任务 - 防止多实例重复执行");
        System.out.println("5. 数据同步 - 确保只有一个进程在同步");
    }
    
    // ❌ 不适合使用Redlock的场景
    public void unsuitableScenarios() {
        System.out.println("不适合使用Redlock的场景：");
        System.out.println("1. 高频操作 - 性能要求极高的场景");
        System.out.println("2. 非关键业务 - 偶尔重复执行可以接受");
        System.out.println("3. 资源受限 - 无法部署多个Redis实例");
        System.out.println("4. 简单缓存 - 普通的缓存更新操作");
    }
}
```

```java
// Redlock算法解决分布式锁脑裂
public class RedlockSolution {
    
    private List<StringRedisTemplate> redisTemplates;
    private final int quorum;
    
    public RedlockSolution(List<StringRedisTemplate> redisTemplates) {
        this.redisTemplates = redisTemplates;
        this.quorum = redisTemplates.size() / 2 + 1;  // 过半数
    }
    
    /**
     * Redlock算法获取分布式锁
     */
    public boolean acquireRedlock(String lockKey, String lockValue, Duration expireTime) {
        long startTime = System.currentTimeMillis();
        int successCount = 0;
        
        // 1. 在多个独立的Redis实例上获取锁
        for (StringRedisTemplate template : redisTemplates) {
            try {
                Boolean success = template.opsForValue()
                    .setIfAbsent(lockKey, lockValue, expireTime);
                if (Boolean.TRUE.equals(success)) {
                    successCount++;
                }
            } catch (Exception e) {
                log.warn("在Redis实例上获取锁失败", e);
            }
        }
        
        // 2. 检查是否获得了大多数实例的锁
        long elapsedTime = System.currentTimeMillis() - startTime;
        long validityTime = expireTime.toMillis() - elapsedTime - 100; // 时钟漂移容忍
        
        if (successCount >= quorum && validityTime > 0) {
            log.info("Redlock获取成功，成功实例数: {}/{}", successCount, redisTemplates.size());
            return true;
        } else {
            // 如果没有获得足够的锁，释放已获得的锁
            releaseRedlock(lockKey, lockValue);
            log.warn("Redlock获取失败，成功实例数: {}/{}", successCount, redisTemplates.size());
            return false;
        }
    }
    
    /**
     * 释放Redlock
     */
    public void releaseRedlock(String lockKey, String lockValue) {
        String script = 
            "if redis.call('GET', KEYS[1]) == ARGV[1] then " +
            "    return redis.call('DEL', KEYS[1]) " +
            "else " +
            "    return 0 " +
            "end";
        
        RedisScript<Long> redisScript = new DefaultRedisScript<>(script, Long.class);
        
        // 在所有实例上释放锁
        for (StringRedisTemplate template : redisTemplates) {
            try {
                template.execute(redisScript, Collections.singletonList(lockKey), lockValue);
            } catch (Exception e) {
                log.warn("释放Redlock失败", e);
            }
        }
    }
}
```

**方案3：Sentinel优化配置**

```java
// 优化Sentinel配置防止脑裂
public class OptimizedSentinelConfig {
    
    /**
     * Sentinel最佳配置实践
     */
    public void optimizeSentinelConfig() {
        /*
         * sentinel.conf 关键配置：
         * 
         * # 1. 主观下线时间（建议30秒）
         * sentinel down-after-milliseconds mymaster 30000
         * 
         * # 2. 故障转移超时时间
         * sentinel failover-timeout mymaster 180000
         * 
         * # 3. 并行同步slave数量
         * sentinel parallel-syncs mymaster 1
         * 
         * # 4. quorum设置（建议为sentinel数量的一半+1）
         * sentinel monitor mymaster 192.168.1.10 6379 2
         * 
         * # 5. 认证配置
         * sentinel auth-pass mymaster yourpassword
         */
    }
    
    /**
     * Sentinel部署最佳实践
     */
    public void sentinelDeploymentBestPractices() {
        System.out.println("Sentinel部署最佳实践：");
        System.out.println("1. 至少3个Sentinel，部署在不同机器/网络分区");
        System.out.println("2. Sentinel数量必须是奇数");
        System.out.println("3. quorum设置为(sentinel数量/2)+1");
        System.out.println("4. 合理设置超时时间，避免网络抖动误判");
        System.out.println("5. 监控Sentinel日志，及时发现网络问题");
    }
}
```

**方案4：监控和告警**

```java
// 脑裂监控和告警
@Component
public class SplitBrainMonitor {
    
    private final StringRedisTemplate redisTemplate;
    private final List<StringRedisTemplate> allRedisTemplates;
    
    /**
     * 监控是否发生脑裂
     */
    @Scheduled(fixedRate = 30000)  // 每30秒检查一次
    public void monitorSplitBrain() {
        try {
            // 1. 检查Master数量
            int masterCount = countMasters();
            if (masterCount > 1) {
                log.error("检测到脑裂！当前Master数量: {}", masterCount);
                sendSplitBrainAlert(masterCount);
            }
            
            // 2. 检查数据一致性
            boolean consistent = checkDataConsistency();
            if (!consistent) {
                log.warn("检测到数据不一致，可能存在脑裂");
            }
            
            // 3. 检查网络连通性
            checkNetworkConnectivity();
            
        } catch (Exception e) {
            log.error("脑裂监控异常", e);
        }
    }
    
    /**
     * 统计Master数量
     */
    private int countMasters() {
        int masterCount = 0;
        for (StringRedisTemplate template : allRedisTemplates) {
            try {
                String info = template.execute(connection -> {
                    return connection.info("replication");
                }).getProperty("role");
                
                if ("master".equals(info)) {
                    masterCount++;
                }
            } catch (Exception e) {
                log.warn("检查Redis实例角色失败", e);
            }
        }
        return masterCount;
    }
    
    /**
     * 检查数据一致性
     */
    private boolean checkDataConsistency() {
        String testKey = "consistency_check:" + System.currentTimeMillis();
        String testValue = UUID.randomUUID().toString();
        
        try {
            // 在主Master上写入测试数据
            redisTemplate.opsForValue().set(testKey, testValue, 10, TimeUnit.SECONDS);
            Thread.sleep(1000);  // 等待复制
            
            // 检查所有实例是否都有相同的数据
            for (StringRedisTemplate template : allRedisTemplates) {
                String value = template.opsForValue().get(testKey);
                if (!testValue.equals(value)) {
                    return false;
                }
            }
            
            return true;
        } catch (Exception e) {
            log.warn("数据一致性检查失败", e);
            return false;
        } finally {
            // 清理测试数据
            try {
                redisTemplate.delete(testKey);
            } catch (Exception ignored) {}
        }
    }
    
    /**
     * 发送脑裂告警
     */
    private void sendSplitBrainAlert(int masterCount) {
        // 实现告警逻辑：邮件、短信、钉钉等
        log.error("!!!!! Redis脑裂告警 !!!!!");
        log.error("当前检测到{}个Master节点", masterCount);
        log.error("请立即检查网络连接和Redis集群状态");
        
        // 可以集成告警系统
        // alertService.sendAlert("Redis Split-Brain Detected", details);
    }
    
    /**
     * 检查网络连通性
     */
    private void checkNetworkConnectivity() {
        // 检查各Redis实例间的网络连通性
        // ping测试、延迟检测等
    }
}
```

#### 脑裂预防最佳实践总结

```java
// 脑裂预防总结
public class SplitBrainPreventionSummary {
    
    /**
     * 架构层面预防
     */
    public void architecturePrevention() {
        System.out.println("架构层面预防措施：");
        System.out.println("1. 使用奇数个Sentinel，部署在不同网络分区");
        System.out.println("2. 合理设置quorum值（过半数）");
        System.out.println("3. 配置min-slaves-to-write防止孤立Master写入");
        System.out.println("4. 考虑使用Redis Cluster代替主从+Sentinel");
    }
    
    /**
     * 配置层面预防
     */
    public void configurationPrevention() {
        System.out.println("配置层面预防措施：");
        System.out.println("1. 适当增加down-after-milliseconds（建议30秒）");
        System.out.println("2. 设置failover-timeout避免频繁故障转移");
        System.out.println("3. 限制parallel-syncs避免大量同步影响性能");
        System.out.println("4. 启用持久化确保数据安全");
    }
    
    /**
     * 运维层面预防
     */
    public void operationPrevention() {
        System.out.println("运维层面预防措施：");
        System.out.println("1. 建立完善的监控告警机制");
        System.out.println("2. 定期检查网络连通性和延迟");
        System.out.println("3. 制定脑裂处理应急预案");
        System.out.println("4. 定期演练故障恢复流程");
    }
    
    /**
     * 应用层面预防
     */
    public void applicationPrevention() {
        System.out.println("应用层面预防措施：");
        System.out.println("1. 关键操作使用Redlock算法");
        System.out.println("2. 实现业务层数据一致性检查");
        System.out.println("3. 设计幂等操作应对数据重复");
        System.out.println("4. 重要数据多重备份和校验");
    }
}
```

**关键要点**：
1. **脑裂本质**：网络分区导致的多Master问题
2. **主要危害**：数据不一致、业务逻辑错误
3. **预防核心**：合理配置+监控告警+应急预案
4. **最佳方案**：Redlock算法（分布式锁）+ min-slaves配置（数据一致性）

## 6.5 性能优化

**Q: Redis性能优化的常见手段有哪些？**

### 1. 内存优化
```java
// 使用合适的数据结构
public void optimizeMemory() {
    // 小对象使用hash而不是string
    redisTemplate.opsForHash().put("user:1", "name", "张三");
    redisTemplate.opsForHash().put("user:1", "age", "25");
    
    // 设置过期时间避免内存泄漏
    redisTemplate.expire("user:1", 1, TimeUnit.HOURS);
}
```

### 2. 命令优化
- **避免大key**：单个key过大影响性能
- **批量操作**：使用pipeline、mget/mset
- **避免耗时命令**：keys *、flushall等

### 3. 网络优化
```java
// 使用pipeline批量操作
public void batchOperations(List<String> keys) {
    redisTemplate.executePipelined(new RedisCallback<Object>() {
        @Override
        public Object doInRedis(RedisConnection connection) {
            for (String key : keys) {
                connection.get(key.getBytes());
            }
            return null;
        }
    });
}
```

### 4. 缓存策略
- **缓存穿透**：布隆过滤器、空值缓存
- **缓存击穿**：互斥锁、热点数据永不过期
- **缓存雪崩**：随机过期时间、限流降级

```java
@Service
public class CacheService {
    
    // 防止缓存穿透
    public Object getWithBloomFilter(String key) {
        if (!bloomFilter.mightContain(key)) {
            return null; // 肯定不存在
        }
        
        Object value = redisTemplate.opsForValue().get(key);
        if (value == null) {
            // 查询数据库
            value = queryFromDB(key);
            if (value != null) {
                redisTemplate.opsForValue().set(key, value, getRandomTTL());
            }
        }
        return value;
    }
    
    // 防止缓存雪崩 - 随机TTL
    private int getRandomTTL() {
        return 3600 + new Random().nextInt(600); // 1小时 + 0-10分钟随机
    }
}
```

**Q: Redis的内存淘汰策略有哪些？惰性删除和定期删除的区别是什么？**

### Redis内存处理机制概述

Redis采用三种机制来处理内存和过期键：**惰性删除（Lazy Deletion）**、**定期删除（Periodic Deletion）**和**内存淘汰（Memory Eviction）**。

### 惰性删除（Lazy Deletion）

**触发时机**：访问键时检查是否过期
**执行方式**：客户端读取键时，如果发现键已过期则立即删除
**特点**：按需删除，CPU友好但可能占用内存

```java
// 惰性删除演示
public class LazyDeletionDemo {
    
    public void demonstrateLazyDeletion() {
        // 设置一个很短过期时间的键
        redisTemplate.opsForValue().set("temp_key", "temp_value", 1, TimeUnit.SECONDS);
        
        try {
            // 等待键过期
            Thread.sleep(2000);
            
            // 尝试访问过期的键
            String value = redisTemplate.opsForValue().get("temp_key");
            
            if (value == null) {
                System.out.println("键已被惰性删除（访问时发现过期）");
            }
            
            // 惰性删除的特点：
            // 1. 只有在访问时才会检查和删除过期键
            // 2. 如果过期键从未被访问，可能会一直占用内存
            // 3. CPU开销小，只在访问时检查
            
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
    
    // 演示惰性删除的内存占用问题
    public void demonstrateMemoryIssue() {
        // 创建大量短期键但不访问它们
        for (int i = 0; i < 10000; i++) {
            redisTemplate.opsForValue().set("unused_key_" + i, "data", 1, TimeUnit.SECONDS);
        }
        
        // 这些键过期后如果不被访问，仍会占用内存
        // 直到定期删除或内存淘汰机制介入
        System.out.println("创建了大量短期键，但不访问它们");
        System.out.println("仅靠惰性删除无法及时清理，需要定期删除配合");
    }
}
```

### 定期删除（Periodic Deletion）

**触发时机**：定期执行（默认每100ms执行一次）
**执行方式**：随机采样检查过期键并删除
**特点**：主动清理，平衡CPU和内存使用

```java
// 定期删除配置和监控
public class PeriodicDeletionDemo {
    
    public void configurePeriodicDeletion() {
        // 定期删除相关配置（在redis.conf中设置）:
        // hz 10  # 定期删除频率，默认10（每秒10次，即每100ms一次）
        // 
        // 定期删除算法:
        // 1. 随机选择20个设置了过期时间的键
        // 2. 删除其中已过期的键
        // 3. 如果过期键比例超过25%，重复步骤1-2
        // 4. 每次执行时间不超过25ms
    }
    
    public void monitorPeriodicDeletion() {
        Properties info = redisTemplate.execute(connection -> {
            return connection.info("stats");
        });
        
        String expiredKeys = info.getProperty("expired_keys");
        String hz = redisTemplate.execute(connection -> {
            return connection.info("server");
        }).getProperty("hz");
        
        System.out.println("定期删除频率: " + hz + "次/秒");
        System.out.println("已删除过期键数量: " + expiredKeys);
        
        // 定期删除的优势:
        // 1. 主动清理过期键，避免内存堆积
        // 2. 采样机制控制CPU开销
        // 3. 时间限制避免长时间阻塞
    }
    
    // 演示定期删除的采样机制
    public void demonstrateSampling() {
        // 创建大量带过期时间的键
        for (int i = 0; i < 1000; i++) {
            redisTemplate.opsForValue().set("periodic_key_" + i, "data", 5, TimeUnit.SECONDS);
        }
        
        System.out.println("创建了1000个5秒过期的键");
        System.out.println("定期删除会在后台随机采样清理过期键");
        System.out.println("不需要客户端访问，系统会主动清理");
        
        // 等待一段时间观察定期删除效果
        try {
            Thread.sleep(6000);
            
            // 检查还剩多少键
            Set<String> remainingKeys = redisTemplate.keys("periodic_key_*");
            System.out.println("6秒后剩余键数量: " + remainingKeys.size());
            System.out.println("大部分过期键已被定期删除清理");
            
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}
```

### 内存淘汰（Memory Eviction）

**触发时机**：内存使用达到`maxmemory`限制时
**执行方式**：根据配置的淘汰策略删除键（包括未过期的键）
**特点**：强制释放内存，保证Redis正常运行

```java
// 内存淘汰机制演示
public class MemoryEvictionDemo {
    
    public void demonstrateEvictionTrigger() {
        // 当内存达到maxmemory限制时触发
        // 与惰性删除和定期删除的区别：
        // - 惰性删除：只删除过期键，且在访问时删除
        // - 定期删除：只删除过期键，且定期删除
        // - 内存淘汰：可删除任意键（包括未过期的），在内存不足时删除
        
        try {
            // 这个SET操作可能触发内存淘汰
            redisTemplate.opsForValue().set("new_key", "value");
            System.out.println("写入成功，可能触发了内存淘汰");
        } catch (Exception e) {
            if (e.getMessage().contains("OOM")) {
                System.out.println("内存不足，可能是noeviction策略");
            }
        }
    }
    
    // 监控内存使用情况
    public void monitorMemoryUsage() {
        Properties info = redisTemplate.execute(connection -> {
            return connection.info("memory");
        });
        
        String usedMemory = info.getProperty("used_memory_human");
        String maxMemory = info.getProperty("maxmemory_human");
        String evictedKeys = info.getProperty("evicted_keys");
        
        System.out.println("已用内存: " + usedMemory);
        System.out.println("最大内存: " + maxMemory);
        System.out.println("已淘汰键数: " + evictedKeys);
    }
}

#### 8种内存淘汰策略详解

**1. noeviction（默认）**
```java
// 配置: maxmemory-policy noeviction
public class NoEvictionStrategy {
    // 特点：内存满时拒绝写操作，返回错误
    // 适用场景：数据库场景，不能丢失数据
    
    public void handleNoEviction() {
        try {
            redisTemplate.opsForValue().set("key", "value");
        } catch (Exception e) {
            // 内存不足时会抛出异常
            log.error("Redis内存不足: {}", e.getMessage());
            // 可以触发告警，手动清理或扩容
        }
    }
}
```

**2. allkeys-lru（推荐：缓存场景）**
```java
// 配置: maxmemory-policy allkeys-lru
public class AllKeysLRUStrategy {
    // 特点：从所有键中淘汰最近最少使用的
    // 适用场景：纯缓存，所有数据都可以重新获取
    
    public void optimizeForLRU() {
        // 频繁访问的数据会保留
        for (int i = 0; i < 100; i++) {
            redisTemplate.opsForValue().get("hot_data:" + (i % 10)); // 热点数据
        }
        
        // 很少访问的数据容易被淘汰
        redisTemplate.opsForValue().set("cold_data:123", "rarely_used");
    }
}
```

**3. volatile-lru**
```java
// 配置: maxmemory-policy volatile-lru
public class VolatileLRUStrategy {
    // 特点：只从设置了过期时间的键中淘汰LRU
    // 适用场景：混合场景，重要数据不设过期时间
    
    public void mixedDataStrategy() {
        // 重要数据：不设过期时间，不会被淘汰
        redisTemplate.opsForValue().set("important:config", "critical_data");
        
        // 缓存数据：设置过期时间，可能被LRU淘汰
        redisTemplate.opsForValue().set("cache:temp", "temp_data", 1, TimeUnit.HOURS);
    }
}
```

**4. allkeys-random & volatile-random**
```java
// 随机淘汰策略（不推荐生产环境）
public class RandomEvictionStrategy {
    // allkeys-random: 从所有键中随机淘汰
    // volatile-random: 从有过期时间的键中随机淘汰
    // 特点：性能好但不智能
    // 适用场景：测试环境或对数据访问模式无要求的场景
}
```

**5. volatile-ttl**
```java
// 配置: maxmemory-policy volatile-ttl
public class VolatileTTLStrategy {
    // 特点：优先淘汰即将过期的键
    // 适用场景：希望让数据按预期时间过期
    
    public void prioritizeExpiringKeys() {
        // 即将过期的数据会被优先淘汰
        redisTemplate.opsForValue().set("short_term", "data1", 1, TimeUnit.MINUTES);
        redisTemplate.opsForValue().set("long_term", "data2", 1, TimeUnit.HOURS);
        
        // 内存不足时，short_term会被优先淘汰
    }
}
```

**6. allkeys-lfu & volatile-lfu（Redis 4.0+，推荐）**
```java
// 配置: maxmemory-policy allkeys-lfu
public class LFUEvictionStrategy {
    // 特点：淘汰访问频率最低的键（比LRU更智能）
    // LFU考虑访问频率，LRU只考虑访问时间
    
    public void demonstrateLFU() {
        // 高频访问数据
        for (int i = 0; i < 1000; i++) {
            redisTemplate.opsForValue().get("popular:item"); // 高频访问
        }
        
        // 低频访问数据（容易被LFU淘汰）
        redisTemplate.opsForValue().get("rare:item"); // 只访问一次
        
        // LFU vs LRU:
        // - LRU: 最近访问过rare:item，popular:item可能被淘汰
        // - LFU: popular:item访问频率高，rare:item会被淘汰
    }
}
```

### 生产环境策略选择建议

```java
public class EvictionPolicyRecommendation {
    
    // 1. 纯缓存场景（推荐：allkeys-lfu）
    public void cacheScenario() {
        // 特点：所有数据都可以从数据库重新获取
        // 配置：maxmemory-policy allkeys-lfu
        // 原因：LFU算法更智能，保留真正的热点数据
    }
    
    // 2. 数据库场景（推荐：noeviction）
    public void databaseScenario() {
        // 特点：数据不能丢失
        // 配置：maxmemory-policy noeviction
        // 配合：监控告警 + 自动扩容
    }
    
    // 3. 混合场景（推荐：volatile-lfu）
    public void hybridScenario() {
        // 特点：重要数据不设过期时间，缓存数据设过期时间
        // 配置：maxmemory-policy volatile-lfu
        
        // 重要数据（永不过期，不会被淘汰）
        redisTemplate.opsForValue().set("config:app", "important_config");
        
        // 缓存数据（设置过期时间，可能被淘汰）
        redisTemplate.opsForValue().set("cache:user:123", "user_info", 30, TimeUnit.MINUTES);
    }
    
    // 4. 高性能场景（可考虑：allkeys-random）
    public void highPerformanceScenario() {
        // 特点：对数据访问模式要求不高，追求极致性能
        // 配置：maxmemory-policy allkeys-random
        // 原因：随机算法性能最好，无需维护LRU/LFU数据结构
    }
}
```

### 内存淘汰性能优化

```java
public class EvictionPerformanceOptimization {
    
    // 1. 配置合适的采样数量
    public void configureSampling() {
        // maxmemory-samples 5  # 默认值，可以调整到3-10
        // 数值越大越精确，但性能越差
        // 生产环境建议：3-5
    }
    
    // 2. 监控淘汰性能
    public void monitorEvictionPerformance() {
        Properties info = redisTemplate.execute(connection -> {
            return connection.info("stats");
        });
        
        String evictedKeys = info.getProperty("evicted_keys");
        String keyspaceHits = info.getProperty("keyspace_hits");
        String keyspaceMisses = info.getProperty("keyspace_misses");
        
        // 计算命中率
        long hits = Long.parseLong(keyspaceHits);
        long misses = Long.parseLong(keyspaceMisses);
        double hitRate = (double) hits / (hits + misses) * 100;
        
        System.out.println("缓存命中率: " + String.format("%.2f%%", hitRate));
        System.out.println("淘汰键数量: " + evictedKeys);
        
        // 命中率过低可能需要调整淘汰策略或增加内存
        if (hitRate < 80) {
            System.out.println("警告：缓存命中率偏低，建议检查淘汰策略");
        }
    }
    
    // 3. 优化键的设计
    public void optimizeKeyDesign() {
        // 避免大键：大键的淘汰会影响性能
        // ❌ 错误：存储大对象
        // redisTemplate.opsForValue().set("big_object", largeObject);
        
        // ✅ 正确：拆分成小键
        Map<String, String> userData = Map.of(
            "name", "张三",
            "age", "25",
            "email", "zhangsan@example.com"
        );
        redisTemplate.opsForHash().putAll("user:123", userData);
        
        // 设置合理的过期时间分布，避免同时过期造成性能抖动
        int baseExpire = 3600; // 1小时
        int randomExpire = new Random().nextInt(600); // 0-10分钟随机
        redisTemplate.expire("user:123", baseExpire + randomExpire, TimeUnit.SECONDS);
    }
}
```

### 实际项目配置示例

```java
@Configuration
public class RedisEvictionConfig {
    
    @Value("${redis.eviction.policy:allkeys-lfu}")
    private String evictionPolicy;
    
    @Value("${redis.eviction.maxmemory:2gb}")
    private String maxMemory;
    
    @Bean
    public RedisTemplate<String, Object> redisTemplate(RedisConnectionFactory connectionFactory) {
        RedisTemplate<String, Object> template = new RedisTemplate<>();
        template.setConnectionFactory(connectionFactory);
        
        // 可以通过代码设置内存策略（通常在redis.conf中配置）
        template.execute(connection -> {
            // CONFIG SET maxmemory 2gb
            // CONFIG SET maxmemory-policy allkeys-lfu
            // CONFIG SET maxmemory-samples 5
            return null;
        });
        
        return template;
    }
    
    // 内存监控Bean
    @Bean
    public RedisMemoryMonitor redisMemoryMonitor(RedisTemplate<String, Object> redisTemplate) {
        return new RedisMemoryMonitor(redisTemplate);
    }
}

@Component
class RedisMemoryMonitor {
    private final RedisTemplate<String, Object> redisTemplate;
    
    public RedisMemoryMonitor(RedisTemplate<String, Object> redisTemplate) {
        this.redisTemplate = redisTemplate;
    }
    
    @Scheduled(fixedRate = 60000) // 每分钟检查一次
    public void checkMemoryUsage() {
        Properties info = redisTemplate.execute(connection -> {
            return connection.info("memory");
        });
        
        String usedMemoryHuman = info.getProperty("used_memory_human");
        String usedMemoryPeak = info.getProperty("used_memory_peak_human");
        double memoryFragmentationRatio = Double.parseDouble(
            info.getProperty("mem_fragmentation_ratio", "1.0"));
        
        // 内存使用率过高告警
        if (memoryFragmentationRatio > 1.5) {
            log.warn("Redis内存碎片率过高: {}, 当前内存: {}, 峰值内存: {}", 
                    memoryFragmentationRatio, usedMemoryHuman, usedMemoryPeak);
        }
    }
}
```

**总结：三种内存处理机制对比**

| 处理机制 | 触发时机 | 处理对象 | 性能影响 | 适用场景 |
|---------|---------|---------|---------|----------|
| **惰性删除** | 访问键时检查 | 过期键 | 访问时轻微影响 | 所有访问场景 |
| **定期删除** | 定期后台任务 | 过期键（采样） | 持续的轻微影响 | 有过期时间的键 |
| **内存淘汰** | 内存满时写操作 | 任意键（根据策略） | 写操作时有延迟 | 内存紧张场景 |

**最佳实践**：
1. **三种机制协同工作**：惰性删除+定期删除+内存淘汰共同保证内存健康
2. **设置合适的maxmemory**：通常为物理内存的70-80%
3. **选择智能策略**：生产环境推荐allkeys-lfu或volatile-lfu
4. **配置合适的hz值**：平衡定期删除的性能和效果
5. **监控关键指标**：命中率、淘汰数量、过期数量、内存碎片率
6. **合理设置过期时间**：避免大量键同时过期对定期删除造成压力
7. **避免大键**：大键的删除和淘汰会影响性能
8. **合理利用惰性删除**：在业务中适当访问可能过期的键，触发惰性清理

#### 内存淘汰策略详解

1. **noeviction**：不淘汰，内存满时返回错误
2. **allkeys-lru**：所有key中淘汰最少使用的
3. **volatile-lru**：设置过期时间的key中淘汰最少使用的
4. **allkeys-random**：所有key中随机淘汰
5. **volatile-random**：设置过期时间的key中随机淘汰
6. **volatile-ttl**：淘汰即将过期的key
7. **allkeys-lfu**：所有key中淘汰使用频率最低的（Redis 4.0+）
8. **volatile-lfu**：设置过期时间的key中淘汰使用频率最低的

**实际项目配置建议**：
- 缓存场景：allkeys-lru
- 数据库场景：noeviction
- 混合场景：volatile-lru

redis 单机  n个数据库
集群 槽位 16384  好处:快速定位数据,方便扩容,数据分配均匀,故障不影响

gossip协议

一致性hash算法
槽位算法

## 6.6 Redis集群原理

**Q: Redis集群的工作原理是什么？**

### Redis单机与集群架构

redis 单机  n个数据库
集群 槽位 16384  好处:快速定位数据,方便扩容,数据分配均匀,故障不影响

平均分,3个节点到4个节点

### Gossip协议

Gossip协议是Redis Cluster中用于节点间通信和状态同步的协议：

1. **工作原理**：
   - 节点间定期随机交换信息
   - 信息传播呈指数级增长
   - 最终达到全局一致性

2. **优势**：
   - 去中心化，无单点故障
   - 网络分区容忍性强
   - 扩展性好，适合大规模集群

3. **应用场景**：
   - 节点状态检测
   - 集群拓扑信息同步
   - 故障检测和恢复

### 一致性Hash算法

0-2的32次方-1
顺时针定位节点


一致性Hash算法用于解决分布式系统中数据分布和负载均衡问题：

1. **基本原理**：
   - 将数据和节点映射到同一环形空间
   - 通过顺时针查找确定数据存储节点
   - 新增/删除节点只影响相邻节点

2. **优势**：
   - 节点变化时数据迁移量最小
   - 负载分布均匀
   - 适合动态扩容场景

3. **虚拟节点**：
   - 解决数据倾斜问题
   - 提高负载均衡效果
   - 增强算法稳定性

### 槽位算法

Redis Cluster采用16384个槽位的分片算法：

1. **槽位分配**：
   ```
   槽位计算公式：CRC16(key) % 16384
   ```

2. **优势**：
   - 固定槽数量，便于管理
   - 数据分布均匀
   - 支持快速定位和迁移
   - 故障恢复简单

3. **集群扩容**：
   - 平滑扩容，无需停机
   - 槽位迁移，数据重分布
   - 支持在线添加/删除节点

### 集群与单机对比

| 特性 | 单机模式 | 集群模式 |
|------|---------|---------|
| 数据库数量 | 16个（默认） | 16384个槽位 |
| 数据存储 | 单节点存储 | 分片存储 |
| 扩展性 | 垂直扩展 | 水平扩展 |
| 高可用 | 需要主从 | 自动故障转移 |
| 性能 | 受单节点限制 | 可线性扩展 |
| 复杂度 | 简单 | 较复杂 |

### 最佳实践

1. **集群规划**：
   - 建议至少3主3从
   - 奇数个节点提高可用性
   - 合理分配内存和CPU资源

2. **数据设计**：
   - 使用Hash Tag保证相关数据在同一节点
   - 避免大Key影响集群性能
   - 合理设置过期时间

3. **运维监控**：
   - 监控集群状态和槽位分布
   - 定期检查节点健康状况
   - 建立完善的故障处理流程

## 6.7 ZSet底层数据结构

### 6.7.1 ZSet数据结构概述

**Q: Redis的ZSet底层数据结构是什么？为什么这样设计？**

Redis的ZSet（有序集合）是一种特殊的集合数据结构，它不仅能够保证成员的唯一性，还能为每个成员关联一个分数（score），并通过分数对成员进行排序。

**ZSet的核心特性**：
1. **唯一性**：集合中的每个成员都是唯一的
2. **有序性**：通过分数（score）对成员进行排序
3. **高效性**：支持O(logN)时间复杂度的插入、删除和范围查询操作

**ZSet的应用场景**：
- 排行榜系统（如游戏积分排行榜）
- 延迟队列（通过分数表示时间戳）
- 范围查询（如查找分数在某个区间的成员）
- 热点数据缓存（通过访问频次作为分数）

```java
// ZSet使用示例
@Service
public class LeaderboardService {
    
    @Autowired
    private StringRedisTemplate redisTemplate;
    
    // 添加用户积分
    public void addUserScore(String userId, double score) {
        redisTemplate.opsForZSet().add("leaderboard", userId, score);
    }
    
    // 获取排行榜前N名
    public Set<ZSetOperations.TypedTuple<String>> getTopPlayers(int topN) {
        return redisTemplate.opsForZSet().reverseRangeWithScores("leaderboard", 0, topN - 1);
    }
    
    // 获取用户排名
    public Long getUserRank(String userId) {
        return redisTemplate.opsForZSet().reverseRank("leaderboard", userId);
    }
    
    // 获取用户分数
    public Double getUserScore(String userId) {
        return redisTemplate.opsForZSet().score("leaderboard", userId);
    }
}
```

### 6.7.2 跳跃表(Skip List)原理

**跳跃表结构详解**：

跳跃表是一种随机化的数据结构，它以O(logN)的期望时间复杂度执行查找、插入和删除操作，性能可以与平衡树相媲美，但实现更简单。

**跳跃表的结构**：
1. **多层链表**：包含多个层级的有序链表
2. **层级关系**：底层包含所有元素，上层是底层元素的子集
3. **向前指针**：每个节点包含多个指向后续节点的指针
4. **分层索引**：高层提供快速跳跃，底层提供精确查找

```c
// Redis中跳跃表节点结构（简化版）
typedef struct zskiplistNode {
    // 成员对象
    robj *obj;
    
    // 分数
    double score;
    
    // 后退指针（用于从后向前遍历）
    struct zskiplistNode *backward;
    
    // 层级数组
    struct zskiplistLevel {
        // 前进指针
        struct zskiplistNode *forward;
        
        // 跨度（到达下一节点需要跨越的节点数）
        unsigned int span;
    } level[];
} zskiplistNode;

// 跳跃表结构
typedef struct zskiplist {
    // 表头节点和表尾节点
    struct zskiplistNode *header, *tail;
    
    // 节点数量
    unsigned long length;
    
    // 最大层数
    int level;
} zskiplist;
```

**层级生成原理**：

跳跃表的层级是通过随机算法生成的，这是跳跃表性能的关键所在。

```c
// Redis中层级生成算法
#define ZSKIPLIST_MAXLEVEL 32  // 最大层级
#define ZSKIPLIST_P 0.25       // 概率因子

int zslRandomLevel(void) {
    int level = 1;
    
    // 使用随机数生成器，以0.25的概率增加层级
    // 这样可以保证高层级节点相对较少，底层节点相对较多
    while ((random() & 0xFFFF) < (ZSKIPLIST_P * 0xFFFF))
        level += 1;
    
    // 确保不超过最大层级
    return (level < ZSKIPLIST_MAXLEVEL) ? level : ZSKIPLIST_MAXLEVEL;
}
```

**层级生成过程详解**：

1. **概率机制**：每个新节点的层级通过概率算法确定
2. **概率因子**：Redis使用0.25作为概率因子
3. **层级分布**：
   - 50%的节点在第1层
   - 25%的节点在第2层
   - 12.5%的节点在第3层
   - 以此类推...

**跳跃表操作复杂度**：
- **查找**：O(logN)平均时间复杂度
- **插入**：O(logN)平均时间复杂度
- **删除**：O(logN)平均时间复杂度
- **空间复杂度**：O(N)平均空间复杂度

**跳跃表示例图解**：
```
Level 3: -∞ ---------------------------------------> +∞
          |                                           |
Level 2: -∞ ---------------> 15 -------------------> +∞
          |                 |                        |
Level 1: -∞ ------> 7 -----> 15 ------> 23 --------> +∞
          |        |        |         |             |
Level 0: -∞ ---> 3 ---> 7 ---> 15 ---> 23 ---> 31 -> +∞
```

**跳跃表的优势**：
1. **实现简单**：相比平衡树，实现更简单
2. **性能稳定**：操作复杂度稳定在O(logN)
3. **范围查询高效**：支持高效的范围查询操作
4. **并发友好**：相比树结构，更容易实现并发控制

### 6.7.3 压缩列表(ziplist)实现

**压缩列表结构**：

当ZSet中的元素较少且元素本身较小时，Redis会使用压缩列表作为底层实现，以节省内存空间。

**压缩列表的特点**：
1. **内存紧凑**：连续内存存储，减少内存碎片
2. **存储效率高**：对于小数据集，内存使用更少
3. **适用场景**：元素数量少且元素值较小时

**压缩列表的结构**：
```c
// 压缩列表结构（简化版）
typedef struct zlentry {
    // 前一个节点的长度
    unsigned int prevrawlensize;
    unsigned int prevrawlen;
    
    // 当前节点的长度
    unsigned int lensize;
    unsigned int len;
    
    // 节点头部信息
    unsigned int headersize;
    
    // 节点编码方式
    unsigned char encoding;
    
    // 节点内容
    unsigned char *p;
} zlentry;
```

**ZSet中压缩列表的存储方式**：
```
[member1][score1][member2][score2][member3][score3]...
```

每个元素由成员和分数交替存储，通过这种方式维护成员与分数的关联关系。

**压缩列表的限制**：
1. **元素数量限制**：默认不超过128个元素
2. **元素大小限制**：默认每个元素不超过64字节
3. **性能限制**：插入和删除操作需要移动内存，性能较差

### 6.7.4 ZSet内部编码选择

**Redis如何选择ZSet的底层实现**：

Redis会根据ZSet中元素的数量和大小动态选择底层数据结构：

1. **压缩列表条件**（满足以下所有条件时使用）：
   - 元素数量不超过`zset-max-ziplist-entries`（默认128）
   - 每个元素的成员长度不超过`zset-max-ziplist-value`（默认64字节）

2. **跳跃表条件**（不满足压缩列表条件时使用）：
   - 元素数量超过阈值
   - 元素大小超过阈值
   - 需要高性能的插入、删除操作

**配置参数**：
```bash
# ziplist实现的最大元素数量
zset-max-ziplist-entries 128

# ziplist实现的最大元素值长度
zset-max-ziplist-value 64
```

**编码转换过程**：

当ZSet从压缩列表转换为跳跃表时，Redis会：
1. 遍历压缩列表中的所有元素
2. 为每个元素创建跳跃表节点
3. 按分数排序插入到跳跃表中
4. 释放压缩列表内存

```java
// 监控ZSet编码方式
@Service
public class ZSetEncodingMonitor {
    
    @Autowired
    private StringRedisTemplate redisTemplate;
    
    public void checkZSetEncoding(String key) {
        // 使用OBJECT ENCODING命令检查编码方式
        String encoding = redisTemplate.execute((RedisCallback<String>) connection -> {
            return new String(connection.execute("OBJECT", "ENCODING".getBytes(), key.getBytes()));
        });
        
        System.out.println("ZSet " + key + " 的编码方式: " + encoding);
        
        // 获取元素数量
        Long size = redisTemplate.opsForZSet().zCard(key);
        System.out.println("ZSet " + key + " 的元素数量: " + size);
        
        // 根据编码方式优化使用策略
        if ("ziplist".equals(encoding)) {
            System.out.println("当前使用压缩列表实现，适合小数据集");
        } else if ("skiplist".equals(encoding)) {
            System.out.println("当前使用跳跃表实现，适合大数据集和高性能要求");
        }
    }
    
    // 优化ZSet使用
    public void optimizeZSetUsage() {
        // 对于小的排行榜，可以接受压缩列表的性能
        // 对于大的排行榜，需要考虑分片或者使用跳跃表
        
        // 合理设置配置参数
        redisTemplate.execute((RedisCallback<Void>) connection -> {
            // 设置最大ziplist元素数量为64（更保守的策略）
            connection.execute("CONFIG", "SET".getBytes(), "zset-max-ziplist-entries".getBytes(), "64".getBytes());
            return null;
        });
    }
}
```

**性能对比**：

| 操作 | 压缩列表 | 跳跃表 |
|------|---------|--------|
| 内存使用 | 少 | 多 |
| 插入性能 | O(N) | O(logN) |
| 删除性能 | O(N) | O(logN) |
| 查找性能 | O(N) | O(logN) |
| 范围查询 | O(N) | O(logN+M) |

**最佳实践**：

1. **合理配置参数**：根据实际数据特点调整`zset-max-ziplist-entries`和`zset-max-ziplist-value`
2. **监控编码方式**：定期检查ZSet的编码方式，确保符合预期
3. **数据分片**：对于超大ZSet，考虑将数据分片到多个key中
4. **定期清理**：及时清理过期或无用的数据，避免ZSet过大
