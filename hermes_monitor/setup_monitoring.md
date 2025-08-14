# 🎯 Hermès 产品监控系统设置指南

## 📋 概述
本服务持续监控 Hermès 官网新品，当发现符合您关注列表条件的产品时自动发送邮件通知。

## 🔧 快速设置

### 系统要求
- **Python**: 3.7+ (推荐 3.9+)
- **操作系统**: Windows 10+, macOS 10.14+, Ubuntu 18.04+
- **内存**: 至少 2GB RAM
- **网络**: 稳定互联网连接
- **浏览器**: Chrome 或 Chromium (自动下载)

### 1. 安装依赖
```bash
pip3 install selenium webdriver-manager
```

### 1.1 可选依赖（推荐）
```bash
pip3 install selenium webdriver-manager requests beautifulsoup4 lxml
```

### 2. 配置邮件设置

#### Gmail 设置：
1. **开启两步验证** 您的Google账户
2. **生成应用专用密码**：
   - 访问 [Google账户安全](https://myaccount.google.com/security)
   - 在"登录Google"下 -> "应用专用密码"
   - 选择"邮件"和"其他"（命名为"Hermès监控"）
   - 复制16位密码

#### 更新 config.json：
```json
{
  "email": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "your_email@gmail.com",
    "sender_password": "your_app_password_here",
    "recipient_emails": [
      "your_email@gmail.com"
    ],
    "subject_prefix": "[Hermès监控]"
  }
}
```

### 3. 配置关注列表

#### 在 config.json 中更新要监控的产品：
```json
{
  "watchlist": {
    "products": [
      {
        "name_contains": "Birkin",
        "max_price": 100000,
        "min_price": 50000
      },
      {
        "name_contains": "Kelly",
        "max_price": 90000,
        "min_price": 40000
      },
      {
        "name_contains": "Picotin",
        "max_price": 50000,
        "min_price": 20000
      }
    ]
  }
}
```

### 4. 开始监控

#### 选项A: 持续监控（推荐）
```bash
python3 hermes_monitor.py
```

#### 选项B: 单次检查
```bash
python3 hermes_monitor.py --single
```

## ⚙️ 配置选项

### 监控设置
```json
{
  "monitoring": {
    "check_interval_minutes": 30,
    "urls": [
      "https://www.hermes.com/hk/en/category/women/bags-and-small-leather-goods/bags-and-clutches/"
    ]
  }
}
```

### 邮件设置
| 参数 | 描述 | 示例 |
|-----------|-------------|---------|
| `smtp_server` | 邮件服务器 | "smtp.gmail.com" |
| `smtp_port` | 服务器端口 | 587 |
| `sender_email` | 您的邮箱 | "your_email@gmail.com" |
| `sender_password` | 应用专用密码 | "abcd efgh ijkl mnop" |
| `recipient_emails` | 收件人列表 | ["email1@gmail.com", "email2@gmail.com"] |
| `subject_prefix` | 邮件前缀 | "[Hermès监控]" |

### Watchlist Format
```json
{
  "watchlist": {
    "products": [
      {
        "name_contains": "keyword",
        "max_price": 100000,
        "min_price": 0
      }
    ]
  }
}
```

**参数说明：**
- `name_contains`: 产品名称包含的关键词
- `max_price`: 最高价格（港币）
- `min_price`: 最低价格（港币）

## 📧 Email Provider Setup

### Gmail (Recommended)
- **SMTP**: smtp.gmail.com:587
- **Password**: Use App Password (16 chars)

### Outlook/Hotmail
- **SMTP**: smtp-mail.outlook.com:587
- **Password**: Your email password

### Other Providers
- **QQ Mail**: smtp.qq.com:587
- **163 Mail**: smtp.163.com:587
- **Yahoo**: smtp.mail.yahoo.com:587

## 🚀 Running the Service

### Background Mode (Linux/Mac)
```bash
# Run in background
nohup python3 hermes_monitor.py > result/monitor.log 2>&1 &

# Check status
tail -f result/monitor.log
```

### Windows Service
```bash
# Use Task Scheduler to run on startup
# Command: python3 C:\path\to\hermes_monitor.py
```

### Docker (Optional)

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY .. .
RUN pip install selenium webdriver-manager
CMD ["python", "hermes_monitor.py"]
```

## 📊 Output Files

### Monitoring Results
- `result/last_products.json` - Last seen products
- `result/monitor.log` - Detailed logs
- `result/monitoring_report_[timestamp].json` - Full reports

### Email Reports Include:
- 📦 New products found
- 🎯 Watchlist matches
- 💰 Price ranges
- 🔗 Direct product links
- 📸 Product images

## 🔍 Monitoring Features

### ✅ What it monitors:
- New product additions
- Price changes on existing products
- Product availability changes
- Watchlist keyword matches

### 📧 Notification triggers:
- New products matching watchlist
- Products returning to stock
- Price drops in watchlist range

### 📈 Tracking includes:
- Product names and SKUs
- Current prices in HKD
- High-resolution images
- Direct product URLs
- Timestamp of detection

## 📋 完整配置文件示例

创建 `config.json` 文件：

```json
{
  "email": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "your_email@gmail.com",
    "sender_password": "your_app_password_here",
    "recipient_emails": [
      "your_email@gmail.com"
    ],
    "subject_prefix": "[Hermès监控]"
  },
  "monitoring": {
    "check_interval_minutes": 30,
    "urls": [
      "https://www.hermes.com/hk/en/category/women/bags-and-small-leather-goods/bags-and-clutches/",
      "https://www.hermes.com/hk/en/category/women/bags-and-small-leather-goods/small-leather-goods/"
    ]
  },
  "watchlist": {
    "products": [
      {
        "name_contains": "Birkin",
        "max_price": 100000,
        "min_price": 50000
      },
      {
        "name_contains": "Kelly",
        "max_price": 90000,
        "min_price": 40000
      },
      {
        "name_contains": "Picotin",
        "max_price": 50000,
        "min_price": 20000
      }
    ]
  }
}
```

## 🔐 安全建议

### 密码安全
- 使用应用专用密码，不要直接使用邮箱密码
- 将配置文件权限设置为600（仅自己可读）
```bash
chmod 600 config.json
```

### 日志安全
- 定期清理日志文件
- 不要在日志中记录敏感信息
- 建议每周清理一次旧日志

### 网络安全
- 使用HTTPS协议
- 定期更新依赖包
- 监控异常访问模式

## 🛠️ 故障排除

### 常见问题：

1. **邮件发送失败**：
   - 检查应用密码是否正确
   - 确保已启用2FA
   - 验证收件人邮箱地址
   - 检查SMTP服务器设置

2. **无法找到产品**：
   - 检查网站结构是否变更
   - 增加页面等待时间
   - 验证URL是否可访问
   - 检查网络连接

3. **内存问题**：
   - 降低检查频率
   - 清理旧日志文件
   - 使用单次检查模式
   - 考虑使用无头模式

4. **验证码问题**：
   - 降低访问频率
   - 使用代理IP轮换
   - 增加随机延迟

### 调试模式：
```bash
# 运行调试日志
python3 hermes_monitor.py --single

