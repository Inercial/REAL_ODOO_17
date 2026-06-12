from odoo import models, fields

class TrialBalanceCustomHandler(models.AbstractModel):
    _inherit = 'account.trial.balance.report.handler'

    # def _custom_options_initializer(self, report, options, previous_options=None):
    #     super()._custom_options_initializer(report, options, previous_options)
    #     is_compact = previous_options.get('custom_compact_view', False) if previous_options else True
    #     options['custom_compact_view'] = is_compact
    #     options['buttons'].append({'name': 'Vista Compacta', 'sequence': 100, 'action': 'action_toggle_compact_view'})
    #     # if is_compact:
    #     if True:
    #         # Balance inicial: 0 Debe, 1 Haber, 2 Saldo
    #         # Periodo actual: 3 Debe, 4 Haber, 5 Saldo
    #         # Balance final: 6 Debe, 7 Haber, 8 Saldo
    #         keep_column_indices = [2, 3, 4, 8]
    #         options['columns'] = [options['columns'][i] for i in keep_column_indices]
    #         if 'column_headers' in options and len(options['column_headers']) > 0:
    #             main_headers = options['column_headers'][0]
    #             if len(main_headers) >= 3:
    #                 main_headers[0]['colspan'] = 1
    #                 main_headers[1]['colspan'] = 2
    #                 main_headers[2]['colspan'] = 1
    #             if len(options['column_headers']) > 1:
    #                 sub_headers_level = len(options['column_headers']) - 1
    #                 options['column_headers'][sub_headers_level] = [options['column_headers'][sub_headers_level][i] for i in keep_column_indices]

    # def action_toggle_compact_view(self, options):
    #     options['custom_compact_view'] = not options.get('custom_compact_view', False)
    #     return {'type': 'ir.actions.client', 'tag': 'reload'}

# docker run -d --name real_4 --restart unless-stopped -p 0.0.0.0:8282:8069 -p 0.0.0.0:8293:8072 quay.io/jarsa/real:real-17.0-31a193c9e2
# quay.io/jarsa/real:real-17.0-31a193c9e2

class AccountReport(models.Model):
    _inherit = 'account.report'

    filter_hide_columns = fields.Boolean(
        string="Hide Columns",
        compute=lambda x: x._compute_report_option_filter('filter_hide_columns'), readonly=False, store=True, depends=['root_report_id', 'section_main_report_ids'],
    )

    def _init_options_hide_columns(self, options, previous_options=None):
        if previous_options is None:
            previous_options = {}

        print("\n\n-------------------------------Initializing unfolded options-------------------------------")
        print(f"Previous options: {previous_options}")
        print('\n-------------------------------\n')
        print(f"Current options before init: {options}")
        options['hide_columns'] = self.filter_hide_columns and previous_options.get('hide_columns', False)
        previous_section_source_id = previous_options.get('sections_source_id')
        print(f"previous_options['columns']: {previous_options['columns'] if 'columns' in previous_options else 'No columns in previous_options'}")
        print('\n-------------------------------\n')
        print(f"previous_options['column_headers']: {previous_options['column_headers'] if 'column_headers' in previous_options else 'No column headers in previous_options'}")
        print('\n-------------------------------\n')
        print(f"Previous section source ID: {previous_section_source_id}")
        print("-------------------------------Initializing unfolded options-------------------------------\n\n")
        # if previous_options and (not previous_section_source_id or previous_section_source_id == options['sections_source_id']):
        #     # Balance inicial: 0 Debe, 1 Haber, 2 Saldo
        #     # Periodo actual: 3 Debe, 4 Haber, 5 Saldo
        #     # Balance final: 6 Debe, 7 Haber, 8 Saldo
        #     keep_column_indices = [2, 3, 4, 8]
        #     options['columns'] = [options['columns'][i] for i in keep_column_indices]
        #     if 'column_headers' in options and len(options['column_headers']) > 0:
        #         main_headers = options['column_headers'][0]
        #         if len(main_headers) >= 3:
        #             main_headers[0]['colspan'] = 1
        #             main_headers[1]['colspan'] = 2
        #             main_headers[2]['colspan'] = 1
        #         if len(options['column_headers']) > 1:
        #             sub_headers_level = len(options['column_headers']) - 1
        #             options['column_headers'][sub_headers_level] = [options['column_headers'][sub_headers_level][i] for i in keep_column_indices]
        #     options['unfolded_lines'] = previous_options.get('unfolded_lines', [])
        # else:
        #     options['unfolded_lines'] = []


        # if previous_options is None:
        #     previous_options = {}

        # print("\n\n-------------------------------Initializing unfolded options-------------------------------")
        # print(f"Previous options: {previous_options}")
        # print('\n-------------------------------\n')
        # print(f"Current options before init: {options}")
        # print("-------------------------------Initializing unfolded options-------------------------------\n\n")
        # options['hide_columns'] = self.filter_hide_columns and previous_options.get('hide_columns', False)