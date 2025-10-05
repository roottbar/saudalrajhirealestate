from odoo import api, SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)


def _patch_view_arch(arch_text):
    """Clean problematic constructs in DB-stored views.

    - Remove deprecated xpath targeting t-call-assets='web.assets_common'
      and replace any direct t-call-assets='web.assets_common' with web.assets_frontend.
    - Remove domain attribute from <field name="external_report_layout_id"> to
      avoid invalid domain parse errors during registry build (Odoo 18).

    Returns (new_text, changed:boolean).
    """
    try:
        # Lazy import to avoid issues if lxml is missing at import time
        from lxml import etree
        parser = etree.XMLParser(remove_blank_text=False, recover=True)
        root = etree.fromstring(arch_text.encode('utf-8'), parser=parser)
        changed = False

        # 1) Remove xpath nodes that target the old assets_common (handle various quoting/escaping)
        for xp in root.xpath(
            
            ".//xpath[contains(@expr, 't-call-assets') and contains(@expr, 'assets_common')]"
        ):
            parent = xp.getparent()
            if parent is not None:
                parent.remove(xp)
                changed = True

        # 2) Replace direct t-call-assets on any node (catch contains as well)
        for node in root.xpath(".//*[@t-call-assets and contains(@t-call-assets, 'assets_common')]"):
            # Use web.assets_frontend which is the valid website bundle in Odoo 18+
            # (backend templates should target web.assets_backend explicitly)
            node.set('t-call-assets', 'web.assets_frontend')
            changed = True

        # 3) Remove domain attribute from external_report_layout_id fields
        for fld in root.xpath(".//field[@name='external_report_layout_id']"):
            if 'domain' in fld.attrib:
                try:
                    del fld.attrib['domain']
                    changed = True
                except Exception:
                    # Defensive: ignore if removal fails
                    pass

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
        # Common xpath open tag removals (various quoting)
        for tag in [
            "<xpath expr=\"//t[@t-call-assets='web.assets_common']\">",
            "<xpath expr=\"//t[@t-call-assets=&#39;web.assets_common&#39;]\">",
            "<xpath expr='//t[@t-call-assets=\"web.assets_common\"]'>",
            "<xpath expr='//t[@t-call-assets=&quot;web.assets_common&quot;]'>",
        ]:
            new_text = new_text.replace(tag, "")
        new_text = new_text.replace("</xpath>", "")
        for frag in [
            "t-call-assets=\"web.assets_common\"",
            "t-call-assets='web.assets_common'",
            "t-call-assets=&#39;web.assets_common&#39;",
            "t-call-assets=&quot;web.assets_common&quot;",
        ]:
            new_text = new_text.replace(frag, "t-call-assets=\"web.assets_frontend\"")

        # Remove domain attribute on external_report_layout_id via text approach
        # Minimal patterns to avoid over-matching
        for pat in [
            ' name="external_report_layout_id"',
            " name='external_report_layout_id'",
        ]:
            if pat in new_text:
                # Remove the domain attribute immediately following the field decl if present
                new_text = new_text.replace(" domain=\"[", " ")
                new_text = new_text.replace(" domain='[", " ")
                # Also handle closing quotes generically (best-effort)
                new_text = new_text.replace("]\"", "")
                new_text = new_text.replace("]'", "")
        return new_text, (new_text != before)


def _clean_views(env):
    """Shared cleaning routine: assets_common and external_report_layout_id domain removal."""
    View = env['ir.ui.view']

    # Find candidate views by arch text content
    patterns = [
        "t-call-assets=\"web.assets_common\"",
        "t-call-assets='web.assets_common'",
        "t-call-assets=&#39;web.assets_common&#39;",
        "t-call-assets=&quot;web.assets_common&quot;",
        "t[@t-call-assets='web.assets_common']",
        "t[@t-call-assets=\"web.assets_common\"]",
        "t[@t-call-assets=&#39;web.assets_common&#39;]",
        "t[@t-call-assets=&quot;web.assets_common&quot;]",
        # External report layout field present
        "external_report_layout_id",
    ]

    views = env['ir.ui.view'].browse()
    for p in patterns:
        views |= View.search([('arch_db', 'ilike', p)])

    # Heuristic: include possible 404/not_found templates that might carry bad xpaths
    views |= View.search([('key', 'ilike', '404')])
    # Explicit common keys for website 404 templates
    views |= View.search([('key', 'in', ['website.404', 'website.not_found_template'])])
    # Occasionally, customized views are named with 404 in their names
    views |= View.search([('name', 'ilike', '404')])

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
        _logger.info("migration_cleanup: cleaned %s DB views (assets_common/domain fixes)", cleaned)
    else:
        _logger.info("migration_cleanup: no DB views required cleaning")


def post_init_hook(cr, registry):
    """Automatically clean DB views on install."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    _clean_views(env)


def post_load_hook(cr, registry):
    """Run cleaning at server load to catch cases where the module was already installed.

    This helps environments where the invalid domain exists before the module is upgraded.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    _clean_views(env)