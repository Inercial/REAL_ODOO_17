# Copyright 2020, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging

from psycopg2 import DatabaseError, sql

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    freight_cost = fields.Float(digits="Freight Factor")
    loads = fields.Boolean()
    prompt_payment = fields.Boolean()
    review_day = fields.Selection(
        [
            ("doesNotApply", "Does not apply"),
            ("monday", "Monday"),
            ("tuesday", "Tuesday"),
            ("wednesday", "Wednesday"),
            ("thursday", "Thursday"),
            ("friday", "Friday"),
            ("saturday", "Saturday"),
            ("sunday", "Sunday"),
        ],
        copy=False,
        help="This field help to know when the reviews days are.",
    )
    paydays = fields.Selection(
        [
            ("doesNotApply", "Does not apply"),
            ("monday", "Monday"),
            ("tuesday", "Tuesday"),
            ("wednesday", "Wednesday"),
            ("thursday", "Thursday"),
            ("friday", "Friday"),
            ("saturday", "Saturday"),
            ("sunday", "Sunday"),
        ],
        copy=False,
        help="This field help to know when the paydays are.",
    )
    full_record = fields.Boolean()
    pamphletes = fields.Boolean()
    samples = fields.Boolean()
    pricers = fields.Boolean()
    child_tag_ids = fields.Many2many(
        comodel_name="res.partner",
        relation="res_partner_tag_rel",
        column1="parent_id",
        column2="child_id",
        store=True,
        string="Contacts",
        compute="_compute_childs_type_delivery",
    )
    commercial_name = fields.Char()
    sales_phone = fields.Char()
    commercial_address = fields.Char()

    def _domain_way_of_shipment(self):
        category = self.env.ref("real.res_partner_category_supplier_freight", False)
        category_id = False
        if category:
            category_id = category.id
        return [("category_id", "=", category_id)]

    way_of_shipment_id = fields.Many2one("res.partner", domain=lambda self: self._domain_way_of_shipment())
    way_shipment_type_id = fields.Many2one("way.of.shipment.type")
    visit_frequency = fields.Integer(default=0)
    contact_is_customer = fields.Boolean(string="Is customer?")
    contact_is_supplier = fields.Boolean(string="Is supplier?")
    prompt_payment_days = fields.Integer()
    special_info = fields.Text()
    total_due = fields.Monetary(
        groups="account.group_account_readonly,account.group_account_invoice,real.res_users_role_seller"
    )
    total_overdue = fields.Monetary(
        groups="account.group_account_readonly,account.group_account_invoice,real.res_users_role_seller"
    )
    followup_status = fields.Selection(
        groups="account.group_account_readonly,account.group_account_invoice,real.res_users_role_seller"
    )
    followup_line_id = fields.Many2one(
        groups="account.group_account_readonly,account.group_account_invoice,real.res_users_role_seller"
    )
    followup_responsible_id = fields.Many2one(
        groups="account.group_account_readonly,account.group_account_invoice,real.res_users_role_seller"
    )

    @api.onchange("company_type")
    def _onchange_company_type(self):
        if self.company_type == "person":
            self.type = "delivery"
        if self.company_type == "company":
            self.type = "contact"

    def _update_childs_parents(self, parents, tags_partner_group):
        for parent in parents:
            tags_parent = parent.mapped("category_id").filtered(lambda cat: cat in tags_partner_group)
            childs = parent.search([("category_id", "in", tags_parent.ids), ("type", "=", "delivery")])
            parent.child_tag_ids = childs

    @api.depends("category_id", "type")
    def _compute_childs_type_delivery(self):
        tag_agroup = self.env.ref("real.res_partner_category_group", False)

        if not tag_agroup:
            return

        for rec in self:
            if rec.is_company:
                tags_partner_group = rec.category_id.filtered(lambda cat: cat.parent_id.id == tag_agroup.id)
                childs = self.search([("category_id", "in", tags_partner_group.ids), ("type", "=", "delivery")])
                rec.child_tag_ids = childs
                break

            if rec.name:
                for tag in self.env["res.partner.category"].search([("parent_id", "=", tag_agroup.id)]):
                    if tag.name.upper() in rec.name.upper():
                        parents = self.search([("is_company", "=", True), ("category_id", "in", tag.id)])
                        tags_parents = parents.category_id.filtered(lambda cat: cat.parent_id.id == tag_agroup.id)
                        rec._update_childs_parents(parents, tags_parents)

    @api.onchange("contact_is_customer")
    def _onchange_contact_is_customer(self):
        if self.contact_is_customer:
            self._increase_rank("customer_rank")
        else:
            self._reset_rank("customer_rank")

    @api.onchange("contact_is_supplier")
    def _onchange_contact_is_supplier(self):
        if self.contact_is_supplier:
            self._increase_rank("supplier_rank")
        else:
            self._reset_rank("supplier_rank")

    def _reset_rank(self, field):
        if self.ids and field in ["customer_rank", "supplier_rank"]:
            try:
                with self.env.cr.savepoint(flush=False):
                    query = sql.SQL(
                        """
                        SELECT {field} FROM res_partner WHERE ID IN %(partner_ids)s FOR UPDATE NOWAIT;
                        UPDATE res_partner SET {field} = 0
                        WHERE id IN %(partner_ids)s
                        """
                    ).format(field=sql.Identifier(field))
                    self.env.cr.execute(query, {"partner_ids": tuple(self.ids)})
                    for partner in self:
                        self.env.cache.remove(partner, partner._fields[field])
            except DatabaseError as e:
                if e.pgcode == "55P03":
                    _logger.debug("Another transaction already locked partner rows. Cannot update partner ranks.")
                else:
                    raise e

    def _get_risk_sale_order_domain(self):
        return super()._get_risk_sale_order_domain() + [("invoice_status", "=", "no")]
