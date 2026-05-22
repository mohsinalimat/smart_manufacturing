frappe.pages["shop_floor-terminal"].on_page_load = function(wrapper) {
    frappe.ui.make_app_page({
        parent: wrapper,
        title: __("Shop Floor Terminal"),
        single_column: false,
    });

    const page = wrapper.page;

    page.set_primary_action(__("Refresh"), () => terminal.refresh(), "refresh");
    page.add_action_item(__("Log Downtime"), () => terminal.log_downtime_dialog());

    const terminal = new SmShopFloorTerminal(wrapper);
    terminal.init();
};

class SmShopFloorTerminal {
    constructor(wrapper) {
        this.wrapper = wrapper;
        this.workstation = null;
        this.operator = frappe.session.user;
        this.$main = $(wrapper).find(".page-content");
    }

    init() {
        this._render_controls();
        this.refresh();
    }

    _render_controls() {
        const html = `
        <div class="sm-terminal-header" style="padding:15px 0; display:flex; gap:12px; align-items:center; flex-wrap:wrap;">
            <div class="sm-ws-selector" style="min-width:220px;"></div>
            <div class="sm-barcode-input" style="min-width:260px;">
                <div class="input-group">
                    <input type="text" class="form-control sm-barcode" placeholder="${__("Scan Barcode / QR Code")}" />
                    <button class="btn btn-sm btn-secondary sm-scan-btn">${__("Scan")}</button>
                </div>
            </div>
            <span class="sm-oee-badge badge badge-info" style="font-size:1em;"></span>
        </div>
        <div class="sm-job-cards-grid row" style="margin-top:10px;"></div>`;
        this.$main.html(html);

        this._ws_field = frappe.ui.form.make_control({
            parent: this.$main.find(".sm-ws-selector")[0],
            df: {fieldtype: "Link", options: "Workstation", label: __("Workstation"), placeholder: __("Select Workstation")},
            only_input: true,
        });
        this._ws_field.refresh();
        this._ws_field.$input.on("change", () => {
            this.workstation = this._ws_field.get_value();
            this.refresh();
        });

        this.$main.find(".sm-scan-btn").on("click", () => this._handle_barcode_scan());
        this.$main.find(".sm-barcode").on("keydown", (e) => {
            if (e.key === "Enter") this._handle_barcode_scan();
        });
    }

    refresh() {
        frappe.call({
            method: "smart_manufacturing.shop_floor.page.shop_floor_terminal.shop_floor_terminal.get_active_job_cards",
            args: {workstation: this.workstation},
            callback: (r) => {
                this._render_job_cards(r.message || []);
                this._update_oee();
            },
        });
    }

    _render_job_cards(cards) {
        const $grid = this.$main.find(".sm-job-cards-grid").empty();
        if (!cards.length) {
            $grid.html(`<div class="col-12 text-muted text-center" style="margin-top:40px;">${__("No active job cards")}</div>`);
            return;
        }
        cards.forEach(c => {
            const progress = c.for_quantity ? Math.round((c.total_completed_qty / c.for_quantity) * 100) : 0;
            const status_color = {
                "Open": "warning", "Work In Progress": "primary", "Complete": "success",
            }[c.status] || "secondary";
            const qc_badge = c.sm_qc_status ? `<span class="badge badge-${c.sm_qc_status === 'Passed' ? 'success' : (c.sm_qc_status === 'Failed' ? 'danger' : 'warning')}">${c.sm_qc_status}</span>` : "";
            const card_html = `
            <div class="col-md-4 col-sm-6" style="margin-bottom:15px;">
                <div class="card h-100 shadow-sm sm-jc-card" data-jc="${frappe.utils.escape_html(c.name)}">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <strong>${frappe.utils.escape_html(c.name)}</strong>
                        <span class="badge badge-${status_color}">${c.status}</span>
                    </div>
                    <div class="card-body" style="font-size:0.9em;">
                        <div><b>${__("Work Order")}:</b> ${frappe.utils.escape_html(c.work_order || "")}</div>
                        <div><b>${__("Operation")}:</b> ${frappe.utils.escape_html(c.operation || "")}</div>
                        <div><b>${__("Workstation")}:</b> ${frappe.utils.escape_html(c.workstation || "")}</div>
                        <div class="mt-2">
                            <div class="d-flex justify-content-between"><small>${__("Progress")}</small><small>${c.total_completed_qty || 0} / ${c.for_quantity || 0}</small></div>
                            <div class="progress mt-1" style="height:8px;">
                                <div class="progress-bar bg-${status_color}" style="width:${progress}%"></div>
                            </div>
                        </div>
                        ${qc_badge ? `<div class="mt-2">${qc_badge}</div>` : ""}
                    </div>
                    <div class="card-footer d-flex gap-2 flex-wrap">
                        ${c.status === "Open" ? `<button class="btn btn-sm btn-primary sm-start-btn">${__("Start")}</button>` : ""}
                        ${c.status === "Work In Progress" ? `<button class="btn btn-sm btn-success sm-complete-btn">${__("Complete")}</button>` : ""}
                        <button class="btn btn-sm btn-secondary sm-scrap-btn">${__("Log Scrap")}</button>
                        <a href="/app/job-card/${encodeURIComponent(c.name)}" class="btn btn-sm btn-light" target="_blank">${__("Open")}</a>
                    </div>
                </div>
            </div>`;
            const $card = $(card_html).appendTo($grid);
            $card.find(".sm-start-btn").on("click", () => this._start_job_card(c.name));
            $card.find(".sm-complete-btn").on("click", () => this._complete_dialog(c));
            $card.find(".sm-scrap-btn").on("click", () => this._scrap_dialog(c));
        });
    }

