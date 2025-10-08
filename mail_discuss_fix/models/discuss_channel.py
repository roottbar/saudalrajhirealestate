from odoo import api, models


class DiscussChannel(models.Model):
    _inherit = "discuss.channel"

    @api.depends("member_ids")
    def _compute_member_count(self):
        # Robust compute to handle read_group output across versions
        grouped = self.env["discuss.channel.member"].read_group(
            [("channel_id", "in", self.ids)], ["channel_id"], ["channel_id"]
        )
        # read_group returns dicts like {'channel_id': (id, name), 'channel_id_count': n}
        counts = {}
        for res in grouped:
            ch = res.get("channel_id")
            if isinstance(ch, (list, tuple)) and ch:
                counts[ch[0]] = res.get("channel_id_count", 0)
            elif hasattr(ch, "id"):
                counts[ch.id] = res.get("channel_id_count", 0)
        for channel in self:
            channel.member_count = counts.get(channel.id, 0)