from odoo import api, SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)


def _patch_view_arch(arch_text):
    """Remove deprecated xpath targeting t-call-assets='web.assets_common' and
    replace any direct t-call-assets='web.assets_common' with website.assets_frontend.

    Returns (new_text, changed:boolean).
    """
    try:
        # Lazy import to avoid issues if lxml is missing at import time
        from lxml import etree
        parser = etree.XMLParser(remove_blank_text=False, recover=True)
        root = etree.fromstring(arch_text.encode('utf-8'), parser=parser)
        changed = False

        # Remove xpath nodes that target the old assets_common
        for xp in root.xpath(".//xpath[contains(@expr, \"t[@t-call-assets='web.assets_common']\")]"):
            parent = xp.getparent()
            if parent is not None:
                parent.remove(xp)
                changed = True

        # Replace direct t-call-assets on any node
        for node in root.xpath(".//*[@t-call-assets='web.assets_common']"):
            # In website contexts, use website.assets_frontend which is valid in Odoo 18
            node.set('t-call-assets', 'website.assets_frontend')
            changed = True

        if changed:
            new_text = etree.tostring(root, encoding='unicode')
            return new_text, True
        return arch_text, False
    except Exception as e:
        _logger.warning("migration_cleanup: XML parse failed, falling back to text replace: %s", e)
        # Fallback: simple text-based removal/replacement
        new_text = arch_text
        before = new_text
        # Remove typical xpath block opening; keep simple to avoid breaking structure too much
        new_text = new_text.replace(
            "<xpath expr=\"//t[@t-call-assets='web.assets_common']\">",
            ""
        )
        new_text = new_text.replace("</xpath>", "")
        new_text = new_text.replace(
            "t-call-assets=\"web.assets_common\"",
            "t-call-assets=\"website.assets_frontend\"",
        )
        return new_text, (new_text != before)


def post_init_hook(cr, registry):
    """Automatically clean DB views that reference deprecated web.assets_common.

    This prevents ValueError during QWeb rendering (e.g., website 404 not_found_template).
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    View = env['ir.ui.view']

    # Find candidate views by arch text content
    v1 = View.search([('arch_db', 'ilike', "t-call-assets=\"web.assets_common\"")])
    v2 = View.search([('arch_db', 'ilike', "t[@t-call-assets='web.assets_common']")])
    views = (v1 | v2)

    cleaned = 0
    for view in views:
        arch = view.arch_db or ''
        new_arch, changed = _patch_view_arch(arch)
        if changed and new_arch:
            try:
                view.write({'arch_db': new_arch})
                cleaned += 1
            except Exception as e:
                _logger.error("migration_cleanup: failed to write cleaned arch for view %s: %s", view.id, e)

    if cleaned:
        _logger.info("migration_cleanup: cleaned %s DB views referencing web.assets_common", cleaned)
    else:
        _logger.info("migration_cleanup: no DB views required cleaning")