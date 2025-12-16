"""
配置文件
请根据实际情况修改以下配置
"""
import os
import json

# AWS账号配置文件路径
# 可以通过环境变量 AWS_ACCOUNTS_FILE 指定，默认为 accounts.json
AWS_ACCOUNTS_FILE = os.getenv('AWS_ACCOUNTS_FILE', 'accounts.json')

def get_aws_accounts():
    """
    获取AWS账号列表
    从 accounts.json 文件或环境变量 AWS_ACCOUNTS 读取配置
    支持从文件路径或JSON字符串读取
    """
    # 首先尝试从环境变量读取（JSON字符串格式）
    aws_accounts_env = os.getenv('AWS_ACCOUNTS', '')
    if aws_accounts_env:
        try:
            accounts = json.loads(aws_accounts_env)
            if isinstance(accounts, list) and len(accounts) > 0:
                return accounts
        except json.JSONDecodeError:
            print("警告: AWS_ACCOUNTS 环境变量 JSON格式错误，尝试从文件读取")
    
    # 尝试从文件读取
    accounts_file = AWS_ACCOUNTS_FILE
    if os.path.exists(accounts_file):
        try:
            with open(accounts_file, 'r', encoding='utf-8') as f:
                accounts = json.load(f)
                if isinstance(accounts, list) and len(accounts) > 0:
                    return accounts
                else:
                    print(f"警告: {accounts_file} 文件格式错误，应为账号列表")
        except json.JSONDecodeError as e:
            print(f"警告: 读取 {accounts_file} 文件时JSON解析错误: {str(e)}")
        except Exception as e:
            print(f"警告: 读取 {accounts_file} 文件时出错: {str(e)}")
    else:
        print(f"警告: 未找到账号配置文件 {accounts_file}，请创建该文件或设置 AWS_ACCOUNTS 环境变量")
    
    return []

# 邮件配置
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.larksuite.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '465'))
SMTP_USERNAME = os.getenv('SMTP_USERNAME', 'sysplat@mail.com')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
EMAIL_FROM = os.getenv('EMAIL_FROM', 'sysplat@mail.pro')
EMAIL_FROM_NAME = os.getenv('EMAIL_FROM_NAME', '运维平台')  # 邮件发送人显示名称

# 收件人配置（支持区分日报表和月报表）
# 如果设置了 EMAIL_TO_DAILY 或 EMAIL_TO_MONTHLY，则优先使用；否则使用 EMAIL_TO
EMAIL_TO_DAILY = os.getenv('EMAIL_TO_DAILY', 'ops@mail.com')
EMAIL_TO_MONTHLY = os.getenv('EMAIL_TO_MONTHLY', 'ops@mail.com,sysplat@mail.pro')
EMAIL_TO = os.getenv('EMAIL_TO', 'ops@mail.com')  # 默认收件人（向后兼容）

# 抄送人配置（支持区分日报表和月报表）
EMAIL_CC_DAILY = os.getenv('EMAIL_CC_DAILY', '')
EMAIL_CC_MONTHLY = os.getenv('EMAIL_CC_MONTHLY', '')
EMAIL_CC = os.getenv('EMAIL_CC', '')  # 默认抄送人（向后兼容）

def get_email_recipients(report_type='daily'):
    """
    根据报表类型获取收件人列表
    
    Args:
        report_type: 报表类型，'daily' 或 'monthly'
    
    Returns:
        收件人邮箱地址列表
    """
    if report_type == 'daily' and EMAIL_TO_DAILY:
        recipients = EMAIL_TO_DAILY
    elif report_type == 'monthly' and EMAIL_TO_MONTHLY:
        recipients = EMAIL_TO_MONTHLY
    else:
        recipients = EMAIL_TO
    
    return [email.strip() for email in recipients.split(',') if email.strip()]

def get_email_cc_recipients(report_type='daily'):
    """
    根据报表类型获取抄送人列表
    
    Args:
        report_type: 报表类型，'daily' 或 'monthly'
    
    Returns:
        抄送人邮箱地址列表（如果没有配置则返回空列表）
    """
    if report_type == 'daily' and EMAIL_CC_DAILY:
        cc_recipients = EMAIL_CC_DAILY
    elif report_type == 'monthly' and EMAIL_CC_MONTHLY:
        cc_recipients = EMAIL_CC_MONTHLY
    elif EMAIL_CC:
        cc_recipients = EMAIL_CC
    else:
        return []
    
    return [email.strip() for email in cc_recipients.split(',') if email.strip()]

# 报表类型配置
# 可选值: 'daily' (日报表) 或 'monthly' (月报表)
# 日报表: 获取前4天和前5天的账单数据
# 月报表: 在每月5号发送，获取上个月和上上个月的月账单数据
#REPORT_TYPE = os.getenv('REPORT_TYPE', 'daily')  # 默认为日报表
REPORT_TYPE = os.getenv('REPORT_TYPE', 'monthly')  # 默认为日报表

# 邮件主题
EMAIL_SUBJECT = 'AWS每日账单报告'
