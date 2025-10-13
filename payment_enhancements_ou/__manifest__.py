{
    "name": "Payments Enhancements (SO/PO refs & OU control)",
    "version": "15.0.1.0.0",
    "summary": "Add SO/PO references on payments and control OU/company constraint visibility.",
    "author": "Othmancs",
    "license": "LGPL-3",
    "depends": [
        "account",
        "sale",
        "purchase",
        "account_operating_unit",
    ],
    "data": [
        "views/account_payment_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
}