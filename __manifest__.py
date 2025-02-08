{
    'name': 'Account Move Advanced',
    'version': '1.0',
    'author':'ANFEPI: Roberto Requejo Fernández',
    'depends': ['account', 'l10n_mx_edi', 'l10n_mx_xml_masive_download'],
    'description': """
    """,
    'data': [
        'views/account_move_view.xml',
        'views/upload_wizard_view.xml',
        'views/custom_validation_confirm.xml',
        'security/ir.model.access.csv',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'auto_install': False,
    "license": "AGPL-3",
}