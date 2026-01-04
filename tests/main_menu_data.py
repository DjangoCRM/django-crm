from django.conf import settings
from django.contrib.admin.models import LogEntry

PREFIX = settings.SECRET_CRM_PREFIX
ADMIN_PREFIX = settings.SECRET_ADMIN_PREFIX

reminder_iconed_name = 'Reminders <i class="material-icons" ' \
                       'style="font-size: 17px;vertical-align: middle;">alarm</i>'
userprofile_iconed_name = 'User profiles <i class="material-icons" ' \
                           'style="font-size: 17px;vertical-align: middle;">people</i>'


def get_perms(add: bool = True,
              change: bool = True,
              delete: bool = True,
              view: bool = True):
    return {'add': add, 'change': change, 'delete': delete, 'view': view}


# -- Data for Analytics Application Models -- #

def get_incomestat_model_data(prefix: str = '') -> dict:
    prefix = prefix or PREFIX
    return {
        'name': 'Income Summary',
        'object_name': 'IncomeStat',
        'perms': get_perms(add=False, change=False, delete=False),
        'admin_url': f'/en/{prefix}analytics/incomestat/',
        'add_url': None,
        'view_only': True
    }


# -- Data for CRM Application Models --

def get_company_model_data(prefix: str = '',
                            perms: dict = {},   # NOQA
                            view_only: bool = True,
                            is_add_url: bool = False,
                            ) -> dict:
    perms = get_perms(**perms)
    prefix = prefix or PREFIX
    add_url = f'/en/{prefix}crm/company/add/' if is_add_url else None
    return {
        'name': 'Companies',
        'object_name': 'Company',
        'perms': perms,
        'admin_url': f'/en/{prefix}crm/company/',
        'add_url': add_url,
        'view_only': view_only
    }


def get_contact_model_data(prefix: str = '',
                            perms: dict = {},   # NOQA
                            view_only: bool = True,
                            is_add_url: bool = False,
                            ) -> dict:
    perms = get_perms(**perms)
    prefix = prefix or PREFIX
    add_url = f'/en/{prefix}crm/contact/add/' if is_add_url else None
    return {
        'name': 'Contact persons',
        'object_name': 'Contact',
        'perms': perms,
        'admin_url': f'/en/{prefix}crm/contact/',
        'add_url': add_url,
        'view_only': view_only
    }


def get_deal_model_data(prefix: str = '',
                            perms: dict = {'add':False},   # NOQA
                            view_only: bool = True,
                            is_add_url: bool = False,
                            ) -> dict:
    perms = get_perms(**perms)
    prefix = prefix or PREFIX
    add_url = f'/en/{prefix}crm/deal/add/' if is_add_url else None
    return {
        'object_name': 'Deal',
        'perms': perms,
        'admin_url': f'/en/{prefix}crm/deal/',
        'add_url': add_url,
        'view_only': view_only
    }


def get_shipment_model_data(prefix: str = '',
                            perms: dict = {},   # NOQA
                            view_only: bool = True,
                            is_add_url: bool = False,
                            ) -> dict:
    perms = get_perms(**perms)
    prefix = prefix or PREFIX
    add_url = f'/en/{prefix}crm/shipment/add/' if is_add_url else None
    return {
        'object_name': 'Shipment',
        'perms': perms,
        'admin_url': f'/en/{prefix}crm/shipment/',
        'add_url': add_url,
        'view_only': view_only
    }


# -- Data for Common Application Models -- #

def get_department_model_data(prefix: str = '') -> dict:
    prefix = prefix or PREFIX
    return {
        'name': 'Departments',
        'object_name': 'Department',
        'perms': get_perms(),
        'admin_url': f'/en/{prefix}common/department/',
        'add_url': f'/en/{prefix}common/department/add/',
        'view_only': False
    }


def get_thefile_model_data(prefix: str = '') -> dict:
    prefix = prefix or PREFIX
    return {
        'name': 'Files',
        'object_name': 'TheFile',
        'perms': get_perms(),
        'admin_url': f'/en/{prefix}common/thefile/',
        'add_url': f'/en/{prefix}common/thefile/add/',
        'view_only': False
    }


def get_publicemaildomain_model_data(name: str = '', prefix: str = '') -> dict:
    prefix = prefix or PREFIX
    name = name or "Public email domains"
    return {
        'name': name,
        'object_name': 'PublicEmailDomain',
        'perms': get_perms(),
        'admin_url': f'/en/{prefix}settings/publicemaildomain/',
        'add_url': f'/en/{prefix}settings/publicemaildomain/add/',
        'view_only': False
    }


def get_reminder_model_data(name: str = '', prefix: str = '', add: bool = False) -> dict:
    prefix = prefix or PREFIX
    name = name or "Reminders"
    return {
        'name': name,
        'object_name': 'Reminder',
        'perms': get_perms(add=add),
        'admin_url': f'/en/{prefix}common/reminder/',
        'add_url': f'/en/{prefix}common/reminder/add/' if add else None,
        'view_only': False
    }


def get_stopphrase_model_data(name: str = '', prefix: str = '') -> dict:
    prefix = prefix or PREFIX
    name = name or "Stop Phrases"
    return {
        'name': name,
        'object_name': 'StopPhrase',
        'perms': get_perms(),
        'admin_url': f'/en/{prefix}settings/stopphrase/',
        'add_url': f'/en/{prefix}settings/stopphrase/add/',
        'view_only': False
    }


