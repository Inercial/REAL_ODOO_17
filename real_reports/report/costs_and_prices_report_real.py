# Copyright 2021, Jarsa Sistemas
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, fields, models
from odoo.exceptions import UserError


class CostsAndPricesReport(models.Model):
    _name = "costs.and.prices.report"
    _description = "Costs and Prices Report"

    date_start = fields.Date()
    date_end = fields.Date()

    def action_print_report(self):
        if self.date_start > self.date_end:
            raise UserError(_("The start date cannot be greater than the end date."))

        self.env.cr.execute(
            """
            SELECT
                q.x_categoria_padre,
                q.x_categoria_hija,
                SUM(q.x_tons),
                SUM(q.x_litros),
                SUM(q.x_costo_linea),
                SUM(q.x_precio_sin_flete_linea),
                SUM(q.x_flete_linea),
                SUM(q.x_cantidad)
            FROM(
                SELECT DISTINCT ON (aml.id)
                    pc2.name AS x_categoria_padre,
                    pc.name AS x_categoria_hija,
                    CASE
                        WHEN am.move_type = 'out_refund'
                        THEN aml.tons_display * -1
                        ELSE aml.tons_display END AS x_tons,
                    CASE
                        WHEN am.move_type = 'out_refund'
                        THEN round(aml.quantity * coalesce(pp.weight, 0), 2) * -1
                        ELSE round(aml.quantity * coalesce(pp.weight, 0), 2) END AS x_litros,
                    CASE
                        WHEN am.move_type = 'out_refund'
                        THEN coalesce(amlc.credit, 0) * -1
                        ELSE coalesce(amlc.debit, 0) END AS x_costo_linea,
                    CASE
                        WHEN am.move_type = 'out_refund'
                        THEN round(
                            greatest(aml.price_subtotal, abs(aml.credit), abs(aml.debit))
                            - (aml.freight_cost * coalesce(pp.freight_weight, 0)::numeric * aml.quantity),
                            2
                        ) * -1
                        ELSE round(
                            greatest(aml.price_subtotal, abs(aml.credit), abs(aml.debit))
                            - (aml.freight_cost * coalesce(pp.freight_weight, 0)::numeric * aml.quantity),
                            2
                        )
                        END AS x_precio_sin_flete_linea,
                    CASE
                        WHEN am.move_type = 'out_refund'
                        THEN ((aml.freight_cost * coalesce(pp.freight_weight, 0)) * aml.quantity) * -1
                        ELSE (aml.freight_cost * coalesce(pp.freight_weight, 0)) * aml.quantity
                        END AS x_flete_linea,
                    CASE
                        WHEN am.move_type = 'out_refund'
                        THEN aml.quantity * -1
                        ELSE aml.quantity END AS x_cantidad
                FROM
                    account_move_line AS aml
                    LEFT JOIN account_account aa ON aa.id = aml.account_id
                    LEFT JOIN product_product pp ON pp.id = aml.product_id
                    LEFT JOIN product_template AS pt ON pt.id = pp.product_tmpl_id
                    LEFT JOIN product_category AS pc ON pc.id = pt.categ_id
                    LEFT JOIN product_category AS pc2 ON pc2.id = pc.parent_id
                    LEFT JOIN account_move am ON am.id = aml.move_id
                    LEFT JOIN account_move_line AS amlc ON amlc.move_id = aml.move_id
                        AND amlc.product_id = aml.product_id AND amlc.quantity = aml.quantity
                        AND amlc.account_id IN (33, 181, 180, 183)
                WHERE
                    am.state IN ('posted')
                    AND am.move_type IN ('out_invoice', 'out_refund')
                    AND aml.price_subtotal > 0
                    AND aa.account_type IN ('income', 'income_other')
                    AND aml.product_id NOT IN (671, 856)
                    AND aml.account_id IN (32, 172, 171, 173, 441, 442, 174, 175, 176, 177)
                    AND am.invoice_date BETWEEN %s AND %s
                UNION ALL
                SELECT
                    pc2.name AS x_categoria_padre,
                    pc.name AS x_categoria_hija,
                    0 AS x_tons,
                    0 AS x_litros,
                    0 AS x_costo_linea,
                    0 AS x_precio_sin_flete_linea,
                    0 AS x_flete_linea,
                    0 AS x_cantidad
                FROM
                    account_move_line AS aml
                    LEFT JOIN account_move am ON am.id = aml.move_id
                    LEFT JOIN account_account aa ON aa.id = aml.account_id
                    LEFT JOIN product_product pp ON pp.id = aml.product_id
                    LEFT JOIN product_template AS pt ON pt.id = pp.product_tmpl_id
                    LEFT JOIN product_category AS pc ON pc.id = pt.categ_id
                    LEFT JOIN product_category AS pc2 ON pc2.id = pc.parent_id
                WHERE
                    am.state IN ('posted')
                    AND am.move_type IN ('out_invoice', 'out_refund')
                    AND aml.price_subtotal > 0
                    AND aa.account_type IN ('income', 'income_other')
                    AND aml.product_id NOT IN (671, 856)
                    AND aml.account_id IN (32, 172, 171, 173, 441, 442, 174, 175, 176, 177)
                    AND am.invoice_date BETWEEN date_trunc('year', now() - interval '1 year')::date AND CURRENT_DATE
                GROUP BY pc2.name, pc.name
            ) AS q
            GROUP BY
                q.x_categoria_padre,
                q.x_categoria_hija
            """,
            (self.date_start, self.date_end),
        )

        query = {"query": self.env.cr.fetchall(), "date_start": self.date_start, "date_end": self.date_end}
        return self.env.ref("real_reports.costs_and_prices_report_template").report_action(self, data=query)


