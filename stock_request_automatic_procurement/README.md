# stock_request_automatic_procurement — Stock Request Automatic Procurement

> **Version:** 17.0.1.0.0 | **License:** LGPL-3 | **Author:** Jarsa

<!-- ============================================================ -->
<!-- ENGLISH SECTION — Technical Reference                        -->
<!-- ============================================================ -->

## Overview

This module extends the `stock.request.order` model from the `stock_request` OCA module to automatically create a `procurement.group` record every time a new Stock Request Order is created. The procurement group is named after the stock request order and is automatically assigned to both the order and all its associated stock request lines. This ensures that all movements derived from a stock request order are correctly grouped under a single procurement group, enabling proper traceability of supply chain operations.

## Dependencies

### Odoo / OCA Modules

- `stock_request` — Base OCA module that provides the `stock.request.order` and `stock.request` models which this module extends.

### Python Libraries

None.

## Installation

1. Place the module in your addons path.
2. Update the module list: **Settings → Activate Developer Mode → Update Apps List**
3. Search for `stock_request_automatic_procurement` and click **Install**.
4. No additional post-install configuration is required. The automatic procurement group creation is active immediately upon installation.

## Models Reference

### `stock.request.order` — Stock Request Order

This model inherits from the OCA `stock.request.order` model. No new fields are added. The module only overrides the `create` method.

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| *(No new fields added)* | — | — | All fields belong to the parent `stock_request` module. |

**Key methods:**
- `create(vals_list)`: Overrides the standard multi-record create method. For each record being created, it generates the next sequence value for `stock.request.order` if no name is set, creates a new `procurement.group` with that name, assigns the `procurement_group_id` to the order, and propagates the same `procurement_group_id` to every stock request line (`stock_request_ids`) included in the same create call.

## Security Groups

No new security groups, access control rules, or record rules are defined by this module. Security is fully inherited from the `stock_request` dependency.

## Menus & Actions

No new menus or actions are defined by this module. All UI elements are inherited from the `stock_request` dependency.

---

<!-- ============================================================ -->
<!-- SECCIÓN EN ESPAÑOL — Documentación Funcional                 -->
<!-- ============================================================ -->

## Descripción General

Este módulo resuelve un problema común en la gestión de solicitudes de stock dentro de Odoo: cuando se crea una Orden de Solicitud de Stock, no siempre se genera automáticamente un grupo de aprovisionamiento (procurement group) que permita rastrear de forma unificada todos los movimientos relacionados con esa solicitud.

Con este módulo instalado, cada vez que un usuario crea una nueva Orden de Solicitud de Stock, el sistema genera de forma transparente y automática un grupo de aprovisionamiento con el mismo nombre que la orden. Este grupo se asigna tanto a la orden principal como a todas las líneas de solicitud de stock incluidas en ella.

Esto permite que el área de logística y almacén pueda identificar fácilmente qué movimientos de inventario, órdenes de compra o transferencias internas están vinculadas a una solicitud de stock específica, mejorando la trazabilidad y el control del proceso de abastecimiento.

El módulo es completamente transparente para el usuario: no agrega pantallas, botones ni configuraciones adicionales. Funciona de manera silenciosa en segundo plano desde el momento en que se instala.

## Objetivo de Negocio

- Garantizar que cada Orden de Solicitud de Stock tenga siempre asociado un grupo de aprovisionamiento único desde el momento de su creación.
- Mejorar la trazabilidad de los movimientos de inventario vinculados a solicitudes de stock.
- Evitar que líneas de solicitud de stock queden desvinculadas del grupo de aprovisionamiento de su orden padre.
- Reducir la intervención manual del usuario en la configuración de grupos de aprovisionamiento.
- Asegurar la coherencia de datos entre la solicitud de stock y los procesos de abastecimiento generados a partir de ella.

## Flujos de Negocio Principales

### Flujo 1: Creación automática de grupo de aprovisionamiento al registrar una Orden de Solicitud de Stock

**Descripción:** Este flujo se desencadena cada vez que un usuario guarda una nueva Orden de Solicitud de Stock en Odoo. El resultado es que el sistema crea automáticamente un grupo de aprovisionamiento y lo vincula tanto a la orden como a todas sus líneas de solicitud, sin que el usuario deba realizar ninguna acción adicional.