def get_userprofile_model_data(name: str = '',
                               prefix: str = '',
                               perms: dict = {},
                               is_add_url: bool = False,
                               view_only: bool = True,) -> dict:
    perms = get_perms(**perms) if perms else get_perms(add=False, change=False, delete=False)
    prefix = prefix or PREFIX
    name = name or "User profiles"
    add_url = f'/en/{prefix}common/userprofile/add/' if is_add_url else None
    return {
        'name': name,
        'object_name': 'UserProfile',
        'perms': perms,
        'admin_url': f'/en/{prefix}common/userprofile/',
        'add_url': add_url,
        'view_only': view_only
    }


# -- Data for Tasks Application Models -- #

def get_memo_model_data(prefix: str = '',
                        perms: dict = {},   # NOQA
                        is_add_url: bool = False) -> dict:
    perms = get_perms(**perms)
    prefix = prefix or PREFIX
    add_url = f'/en/{prefix}tasks/memo/add/' if is_add_url else None
    return {
        'name': 'Memos',
        'object_name': 'Memo',
        'perms': perms,
        'admin_url': f'/en/{prefix}tasks/memo/',
        'add_url': add_url,
        'view_only': False
    }


def get_projectstage_model_data(prefix: str = '') -> dict:
    prefix = prefix or PREFIX
    return {
        'name': 'Project stages',
        'object_name': 'ProjectStage',
        'perms': get_perms(),
        'admin_url': f'/en/{prefix}tasks/projectstage/',
        'add_url': f'/en/{prefix}tasks/projectstage/add/',
        'view_only': False
    }


def get_tag_model_data(prefix: str = '') -> dict:
    prefix = prefix or PREFIX
    return {
        'name': 'Tags',
        'object_name': 'Tag',
        'perms': get_perms(),
        'admin_url': f'/en/{prefix}tasks/tag/',
        'add_url': f'/en/{prefix}tasks/tag/add/',
        'view_only': False
    }


def get_taskstage_model_data(prefix: str = '') -> dict:
    prefix = prefix or PREFIX
    return {
        'name': 'Task stages',
        'object_name': 'TaskStage',
        'perms': get_perms(),
        'admin_url': f'/en/{prefix}tasks/taskstage/',
        'add_url': f'/en/{prefix}tasks/taskstage/add/',
        'view_only': False
    }


def get_resolution_model_data(prefix: str = '') -> dict:
    prefix = prefix or PREFIX
    return {
        'name': 'Resolutions',
        'object_name': 'Resolution',
        'perms': get_perms(),
        'admin_url': f'/en/{prefix}tasks/resolution/',
        'add_url': f'/en/{prefix}tasks/resolution/add/',
        'view_only': False
    }


# -- APP Data -- #

def get_analytics_app_data(prefix: str = '') -> dict:
    prefix = prefix or PREFIX
    return {
        'name': 'Analytics',
        'app_label': 'analytics',
        'app_url': f'/en/{prefix}analytics/',
        'has_module_perms': True,
        'models': [
            {
                'name': 'Closing reason Summary',
                'object_name': 'ClosingReasonStat',
                'perms': get_perms(add=False, change=False, delete=False),
                'admin_url': f'/en/{prefix}analytics/closingreasonstat/',
                'add_url': None,
                'view_only': True
            },
            {
                'name': 'Conversion Summary',
                'object_name': 'ConversionStat',
                'perms': get_perms(add=False, change=False, delete=False),
                'admin_url': f'/en/{prefix}analytics/conversionstat/',
                'add_url': None,
                'view_only': True
            },
            {
                'name': 'Deal Summary',
                'object_name': 'DealStat',
                'perms': get_perms(add=False, change=False, delete=False),
                'admin_url': f'/en/{prefix}analytics/dealstat/',
                'add_url': None,
                'view_only': True
            },
            get_incomestat_model_data(prefix),
            {
                'name': 'Lead source Summary',
                'object_name': 'LeadSourceStat',
                'perms': get_perms(add=False, change=False, delete=False),
                'admin_url': f'/en/{prefix}analytics/leadsourcestat/',
                'add_url': None,
                'view_only': True
            },
            {
                'name': 'Requests Summary',
                'object_name': 'RequestStat',
                'perms': get_perms(add=False, change=False, delete=False),
                'admin_url': f'/en/{prefix}analytics/requeststat/',
                'add_url': None,
                'view_only': True
            },
            {
                'name': 'Sales Report',
                'object_name': 'OutputStat',
                'perms': get_perms(add=False, change=False, delete=False),
                'admin_url': f'/en/{prefix}analytics/outputstat/',
                'add_url': None,
                'view_only': True
            },
            {
                'name': 'Sales funnel',
                'object_name': 'SalesFunnel',
                'perms': get_perms(add=False, change=False, delete=False),
                'admin_url': f'/en/{prefix}analytics/salesfunnel/',
                'add_url': None,
                'view_only': True
            }
        ]
    }


def get_common_app_data(add_models: tuple = tuple(), prefix: str = '') -> dict:
    prefix = prefix or PREFIX
    if add_models:
        models = [*add_models]
    else:
        models = [
            get_reminder_model_data(name=reminder_iconed_name),
            get_userprofile_model_data(name=userprofile_iconed_name),
        ]
    return {
        'name': 'Common',
        'app_label': 'common',
        'app_url': f'/en/{prefix}common/',
        'has_module_perms': True,
        'models': models
    }


