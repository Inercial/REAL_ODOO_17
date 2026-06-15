# report_stock_picking_real — Report Stock Picking Real

> **Version:** 17.0.1.0.4 | **License:** LGPL-3 | **Author:** Jarsa

<!-- ============================================================ -->
<!-- ENGLISH SECTION — Technical Reference                        -->
<!-- ============================================================ -->

## Overview

This module extends the native Odoo `stock.move`, `stock.move.line`, and `stock.picking` models to add computed tonnage fields based on product weight and transferred quantity. It modifies the standard stock picking reports (delivery slip and stock picking report) to include real-world requirements such as tonnage display. A custom decimal precision record (`Tons`) is registered with 6 digits to ensure accuracy in weight-based calculations.

## Dependencies

### Odoo / OCA Modules

- `stock` — Core inventory and stock operations module; provides `stock.picking`, `stock.move`, and `stock.move.line` models that this module extends.
- `stock_barcode` — Barcode scanning module for stock operations; required as the module overrides the kanban view used in barcode workflows (`view_stock_move_line_kanban`).

### Python Libraries

None.

## Installation

1. Place the module in your addons path.
2. Update the module list: **Settings → Activate Developer Mode → Update Apps List**
3. Search for `report_stock_picking_real` and click **Install**.
4. After installation, the `Tons` decimal precision record (6 digits) is automatically created via `data/decimal_precision_data.xml`. No additional manual configuration is required.

## Models Reference

### `stock.move` — Stock Move

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| tons_display | Float (digits="Product Unit of Measure") | Tons | Computed tonnage for the move. Calculated as `quantity * product.weight / 1000`. Uses `quantity` (done qty) if available, otherwise falls back to `product_uom_qty` (demanded qty). Stored and recomputed when `product_id`, `quantity`, or `product_uom_qty` changes. |

**Key methods:**
- `_compute_tons`: Computes `tons_display` by multiplying the effective quantity (done or demanded) by the product's weight and dividing by 1000 to convert grams/units to metric tons.

---

### `stock.move.line` — Stock Move Line

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| tons_display | Float (digits="Product Unit of Measure") | Tons line | Computed tonnage for the move line. Calculated as `quantity * product.weight / 1000`. Stored and recomputed when `product_id` or `quantity` changes. |

**Key methods:**
- `_compute_tons`: Computes `tons_display` using the line's done quantity and the associated product's weight, divided by 1000.

---

### `stock.picking` — Stock Picking (Transfer)

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| tons_display | Float (digits="Product Unit of Measure") | Tons | Computed total tonnage for the entire transfer. Calculated as the sum of `tons_display` across all `move_ids_without_package` (stock moves not in a package). Stored and recomputed when `move_ids_without_package` changes. |

**Key methods:**
- `_compute_tons`: Aggregates `tons_display` from all related stock moves without package to produce the total tonnage of the transfer.

## Security Groups

No new security groups or access control records are defined by this module. It inherits all access rules from the `stock` module.

## Menus & Actions

This module does not define new menu items or actions. It only modifies existing views within the standard Odoo Inventory/Stock interface:

- **Inventory → Operations → Transfers** (form view) — Adds `Tons` column in the operations lines and a `Tons` summary field next to the origin field.
- **Inventory → Operations → Transfers** (list/tree view) — Adds `Tons` and `Note` columns before the `Origin` column.
- **Inventory → Operations → Detailed Operations** (tree view) — Adds `Tons line` column (optional, hidden by default) before the `Quantity` column.
- **Inventory → Operations → Detailed Operations** (kanban view, barcode) — Adds a `Tons` span after the unit of measure field.
- **Stock Move** (kanban view) — Adds a `Tons` span inside the kanban record body (hidden when the move is an inventory adjustment).

## Reports

### Delivery Slip (`report_deliveryslip.xml`)

- **Report Name:** Delivery Slip (modified)
- **Model:** `stock.picking`
- **Trigger:** Standard print action on the Transfer form view
- **Note:** The report template is overridden/redefined via `reports/report_deliveryslip.xml` to incorporate real operational requirements (exact template content adapts the standard Odoo delivery slip).

### Stock Picking Report (`report_stock_picking.xml`)

- **Report Name:** Stock Picking Report (modified)
- **Model:** `stock.picking`
- **Trigger:** Standard print action on the Transfer form view
- **Note:** The report template is overridden/redefined via `reports/report_stock_picking.xml` to include tonnage and other real-world data fields required by the client.

---

<!-- ============================================================ -->
<!-- SECCIÓN EN ESPAÑOL — Documentación Funcional                 -->
<!-- ============================================================ -->

## Descripción General