# 查看详细日志
tail -f result/monitor.log
```

### 性能优化：
```bash
# 使用无头浏览器（推荐）
python3 hermes_monitor.py --headless

# 降低频率减少被封风险
python3 hermes_monitor.py --interval=60
```

### 停止服务：
```bash
# 查找进程
ps aux | grep hermes_monitor.py
kill [PID]

# 一键停止
pkill -f hermes_monitor.py
```

## 📱 Mobile Notifications

### iPhone/iPad:
- Use Gmail app for notifications
- Enable push notifications
- Set VIP for monitoring email

### Android:
- Use Gmail app
- Configure notification sounds
- Set priority for monitoring emails

## 🔄 Service Management

### Check Status:
```bash
# View latest logs
tail -20 result/monitor.log

# Check if running
ps aux | grep hermes_monitor
```

### Restart Service:
```bash
# Stop old process
pkill -f hermes_monitor.py

# Start new process
python3 hermes_monitor.py
```

## 🚀 快速开始脚本

创建 `setup.sh` 一键配置脚本：

```bash
#!/bin/bash
echo "🎯 Hermès 监控系统快速设置"

# 创建目录
mkdir -p result logs

# 安装依赖
echo "📦 安装依赖..."
pip3 install selenium webdriver-manager requests beautifulsoup4 lxml

