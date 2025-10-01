# -*- coding: utf-8 -*-
{
    "name": "e-Invoice KSA | tax invoice | report | qrcode | ZATCA | vat  | electronic | einvoice | e-invoice sa | accounting | tax  | Zakat, Tax and Customs Authority | invoice ",
    "version": "1.2",
    "depends": [
        "base",
        "web",
        "account",
    ],
    "external_dependencies": {
        "python": ["qrcode", "Pillow"],
    },
    "author": "Genius Valley",
    "category": "Accounting",
    "website": "https://genius-valley.com/",
    "support": "odoo@gvitt.com",
    "images": [
        "static/description/assets/main_screenshot.gif",
        "static/description/assets/main_screenshot.png",
        "static/description/assets/ghits_desktop_inv.jpg",
        "static/description/assets/ghits_labtop1.jpg",
    ],
    "price": "0",
    "license": "OPL-1",
    "currency": "USD",
    "summary": "e-Invoice in Kingdom of Saudi Arabia KSA | tax invoice | vat  | electronic | e invoice | accounting | tax | free | ksa | sa |Zakat, Tax and Customs Authority | الفاتورة الضريبية | الفوترة الالكترونية",
    "description": """
    e-Invoice in Kingdom of Saudi Arabia
    and prepare tax invoice to be ready for the second phase.
    Zakat, Tax and Customs Authority
    الفوترة الإلكترونية - الفاتورة الضريبية - المملكة العربية السعودية
    المرحلة الاولي -  مرحلة الاصدار 
    هيئة الزكاة والضريبة والجمارك
    """,
    "data": [
        "view/partner.xml",
        "report/base_document_layout.xml",
        "report/account_move.xml",
    ],
    "assets": {
        "web.report_assets_common": [
            "/einv_sa/static/css/report_style.css",
        ],
    },
    "installable": True,
    "auto_install": False,
    "application": True,
}
