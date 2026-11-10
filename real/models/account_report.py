import io
import re

from odoo import _, fields, models

from collections import defaultdict
from odoo.exceptions import UserError

CFDIBCE_XSLT_CADENA = 'l10n_mx_reports/data/xslt/1.3/BalanzaComprobacion_1_2.xslt'
CFDICATALOGO_XSLT_CADENA = 'l10n_mx_reports/data/xslt/1.3/CatalogoCuentas_1_2.xslt'

class TrialBalanceCustomHandler(models.AbstractModel):
    _inherit = "account.trial.balance.report.handler"

    def _custom_options_initializer(self, report, options, previous_options=None):
        super()._custom_options_initializer(report, options, previous_options)
        if not options.get("hide_columns"):
            return

        if main_headers := options.get("column_headers", [[]])[0]:
            last_hdr = len(main_headers) - 1
            for i, header in enumerate(main_headers):
                header["colspan"] = 1 if i in (0, last_hdr) else 2

        cols = options.get("columns", [])
        comp = options.get("comparison", {})
        comp_periods = 0 if comp.get("filter") == "no_comparison" else comp.get("number_period", 0)
        total_cols = len(cols) - (comp_periods + 6)

        if total_cols > 0:
            for i, col in enumerate(cols):
                if i in (0, total_cols):
                    col["name"] = "Saldo"
                elif 0 < i < total_cols:
                    col["name"] = "Débito" if i % 2 != 0 else "Crédito"
                else:
                    col["name"] = ""

    def _dynamic_lines_generator(self, report, options, all_column_groups_expression_totals, warnings=None):
        lines = super()._dynamic_lines_generator(report, options, all_column_groups_expression_totals, warnings)
        if options.get("hide_columns"):  # and options.get("comparison").get("filter") == "no_comparison":
            for line_tuple in lines:
                line = line_tuple[1]
                if "columns" in line and len(line["columns"]) > 8:
                    line_len = len(line["columns"])
                    to_remove = {0, 1, line_len - 3, line_len - 2}
                    to_remove.update(range(5, line_len - 3, 3))
                    line["columns"] = [col for i, col in enumerate(line["columns"]) if i not in to_remove]
        return lines


    def _l10n_mx_get_sat_values(self, options):
        super()._l10n_mx_get_sat_values(options)
        report = self.env['account.report'].browse(options['report_id'])
        sat_options = self._l10n_mx_get_sat_options(options)
        report_lines = report._get_lines(sat_options)
        sat_code = re.compile(r'((\d{3})\.\d{2})')

        report_lines = [line for line in report_lines if line.get('level') >= 4]
        account_ids = [report._get_res_id_from_line_id(line['id'], 'account.account') for line in report_lines]
        accounts = self.env['account.account'].browse(account_ids)
        self._check_accounts_code_sat_validity(accounts, options, 'action_l10n_mx_generate_sat_xml')

        account_lines = []
        parents = defaultdict(lambda: defaultdict(int))
        for account, line in zip(accounts, report_lines):
            if not account.exists():
                continue
            is_credit_account = any([account.account_type.startswith(acc_type) for acc_type in ['liability', 'equity', 'income']])
            balance_sign = -1 if is_credit_account else 1
            cols = line.get('columns', [])
            initial = balance_sign * (cols[0].get('no_format', 0.0) - cols[1].get('no_format', 0.0))
            debit = cols[3].get('no_format', 0.0)
            credit = cols[4].get('no_format', 0.0)
            end = balance_sign * (cols[6].get('no_format', 0.0) - cols[7].get('no_format', 0.0))
            pid_match = sat_code.match(line['name'])
            if not pid_match:
                raise UserError(_("Invalid SAT code: %s", line['name']))
            for pid in pid_match.groups():
                parents[pid]['initial'] += initial
                parents[pid]['debit'] += debit
                parents[pid]['credit'] += credit
                parents[pid]['end'] += end
        for pid in sorted(parents.keys()):
            account_lines.append({
                'number': pid,
                'initial': '%.2f' % parents[pid]['initial'],
                'debit': '%.2f' % parents[pid]['debit'],
                'credit': '%.2f' % parents[pid]['credit'],
                'end': '%.2f' % parents[pid]['end'],
            })

        report_date = fields.Date.to_date(sat_options['date']['date_from'])
        return {
            'vat': self.env.company.vat or '',
            'month': str(report_date.month).zfill(2),
            'year': report_date.year,
            'type': 'N',
            'accounts': account_lines,
        }


class AccountReport(models.Model):
    _inherit = "account.report"

    filter_hide_columns = fields.Boolean(
        string="Hide Columns",
        compute=lambda x: x._compute_report_option_filter("filter_hide_columns"),
        readonly=False,
        store=True,
        depends=["root_report_id", "section_main_report_ids"],
    )

    def _init_options_hide_columns(self, options, previous_options=None):
        if previous_options is None:
            previous_options = {}
        previous_section_source_id = previous_options.get("sections_source_id")
        if previous_options and (
            not previous_section_source_id or previous_section_source_id == options["sections_source_id"]
        ):
            options["hide_columns"] = previous_options.get("hide_columns", True)
        else:
            options["hide_columns"] = True

    def export_to_pdf(self, options):
        if not options.get("hide_columns"):
            return super().export_to_pdf(options)
        self.ensure_one()
        action_report = self.env["ir.actions.report"]
        files_stream = []
        for bodies, footer, is_landscape in self._get_html_data_for_pdf_export(options):
            modified_bodies = []
            for body in bodies:
                body = re.sub(
                    r'class="o_overflow_name"\s+colspan="3"', "class='o_overflow_name' colspan='1'", body, count=1
                )
                body = re.sub(
                    r'class="o_overflow_name"\s+colspan="3"', "class='o_overflow_name' colspan='2'", body, count=1
                )
                body = re.sub(
                    r'class="o_overflow_name"\s+colspan="3"', "class='o_overflow_name' colspan='1'", body, count=1
                )
                modified_bodies.append(body)
            files_stream.append(
                io.BytesIO(
                    action_report._run_wkhtmltopdf(
                        modified_bodies,
                        footer=footer.decode() if isinstance(footer, bytes) else footer,
                        landscape=is_landscape or self._context.get("force_landscape_printing"),
                        specific_paperformat_args={
                            "data-report-margin-top": 10,
                            "data-report-header-spacing": 10,
                            "data-report-margin-bottom": 15,
                        },
                    )
                )
            )
        if len(files_stream) > 1:
            result_stream = action_report._merge_pdfs(files_stream)
            result = result_stream.getvalue()
            result_stream.close()
            for file_stream in files_stream:
                file_stream.close()
        else:
            result = files_stream[0].read()

        return {
            "file_name": self.get_default_report_filename(options, "pdf"),
            "file_content": result,
            "file_type": "pdf",
        }
