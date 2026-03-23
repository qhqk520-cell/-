# Git协作指南 - 双助手佛学项目

## 📦 项目状态
- ✅ Git仓库已初始化
- ✅ 所有文件已提交
- ⏳ 等待推送到远程仓库

## 🔗 连接方案（选择一种）

### 方案1：GitHub/GitLab远程仓库（推荐）
**步骤：**
1. 在GitHub/GitLab创建新仓库
2. 添加远程地址：`git remote add origin <仓库URL>`
3. 推送代码：`git push -u origin master`

**优点：**
- 自动同步
- 版本控制
- 冲突解决
- 历史记录

### 方案2：共享网络目录
**步骤：**
1. 将 `佛学项目` 目录设为网络共享
2. gpt4o-mini实例挂载该共享
3. 双方直接读写文件

**要求：**
- 网络互通
- 文件权限配置

### 方案3：手动文件传输
**步骤：**
1. 我打包文件发给你
2. 你上传到gpt4o-mini实例
3. 定期同步更改

## 🚀 快速开始（Git方案）

### 对于gpt4o-mini助手：
```bash
# 1. 克隆仓库（创建后）
git clone <仓库URL> 佛学项目

# 2. 进入目录
cd 佛学项目

# 3. 确认连接
编辑 collaboration/status.json
将 "gpt4o-mini" 状态改为 "在线"

# 4. 提交更改
git add collaboration/status.json
git commit -m "gpt4o-mini助手上线"
git push
```

### 对于我（deepseek-chat）：
```bash
# 1. 拉取更新
git pull

# 2. 检查状态
查看 collaboration/status.json

# 3. 开始协作
```

## 📁 目录结构说明
```
佛学项目/
├── README.md              # 项目概述
├── WELCOME_gpt4o-mini.md # 欢迎指南
├── GIT_COLLABORATION_GUIDE.md # 本文件
└── collaboration/        # 协作目录
    ├── status.json      # 状态文件
    ├── 协作协议.md      # 协作规则
    └── 给gpt4o-mini助手的消息.md # 初始消息
```

## 🔄 工作流程
1. **拉取最新代码**：`git pull`
2. **处理任务**：编辑相关文件
3. **提交更改**：`git add . && git commit -m "描述"`
4. **推送更新**：`git push`
5. **通知对方**：通过状态文件或消息文件

## ⚠️ 冲突避免
1. 不同助手处理不同文件/目录
2. 频繁拉取更新
3. 小步提交，避免大改动
4. 使用 `git status` 检查状态

## 📅 建议分工
### 第一阶段：项目规划
- **deepseek-chat**：项目范围定义、总体架构
- **gpt4o-mini**：参考资料收集、工具调研

### 第二阶段：研究执行
- 按主题分工：经典文献、核心概念、现代应用
- 定期交换成果，互相评审

## 🆘 问题解决
1. **Git冲突**：使用 `git mergetool`
2. **连接问题**：检查网络/权限
3. **同步延迟**：设置定时拉取（cron）

## 📞 紧急联系
如果Git不可用，可通过：
1. **状态文件**：`collaboration/status.json`
2. **消息文件**：`collaboration/紧急消息.md`
3. **通过你中转**：人工同步

---
**下一步行动**：
1. 请创建GitHub/GitLab仓库
2. 提供仓库URL
3. 我将推送代码
4. 通知gpt4o-mini助手克隆仓库

**或**：如果选择其他方案，请告知具体实施方式。