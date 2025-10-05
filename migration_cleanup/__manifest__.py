{
    'name': 'Migration Cleanup: Deprecated Assets Fix',
    'summary': 'Auto-clean QWeb views referencing web.assets_common (Odoo 18).',
    'version': '18.0.1.0.0',
    'author': 'Internal Migration Tools',
    'license': 'LGPL-3',
    'depends': ['web', 'website'],
    'data': [],
    'post_init_hook': 'post_init_hook',
    'post_load': 'post_load_hook',
    'installable': True,
    'auto_install': True,
}