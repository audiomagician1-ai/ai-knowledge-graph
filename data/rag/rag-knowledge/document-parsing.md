---
id: "document-parsing"
concept: "文档解析(PDF/HTML/OCR)"
domain: "ai-engineering"
subdomain: "rag-knowledge"
subdomain_name: "RAG与知识库"
difficulty: 5
is_milestone: false
tags: ["RAG"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---


# 文档解析（PDF/HTML/OCR）

## 概述

文档解析是RAG知识库构建的第一道关口，指将PDF、HTML、扫描图片等非结构化或半结构化原始文件转换为可被语言模型处理的纯文本或结构化数据的过程。不同于直接读取数据库中的结构化字段，文档解析必须处理排版噪音、字体编码、嵌套标签、表格跨行、图片内嵌文字等多种复杂情形，每一类格式都需要不同的技术路径。

PDF格式诞生于1993年Adobe公司发布的Portable Document Format规范，其设计目标是跨平台视觉一致性而非语义可提取性。这意味着PDF在物理存储层面保存的是"在坐标(x, y)处绘制字符'A'"的指令，而非"这是一段正文"的语义标注。正是这种设计使得PDF解析至今仍是工程挑战：同一份看似正常的PDF，可能因其由扫描、Word导出、LaTeX编译三种方式生成而需要三套完全不同的解析策略。

在RAG系统中，文档解析质量直接影响后续切分（Chunking）和向量化的效果。若解析阶段将表格拆散成乱序文字，或将页眉页脚混入正文，检索模型将无法找到正确的上下文窗口，导致生成答案的幻觉率显著上升。

---

## 核心原理

### PDF解析的三种技术路径

**文本层提取（Text-based PDF）**：对于由Word或LaTeX生成的"数字原生"PDF，可直接读取PDF内嵌的文本流。Python库`pdfminer.six`和`PyMuPDF`（fitz）均支持按字符级别读取坐标和字号，其中PyMuPDF的`page.get_text("blocks")`方法可以按段落块返回文本，坐标精度达到0.001个点（1 point = 1/72英寸）。此路径速度快、准确率高，但一旦遇到双栏布局，算法若仅按y坐标排序则会交叉合并两栏内容，需要额外的列检测逻辑。

**结构化解析（Structured Parsing）**：针对含有标题层级、表格、列表的PDF，工具如`pdfplumber`可提取表格的行列边界，`PDFMiner`的`LAParams`参数组（`line_margin=0.5`, `char_margin=2.0`）控制字符聚合的宽松程度，精确调整这两个参数可显著改善中文PDF中字符粘连或断裂的问题。商业方案如Adobe PDF Services API则通过分析PDF结构树（Structure Tree）直接输出带语义标签的JSON。

**扫描PDF与OCR**：完全由扫描图像组成的PDF不含任何文本流，必须走OCR路径。Tesseract OCR（由Google维护的开源项目，当前主版本为5.x）对印刷体中文识别率在标准DPI（≥300 DPI）下可达95%以上，但手写体或低分辨率图像则需改用深度学习OCR引擎，如PaddleOCR或阿里云的通义智文。OCR前的预处理包括二值化（Otsu阈值法）、去倾斜（Deskewing，通常使用霍夫变换检测文本行角度并旋转）、去噪（中值滤波）三个步骤，缺少预处理会使字符错误率从2%上升到15%以上。

---

### HTML解析的特殊挑战

HTML文档通过DOM树组织内容，解析目标是在去除`<script>`、`<style>`、广告导航等噪音的同时保留正文的段落层次。`BeautifulSoup4`库提供了基于CSS选择器的节点提取，而`Trafilatura`库则专门针对新闻与博客页面进行正文提取，其内部使用XPath规则集与评分算法（基于文本密度和链接密度两个指标）自动识别主体内容区域，在CC-News语料库上的F1得分约为0.89。

动态渲染页面（JavaScript生成内容）无法被静态解析器抓取，必须使用Playwright或Selenium驱动真实浏览器渲染后再提取`document.body.innerText`或完整HTML。此场景下性能代价显著：Playwright无头浏览器单页面渲染耗时约1-3秒，而静态解析通常在毫秒级完成。

---

### OCR与版面分析（Layout Analysis）

现代文档理解已超越纯字符识别，进入"版面分析+OCR"的两阶段流程。版面分析模型（如基于Detectron2的LayoutParser，或微软的LayoutLMv3）首先将页面分割为标题区、正文区、表格区、图注区等语义区域，再针对不同区域调用不同的后续处理。LayoutLMv3在PubLayNet数据集上的mAP（mean Average Precision）达到0.9498，能够在学术论文中准确区分公式、图表和参考文献列表。

表格是文档解析中最难处理的结构之一。PDF中的表格可能由线框构成，也可能是"无边框表格"（仅靠空白对齐）。`camelot`库处理有线框表格效果良好，但无边框表格需借助`tabula-py`的lattice和stream两种模式，或使用微软Azure Document Intelligence等云服务（其表格提取API能返回单元格的行索引、列索引和跨行跨列信息）。

---

## 实际应用

**金融报告知识库**：某券商构建研报RAG系统时，对PDF研报的解析采用"先检测是否含文本层，若有则用PyMuPDF提取，若无则调用PaddleOCR"的两分支流程。双栏PDF通过检测文本块x坐标中值（通常接近页面宽度的50%附近存在明显间隔）自动判定并分列提取，最终使得检索召回率从61%提升至79%。

**法律文书处理**：法律合同通常包含大量嵌套条款编号（如"第三条第（二）款第1项"），HTML格式的合同可通过保留`<ol>`和`<ul>`的层级关系直接还原为带缩进的Markdown列表，而扫描版合同则需要OCR后额外运行正则表达式`^（[一二三四五六七八九十百]+）`识别条款编号并重建树形结构。

**技术文档多模态解析**：对于含有大量图表的技术手册，RAG系统可对每张图表调用多模态视觉模型（如GPT-4o Vision或Qwen-VL）生成图表描述文字，再与周围文本合并存入向量库，使"如图3所示"类的引用可以被正确检索到。

---

## 常见误区

**误区一：默认所有PDF都能直接提取文字**。很多工程师在遇到`pdfminer`返回乱码或空字符时，误以为是库的bug，实际上该PDF是扫描版，根本不含文本层。正确做法是先用`PyMuPDF`检查`page.get_text()`返回的字符数，若低于阈值（如每页少于50个字符）则判定为图像PDF并切换至OCR流程。

**误区二：OCR输出即可直接入库**。OCR输出通常包含大量断行、连字符断词（英文`cog-\nnition`）和识别错误（如将"0"识别为"O"，将"1"识别为"l"）。未经后处理直接分块会导致向量化时语义破碎。标准后处理流程包括：合并跨行连字符、修复常见字符混淆对、删除置信度低于0.6的字符（Tesseract的`--oem`输出包含置信度字段）。

**误区三：HTML解析只需取`innerText`**。直接对整页调用`innerText`会将导航栏、Cookie提示、广告文字一并混入正文，导致向量嵌入质量严重下降。必须先通过版面识别或规则过滤定位主体内容节点，例如检测`<article>`、`<main>`标签，或使用内容密度算法（正文区的文本字数与超链接字数之比通常大于5:1）剥离导航噪音。

---

## 知识关联

文档解析是RAG流水线的输入端，其输出质量直接影响文本切分（Chunking）策略的选择：解析若能保留段落边界和标题层级，则切分可按语义单元进行；若解析输出为平铺文本，则只能按固定字符数切分，通常需设置10%-20%的重叠（overlap）来弥补语义断裂。

与向量检索模块的关系上，解析阶段保留的元数据（页码、章节标题、文档来源）会作为向量数据库中的`metadata`字段存储，支持混合检索时的过滤条件（如"仅检索2023年以后的报告"）。若解析丢失了这些结构信息，后续的元数据过滤和引用溯源功能将完全失效。

多模态文档理解（将图表转为文字描述后嵌入知识库）是当前RAG领域的前沿方向，依赖文档解析阶段对页面区域的精确分割作为前提。LayoutLMv3等文档理解预训练模型通过将文字、位置坐标、图像三种模态联合预训练，正在将版面分析与内容提取合并为端到端的统一流程。