Este módulo adapta el sistema de transferencias de inventario de Odoo para empresas que necesitan controlar el peso en toneladas métricas de los productos que mueven en sus operaciones logísticas. En industrias como manufactura, distribución de materias primas, productos agrícolas o materiales de construcción, no basta con saber cuántas unidades se transfieren: es fundamental conocer el peso total de cada movimiento.

El módulo agrega automáticamente el campo **Toneladas** a las transferencias de almacén, a los movimientos de inventario individuales y a las líneas de operación detallada. Este cálculo se realiza de forma automática tomando el peso registrado en el producto y multiplicándolo por la cantidad transferida, expresando el resultado en toneladas métricas.

Adicionalmente, el módulo modifica los reportes impresos de transferencia (albarán de entrega y reporte de picking) para que incluyan la información de toneladas, cumpliendo con los requerimientos reales de documentación del cliente.

## Objetivo de Negocio

- Conocer en tiempo real el peso total en toneladas de cada transferencia de almacén, sin cálculos manuales.
- Visualizar las toneladas directamente en las pantallas de operaciones de inventario (listados, formularios y vistas kanban).
- Incluir la información de peso en los documentos impresos de entrega y picking para cumplir con requisitos logísticos y legales.
- Contar con una precisión decimal de 6 dígitos en el cálculo de toneladas, adecuada para productos de bajo peso unitario o grandes volúmenes.
- Facilitar la gestión y supervisión de operaciones de almacén en sectores donde el control de peso es crítico (agro, construcción, manufactura, etc.).

## Flujos de Negocio Principales

### Flujo 1: Registro automático de toneladas en una transferencia

**Descripción:** Cuando un usuario crea o modifica una transferencia de almacén (por ejemplo, una orden de entrega, recepción o movimiento interno), el sistema calcula automáticamente las toneladas correspondientes a cada producto, sin que el usuario tenga que ingresar ningún dato adicional.

**Pasos:**
1. El usuario accede a **Inventario → Operaciones → Transferencias** y abre una transferencia existente o crea una nueva.
2. El usuario agrega o modifica los productos en las líneas de operación (movimientos).
3. El sistema calcula automáticamente el campo **Toneladas** para cada línea de movimiento, usando el peso registrado en la ficha del producto.
4. El sistema calcula también el campo **Toneladas** a nivel de la transferencia completa, sumando las toneladas de todos los movimientos.
5. El usuario puede visualizar las toneladas tanto en la lista de movimientos como en el encabezado del formulario de transferencia.

**Reglas de negocio importantes:**
- Si el producto no tiene registrado su peso en la ficha de producto, el valor de toneladas será 0.
- Si la transferencia ya tiene cantidades realizadas (campo "Done"), el cálculo usa esa cantidad; si no, usa la cantidad demandada.
- El campo de toneladas en la línea de operación detallada usa únicamente la cantidad realizada.
- La precisión decimal del campo está configurada en 6 dígitos para garantizar exactitud.

---

### Flujo 2: Consulta de toneladas en la vista de listado de transferencias

**Descripción:** El supervisor o gerente de almacén puede ver las toneladas de todas las transferencias directamente desde el listado, sin necesidad de abrir cada registro.

**Pasos:**
1. El usuario accede a **Inventario → Operaciones → Transferencias**.
2. En la vista de lista, el sistema muestra las columnas **Toneladas** y **Nota** antes de la columna de origen.
3. El usuario puede ordenar o filtrar transferencias basándose en el peso total.

**Reglas de negocio importantes:**
- El campo se actualiza automáticamente cada vez que cambian los movimientos de la transferencia.
- El valor mostrado es la suma de todas las toneladas de los movimientos sin paquete.

---

### Flujo 3: Visualización de toneladas en operaciones detalladas (modo barcode/kanban)

**Descripción:** Los operadores de almacén que usan la interfaz de escaneo de códigos de barras o la vista kanban pueden ver las toneladas de cada línea de operación directamente en su pantalla.

**Pasos:**
1. El operador inicia una operación de picking o recepción desde la vista kanban o mediante el módulo de código de barras.
2. El sistema muestra las toneladas de cada línea junto a la unidad de medida del producto.
3. El operador puede confirmar la cantidad procesada teniendo visibilidad del peso correspondiente.

**Reglas de negocio importantes:**
- En la vista kanban de movimientos, las toneladas no se muestran cuando el movimiento corresponde a un ajuste de inventario (`is_inventory = True`).
- En la vista de árbol de operaciones detalladas, el campo **Tons line** aparece como columna opcional (oculta por defecto; el usuario puede activarla).

---

### Flujo 4: Impresión de reportes con información de toneladas

**Descripción:** Al imprimir el albarán de entrega o el reporte de picking desde una transferencia, el documento impreso incluye la información de toneladas adaptada a los requerimientos reales del cliente.

