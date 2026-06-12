from odoo import _, fields, models
from odoo.exceptions import ValidationError


class PendingTonsWizard(models.TransientModel):
    _name = "pending.tons.wizard"
    _description = "Pending Tons Report"

    datetime_input = fields.Datetime(string="Datetime", required=True)

    result_tons = fields.Float(string="Pending Tons", readonly=True)

    def action_compute(self):
        self.ensure_one()

        if not self.datetime_input:
            raise ValidationError(_("Datetime is required."))

        date = self.datetime_input

        query = """
            SELECT
                COALESCE(SUM(sub.tons), 0)
            FROM (

                SELECT
                    sp.scheduled_date AS scheduled_date,
                    mh.create_date AS done_date,
                    sm_sum.tons AS tons

                FROM stock_picking sp

                LEFT JOIN sale_order so
                    ON so.id = sp.sale_id

                LEFT JOIN (
                    SELECT
                        sm.picking_id,
                        SUM(sm.tons_display) AS tons
                    FROM stock_move sm
                    JOIN product_product pp
                        ON pp.id = sm.product_id
                    WHERE pp.parent_category_id = 7
                    GROUP BY sm.picking_id
                ) sm_sum
                    ON sm_sum.picking_id = sp.id

                LEFT JOIN LATERAL (
                    SELECT mtv.create_date
                    FROM mail_tracking_value mtv
                    JOIN mail_message mm
                        ON mtv.mail_message_id = mm.id
                    WHERE mtv.old_value_char IN (
                        'Esperando otra operación',
                        'En espera de otra operación',
                        'En espera',
                        'Preparado',
                        'Listo'
                    )
                    AND mtv.new_value_char = 'Hecho'
                    AND mm.res_id = sp.id
                    ORDER BY mtv.create_date DESC
                    LIMIT 1
                ) mh ON true

                WHERE
                    sp.location_dest_id = 5
                    AND sp.picking_type_id = 2
                    AND so.state = 'sale'
                    AND sp.state != 'cancel'

            ) sub

            WHERE
                sub.scheduled_date <= %s
                AND (
                    sub.done_date IS NULL
                    OR sub.done_date > %s
                )
        """

        self.env.cr.execute(query, (date, date))
        result = self.env.cr.fetchone()[0]

        # Assign result
        self.result_tons = result

        # Reopen wizard using XML action (keeps title)
        action = self.env.ref("real_reports.action_pending_tons_wizard").read()[0]

        action.update(
            {
                "res_id": self.id,
                "target": "new",
            }
        )

        return action
