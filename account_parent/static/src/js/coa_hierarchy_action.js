/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onWillStart, useState, useRef, onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";

export class CoAHierarchyAction extends Component {
    static template = "account_parent.CoAHierarchy";
    static props = {
        action: Object,
    };

    setup() {
        this.actionService = useService("action");
        this.rpc = useService("rpc");
        this.orm = useService("orm");
        this.notification = useService("notification");
        
        this.state = useState({
            html: "",
            loading: true,
        });
        
        this.containerRef = useRef("container");
        this.given_context = this.props.action.context || {};
        this.controller_url = this.given_context.url || '/account_parent/output_format/account_parent/active_id';
        
        onWillStart(async () => {
            await this.loadReport();
        });
        
        onMounted(() => {
            this.bindEvents();
            if (this.given_context.auto_unfold) {
                this.autoUnfoldAll();
            }
        });
    }

    bindEvents() {
        const container = this.containerRef.el;
        if (!container) return;
        
        // Bind fold/unfold events
        container.addEventListener('click', (ev) => {
            if (ev.target.closest('.o_coa_foldable')) {
                this.onFold(ev);
            } else if (ev.target.closest('.o_coa_unfoldable')) {
                this.onUnfold(ev);
            } else if (ev.target.closest('.o_coa_action')) {
                this.onActionClick(ev);
            }
        });
    }

    async loadReport() {
        try {
            const result = await this.orm.call(
                "account.open.chart",
                "get_html",
                [this.given_context]
            );
            
            this.state.html = result.html;
            this.state.loading = false;
        } catch (error) {
            this.notification.add("Error loading report", { type: "danger" });
            console.error("Error loading report:", error);
            this.state.loading = false;
        }
    }

    autoUnfoldAll() {
        const unfoldableElements = this.containerRef.el?.querySelectorAll('.o_coa_unfoldable');
        unfoldableElements?.forEach(element => {
            if (element.querySelector('.fa-caret-right')) {
                this.autoUnfold(element);
            }
        });
    }

    async autoUnfold(element) {
        const tr = element.closest('tr');
        const td = tr?.querySelector('td.treeview-td');
        if (!td) return;

        const active_id = parseInt(td.dataset.id);
        const wiz_id = parseInt(td.dataset.wiz_id);
        const model_id = parseInt(td.dataset.model_id);
        const level = parseInt(td.dataset.level);

        try {
            const lines = await this.orm.call(
                "account.open.chart",
                "get_lines",
                [wiz_id, active_id],
                {
                    model_id: model_id,
                    level: level + 1
                }
            );

            // Insert new lines after current row
            let cursor = tr;
            lines.forEach(line => {
                const newRow = this.renderLine(line);
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = newRow;
                const newTr = tempDiv.firstElementChild;
                cursor.parentNode.insertBefore(newTr, cursor.nextSibling);
                cursor = newTr;
                
                if (line.auto_unfold && line.unfoldable) {
                    setTimeout(() => {
                        const newUnfoldable = cursor.querySelector('.o_coa_unfoldable');
                        if (newUnfoldable) {
                            this.autoUnfold(newUnfoldable);
                        }
                    }, 50);
                }
            });

            // Update icon
            const icon = element.querySelector('i');
            if (icon) {
                icon.classList.remove('fa-caret-right');
                icon.classList.add('fa-caret-down');
            }
            element.classList.remove('o_coa_unfoldable');
            element.classList.add('o_coa_foldable');
            tr.classList.add('o_coa_unfolded');
        } catch (error) {
            console.error("Error unfolding:", error);
        }
    }