**Pasos:**
1. El usuario abre una transferencia en **Inventario → Operaciones → Transferencias**.
2. El usuario hace clic en el botón de impresión y selecciona **Delivery Slip** o **Stock Picking Report**.
3. El sistema genera el documento PDF con el formato modificado por este módulo, incluyendo los datos de toneladas y demás información requerida.

**Reglas de negocio importantes:**
- Los reportes están completamente redefinidos para cumplir con los requerimientos reales del cliente, sustituyendo los reportes estándar de Odoo.

## Guía de Configuración

1. **Instalar el módulo:** Ir a **Configuración → Aplicaciones**, buscar `Report Stock Picking Real` e instalar.
2. **Verificar el peso de los productos:** Es fundamental que cada producto que se mueva en el almacén tenga registrado su peso en la ficha de producto. Ir a **Inventario → Productos → Productos**, abrir cada producto y en la pestaña correspondiente verificar que el campo **Peso** esté correctamente configurado (en las unidades que Odoo maneja, generalmente kilogramos). Si el peso es 0, las toneladas calculadas serán 0.
3. **Verificar la precisión decimal:** El módulo crea automáticamente una precisión decimal llamada **Tons** con 6 dígitos. Para verificarla o modificarla, activar el modo desarrollador y acceder a **Configuración → Técnico → Base de Datos → Precisión Decimal**.
4. **Activar la columna Tons line en operaciones detalladas:** En la vista de operaciones detalladas de una transferencia, hacer clic en el ícono de columnas opcionales (extremo derecho del encabezado de la tabla) y activar la columna **Tons line** si se desea verla por defecto.

> ⚠️ **Advertencia:** Si los productos no tienen peso configurado, todos los valores de toneladas serán 0. Asegúrese de mantener actualizados los pesos en las fichas de producto para que los cálculos sean correctos.

## Campos y Pantallas Clave

### Transferencia (Picking)

| Campo en pantalla | Para qué sirve | Valores posibles / Notas |
|---|---|---|
| Tons | Muestra el total de toneladas de todos los productos incluidos en la transferencia completa. | Número decimal con hasta 6 dígitos. Se calcula automáticamente. Si los productos no tienen peso, muestra 0. |
| Note | Campo de notas de la transferencia, visible en el listado de transferencias. | Texto libre. |

### Movimiento de Stock (Stock Move)

| Campo en pantalla | Para qué sirve | Valores posibles / Notas |
|---|---|---|
| Tons | Muestra las toneladas correspondientes a la línea de movimiento de un producto específico dentro de la transferencia. | Número decimal. Usa la cantidad realizada si existe; de lo contrario usa la cantidad demandada. |

### Línea de Operación Detallada (Stock Move Line)

| Campo en pantalla | Para qué sirve | Valores posibles / Notas |
|---|---|---|
| Tons line | Muestra las toneladas de la línea de operación detallada (nivel de lote/serie). | Número decimal. Usa únicamente la cantidad realizada. Columna opcional en la vista de árbol (oculta por defecto). Siempre visible en el formulario y en la vista kanban. |

## Automatizaciones y Reglas

- **Cálculo de toneladas en movimiento:** Se ejecuta automáticamente cuando cambia el producto, la cantidad realizada o la cantidad demandada en un movimiento de stock. Resultado: actualiza el campo **Tons** del movimiento.
- **Cálculo de toneladas en línea de operación:** Se ejecuta automáticamente cuando cambia el producto o la cantidad realizada en una línea de operación detallada. Resultado: actualiza el campo **Tons line** de la línea.
- **Cálculo de toneladas en transferencia:** Se ejecuta automáticamente cuando cambia cualquier movimiento (sin paquete) de la transferencia. Resultado: actualiza el campo **Tons** de la transferencia sumando todas las toneladas de sus movimientos.

## Reportes Disponibles

### Albarán de Entrega (Delivery Slip)
- **Cómo acceder:** Desde el formulario de una transferencia en **Inventario → Operaciones → Transferencias**, hacer clic en el botón de imprimir y seleccionar **Delivery Slip**.
- **Qué muestra:** Documento de entrega con la información del picking adaptada a los requerimientos reales del cliente, incluyendo datos de toneladas y demás campos operativos requeridos.

### Reporte de Picking (Stock Picking Report)
- **Cómo acceder:** Desde el formulario de una transferencia en **Inventario → Operaciones → Transferencias**, hacer clic en el botón de imprimir y seleccionar el reporte de picking.
- **Qué muestra:** Reporte interno de operaciones de picking con el formato modificado para incluir información de peso y toneladas según los requerimientos del cliente.

## Preguntas Frecuentes (FAQ)

