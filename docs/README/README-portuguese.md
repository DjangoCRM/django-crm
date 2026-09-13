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

*(Software de Gestão de Relacionamento com o Cliente Colaborativo e Analítico)*

**Django-CRM** é uma solução CRM de código aberto projetada com dois objetivos principais:

- **Para usuários**: Oferecer software CRM de nível empresarial de código aberto com um conjunto abrangente de soluções de negócios.
- **Para desenvolvedores**: Simplificar os processos de desenvolvimento, personalização e suporte ao servidor de produção.

**Não há necessidade de aprender um framework proprietário**: tudo é construído usando o popular framework Django.
O CRM também aproveita ao máximo o site de administração do Django, com documentação contida em uma única página da web!

[<img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/pics/deals_screenshot.png" alt="Screenshot Django-CRM" align="center" style="float: center"/>](https://github.com/DjangoCRM/django-crm/blob/main/docs/pics/deals_screenshot.png)

## Recursos de Gestão de Relacionamento com o Cliente
|                                     |                                                        |                                              |
|-------------------------------------|--------------------------------------------------------|----------------------------------------------|
| ☑️ **Tarefas e Projetos em Equipe** | ☑️ **Gestão de Leads**                                 | ☑️ **Marketing por Email**                   |
| ☑️ **Gestão de Contatos**           | ☑️ **Acompanhamento de Negócios e Previsão de Vendas** | ☑️ **Controle de Acesso Baseado em Funções** |
| ☑️ **Análise de Vendas**            | ☑️ **Integração de Chat Interno**                      | ☑️ **Design Responsivo**                     |
| ☑️ **Relatórios Personalizáveis**   | ☑️ **Sincronização Automática de Email**               | ☑️ **Suporte a Múltiplas Moedas**            |

Saiba mais sobre [as capacidades do software](https://github.com/DjangoCRM/django-crm/blob/main/docs/crm_system_overview.md).

Django CRM é um software de gestão de relacionamento com o cliente de código aberto.  
Este CRM é escrito em <a href="https://www.python.org" target="_blank"><img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/python-logo.svg" style="vertical-align: middle" alt="python logo" width="25" height="25"> Python</a>.
Frontend e backend são totalmente baseados no site de administração do Django [Admin site](https://docs.djangoproject.com/en/dev/ref/contrib/admin/).
O aplicativo CRM usa templates HTML adaptativos do Admin prontos para uso.
Django é um framework excelentemente documentado com muitos exemplos.
A documentação no site de administração ocupa apenas uma página da web.  
💡 A **ideia original** é que, como o Django Admin já é uma interface profissional de gerenciamento de objetos com um sistema de permissões flexível para usuários (visualizar, alterar, adicionar e excluir objetos), tudo o que você precisa fazer é criar modelos para os objetos (como Leads, Solicitações, Negócios, Empresas, etc.) e adicionar lógica de negócios.

**Tudo isso garante**:

- **personalização e desenvolvimento de projetos significativamente mais fáceis**
- **implantação de projetos e suporte ao servidor de produção mais simples**

O pacote de software fornece dois sites:

1. site CRM para todos os usuários
2. site para administradores

O **projeto é maduro e estável**, e tem sido usado com sucesso em aplicações reais por muitos anos.

## Principais Aplicações

O pacote de software CRM consiste nas seguintes **principais aplicações** e seus modelos:

- **Aplicativo de Gestão de TAREFAS**:
  (disponível para todos os usuários por padrão, independentemente de seu papel)
  - Tarefa (com relacionados: arquivos, chat, lembretes, tags - veja [recursos da tarefa](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_task_features.md))
    - subtarefas
  - Memorando (memorando de escritório) - veja [recursos do memorando](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_memo_features.md)
    - tarefas / projeto
  - Projeto (*coleção de tarefas*):
  - ... (+ *4 mais <a href="https://github.com/DjangoCRM/django-crm/tree/main/tasks/models" target="_blank">modelos</a>*)
- **Aplicativo CRM**:
  - Solicitações (consultas comerciais)
  - Leads (potenciais clientes)
  - Empresas
  - Pessoas de contato (associadas às suas empresas)
  - Negócios (como "Oportunidades")
  - Mensagens de email (sincronização com contas de email do usuário)
  - Produtos (bens e serviços)
  - Estrutura de preços
  - Pagamentos (recebidos, garantidos, alta e baixa probabilidade)
  - ... (*+ 12 mais <a href="https://github.com/DjangoCRM/django-crm/tree/main/crm/models" target="_blank">modelos</a>*)
[<img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/pics/income_summary_thumbnail.png" alt="Relatório analítico crm" align="right" width="190px" style="float: right"/>](https://github.com/DjangoCRM/django-crm/blob/main/docs/pics/income_summary_screenshot.png)
- **Aplicativo de ANÁLISE**: (visão geral detalhada do software [aqui](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_analytics_app_overview.md))
  - Relatório de Resumo de Renda (*veja [screenshot](https://github.com/DjangoCRM/django-crm/blob/main/docs/pics/income_summary_screenshot.png)*)
  - Relatório de funil de vendas
  - Relatório de resumo de fonte de leads
  - ... (+ *5 mais relatórios analíticos*)
- **Aplicativo de EMAIL EM MASSA**:
  - Contas de Email
  - Mensagens de Email (boletins informativos)
  - Assinaturas de Email (assinaturas de usuário)
  - Mailings

## Aplicativos de Suporte

O pacote CRM também contém **aplicativos de suporte** como:

- Aplicativo de Chat (chat disponível em cada instância de uma tarefa, projeto, memorando de escritório e negócio)
- Aplicativo VoIP (contato com clientes a partir de negócios)
- Aplicativo de Ajuda (páginas de ajuda dinâmicas dependendo do papel do usuário)
- Aplicativo Comum:
  - 🪪 Perfis de usuário
  - ⏰ Lembretes (para tarefas, projetos, memorandos de escritório e negócios)
  - 📝 Tags (para tarefas, projetos, memorandos de escritório e negócios)
  - 📂 Arquivos (para tarefas, projetos, memorandos de escritório e negócios)

## Funcionalidade Adicional

- Integração com formulário web: O formulário de contato do CRM possui:
  - proteção reCAPTCHA v3
  - geolocalização automática
- Integração e sincronização da conta de e-mail do utilizador. As mensagens de e-mail são automaticamente:
  - salvas no banco de dados do CRM
  - vinculadas aos objetos apropriados do CRM (como: solicitações, leads, negócios, etc.)
- Callback VoIP para smartphone
- Envio de mensagens via mensageiros (como: Viber, WhatsApp, ...)
- Suporte a Excel: Importação/exportação de detalhes de contato com facilidade.

## Cliente de Email

O sistema CRM em Python inclui um cliente de e-mail integrado que opera usando os protocolos **SMTP** e **IMAP**.
Isso permite que o Django-CRM armazene automaticamente cópias de toda a correspondência relacionada a cada solicitação e negócio dentro de seu banco de dados.
A funcionalidade garante que, mesmo que as comunicações ocorram através da conta de e-mail externa do usuário (fora do CRM).
Elas são capturadas e organizadas dentro do sistema usando um **mecanismo de ticket**.

O CRM pode se integrar com provedores de serviços de email (como o Gmail) que exigem autenticação em duas etapas obrigatória (usando o protocolo **OAuth 2.0**) para aplicativos de terceiros.

## Assistência ao Usuário

- Cada página do CRM inclui um link para uma página de ajuda contextual, com conteúdo dinamicamente adaptado ao papel do usuário para uma orientação mais relevante.
- Dicas de ferramentas estão disponíveis em toda a interface, fornecendo informações instantâneas ao passar o mouse sobre elementos como ícones, botões, links ou cabeçalhos de tabela.
- Um abrangente [guia do usuário](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_user_guide.md) também está incluído para referência e suporte detalhados.

## Aumente a Produtividade da Sua Equipe com Soluções Colaborativas de CRM

Este CRM é projetado para melhorar a colaboração dentro das equipes e simplificar os processos de gestão de projetos.
Como um CRM colaborativo, ele permite que os usuários criem e gerenciem memorandos, tarefas e projetos com facilidade.
[Memorandos de escritório](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_memo_features.md) podem ser direcionados a chefes de departamento ou executivos da empresa, que podem então transformar esses memorandos em tarefas ou projetos, atribuindo pessoas responsáveis ou executores.
[Tarefas](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_task_features.md) podem ser individuais ou coletivas.
As tarefas fornecem recursos como discussões em chat, lembretes, compartilhamento de arquivos, criação de subtarefas e compartilhamento de resultados.
Os usuários recebem notificações diretamente no CRM e por email, garantindo que estejam informados.
Cada usuário tem uma visão clara de sua pilha de tarefas, incluindo prioridades, status e próximos passos, aumentando assim a produtividade e a responsabilidade na gestão colaborativa de relacionamento com o cliente.

## Localização do Projeto

<img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/languages.svg" alt="django logo" width="30" height="30" style="vertical-align: middle"> O software de atendimento ao cliente está agora disponível em **múltiplos idiomas**:  
`ar, cs, de, el, en, es, fr, he, hi, id, it, ja, ko, nl, pl, pt-br, ro, ru, tr, uk, vi, zh-hans`
O Django CRM tem suporte completo para tradução de interface, formatação de datas, horários e fusos horários.

## Por que Escolher o Django-CRM?

- **CRM Colaborativo**: Aumente a produtividade da equipe com ferramentas para gestão de tarefas, colaboração em projetos e comunicação interna.
- **CRM Analítico**: Obtenha insights acionáveis com relatórios integrados como funil de vendas, resumo de renda e análise de fonte de leads.
- **Baseado em Python e Django**: Sem necessidade de frameworks proprietários - tudo é construído no Django com uma interface de administração intuitiva.
- **Python e Django-Based**: Não é necessário aprender um framework proprietário - tudo construído em Django com uma interface de administração intuitiva. O frontend e o backend, baseados em Django Admin, tornam muito mais fácil projetos de customização e desenvolvimento, bem como implantar e manter um servidor de produção.

## Começando

O Django-CRM pode ser facilmente implantado como um projeto Django regular.

📚 Por favor, consulte:

- [Guia de Instalação e Configuração](https://github.com/DjangoCRM/django-crm/blob/main/docs/installation_and_configuration_guide.md)
- [Guia do Usuário](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_user_guide.md)

Se você achar o Django-CRM útil, por favor, ⭐️ **estrele** este repositório no GitHub para apoiar o seu crescimento!

<img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/pics/Django-CRM_star_history.png" alt="Django-CRM star history" align="center" style="float: center"/>

### Compatibilidade

- <img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/django-logo.svg" alt="django logo" width="30" height="30" style="vertical-align: middle"> Django 5.1.x
- <img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/python-logo.svg" alt="python logo" width="30" height="30" style="vertical-align: middle"> Python 3.10+
- <img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/mysql_logo.svg" alt="mysql logo" width="30" height="30" style="vertical-align: middle"> MySQL 8.0.11+
- <img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/postgresql_logo.svg" alt="postgresql logo" width="30" height="30" style="vertical-align: middle"> PostgreSQL 12+

## Contribuindo

Contribuições são bem-vindas! Há espaço para melhorias e novos recursos.
Confira o nosso [Guia de Contribuição](https://github.com/DjangoCRM/django-crm/blob/main/CONTRIBUTING.md) para aprender como começar.
Cada contribuição, grande ou pequena, faz a diferença.

## Licença

O Django-CRM é lançado sob a licença AGPL-3.0 - veja o arquivo [LICENSE](https://github.com/DjangoCRM/django-crm/blob/main/LICENSE) para detalhes.

## Créditos

- Ícones do Google material [icons](https://fonts.google.com/icons).
- [NicEdit](https://nicedit.com) - Editor de Conteúdo WYSIWYG.
- Todos os recursos utilizados sob outras licenças.