    renderLine(line) {
        const space_td = `background-position: ${19*(line.level-1)}px; padding-left: ${4 + 19*(line.level-1)}px;`;
        const trclass = line.type === 'view' ? 'o_coa_level' : 'o_coa_default_style';
        const domainClass = line.unfoldable ? 'o_coa_domain_line_0' : 'o_coa_domain_line_1';

        return `
            <tr data-type="${line.type}" 
                data-unfold="${line.unfoldable}" 
                data-parent_id="${line.parent_id}" 
                data-id="${line.id}"  
                data-model_id="${line.model_id}" 
                data-wiz_id="${line.wiz_id}" 
                data-name="${line.name}" 
                class="${trclass}">
                <td style="white-space: nowrap;" 
                    data-id="${line.id}" 
                    data-name="${line.name}"
                    data-model_id="${line.model_id}" 
                    class="treeview-td" 
                    data-level="${line.level}"  
                    data-wiz_id="${line.wiz_id}">
                    <span style="${space_td}" class="${domainClass}"></span>
                    ${line.unfoldable ? `
                        <span class="o_coa_unfoldable o_coa_caret_icon">
                            <i class="fa fa-fw fa-caret-right"></i>
                        </span>
                    ` : ''}
                    ${line.code}
                </td>
                <td class="o_coa_action" data-id="${line.id}" data-name="${line.name}" data-wiz_id="${line.wiz_id}">
                    ${line.name}
                </td>
                <td class="o_coa_action" data-id="${line.id}" data-name="${line.name}" data-wiz_id="${line.wiz_id}">
                    ${line.ac_type}
                </td>
                ${line.show_initial_balance ? `
                    <td class="o_coa_action" data-id="${line.id}" data-name="${line.name}" data-wiz_id="${line.wiz_id}" style="text-align: right;">
                        ${line.initial_balance}
                    </td>
                ` : ''}
                <td class="o_coa_action" data-id="${line.id}" data-name="${line.name}" data-wiz_id="${line.wiz_id}" style="text-align: right;">
                    ${line.debit}
                </td>
                <td class="o_coa_action" data-id="${line.id}" data-name="${line.name}" data-wiz_id="${line.wiz_id}" style="text-align: right;">
                    ${line.credit}
                </td>
                <td class="o_coa_action" data-id="${line.id}" data-name="${line.name}" data-wiz_id="${line.wiz_id}" style="text-align: right;">
                    ${line.show_initial_balance ? line.ending_balance : line.balance}
                </td>
            </tr>
        `;
    }

    onFold(ev) {
        const element = ev.target.closest('.o_coa_foldable');
        const tr = element.closest('tr');
        const rec_id = tr.dataset.id;
        
        // Remove child rows
        const childRows = [...tr.parentElement.querySelectorAll(`tr[data-parent_id="${rec_id}"]`)];
        childRows.forEach(row => {
            this.removeChildRows(row);
            row.remove();
        });
        
        // Update icon
        const icon = element.querySelector('i');
        if (icon) {
            icon.classList.remove('fa-caret-down');
            icon.classList.add('fa-caret-right');
        }
        element.classList.remove('o_coa_foldable');
        element.classList.add('o_coa_unfoldable');
        tr.classList.remove('o_coa_unfolded');
    }

    removeChildRows(element) {
        const rec_id = element.dataset.id;
        const childRows = [...element.parentElement.querySelectorAll(`tr[data-parent_id="${rec_id}"]`)];
        childRows.forEach(row => {
            this.removeChildRows(row);
            row.remove();
        });
    }

    onUnfold(ev) {
        const element = ev.target.closest('.o_coa_unfoldable');
        this.autoUnfold(element);
    }

    async onActionClick(ev) {
        const element = ev.target.closest('.o_coa_action');
        const account_id = parseInt(element.dataset.id);
        const account_name = element.dataset.name;
        const wiz_id = parseInt(element.dataset.wiz_id);

        try {
            const [domain, context] = await this.orm.call(
                "account.open.chart",
                "build_domain_context",
                [wiz_id, account_id]
            );

            if (!context.company_id) {
                this.notification.add("Journal items are not available for current report", { type: "warning" });
                return;
            }

            await this.actionService.doAction({
                name: `Journal Items (${account_name})`,
                type: 'ir.actions.act_window',
                res_model: 'account.move.line',
                domain: domain,
                context: context,
                views: [[false, 'list'], [false, 'form']],
                view_mode: "list",
                target: 'current'
            });
        } catch (error) {
            console.error("Error opening journal items:", error);
        }
    }

    async onPrintPDF() {
        const active_id = this.given_context.active_id;
        const url = this.controller_url.replace('active_id', active_id).replace('output_format', 'pdf');
        window.open(url, '_blank');
    }

    getCSRFToken() {
        // Get CSRF token from meta tag or cookie
        const metaTag = document.querySelector('meta[name="csrf_token"]');
        if (metaTag) {
            return metaTag.getAttribute('content');
        }
        
        // Fallback to cookie
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrf_token') {
                return value;
            }
        }
        
        return '';
    }

    async onPrintXLS() {
        const active_id = this.given_context.active_id;
        const data = {
            model: 'account.open.chart',
            wiz_id: active_id,
        };
        
        // Create form and submit for download
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/account_parent/export/xls';
        
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'data';
        input.value = JSON.stringify(data);
        
        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrf_token';
        csrfInput.value = this.getCSRFToken();
        
        form.appendChild(input);
        form.appendChild(csrfInput);
        document.body.appendChild(form);
        form.submit();
        document.body.removeChild(form);
        form.remove();
    }
}

registry.category("actions").add("coa_hierarchy", CoAHierarchyAction);
