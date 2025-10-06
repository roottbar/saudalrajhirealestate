/** @odoo-module **/

import { AbstractAction } from "@web/webclient/actions/abstract_action";
import { Dialog } from "@web/core/dialog/dialog";
import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart, onMounted, onWillUnmount } from "@odoo/owl";
import { session } from "@web/session";
import { loadJS, loadCSS } from "@web/core/assets";
import { formatDateTime, formatDate } from "@web/core/l10n/dates";
import { rpc } from "@web/core/network/rpc";

export class KsDashboardNinja extends AbstractAction {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.action = useService("action");
        this.dialog = useService("dialog");
        this.notification = useService("notification");
        
        // Initialize properties
        this.ks_mode = 'active';
        this.name = "ks_dashboard";
        this.ksIsDashboardManager = false;
        this.ksDashboardEditMode = false;
        this.ksNewDashboardName = false;
        this.file_type_magic_word = {
            '/': 'jpg',
            'R': 'gif',
            'i': 'png',
            'P': 'svg+xml',
        };
        this.ksAllowItemClick = true;

        // Date filter initialization
        this.form_template = 'ks_dashboard_ninja_template_view';
        this.date_format = formatDate.toString();
        this.datetime_format = formatDateTime.toString();
        this.ks_date_filter_data = null;

        // Date filter selection options
        this.ks_date_filter_selections = {
            'l_none': _t('Date Filter'),
            'l_day': _t('Today'),
            't_week': _t('This Week'),
            't_month': _t('This Month'),
            't_quarter': _t('This Quarter'),
            't_year': _t('This Year'),
            'n_day': _t('Next Day'),
            'n_week': _t('Next Week'),
            'n_month': _t('Next Month'),
            'n_quarter': _t('Next Quarter'),
            'n_year': _t('Next Year'),
            'ls_day': _t('Last Day'),
            'ls_week': _t('Last Week'),
            'ls_month': _t('Last Month'),
            'ls_quarter': _t('Last Quarter'),
            'ls_year': _t('Last Year'),
            'l_week': _t('Last 7 days'),
            'l_month': _t('Last 30 days'),
            'l_quarter': _t('Last 90 days'),
            'l_year': _t('Last 365 days'),
            'ls_past_until_now': _t('Past Till Now'),
            'ls_pastwithout_now': _t('Past Excluding Today'),
            'n_future_starting_now': _t('Future Starting Now'),
            'n_futurestarting_tomorrow': _t('Future Starting Tomorrow'),
            'l_custom': _t('Custom Filter'),
        };

        // Date filter selection order
        this.ks_date_filter_selection_order = ['l_day', 't_week', 't_month', 't_quarter', 't_year', 'n_day',
            'n_week', 'n_month', 'n_quarter', 'n_year', 'ls_day', 'ls_week', 'ls_month', 'ls_quarter',
            'ls_year', 'l_week', 'l_month', 'l_quarter', 'l_year','ls_past_until_now', 'ls_pastwithout_now',
             'n_future_starting_now', 'n_futurestarting_tomorrow', 'l_custom'
        ];

        this.ks_dashboard_id = this.props.action?.params?.ks_dashboard_id;

        this.gridstack_options = {
            staticGrid: true,
            float: false,
            cellHeight: 80,
            styleInHead: true,
            disableOneColumnMode: true,
        };
        
        this.gridstackConfig = {};
        this.grid = false;
        this.chartMeasure = {};
        this.chart_container = {};
        this.list_container = {};

        this.ksChartColorOptions = ['default', 'cool', 'warm', 'neon'];
        this.ksUpdateDashboardItem = this.ksUpdateDashboardItem.bind(this);

        this.ksDateFilterSelection = false;
        this.ksDateFilterStartDate = false;
        this.ksDateFilterEndDate = false;
        this.ksUpdateDashboard = {};

        onWillStart(this.onWillStart);
        onMounted(this.onMounted);
        onWillUnmount(this.onWillUnmount);
    }

    async onWillStart() {
        // Load required JS and CSS libraries
        await Promise.all([
            loadJS('/ks_dashboard_ninja/static/lib/js/Chart.bundle.min.js'),
            loadJS('/ks_dashboard_ninja/static/lib/js/gridstack-h5.js'),
            loadJS('/ks_dashboard_ninja/static/lib/js/chartjs-plugin-datalabels.js'),
            loadJS('/ks_dashboard_ninja/static/lib/js/pdfmake.min.js'),
            loadJS('/ks_dashboard_ninja/static/lib/js/vfs_fonts.js'),
            loadCSS('/ks_dashboard_ninja/static/lib/css/Chart.css'),
            loadCSS('/ks_dashboard_ninja/static/lib/css/Chart.min.css'),
        ]);

        // Add viewport meta tag
        if (!document.querySelector('meta[name="viewport"]')) {
            const meta = document.createElement('meta');
            meta.name = 'viewport';
            meta.content = 'width=device-width, initial-scale=1, user-scalable=no';
            document.head.appendChild(meta);
        }
    }

    onMounted() {
        this.ks_fetch_items_data().then(() => {
            this.ksRenderDashboard();
        });
    }

    onWillUnmount() {
        // Clean up intervals
        Object.values(this.ksUpdateDashboard).forEach(interval => {
            clearInterval(interval);
        });
    }

    getContext() {
        return {
            ksDateFilterSelection: this.ksDateFilterSelection,
            ksDateFilterStartDate: this.ksDateFilterStartDate,
            ksDateFilterEndDate: this.ksDateFilterEndDate,
            ...session.user_context,
        };
    }

    async ks_fetch_items_data() {
        const result = await this.orm.call(
            'ks_dashboard_ninja.board',
            'ks_fetch_dashboard_data',
            [parseInt(this.ks_dashboard_id)],
            { context: this.getContext() }
        );
        
        this.ks_dashboard_data = result;
        this.ksIsDashboardManager = result.ks_dashboard_manager;
        this.ksDashboardEditMode = result.ks_dashboard_edit_mode || false;
        
        return result;
    }

    ksRenderDashboard() {
        // Dashboard rendering logic will be implemented here
        // This is a placeholder for the main rendering method
        console.log('Dashboard rendering started');
    }

    ksUpdateDashboardItem(itemId) {
        // Update dashboard item logic
        console.log('Updating dashboard item:', itemId);
    }
}

// Register the action
registry.category("actions").add("ks_dashboard_ninja", KsDashboardNinja);