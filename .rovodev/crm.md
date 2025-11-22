# CRM Django и Frontend Frameworks

## Описание
Инструкция для работы с Django CRM системой и интеграции frontend фреймворков.

## Django Backend

### Структура проекта
- **apps/**: Основные модули CRM (crm, analytics, chat, common, massmail, tasks, voip)
- **models/**: Модели данных для контактов, компаний, сделок, задач
- **admin/**: Кастомизированный Django Admin интерфейс
- **api/**: REST API эндпоинты для frontend интеграции

### Ключевые модели
- `Contact` - контакты клиентов
- `Company` - компании
- `Deal` - сделки
- `Lead` - лиды
- `Task` - задачи
- `Project` - проекты
- `CrmEmail` - email коммуникации

### Работа с моделями
```python
# Пример создания контакта
from crm.models import Contact, Company

contact = Contact.objects.create(
    first_name="Иван",
    last_name="Петров",
    email="ivan@example.com",
    phone="+79001234567"
)
```

## Frontend Интеграция

### Статические файлы
- `static/` - статические ресурсы
- Используется Django's `collectstatic` для сборки
- CSS файлы в `*/static/*/css/`
- JS файлы в `*/static/*/js/`

### Шаблоны
- Django templates в `*/templates/`
- Наследование от `admin/base.html`
- Кастомные виджеты в `common/templates/common/widgets/`

### JavaScript интеграция
```javascript
// Пример AJAX запроса к API
fetch('/api/contacts/', {
    method: 'GET',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
    }
})
.then(response => response.json())
.then(data => console.log(data));
```

### CSS фреймворки
- Bootstrap готов к интеграции
- Кастомные стили в `common/static/common/css/`
- Поддержка responsive дизайна

## API Endpoints

### Основные эндпоинты
- `/api/contacts/` - управление контактами
- `/api/companies/` - управление компаниями  
- `/api/deals/` - управление сделками
- `/api/tasks/` - управление задачами

### Аутентификация
```python
# В settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}
```

## Frontend фреймворки

### React интеграция
```jsx
// Компонент списка контактов
import React, { useState, useEffect } from 'react';

function ContactList() {
    const [contacts, setContacts] = useState([]);
    
    useEffect(() => {
        fetch('/api/contacts/')
            .then(res => res.json())
            .then(data => setContacts(data));
    }, []);
    
    return (
        <div>
            {contacts.map(contact => (
                <div key={contact.id}>
                    {contact.first_name} {contact.last_name}
                </div>
            ))}
        </div>
    );
}
```

### Vue.js интеграция
```vue
<template>
  <div>
    <div v-for="contact in contacts" :key="contact.id">
      {{ contact.first_name }} {{ contact.last_name }}
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      contacts: []
    }
  },
  async mounted() {
    const response = await fetch('/api/contacts/');
    this.contacts = await response.json();
  }
}
</script>
```

## Рекомендации

### Разработка
1. Используйте Django REST Framework для API
2. Применяйте Django's CSRF защиту
3. Кэшируйте статические файлы
4. Используйте Django's i18n для многоязычности

### Производительность
1. Оптимизируйте запросы к БД с `select_related()`/`prefetch_related()`
2. Используйте Django's кэширование
3. Минифицируйте CSS/JS файлы
4. Используйте CDN для статических файлов

### Безопасность
1. Валидируйте данные на backend
2. Используйте Django's встроенную защиту от XSS
3. Настройте CORS для API запросов
4. Применяйте rate limiting для API

## Примеры кастомизации

### Кастомный admin виджет
```python
from django.contrib.admin import ModelAdmin

class ContactAdmin(ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'phone']
    search_fields = ['first_name', 'last_name', 'email']
    list_filter = ['created', 'modified']
```

### Кастомное API представление
```python
from rest_framework.viewsets import ModelViewSet
from .models import Contact
from .serializers import ContactSerializer

class ContactViewSet(ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    
    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)
```