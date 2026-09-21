---
编号: UBH-016
验证状态: 动态确认
严重程度: 高
披露状态: 内部研究
源平台: 优必选人型
源候选目录: jetson-调试UART无认证root-shell
---
# UBH-016 VB1 · Jetson 调试 UART 无认证 root shell

## 1. 一句话结论

- \| 危害 \| **严重** — 物理接调试 UART（115200）即落入 walker shell，免密 sudo → root \|
- ## 结论

## 2. 影响产品与版本

- \| 组件 \| vision 板 Jetson T234 调试串口 ttyTCU0 \|

## 3. 验证状态

`动态确认`。该状态来自源报告的验证边界；迁移过程不把目录名称自动视为动态确认。

## 4. 攻击前提

攻击前提以脱敏研究正文为准；复现必须使用自有设备、隔离网络和授权环境，不得对第三方设备执行写入、控制或破坏性操作。

## 5. 根本原因

- # VB1 · Jetson 调试 UART 无认证 root shell
- 物理接触调试口 → 无认证 shell（自动登录 walker）→ 免密 sudo → root。

## 6. 攻击过程

源报告描述的入口、协议和利用顺序见第 13 节脱敏正文；本目录只保留最小复现材料，不复制原始大型证据。

## 7. 实际影响

- # VB1 · Jetson 调试 UART 无认证 root shell
- \| 危害 \| **严重** — 物理接调试 UART（115200）即落入 walker shell，免密 sudo → root \|
- root   1906  /bin/login -f     (ttyTCU0 无密码登录)
- - walker 免密 sudo → `sudo -i` 即 root
- 物理接触调试口 → 无认证 shell（自动登录 walker）→ 免密 sudo → root。

## 8. 复现方法

复现材料见 [复现材料清单](复现/材料清单.md)。导入脚本已做文本脱敏；未导入的原始脚本、日志、抓包和二进制见根目录材料清单。

## 9. 支撑证据

见 [证据材料清单](证据/材料清单.md) 和本页第 13 节。来源文件只登记哈希和本地保管路径，不把原始敏感材料带入 Git。

## 10. 修复建议

- 对入口实施身份认证、细粒度授权、消息完整性校验和重放防护；
- 对路径、长度、协议字段、文件类型和状态转换使用允许列表；
- 删除硬编码凭据并轮换已暴露材料；
- 对高风险服务降权，增加审计日志和负向回归测试。

## 11. 相关 AI 会话

当前未发现与该报告一一对应的完整 Claude Code 会话记录；如后续补齐，将在 [AI 会话索引](../../../../../AI轨迹/会话索引.md) 中登记。

## 12. 披露记录

- 当前披露状态：内部研究。
- 对外披露前必须重新审查凭据、设备标识、证据和厂商协调状态。

## 13. 脱敏后的原始研究正文

# VB1 · Jetson 调试 UART 无认证 root shell

| 项 | 值 |
|---|---|
| 组件 | vision 板 Jetson T234 调试串口 ttyTCU0 |
| 机制 | **systemd autologin**：`<个人邮箱_01>.d/autologin.conf` = `agetty --autologin walker` |
| 危害 | **严重** — 物理接调试 UART（115200）即落入 walker shell，免密 sudo → root |
| 来源 | report_voice_boot(1).md (VB1)，**本会话现场复验确认（机制与报告略不同）** |
| 复验 | 🟢 **已确认**：autologin 配置 + 活体 `/bin/login -f` + `-bash` 会话就在 ttyTCU0 上 |

## 现场复验证据（2026-08-29）
```
/etc/systemd/system/<个人邮箱_01>.d/autologin.conf:
    ExecStart=-/sbin/agetty --autologin walker --keep-baud 115200 %I $TERM
ps aux | grep ttyTCU0:
    root   1906  /bin/login -f     (ttyTCU0 无密码登录)
    walker 2609  -bash             (ttyTCU0 活动会话)
```
- `console=ttyTCU0,115200` 双处确认（payload cmdline + DTB /chosen/bootargs）
- 同样的 autologin 还覆盖 ttyAMA0 / ttyAMA6 / ttyS0 / tty1
- walker 免密 sudo → `sudo -i` 即 root
- **与报告差异**：报告的 initrd 内 "Press [ENTER] to start bash" 字符串未在
  kernel_only_payload 和 /boot/initrd 中找到；实际机制是 systemd autologin，效果等价。

## 结论
物理接触调试口 → 无认证 shell（自动登录 walker）→ 免密 sudo → root。
报告所述字符串虽未找到，**漏洞本身成立且已在活体系统上确认**。
详见 `evidence/uart_shell_evidence.txt`（当前存于共享证据目录 `漏洞整理/evidence/`）。
