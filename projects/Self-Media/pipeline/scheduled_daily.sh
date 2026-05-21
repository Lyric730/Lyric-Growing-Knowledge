#!/bin/bash
# Windows 任务计划程序 → WSL bash 入口
# 每天中午 12:00 触发，自动跑日报全链路
#
# Windows 任务计划程序 action:
#   程序：C:\Windows\System32\wsl.exe
#   参数：bash -lc "/home/lyric/Making money/Lyric-Self-Improve/projects/Self-Media/pipeline/scheduled_daily.sh"

set -e

# ----- 环境 -----
export PATH="$HOME/.local/bin:$HOME/.nvm/versions/node/v24.15.0/bin:/usr/local/bin:/usr/bin:/bin"
# Clash 代理（WSL 走 Windows Clash）
export HTTP_PROXY="http://127.0.0.1:7897"
export HTTPS_PROXY="http://127.0.0.1:7897"
export NODE_USE_ENV_PROXY=1

# ----- SMTP 凭证（chmod 600 不入 git）-----
if [ -f "$HOME/.self-media-secrets.env" ]; then
    set -a
    source "$HOME/.self-media-secrets.env"
    set +a
fi

# ----- 路径 -----
PROJECT="/home/lyric/Making money/Lyric-Self-Improve/projects/Self-Media"
DATE=$(date +%F)                    # "今天" = 2026-05-18
LOG="/tmp/daily-${DATE}.log"
STATE_FILE="${PROJECT}/daily/${DATE}/.scheduled-state"

cd "$PROJECT"
mkdir -p "daily/${DATE}"

# ----- 头部 log -----
{
  echo "═════════════════════════════════════════"
  echo "  Daily Pipeline · $(date '+%Y-%m-%d %H:%M:%S')"
  echo "  Date: ${DATE}"
  echo "  PWD: $(pwd)"
  echo "  PATH: ${PATH}"
  echo "═════════════════════════════════════════"
} | tee -a "$LOG"

# ----- 跑 run.py --auto -----
set +e
python3 pipeline/run.py "$DATE" --auto >> "$LOG" 2>&1
EXIT=$?
set -e

if [ "$EXIT" -eq 0 ]; then
    echo "SUCCESS $(date '+%H:%M:%S')" > "$STATE_FILE"
    {
      echo ""
      echo "═══ ✓ DONE @ $(date '+%H:%M:%S') ═══"
      echo "  → daily/${DATE}/publish/post.md"
      echo "  → 9 PNG 在 daily/${DATE}/publish/images/"
    } | tee -a "$LOG"

    # ----- 发邮件（含 9 PNG + post.md + README 附件）-----
    {
      echo ""
      echo "→ 发邮件通知..."
      python3 pipeline/send_notify.py "$DATE" 2>&1 || echo "  ⚠ 邮件发送失败但日报已生成"
    } | tee -a "$LOG"

    # Windows 通知（成功）
    if command -v powershell.exe &> /dev/null; then
        powershell.exe -Command "
            \$msg = '日报已生成：daily/${DATE}/publish/。已发邮件，审完发小红书。'
            \$bal = New-Object System.Windows.Forms.NotifyIcon
            \$bal.Icon = [System.Drawing.SystemIcons]::Information
            \$bal.BalloonTipTitle = 'Self-Media 日报 ✓'
            \$bal.BalloonTipText = \$msg
            \$bal.Visible = \$true
            \$bal.ShowBalloonTip(10000)
            Start-Sleep -Seconds 12
        " 2>/dev/null &
    fi

    exit 0
else
    echo "FAIL exit=${EXIT} $(date '+%H:%M:%S')" > "$STATE_FILE"
    {
      echo ""
      echo "═══ ✗ FAILED (exit ${EXIT}) @ $(date '+%H:%M:%S') ═══"
      echo "  Check log: $LOG"
    } | tee -a "$LOG"

    # ----- 发失败邮件（附 log）-----
    {
      echo ""
      echo "→ 发失败邮件..."
      python3 pipeline/send_notify.py "$DATE" --fail "run.py exit=${EXIT}" 2>&1 || echo "  ⚠ 邮件发送也失败"
    } | tee -a "$LOG"

    # Windows 通知（失败）
    if command -v powershell.exe &> /dev/null; then
        powershell.exe -Command "
            \$msg = '日报生成失败 exit=${EXIT}。看邮件 / log: $LOG'
            \$bal = New-Object System.Windows.Forms.NotifyIcon
            \$bal.Icon = [System.Drawing.SystemIcons]::Warning
            \$bal.BalloonTipTitle = 'Self-Media 日报 ✗ FAIL'
            \$bal.BalloonTipText = \$msg
            \$bal.Visible = \$true
            \$bal.ShowBalloonTip(15000)
            Start-Sleep -Seconds 17
        " 2>/dev/null &
    fi

    exit "$EXIT"
fi
