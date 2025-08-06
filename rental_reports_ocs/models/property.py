from odoo import models, fields, api

class RentProperty(models.Model):
    _name = 'rent.property'
    _description = 'Rental Property'

    name = fields.Char(string='Property Name', required=True)
    address = fields.Text(string='Address')
    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit')
    elevators = fields.One2many('rent.property.elevator', 'property_id', string='Elevators')
    property_address_build = fields.Many2one(
        comodel_name='rent.property.build',
        string='المجمع العقاري'
    )
    property_address_city = fields.Many2one(
        comodel_name='rent.property.city',
        string='مدينة العقار'
    )
    country = fields.Many2one(
        comodel_name='res.country',
        string='الدولة'
    )
    property_analytic_account = fields.Many2one(
        comodel_name='account.analytic.account',
        string='الحساب التحليلي'
    )

class RentPropertyElevator(models.Model):
    _name = 'rent.property.elevator'
    _description = 'Property Elevator'
    _rec_name = 'elevator_maintenance_date'

    property_id = fields.Many2one('rent.property', copy=True, string='Properties', ondelete='cascade')
    elevator_maintenance_description = fields.Char(string='Maintenance Description')
    elevator_number_name = fields.Char(string='Elevator Number/Name')
    elevator_maintenance_date = fields.Date(string='Maintenance Date')
    elevator_maintenance_value = fields.Float(string='Maintenance Value')

class RentPropertyBuild(models.Model):
    _name = 'rent.property.build'
    _description = 'Property Building Complex'

    name = fields.Char(string='اسم المجمع')

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    property_analytic_account = fields.Many2one(
        comodel_name='account.analytic.account',
        related='product_rental_id.property_analytic_account',
        store=True
    )
    product_rental_id = fields.Many2one(
        comodel_name='rent.property',
        string='الوحدة الإيجارية'
    )
    
    property_address_city = fields.Many2one(
        comodel_name='rent.property.city',
        string='مدينة العقار',
        related='product_rental_id.property_address_city',
        store=True
    )
    country = fields.Many2one(
        comodel_name='res.country',
        string='الدولة',
        related='product_rental_id.country',
        store=True
    )

class RentPropertyCity(models.Model):
    _name = 'rent.property.city'
    _description = 'Property City'

    name = fields.Char(string='اسم المدينة')
    
    property_address_build = fields.Many2one(
        comodel_name='rent.property.build',
        string='المجمع العقاري',
        related='product_rental_id.property_address_build'
    )
    property_analytic_account = fields.Many2one(
        comodel_name='account.analytic.account',
        string='الحساب التحليلي',
        related='product_rental_id.property_analytic_account',
        store=True
    )
    
