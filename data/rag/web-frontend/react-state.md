# React状态管理

## 概述

React状态管理是指在React应用中组织、存储和同步UI数据的系统性方法。React组件通过`useState`（2019年2月React 16.8引入Hooks）提供局部状态，通过`useReducer`处理复杂状态逻辑，但当多个不相邻组件需要共享同一份数据时，单靠Props传递会产生"Prop Drilling"问题——数据需要穿越与其无关的中间层组件才能抵达目标。

React状态管理本质上是在三个维度做出权衡：**数据存储位置**（组件局部 vs 全局单一Store vs 原子化分散）、**变更控制权**（纯函数Reducer vs 直接赋值 vs 不可变更新）、**订阅粒度**（全量重渲染 vs 选择器精确订阅）。Redux（Dan Abramov, 2015年发布）选择严格单向数据流和单一数据源；Zustand（Daishi Katoさん, 2019年）选择最小化API和直接状态更新；Jotai（2021年）选择类Recoil的原子化模型，每个`atom`是独立的最小状态单元。这三种路线代表了不同的设计哲学，而非简单的版本迭代关系。

理解React状态管理，需要理解为何Facebook工程师在2014年提出Flux架构：MVC模式下，Controller可以更新多个Model，Model之间还可互相调用，导致数据流向难以追踪（Pete Hunt在React.js Conf 2015演讲中称之为"cascading updates"问题）。Flux通过引入单向数据流切断了这种级联更新，Redux随后将其精炼为最简实现。

## 核心原理

### 单向数据流与Reducer纯函数

Redux将状态管理抽象为一个数学函数：

$$\text{reducer}(S_{t-1}, A_t) = S_t$$

其中 $S_{t-1}$ 是前一时刻的状态，$A_t$ 是当前Action，$S_t$ 是新状态。Reducer必须是**纯函数**：相同输入永远产生相同输出，且不产生任何副作用。这一约束使Redux DevTools能够实现时间旅行调试——任意两个状态快照之间可以通过回放Action序列精确重现。

不可变性（Immutability）在嵌套对象中实现极为繁琐。Redux Toolkit（RTK，2019年官方发布）内置Immer 9.x，使用ES6 Proxy拦截赋值操作，对外表现为直接修改，内部产生全新的不可变状态树：

```javascript
// RTK createSlice中Immer驱动的"假直接修改"
const counterSlice = createSlice({
  name: 'counter',
  initialState: { value: 0, history: [] },
  reducers: {
    increment: (state) => {
      state.history.push(state.value); // Immer拦截push，生成新数组
      state.value += 1;               // Immer拦截赋值，生成新对象
    }
  }
});
```

RTK的`createAsyncThunk`还封装了`pending/fulfilled/rejected`三个Action生命周期，配合`extraReducers`统一处理异步状态，解决了早期Redux需要手写大量样板代码（Boilerplate）的痛点——官方数据显示RTK可减少约40%的Redux代码量。

### Context API的渲染传播机制

React Context通过`React.createContext(defaultValue)`创建上下文。当Provider的`value` prop发生**引用变化**（Object.is比较为false），React会遍历整个子树，找出所有`useContext(MyContext)`的消费者并强制触发重渲染——这是一次**全量广播**，与该组件是否实际使用了变化的字段无关。

例如以下设计存在严重的性能陷阱：

```javascript
// 反例：每次父组件渲染都创建新对象引用
const AppContext = createContext();
function App() {
  const [user, setUser] = useState(null);
  const [theme, setTheme] = useState('light');
  // 每次App重渲染，{ user, theme, setUser, setTheme }都是新引用
  return (
    <AppContext.Provider value={{ user, theme, setUser, setTheme }}>
      <DeepTree />
    </AppContext.Provider>
  );
}
```

正确做法是拆分Context（将频繁变化的`theme`与稳定的`user`分离），并用`useMemo`稳定value引用。但即便如此，Context也无法做到"只订阅对象中某个字段变化时才重渲染"——这正是Recoil和Jotai出现的技术动机。

### Zustand的订阅-选择器模型

Zustand基于发布-订阅模式，Store维护一个JS模块级别的单例状态，组件通过`useStore(selector)`传入选择器函数订阅状态切片：

```javascript
const useBearStore = create((set) => ({
  bears: 0,
  fish: 100,
  addBear: () => set((state) => ({ bears: state.bears + 1 })),
}));

// 该组件只在bears变化时重渲染，fish变化不触发
function BearCounter() {
  const bears = useBearStore((state) => state.bears);
  return <h1>{bears}</h1>;
}
```

Zustand使用`Object.is`对选择器返回值进行浅比较（shallow equality），若需深比较可传入第二参数`shallow`工具函数。这一机制使Zustand在中型应用中无需任何额外配置即可获得精准的重渲染控制，bundle size仅约1KB（gzip后），远小于Redux+React-Redux的约12KB组合。

### Jotai原子化模型与依赖追踪

Jotai借鉴了Recoil（Facebook, 2020年）的原子化思想，但去除了Recoil对`key`字符串的强制要求。每个`atom`是独立的状态单元，`derivedAtom`（衍生原子）通过`get`函数声明对其他atom的依赖：

```javascript
const priceAtom = atom(100);
const quantityAtom = atom(3);
// 衍生原子：自动追踪priceAtom和quantityAtom的变化
const totalAtom = atom((get) => get(priceAtom) * get(quantityAtom));
```

当`priceAtom`变化时，只有订阅了`priceAtom`或`totalAtom`的组件重渲染，订阅`quantityAtom`的组件完全不受影响。Jotai在内部维护一个WeakMap实现的依赖图，时间复杂度接近 $O(1)$ 的原子读写，非常适合粒度极细的局部状态管理场景。

