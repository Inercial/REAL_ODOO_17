# report_sale_order_real — Report Sale Order Real

> **Version:** 17.0.1.0.0 | **License:** LGPL-3 | **Author:** Jarsa

<!-- ============================================================ -->
<!-- ENGLISH SECTION — Technical Reference                        -->
<!-- ============================================================ -->

## Overview

`report_sale_order_real` is an Odoo 17 module that extends the native `sale.order` and `sale.order.line` models to add weight-based tonnage computation fields at both the order line and order header levels. It modifies the standard Sale Order form view to expose these tonnage fields and overrides/extends the standard sale order PDF reports (quotation and order confirmation) with custom QWeb templates adapted to real business requirements.

## Dependencies

### Odoo / OCA Modules

- `sale_management` — Provides the core `sale.order` and `sale.order.line` models that this module extends.
- `report_stock_picking_real` — Custom report module (likely from the same Jarsa ecosystem) providing shared report assets or stock picking report layouts reused in the sale order reports.
- `sale_pdf_quote_builder` — Odoo native module enabling PDF quote building; this module overrides/extends its report templates.

### Python Libraries

None.

## Installation

1. Place the module in your addons path.
2. Update the module list: **Settings → Activate Developer Mode → Update Apps List**
3. Search for `report_sale_order_real` and click **Install**.
4. No additional post-install configuration is required; fields and reports are available immediately after installation.

## Models Reference

### `sale.order` — Sale Order

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| `total_tons_display` | `Float` (digits: Product Unit of Measure) | Tons | Computed, stored field. Aggregates the `tons_display` value from all order lines to provide the total weight in metric tons for the entire order. Depends on `order_line`. |

**Key methods:**
- `_compute_total_tons`: Iterates over all records and sums `tons_display` from each line in `order_line`, storing the result in `total_tons_display`.

---

### `sale.order.line` — Sale Order Line

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| `tons_display` | `Float` (digits: Product Unit of Measure) | Tons | Computed, stored field. Calculates the weight in metric tons for the line as `(product_uom_qty × product.weight) / 1000`. Returns 0 if no product is set. Depends on `product_uom_qty` and `product_id`. |

**Key methods:**
- `_compute_tons`: For each order line, multiplies the ordered quantity by the product's weight (in grams/units as stored in Odoo) and divides by 1000 to convert to metric tons. Returns 0 if `product_id` is not set.

## Security Groups

No new security groups or access control rules are defined by this module. Access to the extended fields follows the existing permissions of `sale.order` and `sale.order.line` from `sale_management`.

## Menus & Actions

No new menu items or window actions are introduced by this module. All functionality is embedded within the existing **Sales → Orders → Quotations** and **Sales → Orders → Orders** views inherited from `sale_management`.

## Reports

The following QWeb reports are defined or overridden by this module:

| Report Name | Model | Trigger |
|---|---|---|
| Report Sale Order (base template) | `sale.order` | Defined in `reports/report_sale_order.xml` — base layout/template reused by quotation and order reports |
| Sale Order Quotation | `sale.order` | Defined in `reports/report_sale_order_quotation.xml` — triggered from the Quotation form (Print button) |
| Sale Order Confirmation | `sale.order` | Defined in `reports/report_sale_order_order.xml` — triggered from the Sale Order form (Print button) |
| Sale Order Reports (actions) | `sale.order` | Defined in `reports/sale_order_reports.xml` — registers report actions in Odoo's reporting framework |

---

<!-- ============================================================ -->
<!-- SECCIÓN EN ESPAÑOL — Documentación Funcional                 -->
<!-- ============================================================ -->

## Descripción General

Este módulo extiende las órdenes de venta de Odoo para incorporar el cálculo automático del **peso en toneladas métricas** tanto a nivel de cada línea de producto como a nivel del total de la orden. Esta información es esencial para empresas que comercializan productos industriales, materias primas, materiales de construcción u otros bienes donde el peso total del pedido es un dato crítico para la operación logística, comercial o de transporte.

