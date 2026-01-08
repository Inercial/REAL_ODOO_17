# Copyright 2020, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import re
from datetime import date, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ProductionLot(models.Model):
    _inherit = "stock.lot"

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            rec.validate_lot_name()
        return records

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            if vals.get("name"):
                rec.validate_lot_name()
        return res

    def validate_lot_name(self):
        self.ensure_one()
        categ = self.env["product.category"].search(
            [
                ("id", "parent_of", self.product_id.categ_id.id),
                "|",
                ("name", "=", "PT PINTURAS Y PASTAS"),
                ("name", "=", "PT POLVOS"),
            ]
        )
        if not categ:
            return False
        pattern = "^[A-Z]([0-2][0-9]|[3][0-1])([0][0-9]|[1][0-2])([2-9][0-9])\\d{2}$"
        if categ.name == "PT PINTURAS Y PASTAS":
            pattern = "^([0-2][0-9]|[3][0-1])([0][0-9]|[1][0-2])([2-9][0-9])\\d{2}[A-Z]{3}\\d{3}$"
        regex = re.compile(pattern)
        match = regex.match(self["name"])
        if not match:
            definition = _(
                "1 letter indicating the stamp (Machine) color.\n"
                "6 Digits for the date in format ddmmyy.\n"
                "2 Digits for consecutive number.\n\n"
                "Example: A31122001"
            )
            if categ.name == "PT PINTURAS Y PASTAS":
                definition = _(
                    "6 Digits for the date in format ddmmyy.\n"
                    "2 Digits for consecutive number.\n"
                    "3 Letters\n"
                    "3 Digits\n\n"
                    "Example: 31122001AAA000"
                )
            raise UserError(
                _("The name of the lot does not meet the defined standard\n\n%(definition)s", definition=definition)
            )
        date_tuple = [int(x) for x in match.groups()]
        date_tuple[2] += 2000  # Convert to year 20XX
        try:
            lot_date = date(
                year=date_tuple[2],
                month=date_tuple[1],
                day=date_tuple[0],
            )
        except ValueError:
            raise UserError(
                _("Invalid date: Month %(month)s has no day %(day)s", month=date_tuple[1], day=date_tuple[0])
            )
        today = fields.Date.context_today(self)
        min_date = today - timedelta(days=10)
        if lot_date < min_date or lot_date > today:
            raise UserError(
                _(
                    "The date is not within the allowed range.\n(date_min)%s - %(date_max)s",
                    date_min=min_date.strftime("%d/%m/%Y"),
                    date_max=today.strftime("%d/%m/%Y"),
                )
            )
