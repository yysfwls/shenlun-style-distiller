# 研究产物规范

本规范只适用于蒸馏或更新作者 Writing DNA。普通写作、比较和核查使用 `runtime-output-contract.md`。

## 目录结构

每位作者在私有研究工作区独立保存。准备公开包时，只复制 `reports/` 与 `Writing-DNA.md`，排除 `raw/`、`prompts/`、`materials/`、`commentary/`、`_meta/`、`_annotations/` 等可回溯原文的目录。公开包内部路径使用 ASCII，中文名称写在文档正文：

```text
profiles/<author-slug>/
├── raw/                         # 原始范文，不覆盖
├── prompts/                     # 题目
├── materials/                   # 给定材料
├── commentary/                  # 讲解、批注、评分，可选
├── _meta/                       # 客观元数据
├── _annotations/                # 使用统一 codebook 的分析标注
├── reports/
│   ├── language-dna.md
│   ├── structure-templates.md
│   ├── thesis-generation.md
│   ├── evidence-strategy.md
│   ├── cognitive-framework.md
│   ├── rule-evidence-index.md
│   └── application-checklist.md
└── Writing-DNA.md
```

双作者结果另设：

```text
comparisons/
├── same-prompt-comparison.md
├── layer-difference-matrix.md
└── style-selection-guide.md
```

不存在的原始材料目录不必创建空占位，但必须在报告中记录缺失项。

## Writing DNA 必备内容

`Writing-DNA.md` 是执行入口，不复制五份报告全文。它必须包含：

1. 版本、日期、作者、语料数量和适用范围；
2. 缺失材料、采样偏差和其他限制；
3. 跨题稳定的高置信度规则；
4. 按题型路由的结构与立意规则；
5. 五层分析摘要；
6. 高置信度 Do / Don't；
7. 生成前决策顺序；
8. 成稿后的检查表；
9. 低置信度假设和待补证据；
10. 指向 `rule-evidence-index.md` 的规则编号。

每条执行规则使用证据索引中的稳定编号，例如 `BL-L3-004`。`Writing-DNA.md` 必须直接显示编号并指向 `rule-evidence-index.md`；不得只使用与证据脱节的普通序号。详细例证留在分层报告和证据索引中，避免总入口过长。

## 规则证据索引与应用检查

索引至少记录规则编号、作者、案例编号或覆盖统计、证据摘要、反例和置信度。引用原文只保留判断所需的短片段，不汇编大段范文。公开数据不得包含原始文件名、完整开头结尾句、连续长段原文或本地绝对路径。

应用检查必须分开评价题目要求、材料忠实度、论点质量、论据功能、规则执行、机械套用、与语料的高度近似，以及风格是否损害清晰度或事实准确性。不得用单一的“像不像”分数代替这些维度。
