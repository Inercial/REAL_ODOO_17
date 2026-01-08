from odoo import api, fields, models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    has_pending_sample = fields.Boolean(compute="_compute_has_pending_sample")

    @api.depends("count")
    def _compute_has_pending_sample(self):
        current_orders = self.env["sale.order"].browse(self._context.get("active_ids"))

        for so in current_orders:
            self.has_pending_sample = bool(
                self.env["stock.request.order"].search_count(
                    [
                        ("partner_id", "=", so.partner_id.id),
                        ("location_id", "=", 24),
                        ("state", "in", ["draft", "open"]),
                    ]
                )
                > 0
            )
