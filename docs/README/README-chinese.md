<p align="right">
<a href="https://github.com/DjangoCRM/django-crm/blob/main/README.md">English</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-hindi.md">हिन्दी</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-spanish.md">Español</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-chinese.md">中文</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-portuguese.md">Português</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-arabic.md">اَلْعَرَبِيَّةُ</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-french.md">Français</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-german.md">Deutsch</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-dutch.md">Nederlands</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-italian.md">Italiano</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-ukrainian.md">Українська</a>
</p>

---

# Django-CRM

## 免费开源的 Python CRM，集成任务管理、电子邮件营销与数据分析

**Django CRM** 是一款基于 [Python](https://www.python.org) 和 [Django](https://www.djangoproject.com) 构建的免费客户关系管理软件。它专为需要自托管 CRM、CRM 任务管理器、邮件营销 CRM 以及 CRM 分析软件的一体化可扩展平台的团队而设计。

[<img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/pics/deals_screenshot.png" alt="Screenshot Django-CRM" align="center" style="float: center"/>](https://github.com/DjangoCRM/django-crm/blob/main/docs/pics/deals_screenshot.png)

**项目状态：** 生产环境 / 稳定版本
已在真实商业环境中稳定运行多年。

⭐️ 如果您觉得本项目有价值，请为该仓库加星标（Star）——这有助于更多人发现这款免费开源的 Python CRM。

---

## 为什么选择 Django-CRM？

Django CRM 将 CRM 与任务管理软件、带邮件集成功能的 CRM 以及 CRM 邮件营销软件整合于一体——无需专有框架、无厂商锁定、无 SaaS 限制。

### 面向企业和终端用户

* 在一个系统中管理 **线索、商机、联系人、任务、项目和邮件营销活动**
* 用一个 **协作型 CRM 系统** 替代多个工具
* 通过内置的 **CRM 分析软件** 获取业务洞察

### 面向开发者和系统集成商

* 100% 基于 Django 框架的 Python CRM
* 无专有 UI 层——全部基于 [Django Admin](https://docs.djangoproject.com/en/dev/ref/contrib/admin/)
* 快速定制、可预测升级、简化部署
* 非常适合 **自托管 CRM** 和本地部署（on-premise）

---

## 核心 CRM 功能

| CRM & 销售        | 任务与协作     | 邮件与营销            |
| ----------------- | ------------- | -------------------- |
| 线索管理           | CRM 任务管理器 | 邮件营销 CRM         |
| 交易跟踪与预测     | 项目与子任务   | CRM 与电子邮件营销软件 |
| 公司与联系人管理   | 内部聊天       | 带邮件集成的 CRM      |
| 基于角色的访问控制 | 提醒与文件     | SMTP / IMAP 支持     |
| CRM 分析软件      | 办公备忘录     | 邮件活动自动化        |

🔎 了解更多内容请参阅：
[CRM 系统概览](https://github.com/DjangoCRM/django-crm/blob/main/docs/crm_system_overview.md)

---

## 基于 Django Admin 构建的 Python CRM

Django-CRM 是一个充分利用 **Django Admin 界面** 的 Python CRM 系统：

* 自适应后台模板（桌面与移动端）
* 高级筛选、排序与搜索
* 对象级权限控制（查看、添加、修改、删除）
* 单页后台文档系统

与其重新开发 UI 框架，Django-CRM 更专注于 **业务逻辑**、**数据完整性** 与 **可扩展性** —— 非常适合希望拥有并控制其系统的中小型企业。

---

## 主要应用模块

### CRM 应用

* 请求（咨询、事件）
* 线索与销售机会
* 公司与联系人
* 交易（销售流程）
* 产品与付款
* 与 CRM 对象关联的邮件消息

➡️ 超过 20 个相互关联的 CRM 数据模型，支持复杂销售流程。

---

### 任务与项目管理（CRM 任务管理器）

完整的 **CRM 与任务管理软件模块**：

* 任务与子任务
* 项目（任务集合）
* 办公备忘录可转换为任务或项目
* 聊天、文件、提醒、标签
* 个人与团队任务分配

🔗 [任务功能说明](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_task_features.md)

---

[<img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/pics/income_summary_thumbnail.png" alt="Analytical crm report" align="right" width="190px" style="float: right"/>](https://github.com/DjangoCRM/django-crm/blob/main/docs/pics/income_summary_screenshot.png)

### 分析模块（Analytical CRM）

内置的 **CRM 分析软件**，提供可执行的业务洞察：

* 销售漏斗分析
* 收入汇总报表
* 线索来源分析
* 请求统计

🔗 [分析模块概览](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_analytics_app_overview.md)

---

### 邮件营销 CRM

邮件营销模块提供完整的 CRM 与电子邮件营销功能：

* 邮件账户管理（SMTP / IMAP）
* 邮件活动与新闻简报
* 动态模板
* 邮件签名
* 联系人分组

使 Django-CRM 成为一个具备邮件集成与内部邮件客户端功能的 CRM 系统。

---

## 邮件客户端与集成

内置邮件客户端支持：

* SMTP 和 IMAP
* Gmail 及其他邮件服务商
* OAuth 2.0（双重认证）
* 自动邮件同步

所有邮件往来：

* 存储在 CRM 数据库中
* 自动关联到请求、线索和交易
* 通过类似工单（ticket）的机制组织管理

---

## 其他功能

* Web 表单集成（支持 reCAPTCHA v3）
* 自动地理定位
* VoIP 回拨支持
* 即时通讯集成（WhatsApp、Viber 等）
* Excel 导入/导出
* 上下文感知帮助页面
* 工具提示与内嵌文档

---

## 多语言与本地化支持

<img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/languages.svg" alt="django logo" width="30" height="30" style="vertical-align: bottom"> 支持的界面语言：

`ar, cs, de, el, en, es, fr, he, hi, id, it, ja, ko, nl, pl, pt-br, ro, ru, tr, uk, vi, zh-hans`

完整支持：

* 翻译机制
* 时区设置
* 本地化日期与时间格式

---

## 为什么选择这款免费 CRM？

* ✅ 免费客户关系管理软件
* ✅ 完全自托管
* ✅ 基于 Python 与 Django
* ✅ CRM、任务、邮件和分析集成于一体
* ✅ 适合中小企业、代理机构和企业内部系统
* ✅ 无 SaaS 订阅费用，无厂商锁定

---

## 快速开始

Django-CRM 作为标准 Django 项目运行。

用于测试和评估：

* 无需外部数据库
* 开箱即用支持 SQLite

📘 文档：

* [安装与配置指南](https://github.com/DjangoCRM/django-crm/blob/main/docs/installation_and_configuration_guide.md)
* [用户指南](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_user_guide.md)
* [在线文档](https://django-crm-admin.readthedocs.io)
* [更新日志](https://github.com/DjangoCRM/django-crm/blob/main/CHANGELOG.md)

---

## 兼容性

* <img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/django-logo.svg" alt="django logo" width="30" height="30" style="vertical-align: middle"> Django 6.0+
* <img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/python-logo.svg" alt="python logo" width="30" height="30" style="vertical-align: middle"> Python 3.12+
* <img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/mysql_logo.svg" alt="mysql logo" width="30" height="30" style="vertical-align: middle"> MySQL 8.0.11+
* <img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/postgresql_logo.svg" alt="postgresql logo" width="30" height="30" style="vertical-align: middle"> PostgreSQL 14+

兼容 Django 5.2.11 LTS 的版本可在此获取：
[https://github.com/DjangoCRM/django-crm/tree/v1.7.x-LTS](https://github.com/DjangoCRM/django-crm/tree/v1.7.x-LTS)

---

## 参与贡献

欢迎提交功能改进、问题修复和文档优化。

📄 详见：
[贡献指南](https://github.com/DjangoCRM/django-crm/blob/main/CONTRIBUTING.md)

---

## 许可证

本项目基于 **AGPL-3.0** 许可证发布。
详见 [LICENSE](https://github.com/DjangoCRM/django-crm/blob/main/LICENSE) 文件。

---

## 支持开源 ❤️

如果本项目对您有帮助，请在 GitHub 上为仓库添加 ⭐ Star —— 这将帮助更多人发现这款免费开源的 Python CRM。
