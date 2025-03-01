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

# Django-CRM

*(协作和分析客户关系管理软件)*

**Django-CRM** 是一个开源的CRM解决方案，设计有**两个主要目标**：

- **对于用户**：提供企业级开源CRM软件，具有全面的业务解决方案套件。  
- **对于开发者**：简化开发、定制和生产服务器支持的过程。

**无需学习专有框架**：所有内容都使用流行的Django框架构建。  
CRM充分利用了Django Admin站点，所有文档都包含在一个网页上！

[<img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/pics/deals_screenshot.png" alt="Django-CRM截图" align="center" style="float: center"/>](https://github.com/DjangoCRM/django-crm/blob/main/docs/pics/deals_screenshot.png)

## 客户关系管理功能

|                     |                        |                       |
|---------------------|------------------------|-----------------------|
| ☑️ **团队任务和项目**  | ☑️ **潜在客户管理**      | ☑️ **电子邮件营销**     |
| ☑️ **联系人管理**     | ☑️ **交易跟踪和销售预测** | ☑️ **基于角色的访问控制** |
| ☑️ **销售分析**       | ☑️ **内部聊天集成**      | ☑️ **移动友好设计**     |
| ☑️ **可定制报告**     | ☑️ **自动电子邮件同步**   | ☑️ **多货币支持**       |

了解更多关于[软件功能](https://github.com/DjangoCRM/django-crm/blob/main/docs/crm_system_overview.md)。

Django CRM 是一个开源的客户关系管理软件。该CRM是用<a href="https://www.python.org" target="_blank"><img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/python-logo.svg" style="vertical-align: middle" alt="python logo" width="25" height="25"> Python</a>编写的。  
前端和后端完全基于[Django Admin站点](https://docs.djangoproject.com/en/dev/ref/contrib/admin/)。  
CRM应用程序使用自适应Admin HTML模板开箱即用。  
Django是一个文档丰富的框架，提供了大量示例。  
Admin站点上的文档仅占用一个网页。  
💡 **原始想法**是，由于Django Admin已经是一个专业的对象管理界面，具有灵活的用户权限系统（查看、更改、添加和删除对象），您只需为对象（如潜在客户、请求、交易、公司等）创建模型并添加业务逻辑。

**所有这些确保**：

- **显著简化项目定制和开发**
- **简化项目部署和生产服务器支持**

该软件包提供两个网站：

- 所有用户的CRM站点
- 管理员站点

**项目成熟且稳定**，已在实际应用中成功使用多年。

## 主要应用程序

CRM软件套件包括以下**主要应用程序**及其模型：

- **任务管理应用程序**：
  （默认情况下，所有用户均可使用，无论其角色如何）
  - 任务（相关：文件、聊天、提醒、标签 - 参见[任务功能](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_task_features.md)）
    - 子任务
  - 备忘录（办公室备忘录） - 参见[备忘录功能](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_memo_features.md)
    - 任务/项目
  - 项目（*任务集合*）：
  - ...（*+ 4个<a href="https://github.com/DjangoCRM/django-crm/tree/main/tasks/models" target="_blank">模型</a>*）
- **CRM应用程序**：
  - 请求（商业询问）
  - 潜在客户（潜在客户）
  - 公司
  - 联系人（与其公司相关联）
  - 交易（如“机会”）
  - 电子邮件（与用户电子邮件帐户同步）
  - 产品（商品和服务）
  - 付款（已收到、保证、高概率和低概率）
  - ...（*+ 12个<a href="https://github.com/DjangoCRM/django-crm/tree/main/crm/models" target="_blank">模型</a>*）
[<img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/pics/income_summary_thumbnail.png" alt="分析crm报告" align="right" width="190px" style="float: right"/>](https://github.com/DjangoCRM/django-crm/blob/main/docs/pics/income_summary_screenshot.png)
- **分析应用程序**：([详细软件概述](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_analytics_app_overview.md))
  - 收入摘要报告（*参见[截图](https://github.com/DjangoCRM/django-crm/blob/main/docs/pics/income_summary_screenshot.png)*）
  - 销售漏斗报告
  - 潜在客户来源摘要报告
  - ...（*+ 5个分析报告*）
- **群发邮件应用程序**：
  - 电子邮件帐户
  - 电子邮件（新闻通讯）
  - 电子邮件签名（用户签名）
  - 邮件

## 支持应用程序

CRM软件包还包含**支持应用程序**，例如：

- 聊天应用程序（聊天在每个任务、项目、办公室备忘录和交易实例中可用）
- VoIP应用程序（从交易中联系客户）
- 帮助应用程序（根据用户角色动态帮助页面）
- 通用应用程序：
  - 🪪 用户资料
  - ⏰ 提醒（用于任务、项目、办公室备忘录和交易）
  - 📝 标签（用于任务、项目、办公室备忘录和交易）
  - 📂 文件（用于任务、项目、办公室备忘录和交易）

## 附加功能

- Web表单集成：CRM联系表单内置：
  - reCAPTCHA v3保护
  - 自动地理位置
- 用户的电子邮件帐户集成和同步。电子邮件自动：
  - 保存在CRM数据库中
  - 链接到相应的CRM对象（如：请求、潜在客户、交易等）
- VoIP回拨到智能手机
- 通过信使发送消息（如：Viber、WhatsApp等）
- Excel支持：轻松导入/导出联系人详细信息。

## 电子邮件客户端

Python CRM系统包括一个内置的电子邮件客户端，使用**SMTP**和**IMAP**协议操作。  
这使得Django-CRM能够自动存储与每个请求和交易相关的所有通信副本在其数据库中。  
该功能确保即使通过用户的外部电子邮件帐户（在CRM之外）进行通信。  
它们也会被捕获并在系统中组织，使用**票务机制**。

CRM可以与需要强制两步验证（使用**OAuth 2.0**协议）的电子邮件服务提供商（如Gmail）集成，用于第三方应用程序。

## 用户帮助  

- 每个CRM页面都包含一个上下文感知的帮助页面链接，内容根据用户角色动态调整，以提供更相关的指导。  
- 界面中提供工具提示，当悬停在图标、按钮、链接或表头上时，提供即时信息。  
- 还包括一个全面的[用户指南](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_user_guide.md)文件，以供深入参考和支持。  

## 提升团队生产力的协作CRM解决方案

该CRM旨在增强团队内的协作并简化项目管理流程。  
作为协作CRM，它允许用户轻松创建和管理备忘录、任务和项目。  
[办公室备忘录](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_memo_features.md)可以发送给部门主管或公司高管，他们可以将这些备忘录转化为任务或项目，分配负责人或执行者。  
[任务](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_task_features.md)可以是个人或集体的。  
任务提供聊天讨论、提醒、文件共享、创建子任务和共享结果等功能。  
用户直接在CRM和通过电子邮件接收通知，确保他们保持知情。  
每个用户都可以清晰地查看其任务堆栈，包括优先级、状态和下一步，从而提高生产力和协作客户关系管理中的责任感。

## 项目本地化

<img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/languages.svg" alt="django logo" width="30" height="30" style="vertical-align: middle"> 客户服务软件现已支持**多种语言**：  

`ar, cs, de, el, en, es, fr, he, hi, id, it, ja, ko, nl, pl, pt-br, ro, ru, tr, uk, vi, zh-hans`

Django CRM完全支持界面翻译、日期、时间和时区格式化。  

## 为什么选择Django-CRM？

- **自托管**：CRM应用软件设计为自托管，允许您完全控制您的CRM数据和环境。通过自托管，您可以根据特定业务需求定制CRM，并确保您的数据保持私密和安全。
- **协作CRM**：通过任务管理、项目协作和内部沟通工具提升团队生产力。
- **分析CRM**：通过内置报告（如销售漏斗、收入摘要和潜在客户来源分析）获得可操作的见解。
- **基于Python和Django**：无需学习专有框架 - 所有内容都基于Django，具有直观的管理界面。前端和后端基于Django Admin，使定制和开发项目以及部署和维护生产服务器变得更加容易。

## 入门

Django-CRM可以轻松部署为常规Django项目。

📚 请参考：

- [安装和配置指南](https://github.com/DjangoCRM/django-crm/blob/main/docs/installation_and_configuration_guide.md)
- [用户指南](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_user_guide.md)

如果您觉得Django-CRM有帮助，请在GitHub上⭐️**加星**支持其发展！

<img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/pics/Django-CRM_star_history.png" alt="Django-CRM加星历史" align="center" style="float: center"/>

### 兼容性

- <img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/django-logo.svg" alt="django logo" width="30" height="30" style="vertical-align: middle"> Django 5.1.x
- <img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/python-logo.svg" alt="python logo" width="30" height="30" style="vertical-align: middle"> Python 3.10+
- <img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/mysql_logo.svg" alt="mysql logo" width="30" height="30" style="vertical-align: middle"> MySQL 8.0.11+
- <img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/postgresql_logo.svg" alt="postgresql logo" width="30" height="30" style="vertical-align: middle"> PostgreSQL 12+  

## 贡献

欢迎贡献！有改进和新功能的空间。  
查看我们的[贡献指南](https://github.com/DjangoCRM/django-crm/blob/main/CONTRIBUTING.md)以了解如何开始。  
每一个贡献，无论大小，都会有所不同。

## 许可证

Django-CRM在AGPL-3.0许可证下发布 - 详情请参见[许可证](https://github.com/DjangoCRM/django-crm/blob/main/LICENSE)文件。

## 致谢

- Google material [icons](https://fonts.google.com/icons)。
- [NicEdit](https://nicedit.com) - WYSIWYG内容编辑器。
- 在其他许可证下使用的所有资源。