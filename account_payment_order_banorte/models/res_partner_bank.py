# Copyright 2020, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    id_supplier = fields.Char(
        size=13, help="Supplier ID that must exist in the supplier database.", string="ID Supplier"
    )
    operation_type = fields.Selection(
        [
            ("01", "Own"),
            ("02", "Third parties"),
            ("04", "SPEI"),
            ("05", "TEF"),
            ("09", "TdeC Empresariales Banorte"),
            ("10", "Pago de TdC Banorte"),
            ("11", "Pago de TdC Otros Bancos"),
            ("12", "Pago de TdC AMEX"),
        ]
    )
    supplier_reference = fields.Char(
        help="Field used to define reference of supplier, if it's not used the"
        " reference must be the invoices that are paid."
    )

    @api.depends("acc_holder_name", "partner_id")
    def _compute_display_name(self):
        res = super()._compute_display_name()

        for bank in self:
            # Only modify for company-owned bank accounts (used in internal transfers)
            # Skip if no holder name or not a company account
            if not bank.acc_holder_name or bank.partner_id != self.env.company.partner_id:
                continue

            current_name = bank.display_name
            holder_part = f" · {bank.acc_holder_name}"

            # Insert holder after acc_number, before bank name or any suffix
            if " - " in current_name:
                # Has bank name: "0123456789 · BBVA (something)"
                acc_part, rest = current_name.split(" - ", 1)
                bank.display_name = f"{acc_part}{holder_part} · {rest}"
            elif " (" in current_name:
                # No bank name but has label: "0123456789 (trusted)"
                acc_part, suffix = current_name.rsplit(" (", 1)
                bank.display_name = f"{acc_part}{holder_part} ({suffix}"
            else:
                # Simple fallback
                bank.display_name += holder_part
        return res
