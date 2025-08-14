# Hermès 自动购买功能使用指南

## 功能概述

自动购买功能在检测到匹配的商品时，会自动登录账号并尝试将商品添加到购物车，启动结账流程。

## 配置步骤

### 1. 启用自动购买功能
编辑 `config.json` 文件：

```json
{
  "purchase": {
    "enabled": true,
    "login_credentials": {
      "email": "your_email@example.com",
      "password": "your_password"
    },
    "purchase_settings": {
      "max_price": 100000,
      "timeout_seconds": 60,
      "take_screenshots": true
    }
  }
}
```

### 2. 配置说明

- `enabled`: 是否启用自动购买功能（true/false）
- `login_credentials.email`: 登录邮箱
- `login_credentials.password`: 登录密码
- `purchase_settings.max_price`: 最大购买价格限制
- `purchase_settings.timeout_seconds`: 操作超时时间（秒）
- `purchase_settings.take_screenshots`: 是否截图保存操作过程

### 3. 使用注意事项

#### 安全警告
- **请勿在配置文件中保存真实密码**，建议使用环境变量或安全存储
- **购买功能仅供学习和测试使用**，请谨慎使用
- **建议在测试环境中先验证功能**

#### 价格限制
- 系统会自动检查商品价格，超过 `max_price` 的商品不会自动购买
- 价格检查基于商品的 `price` 字段

#### 截图记录
- 所有操作步骤都会截图保存到 `result/screenshots/` 目录
- 截图文件命名格式：`操作类型_时间戳.png`

#### 购买记录
- 所有购买尝试都会记录在 `result/purchase_history.json` 文件中
- 记录包括商品信息、操作结果、时间戳等

### 4. 运行方式

#### 启动监控（带自动购买）
```bash
python hermes_monitor.py
```

#### 单次检查（带自动购买）
```bash
python hermes_monitor.py --single
```

### 5. 常见问题

#### Q: 自动购买功能安全吗？
A: 该功能需要存储登录凭据，建议仅在测试环境中使用，或修改代码使用更安全的方式存储密码。

#### Q: 如何禁用自动购买？
A: 将 `config.json` 中的 `purchase.enabled` 设置为 `false`。

#### Q: 购买流程会完成整个下单吗？
A: 目前只完成到"添加到购物车"和"进入结账页面"的步骤，不会真正完成支付。

#### Q: 如何查看购买记录？
A: 查看 `result/purchase_history.json` 文件，或使用日志查看器。

### 6. 技术细节

#### 购买流程
1. 检测匹配商品
2. 启动浏览器（非headless模式）
3. 登录账号
4. 访问商品页面
5. 添加到购物车
6. 截图保存
7. 进入结账流程
8. 记录结果

#### 错误处理
- 每一步都有超时处理
- 失败时会截图保存错误状态
- 所有错误都会记录到日志
- 不会影响主监控流程的运行

### 7. 自定义扩展

可以根据需要修改 `auto_purchase.py` 文件：
- 添加更多商品筛选条件
- 实现完整的结账流程
- 添加多账号支持
- 增加验证码处理
- 添加代理支持

### 8. 性能考虑

- 自动购买使用独立浏览器实例
- 每次购买完成后会关闭浏览器
- 截图功能可通过配置禁用以提高性能
- 购买记录会定期清理