**P: ¿Por qué el campo de Toneladas muestra 0 en mis transferencias?**
R: El valor de toneladas es 0 cuando el producto no tiene registrado su peso en su ficha. Para corregirlo, ve a **Inventario → Productos → Productos**, abre el producto correspondiente y registra su peso en el campo **Peso**. Una vez guardado, las transferencias nuevas calcularán correctamente las toneladas. Las transferencias ya confirmadas actualizarán el valor si se vuelven a guardar o si los movimientos cambian.

**P: ¿Las toneladas se calculan con la cantidad pedida o con la cantidad real entregada?**
R: En los movimientos de stock (**Tons**), el sistema usa la cantidad real entregada (Done) si ya fue registrada. Si aún no hay cantidad realizada, usa la cantidad demandada (a pedir). En las líneas de operación detallada (**Tons line**), siempre se usa la cantidad realizada.

**P: ¿Puedo ver las toneladas en la aplicación de código de barras del almacén?**
R: Sí. La vista kanban de líneas de operación (usada por el módulo de código de barras) muestra las toneladas de cada línea junto a la unidad de medida. También la vista kanban de movimientos muestra las toneladas, excepto cuando el movimiento es un ajuste de inventario.

**P: ¿La columna de Toneladas en operaciones detalladas siempre está visible?**
R: No. En la vista de lista (árbol) de operaciones detalladas, la columna **Tons line** es opcional y aparece oculta por defecto. Puedes activarla haciendo clic en el ícono de columnas opcionales en el extremo derecho del encabezado de la tabla. En el formulario de línea y en la vista kanban, siempre es visible.

**P: ¿Con cuántos decimales se muestran las toneladas?**
R: El módulo configura una precisión decimal llamada **Tons** con 6 dígitos. Sin embargo, el campo usa la precisión de **Product Unit of Measure**, por lo que el número de decimales visible puede depender de la configuración de esa precisión en tu instancia de Odoo. Si necesitas más o menos decimales, puedes ajustar la precisión **Tons** desde **Configuración → Técnico → Base de Datos → Precisión Decimal** (requiere modo desarrollador).

**P: ¿Este módulo modifica los reportes estándar de Odoo o los reemplaza?**
R: Los reportes de albarán de entrega y de picking son redefinidos por este módulo para adaptarlos a los requerimientos reales del cliente. Esto significa que el formato y contenido del reporte impreso puede diferir significativamente del reporte estándar de Odoo.

**P: ¿Funciona el cálculo de toneladas para transferencias con productos en paquetes?**
R: El campo **Tons** de la transferencia se calcula sumando los movimientos que no están en paquete (`move_ids_without_package`). Los movimientos asociados a paquetes no se incluyen en el total de la transferencia, aunque sí tienen su propio campo de toneladas calculado individualmente.

---

<!-- ============================================================ -->
<!-- NOTEBOOKLM TRAINING SECTION                                  -->
<!-- ============================================================ -->

## 🤖 Contexto para Asistente IA

> Esta sección está optimizada para el entrenamiento del asistente de IA del cliente.

**¿Qué hace este módulo en una oración?**
Agrega el cálculo automático de toneladas métricas a las transferencias, movimientos y líneas de operación de inventario en Odoo, y lo muestra en pantalla y en los reportes impresos de picking y entrega.

**Palabras clave asociadas a este módulo:**
toneladas, peso, picking, transferencia, almacén, albarán de entrega, reporte de picking, movimiento de stock, línea de operación, kilogramos, tons, delivery slip, stock picking report, operaciones detalladas, control de peso, logística, inventario

**Casos de uso típicos:**
1. "¿Cómo puedo ver el peso total en toneladas de una transferencia de almacén?"
2. "El campo de toneladas muestra 0, ¿qué debo configurar?"
3. "¿Cómo activo la columna de toneladas en las operaciones detalladas del picking?"
4. "¿El reporte de entrega incluye el peso en toneladas de los productos?"
5. "¿Cómo se calcula el peso en toneladas de un movimiento de inventario?"
6. "¿Puedo ver las toneladas en la app de escaneo de códigos de barras del almacén?"
7. "¿Con cuántos decimales se muestra el campo de toneladas en Odoo?"
8. "¿Las toneladas se calculan con la cantidad pedida o la cantidad entregada?"

**Lo que este módulo NO hace:**
- No permite ingresar manualmente el valor de toneladas; el campo siempre es calculado automáticamente.
- No agrega nuevos menús, grupos de seguridad ni permisos de acceso; utiliza los permisos estándar del módulo de inventario de Odoo.
- No gestiona el peso de productos en paquetes dentro del total de la transferencia (solo suma movimientos sin paquete).
- No convierte entre unidades de medida de peso; asume que el peso del producto en Odoo está registrado en la unidad que, al dividir entre 1000, da toneladas métricas.
<!-- odoo-docs: last-commit=8e71b5dbe6264665fc32329f2b4a2ff809c24057 | updated=2026-05-11 -->
