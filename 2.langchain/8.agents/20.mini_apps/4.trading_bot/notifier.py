"""
이메일 발송 — SMTP 설정 있으면 실제 발송, 없으면 콘솔 출력 (POC 폴백).
키 없이도 전체 흐름을 데모할 수 있게 콘솔로 '메일 내용 + 승인/거부 URL' 을 찍는다.

  ※ Gmail 사용 시 EMAIL_APP_PASSWORD 는 '앱 비밀번호'(2단계 인증 후 발급)
"""

import os
import smtplib
from email.mime.text import MIMEText


def send_email(subject: str, body: str):
    user = os.getenv("EMAIL_USER")
    pw = os.getenv("EMAIL_APP_PASSWORD")
    to = os.getenv("EMAIL_TO") or user

    if not (user and pw and to):
        print("\n" + "=" * 56)
        print("[이메일 미설정 — 콘솔 폴백]")
        print(f"제목: {subject}")
        print(body)
        print("=" * 56 + "\n")
        return

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = to
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(user, pw)
        s.sendmail(user, [to], msg.as_string())
    
    print(f"[이메일 발송됨] → {to}  (제목: {subject})")
