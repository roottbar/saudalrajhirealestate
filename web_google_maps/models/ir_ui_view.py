# -*- coding: utf-8 -*-
# License AGPL-3
from lxml import etree
from odoo import fields, models, _
from odoo.tools.safe_eval import safe_eval


class IrUiView(models.Model):
    _inherit = 'ir.ui.view'

    # إضافة نوع Google Maps
    type = fields.Selection(selection_add=[('google_map', 'Google Maps')])

    def _validate_tag_field(self, node, name_manager, node_info):
        """
        نسخة محدثة لتدعم Odoo 18:
        - دعم tag 'google_map'
        - استخدام _validate_domain_identifiers بدلًا من _get_domain_identifiers
        """
        validate = node_info['validate']
        name = node.get('name')
        if not name:
            self._raise_view_error(
                _("Field tag must have a \"name\" attribute defined"), node
            )

        field = name_manager.model._fields.get(name)
        if field:
            if validate and field.relational:
                domain = (
                    node.get('domain')
                    or node_info['editable']
                    and field._description_domain(self.env)
                )
                if isinstance(domain, str):
                    # تحقق من domain باستخدام الدالة الجديدة في Odoo 18
                    desc = (
                        f'domain of <field name="{name}">'
                        if node.get('domain')
                        else f"domain of field '{name}'"
                    )
                    try:
                        self._validate_domain_identifiers(node, domain, desc)
                    except Exception as e:
                        self._raise_view_error(str(e), node)

            elif validate and node.get('domain'):
                msg = _(
                    'Domain on non-relational field "%(name)s" makes no sense (domain:%(domain)s)',
                    name=name,
                    domain=node.get('domain'),
                )
                self._raise_view_error(msg, node)

            # تحقق من الفيوهات الفرعية
            for child in node:
                if child.tag not in ('form', 'tree', 'graph', 'kanban', 'calendar', 'google_map'):
                    continue
                node.remove(child)
                sub_manager = self._validate_view(
                    child,
                    field.comodel_name,
                    editable=node_info['editable'],
                    full=validate,
                )
                for fname, use in sub_manager.mandatory_parent_fields.items():
                    name_manager.must_have_field(fname, use)

        elif validate and name not in name_manager.field_info:
            msg = _(
                'Field "%(field_name)s" does not exist in model "%(model_name)s"',
                field_name=name,
                model_name=name_manager.model._name,
            )
            self._raise_view_error(msg, node)

        # التحقق من attributes مثل invisible و readonly و required
        if validate:
            for attribute in ('invisible', 'readonly', 'required'):
                val = node.get(attribute)
                if val:
                    res = safe_eval(val, {'context': self._context})
                    if res not in (1, 0, True, False, None):
                        msg = _(
                            'Attribute %(attribute)s evaluation expects a boolean, got %(value)s',
                            attribute=attribute,
                            value=val,
                        )
                        self._raise_view_error(msg, node)
