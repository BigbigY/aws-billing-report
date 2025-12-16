# AWS每日账单报告系统

这个项目用于每日自动获取AWS Cost Explorer的前5天(因为账户延迟问题)账单数据，按服务分组，并与前一天进行对比，然后通过邮件发送报告。

## 功能特性

- 📊 获取AWS Cost Explorer的每日账单数据
- 🔍 按服务分组显示成本
- 📈 对比昨天和前天的账单变化
- 🎨 增长用红色标记，下降用绿色标记
- 📧 自动发送HTML格式的邮件报告

## 安装

1. 克隆或下载项目

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 配置

### 方法1: 环境变量

###
账单类型变量：
日账单（默认）
- name: REPORT_TYPE
  value: "daily"
月账单
- name: REPORT_TYPE
  value: "monthly"

#### 单个AWS账号配置

设置以下环境变量：

```bash
# AWS配置
export AWS_ACCESS_KEY_ID="your-access-key-id"
export AWS_SECRET_ACCESS_KEY="your-secret-access-key"
export AWS_REGION="us-east-1"

# 邮件配置
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USERNAME="your-email@gmail.com"
export SMTP_PASSWORD="your-app-password"  # Gmail需要使用应用专用密码
export EMAIL_FROM="your-email@gmail.com"
export EMAIL_TO="recipient1@example.com,recipient2@example.com"
```

#### 多个AWS账号配置

使用 `AWS_ACCOUNTS` 环境变量配置多个账号：

```bash
export AWS_ACCOUNTS='[
  {
    "access_key_id": "AKIA...",
    "secret_access_key": "xxx...",
    "region": "us-east-1",
    "account_name": "生产环境"
  },
  {
    "access_key_id": "AKIA...",
    "secret_access_key": "yyy...",
    "region": "us-west-2",
    "account_name": "测试环境"
  }
]'

# 邮件配置
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USERNAME="your-email@gmail.com"
export SMTP_PASSWORD="your-app-password"
export EMAIL_FROM="your-email@gmail.com"
export EMAIL_TO="recipient1@example.com,recipient2@example.com"
```

**注意：** `account_name` 字段是可选的，如果不提供，将使用默认名称（如"账号1"、"账号2"）。

### 方法2: 使用 accounts.json 文件（推荐）

创建或编辑 `accounts.json` 文件，配置AWS账号信息：

```json
[
    {
        "access_key_id": "AKIA...",
        "secret_access_key": "xxx...",
        "region": "us-east-1",
        "account_name": "生产环境"
    },
    {
        "access_key_id": "AKIA...",
        "secret_access_key": "yyy...",
        "region": "us-west-2",
        "account_name": "测试环境"
    }
]
```

**注意：**
- 默认配置文件为 `accounts.json`，可通过环境变量 `AWS_ACCOUNTS_FILE` 指定其他文件路径
- `account_name` 字段是可选的，如果不提供，将使用默认名称
- 建议将 `accounts.json` 添加到 `.gitignore` 中，避免泄露敏感信息

## AWS权限要求

您的AWS账户需要以下权限：

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ce:GetCostAndUsage"
            ],
            "Resource": "*"
        }
    ]
}
```

## 使用方法

### 手动运行

```bash
python main.py
```

### 定时任务（Cron）

添加到crontab，每天上午9点运行：

```bash
# 编辑crontab
crontab -e

# 添加以下行（根据实际路径修改）
0 9 * * * /usr/bin/python3 main.py >> /path/to/logs/aws-billing.log 2>&1
```

### Docker方式

创建 `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

## 邮件服务配置

### Gmail配置

1. 启用两步验证
2. 生成应用专用密码：https://myaccount.google.com/apppasswords
3. 使用应用专用密码作为 `SMTP_PASSWORD`

### 其他邮件服务

修改 `config.py` 中的 `SMTP_SERVER` 和 `SMTP_PORT`：
- Outlook: `smtp-mail.outlook.com:587`
- 163邮箱: `smtp.163.com:465` 或 `smtp.163.com:25`
- QQ邮箱: `smtp.qq.com:587`

## 报告格式

报告包含：
- 总账单对比（昨天 vs 前天）
- 按服务分组的详细账单
- 每个服务的变化量和变化百分比
- 颜色标记：红色=增长，绿色=下降

## 故障排除

1. **AWS权限错误**: 确保IAM用户/角色有 `ce:GetCostAndUsage` 权限
2. **邮件发送失败**: 检查SMTP配置和密码是否正确
3. **数据为空**: 检查日期范围，确保有账单数据
4. **时区问题**: 代码使用UTC时区，确保AWS账户时区设置正确

