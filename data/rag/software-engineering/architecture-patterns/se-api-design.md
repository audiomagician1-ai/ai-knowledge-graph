# API设计原则

## 概述

API（Application Programming Interface）是软件系统之间通信的契约，定义了调用方式、数据格式、认证机制与错误处理规范。Roy Fielding在2000年的博士论文《Architectural Styles and the Design of Network-based Software Architectures》中正式提出REST（Representational State Transfer），确立了无状态（Stateless）、统一接口（Uniform Interface）、客户端-服务器分离（Client-Server）、可缓存（Cacheable）、分层系统（Layered System）、按需代码（Code-on-Demand，可选）六大架构约束。2012年Facebook内部孵化、2015年公开发布的GraphQL旨在解决移动端因REST过度获取（Over-fetching）和获取不足（Under-fetching）导致的网络流量浪费问题。同年，Google发布gRPC框架，基于HTTP/2多路复用与Protocol Buffers二进制序列化，实现了比JSON-over-HTTP低40%~60%的传输体积和更低的反序列化延迟（Google内部测量数据）。

良好API设计的核心价值在于：API一经发布便形成契约，破坏性变更（Breaking Change）会直接导致下游调用方故障。Twitter在2012年将API v1强制迁移至v1.1时，因未给足迁移窗口导致数千个第三方应用在同一天崩溃。Stripe在其API设计哲学中明确规定"永不废弃已发布字段，只增不删"，并为每个API密钥记录其调用的最低版本，以便精确评估废弃影响。

## 核心原理

### RESTful资源建模与HTTP语义

REST以"资源"为核心组织URL，资源用名词复数表示，HTTP动词承载操作语义。标准映射关系如下：

- `GET /orders` — 列表查询，幂等，可缓存
- `GET /orders/{id}` — 单资源读取，幂等
- `POST /orders` — 创建资源，非幂等，响应应携带 `Location: /orders/456` 头及 `201 Created` 状态码
- `PUT /orders/{id}` — 全量替换，幂等
- `PATCH /orders/{id}` — 局部更新，按RFC 7396规范应传递JSON Merge Patch格式
- `DELETE /orders/{id}` — 删除，幂等，成功返回 `204 No Content`

HTTP状态码必须精确传递语义：`400 Bad Request` 用于参数格式错误，`422 Unprocessable Entity` 用于格式合法但业务校验失败（如余额不足），`409 Conflict` 用于并发写冲突，`429 Too Many Requests` 用于限流并附带 `Retry-After` 响应头。在响应体中使用 `{"code": 0, "msg": "success", "data": {...}}` 的包装模式，并对所有请求返回 `200 OK`，会完全破坏HTTP语义，使得负载均衡器、CDN缓存、监控系统无法正确识别错误。

**HATEOAS**（Hypermedia As The Engine Of Application State）是Fielding论文中REST Level 3的要求，在响应中嵌入后续操作的链接：

```json
{
  "id": 123,
  "status": "pending",
  "_links": {
    "confirm": { "href": "/orders/123/confirm", "method": "POST" },
    "cancel":  { "href": "/orders/123/cancel",  "method": "DELETE" }
  }
}
```

Richardson成熟度模型（Leonard Richardson, 2008）将REST实现分为四级（Level 0~3），业界大多数"RESTful API"实际停留在Level 2（正确使用HTTP动词和状态码），真正达到Level 3（HATEOAS）的较少。

### GraphQL类型系统与查询语言

GraphQL通过Schema Definition Language（SDL）声明类型系统，客户端可通过Introspection接口（`__schema`、`__type`）在运行时查询完整的类型定义，这是GraphQL自文档化的基础。一个完整的SDL示例：

```graphql
type Order {
  id: ID!
  totalAmount: Float!
  items: [OrderItem!]!
  createdAt: String!
}

type Query {
  order(id: ID!): Order
  orders(userId: ID!, last: Int = 10): [Order!]!
}

type Mutation {
  createOrder(input: CreateOrderInput!): Order!
}
```

客户端精确指定所需字段，服务端仅返回请求字段，消除Over-fetching：

```graphql
query {
  order(id: "42") {
    totalAmount
    items { productName quantity }
  }
}
```

GraphQL的N+1问题是最典型的性能陷阱：查询100个订单时，若每个订单触发一次独立的用户查询，将产生101次数据库请求。解决方案是使用DataLoader（Facebook开源，2015年）进行请求批处理（Batching）和去重（Deduplication），将N+1次查询合并为2次。

### gRPC协议设计与Protocol Buffers

gRPC使用`.proto`文件定义服务契约，字段编号（Field Number）是协议兼容性的核心保证：已发布的字段编号不得复用，删除字段后其编号应标记为`reserved`以防止意外重用。

```protobuf
syntax = "proto3";

service OrderService {
  rpc GetOrder (GetOrderRequest) returns (Order);
  rpc StreamOrders (StreamOrdersRequest) returns (stream Order);
}

message Order {
  string id = 1;
  double total_amount = 2;
  repeated OrderItem items = 3;
  reserved 4; // 已废弃字段，防止编号复用
}
```

gRPC支持四种通信模式：一元（Unary）、服务端流（Server Streaming）、客户端流（Client Streaming）和双向流（Bidirectional Streaming），后三种均基于HTTP/2的多路复用特性，适合日志上传、实时推送等场景。相比JSON，Protocol Buffers在同等数据量下体积约小3~10倍，反序列化速度约快5~7倍（Google, 2008年Protocol Buffers技术博客）。

## 关键方法与公式

### API版本管理策略

版本管理的本质是在向后兼容与接口演进之间寻求平衡。三种主流方案的权衡如下：

