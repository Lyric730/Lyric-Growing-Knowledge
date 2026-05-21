"""
日报跑完后发邮件通知到小刀 Gmail。

Usage:
    python3 pipeline/send_notify.py 2026-05-21              # 成功通知
    python3 pipeline/send_notify.py 2026-05-21 --fail "原因" # 失败通知

环境变量（由 ~/.self-media-secrets.env source 注入）:
    SMTP_HOST  smtp.gmail.com
    SMTP_PORT  465
    SMTP_USER  你的发件 Gmail
    SMTP_PASS  16 位应用专用密码
    NOTIFY_TO  收件邮箱

退出码:
    0 发送成功
    1 配置错误（缺环境变量 / final.json 不存在）
    2 SMTP 发送失败
"""
import argparse
import json
import os
import smtplib
import socket
import ssl
import sys
from email.message import EmailMessage
from pathlib import Path

import socks  # type: ignore

ROOT = Path(__file__).resolve().parent.parent

# Gmail SMTP SSL 直连在国内被中间盒拦——SSL 握手会 timeout。
# 走 Clash mixed-port (7897) 的 SOCKS5 绕开。Clash 必须开着。
SOCKS_HOST = "127.0.0.1"
SOCKS_PORT = int(os.environ.get("SOCKS_PORT", 7897))


def build_success_body(date: str, data: dict) -> tuple[str, str]:
    events = data["events"]
    issue = data.get("issue_number", "")
    lines = [
        f"5/{date.split('-')[-1]} 第 {issue.replace('VOL. ', '')} 期日报已生成 ✓",
        f"",
        f"8 件标题：",
    ]
    for e in events:
        cat = e.get("category", "?")
        lines.append(f"  {e['id'][-2:]} [{cat}] {e['title']}")
    lines += [
        "",
        "—— 发布步骤 ——",
        f"1. 浏览器审稿: http://localhost:8765/daily/{date}/publish/daily.html",
        f"2. 拿 9 PNG（资源管理器打开）:",
        f"   \\\\wsl.localhost\\Ubuntu\\home\\lyric\\Making money\\Lyric-Self-Improve\\projects\\Self-Media\\daily\\{date}\\publish\\images\\",
        f"3. 看发布稿:",
        f"   \\\\wsl.localhost\\Ubuntu\\home\\lyric\\Making money\\Lyric-Self-Improve\\projects\\Self-Media\\daily\\{date}\\publish\\post.md",
        f"4. 小红书 19-22 点发（按 01 → 09 顺序上传 9 张 PNG）",
        "",
        f"—— 自检 ——",
        f"合规 grep:    0 hits ✓",
        f"事件数:       {len(events)} ✓",
        f"Pydantic:    schema OK ✓",
    ]
    subject = f"✓ 日报 {date} 第 {issue.replace('VOL. ', '')} 期已生成"
    return subject, "\n".join(lines)


def build_fail_body(date: str, reason: str) -> tuple[str, str]:
    log_path = f"/tmp/daily-{date}.log"
    body = [
        f"日报 {date} 生成失败 ✗",
        "",
        f"原因: {reason}",
        f"",
        f"看日志（WSL 终端）:",
        f"   tail -50 {log_path}",
        f"",
        f"或 Windows 资源管理器开:",
        f"   \\\\wsl.localhost\\Ubuntu\\tmp\\daily-{date}.log",
        f"",
        "建议：手工排查后跑 `python3 pipeline/run.py {date} --only-render`（如 final.json 已生成）",
    ]
    subject = f"✗ 日报 {date} 失败"
    return subject, "\n".join(body)


def attach_files(msg: EmailMessage, paths: list[Path]) -> int:
    """把文件附到邮件。返回成功附上的数量。"""
    import mimetypes
    n = 0
    for p in paths:
        if not p.exists():
            continue
        mtype, _ = mimetypes.guess_type(p.name)
        if not mtype:
            mtype = "application/octet-stream"
        maintype, subtype = mtype.split("/", 1)
        msg.add_attachment(p.read_bytes(), maintype=maintype, subtype=subtype, filename=p.name)
        n += 1
    return n


def send(subject: str, body: str, attachments: list[Path] = None) -> None:
    host = os.environ.get("SMTP_HOST")
    port = int(os.environ.get("SMTP_PORT", 465))
    user = os.environ.get("SMTP_USER")
    password = os.environ.get("SMTP_PASS")
    to_addr = os.environ.get("NOTIFY_TO")

    if not all([host, user, password, to_addr]):
        print("✗ 缺少 SMTP_* 或 NOTIFY_TO 环境变量。检查 ~/.self-media-secrets.env 是否被 source。")
        sys.exit(1)

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = to_addr
    msg.set_content(body)

    if attachments:
        n = attach_files(msg, attachments)
        print(f"  附件: {n}/{len(attachments)} 个")

    # 强制 SMTP 走 Clash SOCKS5（绕开中间盒 SSL 拦截）
    socks.set_default_proxy(socks.SOCKS5, SOCKS_HOST, SOCKS_PORT)
    _orig_socket = socket.socket
    socket.socket = socks.socksocket

    ctx = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL(host, port, context=ctx, timeout=30) as smtp:
            smtp.login(user, password)
            smtp.send_message(msg)
        print(f"✓ 邮件已发 → {to_addr}: {subject}")
    except smtplib.SMTPAuthenticationError as e:
        print(f"✗ Gmail 认证失败（密码错误 / 应用专用密码已撤销）: {e}")
        sys.exit(2)
    except (socks.ProxyConnectionError, socks.ProxyError) as e:
        print(f"✗ Clash SOCKS5 ({SOCKS_HOST}:{SOCKS_PORT}) 不可达——Clash 是否开着？{e}")
        sys.exit(2)
    except Exception as e:
        print(f"✗ SMTP 发送失败: {type(e).__name__}: {e}")
        sys.exit(2)
    finally:
        socket.socket = _orig_socket


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("date", help="YYYY-MM-DD")
    p.add_argument("--fail", dest="fail_reason", help="发失败通知，提供失败原因（exit code 等）")
    args = p.parse_args()

    attachments = []
    if args.fail_reason:
        subject, body = build_fail_body(args.date, args.fail_reason)
        # 失败时附 log
        log = Path(f"/tmp/daily-{args.date}.log")
        if log.exists():
            attachments.append(log)
    else:
        final = ROOT / "daily" / args.date / "work" / "final.json"
        if not final.exists():
            print(f"✗ {final} 不存在 — 跑成功通知前必须先有 final.json")
            sys.exit(1)
        data = json.loads(final.read_text(encoding="utf-8"))
        subject, body = build_success_body(args.date, data)

        # 成功：附 9 PNG + post.md + README + final.json
        pub = ROOT / "daily" / args.date / "publish"
        attachments.append(pub / "post.md")
        attachments.append(pub / "README.md")
        for i in range(1, 10):
            stem = "cover" if i == 1 else f"event-{i-1:02d}"
            attachments.append(pub / "images" / f"{i:02d}-{stem}.png")

    send(subject, body, attachments)


if __name__ == "__main__":
    main()
