from odoo import _, fields, models
from odoo.exceptions import ValidationError


class PendingTonsWizard(models.TransientModel):
    _name = "pending.tons.wizard"
    _description = "Pending Tons Report"

    datetime_input = fields.Datetime(string="Datetime", required=True)
    line_ids = fields.One2many("pending.tons.wizard.line", "wizard_id", string="Vendedores")
    total_tons = fields.Float(string="Total Tons", readonly=True)

    def action_compute(self):
        self.ensure_one()

        if not self.datetime_input:
            raise ValidationError(_("Datetime is required."))

        # Clear existing lines prior to recalculation
        self.line_ids.unlink()

        date = self.datetime_input

        query = """
            SELECT
                COALESCE(rp.name, 'Sin Vendedor') AS vendedor,
                COALESCE(SUM(sm.tons_display), 0) AS total_tons
            FROM stock_picking sp

            -- 1. Explicit INNER JOIN filtering early
            INNER JOIN sale_order so
                ON so.id = sp.sale_id
               AND so.state = 'sale'

            -- 2. Salesperson joins
            LEFT JOIN res_users ru
                ON ru.id = so.user_id

            LEFT JOIN res_partner rp
                ON rp.id = ru.partner_id

            -- 3. Set-based moves join
            INNER JOIN stock_move sm
                ON sm.picking_id = sp.id

            INNER JOIN product_product pp
                ON pp.id = sm.product_id
               AND pp.parent_category_id = 7

            -- 4. Date and status filters
            WHERE
                sp.location_dest_id = 5
                AND sp.picking_type_id = 2
                AND sp.state != 'cancel'
                AND sp.scheduled_date <= %s
                AND (sp.date_done IS NULL OR sp.date_done > %s)

            GROUP BY
                rp.id,
                rp.name
            ORDER BY
                total_tons DESC,
                vendedor ASC
        """

        self.env.cr.execute(query, (date, date))
        results = self.env.cr.fetchall()

        lines = []
        grand_total = 0.0

        for vendedor, tons in results:
            lines.append(
                (
                    0,
                    0,
                    {
                        "vendedor": vendedor,
                        "tons": tons,
                    },
                )
            )
            grand_total += tons

        # Save lines and overall total to the wizard instance
        self.write(
            {
                "line_ids": lines,
                "total_tons": grand_total,
            }
        )

        # Reopen wizard
        action = self.env.ref("real_reports.action_pending_tons_wizard").read()[0]
        action.update(
            {
                "res_id": self.id,
                "target": "new",
            }
        )
        return action


class PendingTonsWizardLine(models.TransientModel):
    _name = "pending.tons.wizard.line"
    _description = "Pending Tons Report Line"

    wizard_id = fields.Many2one("pending.tons.wizard", string="Wizard", ondelete="cascade")
    vendedor = fields.Char(string="Vendedor", readonly=True)
    tons = fields.Float(string="Tons", readonly=True)
