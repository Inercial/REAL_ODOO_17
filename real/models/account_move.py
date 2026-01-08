# Copyright 2020, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    way_of_shipment_id = fields.Many2one(
        "res.partner", domain=lambda self: self._domain_way_of_shipment(), tracking=True
    )
    way_shipment_type_id = fields.Many2one(related="partner_id.way_shipment_type_id", store=True)
    child_tag_ids = fields.Many2many(related="partner_id.child_tag_ids")
    is_freight_supplier = fields.Boolean(default=False)
    state_id = fields.Many2one("res.country.state")
    city_id = fields.Many2one("res.city")
    stop_inv = fields.Boolean(default=False, tracking=True)
    tons_display = fields.Float(digits="Product Unit of Measure", compute="_compute_tons", store=True, string="Tons")
    previous_folio = fields.Char()

    @api.depends("invoice_line_ids")
    def _compute_tons(self):
        for rec in self:
            rec.tons_display = sum(rec.invoice_line_ids.mapped("tons_display"))

    @api.depends("move_type", "invoice_date_due", "invoice_date", "invoice_payment_term_id")
    def _compute_l10n_mx_edi_payment_policy(self):
        for move in self:
            move.l10n_mx_edi_payment_policy = False

            if (
                move.is_invoice(include_receipts=True)
                and move.l10n_mx_edi_is_cfdi_needed
                and move.invoice_date_due
                and move.invoice_date
            ):
                move.l10n_mx_edi_payment_policy = "PUE"

                if move.move_type == "out_invoice" and (
                    move.invoice_date_due > move.invoice_date or len(move.invoice_payment_term_id.line_ids) > 1
                ):
                    move.l10n_mx_edi_payment_policy = "PPD"

    def action_register_payment(self):
        names = []
        for rec in self:
            if rec.stop_inv:
                names.append(rec.name)
        if names:
            msg = _("These invoices are blocked for payment. \nBlocked invoices: %s ", names)
            raise UserError(msg)
        return super().action_register_payment()

    @api.model
    def default_get(self, default_fields):
        res = super().default_get(default_fields)
        if self._context.get("default_move_type") == "in_invoice":
            res["date"] = fields.Date.context_today(self)
            res["invoice_date"] = fields.Date.context_today(self)
        return res

    def action_post(self):
        self._chek_pdf_xml()
        return super().action_post()

    def _chek_pdf_xml(self):
        mx_country = self.env.ref("base.mx")
        for rec in self:
            if (
                not rec.l10n_edi_expense_id
                and rec.move_type in ["in_invoice", "in_refund"]
                and rec.partner_id.country_id
                and rec.partner_id.country_id == mx_country
            ):
                attachments = self.env["ir.attachment"].search(
                    [
                        ("res_id", "=", rec.id),
                        ("res_model", "=", "account.move"),
                    ]
                )
                if not attachments:
                    raise UserError(
                        _("You cannot publish a supplier invoice if you do not have the pdf and xml attached")
                    )
                has_xml = False
                has_pdf = False
                for name in attachments.mapped("name"):
                    if ".xml" in name.lower():
                        has_xml = True
                    if ".pdf" in name.lower():
                        has_pdf = True
                if has_pdf and has_xml:
                    return True
                raise UserError(_("The xml is missing or the pdf is missing"))

    def _domain_way_of_shipment(self):
        category = self.env.ref("real.res_partner_category_supplier_freight", False)
        category_id = False
        if category:
            category_id = category.id
        return [("category_id", "=", category_id)]

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        res = super()._onchange_partner_id()

        if self.partner_id:
            freight_category = self.env.ref("real.res_partner_category_supplier_freight", raise_if_not_found=False)
            if freight_category.id in self.partner_id.category_id.ids:
                self.is_freight_supplier = True
            else:
                self.is_freight_supplier = False
                self.state_id = False
                self.city_id = False
        else:
            self.is_freight_supplier = False

        if self.move_type in ["out_invoice", "out_refund"]:
            vals = {"partner_shipping_id": False}
            if self.partner_id.child_tag_ids:
                child = self.partner_id.child_tag_ids[0]
                vals.update(
                    {
                        "partner_shipping_id": child,
                        "way_of_shipment_id": child.way_of_shipment_id,
                        "invoice_user_id": child.user_id,
                    }
                )
            self.update(vals)
        return res

    @api.onchange("partner_shipping_id")
    def _onchange_partner_shipping_id(self):
        if self.partner_shipping_id and (self.move_type in ["out_invoice", "out_refund"]):
            self.update(
                {
                    "way_of_shipment_id": (self.partner_shipping_id.way_of_shipment_id),
                    "invoice_user_id": self.partner_shipping_id.user_id,
                }
            )
            for line in self.invoice_line_ids:
                line.freight_cost = self.partner_shipping_id.freight_cost

    @api.onchange("invoice_line_ids")
    def _onchange_invoice_line_ids(self):
        if self.move_type == "out_invoice":
            for line in self.invoice_line_ids:
                line.freight_cost = self.partner_shipping_id.freight_cost

    @api.onchange("invoice_date")
    def _onchange_invoice_date_real(self):
        if self.invoice_date and self.move_type in ("in_invoice", "in_refund", "in_receipt"):
            self.date = self.invoice_date

    @api.onchange("state_id")
    def _onchange_city_id(self):
        self.city_id = False


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    freight_cost = fields.Float(digits="Freight Factor")
    price_unit_without_freight = fields.Float(compute="_compute_price_unit_without_freight", store=True)
    tons_display = fields.Float(
        digits="Product Unit of Measure",
        compute="_compute_tons",
        store=True,
        string="Tons",
    )

    @api.depends("quantity", "product_id")
    def _compute_tons(self):
        for rec in self:
            tons = 0
            if rec.product_id:
                tons = rec.quantity * rec.product_id.weight / 1000
            rec.tons_display = tons

    @api.depends("product_id", "freight_cost")
    def _compute_price_unit_without_freight(self):
        for rec in self:
            price_unit_without_freight = 0
            if rec.product_id and rec.move_id.move_type in ("out_invoice", "out_refund"):
                price_unit_without_freight = rec.price_unit - (rec.product_id.freight_weight * rec.freight_cost)
            rec.price_unit_without_freight = price_unit_without_freight

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            company = self.env.user.company_id
            accounts = company.expense_currency_exchange_account_id
            accounts |= company.income_currency_exchange_account_id
            if vals.get("account_id") and vals["account_id"] in accounts.ids:
                vals["analytic_distribution"] = {"110": 100}
        return super().create(vals_list)
