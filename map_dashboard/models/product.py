# Copyright 2015 Akretion (http://www.akretion.com/) - Alexis de Lattre
# Copyright 2016 Antiun Ingeniería S.L. - Javier Iniesta
# Copyright 2017 Tecnativa - Luis Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = "res.partner"
    # active = fields.Boolean('Active', default=True, tracking=True)

    is_location = fields.Boolean(
        string="هل موقع ؟", default=False
    )


class ProductTemplate(models.Model):
    _inherit = "product.template"

    city = fields.Char('المدينة')
    country = fields.Many2one('res.country', string='الدولة')
    zip = fields.Char('العنوان الوطني')
    address = fields.Char('الشارع')
    state = fields.Many2one('res.country.state', string='المحافظة')
    partner_id = fields.Many2one(
        'res.partner', string='Customer', index=True, tracking=10,
        # domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="Linked partner (optional). Usually created when converting the lead. You can find a partner by its Name, TIN, Email or Internal Reference.")

    @api.model_create_multi
    def create(self, vals_list):
        res = super(ProductTemplate, self).create(vals_list)
        partner = self.env['res.partner'].sudo().create(
            {'name': res.name, 'type': 'private', 'street': res.address, 'city': res.city, 'state_id': res.state.id,
             'country_id': res.country.id, 'zip': res.zip, 'is_location': True})
        res.partner_id = partner.id
        return res