Adicionalmente, el módulo reemplaza los reportes PDF estándar de cotizaciones y órdenes de venta de Odoo con plantillas personalizadas que incorporan estos datos de tonelaje y se adaptan a los requerimientos reales del negocio del cliente. De esta forma, los documentos que se envían a los clientes reflejan fielmente la información relevante para la operación.

La solución está diseñada para integrarse de forma transparente con el flujo de ventas existente en Odoo, sin requerir configuraciones adicionales complejas.

## Objetivo de Negocio

- Calcular automáticamente el peso en toneladas de cada línea de una cotización u orden de venta, basándose en el peso unitario del producto y la cantidad solicitada.
- Mostrar el total de toneladas de toda la orden en un campo visible en la pantalla de ventas, facilitando la toma de decisiones logísticas desde el área comercial.
- Generar documentos PDF (cotizaciones y confirmaciones de pedido) que incluyan información de tonelaje adaptada a los requisitos reales del cliente.
- Evitar cálculos manuales de peso por parte del equipo de ventas, reduciendo errores y ahorrando tiempo en la elaboración de cotizaciones.
- Proveer información de peso consolidada en el pedido para apoyar la planeación de transporte y despacho.

## Flujos de Negocio Principales

### Flujo 1: Creación de Cotización con Cálculo Automático de Toneladas

**Descripción:** Cuando un vendedor agrega líneas de productos a una cotización, el sistema calcula automáticamente el peso en toneladas de cada línea y el total del pedido, sin intervención manual del usuario.

**Pasos:**
1. El vendedor accede a **Ventas → Pedidos → Presupuestos** y crea una nueva cotización.
2. Agrega una o más líneas de producto con su respectiva cantidad.
3. El sistema calcula automáticamente el campo **Tons** en cada línea, usando la fórmula: `Cantidad × Peso del producto / 1000`.
4. El campo **Total Tons** en el encabezado de la orden se actualiza con la suma de todas las líneas.
5. El vendedor puede visualizar el campo **Tons** en la vista de árbol (columna opcional), en el formulario de la línea y en la vista kanban.
6. Al imprimir o enviar la cotización en PDF, el documento incluye la información de tonelaje según la plantilla personalizada.

**Reglas de negocio importantes:**
- Si una línea de producto no tiene un producto seleccionado, el valor de toneladas para esa línea será **0**.
- El peso utilizado para el cálculo proviene del campo **Peso** del producto en el catálogo de productos de Odoo (campo `product.weight`), expresado en la unidad de medida configurada.
- La división entre 1000 asume que el peso del producto está registrado en gramos o kilogramos para convertir a toneladas métricas.
- Los campos de toneladas se almacenan en base de datos (`store=True`), por lo que están disponibles para filtros, agrupaciones y reportes.

---

### Flujo 2: Impresión de Reportes Personalizados

**Descripción:** Cuando el usuario solicita imprimir o descargar el PDF de una cotización o una orden de venta confirmada, el sistema genera el documento usando las plantillas personalizadas de este módulo en lugar de las plantillas estándar de Odoo.

**Pasos:**
1. El usuario abre una cotización (estado Presupuesto) o una orden de venta confirmada.
2. Hace clic en el botón **Imprimir** y selecciona la opción correspondiente (cotización o pedido).
3. El sistema utiliza las plantillas QWeb definidas en `reports/report_sale_order_quotation.xml` o `reports/report_sale_order_order.xml`.
4. Se genera el PDF con el formato adaptado a los requerimientos reales del negocio.
5. El usuario puede descargar el PDF o enviarlo directamente al cliente por correo electrónico.

**Reglas de negocio importantes:**
- Las plantillas de reporte reemplazan o extienden las plantillas estándar de `sale_pdf_quote_builder`.
- El módulo depende de `report_stock_picking_real` para componentes visuales o de diseño compartidos.

