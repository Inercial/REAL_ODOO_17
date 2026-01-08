# Copyright 2020, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from datetime import datetime, timedelta

import pytz

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare


class SaleOrder(models.Model):
    _inherit = "sale.order"

    comment_marketing = fields.Text()
    can_modify_invoice = fields.Boolean(compute="_compute_can_modify_invoice")
    can_modify_quotation_date = fields.Boolean(compute="_compute_can_modify_quotation_date")
    can_modify_pricelist = fields.Boolean(compute="_compute_can_modify_pricelist")
    child_tag_ids = fields.Many2many(related="partner_id.child_tag_ids")
    analytic_account_id = fields.Many2one(copy=True)
    block_order = fields.Boolean(copy=False)
    order_signal = fields.Selection(
        [("on_time", "on time"), ("due_soon", "due soon"), ("overdue", "overdue")], compute="_compute_order_signal"
    )
    out_pending = fields.Selection(
        [
            ("avail", "available"),
            ("not_avail", "not available"),
        ],
        compute="_compute_out_pending",
    )

    def _domain_way_of_shipment(self):
        category = self.env.ref("real.res_partner_category_supplier_freight", False)
        category_id = False

        if category:
            category_id = category.id

        return [("category_id", "=", category_id)]

    way_of_shipment_id = fields.Many2one(
        "res.partner", domain=lambda self: self._domain_way_of_shipment(), tracking=True
    )
    way_shipment_type_id = fields.Many2one(related="partner_id.way_shipment_type_id")
    total_volume = fields.Float("Total volume", readonly=True, compute="_compute_total_volume")

    def _prepare_invoice(self):
        """Pricelist_id is set on invoice."""
        self.ensure_one()
        val = super()._prepare_invoice()

        if self.way_of_shipment_id:
            val.update({"way_of_shipment_id": self.way_of_shipment_id.id})

        return val

    @api.depends("partner_id", "company_id", "partner_shipping_id")
    def _compute_pricelist_id(self):
        for order in self:
            if order.state != "draft":
                continue
            if not order.partner_shipping_id:
                order.pricelist_id = False
                continue
            order = order.with_company(order.company_id)
            order.pricelist_id = order.partner_shipping_id.property_product_pricelist

    @api.onchange("partner_id")
    def _real_onchange_partner_id(self):
        """Use native method, because we need to execute first that method to
        change pricelist and then compute the price in every line.
        """
        default_child = False
        if self.partner_id.child_tag_ids:
            default_child = self.partner_id.child_tag_ids[0]
        self.partner_shipping_id = default_child
        self.analytic_account_id = self.user_id.default_analytic_account_id

    @api.onchange("partner_shipping_id")
    def _onchange_partner_shipping_id(self):
        res = super()._onchange_partner_shipping_id()

        if self.partner_shipping_id:
            self.update(
                {
                    "pricelist_id": (self.partner_shipping_id.property_product_pricelist),
                    "way_of_shipment_id": (self.partner_shipping_id.way_of_shipment_id),
                    "user_id": self.partner_shipping_id.user_id,
                    "analytic_account_id": (self.partner_shipping_id.user_id.default_analytic_account_id),
                }
            )

        return res

    @api.constrains("pricelist_id", "partner_shipping_id")
    def _check_prices_of_pricelist(self):
        for rec in self:
            rec.action_update_prices()

    @api.model_create_multi
    def create(self, vals_list):
        if self.env.user.has_group("real.res_groups_extra_permissions_sale_order_readonly"):
            raise UserError(_("Your not allowed to create quotations"))

        res = super().create(vals_list)
        for order in res:
            order.validate_no_empty_order()
            order.validate_payment_term_edit()
            order.validate_partner_shipping_id_pricelist()

            if not order.create_date:
                order.block_order = True

        return res

    def write(self, vals):
        for rec in self:
            if rec.create_date != rec.write_date and not self.env.user.has_group(
                "real.res_groups_can_modify_sale_order_after_creation"
            ):
                raise UserError(_("You are not allowed to edit a Sale Order."))

            # Indented the next lines to fix the expected singleton error.
            # Fixed the bug so that a seller cannot modify fields that are not allowed for his role.
            allowed_fields = ["note", "state", "message_main_attachment_id", "access_token"]
            seller_block = any(val not in allowed_fields for val in vals)

            if (
                rec.block_order
                and self.env.ref("real.res_users_role_seller") in self.env.user.groups_id.role_id
                and seller_block
            ):
                raise UserError(_("You cannot edit this quotation."))

            if vals and "show_update_pricelist" not in vals and not rec.block_order:
                vals["block_order"] = True

        res = super().write(vals)
        self.validate_no_empty_order()
        self.validate_payment_term_edit()
        self.validate_partner_shipping_id_pricelist()

        # Update way of shipment in all pickings related to the order
        for rec in self:
            if "way_of_shipment_id" in vals and rec.delivery_count > 0:
                pickings = rec.picking_ids
                pickings.write({"way_of_shipment_id": vals["way_of_shipment_id"]})

        return res

    def validate_partner_shipping_id_pricelist(self):
        for rec in self:
            if self.env.user.has_group("real.res_groups_can_confirm_sales_with_different_pricelist"):
                continue

            if rec.pricelist_id != rec.partner_shipping_id.property_product_pricelist:
                raise UserError(_("The pricelist cannot be different from the shipping address."))

    def validate_no_empty_order(self):
        for rec in self:
            if not rec.order_line:
                raise UserError(_("You cannot save quotes without lines."))

    def _compute_can_modify_invoice(self):
        self.can_modify_invoice = self.env.user.has_group("real.res_groups_can_access_partner_invoice_id")

    def _compute_can_modify_quotation_date(self):
        self.can_modify_quotation_date = self.env.user.has_group("real.res_groups_can_access_date_order")

    def _compute_can_modify_pricelist(self):
        self.can_modify_pricelist = self.env.user.has_group("real.res_groups_can_access_pricelist_id")

    def validate_payment_term_edit(self):
        for rec in self:
            if self.env.user.has_group("real.res_groups_can_access_payment_term_id"):
                continue

            if rec.partner_id.property_payment_term_id != rec.payment_term_id:
                raise UserError(_("You are not allowed to change the payment term"))

    @api.depends("order_line.price_total")
    def _compute_total_volume(self):
        for order in self:
            total_volume = 0.0

            for line in order.order_line:
                total_volume += line.line_volume

            order.update({"total_volume": total_volume})

    @api.model
    def _compute_order_signal(self):
        exclude = ["Parras de la Fuente", "Francisco I. Madero", "San Pedro"]
        # Mods to calculate the elapsed hours between the order and current dates WITHOUT considering the weekends
        # Convert current date to current timezone
        now = datetime.now().astimezone(pytz.timezone(self.env.user.tz))

        for rec in self:
            order_dt = rec.date_order.astimezone(pytz.timezone(self.env.user.tz))
            # Get the dates BETWEEN the order and current dates (not including both)
            dates = [order_dt.date() + timedelta(i + 1) for i in range((now.date() - order_dt.date()).days - 1)]
            # Sum 24 hours for each day in the dates list
            hours = 0
            hours = sum(24 for day in dates if day.isoweekday() < 6)

            # Substract or add the hours for the initial and ending dates
            if order_dt.date() == now.date() and order_dt.isoweekday() < 6:
                hours = (
                    hours
                    + (now.hour - order_dt.hour)
                    + (now.minute / 60 - order_dt.minute / 60)
                    + (now.second / 3600 - order_dt.second / 3600)
                )
            else:
                if order_dt.isoweekday() < 6:
                    hours = hours + 24 - order_dt.hour - order_dt.minute / 60 - order_dt.second / 3600
                if now.isoweekday() < 6:
                    hours = hours + now.hour + now.minute / 60 + now.second / 3600

            if not any(delivery.state not in ("done", "cancel") for delivery in rec.picking_ids):
                rec.order_signal = ""
            elif (
                rec.partner_shipping_id.city_id.name in exclude and rec.partner_shipping_id.state_id.name == "Coahuila"
            ):
                if hours <= 48:
                    rec.order_signal = "on_time"
                elif 48 < hours < 72:
                    rec.order_signal = "due_soon"
                else:
                    rec.order_signal = "overdue"
            elif rec.client_location == "local":
                if hours <= 36:
                    rec.order_signal = "on_time"
                elif 36 < hours < 60:
                    rec.order_signal = "due_soon"
                else:
                    rec.order_signal = "overdue"
            elif rec.client_location == "foreigner":
                if hours <= 72:
                    rec.order_signal = "on_time"
                elif 72 < hours < 96:
                    rec.order_signal = "due_soon"
                else:
                    rec.order_signal = "overdue"
            else:
                rec.order_signal = "overdue"

    def _compute_out_pending(self):
        for rec in self:
            rec.out_pending = ""
            delivery = self.env["stock.picking"].search(
                [("sale_id", "=", rec.id), ("picking_type_id", "=", 2), ("state", "in", ("assigned", "waiting"))]
            )
            if delivery:
                rec.out_pending = "avail"

                for picking in delivery:
                    if any(
                        float_compare(
                            move.forecast_availability,
                            move.product_qty,
                            precision_rounding=move.product_id.uom_id.rounding,
                        )
                        == -1
                        or move.forecast_expected_date
                        for move in picking.move_ids
                    ):
                        rec.out_pending = "not_avail"
                        break


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    can_modify_price_unit = fields.Boolean(compute="_compute_can_modify_price_unit")
    can_modify_tax_id = fields.Boolean(compute="_compute_can_modify_tax_id")
    can_modify_customer_lead = fields.Boolean(compute="_compute_can_modify_customer_lead")
    can_modify_line_description = fields.Boolean(compute="_compute_can_modify_line_description")
    line_volume = fields.Float("Volume", compute="_compute_line_volume")

    def _compute_can_modify_price_unit(self):
        self.can_modify_price_unit = self.env.user.has_group("real.res_groups_can_access_price_unit")

    def _compute_can_modify_tax_id(self):
        self.can_modify_tax_id = self.env.user.has_group("real.res_groups_can_access_tax_id")

    def _compute_can_modify_customer_lead(self):
        self.can_modify_customer_lead = self.env.user.has_group("real.res_groups_can_modify_customer_lead")

    def _compute_can_modify_line_description(self):
        self.can_modify_line_description = self.env.user.has_group("real.res_groups_can_modify_line_description")

    def _prepare_invoice_line(self, **optional_values):
        res = super()._prepare_invoice_line(**optional_values)
        res["freight_cost"] = self.order_id.partner_shipping_id.freight_cost
        return res

    @api.depends("product_uom_qty")
    def _compute_line_volume(self):
        for rec in self:
            rec.line_volume = (rec.product_uom_qty * rec.product_id.volume) / 1000