# 创建示例配置文件
if [ ! -f config.json ]; then
    echo "⚙️ 创建配置文件..."
    cat > config.json << 'EOF'
{
  "email": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "your_email@gmail.com",
    "sender_password": "your_app_password_here",
    "recipient_emails": [
      "your_email@gmail.com"
    ],
    "subject_prefix": "[Hermès监控]"
  },
  "monitoring": {
    "check_interval_minutes": 30,
    "urls": [
      "https://www.hermes.com/hk/en/category/women/bags-and-small-leather-goods/bags-and-clutches/"
    ]
  },
  "watchlist": {
    "products": [
      {
        "name_contains": "Birkin",
        "max_price": 100000,
        "min_price": 50000
      }
    ]
  }
}
EOF
    chmod 600 config.json
    echo "✅ 配置文件已创建，请编辑 config.json 设置您的邮箱信息"
else
    echo "⚠️ 配置文件已存在"
fi

echo "🎉 设置完成！运行 python3 hermes_monitor.py 开始监控"
```

运行设置：
```bash
chmod +x setup.sh
./setup.sh
```

## 💡 高级功能

### 自定义监控
- 修改 `config.json` 支持不同产品类别
- 添加多个地区URL
- 自定义邮件模板
- 集成webhook通知

### 扩展集成示例
- **Slack通知**：通过webhook发送消息
- **Telegram机器人**：使用Bot API
- **Discord频道**：webhook集成
- **企业微信**：群机器人消息
- **钉钉**：自定义机器人

### 批量监控配置
```json
{
  "monitoring": {
    "urls": [
      "https://www.hermes.com/hk/en/category/women/bags-and-small-leather-goods/",
      "https://www.hermes.com/us/en/category/women/bags-and-small-leather-goods/",
      "https://www.hermes.com/sg/en/category/women/bags-and-small-leather-goods/"
    ],
    "regions": ["hk", "us", "sg"]
  }
}
```

## 📊 监控报告示例

### 邮件报告格式
```
📧 [Hermès监控] 发现 3 个新产品
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 搜索关键词: Birkin
💰 价格范围: HKD 50,000 - 100,000
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📦 新产品 #1
🏷️ 名称: Hermès Birkin 30 Epsom
💵 价格: HKD 85,000
🔗 链接: https://www.hermes.com/...
📸 图片: [自动加载]
⏰ 发现时间: 2024-01-15 14:30:25

📦 新产品 #2
🏷️ 名称: Hermès Birkin 25 Togo
💵 价格: HKD 78,000
🔗 链接: https://www.hermes.com/...
📸 图片: [自动加载]
⏰ 发现时间: 2024-01-15 14:30:25
```

## 🔄 版本更新日志

### v1.2.0 (2024-01-15)
- ✅ 添加无头浏览器支持
- ✅ 优化内存使用
- ✅ 增加错误重试机制
- ✅ 支持多地区监控

### v1.1.0 (2024-01-10)
- ✅ 添加产品图片显示
- ✅ 改进邮件格式
- ✅ 增加价格变化通知
- ✅ 支持代理配置

### v1.0.0 (2024-01-05)
- ✅ 基础监控功能
- ✅ 邮件通知
- ✅ 配置文件支持
- ✅ 日志记录