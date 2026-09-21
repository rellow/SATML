#!/bin/sh
# 收尾清理：移除持久化 SSH 服务 sshd-persist。
# 用法(狗上 root): sh remove_persist.sh
systemctl disable --now sshd-persist 2>/dev/null || true
rm -f /etc/systemd/system/sshd-persist.service /etc/ssh/sshd_persist.conf
systemctl daemon-reload
echo "=== sshd-persist 已移除 ==="
ss -tlnp | grep 22022 && echo "(22022 仍在监听？可能有残留 sshd 进程)" || echo "22022 已关闭"
echo "如需同时清理凭据: 删除 /root/.ssh/authorized_keys 中本次加入的公钥；如设过 root 口令请另行轮换。"
