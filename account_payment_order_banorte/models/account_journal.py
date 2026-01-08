# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import re
from datetime import datetime

from odoo import api, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    def _get_bank_statements_available_import_formats(self):
        rslt = super()._get_bank_statements_available_import_formats()
        rslt.extend(["TXT"])
        return rslt

    def _check_file_format(self, filename):
        return filename and filename.lower().strip().endswith(".txt")

    @api.model
    def _search_partner(self, ref):
        match_rfc = re.search("RFC(.*)", ref) or re.search("R.F.C(.*?)", ref)
        if match_rfc:
            vat = match_rfc.group(1)
            vat = vat[0:14].strip()
            partner = self.env["res.partner"].search([("vat", "=ilike", vat)], limit=1)
            return partner.id
        return False

    @api.model
    def _search_method(self, ref):
        match_spei = re.search("SPEI (.*?)", ref)
        if match_spei:
            method_id = 3
            return method_id
        return False

    def _import_bank_statement(self, attachments):
        # In case of CSV files, only one file can be imported at a time.
        if len(attachments) > 1:
            return super()._import_bank_statement(attachments)

        if not self._check_file_format(attachments.name):
            return super()._import_bank_statement(attachments)

        journal_id = self.id
        file_data = str(attachments.mapped("raw")[0]).replace("\\xa0", " ").split("b'")[1].split("'")[0].split("\\n")
        # toma la fecha final del registro de cabecera de cuenta para asignarla como fecha de cada operacion
        date = file_data[0][41:47]
        statement_dict = {}
        count = 0
        for line in file_data:
            if line[0:2] == "11":
                # 11 registro de cabecera de cuenta
                continue
            if line[0:2] == "22":
                # 12 registro principal de movimientos
                # fecha de operacion de 6 caracteres = date
                # debe o haber (1 negativo, 2 positivo)
                # referencia de 30 caracteres [52:82
                # monto de 14 caracteres = amount
                count += 1
                amount = int(line[28:42]) / 100
                statement_dict.setdefault(
                    date,
                    {
                        "name": self.process_date(date),
                        "journal_id": journal_id,
                        "line_ids": [],
                    },
                )
                statement_dict[date]["line_ids"].append(
                    (
                        0,
                        0,
                        {
                            "date": self.process_date(date),
                            "payment_ref": line[52:82].strip(),
                            "journal_id": journal_id,
                            "amount": amount if line[27] == "2" else -amount,
                            "narration": "",
                        },
                    )
                )
            if line[0:2] == "23":
                # 23 Registro complementario de concepto
                # Se busca el RFC en el concepto de 76 caracteres
                # ademas el metodod de pago si SPEI = Transferencia
                # electronica
                if len(statement_dict) > 1 and count > 1:
                    count = 0
                    statement_dict[date]["line_ids"][count][2]["narration"] += " " + line[4:80].strip()
                statement_dict[date]["line_ids"][count - 1][2]["narration"] += " " + line[4:80].strip()

        for statement in statement_dict.values():
            for line in statement["line_ids"]:
                line[2]["partner_id"] = self._search_partner(line[2]["narration"])
                line[2]["l10n_mx_edi_payment_method_id"] = self._search_method(line[2]["narration"])
        statements = self.env["account.bank.statement"].create(statement_dict.values())
        action = self.env["ir.actions.actions"]._for_xml_id(
            "account_statement_base.account_bank_statement_line_action"
        )
        action["domain"] = [("id", "in", statements.mapped("line_ids").ids)]
        action["context"] = {"account_bank_statement_line_main_view": True}
        return action

    def process_date(self, date):
        date_format = "%y%m%d"
        return datetime.strptime(date, date_format).date()
