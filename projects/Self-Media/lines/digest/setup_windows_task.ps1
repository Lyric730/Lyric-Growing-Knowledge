# Windows 任务计划程序 — 注册 Self-Media 日报自动跑
#
# 用法（PowerShell 管理员）：
#   powershell -ExecutionPolicy Bypass -File setup_windows_task.ps1
#
# 创建任务名：SelfMedia-DailyDigest
# 触发：每天 12:00
# 动作：wsl.exe bash -lc "/home/lyric/.../scheduled_daily.sh"
# 选项：开机唤醒 / 允许息屏跑 / 失败重试 3 次

# ------- 参数 -------
$TaskName = "SelfMedia-DailyDigest"
$TaskDesc = "每天中午 12:00 自动跑 AI 日报生成 (fetch → enrich → claude /daily → render → screenshot → post.md)"
$WSLScript = "/home/lyric/sm-daily.sh"   # 无空格 wrapper，避开 Windows 任务计划程序的 quote 转义坑
$Trigger = New-ScheduledTaskTrigger -Daily -At (Get-Date "12:00:00")

# ------- 删除已有同名任务（如果有）-------
$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "→ 发现已存在 $TaskName，先删除..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# ------- 创建动作：wsl.exe bash -lc "<script>" -------
# 注意 1: bash -lc 让 .bashrc / .profile 加载（拿到 PATH 等）
# 注意 2: 路径含空格 "Making money"，必须用 PowerShell single quote 保持双引号原样传给 wsl
$Action = New-ScheduledTaskAction `
    -Execute "C:\Windows\System32\wsl.exe" `
    -Argument "bash -lc $WSLScript"

# ------- 设置：允许息屏跑 / 唤醒 / 失败重试 -------
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -WakeToRun `
    -StartWhenAvailable `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 10) `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1)

# ------- 注册任务（默认 Interactive 模式：用户登录时跑，息屏 OK，无需管理员）-------
Register-ScheduledTask `
    -TaskName $TaskName `
    -Description $TaskDesc `
    -Trigger $Trigger `
    -Action $Action `
    -Settings $Settings

Write-Host "" -ForegroundColor Green
Write-Host "✓ 任务已注册：$TaskName" -ForegroundColor Green
Write-Host "  触发：每天 12:00 PM" -ForegroundColor Green
Write-Host "  动作：wsl.exe bash -lc $WSLScript" -ForegroundColor Green
Write-Host "" -ForegroundColor Green
Write-Host "→ 立即测试（不等到 12:00）：" -ForegroundColor Cyan
Write-Host "    Start-ScheduledTask -TaskName $TaskName" -ForegroundColor Cyan
Write-Host "" -ForegroundColor Cyan
Write-Host "→ 查看任务状态：" -ForegroundColor Cyan
Write-Host "    Get-ScheduledTask -TaskName $TaskName | Get-ScheduledTaskInfo" -ForegroundColor Cyan
Write-Host "" -ForegroundColor Cyan
Write-Host "→ 看日志（在 WSL）：" -ForegroundColor Cyan
Write-Host '    wsl tail -f /tmp/daily-$(date +%F).log' -ForegroundColor Cyan
Write-Host "" -ForegroundColor Cyan
Write-Host "→ 删除任务（PowerShell）：" -ForegroundColor Cyan
Write-Host ('    Unregister-ScheduledTask -TaskName ' + $TaskName + ' -Confirm:[bool]0') -ForegroundColor Cyan
