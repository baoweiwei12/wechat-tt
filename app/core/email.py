import logging
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional


class EmailVerification:
    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        sender_email: str,
        sender_password: str,
    ):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.verification_code: Optional[str] = None
        self.server: Optional[smtplib.SMTP] = None

        # 初始化时创建 SMTP 连接
        self._connect()

    def _connect(self):
        """创建并初始化 SMTP 连接"""
        try:
            self.server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            self.server.login(self.sender_email, self.sender_password)
            logging.info("SMTP connection established.")
        except Exception as e:
            logging.error(f"Failed to establish SMTP connection: {e}")
            raise

    def __del__(self):
        """析构时关闭 SMTP 连接"""
        if self.server:
            try:
                self.server.quit()
                logging.info("SMTP connection closed.")
            except Exception as e:
                logging.error(f"Failed to close SMTP connection: {e}")

    def generate_verification_code(self):
        """生成 4 位验证码"""
        self.verification_code = "".join([str(random.randint(0, 9)) for _ in range(4)])
        return self.verification_code

    def send_verification_email(self, receiver_email: str) -> bool:
        """发送验证码邮件"""
        if not self.verification_code:
            self.generate_verification_code()

        subject = "Your Verification Code"

        # HTML 邮件内容
        html_content = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    padding: 20px;
                }}
                .email-container {{
                    background-color: #ffffff;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                    max-width: 600px;
                    margin: 0 auto;
                }}
                .email-header {{
                    font-size: 24px;
                    color: #333333;
                    text-align: center;
                    margin-bottom: 20px;
                }}
                .email-body {{
                    font-size: 16px;
                    color: #555555;
                    text-align: center;
                }}
                .verification-code {{
                    font-size: 32px;
                    font-weight: bold;
                    color: #28a745;
                    margin: 20px 0;
                }}
                .email-footer {{
                    font-size: 14px;
                    color: #888888;
                    text-align: center;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="email-header">Your Verification Code</div>
                <div class="email-body">
                    <p>Please use the following verification code to complete your request:</p>
                    <div class="verification-code">{self.verification_code}</div>
                    <p>This code will expire in 5 minutes.</p>
                </div>
                <div class="email-footer">
                    <p>If you did not request this code, please ignore this email.</p>
                </div>
            </div>
        </body>
        </html>
        """

        # 创建 MIMEMultipart 对象
        msg = MIMEMultipart()
        msg["From"] = self.sender_email
        msg["To"] = receiver_email
        msg["Subject"] = subject

        # 添加 HTML 内容
        msg.attach(MIMEText(html_content, "html"))

        try:
            # 发送邮件
            if self.server:
                self.server.sendmail(self.sender_email, receiver_email, msg.as_string())
                logging.info(
                    f"Email sent to {receiver_email} - [{self.verification_code}]"
                )
                return True
            logging.error(
                f"Failed to send email to {receiver_email}: Server not connected"
            )
            return False
        except Exception as e:
            logging.error(f"Failed to send email to {receiver_email}: {e}")
            return False