**Pasos:**
1. El usuario navega al módulo de Solicitudes de Stock y crea una nueva Orden de Solicitud de Stock.
2. El usuario completa los campos requeridos (producto, cantidad, ubicación, etc.) y agrega las líneas de solicitud correspondientes.
3. El usuario guarda el registro haciendo clic en **Guardar** (o el sistema lo guarda automáticamente).
4. En ese momento, el sistema genera automáticamente el siguiente número de secuencia para la orden (si no tiene nombre asignado) y crea un nuevo **Grupo de Aprovisionamiento** con ese nombre.
5. El grupo de aprovisionamiento se asigna automáticamente a la Orden de Solicitud de Stock y a cada una de sus líneas de solicitud incluidas en la misma operación de creación.

**Reglas de negocio importantes:**
- Si la orden no tiene un nombre asignado al momento de su creación (valor `/`), el sistema obtiene automáticamente el siguiente valor de la secuencia `stock.request.order`.
- El grupo de aprovisionamiento se crea con el mismo nombre que la orden, facilitando su identificación.
- La asignación del grupo se propaga a todas las líneas de solicitud de stock (`stock_request_ids`) que se creen junto con la orden en la misma transacción.
- Este comportamiento es automático e invisible para el usuario; no requiere confirmación ni acción adicional.

## Guía de Configuración

Este módulo no requiere configuración adicional después de su instalación. Una vez instalado, el comportamiento de creación automática de grupos de aprovisionamiento está activo de forma inmediata para todas las nuevas Órdenes de Solicitud de Stock.

**Pasos post-instalación:**
1. Instalar el módulo desde **Aplicaciones → Buscar `stock_request_automatic_procurement` → Instalar**.
2. Verificar que el módulo base `stock_request` esté instalado previamente.
3. Crear una nueva Orden de Solicitud de Stock y confirmar que el campo **Grupo de Aprovisionamiento** se llena automáticamente al guardar.

> ⚠️ **Advertencia:** Este módulo solo aplica su lógica a registros creados **después** de su instalación. Las Órdenes de Solicitud de Stock existentes que no tengan grupo de aprovisionamiento asignado no serán modificadas retroactivamente.

## Campos y Pantallas Clave

### Orden de Solicitud de Stock

Este módulo no agrega campos nuevos a la pantalla. Opera sobre campos existentes del módulo base `stock_request`. Los campos relevantes afectados por la lógica de este módulo son:

| Campo en pantalla | Para qué sirve | Valores posibles / Notas |
|---|---|---|
| Nombre / Referencia | Identificador único de la Orden de Solicitud de Stock | Se genera automáticamente usando la secuencia `stock.request.order` si no se especifica manualmente al crear el registro |
| Grupo de Aprovisionamiento | Agrupa todos los movimientos y operaciones de abastecimiento relacionados con esta orden | Se crea y asigna automáticamente al guardar la orden; el nombre del grupo coincide con el nombre de la orden |

## Automatizaciones y Reglas

- **Creación automática de Grupo de Aprovisionamiento:** Se ejecuta cuando se crea una nueva Orden de Solicitud de Stock. Resultado: se genera un nuevo `procurement.group` con el nombre de la orden y se asigna automáticamente a la orden y a todas sus líneas de solicitud de stock creadas en la misma transacción.

## Preguntas Frecuentes (FAQ)

**P: ¿Necesito hacer algo especial después de instalar este módulo para que funcione?**
R: No. Una vez instalado, el módulo funciona de forma completamente automática. Cada nueva Orden de Solicitud de Stock que se cree tendrá su grupo de aprovisionamiento asignado sin necesidad de ninguna acción por parte del usuario.

**P: ¿Qué pasa con las Órdenes de Solicitud de Stock que ya existían antes de instalar el módulo?**
R: Las órdenes existentes no se ven afectadas. El módulo solo aplica la creación automática del grupo de aprovisionamiento a los registros nuevos creados después de la instalación. Si necesita asignar grupos a órdenes existentes, deberá hacerlo de forma manual.

