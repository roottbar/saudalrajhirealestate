from odoo import api, fields, models


class Partner(models.Model):
    _inherit = 'res.partner'

    def get_branch_id(self):
        return self.env.user.branch_id

    branch_id = fields.Many2one('branch.branch', string='Branch', default=get_branch_id)
    code = fields.Char(string='', default='New')

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if not self.env.user.allowed_see_other_customers:
            args += ['|', ('branch_id', 'in', self.env.user.allowed_branches.ids), ('branch_id', '=', False)]
        return super(Partner, self).search(args=args, offset=offset, limit=limit, order=order, count=count)

    @api.model
    def create(self, vals):
        res = super(Partner, self).create(vals)
        branch = self.env['branch.branch'].browse(vals.get('branch_id'))
        if res.company_type != "person":
            if not branch:
                branch = self.env.user.branch_id
            sequence = self.env['ir.sequence'].search(
                [('id', '=', branch.partner_sequence_id.id)])
            if sequence:
                if 'model' in self._context:
                    if not self._context.get("module") == 'general_settings':
                        res.code = str(sequence.get_id(sequence.id))
                else:
                    res.code = str(sequence.get_id(sequence.id))
        else:
            res.code = ""
        return res

    def _get_name(self):
        """ Utility method to allow name_get to be overrided without re-browse the partner """
        partner = self
        name = partner.name or ''
        code = str(" [" + partner.ref + "] ") if partner.ref else ""
        name = name + code

        if partner.company_name or partner.parent_id:
            if not name and partner.type in ['invoice', 'delivery', 'other']:
                name = dict(self.fields_get(['type'])[
                                'type']['selection'])[partner.type]
            if not partner.is_company:
                name = self._get_contact_name(partner, name)
        if self._context.get('show_address_only'):
            name = partner._display_address(without_company=True)
        if self._context.get('show_address'):
            name = name + "\n" + partner._display_address(without_company=True)
        name = name.replace('\n\n', '\n')
        name = name.replace('\n\n', '\n')
        if self._context.get('partner_show_db_id'):
            name = "%s (%s)" % (name, partner.id)
        if self._context.get('address_inline'):
            splitted_names = name.split("\n")
            name = ", ".join([n for n in splitted_names if n.strip()])
        if self._context.get('show_email') and partner.email:
            name = "%s <%s>" % (name, partner.email)
        if self._context.get('html_format'):
            name = name.replace('\n', '<br/>')
        if self._context.get('show_vat') and partner.vat:
            name = "%s ‒ %s" % (name, partner.vat)
        return name

    @api.depends('is_company', 'name', 'parent_id.display_name', 'type', 'company_name', 'ref')
    def _compute_display_name(self):
        diff = dict(show_address=None, show_address_only=None,
                    show_email=None, html_format=None, show_vat=None)
        names = dict(self.with_context(**diff).name_get())
        for partner in self:
            partner.display_name = names.get(partner.id)
