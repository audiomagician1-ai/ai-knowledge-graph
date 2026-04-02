---
id: "se-gitignore"
concept: "忽略规则"
domain: "software-engineering"
subdomain: "version-control"
subdomain_name: "版本控制"
difficulty: 1
is_milestone: false
tags: ["配置"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.448
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 忽略规则

## 概述

忽略规则（Ignore Rules）是Git版本控制系统中用于指定哪些文件或目录不应被追踪和提交的机制。开发者通过编写模式匹配规则，告知Git在执行`git add`、`git status`等命令时自动跳过符合条件的文件。这套机制的核心载体是`.gitignore`文件，它以纯文本格式存储，每行描述一条匹配规则。

`.gitignore`的设计来源于Git早期开发（约2005年）时，Linus Torvalds意识到编译产物、操作系统缓存文件和IDE配置等垃圾文件会污染代码仓库。忽略规则让仓库只保留真正需要版本管理的源文件，避免`git status`输出中充斥无关文件，也防止误提交包含本地密钥或数据库密码的配置文件。

在实际工程中，一个Node.js项目如果没有忽略规则，`node_modules/`目录可能包含数万个文件，单次`git add .`就会将数百MB的依赖包永久写入提交历史，导致仓库体积膨胀且几乎无法恢复。忽略规则使这类问题从根本上得到避免。

---

## 核心原理

### 模式语法与匹配规则

`.gitignore`采用glob模式（而非正则表达式）进行文件路径匹配。以下是精确的语法规范：

- `*` 匹配除`/`之外的任意字符序列，例如`*.log`匹配所有`.log`结尾的文件。
- `**` 匹配包含`/`的任意路径，例如`**/temp`匹配任意子目录下的`temp`文件夹。
- `?` 匹配单个非`/`字符，例如`file?.txt`可匹配`file1.txt`但不匹配`file10.txt`。
- 以`/`结尾的规则只匹配目录，例如`build/`只忽略名为`build`的目录，而不忽略名为`build`的文件。
- 以`!`开头的规则表示**取反**，即重新追踪之前被忽略的文件，例如先写`*.log`再写`!important.log`，可以忽略所有日志但保留`important.log`。
- 以`#`开头的行为注释，不参与匹配。

规则的**位置影响作用域**：`.gitignore`中不含`/`的规则（如`*.txt`）会递归匹配所有子目录；含有`/`的规则（如`config/secrets.yml`）则相对于`.gitignore`所在目录进行匹配。

### 规则优先级与多文件层级

Git支持在仓库的不同层级放置多个`.gitignore`文件，优先级规则如下：

1. 命令行参数`--exclude`指定的规则优先级最高。
2. 与被忽略文件**同目录**的`.gitignore`优先级高于父目录的`.gitignore`。
3. 仓库根目录的`.gitignore`适用于整个项目。
4. 全局配置文件（`~/.gitignore_global`）的优先级最低，作用于该用户的所有仓库。

**后写的规则覆盖先写的规则**：若`.gitignore`中第3行写`*.log`，第7行写`!debug.log`，则`debug.log`不会被忽略，因为第7行的取反规则在后面生效。

### 全局配置：`~/.gitignore_global`

全局忽略规则存储在用户主目录下，通过以下命令配置：

```bash
git config --global core.excludesFile ~/.gitignore_global
```

全局配置的典型用途是忽略操作系统或IDE生成的文件，例如macOS的`.DS_Store`、Windows的`Thumbs.db`、JetBrains IDE生成的`.idea/`目录等。这些文件与具体项目无关，不应出现在项目级`.gitignore`中（否则会将个人环境偏好强制推送给所有协作者）。

Git还支持第三种忽略规则存储位置：仓库内的`.git/info/exclude`文件，它仅对本地生效且不会被提交，适合存储只对自己有意义的临时忽略规则。

### 已追踪文件的特殊处理

**忽略规则对已追踪文件无效**。若某文件已经被`git add`并提交过，即使之后在`.gitignore`中添加对它的匹配规则，Git仍会继续追踪它的变更。要使忽略规则对已追踪文件生效，必须先执行：

```bash
git rm --cached <文件路径>
```

此命令将文件从暂存区（Index）移除但保留工作区的实际文件，之后`.gitignore`规则才能正常生效。

---

## 实际应用

**Python项目**：典型`.gitignore`会包含`__pycache__/`、`*.pyc`、`.env`、`venv/`、`dist/`和`*.egg-info/`。其中`.env`文件通常存储`DATABASE_URL`、`SECRET_KEY`等敏感环境变量，绝对不能提交到公共仓库。

**Java Maven项目**：需要忽略`target/`目录（Maven编译输出）和`*.class`文件。若使用IntelliJ IDEA，`.idea/`目录和`*.iml`文件应写入全局忽略规则，而非项目`.gitignore`，因为Eclipse用户有自己不同的IDE产物。

**前端项目**：`node_modules/`必须忽略，但`package-lock.json`或`yarn.lock`**不应忽略**——这是常见错误，锁文件记录了精确的依赖版本，对团队协作至关重要。

**验证忽略规则是否生效**：使用命令`git check-ignore -v <文件路径>`，Git会输出哪一条规则、在哪个`.gitignore`文件的第几行命中了该文件，例如：

```
.gitignore:3:*.log    debug.log
```

---

## 常见误区

**误区一：取反规则可以恢复被父规则忽略的整个目录内的文件**

若父规则是`logs/`（忽略整个目录），则`!logs/important.log`**不会生效**。这是Git的明确设计限制：一旦整个目录被忽略，Git不再递归检查目录内容，因此目录内的取反规则无法命中任何文件。解决办法是将父规则改为`logs/*`（忽略目录内的文件而非目录本身），再写`!logs/important.log`。

**误区二：`.gitignore`可以删除已提交的敏感文件**

将密码文件加入`.gitignore`后，虽然新的变更不再被追踪，但历史提交中的敏感数据仍然存在于Git对象数据库中，任何人执行`git log`并检出旧提交都能找回该文件。真正清除历史中的敏感文件需要使用`git filter-branch`或`BFG Repo-Cleaner`工具重写提交历史。

**误区三：`gitignore.io`生成的模板可以直接全部使用**

`gitignore.io`（现为`toptal.com/developers/gitignore`）生成的模板通常包含大量冗余规则。例如对于一个纯Python项目，模板可能混入Visual Studio、Eclipse等与项目完全无关的规则，增加维护负担。建议只保留项目实际使用的语言、构建工具和IDE对应的规则段落。

---

## 知识关联

忽略规则建立在**Git工作区与暂存区的三区模型**基础之上——只有理解文件存在"未追踪（Untracked）"、"已追踪（Tracked）"、"已暂存（Staged）"三种状态，才能准确理解为何`git rm --cached`是解除追踪的必要步骤，以及为何忽略规则无法影响已追踪文件。

掌握忽略规则后，开发者可以进一步学习**Git属性文件（`.gitattributes`）**，它同样使用glob模式，但控制的不是是否追踪，而是文件的换行符处理（`text=auto`）、合并策略（`merge=ours`）和差异对比方式（`diff=word`）等行为——与`.gitignore`并列构成Git的两大模式匹配配置体系。