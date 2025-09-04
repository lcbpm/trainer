# 4. Spring 框架

## 目录
- [4.1 IOC 容器](#41-ioc-容器)
- [4.2 AOP 切面](#42-aop-切面)
- [4.3 Spring Boot](#43-spring-boot)
- [4.4 Spring 源码分析](#44-spring-源码分析)
- [4.5 Spring三级缓存与循环依赖](#45-spring三级缓存与循环依赖)
- [4.6 Spring MVC执行原理](#46-spring-mvc执行原理)

---

## 4.1 IOC 容器
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

## 4.2 AOP 切面
**Q: AOP的实现原理？**
- **JDK动态代理**：基于接口代理
- **CGLIB代理**：基于类继承代理
- Spring默认：有接口用JDK，无接口用CGLIB
- 切面执行顺序：Around → Before → 目标方法 → After → AfterReturning/AfterThrowing

## 4.3 Spring Boot
**Q: Spring Boot自动配置原理？**
- @SpringBootApplication包含@EnableAutoConfiguration
- EnableAutoConfiguration通过AutoConfigurationImportSelector加载
- AutoConfigurationImportSelector使用SpringFactoriesLoader扫描META-INF/spring.factories文件
- 根据条件注解决定是否创建Bean
- @ConditionalOnClass、@ConditionalOnProperty等

## 4.4 Spring 源码分析
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

## 4.5 Spring三级缓存与循环依赖

**Q: Spring三级缓存的原理及作用？**

Spring三级缓存是Spring框架为解决单例Bean循环依赖问题而设计的机制，包含以下三个缓存：

1. **singletonObjects（一级缓存）**：存放完全初始化完成的单例Bean实例
2. **earlySingletonObjects（二级缓存）**：存放提前暴露的Bean实例（未完全初始化完成）
3. **singletonFactories（三级缓存）**：存放Bean工厂对象，用于创建提前暴露的Bean实例

**Q: Spring如何使用三级缓存解决循环依赖？**

以A依赖B，B依赖A的循环依赖为例：

1. 创建Bean A，实例化但未填充属性
2. 将A的ObjectFactory放入三级缓存singletonFactories
3. 填充A的属性，发现需要注入Bean B
4. 创建Bean B，实例化但未填充属性
5. 将B的ObjectFactory放入三级缓存singletonFactories
6. 填充B的属性，发现需要注入Bean A
7. 从三级缓存中获取A的ObjectFactory，调用getObject()方法获取A的早期引用
8. 将A的早期引用放入二级缓存earlySingletonObjects，同时从三级缓存移除
9. 完成B的属性填充和初始化，将B放入一级缓存singletonObjects
10. 回到A的初始化流程，完成A的属性填充，将A放入一级缓存singletonObjects

**Q: 为什么需要三级缓存而不是二级缓存？**

三级缓存的设计主要是为了处理AOP代理场景：

- 如果只有二级缓存，在普通Bean场景下确实可以解决循环依赖
- 但在涉及AOP代理时，需要在Bean初始化完成之后才创建代理对象
- 三级缓存中的ObjectFactory可以延迟代理对象的创建，确保只有在需要时才创建代理
- 这样既解决了循环依赖问题，又保证了AOP代理的正确性

**Q: 三级缓存能解决所有循环依赖问题吗？**

不能，Spring三级缓存只能解决以下场景的循环依赖：

- 单例Bean的setter注入循环依赖
- 单例Bean的field注入循环依赖

无法解决：

- prototype作用域Bean的循环依赖
- 构造器注入的循环依赖
- 多实例Bean的循环依赖

```java
// 循环依赖示例代码
@Component
public class ServiceA {
    @Autowired
    private ServiceB serviceB;
}

@Component
public class ServiceB {
    @Autowired
    private ServiceA serviceA;
}

// 三级缓存相关源码结构
public class DefaultSingletonBeanRegistry {
    // 一级缓存：存放完全初始化的单例Bean
    private final Map<String, Object> singletonObjects = new ConcurrentHashMap<>(256);
    
    // 二级缓存：存放提前暴露的Bean实例
    private final Map<String, Object> earlySingletonObjects = new HashMap<>(16);
    
    // 三级缓存：存放Bean工厂，用于创建提前暴露的Bean实例
    private final Map<String, ObjectFactory<?>> singletonFactories = new HashMap<>(16);
}
```

## 4.6 Spring MVC执行原理

**Q: Spring MVC的核心组件有哪些？**

Spring MVC框架包含以下核心组件：

1. **DispatcherServlet（前端控制器）**：整个流程控制的中心，负责接收请求并分发给合适的组件处理
2. **HandlerMapping（处理器映射器）**：根据请求URL查找对应的处理器（Controller）
3. **Controller（处理器/控制器）**：处理具体业务逻辑的组件
4. **ModelAndView（模型和视图）**：封装处理器返回的数据和视图信息
5. **ViewResolver（视图解析器）**：根据逻辑视图名解析为具体视图
6. **View（视图）**：负责渲染数据到客户端

**Q: Spring MVC的执行流程是什么？**

Spring MVC的执行流程如下：

1. **请求到达DispatcherServlet**：用户发送请求到前端控制器DispatcherServlet
2. **查找HandlerMapping**：DispatcherServlet调用HandlerMapping查找对应的处理器
3. **返回HandlerExecutionChain**：HandlerMapping返回一个HandlerExecutionChain对象（包含处理器和拦截器）
4. **调用HandlerAdapter**：DispatcherServlet通过HandlerAdapter执行处理器
5. **执行Controller**：HandlerAdapter调用具体的Controller处理业务逻辑
6. **返回ModelAndView**：Controller处理完成后返回ModelAndView对象
7. **视图解析**：DispatcherServlet调用ViewResolver解析视图
8. **渲染视图**：ViewResolver返回具体View，DispatcherServlet调用View渲染数据
9. **响应用户**：将渲染结果返回给用户

**Q: Spring MVC执行流程的详细步骤？**

```java
// Spring MVC核心组件交互示例
@Controller
public class UserController {
    
    @RequestMapping("/user")
    public ModelAndView getUser() {
        ModelAndView mav = new ModelAndView();
        // 设置数据模型
        mav.addObject("user", new User("张三", 25));
        // 设置视图名
        mav.setViewName("user");
        return mav;
    }
}

// User实体类
class User {
    private String name;
    private int age;
    
    public User(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    // getter和setter方法
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public int getAge() { return age; }
    public void setAge(int age) { this.age = age; }
}

// 自定义拦截器示例
public class MyInterceptor implements HandlerInterceptor {
    
    @Override
    public boolean preHandle(HttpServletRequest request, 
                           HttpServletResponse response, 
                           Object handler) throws Exception {
        System.out.println("预处理");
        return true; // 返回true继续执行，false中断执行
    }
    
    @Override
    public void postHandle(HttpServletRequest request, 
                         HttpServletResponse response, 
                         Object handler, 
                         ModelAndView modelAndView) throws Exception {
        System.out.println("后处理");
    }
    
    @Override
    public void afterCompletion(HttpServletRequest request, 
                              HttpServletResponse response, 
                              Object handler, 
                              Exception ex) throws Exception {
        System.out.println("完成处理");
    }
}
```

**Q: Spring MVC的九大组件是什么？**

Spring MVC中DispatcherServlet有九大核心组件：

1. **MultipartResolver**：处理文件上传
2. **LocaleResolver**：处理国际化
3. **ThemeResolver**：处理主题
4. **HandlerMapping**：处理器映射器
5. **HandlerAdapter**：处理器适配器
6. **HandlerExceptionResolver**：异常处理器
7. **RequestToViewNameTranslator**：视图名称转换器
8. **ViewResolver**：视图解析器
9. **FlashMapManager**：FlashMap管理器，用于重定向时参数传递

**Q: Spring MVC的工作原理总结**

Spring MVC基于前端控制器模式设计，将请求处理流程分为三个阶段：

1. **初始化阶段**：加载配置、创建组件
2. **运行阶段**：处理请求、执行业务逻辑
3. **销毁阶段**：清理资源、关闭容器

这种设计实现了请求处理的统一调度，降低了组件间的耦合度，提高了系统的可扩展性和可维护性。