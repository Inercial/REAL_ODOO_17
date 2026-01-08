from odoo import api, fields, models


class InvoiceApplyAdvancesDetail(models.TransientModel):
    _inherit = "invoice.apply.advance.detail"

    advance_date = fields.Date(compute="_compute_date_total")
    advance_total = fields.Float(compute="_compute_date_total")

    @api.depends("advance_id")
    def _compute_date_total(self):
        with_advance = self.filtered("advance_id")

        for line in self - with_advance:
            line.advance_date = False
            line.advance_total = 0

        for line in self:
            for field in self.advance_id:
                if field.name == line.advance_id.name:
                    line.advance_date = field.date
                    line.advance_total = field.advance_total