## Guía de Configuración

1. **Verificar el peso de los productos:** Para que el cálculo de toneladas funcione correctamente, cada producto vendible debe tener configurado su peso en **Inventario → Productos → [Producto] → pestaña General → Peso**. Si el peso no está configurado, el campo de toneladas mostrará 0.
2. **Unidad de medida del peso:** Confirmar que la unidad de medida de peso en Odoo esté configurada de forma consistente (kilogramos recomendado) para que la conversión a toneladas sea correcta.
3. **Columna Tons en listado:** En la vista de lista de líneas de la orden de venta, el campo **Tons** aparece como columna **opcional** (oculta por defecto). Para activarla, el usuario puede hacer clic en el ícono de configuración de columnas en la cabecera de la tabla.
4. **Activar modo desarrollador** solo si se necesita ajustar las plantillas de reporte desde **Configuración → Reportes técnicos**.

> ⚠️ **Advertencia:** Si el campo `weight` de un producto no está configurado en el catálogo, el cálculo de toneladas retornará 0 para todas las líneas que contengan ese producto.

## Campos y Pantallas Clave

### Orden de Venta

| Campo en pantalla | Para qué sirve | Valores posibles / Notas |
|---|---|---|
| Total Tons | Muestra el total de toneladas métricas de todos los productos incluidos en la orden, calculado automáticamente. | Número decimal. Se muestra en el encabezado de la orden, justo antes del resumen de impuestos. Se actualiza automáticamente al modificar las líneas. |

### Línea de Orden de Venta

| Campo en pantalla | Para qué sirve | Valores posibles / Notas |
|---|---|---|
| Tons | Muestra el peso en toneladas métricas de la cantidad indicada en esa línea de producto. | Número decimal. Calculado como `Cantidad × Peso del producto / 1000`. Es 0 si no hay producto seleccionado. Visible en lista (columna opcional), formulario de línea y vista kanban. |

## Automatizaciones y Reglas

- **Cálculo de Tons por línea:** Se ejecuta automáticamente cada vez que cambia la **cantidad ordenada** (`product_uom_qty`) o el **producto** (`product_id`) en una línea de venta. Resultado: actualiza el campo **Tons** de esa línea con el peso en toneladas métricas.
- **Cálculo de Total Tons:** Se ejecuta automáticamente cada vez que se modifica cualquier línea de la orden (`order_line`). Resultado: actualiza el campo **Total Tons** en el encabezado de la orden con la suma de los campos **Tons** de todas las líneas.

## Reportes Disponibles

### Cotización (Presupuesto)
- **Acceso:** Desde la pantalla de una cotización → botón **Imprimir → Presupuesto**
- **Contenido:** Documento PDF con el detalle de productos, cantidades, precios y, con este módulo, información de tonelaje. Diseño adaptado a los requerimientos reales del cliente.

### Orden de Venta (Confirmación de Pedido)
- **Acceso:** Desde la pantalla de una orden de venta confirmada → botón **Imprimir → Orden de Venta**
- **Contenido:** Documento PDF con la confirmación del pedido, incluyendo el detalle completo con tonelaje. Diseño adaptado a los requerimientos reales del cliente.

## Preguntas Frecuentes (FAQ)

**P: ¿Por qué el campo Tons muestra 0 en algunas líneas de mi cotización?**
R: Esto ocurre porque el producto en esa línea no tiene configurado su peso en el catálogo. Para corregirlo, ve a **Inventario → Productos**, abre el producto correspondiente, y en la pestaña **General** (o **Información general**) ingresa el valor de peso. Una vez guardado, recalcula la cotización modificando la cantidad.

**P: ¿En qué unidad se muestra el campo Tons?**
R: El campo muestra el valor en toneladas métricas (1 tonelada = 1,000 kg). El cálculo divide el resultado de `Cantidad × Peso del producto` entre 1,000, por lo que el peso del producto debe estar registrado en kilogramos para que el resultado sea correcto.

