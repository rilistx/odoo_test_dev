{
    'name': 'Estate',
    'version': '1.0',
    'summary': 'Estate Property Management',
    'category': 'Real Estate',
    'author': 'RILISTX',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/menu_actions.xml',
        'views/estate_property_offer_views.xml',
        'views/estate_property_tag_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_views.xml',
        'views/estate_property_kanban_views.xml',
        'views/res_users_views.xml',
    ],
    'installable': True,
    'application': True,
}
