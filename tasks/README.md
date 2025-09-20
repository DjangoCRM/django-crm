# Tasks Module for CRM

Welcome to the [Task management software](https://djangocrm.github.io/info/features/tasks-app-features/) directory of [the CRM](https://github.com/DjangoCRM/django-crm/) project.
This module provides advanced **CRM task management** features, enabling users to efficiently create, assign, track, and collaborate on tasks within a unified CRM and task management software environment. This can be done either independently or as part of broader CRM workflows.

## Overview

This README provides an overview of the task system's structure, features, usage patterns, and its role as a **CRM task manager** within the larger CRM and task management stack.  
The Tasks management app is designed to enhance productivity and organization for teams and individuals. It integrates with project workflows, supports individual and team tasks, and facilitates communication between team members. As a core part of the CRM task manager, it ensures that all task-related activities are efficiently managed within the CRM. This integration makes Django CRM a true CRM and task management solution — avoiding the need for separate external tools.

## 📂 Directory Structure

The /tasks directory includes models, views, templates, and utilities for managing tasks. Almost all files are in Python, with some HTML templates for the admin interface. The structure is as follows:

- `admin.py` — Admin interface configuration for task models.
- `apps.py` — App registration for Django.
- `forms.py` — Forms for creating and editing tasks.
- `settings.py` — App-specific settings.
- `urls.py` — URL routing for task-related views.
- `fixtures/` — Initial data for stages and resolutions.
- `migrations/` — Database migration files.
- `models/` — Defines core models, including task, project, memo, and metadata fields like status, priority, and tags.:
  - `memo.py`, `project.py`, `projectstage.py`, `resolution.py`, `stagebase.py`, `tag.py`, `task.py`, `taskbase.py`, `taskstage.py`
- `site/` — CRM site configuration for tasks, projects, tags, and memos.
- `templates/admin/tasks/` — Custom HTML templates for task, project, and memo management.
- `utils/` — Utility functions and filters for views.
- `views/` — Views for task creation and completion.

## Key Features

### Task Creation & Assignment

- Users can create tasks for themselves or assign them to others.
- Add subtasks to break down work into manageable parts.
- Associate tasks with projects for integrated project management.
- Attach files and tags for better organization.

### Roles & Permissions

- **Owners & Co-Owners**: Manage tasks and share rights.
- **Responsible**: Executors for task completion.
- **Subscribers**: Receive updates and notifications.
- **Operators**: Optional administrators with advanced permissions.

### Status & Stages

- Default stages: Pending, In Progress, Completed, Postponed, Canceled.
- Status updates by executors, owners, or operators.
- Automated status changes for team tasks based on subtask progress.

### 🧑‍🤝‍🧑 Notifications & Communication

- Email and CRM alerts for all participants on task updates.
- Built-in chat for collaboration, file sharing, and discussions.

### 🏷 Filtering, Sorting & Tagging

- Filter tasks by owner, responsible, status, tags, creation date, and projects.
- Default sort: creation date; suggested sort: "Next Step" date for better prioritization.
- Custom tags help categorize tasks by context (e.g., "Marketing", "Meeting").

### ⏰ Reminders and Planning

- Users can set personal reminders for task deadlines, ensuring timely completion.
- The "Next Step" field enables forward planning by logging future actions and deadlines.

### 🧩 Special Features

- Сollective tasks and subtasks for team collaboration.
- Automatic progress tracking and visibility for managers.
- Cross-department assignment for breaking organizational silos.

## Related Documentation

For more detailed information on the tasks module, please refer to the following documentation:

- [CRM documentation](https://django-crm-admin.readthedocs.io/en/latest/tasks_section/) site
- [Tasks app](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_task_features.md) features

## Feedback & Contributing

Contributions to the **Task management software** module are welcome! Please submit issues or pull requests.
