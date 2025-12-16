"""
报告生成模块
"""
from typing import Dict, Tuple
from datetime import datetime


class ReportGenerator:
    @staticmethod
    def calculate_change(current: float, previous: float) -> Tuple[float, float, str]:
        """
        计算变化量和变化百分比
        
        Args:
            current: 当前值
            previous: 之前的值
            
        Returns:
            (变化量, 变化百分比, 颜色标记)
        """
        if previous == 0:
            if current > 0:
                return current, float('inf'), 'red'
            else:
                return 0.0, 0.0, 'black'
        
        change = current - previous
        change_percent = (change / previous) * 100
        
        if change > 0:
            color = 'red'  # 增长用红色
        elif change < 0:
            color = 'green'  # 下降用绿色
        else:
            color = 'black'
        
        return change, change_percent, color
    
    @staticmethod
    def format_currency(amount: float) -> str:
        """
        格式化货币显示
        
        Args:
            amount: 金额
            
        Returns:
            格式化后的字符串
        """
        return f"${amount:,.2f}"
    
    @staticmethod
    def generate_html_report(
        yesterday_costs: Dict[str, float],
        day_before_costs: Dict[str, float],
        yesterday_total: float,
        day_before_total: float,
        yesterday_date: datetime,
        day_before_date: datetime,
        account_details: list = None,
        is_monthly: bool = False
    ) -> str:
        """
        生成HTML格式的报告
        
        Args:
            yesterday_costs: 昨天的服务成本字典（汇总）
            day_before_costs: 前天的服务成本字典（汇总）
            yesterday_total: 昨天总成本（汇总）
            day_before_total: 前天总成本（汇总）
            yesterday_date: 昨天的日期
            day_before_date: 前天的日期
            account_details: 可选，每个账号的明细数据列表
            is_monthly: 是否为月报表
            
        Returns:
            HTML字符串
        """
        # 获取所有服务名称（合并两天的服务）
        all_services = set(yesterday_costs.keys()) | set(day_before_costs.keys())
        
        # 按昨天的费用从高到低排序
        # 创建一个包含服务名和费用的列表，然后按费用降序排序
        services_with_costs = [
            (service, yesterday_costs.get(service, 0.0))
            for service in all_services
        ]
        services_with_costs.sort(key=lambda x: x[1], reverse=True)  # 按费用降序排序
        sorted_services = [service for service, _ in services_with_costs]
        
        # 计算总成本变化
        total_change, total_change_percent, total_color = ReportGenerator.calculate_change(
            yesterday_total, day_before_total
        )
        
        # 生成服务表格行
        service_rows = []
        for service in sorted_services:
            yesterday_cost = yesterday_costs.get(service, 0.0)
            day_before_cost = day_before_costs.get(service, 0.0)
            change, change_percent, color = ReportGenerator.calculate_change(
                yesterday_cost, day_before_cost
            )
            
            # 格式化显示
            change_str = ReportGenerator.format_currency(change)
            change_percent_str = f"{change_percent:+.2f}%"
            
            service_rows.append(f"""
            <tr>
                <td>{service}</td>
                <td>{ReportGenerator.format_currency(yesterday_cost)}</td>
                <td>{ReportGenerator.format_currency(day_before_cost)}</td>
                <td style="color: {color}; font-weight: bold;">{change_str}</td>
                <td style="color: {color}; font-weight: bold;">{change_percent_str}</td>
            </tr>
            """)
        
        # 根据报表类型格式化日期
        if is_monthly:
            yesterday_str = f"{yesterday_date.year}年{yesterday_date.month}月"
            day_before_str = f"{day_before_date.year}年{day_before_date.month}月"
        else:
            yesterday_str = yesterday_date.strftime('%Y年%m月%d日')
            day_before_str = day_before_date.strftime('%Y年%m月%d日')
        
        # 生成账号汇总表格（如果有多账号）
        account_summary_rows = ""
        if account_details and len(account_details) > 1:
            for acc_detail in account_details:
                acc_name = acc_detail['account_name']
                acc_yesterday_total = acc_detail['yesterday_total']
                acc_day_before_total = acc_detail['day_before_total']
                acc_change, acc_change_percent, acc_color = ReportGenerator.calculate_change(
                    acc_yesterday_total, acc_day_before_total
                )
                account_summary_rows += f"""
                <tr>
                    <td>{acc_name}</td>
                    <td>{ReportGenerator.format_currency(acc_yesterday_total)}</td>
                    <td>{ReportGenerator.format_currency(acc_day_before_total)}</td>
                    <td style="color: {acc_color}; font-weight: bold;">{ReportGenerator.format_currency(acc_change)}</td>
                    <td style="color: {acc_color}; font-weight: bold;">{acc_change_percent:+.2f}%</td>
                </tr>
                """
        
        # 为每个账号生成独立的服务明细表格
        account_service_tables = ""
        if account_details:
            for acc_detail in account_details:
                acc_name = acc_detail['account_name']
                acc_yesterday_costs = acc_detail['yesterday_costs']
                acc_day_before_costs = acc_detail['day_before_costs']
                acc_yesterday_total = acc_detail['yesterday_total']
                acc_day_before_total = acc_detail['day_before_total']
                
                # 获取该账号的所有服务
                acc_all_services = set(acc_yesterday_costs.keys()) | set(acc_day_before_costs.keys())
                
                # 按昨天的费用从高到低排序
                acc_services_with_costs = [
                    (service, acc_yesterday_costs.get(service, 0.0))
                    for service in acc_all_services
                ]
                acc_services_with_costs.sort(key=lambda x: x[1], reverse=True)
                acc_sorted_services = [service for service, _ in acc_services_with_costs]
                
                # 计算该账号的总成本变化
                acc_change, acc_change_percent, acc_color = ReportGenerator.calculate_change(
                    acc_yesterday_total, acc_day_before_total
                )
                
                # 生成该账号的服务表格行
                acc_service_rows = []
                for service in acc_sorted_services:
                    acc_yesterday_cost = acc_yesterday_costs.get(service, 0.0)
                    acc_day_before_cost = acc_day_before_costs.get(service, 0.0)
                    service_change, service_change_percent, service_color = ReportGenerator.calculate_change(
                        acc_yesterday_cost, acc_day_before_cost
                    )
                    
                    change_str = ReportGenerator.format_currency(service_change)
                    change_percent_str = f"{service_change_percent:+.2f}%"
                    
                    acc_service_rows.append(f"""
                    <tr>
                        <td>{service}</td>
                        <td>{ReportGenerator.format_currency(acc_yesterday_cost)}</td>
                        <td>{ReportGenerator.format_currency(acc_day_before_cost)}</td>
                        <td style="color: {service_color}; font-weight: bold;">{change_str}</td>
                        <td style="color: {service_color}; font-weight: bold;">{change_percent_str}</td>
                    </tr>
                    """)
                
                # 生成该账号的折叠表格
                period_label = f"{yesterday_str}" if is_monthly else f"{yesterday_str} 成本"
                previous_period_label = f"{day_before_str}" if is_monthly else f"{day_before_str} 成本"
                
                account_service_tables += f"""
                <details>
                    <summary>{acc_name} - 服务明细 (总成本: {ReportGenerator.format_currency(acc_yesterday_total)})</summary>
                    <table>
                        <thead>
                            <tr>
                                <th>服务名称</th>
                                <th>{period_label}</th>
                                <th>{previous_period_label}</th>
                                <th>变化量</th>
                                <th>变化百分比</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join(acc_service_rows)}
                            <tr class="total-row">
                                <td><strong>总计</strong></td>
                                <td><strong>{ReportGenerator.format_currency(acc_yesterday_total)}</strong></td>
                                <td><strong>{ReportGenerator.format_currency(acc_day_before_total)}</strong></td>
                                <td style="color: {acc_color};"><strong>{ReportGenerator.format_currency(acc_change)}</strong></td>
                                <td style="color: {acc_color};"><strong>{acc_change_percent:+.2f}%</strong></td>
                            </tr>
                        </tbody>
                    </table>
                </details>
                """
        
        # 生成HTML
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 10px;
        }}
        .summary {{
            background-color: #f9f9f9;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .summary-item {{
            margin: 10px 0;
            font-size: 16px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th {{
            background-color: #4CAF50;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }}
        td {{
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .total-row {{
            font-weight: bold;
            background-color: #e8f5e9;
        }}
        .footer {{
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #666;
            font-size: 12px;
        }}
        details {{
            margin-top: 20px;
        }}
        summary {{
            cursor: pointer;
            font-size: 18px;
            font-weight: bold;
            color: #333;
            padding: 10px;
            background-color: #f0f0f0;
            border-radius: 5px;
            user-select: none;
        }}
        summary:hover {{
            background-color: #e0e0e0;
        }}
        summary::-webkit-details-marker {{
            display: inline-block;
            margin-right: 8px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{'AWS月度账单报告' if is_monthly else 'AWS每日账单报告'}</h1>
        
        <div class="summary">
            <div class="summary-item">
                <strong>{'报告月份' if is_monthly else '报告日期'}:</strong> {yesterday_str}
            </div>
            <div class="summary-item">
                <strong>统计账号数:</strong> {len(account_details) if account_details else 1} 个
            </div>
            <div class="summary-item">
                <strong>{yesterday_str}总账单:</strong> {ReportGenerator.format_currency(yesterday_total)}
            </div>
            <div class="summary-item">
                <strong>{day_before_str}总账单:</strong> {ReportGenerator.format_currency(day_before_total)}
            </div>
            <div class="summary-item">
                <strong>总账单变化:</strong> 
                <span style="color: {total_color}; font-weight: bold;">
                    {ReportGenerator.format_currency(total_change)} 
                    ({total_change_percent:+.2f}%)
                </span>
            </div>
        </div>
        
        {f'''
        <h2>按账号汇总</h2>
        <table>
            <thead>
                <tr>
                    <th>账号名称</th>
                    <th>{yesterday_str} 总成本</th>
                    <th>{day_before_str} 总成本</th>
                    <th>变化量</th>
                    <th>变化百分比</th>
                </tr>
            </thead>
            <tbody>
                {account_summary_rows}
                <tr class="total-row">
                    <td><strong>总计</strong></td>
                    <td><strong>{ReportGenerator.format_currency(yesterday_total)}</strong></td>
                    <td><strong>{ReportGenerator.format_currency(day_before_total)}</strong></td>
                    <td style="color: {total_color};"><strong>{ReportGenerator.format_currency(total_change)}</strong></td>
                    <td style="color: {total_color};"><strong>{total_change_percent:+.2f}%</strong></td>
                </tr>
            </tbody>
        </table>
        ''' if account_details and len(account_details) > 1 else ''}
        
        <h2>按账号分组的服务明细</h2>
        {account_service_tables if account_service_tables else f'''
        <details>
            <summary>按服务分组的账单明细（所有账号汇总）</summary>
            <table>
                <thead>
                    <tr>
                        <th>服务名称</th>
                        <th>{yesterday_str if is_monthly else yesterday_str + ' 成本'}</th>
                        <th>{day_before_str if is_monthly else day_before_str + ' 成本'}</th>
                        <th>变化量</th>
                        <th>变化百分比</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(service_rows)}
                    <tr class="total-row">
                        <td><strong>总计</strong></td>
                        <td><strong>{ReportGenerator.format_currency(yesterday_total)}</strong></td>
                        <td><strong>{ReportGenerator.format_currency(day_before_total)}</strong></td>
                        <td style="color: {total_color};"><strong>{ReportGenerator.format_currency(total_change)}</strong></td>
                        <td style="color: {total_color};"><strong>{total_change_percent:+.2f}%</strong></td>
                    </tr>
                </tbody>
            </table>
        </details>
        '''}
        
        <div class="footer">
            <p>注: 红色表示增长，绿色表示下降</p>
            <p>因成本数据存在滞后问题, 一般4天前的数据是完全更新</p>
            <p>旨在帮助团队了解AWS资源使用情况, 优化资源利用, 降低成本</p>
        </div>
    </div>
</body>
</html>
        """
        
        return html

