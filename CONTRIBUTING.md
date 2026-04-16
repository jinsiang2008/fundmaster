# 贡献指南

感谢您对 FundMaster 的关注！

## 🤝 如何贡献

### 报告 Bug
1. 在 Issues 中搜索是否已有相同问题
2. 创建新 Issue，提供详细信息：
   - 问题描述
   - 复现步骤
   - 预期行为vs实际行为
   - 环境信息（OS、Python/Node 版本）
   - 错误日志或截图

### 提交功能建议
1. 创建 Issue，标注为 `enhancement`
2. 描述功能需求和使用场景
3. 如果可能，提供设计草图或示例

### 提交代码

1. **Fork 项目**
2. **创建功能分支**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **遵循代码规范**
   - Python: PEP 8
   - TypeScript: ESLint 配置
   - 添加必要的类型注解
   - 编写清晰的注释

4. **测试您的更改**
   ```bash
   # 后端
   cd backend
   pytest  # (如果有测试)
   
   # 前端
   cd frontend
   npm run build  # 确保能编译通过
   ```

5. **提交更改**
   ```bash
   git add .
   git commit -m "feat: 添加某某功能"
   ```
   
   提交信息格式：
   - `feat:` 新功能
   - `fix:` Bug 修复
   - `docs:` 文档更新
   - `style:` 代码格式调整
   - `refactor:` 重构
   - `perf:` 性能优化
   - `test:` 测试相关

6. **推送并创建 Pull Request**
   ```bash
   git push origin feature/amazing-feature
   ```

## 📋 代码规范

### Python (Backend)
- 使用 Type Hints
- 函数和类添加 Docstring
- 每个文件顶部添加模块说明
- 异常处理要具体
- 使用 async/await 处理 I/O 操作

示例：
```python
async def get_fund_info(fund_code: str) -> Optional[FundBasicInfo]:
    """
    Get fund basic information.
    
    Args:
        fund_code: 6-digit fund code
        
    Returns:
        FundBasicInfo if found, None otherwise
    """
    try:
        # Implementation
        pass
    except Exception as e:
        logger.error(f"Failed to get fund info: {e}")
        return None
```

### TypeScript (Frontend)
- 使用明确的类型定义
- 组件使用函数式写法
- Props 使用 interface 定义
- 使用自定义 Hooks 复用逻辑

示例：
```typescript
interface FundCardProps {
  fund: FundBasicInfo;
  onClick?: () => void;
}

export function FundCard({ fund, onClick }: FundCardProps) {
  // Implementation
}
```

## ⚠️ 注意事项

1. **不要提交敏感信息**
   - API Keys
   - 个人数据
   - 生产环境配置

2. **测试您的更改**
   - 确保现有功能不受影响
   - 新功能有基本的测试覆盖

3. **更新文档**
   - 新 API 端点需要在 README 中说明
   - 重大更改需要更新文档

## 📬 联系

有任何问题欢迎创建 Issue 讨论！
