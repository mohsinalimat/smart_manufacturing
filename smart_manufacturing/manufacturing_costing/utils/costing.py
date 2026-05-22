import frappe
from frappe.utils import flt


def compute_actual_costs(cost_sheet_name):
    cs = frappe.get_doc("SM Cost Sheet", cost_sheet_name)
    wo = frappe.get_doc("Work Order", cs.work_order)

    material = _get_material_cost(wo)
    labor    = _get_labor_cost(wo)
    machine  = _get_machine_cost(wo)
    overhead = _get_overhead_cost(wo, machine, labor)

    cs.act_material_cost = material
    cs.act_labor_cost    = labor
    cs.act_machine_cost  = machine
    cs.act_overhead_cost = overhead
    cs.act_total_cost    = material + labor + machine + overhead

    cs.actual_qty = flt(wo.produced_qty)
    cs.scrap_qty  = flt(wo.scrap_qty)
    cs.good_qty   = cs.actual_qty - cs.scrap_qty

    cs.material_variance = flt(cs.act_material_cost) - flt(cs.std_material_cost) * cs.planned_qty
    cs.labor_variance    = flt(cs.act_labor_cost)    - flt(cs.std_labor_cost)    * cs.planned_qty
    cs.machine_variance  = flt(cs.act_machine_cost)  - flt(cs.std_machine_cost)  * cs.planned_qty
    cs.overhead_variance = flt(cs.act_overhead_cost) - flt(cs.std_overhead_cost) * cs.planned_qty
    cs.total_variance    = cs.material_variance + cs.labor_variance + cs.machine_variance + cs.overhead_variance

    std_total = flt(cs.std_total_cost) * cs.planned_qty
    cs.variance_pct = (cs.total_variance / std_total * 100) if std_total else 0

    cs.save(ignore_permissions=True)
    return cs


def _get_material_cost(wo):
    result = frappe.db.sql("""
        SELECT COALESCE(SUM(sed.amount), 0)
        FROM `tabStock Entry` se
        JOIN `tabStock Entry Detail` sed ON sed.parent = se.name
        WHERE se.work_order = %s AND se.docstatus = 1
          AND se.stock_entry_type = 'Material Transfer for Manufacture'
    """, wo.name)
    return flt(result[0][0]) if result else 0.0


def _get_labor_cost(wo):
    result = frappe.db.sql("""
        SELECT COALESCE(SUM(
            TIMESTAMPDIFF(HOUR, tl.from_time, tl.to_time) *
            COALESCE(e.ctc / (26 * 8), 0)
        ), 0)
        FROM `tabJob Card` jc
        JOIN `tabJob Card Time Log` tl ON tl.parent = jc.name
        LEFT JOIN `tabEmployee` e ON e.name = jc.sm_operator
        WHERE jc.work_order = %s AND jc.docstatus = 1
    """, wo.name)
    return flt(result[0][0]) if result else 0.0


def _get_machine_cost(wo):
    result = frappe.db.sql("""
        SELECT COALESCE(SUM(
            TIMESTAMPDIFF(HOUR, tl.from_time, tl.to_time) *
            COALESCE(mcr.total_rate, ws.hour_rate, 0)
        ), 0)
        FROM `tabJob Card` jc
        JOIN `tabJob Card Time Log` tl ON tl.parent = jc.name
        JOIN `tabWorkstation` ws ON ws.name = jc.workstation
        LEFT JOIN `tabSM Machine Cost Rate` mcr
            ON mcr.workstation = jc.workstation AND mcr.effective_from <= CURDATE()
        WHERE jc.work_order = %s AND jc.docstatus = 1
        ORDER BY mcr.effective_from DESC
        LIMIT 1
    """, wo.name)
    return flt(result[0][0]) if result else 0.0


def _get_overhead_cost(wo, machine_hours_cost, labor_hours_cost):
    overhead_template = frappe.db.get_value("Item", wo.production_item, "sm_industry_type")
    if not overhead_template:
        return machine_hours_cost * 0.15  # default 15% of machine
    return machine_hours_cost * 0.20


def get_production_profitability(work_order):
    cs_name = frappe.db.get_value("Work Order", work_order, "sm_cost_sheet")
    if not cs_name:
        return {}
    cs = frappe.get_doc("SM Cost Sheet", cs_name)
    revenue = frappe.db.sql("""
        SELECT COALESCE(SUM(si.base_net_total), 0)
        FROM `tabSales Invoice` si
        JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        WHERE sii.work_order = %s AND si.docstatus = 1
    """, work_order)
    revenue = flt(revenue[0][0]) if revenue else 0
    return {
        "revenue": revenue,
        "total_cost": cs.act_total_cost,
        "gross_profit": revenue - cs.act_total_cost,
        "gross_margin_pct": ((revenue - cs.act_total_cost) / revenue * 100) if revenue else 0,
    }
