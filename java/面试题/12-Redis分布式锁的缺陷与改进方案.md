# 12. Redis分布式锁的缺陷与改进方案

## 目录
- [12.1 SET EXPIRE原子性问题](#121-set-expire原子性问题)
- [12.2 锁续期的复杂性问题](#122-锁续期的复杂性问题)
- [12.3 网络分区和脑裂问题](#123-网络分区和脑裂问题)
- [12.4 时钟漂移问题](#124-时钟漂移问题)
- [12.5 使用注意事项与最佳实践](#125-使用注意事项与最佳实践)

---

## 12.1 SET EXPIRE原子性问题

**问题描述**：早期实现中SET和EXPIRE分离操作可能导致死锁

```java
// 有问题的实现方式
public class ProblematicRedisLock {
    
    public boolean badLock(String lockKey, String lockValue, int expireSeconds) {
        // 步骤1：设置键值
        Boolean success = redisTemplate.opsForValue().setIfAbsent(lockKey, lockValue);
        if (!Boolean.TRUE.equals(success)) {
            return false;
        }
        
        // 步骤2：设置过期时间（如果这里失败，锁永不过期！）
        try {
            redisTemplate.expire(lockKey, Duration.ofSeconds(expireSeconds));
            return true;
        } catch (Exception e) {
            // 已经设置了锁，但过期时间设置失败 - 造成死锁！
            log.error("设置过期时间失败，可能导致死锁", e);
            return false;
        }
    }
    
    // 正确的原子操作实现
    public boolean goodLock(String lockKey, String lockValue, Duration expireTime) {
        // SET key value EX seconds NX - 原子操作
        Boolean result = redisTemplate.opsForValue()
            .setIfAbsent(lockKey, lockValue, expireTime);
        return Boolean.TRUE.equals(result);
    }
}
```

## 12.2 锁续期的复杂性问题

**问题描述**：自动续期机制可能引入新的问题

```java
/**
 * 续期失败处理机制
 */
@Slf4j
public class RenewFailureHandler {
    
    private volatile int renewFailCount = 0;
    private final int maxFailCount = 3;
    private volatile boolean lockValid = true;
    
    public void handleRenewFailure(String lockKey, Exception e) {
        renewFailCount++;
        log.warn("锁续期失败，失败次数: {}, 锁: {}", renewFailCount, lockKey, e);
        
        if (renewFailCount >= maxFailCount) {
            lockValid = false;
            log.error("锁续期连续失败{}次，标记锁为无效: {}", maxFailCount, lockKey);
            
            // 通知业务层停止使用锁
            notifyLockInvalid(lockKey);
        }
    }
    
    public boolean isLockValid() {
        return lockValid;
    }
    
    private void notifyLockInvalid(String lockKey) {
        // 发送告警或通知
        // 可以通过监听器模式通知业务层
    }
    
    // 改进的续期实现
    public boolean safeRenew(String lockKey, String lockValue, Duration expireTime) {
        try {
            // 添加续期超时控制
            String script = 
                "if redis.call('GET', KEYS[1]) == ARGV[1] then " +
                "    redis.call('EXPIRE', KEYS[1], ARGV[2]) " +
                "    return 1 " +
                "else " +
                "    return 0 " +
                "end";
            
            Long result = redisTemplate.execute(
                new DefaultRedisScript<>(script, Long.class),
                Collections.singletonList(lockKey),
                lockValue,
                String.valueOf(expireTime.getSeconds())
            );
            
            boolean success = Long.valueOf(1L).equals(result);
            if (success) {
                renewFailCount = 0; // 重置失败计数
            } else {
                handleRenewFailure(lockKey, new RuntimeException("续期失败：锁不存在或不属于当前进程"));
            }
            
            return success;
            
        } catch (Exception e) {
            handleRenewFailure(lockKey, e);
            return false;
        }
    }
}
```

## 12.3 网络分区和脑裂问题

**问题描述**：Redis主从架构下可能出现脑裂现象

```java
/**
 * Redlock算法实现，解决脑裂问题
 */
@Component
public class RedlockManager {
    
    private List<StringRedisTemplate> redisTemplates;
    private final int quorum;
    
    public RedlockManager(List<StringRedisTemplate> redisTemplates) {
        this.redisTemplates = redisTemplates;
        this.quorum = redisTemplates.size() / 2 + 1;
    }
    
    /**
     * Redlock算法获取锁
     */
    public boolean acquireRedlock(String lockKey, String lockValue, Duration expireTime) {
        long startTime = System.currentTimeMillis();
        int successCount = 0;
        
        // 尝试在所有Redis实例上获取锁
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
        
        // 检查是否达到法定人数且在有效时间内
        long elapsedTime = System.currentTimeMillis() - startTime;
        long validityTime = expireTime.toMillis() - elapsedTime - 100; // 100ms时钟漂移容忍
        
        if (successCount >= quorum && validityTime > 0) {
            log.info("Redlock获取成功，成功实例数: {}/{}", successCount, redisTemplates.size());
            return true;
        } else {
            // 如果没有获得足够的锁，释放已获得的锁
            releaseRedlock(lockKey, lockValue);
            log.warn("Redlock获取失败，成功实例数: {}/{}, 有效时间: {}ms", 
                    successCount, redisTemplates.size(), validityTime);
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

## 12.4 时钟漂移问题

**问题描述**：不同服务器时钟差异影响锁有效性

```java
/**
 * 考虑时钟漂移的安全锁实现
 */
@Component
public class ClockDriftSafeLock {
    
    private final StringRedisTemplate redisTemplate;
    private final Duration clockDriftTolerance;
    
    public ClockDriftSafeLock(StringRedisTemplate redisTemplate) {
        this.redisTemplate = redisTemplate;
        this.clockDriftTolerance = Duration.ofSeconds(2); // 容忍2秒时钟漂移
    }
    
    public boolean safeLock(String lockKey, String lockValue, Duration originalExpireTime) {
        // 调整锁的有效期，考虑时钟漂移
        Duration safeExpireTime = originalExpireTime.minus(clockDriftTolerance.multipliedBy(2));
        
        if (safeExpireTime.isNegative() || safeExpireTime.isZero()) {
            throw new IllegalArgumentException(
                String.format("锁有效期%s太短，无法容忍时钟漂移%s", 
                    originalExpireTime, clockDriftTolerance));
        }
        
        log.debug("调整锁有效期：原始{}，安全{}", originalExpireTime, safeExpireTime);
        
        Boolean result = redisTemplate.opsForValue()
            .setIfAbsent(lockKey, lockValue, safeExpireTime);
        
        return Boolean.TRUE.equals(result);
    }
}
```

## 12.5 使用注意事项与最佳实践

1. **原子性操作**：始终使用SET NX EX等原子命令
2. **续期监控**：监控续期成功率，及时发现网络问题
3. **时钟同步**：确保各服务器时钟同步，或预留时钟漂移容忍度
4. **网络分区**：考虑使用Redlock算法应对脑裂问题
5. **异常处理**：完善的异常处理和降级机制
6. **监控告警**：建立完善的锁监控和告警机制
7. **性能权衡**：根据业务需求选择合适的一致性级别

redis为什么要设计成槽位