def get_task_app_data(add_models: tuple = tuple(), prefix: str = '') -> dict:
    prefix = prefix or PREFIX
    models = [
        {
            'name': 'Projects',
            'object_name': 'Project',
            'perms': get_perms(),
            'admin_url': f'/en/{prefix}tasks/project/',
            'add_url': f'/en/{prefix}tasks/project/add/',
            'view_only': False
        },
        {
            'name': 'Tasks',
            'object_name': 'Task',
            'perms': get_perms(),
            'admin_url': f'/en/{prefix}tasks/task/',
            'add_url': f'/en/{prefix}tasks/task/add/',
            'view_only': False
        }
    ]
    if add_models:
        models.extend([*add_models])
    return {
        'name': 'Tasks',
        'app_label': 'tasks',
        'app_url': f'/en/{prefix}tasks/',
        'has_module_perms': True,
        'models': models
    }


# -- Output Data -- #

DATA = [
    (
        'Olga.Co-worker.Global',  # 'username'
        [
            get_task_app_data(add_models=(get_memo_model_data(is_add_url=True),)),
            get_common_app_data()
        ]  # 'correct_app_list'
    ),
    (
        'Ekaterina.Task_operator',
        [
            get_task_app_data(add_models=(
                get_memo_model_data(is_add_url=True),
                get_resolution_model_data(),
                get_tag_model_data()
            )),
            {
                'name': 'Crm',
                'app_label': 'crm',
                'app_url': f'/en/{PREFIX}crm/',
                'has_module_perms': True,
                'models': [
                    get_shipment_model_data(perms={'add': False, 'change': False, 'delete': False}),
                ]
            },
            get_common_app_data()
        ]
    ),
    (
        'Garry.Chief',
        [
            get_task_app_data(add_models=(get_memo_model_data(is_add_url=True),)),
            {
                'name': 'Crm',
                'app_label': 'crm',
                'app_url': f'/en/{PREFIX}crm/',
                'has_module_perms': True,
                'models': [
                    get_company_model_data(perms={'add': False, 'change': False, 'delete': False}),
                    get_contact_model_data(perms={'add': False, 'change': False, 'delete': False}),
                    get_deal_model_data(perms={'add': False, 'delete': False}, view_only=False),
                    {
                        'name': 'Emails in CRM',
                        'object_name': 'CrmEmail',
                        'perms': get_perms(add=False, change=False, delete=False),
                        'admin_url': f'/en/{PREFIX}crm/crmemail/',
                        'add_url': None,
                        'view_only': True
                    },
                    {
                        'name': 'Leads',
                        'object_name': 'Lead',
                        'perms': get_perms(add=False, change=False, delete=False),
                        'admin_url': f'/en/{PREFIX}crm/lead/',
                        'add_url': None,
                        'view_only': True
                    },
                    {
                        'name': 'Payments',
                        'object_name': 'Payment',
                        'perms': get_perms(add=False, change=False, delete=False),
                        'admin_url': f'/en/{PREFIX}crm/payment/', 'add_url': None,
                        'view_only': True
                    },
                    {
                        'name': 'Products',
                        'object_name': 'Product',
                        'perms': get_perms(add=False, change=False, delete=False),
                        'admin_url': f'/en/{PREFIX}crm/product/',
                        'add_url': None,
                        'view_only': True
                    },
                    {
                        'name': 'Requests',
                        'object_name': 'Request',
                        'perms': get_perms(add=False, change=False, delete=False),
                        'admin_url': f'/en/{PREFIX}crm/request/',
                        'add_url': None,
                        'view_only': True
                    },
                    get_shipment_model_data(
                        perms={'add': False, 'change': False, 'delete': False}
                    ),
                ]
            },
            get_analytics_app_data(),
            {
                'name': 'Mass mail',
                'app_label': 'massmail',
                'app_url': f'/en/{PREFIX}massmail/',
                'has_module_perms': True,
                'models': [
                    {
                        'name': 'Email Messages',
                        'object_name': 'EmlMessage',
                        'perms': get_perms(add=False, change=False, delete=False),
                        'admin_url': f'/en/{PREFIX}massmail/emlmessage/',
                        'add_url': None,
                        'view_only': True
                    },
                    {
                        'name': 'Mailing Outs',
                        'object_name': 'MailingOut',
                        'perms': get_perms(add=False, change=False, delete=False),
                        'admin_url': f'/en/{PREFIX}massmail/mailingout/',
                        'add_url': None,
                        'view_only': True
                    }
                ]
            },
            get_common_app_data()
        ]
    ),
    (
        'Valeria.Operator.Global',
        [
            get_task_app_data(add_models=(get_memo_model_data(is_add_url=True),)),
            {
                'name': 'Crm',
                'app_label': 'crm',
                'app_url': f'/en/{PREFIX}crm/',
                'has_module_perms': True,
                'models': [
                    get_company_model_data(is_add_url=True, view_only=False),
                    get_contact_model_data(),
                    get_deal_model_data(perms={'add': False}, view_only=False),
                    {
                        'name': 'Emails in CRM',
                        'object_name': 'CrmEmail',
                        'perms': get_perms(),
                        'admin_url': f'/en/{PREFIX}crm/crmemail/',
                        'add_url': f'/en/{PREFIX}crm/crmemail/add/',
                        'view_only': False
                    },
                    {
                        'name': 'Leads',
                        'object_name': 'Lead',
                        'perms': get_perms(),
                        'admin_url': f'/en/{PREFIX}crm/lead/',
                        'add_url': f'/en/{PREFIX}crm/lead/add/',
                        'view_only': False
                    },
                    {
                        'name': 'Products',
                        'object_name': 'Product',
                        'perms': get_perms(),
                        'admin_url': f'/en/{PREFIX}crm/product/',
                        'add_url': f'/en/{PREFIX}crm/product/add/',
                        'view_only': False
                    },
                    {
                        'name': 'Requests',
                        'object_name': 'Request',
                        'perms': get_perms(),
                        'admin_url': f'/en/{PREFIX}crm/request/',
                        'add_url': f'/en/{PREFIX}crm/request/add/',
                        'view_only': False
                    }
                ]
            },
            get_common_app_data(),
            {
                'name': 'Settings',
                'app_label': 'settings',
                'app_url': f'/en/{PREFIX}settings/',
                'has_module_perms': True,
                'models': [
                    {
                        'name': 'Public email domains',
                        'object_name': 'PublicEmailDomain',
                        'perms': get_perms(),
                        'admin_url': f'/en/{PREFIX}settings/publicemaildomain/',
                        'add_url': f'/en/{PREFIX}settings/publicemaildomain/add/',
                        'view_only': False
                    },
                    {
                        'name': 'Stop Phrases', 'object_name': 'StopPhrase',
                        'perms': get_perms(),
                        'admin_url': f'/en/{PREFIX}settings/stopphrase/',
                        'add_url': f'/en/{PREFIX}settings/stopphrase/add/',
                        'view_only': False
                    }
                ]
            }
        ]
    ),
    (
        'Andrew.Manager.Global',
        [
            get_task_app_data(add_models=(
                get_memo_model_data(is_add_url=True),
                get_tag_model_data(),
            )),
            {
                'name': 'Crm',
                'app_label': 'crm',
                'app_url': f'/en/{PREFIX}crm/',
                'has_module_perms': True,
                'models': [
                    get_company_model_data(is_add_url=True, view_only=False),
                    get_contact_model_data(),
                    {
                        'name': 'Currencies',
                        'object_name': 'Currency',
                        'perms': get_perms(),
                        'admin_url': f'/en/{PREFIX}crm/currency/',
                        'add_url': f'/en/{PREFIX}crm/currency/add/',
                        'view_only': False
                    },
                    get_deal_model_data(perms={'add': False}, view_only=False),
                    {
                        'name': 'Emails in CRM',
                        'object_name': 'CrmEmail',
                        'perms': get_perms(),
                        'admin_url': f'/en/{PREFIX}crm/crmemail/',
                        'add_url': f'/en/{PREFIX}crm/crmemail/add/',
                        'view_only': False
                    },
                    {
                        'name': 'Leads',
                        'object_name': 'Lead',
                        'perms': get_perms(),
                        'admin_url': f'/en/{PREFIX}crm/lead/',
                        'add_url': f'/en/{PREFIX}crm/lead/add/',
                        'view_only': False
                    },
                    {
                        'name': 'Payments',
                        'object_name': 'Payment',
                        'perms': get_perms(),
                        'admin_url': f'/en/{PREFIX}crm/payment/',
                        'add_url': f'/en/{PREFIX}crm/payment/add/',
                        'view_only': False
                    },
                    {
                        'name': 'Products',
                        'object_name': 'Product',
                        'perms': get_perms(),
                        'admin_url': f'/en/{PREFIX}crm/product/',
                        'add_url': f'/en/{PREFIX}crm/product/add/',
                        'view_only': False
                    },
                    {
                        'name': 'Requests',
                        'object_name': 'Request',
                        'perms': get_perms(delete=False),
                        'admin_url': f'/en/{PREFIX}crm/request/',
                        'add_url': f'/en/{PREFIX}crm/request/add/',
                        'view_only': False
                    },
                    get_shipment_model_data(
                        perms={'add': False, 'delete': False}, view_only=False
                    ),
                    {
                        'name': 'Tags',
                        'object_name': 'Tag',
                        'perms': get_perms(),
                        'admin_url': f'/en/{PREFIX}crm/tag/',
                        'add_url': f'/en/{PREFIX}crm/tag/add/',
                        'view_only': False
                    }
                ]
            },
            get_analytics_app_data(),
            {
                'name': 'Mass mail',
                'app_label': 'massmail',
                'app_url': f'/en/{PREFIX}massmail/',
                'has_module_perms': True,
                'models': [
                    {
                        'name': 'Email Accounts',
                        'object_name': 'EmailAccount',
                        'perms': get_perms(add=False, change=False, delete=False),
                        'admin_url': f'/en/{PREFIX}massmail/emailaccount/',
                        'add_url': None,
                        'view_only': True
                    },
                    {
                        'name': 'Email Messages',
                        'object_name': 'EmlMessage',
                        'perms': get_perms(),
                        'admin_url': f'/en/{PREFIX}massmail/emlmessage/',
                        'add_url': f'/en/{PREFIX}massmail/emlmessage/add/',
                        'view_only': False
                    },
                    {
                        'name': 'Mailing Outs',
                        'object_name': 'MailingOut',
                        'perms': get_perms(add=False,),
                        'admin_url': f'/en/{PREFIX}massmail/mailingout/',
                        'add_url': None,
                        'view_only': False
                    },
                    {
                        'name': 'Signatures',
                        'object_name': 'Signature',
                        'perms': get_perms(),
                        'admin_url': f'/en/{PREFIX}massmail/signature/',
                        'add_url': f'/en/{PREFIX}massmail/signature/add/',
                        'view_only': False
                    }
                ]
            },
            get_common_app_data()
        ]
    ),
    (
        'Adam.Admin',
        [
            get_task_app_data(
                add_models=(
                    get_memo_model_data(is_add_url=True),
                    get_resolution_model_data(),
                    get_tag_model_data()
                )
            ),
            {
                'name': 'Crm',
                'app_label': 'crm',
                'app_url': f'/en/{PREFIX}crm/',
                'has_module_perms': True,
                'models': [
                    get_company_model_data(is_add_url=True, view_only=False),
                    get_contact_model_data(),
                    {
                        'name': 'Currencies',
                        'object_name': 'Currency',
                        'perms': get_perms(),
                        'admin_url': f'/en/{PREFIX}crm/currency/',
                        'add_url': f'/en/{PREFIX}crm/currency/add/',
                        'view_only': False
                    },
                    get_deal_model_data(perms={'add': False}, view_only=False),
                    {
                        'name': 'Emails in CRM',
                        'object_name': 'CrmEmail',
                        'perms': get_perms(),
                        'admin_url': f'/en/{PREFIX}crm/crmemail/',
                        'add_url': f'/en/{PREFIX}crm/crmemail/add/',
                        'view_only': False
                    },
                    {
                        'name': 'Leads',
                        'object_name': 'Lead',
                        'perms': get_perms(),
                        'admin_url': f'/en/{PREFIX}crm/lead/',
                        'add_url': f'/en/{PREFIX}crm/lead/add/',
                        'view_only': False
                    },
                    {
                        'name': 'Payments',
                        'object_name': 'Payment',
                        'perms': get_perms(),
                        'admin_url': f'/en/{PREFIX}crm/payment/',
                        'add_url': f'/en/{PREFIX}crm/payment/add/',
                        'view_only': False
                    },
                    {
                        'name': 'Products',
                        'object_name': 'Product',
                        'perms': get_perms(),
                        'admin_url': f'/en/{PREFIX}crm/product/',
                        'add_url': f'/en/{PREFIX}crm/product/add/',
                        'view_only': False
                    },
                    {
                        'name': 'Requests',
                        'object_name': 'Request',
                        'perms': get_perms(),
                        'admin_url': f'/en/{PREFIX}crm/request/',
                        'add_url': f'/en/{PREFIX}crm/request/add/',
                        'view_only': False
                    },
                    get_shipment_model_data(
                        view_only=False, is_add_url=False,
                        perms={
                            'add': False, 'change': True,
                            'delete': True, 'view': True
                        }
                    ),
                    {
                        'name': 'Tags',
                        'object_name': 'Tag',
                        'perms': get_perms(),
                        'admin_url': f'/en/{PREFIX}crm/tag/',
                        'add_url': f'/en/{PREFIX}crm/tag/add/',
                        'view_only': False
                    }
                ]
            },
            get_analytics_app_data(),
            {
                'name': 'Mass mail',
                'app_label': 'massmail',
                'app_url': f'/en/{PREFIX}massmail/',
                'has_module_perms': True,
                'models': [
                    {
                        'name': 'Email Accounts',
                        'object_name': 'EmailAccount',
                        'perms': get_perms(),
                        'admin_url': f'/en/{PREFIX}massmail/emailaccount/',
                        'add_url': f'/en/{PREFIX}massmail/emailaccount/add/',
                        'view_only': False
                    },
                    {
                        'name': 'Email Messages',
                        'object_name': 'EmlMessage',
                        'perms': get_perms(),
                        'admin_url': f'/en/{PREFIX}massmail/emlmessage/',
                        'add_url': f'/en/{PREFIX}massmail/emlmessage/add/',
                        'view_only': False
                    },
                    {
                        'name': 'Mailing Outs',
                        'object_name': 'MailingOut',
                        'perms': get_perms(add=False),
                        'admin_url': f'/en/{PREFIX}massmail/mailingout/',
                        'add_url': None,
                        'view_only': False
                    },
                    {
                        'name': 'Signatures',
                        'object_name': 'Signature',
                        'perms': get_perms(),
                        'admin_url': f'/en/{PREFIX}massmail/signature/',
                        'add_url': f'/en/{PREFIX}massmail/signature/add/',
                        'view_only': False
                    }
                ]
            },
            get_common_app_data(add_models=(
                get_reminder_model_data(name=reminder_iconed_name),
                get_userprofile_model_data(
                    name=userprofile_iconed_name,
                    perms={'add': False, 'change': True, 'delete': True, 'view': True},
                    view_only=False,
                    is_add_url=False
                ),                
            )),
            {
                'name': 'Settings',
                'app_label': 'settings',
                'app_url': f'/en/{PREFIX}settings/',
                'has_module_perms': True,
                'models': [
                    {
                        'name': 'Public email domains',
                        'object_name': 'PublicEmailDomain',
                        'perms': get_perms(),
                        'admin_url': f'/en/{PREFIX}settings/publicemaildomain/',
                        'add_url': f'/en/{PREFIX}settings/publicemaildomain/add/',
                        'view_only': False
                    },
                    {
                        'name': 'Stop Phrases', 'object_name': 'StopPhrase',
                        'perms': get_perms(),
                        'admin_url': f'/en/{PREFIX}settings/stopphrase/',
                        'add_url': f'/en/{PREFIX}settings/stopphrase/add/',
                        'view_only': False
                    }
                ]
            }
        ]
    ),
    (
        "Sergey.Co-worker.Head.Bookkeeping",
        [
            get_task_app_data(add_models=(get_memo_model_data(is_add_url=True),),),
            get_common_app_data()
        ]
    )
]