## 关键方法与公式

### 状态规范化（Normalization）

当Store中存储嵌套实体数据时，Redux官方推荐使用**状态规范化**，将数据扁平化存储：

$$\text{NormalizedState} = \{ \text{entities}: \{ id \Rightarrow item \}, \text{ids}: [id_1, id_2, \ldots] \}$$

RTK内置`createEntityAdapter`实现这一模式，提供`addOne`、`upsertMany`等预构建Reducer和`selectAll`、`selectById`等Memoized选择器。规范化后查询特定实体的时间复杂度从 $O(n)$（遍历数组）降至 $O(1)$（哈希表查找）。

### Memoized选择器与Reselect

当选择器需要做计算推导时，直接在组件内写内联函数会导致每次渲染都重新计算。`reselect`库（Redux官方维护）的`createSelector`实现了**记忆化（Memoization）**：

```javascript
const selectCompletedTodos = createSelector(
  [(state) => state.todos],           // 输入选择器
  (todos) => todos.filter(t => t.done) // 结果函数：只在todos引用变化时重新执行
);
```

若`todos`数组引用未变，`createSelector`直接返回上次的缓存结果，避免了每次渲染产生新的数组引用导致的下游重渲染链。`reselect` v5（2023年）起支持多缓存槽（`memoizeOptions.maxSize`），解决了v4单槽缓存在参数频繁变化场景下缓存命中率低的问题。

### useReducer + useContext的轻量模式

对于中小型应用，`useReducer` + `useContext`可以实现无外部库的状态共享：

```javascript
const TodoContext = createContext();
function TodoProvider({ children }) {
  const [state, dispatch] = useReducer(todoReducer, initialState);
  // 关键优化：分离state和dispatch的Context，避免dispatch不变但state变化引起订阅dispatch的组件重渲染
  return (
    <TodoDispatchContext.Provider value={dispatch}>
      <TodoStateContext.Provider value={state}>
        {children}
      </TodoStateContext.Provider>
    </TodoDispatchContext.Provider>
  );
}
```

将`state`和`dispatch`放入**两个独立的Context**是React官方文档（Dan Abramov在reactjs.org）明确推荐的模式——因为`dispatch`函数在组件生命周期内引用稳定，不会触发消费者重渲染。

## 实际应用

### 案例：电商购物车的状态方案选型

**场景描述**：电商应用包含商品列表页、购物车侧边栏、结算页，三个模块共享cart数据，同时商品列表有本地筛选状态，结算页有表单状态。

**方案选择**：
- `cart`数据（跨页面共享、需持久化）→ Zustand Store，配合`zustand/middleware`的`persist`中间件写入localStorage
- 商品列表筛选（单组件局部）→ `useState`
- 结算表单（复杂验证逻辑）→ `useReducer`或React Hook Form

**Zustand实现购物车**：
```javascript
const useCartStore = create(
  persist(
    (set, get) => ({
      items: [],
      addItem: (product) => set((state) => {
        const existing = state.items.find(i => i.id === product.id);
        if (existing) {
          return { items: state.items.map(i =>
            i.id === product.id ? { ...i, qty: i.qty + 1 } : i
          )};
        }
        return { items: [...state.items, { ...product, qty: 1 }] };
      }),
      total: () => get().items.reduce((sum, i) => sum + i.price * i.qty, 0),
    }),
    { name: 'cart-storage' }
  )
);
```

### 案例：大型后台系统的Redux Toolkit实践

某金融后台（数十个业务模块，数据依赖关系复杂）使用RTK的`createSlice` + `RTK Query`方案。RTK Query基于Redux Store内置了数据缓存、自动轮询、乐观更新机制，将服务端状态（Server State）与客户端UI状态严格分离——这一分离思想与TanStack Query（React Query）的设计哲学一致（Tanner Linsley, 2019年）。

RTK Query定义API端点：

```javascript
const api = createApi({
  baseQuery: fetchBaseQuery({ baseUrl: '/api' }),
  endpoints: (builder) => ({
    getOrders: builder.query({ query: (userId) => `/orders/${userId}` }),
    updateOrder: builder.mutation({
      query: ({ id, ...patch }) => ({ url: `/orders/${id}`, method: 'PATCH', body: patch }),
      invalidatesTags: ['Order'], // 更新后自动使getOrders缓存失效并重新请求
    }),
  }),
});
```

## 常见误区

### 误区1：将所有状态放入全局Store

许多开发者误认为"Redux项目必须把所有状态放Redux"。实际上，Dan Abramov本人在Twitter（2018年）明确表示："Don't use Redux for everything. Keep local state local." 表单的输入值、下拉菜单的开关状态、本地的加载动画——这些**只属于单个组件的短暂UI状态**不应提升至全局。滥用全局状态会导致Store臃肿、组件复用困难。

判断依据：若某状态在当前组件卸载后不需要保留，且没有其他组件依赖它，应使用`useState`。

### 误区2：Context = 状态管理库的替代品

Context API被设计用于解决依赖注入（Dependency Injection）问题，如主题、语言、当前用户——这些**低频变化**的"环境数据"。将高频变化的业务数据（如实时列表、计数器）放入Context，会因缺乏精准订阅能力而导致大量无效重渲染。Sebastian Markbåge（React核心团队）在2021年的GitHub issue中明确指出Context不是高性能状态管理的解决方案，React团队已通过Jotai、Zustand等外部库补全这一能力。

### 误区3：Zustand不适合大型应用

部分团队认为Zustand"太简单"无法支撑大型应用。实际上Zustand通过中间件机制（`devtools`、`immer`、`persist`、`subscribeWithSelector`）可组合扩展，支持Redux DevTools调试，且与RTK一样支持切片化（Sl