**P: ¿Por qué es importante que la solicitud de stock tenga un grupo de aprovisionamiento?**
R: El grupo de aprovisionamiento permite que Odoo agrupe y rastree todos los movimientos de inventario, transferencias y órdenes de compra que se generen a partir de una misma solicitud. Sin este grupo, sería difícil identificar qué operaciones están relacionadas entre sí.

**P: ¿El nombre del grupo de aprovisionamiento creado automáticamente se puede cambiar?**
R: El grupo de aprovisionamiento se crea con el mismo nombre que la Orden de Solicitud de Stock. Si bien técnicamente es posible modificarlo desde la configuración de inventario, no se recomienda hacerlo ya que puede dificultar la trazabilidad.

**P: ¿Este módulo afecta el rendimiento del sistema al crear muchas solicitudes de stock simultáneamente?**
R: El módulo fue desarrollado usando el método `create` con soporte para múltiples registros (`model_create_multi`), lo que significa que está optimizado para la creación masiva de registros y no debería representar un impacto significativo en el rendimiento.

**P: ¿Este módulo es compatible con otras personalizaciones del modelo `stock.request.order`?**
R: El módulo hereda correctamente el modelo usando `_inherit` y llama al método `super().create()`, por lo que es compatible con otras extensiones del mismo modelo, siempre que estas también respeten la cadena de herencia de Odoo.

**P: ¿Qué sucede si creo una solicitud de stock sin líneas de solicitud?**
R: El módulo crea el grupo de aprovisionamiento y lo asigna a la orden sin importar si hay líneas o no. Si se agregan líneas posteriormente (en una operación de escritura separada), estas no recibirán automáticamente el grupo de aprovisionamiento a través de este módulo, ya que la lógica solo aplica durante la creación del registro.

---

<!-- ============================================================ -->
<!-- NOTEBOOKLM TRAINING SECTION                                  -->
<!-- ============================================================ -->

## 🤖 Contexto para Asistente IA

> Esta sección está optimizada para el entrenamiento del asistente de IA del cliente.

**¿Qué hace este módulo en una oración?**
Crea automáticamente un grupo de aprovisionamiento y lo asigna a cada nueva Orden de Solicitud de Stock y sus líneas al momento de guardarla.

**Palabras clave asociadas a este módulo:**
- Solicitud de stock
- Orden de solicitud de stock
- Grupo de aprovisionamiento
- Procurement group
- Trazabilidad de inventario
- Abastecimiento automático
- Stock request order
- Movimientos de inventario agrupados
- Secuencia de solicitud
- Automatización de almacén
- Aprovisionamiento
- Stock request
- Jarsa
- Módulo OCA stock

**Casos de uso típicos:**
1. "¿Por qué la solicitud de stock ya tiene un grupo de aprovisionamiento cuando la acabo de crear?"
2. "¿Cómo puedo saber qué movimientos de inventario están relacionados con una solicitud de stock específica?"
3. "¿Necesito asignar manualmente el grupo de aprovisionamiento a mis solicitudes de stock?"
4. "Creé una solicitud de stock y el campo de grupo de aprovisionamiento se llenó solo, ¿es normal?"
5. "¿Qué módulo controla la creación automática del grupo de aprovisionamiento en las solicitudes de stock?"
6. "¿Las solicitudes de stock antiguas también tienen grupo de aprovisionamiento automático?"
7. "¿Puedo desactivar la creación automática del grupo de aprovisionamiento para ciertas solicitudes?"

**Lo que este módulo NO hace:**
- No agrega nuevos campos, menús ni vistas a la interfaz de usuario de Odoo.
- No modifica ni asigna grupos de aprovisionamiento a Órdenes de Solicitud de Stock ya existentes antes de su instalación.
- No gestiona el proceso de aprovisionamiento en sí (compras, transferencias, etc.); únicamente crea y asigna el grupo de agrupación.
- No aplica su lógica a líneas de solicitud de stock que se agreguen a una orden ya existente en operaciones de edición posteriores a la creación.
<!-- odoo-docs: last-commit=8e71b5dbe6264665fc32329f2b4a2ff809c24057 | updated=2026-05-11 -->
