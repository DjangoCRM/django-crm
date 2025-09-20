<p align="right">
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_task_features.md">English</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_task_features-spanish.md">Español</a>
</p>

# Detailed Overview of the Task features for Django-CRM Users

The **Task app in [Django-CRM](https://github.com/DjangoCRM/django-crm)** streamlines task management,
enabling users to create, assign, track, and collaborate on tasks efficiently.
It supports individual and team tasks, integrates with project workflows,
and ensures seamless communication between team members.

---

## Core Features

### Task Creation

- Tasks can be created by users for themselves or assigned by department heads and management.
- Subtasks can be added to break down work into smaller, manageable parts.
- Tasks can be associated with projects for streamlined project management.
- Files and tags can be attached to tasks for better organization.

#### Steps to Create a Task

1. Navigate to the "Tasks" section from the home page.
2. Click "Create Task" and fill in details:
   - Task name, description, due date, priority (high/medium/low).
   - Assign tasks to users or teams.
   - Optionally, specify subscribers and attach relevant files.
   - Save to notify participants.

---

#### Task Roles

- **Task Owners and Co-Owners**: Those who create tasks and share managerial rights with co-owners (e.g., department heads by default).
- **Responsible (Executors)**: Individuals accountable for task execution.
- **Subscribers**: Notified about task progress or updates.
- **Task Operators**: Optional administrators with ownership-level permissions.

---

#### Task Status and Stages

- Tasks move through customizable statuses:  
  *Pending*, *In Progress*, *Completed*, *Postponed*, and *Canceled*.
- Status updates can be made by executors, owners, or operators. In team tasks, status changes are partially automated based on subtask progress.

---

#### Task Notifications and Chat

- **Notifications:**
  - All participants (owners, executors, subscribers) receive email and CRM alerts for task updates, including status changes and completions.
- **Chat:**
  - Built-in messaging for collaboration, file sharing, and task discussions.
  - Accessible via the "Message+" button, which transforms into a "Chat" button after use.

---

#### Task Filters, Sorting, and Tags

- **Filters:**
- Located to the right of the task list for refining results.
- Includes criteria like status, priority, and due date.
- **Sorting:**
- Default: By creation date.
- Recommended: By "Next Step" date for active task prioritization.
- **Tags:**
- Custom tags can label tasks (e.g., "Production Meeting").
- Tasks can be filtered by tags.

---

## Special Features

1. **Subtasks and Team Tasks**
   - Tasks can be broken down into subtasks for better organization.
   - In team tasks:
      - Executors create subtasks for themselves or others.
      - Main task status updates automatically based on subtask progress.
      - Executors can hide the main task from their list if their subtasks are completed.

2. **Notifications**:
   - Participants are notified of task creation, updates, and completion via email and CRM alerts.

3. **Reminders**:
   - Personal reminders for deadlines and meetings can be set using the calendar view or task details.

4. **Next Step Field**:
   - Enter planned actions and their deadlines for clarity and better workflow tracking.
   - Automatically updates the task's workflow and impacts sorting in the task list.

---

## **How Teams Use the Task App**

1. **Team Tasks**:
   - Performers create subtasks for themselves and others.
   - Automatic updates ensure visibility into task progress, with notifications reducing manual follow-ups.

2. **Progress Tracking**:
   - Clear visibility into *Pending*, *In Progress*, and *Completed* tasks.
   - Managers can use filters to monitor individual or team workloads.

3. **Cross-Department Collaboration**:
   - Subtasks can be assigned across departments, breaking organizational silos.

---

## **Best Practices**

- **Self-Tasking**: When receiving verbal assignments, create tasks in the CRM to ensure proper tracking and transparency.
- **Tagging**: Use meaningful tags for quick sorting and retrieval.
- **Stage Updates**: Keep task stages updated for real-time tracking by other participants.
- **Completion Check**: Always mark tasks as "Done" to notify stakeholders and remove them from active lists.

The Task app in **Django-CRM** combines simplicity and powerful features to streamline task management and collaboration, ensuring projects progress efficiently.
