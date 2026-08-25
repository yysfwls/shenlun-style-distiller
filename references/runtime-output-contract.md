# 运行产物规范

本规范适用于普通写作、双作者比较和成稿核查；新作者蒸馏使用 `output-contract.md`。

## 保存位置

用户指定路径时优先使用。用户未指定且当前工作区可写时，使用：

```text
outputs/shenlun-style-distiller/<YYYYMMDD-task-slug>/
```

`task-slug` 使用简短 ASCII 小写词和连字符，例如 `2026-zhejiang-a-electricity-bailu`。不得写入 Skill 安装目录。目录重名时创建 `-v2`、`-v3`，不覆盖旧结果。当前环境不可写时，在对话中完整交付并说明未保存文件。

简短解释、单个判断或用户明确要求只在对话中回答时，不必创建目录。

## 单作者应用

```text
<task>/
├── source-manifest.md      # 文件名、页数、读取方式；不复制原始付费资料
├── 01-task-analysis.md     # 题意、中心论点、分论点
├── 02-material-map.md      # 材料事实与论证功能
├── 03-essay.md             # 仅标题和纯净成稿
├── 04-validation.md        # 题意、事实、字数、原创性和规则执行
└── result.md               # 面向用户的合并交付
```

用户只要求提纲时可省略 `03-essay.md`，但 `result.md` 仍需反映实际交付内容。不要创建空文件。

## 双作者比较

```text
<task>/
├── source-manifest.md
├── bailu/
│   ├── analysis.md
│   ├── essay.md            # 仅在用户要求成稿时生成
│   └── validation.md
├── yuandong/
│   ├── analysis.md
│   ├── essay.md            # 仅在用户要求成稿时生成
│   └── validation.md
└── comparison.md
```

两位老师必须独立完成后再比较，不能先写一个混合提纲再拆分。

## 成稿核查

```text
<task>/
├── source-manifest.md
├── review.md
└── revised-essay.md        # 仅在用户要求修改时生成
```

默认只诊断，不擅自重写。

## 成稿验证

验证分开报告：题目要求、材料忠实度、中心与分论点、论据功能、字数、原创性、老师规则执行、机械套用风险。不得用单一“像不像”分数代替。

完成成稿后运行：

```bash
python3 scripts/validate_essay.py 03-essay.md --min-chars 1000 --max-chars 1200
```

机械脚本只检查字符数、结构和明显占位符；事实与题意仍需人工推理核查。