    _start_job_card(jc_name) {
        frappe.call({
            method: "smart_manufacturing.shop_floor.page.shop_floor_terminal.shop_floor_terminal.start_job_card",
            args: {job_card: jc_name, operator: frappe.session.user},
            callback: () => { frappe.show_alert({message: __("Job Card Started"), indicator: "green"}); this.refresh(); },
        });
    }

    _complete_dialog(jc) {
        const d = new frappe.ui.Dialog({
            title: __("Complete Job Card: {0}", [jc.name]),
            fields: [
                {fieldtype: "Float", fieldname: "qty_completed", label: __("Qty Completed"), reqd: 1, default: jc.for_quantity},
                {fieldtype: "Float", fieldname: "scrap_qty",     label: __("Scrap Qty"),     default: 0},
            ],
            primary_action_label: __("Complete"),
            primary_action: (vals) => {
                frappe.call({
                    method: "smart_manufacturing.shop_floor.page.shop_floor_terminal.shop_floor_terminal.complete_job_card",
                    args: {job_card: jc.name, qty_completed: vals.qty_completed, scrap_qty: vals.scrap_qty},
                    callback: () => { d.hide(); frappe.show_alert({message: __("Job Card Completed"), indicator: "green"}); this.refresh(); },
                });
            },
        });
        d.show();
    }

    _scrap_dialog(jc) {
        const d = new frappe.ui.Dialog({
            title: __("Log Scrap / Rejection"),
            fields: [
                {fieldtype: "Link",   fieldname: "item_code",        label: __("Item"),           options: "Item", reqd: 1},
                {fieldtype: "Float",  fieldname: "scrap_qty",         label: __("Scrap Qty"),      reqd: 1},
                {fieldtype: "Select", fieldname: "rejection_type",    label: __("Rejection Type"),
                  options: "Scrap\nRework\nReturn to Vendor\nQuarantine"},
                {fieldtype: "Data",   fieldname: "defect_code",       label: __("Defect Code")},
                {fieldtype: "Small Text", fieldname: "defect_description", label: __("Description")},
            ],
            primary_action_label: __("Log"),
            primary_action: (vals) => {
                frappe.call({
                    method: "frappe.client.insert",
                    args: {doc: {
                        doctype: "SM Scrap Rejection Log",
                        work_order: jc.work_order,
                        job_card: jc.name,
                        workstation: jc.workstation,
                        ...vals,
                    }},
                    callback: () => { d.hide(); frappe.show_alert({message: __("Scrap Logged"), indicator: "orange"}); this.refresh(); },
                });
            },
        });
        d.show();
    }

    log_downtime_dialog() {
        const d = new frappe.ui.Dialog({
            title: __("Log Downtime"),
            fields: [
                {fieldtype: "Link",     fieldname: "workstation",    label: __("Workstation"),    options: "Workstation", reqd: 1, default: this.workstation},
                {fieldtype: "Link",     fieldname: "work_order",     label: __("Work Order"),     options: "Work Order"},
                {fieldtype: "Select",   fieldname: "downtime_type",  label: __("Downtime Type"),
                  options: "Planned\nUnplanned\nBreakdown\nChangeover\nQuality Issue\nMaterial Shortage\nOther", reqd: 1},
                {fieldtype: "Select",   fieldname: "cause_category", label: __("Cause Category"),
                  options: "\nMachine Failure\nOperator Error\nMaterial Issue\nPower Failure\nScheduled Maintenance\nSetup/Changeover\nOther"},
                {fieldtype: "Datetime", fieldname: "from_time",      label: __("From"),           reqd: 1, default: frappe.datetime.now_datetime()},
            ],
            primary_action_label: __("Log"),
            primary_action: (vals) => {
                frappe.call({
                    method: "smart_manufacturing.shop_floor.page.shop_floor_terminal.shop_floor_terminal.log_downtime",
                    args: vals,
                    callback: (r) => { d.hide(); frappe.show_alert({message: __("Downtime Logged: {0}", [r.message]), indicator: "orange"}); },
                });
            },
        });
        d.show();
    }

    _handle_barcode_scan() {
        const barcode = this.$main.find(".sm-barcode").val().trim();
        if (!barcode) return;
        frappe.call({
            method: "smart_manufacturing.shop_floor.page.shop_floor_terminal.shop_floor_terminal.scan_barcode",
            args: {barcode},
            callback: (r) => {
                const res = r.message;
                if (!res || !res.type) {
                    frappe.show_alert({message: __("Barcode not found"), indicator: "red"});
                    return;
                }
                frappe.show_alert({message: __("{0}: {1}", [res.type, res.name]), indicator: "green"});
                if (res.type === "Work Order") {
                    frappe.set_route("Form", "Work Order", res.name);
                } else if (res.type === "Job Card") {
                    frappe.set_route("Form", "Job Card", res.name);
                }
                this.$main.find(".sm-barcode").val("");
            },
        });
    }

    _update_oee() {
        if (!this.workstation) { this.$main.find(".sm-oee-badge").text(""); return; }
        frappe.call({
            method: "smart_manufacturing.analytics.utils.oee.get_current_oee",
            args: {workstation: this.workstation},
            callback: (r) => {
                if (r.message !== undefined) {
                    this.$main.find(".sm-oee-badge").text(`OEE: ${r.message}%`);
                }
            },
        });
    }
}