# data for admin site
ADMIN_DATA = [
    {
        'name': 'Administration',
        'app_label': 'admin',
        'app_url': f'/en/{ADMIN_PREFIX}admin/',
        'has_module_perms': True,
        'models': [
            {
                'name': 'Log entries',
                'admin_url': f'/en/{ADMIN_PREFIX}admin/logentry/',
                'model': LogEntry,
                'object_name': 'LogEntry',
                'perms': {'add': False, 'change': False, 'delete': False, 'view': True},
                'view_only': True
            }
        ],
    },
    {
        'name': 'Analytics',
        'app_label': 'analytics',
        'app_url': f'/en/{ADMIN_PREFIX}analytics/',
        'has_module_perms': True,
        'models': [
            get_incomestat_model_data(prefix=ADMIN_PREFIX),
            {
                'name': 'IncomeStat Snapshots',
                'object_name': 'IncomeStatSnapshot',
                'perms': get_perms(),
                'admin_url': f'/en/{ADMIN_PREFIX}analytics/incomestatsnapshot/',
                'add_url': f'/en/{ADMIN_PREFIX}analytics/incomestatsnapshot/add/',
                'view_only': False
            }
        ]
    },
    {
        'name': 'Authentication and Authorization',
        'app_label': 'auth', 'app_url': f'/en/{ADMIN_PREFIX}auth/',
        'has_module_perms': True,
        'models': [
            {
                'name': 'Groups',
                'object_name': 'Group',
                'perms': get_perms(),
                'admin_url': f'/en/{ADMIN_PREFIX}auth/group/',
                'add_url': f'/en/{ADMIN_PREFIX}auth/group/add/',
                'view_only': False
            },
            {
                'name': 'Permissions',
                'object_name': 'Permission',
                'perms': get_perms(),
                'admin_url': f'/en/{ADMIN_PREFIX}auth/permission/',
                'add_url': f'/en/{ADMIN_PREFIX}auth/permission/add/',
                'view_only': False
            },
            {
                'name': 'Users',
                'object_name': 'User',
                'perms': get_perms(),
                'admin_url': f'/en/{ADMIN_PREFIX}auth/user/',
                'add_url': f'/en/{ADMIN_PREFIX}auth/user/add/',
                'view_only': False
            }
        ]
    },
    {
        'name': 'Chat',
        'app_label': 'chat',
        'app_url': f'/en/{ADMIN_PREFIX}chat/',
        'has_module_perms': True,
        'models': [{
                'name': 'Messages',
                'object_name': 'ChatMessage',
                'perms': get_perms(),
                'admin_url': f'/en/{ADMIN_PREFIX}chat/chatmessage/',
                'add_url': f'/en/{ADMIN_PREFIX}chat/chatmessage/add/',
                'view_only': False
            }]
    },
    get_common_app_data(
        add_models=(
            get_department_model_data(prefix=ADMIN_PREFIX),
            get_thefile_model_data(prefix=ADMIN_PREFIX),
            get_reminder_model_data(prefix=ADMIN_PREFIX, add=True),
            get_userprofile_model_data(
                prefix=ADMIN_PREFIX,
                perms={'add': False, 'change': True, 'delete': True, 'view': True},
                view_only=False,
                is_add_url=False
            ),
        ),
        prefix=ADMIN_PREFIX
    ),
    {
        'name': 'Crm',
        'app_label': 'crm',
        'app_url': f'/en/{ADMIN_PREFIX}crm/',
        'has_module_perms': True,
        'models': [
            {
                'name': 'Cities',
                'object_name': 'City',
                'perms': get_perms(),
                'admin_url': f'/en/{ADMIN_PREFIX}crm/city/',
                'add_url': f'/en/{ADMIN_PREFIX}crm/city/add/',
                'view_only': False
            },
            {
                'name': 'Closing reasons',
                'object_name': 'ClosingReason',
                'perms': get_perms(),
                'admin_url': f'/en/{ADMIN_PREFIX}crm/closingreason/',
                'add_url': f'/en/{ADMIN_PREFIX}crm/closingreason/add/',
                'view_only': False
            },
            get_company_model_data(prefix=ADMIN_PREFIX, is_add_url=True, view_only=False),
            get_contact_model_data(prefix=ADMIN_PREFIX, is_add_url=True, view_only=False),
            {
                'name': 'Countries',
                'object_name': 'Country',
                'perms': get_perms(),
                'admin_url': f'/en/{ADMIN_PREFIX}crm/country/',
                'add_url': f'/en/{ADMIN_PREFIX}crm/country/add/',
                'view_only': False
            },
            {
                'name': 'Currencies',
                'object_name': 'Currency',
                'perms': get_perms(),
                'admin_url': f'/en/{ADMIN_PREFIX}crm/currency/',
                'add_url': f'/en/{ADMIN_PREFIX}crm/currency/add/',
                'view_only': False
            },
            {
                'name': 'Currency rates',
                'object_name': 'Rate',
                'perms': get_perms(),
                'admin_url': f'/en/{ADMIN_PREFIX}crm/rate/',
                'add_url': f'/en/{ADMIN_PREFIX}crm/rate/add/',
                'view_only': False
            },
            get_deal_model_data(
                prefix=ADMIN_PREFIX, is_add_url=False, view_only=False
            ),
            {
                'name': 'Emails in CRM',
                'object_name': 'CrmEmail',
                'perms': get_perms(),
                'admin_url': f'/en/{ADMIN_PREFIX}crm/crmemail/',
                'add_url': f'/en/{ADMIN_PREFIX}crm/crmemail/add/',
                'view_only': False
            },
            {
                'name': 'Industries of Clients',
                'object_name': 'Industry',
                'perms': get_perms(),
                'admin_url': f'/en/{ADMIN_PREFIX}crm/industry/',
                'add_url': f'/en/{ADMIN_PREFIX}crm/industry/add/',
                'view_only': False
            },
            {
                'name': 'Lead Sources',
                'object_name': 'LeadSource',
                'perms': get_perms(),
                'admin_url': f'/en/{ADMIN_PREFIX}crm/leadsource/',
                'add_url': f'/en/{ADMIN_PREFIX}crm/leadsource/add/',
                'view_only': False
            },
            {
                'name': 'Leads',
                'object_name': 'Lead',
                'perms': get_perms(),
                'admin_url': f'/en/{ADMIN_PREFIX}crm/lead/',
                'add_url': f'/en/{ADMIN_PREFIX}crm/lead/add/',
                'view_only': False
            },
            {
                'name': 'Payments',
                'object_name': 'Payment',
                'perms': get_perms(),
                'admin_url': f'/en/{ADMIN_PREFIX}crm/payment/',
                'add_url': f'/en/{ADMIN_PREFIX}crm/payment/add/',
                'view_only': False
            },
            {
                'name': 'Product categories',
                'object_name': 'ProductCategory',
                'perms': get_perms(),
                'admin_url': f'/en/{ADMIN_PREFIX}crm/productcategory/',
                'add_url': f'/en/{ADMIN_PREFIX}crm/productcategory/add/',
                'view_only': False
            },
            {
                'name': 'Products',
                'object_name': 'Product',
                'perms': get_perms(),
                'admin_url': f'/en/{ADMIN_PREFIX}crm/product/',
                'add_url': f'/en/{ADMIN_PREFIX}crm/product/add/',
                'view_only': False
            },
            {
                'name': 'Requests',
                'object_name': 'Request',
                'perms': get_perms(),
                'admin_url': f'/en/{ADMIN_PREFIX}crm/request/',
                'add_url': f'/en/{ADMIN_PREFIX}crm/request/add/',
                'view_only': False
            },
            get_shipment_model_data(
                prefix=ADMIN_PREFIX, view_only=False, is_add_url=False,
                perms={
                    'add': False, 'change': True,
                    'delete': True, 'view': True
                }
            ),
            {
                'name': 'Stages',
                'object_name': 'Stage',
                'perms': get_perms(),
                'admin_url': f'/en/{ADMIN_PREFIX}crm/stage/',
                'add_url': f'/en/{ADMIN_PREFIX}crm/stage/add/',
                'view_only': False
            },
            {
                'name': 'Tags',
                'object_name': 'Tag',
                'perms': get_perms(),
                'admin_url': f'/en/{ADMIN_PREFIX}crm/tag/',
                'add_url': f'/en/{ADMIN_PREFIX}crm/tag/add/',
                'view_only': False
            },
            {
                'name': 'Types of Clients',
                'object_name': 'ClientType',
                'perms': get_perms(),
                'admin_url': f'/en/{ADMIN_PREFIX}crm/clienttype/',
                'add_url': f'/en/{ADMIN_PREFIX}crm/clienttype/add/',
                'view_only': False
            },
        ]
    },
    {
        'name': 'Help',
        'app_label': 'help',
        'app_url': f'/en/{ADMIN_PREFIX}help/',
        'has_module_perms': True,
        'models': [
            {
                'name': 'Help pages',
                'object_name': 'Page',
                'perms': get_perms(),
                'admin_url': f'/en/{ADMIN_PREFIX}help/page/',
                'add_url': f'/en/{ADMIN_PREFIX}help/page/add/',
                'view_only': False
            },
            {
                'name': 'Paragraphs',
                'object_name': 'Paragraph',
                'perms': get_perms(),
                'admin_url': f'/en/{ADMIN_PREFIX}help/paragraph/',
                'add_url': f'/en/{ADMIN_PREFIX}help/paragraph/add/',
                'view_only': False
            }
        ]
    },
    {
        'name': 'Mass mail',
        'app_label': 'massmail',
        'app_url': f'/en/{ADMIN_PREFIX}massmail/',
        'has_module_perms': True,
        'models': [
            {
                'name': 'Email Accounts',
                'object_name': 'EmailAccount',
                'perms': get_perms(),
                'admin_url': f'/en/{ADMIN_PREFIX}massmail/emailaccount/',
                'add_url': f'/en/{ADMIN_PREFIX}massmail/emailaccount/add/',
                'view_only': False
            },
            {
                'name': 'Email Messages',
                'object_name': 'EmlMessage',
                'perms': get_perms(),
                'admin_url': f'/en/{ADMIN_PREFIX}massmail/emlmessage/',
                'add_url': f'/en/{ADMIN_PREFIX}massmail/emlmessage/add/',
                'view_only': False
            },
            {
                'name': 'Eml accounts queues',
                'object_name': 'EmlAccountsQueue',
                'perms': get_perms(),
                'admin_url': f'/en/{ADMIN_PREFIX}massmail/emlaccountsqueue/',
                'add_url': f'/en/{ADMIN_PREFIX}massmail/emlaccountsqueue/add/',
                'view_only': False
            },
            {
                'name': 'Mailing Outs',
                'object_name': 'MailingOut',
                'perms': get_perms(add=False),
                'admin_url': f'/en/{ADMIN_PREFIX}massmail/mailingout/',
                'add_url': None,
                'view_only': False
            },
            {
                'name': 'Mass contacts',
                'object_name': 'MassContact',
                'perms': get_perms(),
                'admin_url': f'/en/{ADMIN_PREFIX}massmail/masscontact/',
                'add_url': f'/en/{ADMIN_PREFIX}massmail/masscontact/add/',
                'view_only': False
            },
            {
                'name': 'Signatures',
                'object_name': 'Signature',
                'perms': get_perms(),
                'admin_url': f'/en/{ADMIN_PREFIX}massmail/signature/',
                'add_url': f'/en/{ADMIN_PREFIX}massmail/signature/add/',
                'view_only': False
            }
        ]
    },
    {
        'name': 'Settings',
        'app_label': 'settings',
        'app_url': f'/en/{ADMIN_PREFIX}settings/',
        'has_module_perms': True,
        'models': [
            {
                'name': 'Banned company names',
                'object_name': 'BannedCompanyName',
                'perms': get_perms(),
                'admin_url': f'/en/{ADMIN_PREFIX}settings/bannedcompanyname/',
                'add_url': f'/en/{ADMIN_PREFIX}settings/bannedcompanyname/add/',
                'view_only': False
            },
            {
                'name': 'Massmail Settings',
                'object_name': 'MassmailSettings',
                'perms': get_perms(add=False, delete=False),
                'admin_url': f'/en/{ADMIN_PREFIX}settings/massmailsettings/',
                'add_url': None,
                'view_only': False
            },
            {
                'name': 'Public email domains',
                'object_name': 'PublicEmailDomain',
                'perms': get_perms(),
                'admin_url': f'/en/{ADMIN_PREFIX}settings/publicemaildomain/',
                'add_url': f'/en/{ADMIN_PREFIX}settings/publicemaildomain/add/',
                'view_only': False
            },
            {
                'name': 'Reminder settings',
                'object_name': 'Reminders',
                'perms': get_perms(add=False, delete=False),
                'admin_url': f'/en/{ADMIN_PREFIX}settings/reminders/',
                'add_url': None,
                'view_only': False
            },
            {
                'name': 'Stop Phrases',
                'object_name': 'StopPhrase',
                'perms': get_perms(),
                'admin_url': f'/en/{ADMIN_PREFIX}settings/stopphrase/',
                'add_url': f'/en/{ADMIN_PREFIX}settings/stopphrase/add/',
                'view_only': False
            }
        ]
    },
    {
        'name': 'Sites',
        'app_label': 'sites',
        'app_url': f'/en/{ADMIN_PREFIX}sites/',
        'has_module_perms': True,
        'models': [{
                'name': 'Sites',
                'object_name': 'Site',
                'perms': get_perms(),
                'admin_url': f'/en/{ADMIN_PREFIX}sites/site/',
                'add_url': f'/en/{ADMIN_PREFIX}sites/site/add/',
                'view_only': False
            }]
    },
    {
        'name': 'Tasks',
        'app_label': 'tasks',
        'app_url': f'/en/{ADMIN_PREFIX}tasks/',
        'has_module_perms': True,
        'models': [
            {
                'name': 'Memos',
                'object_name': 'Memo',
                'perms': get_perms(),
                'admin_url': f'/en/{ADMIN_PREFIX}tasks/memo/',
                'add_url': f'/en/{ADMIN_PREFIX}tasks/memo/add/',
                'view_only': False
            },
            get_projectstage_model_data(prefix=ADMIN_PREFIX),
            {
                'name': 'Projects',
                'object_name': 'Project',
                'perms': get_perms(),
                'admin_url': f'/en/{ADMIN_PREFIX}tasks/project/',
                'add_url': f'/en/{ADMIN_PREFIX}tasks/project/add/',
                'view_only': False
            },
            get_resolution_model_data(prefix=ADMIN_PREFIX),
            get_tag_model_data(prefix=ADMIN_PREFIX),
            get_taskstage_model_data(prefix=ADMIN_PREFIX),
            {
                'name': 'Tasks',
                'object_name': 'Task',
                'perms': get_perms(),
                'admin_url': f'/en/{ADMIN_PREFIX}tasks/task/',
                'add_url': f'/en/{ADMIN_PREFIX}tasks/task/add/',
                'view_only': False
            }
        ]
    },
    {
        'name': 'Transaction quality',
        'app_label': 'quality',
        'app_url': '/en/q7sSln_Wd10Or-admin/quality/',
        'has_module_perms': True,
        'models': [
            {
                'name': 'Transaction-Quality Events',
                'object_name': 'TransactionQualityEvent',
                'perms': {'add': True, 'change': True, 'delete': True, 'view': True},
                'add_url': '/en/q7sSln_Wd10Or-admin/quality/transactionqualityevent/add/',
                'admin_url': '/en/q7sSln_Wd10Or-admin/quality/transactionqualityevent/',
                'view_only': False
            },
            {
                'name': 'Transaction-Quality Signals',
                'object_name': 'TransactionQualitySignal',
                'perms': {'add': True, 'change': True, 'delete': True, 'view': True},
                'add_url': '/en/q7sSln_Wd10Or-admin/quality/transactionqualitysignal/add/',
                'admin_url': '/en/q7sSln_Wd10Or-admin/quality/transactionqualitysignal/',
                'view_only': False
            }
        ],
    },
    {
        'name': 'Voip',
        'app_label': 'voip',
        'app_url': f'/en/{ADMIN_PREFIX}voip/',
        'has_module_perms': True,
        'models': [{
                'name': 'Connections',
                'object_name': 'Connection',
                'perms': get_perms(),
                'admin_url': f'/en/{ADMIN_PREFIX}voip/connection/',
                'add_url': f'/en/{ADMIN_PREFIX}voip/connection/add/',
                'view_only': False
            }]
    }
]
