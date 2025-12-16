"""
邮件发送模块
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from typing import List


class EmailSender:
    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str, use_ssl: bool = None):
        """
        初始化邮件发送器
        
        Args:
            smtp_server: SMTP服务器地址
            smtp_port: SMTP端口
            username: 邮箱用户名
            password: 邮箱密码或应用专用密码
            use_ssl: 是否使用SSL连接（None表示自动判断：465端口使用SSL，其他端口使用STARTTLS）
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        # 如果未指定，根据端口自动判断：465使用SSL，其他使用STARTTLS
        if use_ssl is None:
            self.use_ssl = (smtp_port == 465)
        else:
            self.use_ssl = use_ssl
    
    def send_email(self, from_addr: str, to_addrs: List[str], subject: str, html_content: str, from_name: str = None, cc_addrs: List[str] = None):
        """
        发送HTML邮件
        
        Args:
            from_addr: 发件人地址
            to_addrs: 收件人地址列表
            subject: 邮件主题
            html_content: HTML内容
            from_name: 发件人显示名称（可选）
            cc_addrs: 抄送人地址列表（可选）
        """
        server = None
        email_sent = False
        try:
            # 创建邮件
            msg = MIMEMultipart('alternative')
            
            # 设置发件人（如果有显示名称，使用格式：显示名称 <email@example.com>）
            if from_name:
                # 使用 Header 编码中文显示名称
                from_header = Header(from_name, 'utf-8').encode()
                msg['From'] = f'{from_header} <{from_addr}>'
            else:
                msg['From'] = from_addr
            
            msg['To'] = ', '.join(to_addrs)
            
            # 设置抄送人（如果有）
            if cc_addrs and len(cc_addrs) > 0:
                msg['Cc'] = ', '.join(cc_addrs)
            
            msg['Subject'] = Header(subject, 'utf-8').encode()
            
            # 添加HTML内容
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # 发送邮件（根据配置选择SSL或STARTTLS）
            # 增加超时时间到60秒，因为某些SMTP服务器响应较慢
            if self.use_ssl:
                # 使用SSL连接（端口465）
                print(f"使用SSL连接 {self.smtp_server}:{self.smtp_port}")
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=60)
            else:
                # 使用STARTTLS连接（端口587或其他）
                print(f"使用STARTTLS连接 {self.smtp_server}:{self.smtp_port}")
                server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=60)
                server.starttls()
            
            server.login(self.username, self.password)
            
            # 合并收件人和抄送人列表用于 sendmail
            all_recipients = to_addrs.copy()
            if cc_addrs and len(cc_addrs) > 0:
                all_recipients.extend(cc_addrs)
            
            server.sendmail(from_addr, all_recipients, msg.as_string())
            email_sent = True  # 标记邮件已成功发送
            
            # 显示发送信息
            send_info = f"收件人: {', '.join(to_addrs)}"
            if cc_addrs and len(cc_addrs) > 0:
                send_info += f" | 抄送: {', '.join(cc_addrs)}"
            print(f"邮件已成功发送 - {send_info}")
            
        except smtplib.SMTPResponseException as e:
            # 处理 SMTP 响应错误，包括 (-1, b'\x00\x00\x00') 这种连接关闭错误
            if e.smtp_code == -1 and email_sent:
                # 如果邮件已经发送成功，忽略退出时的连接关闭错误
                print(f"邮件已发送，但连接关闭时出现警告（可忽略）: {str(e)}")
                return  # 邮件已成功发送，直接返回
            else:
                print(f"SMTP服务器返回错误: {e.smtp_code} - {e.smtp_error}")
                raise
        except smtplib.SMTPAuthenticationError as e:
            error_msg = str(e)
            if '535' in error_msg or 'BadCredentials' in error_msg:
                print("=" * 60)
                print("Gmail SMTP 认证失败！")
                print("=" * 60)
                print("可能的原因：")
                print("1. 使用了普通密码而不是应用专用密码")
                print("2. 未启用两步验证")
                print("3. 应用专用密码配置错误")
                print("\n解决方法：")
                print("1. 确保已启用两步验证：")
                print("   https://myaccount.google.com/security")
                print("2. 生成应用专用密码：")
                print("   https://myaccount.google.com/apppasswords")
                print("3. 使用应用专用密码（16位字符，无空格）作为 SMTP_PASSWORD")
                print("=" * 60)
            raise
        except (smtplib.SMTPServerDisconnected, TimeoutError, ConnectionError) as e:
            error_msg = str(e)
            print("=" * 60)
            print("SMTP连接失败！")
            print("=" * 60)
            print(f"错误信息: {error_msg}")
            print(f"SMTP服务器: {self.smtp_server}:{self.smtp_port}")
            print(f"连接方式: {'SSL' if self.use_ssl else 'STARTTLS'}")
            print("\n可能的原因：")
            print("1. SMTP服务器地址或端口配置错误")
            print("2. 网络连接问题或防火墙阻止")
            print("3. 需要使用SSL连接（端口465）但使用了STARTTLS，或反之")
            print("4. SMTP服务器响应超时")
            print("\n解决方法：")
            if 'larksuite' in self.smtp_server.lower():
                print("Lark SMTP配置建议：")
                print("  - 端口465：使用SSL连接")
                print("  - 端口587：使用STARTTLS连接")
                print("  - 确保在Lark管理后台启用了IMAP/SMTP服务")
                print("  - 检查是否使用了正确的授权码（不是登录密码）")
            print("=" * 60)
            raise
        except Exception as e:
            print(f"发送邮件时出错: {str(e)}")
            raise
        finally:
            # 安全关闭连接（忽略关闭时的错误，因为邮件可能已经成功发送）
            if server:
                try:
                    server.quit()
                except (smtplib.SMTPResponseException, Exception) as close_error:
                    # 如果邮件已发送成功，忽略关闭连接时的错误
                    if email_sent:
                        # 邮件已成功发送，连接关闭错误可以忽略
                        pass
                    else:
                        # 如果邮件未发送，记录关闭错误但不抛出（避免掩盖原始错误）
                        pass
                try:
                    server.close()
                except:
                    pass

