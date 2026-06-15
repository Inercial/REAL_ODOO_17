from odoo import api, fields, models


class AccountReconcileWizard(models.TransientModel):
    _inherit = "account.reconcile.wizard"

    # The main distribution field
    analytic_distribution = fields.Json(
        string="Analytic Distribution",
    )

    # Required field for the JS widget to work without crashing
    analytic_precision = fields.Integer(
        related="company_id.currency_id.decimal_places",
        string="Analytic Precision",
    )

    @api.onchange("account_id", "label")
    def _onchange_reconcile_fields(self):
        """Automatically pulls the analytic distribution based on account and label"""
        if not self.account_id:
            self.analytic_distribution = False
            return

        # 1. Single DB query: Grab all reconcile rules using this account
        model_lines = self.env["account.reconcile.model.line"].search([("account_id", "=", self.account_id.id)])

        # 2. In-Memory Filter: Prioritize an exact label match, fallback to the first line found
        best_match = model_lines.filtered(lambda l: l.label == self.label) or model_lines

        # 3. Assign the distribution if a match exists
        self.analytic_distribution = best_match[0].analytic_distribution if best_match else False

    def create_write_off(self):
        """
        Intercept the write-off move creation right before it gets planned
        and stamp the wizard's analytic distribution onto the write-off lines.
        """
        # 1. Let Odoo create the write-off entry natively
        write_off_move = super().create_write_off()

        # 2. Inject the analytic distribution onto the lines matching our selected account
        if self.analytic_distribution and write_off_move:
            lines_to_update = write_off_move.line_ids.filtered(lambda line: line.account_id == self.account_id)
            if lines_to_update:
                lines_to_update.write({"analytic_distribution": self.analytic_distribution})

        return write_off_move