**P: ¿Puedo ver el campo Tons en la lista de líneas de la cotización?**
R: Sí, pero la columna está oculta por defecto. Para activarla, en la vista de lista de las líneas de la orden de venta, haz clic en el ícono de opciones de columnas (generalmente un ícono de engranaje o ajuste en la cabecera de la tabla) y activa la columna **Tons**.

**P: ¿El Total de Toneladas se actualiza automáticamente cuando agrego o elimino líneas?**
R: Sí. El campo **Total Tons** en el encabezado de la orden se recalcula automáticamente cada vez que se agrega, elimina o modifica cualquier línea de la cotización u orden de venta.

**P: ¿Los reportes PDF de cotización y orden de venta cambian con este módulo?**
R: Sí. Este módulo reemplaza las plantillas estándar de reporte de Odoo con plantillas personalizadas adaptadas a los requerimientos reales del negocio. Si necesitas volver a la plantilla estándar, sería necesario desinstalar el módulo.

**P: ¿Este módulo afecta el funcionamiento normal de las ventas?**
R: No. El módulo solo agrega campos calculados de tonelaje y personaliza los reportes PDF. No modifica ningún flujo de ventas, estados, validaciones de negocio originales ni precios.

**P: ¿Puedo filtrar o agrupar cotizaciones por Total de Toneladas?**
R: Sí. Dado que el campo **Total Tons** se almacena en la base de datos (`store=True`), es posible usarlo en filtros personalizados y agrupaciones desde la vista de lista de órdenes de venta en Odoo.

---

<!-- ============================================================ -->
<!-- NOTEBOOKLM TRAINING SECTION                                  -->
<!-- ============================================================ -->

## 🤖 Contexto para Asistente IA

> Esta sección está optimizada para el entrenamiento del asistente de IA del cliente.

**¿Qué hace este módulo en una oración?**
Calcula automáticamente el peso en toneladas métricas de cada línea y del total de las órdenes de venta, y personaliza los reportes PDF de cotizaciones y pedidos para incluir esa información.

**Palabras clave asociadas a este módulo:**
- Toneladas
- Tons
- Total Tons
- Peso en cotización
- Tonelaje pedido
- Reporte cotización personalizado
- Reporte orden de venta
- Peso producto venta
- Presupuesto con toneladas
- Cálculo de peso línea
- Orden de venta tonelaje
- PDF cotización personalizado
- Cantidad por peso
- Toneladas métricas venta
- Reporte sale order

**Casos de uso típicos:**
1. "¿Cómo puedo ver el total de toneladas de mi cotización?"
2. "El campo de toneladas me aparece en 0, ¿qué debo configurar?"
3. "¿Por qué el PDF de mi cotización tiene un formato diferente al estándar de Odoo?"
4. "Necesito saber cuántas toneladas incluye este pedido para coordinar el transporte."
5. "¿Cómo activo la columna de toneladas en el listado de líneas de la orden de venta?"
6. "¿El peso de toneladas se calcula solo o tengo que ingresarlo manualmente?"
7. "¿Puedo imprimir la orden de venta con el peso total incluido?"
8. "¿Dónde configuro el peso del producto para que aparezca en la cotización?"

**Lo que este módulo NO hace:**
- No modifica precios, descuentos ni condiciones comerciales de las órdenes de venta.
- No gestiona rutas logísticas, transportistas ni planificación de envíos; solo calcula y muestra el peso en toneladas.
- No crea nuevos menús ni secciones de configuración propias en Odoo.
- No afecta los reportes de albaranes (picking) ni otros documentos distintos a la cotización y la orden de venta.
<!-- odoo-docs: last-commit=8e71b5dbe6264665fc32329f2b4a2ff809c24057 | updated=2026-05-11 -->
