{
    'name': 'Rental Reports',
    'version': '15.0.1.0.0',
    'summary': 'Generate XML and HTML reports for rented units',
    'description': """
        This module generates detailed reports for rented units in XML and HTML formats
        with filtering by company, operating unit, building address and property.
    """,
    'author': 'Othmancs',
    'website': 'https://www.tbarholding.com',
    'category': 'Real Estate/Rental',
    'depends': ['product', 'operating_unit', 'renting', 'rent_customize'],
    'data': [
        'views/property_views.xml',
        'views/rental_report_views.xml',
        'reports/rental_report.xml',
        'reports/rental_report_template.xml',
        'reports/rental_report_template.html',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
