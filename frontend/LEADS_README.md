# 🎯 Leads Module - Frontend Integration

## Быстрый старт

### 1. Убедитесь, что Django сервер запущен
```bash
python manage.py runserver
```

### 2. Откройте тестовую страницу
```
http://127.0.0.1:8000/frontend/test_leads_integration.html
```

### 3. Или используйте основное приложение
```javascript
// В консоли браузера на http://127.0.0.1:8000/frontend/
app.navigateTo('leads');
```

## Основные функции

### Создание лида
```javascript
app.leads.showLeadForm();
// Заполните форму и нажмите "Create Lead"
```

### Просмотр лида
```javascript
app.leads.viewLead(leadId);
```

### Редактирование лида
```javascript
app.leads.editLead(leadId);
```

### Конвертация лида
```javascript
app.leads.convertLead(leadId);
// Выберите владельца и опцию создания сделки
```

### Bulk операции
```javascript
// Выберите несколько лидов в UI
app.leads.openBulkAssignDialog();
app.leads.openBulkTagDialog();
app.leads.openBulkDisqualifyDialog();
```

## API Примеры

### Получить список лидов
```javascript
const leads = await window.apiClient.get('leads/');
console.log(leads.results);
```

### Создать лида
```javascript
const lead = await window.apiClient.post('leads/', {
    first_name: 'John',
    last_name: 'Doe',
    email: 'john@example.com',
    company_name: 'Acme Corp'
});
```

### Поиск лидов
```javascript
const results = await window.apiClient.get('leads/?search=john');
```

### Фильтрация
```javascript
// Только активные
const active = await window.apiClient.get('leads/?disqualified=false');

// Только дисквалифицированные
const disqualified = await window.apiClient.get('leads/?disqualified=true');
```

### Конвертация лида
```javascript
const result = await window.apiClient.post(`leads/${leadId}/convert/`, {
    owner: userId,
    create_deal: true
});
// result: { lead, contact, company, deal }
```

## Структура файлов

```
frontend/
├── js/
│   ├── leads.js                    # LeadManager класс
│   ├── config.js                   # Конфигурация endpoints
│   ├── api.js                      # HTTP client
│   └── typeahead.js                # Компонент выбора
├── test_leads_integration.html     # Тестовая страница
├── LEADS_INTEGRATION_COMPLETE.md  # Полная документация
└── LEADS_README.md                # Этот файл
```

## Доступные методы LeadManager

| Метод | Описание |
|-------|----------|
| `loadLeads()` | Загрузить и отобразить список лидов |
| `showLeadForm(leadId)` | Показать форму создания/редактирования |
| `saveLead(leadId)` | Сохранить лида |
| `viewLead(leadId)` | Просмотр деталей лида |
| `editLead(leadId)` | Редактировать лида |
| `deleteLead(leadId)` | Удалить лида |
| `convertLead(leadId)` | Конвертировать в контакт/сделку |
| `disqualifyLead(leadId)` | Дисквалифицировать лида |
| `assignLead(leadId)` | Назначить владельца |
| `openBulkAssignDialog()` | Массовое назначение |
| `openBulkTagDialog()` | Массовое добавление тегов |
| `openBulkDisqualifyDialog()` | Массовая дисквалификация |

## Endpoints

Все endpoints доступны через `window.CRM_CONFIG.ENDPOINTS`:

- `LEADS` → `/api/leads/`
- `USERS` → `/api/users/`
- `CRM_TAGS` → `/api/crm-tags/`
- `STAGES` → `/api/stages/`

### Специальные действия

- `POST /api/leads/{id}/disqualify/` - Дисквалификация
- `POST /api/leads/{id}/assign/` - Назначение владельца
- `POST /api/leads/{id}/convert/` - Конвертация
- `POST /api/leads/bulk_tag/` - Массовое добавление тегов

## Тестирование

### Запустить все тесты
Откройте `test_leads_integration.html` и нажмите "Run All Tests"

### Запустить конкретный тест
```javascript
// В консоли на test_leads_integration.html
testListLeads();
testCreateLead();
testUpdateLead();
testSearchLeads();
// и т.д.
```

## Валидация

### Frontend валидация
- Требуется `first_name` ИЛИ `company_name`
- Email format
- Телефоны нормализуются автоматически

### Backend валидация
- Email уникальность
- Требуется `first_name` или `company_name`
- Автоматическая нормализация данных

## Troubleshooting

### Лиды не загружаются
1. Проверьте авторизацию: `console.log(window.apiClient.token)`
2. Проверьте endpoint: `console.log(window.CRM_CONFIG.ENDPOINTS.LEADS)`
3. Проверьте консоль на ошибки

### Форма не открывается
1. Проверьте, что `app.leads` существует
2. Проверьте консоль на ошибки JavaScript

### 403 Forbidden
1. Убедитесь, что пользователь авторизован
2. Проверьте права доступа пользователя

### Конвертация не работает
1. Убедитесь, что у вас есть права на создание контактов
2. Проверьте, что лид еще не конвертирован

## Дополнительная информация

Полная документация: `LEADS_INTEGRATION_COMPLETE.md`

## Поддержка

Для вопросов и предложений создайте issue в GitHub или обратитесь к команде разработки.

---

**Версия:** 1.0.0  
**Дата:** 2024  
**Статус:** ✅ Production Ready
