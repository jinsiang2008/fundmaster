# 安全指南

## 🔑 API Key 管理

### 重要原则

1. **永远不要将 API Key 提交到版本控制系统**
2. **永远不要在代码中硬编码 API Key**
3. **定期轮换密钥**
4. **使用最小权限原则**

### 正确的做法

✅ **使用 .env 文件**（已被 .gitignore 排除）
```bash
# backend/.env
DEEPSEEK_API_KEY=sk-your-real-key-here
```

✅ **.env.example 只包含占位符**
```bash
# backend/.env.example
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

❌ **错误做法**
```python
# 不要这样做！
api_key = "sk-4b161dbc969a4606896e2b99804d5eab"
```

## 🛡️ 环境隔离

### 开发环境
- 使用测试用的 API Key
- 设置较低的速率限制
- `.env` 文件仅在本地

### 生产环境
- 使用环境变量注入
- 使用密钥管理服务（AWS Secrets Manager、Azure Key Vault 等）
- 启用 API Key 轮换策略

## 🔍 检查泄露

如果不小心将 API Key 提交到了 Git：

1. **立即失效密钥**：在 DeepSeek 平台删除该密钥
2. **生成新密钥**
3. **使用 git-filter-branch 清除历史记录**
4. **强制推送清理后的历史**

## 📝 最佳实践

### Git 提交前检查
```bash
# 检查 .env 文件是否被忽略
git status | grep ".env"  # 应该看不到 .env

# 检查是否有 API Key 泄露
git diff | grep -i "api.key\|sk-"
```

### 团队协作
- 每个开发者使用自己的 API Key
- 通过安全渠道共享密钥（如 1Password、LastPass）
- 不要在聊天工具中发送密钥

## 🚨 如果密钥泄露

1. 立即在 https://platform.deepseek.com/api_keys 删除泄露的密钥
2. 生成新密钥
3. 更新本地 `.env` 文件
4. 通知团队成员
5. 检查是否有异常的 API 使用

## 📞 联系

如果发现安全问题，请通过 Issue 报告（不要在 Issue 中包含敏感信息）。
