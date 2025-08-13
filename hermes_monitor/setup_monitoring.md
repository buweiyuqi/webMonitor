# 🎯 Hermès Product Monitoring Service Setup Guide

## 📋 Overview
This service continuously monitors the Hermès website for new products and sends email notifications when products matching your watchlist criteria appear.

## 🔧 Quick Setup

### 1. Install Dependencies
```bash
pip3 install selenium webdriver-manager
```

### 2. Configure Email Settings

#### For Gmail:
1. **Enable 2-factor authentication** on your Google account
2. **Generate App Password**:
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Under "Signing in to Google" -> "App passwords"
   - Select "Mail" and "Other" (name it "Hermès Monitor")
   - Copy the 16-character password

#### Update config.json:
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

### 3. Configure Watchlist

#### Update products to watch in config.json:
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

### 4. Start Monitoring

#### Option A: Continuous Monitoring (Recommended)
```bash
python3 hermes_monitor.py
```

#### Option B: Single Check
```bash
python3 hermes_monitor.py --single
```

## ⚙️ Configuration Options

### Monitoring Settings
```json
{
  "monitoring": {
    "check_interval_minutes": 30,  # Check every 30 minutes
    "urls": [
      "https://www.hermes.com/hk/en/category/women/bags-and-small-leather-goods/bags-and-clutches/"
    ]
  }
}
```

### Email Settings
| Parameter | Description | Example |
|-----------|-------------|---------|
| `smtp_server` | Email server | "smtp.gmail.com" |
| `smtp_port` | Server port | 587 |
| `sender_email` | Your email | "your_email@gmail.com" |
| `sender_password` | App password | "abcd efgh ijkl mnop" |
| `recipient_emails` | Recipients | ["email1@gmail.com", "email2@gmail.com"] |
| `subject_prefix` | Email prefix | "[Hermès监控]" |

### Watchlist Format
```json
{
  "watchlist": {
    "products": [
      {
        "name_contains": "keyword",    # Part of product name
        "max_price": 100000,          # Maximum price in HKD
        "min_price": 0                # Minimum price in HKD
      }
    ]
  }
}
```

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

## 🛠️ Troubleshooting

### Common Issues:

1. **Email not sending**:
   - Check app password is correct
   - Ensure 2FA is enabled
   - Verify recipient emails

2. **Products not found**:
   - Check website structure changes
   - Increase wait times in code
   - Verify URLs are accessible

3. **Memory issues**:
   - Reduce check frequency
   - Clear old log files
   - Use single check mode

### Debug Mode:
```bash
# Run with debug logging
python3 hermes_monitor.py --single
```

### Stop Service:
```bash
# Find process
ps aux | grep hermes_monitor.py
kill [PID]
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

## 💡 Advanced Usage

### Custom Monitoring:
- Modify `config.json` for different categories
- Add multiple URLs for different regions
- Customize email templates
- Add webhook notifications

### Integration Examples:
- Slack notifications
- Telegram bots
- Discord webhooks
- Custom API endpoints