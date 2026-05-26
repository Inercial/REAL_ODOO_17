from odoo import api, models, fields
from datetime import datetime
from zoneinfo import ZoneInfo


class PhysicalInventoryCountMP(models.TransientModel):
    _name = "physical.inventory.count.mp"

    category_id = fields.Many2one(
            'product.category',
            string='Seleccionar Categoría',
            domain=[
                ('is_mp_category', '=', True),
                ('parent_id', '!=', False),
                '|', '|',
                ('parent_path', '=ilike', '5/%'),
                ('parent_path', '=ilike', '4/%'),
                ('parent_path', '=ilike', '110/%')
            ]
        )

    def action_print_report(self):
        complete_name = self.category_id.complete_name
        self.env.cr.execute("""
SELECT
    trim(pt.name ->> 'es_MX' || ' ' || COALESCE(pav.name ->> 'es_MX', '')) AS product_name
FROM
    product_product AS pp
    INNER JOIN product_template AS pt ON pt.id = pp.product_tmpl_id
    INNER JOIN product_category AS pc ON pc.id = pt.categ_id
    LEFT JOIN (
        SELECT product_id, SUM(quantity) AS total_qty
        FROM stock_quant
        WHERE location_id IN (8, 19, 11)
        GROUP BY product_id
    ) AS sq_sum ON sq_sum.product_id = pp.id
    LEFT JOIN product_variant_combination AS pvc ON pvc.product_product_id = pp.id
    LEFT JOIN product_template_attribute_value AS ptav ON ptav.id = pvc.product_template_attribute_value_id
    LEFT JOIN product_attribute_value AS pav ON pav.id = ptav.product_attribute_value_id
WHERE
    pt.type = 'product'
    AND pp.active = true
    AND pc.complete_name ILIKE %(complete_name)s
ORDER BY
    product_name
        """, {"complete_name": complete_name},)
        lines = {'docs': self.env.cr.dictfetchall(), 'category_name': complete_name}
        return self.env.ref("real_reports.action_physical_inventory_count_mp")\
            .report_action(self, data=lines)


class ReportPhysicalInventoryMP(models.AbstractModel):
    _name = 'report.real_reports.report_physical_inventory_count_mp'

    @api.model
    def _get_report_values(self, docids, data):
        return {
            'docs': data['docs'],
            'category_name': data['category_name'],
            'logo': self.env.company.logo,
            'print_date': datetime.now(ZoneInfo("America/Mexico_City")).strftime('%Y-%m-%d %H:%M:%S')
        }
