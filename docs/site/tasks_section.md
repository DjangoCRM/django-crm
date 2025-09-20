## Working in the TASKS section (for all users)

[CRM task management](https://djangocrm.github.io/info/features/tasks-app-features/){target="_blank"} allows users to work with office memos, tasks, and projects (collections of tasks).  
Participating users receive notifications about all events in [CRM application](https://docs.djangoproject.com/en/dev/ref/contrib/admin/){target="_blank"} and by email.  
!!! Important
    Only users specified in them in any role and company managers have access to specific memos, tasks, and projects.
    Other users will not see them.  
If it is necessary to regularly make edits or correct errors in these objects, the administrator can assign the "task operator" [role](adding_crm_users.md#user-groups-roles) to a user. This user will have the right to edit objects of other users.

### Chat in objects

<span style="vertical-align: baseline"><img src="../icons/chat-left-text.svg" alt="Chat icon" width="25"></span> Objects have chat. For example, in each task, all participants can discuss its implementation and share files in the chat. Accordingly, all messages will be tied to a specific task. To create a message, click the button "Message +".  
Messages are sent to users in CRM and by email.

### Reminders

<span style="vertical-align: baseline"><img src="../icons/alarm.svg" alt="alarm icon" width="25"></span> In many objects, you can create a reminder associated with this object.  
You can set the date and time when the reminder will appear in CRM and be sent by email.  
In the general section, you can see a list of all created reminders. If necessary, you can deactivate reminders that have become irrelevant.

### Tasks

Tasks can be team or individual, main or subtasks.  
The task can include subscribers. These are the users who should be notified when the task is created and completed. They can see the task.  
!!! Note 
    By default, only active tasks are displayed in the task list.  
    To see all tasks, change the filter.

If several users (responsible) are assigned to perform a task, then this is a team task. In the task list they can be distinguished by color.  
To work on a team task, performers:

- must create subtasks for themselves
- can create subtasks for each other

Tasks can have the following status:

- pending
- in progress
- done
- canceled

Django CRM automatically marks a team task as completed if each responsible person has at least one subtask and all subtasks are completed.  
In other cases, it is up to the owner (co-owner) of the task to change the status of the main task.

Users can create tasks for themselves. In this case, CRM automatically assigns a co-owner of the task to the head of the executor's department. This allows department heads to be aware of their employees' tasks.

### Memos

Users can create office memos to department or company managers to inform them or to make decisions.  
If there are users who need to know about the memo and its content, they can be specified as subscribers of this memo.  
The recipient of the memo and the subscribers will be notified and will have access to the memo.

You can save a memo with the status "draft." In this case, no notifications will be sent and only the author (owner) will have access to it.

The author can modify the memo until the recipient sets the status to "reviewed." The author will be notified of this.

A [task](#tasks) or project can be created as a result of the memo. For convenience, information from the memo is copied into them. But the recipient can modify or add to it.  
The author of the memo and the subscribers automatically become subscribers of the created task or project.

Sales managers can create a memo from a [deal](guide_for_sales_manager.md#deal-object). In this case, the "View Deal" button will appear in the memo.  
Chat is available in the memo for participants and company management.
Chat is also available in a task or project.  
It can be used, for example, to notify participants about changes that have occurred since the memo was reviewed.

In the list of memos, you can see the status of the task created for it. The color of the "View task" button reflects the status of the task. Also, if you put the mouse cursor over it, the status information appears.
