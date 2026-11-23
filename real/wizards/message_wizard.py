from odoo import fields, models


class GenericMessageWizard(models.TransientModel):
    _name = "generic.message.wizard"

    message = fields.Html(readonly=True)
    show_continue = fields.Boolean(readonly=True)
    target_model = fields.Char(readonly=True)
    target_res_id = fields.Integer(readonly=True)

    def action_continue(self):
        self.ensure_one()
        if self.target_model and self.target_res_id:
            record = self.env[self.target_model].browse(self.target_res_id).exists()
            if record and hasattr(record, "action_continue_after_message"):
                return record.action_continue_after_message()
        return {"type": "ir.actions.act_window_close"}

    def action_back(self):
        return {"type": "ir.actions.act_window_close"}