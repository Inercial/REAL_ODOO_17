# Copyright 2020, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
# pylint: skip-file

from odoo import fields, models


class AccountMoveReversal(models.TransientModel):
    _inherit = "account.move.reversal"

    rectified_invoices = fields.Selection(
        selection=[
            ("unassigned", "Unassigned"),
            ("application_of_advance", "Application of Advance"),
            ("uncollectible_account", "Uncollectible account"),
            ("Special_discounts", "Special discounts"),
            ("discounts_promp_payment", "Discounts for prompt payment"),
            ("advance_refund", "Advance refund"),
            ("Seller_error", "Seller error"),
            ("custom_err", "Customer error"),
            ("shipment_delivery_mistake", "Shipment delivery mistake"),
            ("logistics_err", "Logistics error"),
            ("wet_shipping_material", "Wet shipping material"),
            ("broken_shipping_material", "Broken shipping material"),
            ("non_rotating_material", "Non-rotating material"),
            ("material_exit_sample", "Material exit as sample"),
            ("return_invoice_paid", "Return invoice paid"),
            ("physical_retur", "Physical return"),
            ("different_prices", "Different prices"),
            ("damaged_material", "Damaged Material"),
            ("customer_not_received", "Customer not received"),
            ("did_not_leave_plant", "Did not leave the plant"),
            ("rebilling_others", "Rebilling Others"),
            ("rebilling_date", "Rebilling by date"),
            ("rebilling_type_payment", "Rebilling by type of payment"),
            ("transfer_other_client", "Transfer to other client"),
        ],
        required=True,
        default="unassigned",
    )

    def reverse_moves(self, is_modify=False):
        res = super().reverse_moves(is_modify)
        self.new_move_ids.rectified_invoices = self.rectified_invoices
        return res
