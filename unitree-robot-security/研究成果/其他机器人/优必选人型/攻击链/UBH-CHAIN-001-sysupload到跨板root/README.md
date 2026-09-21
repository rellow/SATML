# UBH-CHAIN-001 sysupload 到跨板 root

## 链路结论

未认证的任意路径写入与跨板 SFTP 写入组合，可将文件写入 motion 板并形成 root 命令执行链。

## 组成漏洞

1. [UBH-009 sysupload 任意路径写到宿主 root RCE](../../漏洞/UBH-009-api-sysupload任意路径写-宿主root-RCE/README.md)
2. [UBH-010 sysupload 任意路径写跨板 SFTP RCE](../../漏洞/UBH-010-api-sysupload任意路径写跨板SFTP-RCE/README.md)

## 说明

本目录只串联漏洞，不复制 PoC、脚本或证据。原始跨板凭据、主机地址和授权密钥不进入 Git。

## 状态

已动态确认；复现必须使用自有设备、隔离网络和可恢复快照。
