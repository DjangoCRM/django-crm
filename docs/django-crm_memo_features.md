<p align="right">
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_memo_features.md">English</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_memo_features-spanish.md">Español</a>
</p>

# Django-CRM Memo Features

In [Django-CRM](https://github.com/DjangoCRM/django-crm), a memo is an office memo that can be directed to department heads (team leads) or company executives, 
allowing users to inform them or make decisions. A user can also create memos for themselves (todo list).

---

## Roles and Access Control

Users can be in one of three roles related to a memo:

### Owner (Author)

The person who created the memo has complete control over it.

### Recipient

The person receiving the memo, typically for review or action. It can view the memo and respond to it.

### Subscriber

Users notified and allowed access to the memo. They can view the memo but cannot edit it.

---

## States of a Memo

A memo can be in one of four states:

### 1. Draft

Not visible to anyone except the author (and CRM administrators), no notifications are sent.

### 2. Pending

The memo has been sent to recipients, but they have not reviewed it yet.

### 3. Reviewed

The recipient has reviewed the memo and may have taken action or assigned [tasks](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_task_features.md)/projects.

### 4. Postponed

The memo is still pending review, but its status indicates that it was postponed for further consideration.

---

## Visibility

Only users with a relationship to the memo (owner, recipient, or subscriber) and administrators can view the memo. This ensures that sensitive information is only accessible to those who need it.

---

## Creating a Memo

To create a new memo, users can follow these steps:

1. Navigate to the Tasks section.
2. Click on the "Create" button or use the "+" icon to add a new memo.
3. Select the "Memo" option from the dropdown list.

Additionally, a new memo can be created directly from a deal, and they will be linked.

Users can create memos for:

* Themselves (todo list)
* Department heads (team leads)
* Company managers

When creating a memo, users can attach files and set reminders.

---

## Editing a Memo

To edit an existing memo, users can follow these steps:

1. Navigate to the Tasks section.
2. Search for the memo you want to edit and click on it.
3. Make any necessary changes to the memo details or attach new files.

---

## Memo Content and Collaboration

A memo contains:

* Files attached by the owner or recipients
* Chat with participants to discuss the memo's content
* Reminders for tasks or deadlines related to the memo

---

## Task/Project Creation from Memos

After a memo has been reviewed, management can create [tasks](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_task_features.md) or projects based on its content. The task/project is automatically linked to the memo, and users receive notifications.

Once a memo has been reviewed by the recipient, it cannot be changed by the owner.

---

## Task Status Display

In the list of memos, the status of associated tasks is displayed, indicating their progress.
