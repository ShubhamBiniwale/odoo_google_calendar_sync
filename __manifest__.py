# -*- coding: utf-8 -*-
{
    'name': "Odoo google calendar event syncs",
    'summary': """
            This module lets you sync your calendar events added in odoo
            to your google calendar. So that, You will get alert/ reminder
            email, sms from google before an event.""",
    'description': """
            This module lets you sync your calendar events added in odoo
            to your google calendar. So that, You will get alert/ reminder
            email, sms from google before an event.
        """,
    'author': "Mr. Shubham Biniwale",
    'category': 'CRM',
    'version': '0.1',
    'depends': ['base','crm'],
    'data': [
        'views/views.xml'
    ]
}
