from odoo import models, fields

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    analytic_account_name = fields.Char(
        compute='_compute_analytic_account_name',
        store=False
    )

    def _compute_analytic_account_name(self):
        Analytic = self.env['account.analytic.account']
        for line in self:
            name = ''
            distr = line.analytic_distribution or {}
            for key in distr.keys():
                for acc_id in key.split(','):
                    acc = Analytic.browse(int(acc_id.strip()))
                    if acc.exists() and (not acc.plan_id or acc.plan_id.id != 78):
                        name = acc.name
                        break
                if name:
                    break
            line.analytic_account_name = name