class TemplateCostsAndPrices(models.AbstractModel):
    _name = "report.real_reports.costs_and_prices_template"
    _description = "Costs and Prices Template"

    def _get_report_values(self, docids, data=None):
        """En la lista llamada “titles” se almacenan los diferentes elementos de
        la columna x_categoria_padre de la consulta de PSQL.
        Las variables:
            sum_cl      |   sum_v    | sum_fl      |   sum_c     |    mp
        Representan la suma de las columnas dentro del reporte, las cuales son:
            COSTO LINEA |   VENTA    | FLETE LINEA |   CANTIDAD  |  % M.P.
        Originalmente el reporte tiene 9 columnas pero solo nos interesan estos 5.
        Se inicializa cada uno en ceros, lo que se veria asi:
            sum_cl      |   sum_v    | sum_fl      |   sum_c     |    mp
            0.0         |   0.0      | 0.0         |   0         |    0.0
        """
        titles = []
        # Estas variables hacen referencia a la sumatoria de las columnas
        sum_ton, sum_lit, sum_cl, sum_v, sum_fl, sum_c, mp = 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0.0

        # Este primer “for” se usa para calcular el valor que se pondrá en las columnas:
        # costo, venta, mp; del reporte, además de ir guardando los valores de “titles”
        for line in data.get("query"):
            # Si la línea 4 y 7 no son 0, entonces se calculan los valores de costo.
            if line[4] and line[7]:
                # "costo" se calcula dividiendo la línea 4 (COSTO) y la línea 7 (CANTIDAD)
                costo = line[4] / line[7]
            else:
                costo = 0

            # Si la línea 5 y 7 no son 0, entonces se calculan los valores de venta.
            if line[5] and line[7]:
                # "venta" se calcula dividiendo la línea 5 (VENTA) y la línea 7 (CANTIDAD)
                venta = line[5] / line[7]
            else:
                venta = 0

            # Si "costo" y "venta" no son 0, entonces se calculan los valores de mp.
            if costo and venta:
                # "mp" se calcula dividiendo "costo" y "venta" y multiplicando por 100 para sacar un porcentaje
                mp = (costo / venta) * 100
            else:
                mp = 0

            # Para acabar, agregamos los resultados a “line”
            line.extend([costo, venta, mp])
            # Agregamos los elementos de la columna x_categoria_padre a la lista "titles" para usarla en el reporte.
            if line[0] not in titles:
                titles.append(line[0])

        # Este segundo "for" se usa para agregar las líneas "TOTAL" al reporte.
        # Se resetean los valores de las variables:
        sum_ton, sum_lit, sum_cl, sum_v, sum_fl, sum_c, mp = 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0.0

        # Se recorren los valores de la lista “titles” para compararlos en un “for” anidado que recorre la consulta
        for title in titles:
            # Se crea la variable pos (POSICIÓN) para guardar la posición del último elemento de la consulta original
            pos = 0

            for last_pos, line in enumerate(data.get("query")):
                # Se compara line[0] que es igual a x_categoria_padre de la consulta con el valor de title, siempre
                # que sean iguales se van a sumar los valores de sum_ton, sum_lit, sum_cl, sum_v, sum_fl, sum_c y
                # se va a guardar la posición del último elemento
                if line[0] == title:
                    sum_ton += line[2]
                    sum_lit += line[3]
                    sum_cl += line[4]
                    sum_v += line[5]
                    sum_fl += line[6]
                    sum_c += line[7]
                    pos = last_pos

            # Se calcula el valor de "mp" en caso de que sum_cl, sum_v y sum_c no sean 0.
            # En caso contrario, se pone 0.
            # En caso de que no sean 0, se deja el valor original de mp que es 0.0
            if sum_cl and sum_v and sum_c:
                # "mp" se calcula dividiendo "sum_cl" y "sum_v" y multiplicando por 100 para sacar un porcentaje
                mp = ((sum_cl / sum_c) / (sum_v / sum_c)) * 100

            # Se agrega la línea "TOTAL" al reporte, con los valores de sum_cl, sum_v, sum_fl, sum_c y mp.
            data.get("query").insert(pos + 1, [title, "TOTAL", sum_ton, sum_lit, sum_cl, sum_v, sum_fl, sum_c, mp])
            # Se reinician los valores de las variables para poder hacer el cálculo de la siguiente línea.
            sum_ton, sum_lit, sum_cl, sum_v, sum_fl, sum_c, mp = 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0.0

        return {
            "lines": data.get("query"),
            "date_start": data.get("date_start"),
            "date_end": data.get("date_end"),
            "titles": titles,
        }