| 方案 | 示例 | 优点 | 缺点 |
|------|------|------|------|
| URI路径版本 | `/v2/users` | 可读性强，易于路由 | 多版本代码共存 |
| 请求头版本 | `Accept: application/vnd.api+json;version=2` | 符合HTTP内容协商规范 | 调试不便，浏览器直接访问困难 |
| 查询参数版本 | `?api_version=2` | 实现简单 | 不符合RESTful语义，URL缓存失效 |

GitHub API、Stripe API均采用URI路径版本（`/v1/`、`/v2/`），并承诺每个主版本的支持周期不少于18个月。

语义化版本控制（Semantic Versioning，SemVer）在API上下文中的应用规则：主版本号（MAJOR）升级表示破坏性变更，如删除字段或更改字段类型；次版本号（MINOR）升级表示新增功能，向后兼容；修订号（PATCH）升级表示错误修复。

### 限流算法与速率限制

API限流的令牌桶算法（Token Bucket）允许突发流量，漏桶算法（Leaky Bucket）强制平滑输出速率。令牌桶的令牌生成速率 $r$（tokens/s）与桶容量 $b$（tokens）决定了允许的最大突发请求量。当请求到达时，若桶中令牌数 $n \geq 1$，则消耗一个令牌并处理请求；否则返回 `429 Too Many Requests`，并在 `Retry-After` 头中返回下次可用时间（单位：秒）：

$$
t_{retry} = \frac{1 - n}{r}
$$

其中 $n$ 为当前令牌数（可为负数），$r$ 为令牌填充速率。

### 幂等性设计

幂等性（Idempotency）是指多次执行相同操作产生与单次执行相同的结果。`GET`、`PUT`、`DELETE` 在REST规范中定义为幂等操作，`POST` 非幂等。对于支付、订单创建等`POST`操作，可通过客户端生成唯一的幂等键（Idempotency Key）实现幂等性：

```http
POST /payments
Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000
Content-Type: application/json

{"amount": 9900, "currency": "CNY"}
```

服务端以此键为主键存储请求结果，对于重复请求直接返回缓存响应（HTTP `200`），而不重新执行业务逻辑。Stripe的支付API强制要求客户端传递此请求头，以防止网络重试导致的重复扣款。

## 实际应用

### 例如：电商订单API的三种范式对比

假设需要实现"查询用户最近5笔订单及每笔订单的商品名称"：

**REST方案**需要2~N次请求：
1. `GET /users/42/orders?limit=5` 获取订单列表
2. 若订单详情不含商品信息，还需对每个订单调用 `GET /orders/{id}/items`（N+1问题）

**GraphQL方案**单次请求获取精确数据：
```graphql
query {
  user(id: "42") {
    orders(last: 5) {
      id totalAmount
      items { productName quantity }
    }
  }
}
```

**gRPC方案**定义强类型契约，适合微服务内部调用：
```protobuf
rpc ListUserOrders (ListUserOrdersRequest) returns (ListUserOrdersResponse);
```

gRPC在内网微服务调用中因二进制序列化和HTTP/2多路复用，延迟比REST低约30%~40%（Uber Engineering Blog, 2018年，对比gRPC与REST在内部服务调用的基准测试）。

### OpenAPI规范与文档自动化

OpenAPI 3.0规范（前身为Swagger，2016年更名）使用YAML/JSON描述REST API的全部端点、参数、响应Schema和认证方式。通过`$ref`机制复用数据模型，避免Schema定义冗余。工具链（Swagger UI、ReDoc、Postman）可从OpenAPI规范自动生成交互式文档和客户端SDK，实现"规范即文档、规范即代码"的设计优先（Design-First）开发流程。

## 常见误区

**误区一：将动词写入URL路径**。`POST /createUser`、`GET /getUserById?id=1` 是RPC风格而非REST风格。URL应仅表达资源层级，操作语义由HTTP方法承载。

**误区二：对所有错误返回HTTP 200**。部分团队为了统一前端处理逻辑，将业务错误包裹在200响应中。这会导致：Nginx访问日志无法区分成功与失败，Prometheus等监控系统的HTTP错误率指标失真，API网关的熔断策略无法触发。

**误区三：忽略GraphQL的安全边界**。GraphQL允许客户端构造任意深度的嵌套查询，攻击者可构造深度嵌套的查询消耗服务器资源（Query Depth Attack）。防御措施包括设置最大查询深度（通常为10~15层）、查询复杂度计算（Query Complexity Score）和持久化查询（Persisted Queries，仅允许预注册的查询哈希值）。

**误区四：gRPC字段编号随意复用**。在`.proto`文件中删除字段后若未标注`reserved`，后续新字段复用该编号会导致反序列化时数据错乱，因为旧客户端会将新字段的二进制数据按旧字段类型解析。

**误区五：遗漏API幂等性设计**。在微服务架构中，网络超时后客户端重试是常见行为。若`POST /payments`不实现幂等性，重试将导致重复扣款。幂等性应在API设计阶段明确声明，而非事后补救。

## 知识关联

**与微服务架构（Microservices）的关联**：API网关（API Gateway）是微服务对外暴露的统一入口，负责认证、限流、协议转换（如REST↔gRPC）和请求路由。服务网格（Service Mesh，如Istio）在微服务内部通信层实现了gRPC负载均衡和mTLS认证，与API设计规范形成分层治理体系。

**与契约测试（Contract Testing）的关联**：Pact框架（ThoughtWorks开源）基于Consumer-Driven Contract Testing思想，消费方（Consumer）定义期望的API响应格式，发布为契约文件；提供方（Provider）在CI流水线中验证契约，从而在不运行完整集成测试的情况下检测破坏性变更。这是API版本演进中防止契约破坏的工程实践。

**与缓存策略的关联**：REST的可缓存约束通过HTTP `Cache-Control`、`E