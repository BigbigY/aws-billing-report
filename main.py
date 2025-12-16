#!/usr/bin/env python3
"""
AWS账单报告主程序
支持日报表和月报表
"""
import sys
from datetime import datetime, timedelta
from dateutil import tz

from config import (
    get_aws_accounts,
    REPORT_TYPE,
    SMTP_SERVER,
    SMTP_PORT,
    SMTP_USERNAME,
    SMTP_PASSWORD,
    EMAIL_FROM,
    EMAIL_FROM_NAME,
    get_email_recipients,
    get_email_cc_recipients,
    EMAIL_SUBJECT
)
from aws_cost_explorer import AWSCostExplorer
from report_generator import ReportGenerator
from email_sender import EmailSender


def main():
    """主函数"""
    # 检查配置
    if not EMAIL_FROM:
        print("错误: 请配置EMAIL_FROM环境变量或在config.py中设置")
        sys.exit(1)
    
    # 检查收件人配置（根据报表类型）
    recipients = get_email_recipients(REPORT_TYPE)
    if not recipients:
        print(f"错误: 请配置EMAIL_TO_{REPORT_TYPE.upper()}或EMAIL_TO环境变量或在config.py中设置")
        sys.exit(1)
    
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        print("错误: 请配置SMTP_USERNAME和SMTP_PASSWORD环境变量或在config.py中设置")
        sys.exit(1)
    
    # 获取AWS账号列表
    aws_accounts = get_aws_accounts()
    if not aws_accounts:
        print("错误: 未配置AWS账号，请设置AWS_ACCOUNTS环境变量或在config.py中配置")
        sys.exit(1)
    
    print(f"找到 {len(aws_accounts)} 个AWS账号")
    print(f"报表类型: {REPORT_TYPE}")
    
    # 根据报表类型计算日期
    utc = tz.gettz('UTC')
    now = datetime.now(utc)
    
    is_monthly = REPORT_TYPE.lower() == 'monthly'
    
    if is_monthly:
        # 月报表：获取上个月和上上个月的月账单数据
        # 例如：今天是1月5号，获取12月（上个月）和11月（上上个月）的账单
        current_year = now.year
        current_month = now.month
        
        # 计算上个月
        if current_month == 1:
            last_month_year = current_year - 1
            last_month = 12
        else:
            last_month_year = current_year
            last_month = current_month - 1
        
        # 计算上上个月
        if last_month == 1:
            previous_month_year = last_month_year - 1
            previous_month = 12
        else:
            previous_month_year = last_month_year
            previous_month = last_month - 1
        
        print(f"获取 {last_month_year}年{last_month}月（上个月）和 {previous_month_year}年{previous_month}月（上上个月）的账单数据...")
        
        # 为了兼容报告生成器，创建日期对象（使用月份的第一天）
        yesterday = datetime(last_month_year, last_month, 1, tzinfo=utc)
        day_before = datetime(previous_month_year, previous_month, 1, tzinfo=utc)
        
    else:
        # 日报表：计算日期（前4天和前5天，因为AWS账单有延迟）
        # 例如：今天是18号，获取14号（前4天，较新）和13号（前5天，较旧）的账单对比
        day_4_ago = now - timedelta(days=4)    # 前4天（较新的日期，对应yesterday）
        day_5_ago = now - timedelta(days=5)    # 前5天（较旧的日期，对应day_before）
        
        # 确保日期是当天的开始
        yesterday = day_4_ago.replace(hour=0, minute=0, second=0, microsecond=0)
        day_before = day_5_ago.replace(hour=0, minute=0, second=0, microsecond=0)
        
        print(f"获取 {yesterday.strftime('%Y-%m-%d')}（前4天）和 {day_before.strftime('%Y-%m-%d')}（前5天）的账单数据...")
    
    try:
        # 汇总所有账号的数据
        all_yesterday_costs = {}  # 所有账号昨天的服务成本汇总
        all_day_before_costs = {}  # 所有账号前天的服务成本汇总
        account_details = []  # 每个账号的明细数据
        
        yesterday_total = 0.0
        day_before_total = 0.0
        
        # 遍历每个账号
        for idx, account in enumerate(aws_accounts, 1):
            account_name = account.get('account_name', f'账号{idx}')
            access_key_id = account.get('access_key_id')
            secret_access_key = account.get('secret_access_key')
            region = account.get('region', 'us-east-1')
            
            print(f"\n[{idx}/{len(aws_accounts)}] 正在处理账号: {account_name}")
            
            try:
                # 初始化AWS Cost Explorer
                cost_explorer = AWSCostExplorer(
                    access_key_id=access_key_id,
                    secret_access_key=secret_access_key,
                    region=region
                )
                
                # 根据报表类型获取数据
                if is_monthly:
                    # 月报表：获取月度对比数据
                    acc_yesterday_costs, acc_day_before_costs, acc_yesterday_total, acc_day_before_total = \
                        cost_explorer.get_monthly_comparison_data(
                            yesterday.year, yesterday.month,
                            day_before.year, day_before.month
                        )
                    print(f"  {account_name} - {yesterday.year}年{yesterday.month}月: ${acc_yesterday_total:,.2f}, {day_before.year}年{day_before.month}月: ${acc_day_before_total:,.2f}")
                else:
                    # 日报表：获取日度对比数据
                    acc_yesterday_costs, acc_day_before_costs, acc_yesterday_total, acc_day_before_total = \
                        cost_explorer.get_comparison_data(yesterday, day_before)
                    print(f"  {account_name} - 昨天: ${acc_yesterday_total:,.2f}, 前天: ${acc_day_before_total:,.2f}")
                
                # 汇总到总数据
                for service, cost in acc_yesterday_costs.items():
                    all_yesterday_costs[service] = all_yesterday_costs.get(service, 0.0) + cost
                
                for service, cost in acc_day_before_costs.items():
                    all_day_before_costs[service] = all_day_before_costs.get(service, 0.0) + cost
                
                yesterday_total += acc_yesterday_total
                day_before_total += acc_day_before_total
                
                # 保存账号明细
                account_details.append({
                    'account_name': account_name,
                    'yesterday_costs': acc_yesterday_costs,
                    'day_before_costs': acc_day_before_costs,
                    'yesterday_total': acc_yesterday_total,
                    'day_before_total': acc_day_before_total
                })
                
            except Exception as e:
                print(f"  警告: 账号 {account_name} 获取数据失败: {str(e)}")
                # 继续处理其他账号
                continue
        
        print(f"\n汇总结果:")
        if is_monthly:
            print(f"  {yesterday.year}年{yesterday.month}月总成本: ${yesterday_total:,.2f}")
            print(f"  {day_before.year}年{day_before.month}月总成本: ${day_before_total:,.2f}")
        else:
            print(f"  昨天总成本: ${yesterday_total:,.2f}")
            print(f"  前天总成本: ${day_before_total:,.2f}")
        print(f"  服务数量: {len(set(all_yesterday_costs.keys()) | set(all_day_before_costs.keys()))}")
        
        # 生成HTML报告
        html_report = ReportGenerator.generate_html_report(
            yesterday_costs=all_yesterday_costs,
            day_before_costs=all_day_before_costs,
            yesterday_total=yesterday_total,
            day_before_total=day_before_total,
            yesterday_date=yesterday,
            day_before_date=day_before,
            account_details=account_details,  # 传递账号明细
            is_monthly=is_monthly  # 传递报表类型
        )
        
        # 发送邮件
        email_sender = EmailSender(
            smtp_server=SMTP_SERVER,
            smtp_port=SMTP_PORT,
            username=SMTP_USERNAME,
            password=SMTP_PASSWORD
        )
        
        # 根据报表类型获取收件人列表
        recipients = get_email_recipients(REPORT_TYPE)
        
        if not recipients:
            print(f"错误: 未配置 {REPORT_TYPE} 报表的收件人，请设置 EMAIL_TO_{REPORT_TYPE.upper()} 或 EMAIL_TO 环境变量")
            sys.exit(1)
        
        # 根据报表类型获取抄送人列表
        cc_recipients = get_email_cc_recipients(REPORT_TYPE)
        
        # 根据报表类型生成邮件主题
        if is_monthly:
            subject = f"AWS月度账单报告 - {yesterday.year}年{yesterday.month}月"
        else:
            subject = f"{EMAIL_SUBJECT} - {yesterday.strftime('%Y-%m-%d')}"
        
        email_sender.send_email(
            from_addr=EMAIL_FROM,
            to_addrs=recipients,
            subject=subject,
            html_content=html_report,
            from_name=EMAIL_FROM_NAME,
            cc_addrs=cc_recipients if cc_recipients else None
        )
        
        print("报告已成功生成并发送！")
        
    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
