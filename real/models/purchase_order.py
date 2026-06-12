from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    currency_copy = fields.Char("Currency (Copy)", compute="_compute_currency_copy", store=False)

    @api.onchange("currency_id")
    def _compute_currency_copy(self):
        self.currency_copy = self.currency_id.name

    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()
        freight_category = self.env.ref("real.res_partner_category_supplier_freight", raise_if_not_found=False)
        is_freight_supplier = bool(freight_category.id in self.partner_id.category_id.ids)
        invoice_vals.update(
            {
                "is_freight_supplier": is_freight_supplier,
            }
        )
        return invoice_vals

    def button_confirm(self):
        for order in self:
            product_lines = order.order_line.filtered(lambda line: not line.analytic_distribution)

            if product_lines:
                raise ValidationError(_("Please fill Analytic Distribution on all product lines."))

        return super().button_confirm()
