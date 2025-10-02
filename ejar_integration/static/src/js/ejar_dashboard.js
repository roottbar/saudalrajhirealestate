odoo.define('ejar_integration.dashboard', function (require) {
    'use strict';

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var session = require('web.session');
    var web_client = require('web.web_client');
    var Widget = require('web.Widget');

    var QWeb = core.qweb;
    var _t = core._t;

    var EjarDashboard = AbstractAction.extend({
        template: 'EjarDashboardMain',
        cssLibs: [
            '/ejar_integration/static/src/css/ejar_styles.css',
        ],
        jsLibs: [],

        events: {
            'click .ejar-refresh-btn': 'refresh_dashboard',
            'click .ejar-sync-all-btn': 'sync_all_data',
            'click .ejar-card': 'open_related_view',
            'click .ejar-quick-action': 'execute_quick_action',
        },

        init: function(parent, context) {
            this._super(parent, context);
            this.dashboard_data = {};
            this.is_loading = false;
        },

        willStart: function() {
            var self = this;
            return this._super().then(function() {
                return self.fetch_dashboard_data();
            });
        },

        start: function() {
            var self = this;
            return this._super().then(function() {
                self.render_dashboard();
                self.setup_auto_refresh();
            });
        },

        fetch_dashboard_data: function() {
            var self = this;
            this.is_loading = true;
            
            return rpc.query({
                model: 'ejar.dashboard',
                method: 'get_dashboard_data',
                args: [],
                context: session.user_context,
            }).then(function(data) {
                self.dashboard_data = data;
                self.is_loading = false;
                return data;
            }).catch(function(error) {
                self.is_loading = false;
                self.show_notification(_t('Error loading dashboard data'), 'danger');
                console.error('Dashboard data fetch error:', error);
            });
        },

        render_dashboard: function() {
            var self = this;
            
            if (this.is_loading) {
                this.$('.ejar-dashboard-content').html('<div class="text-center"><i class="fa fa-spinner fa-spin fa-3x"></i><p>Loading...</p></div>');
                return;
            }

            // Render main dashboard cards
            this.render_summary_cards();
            this.render_charts();
            this.render_recent_activities();
            this.render_quick_actions();
        },

        render_summary_cards: function() {
            var data = this.dashboard_data;
            var cards_html = '';

            // Properties Card
            cards_html += this.render_card({
                title: _t('Properties'),
                icon: 'fa-building',
                icon_class: 'property',
                value: data.properties_count || 0,
                subtitle: _t('Total Properties'),
                action: 'ejar.property',
                additional_info: [
                    {label: _t('Available'), value: data.available_properties || 0},
                    {label: _t('Rented'), value: data.rented_properties || 0}
                ]
            });

            // Contracts Card
            cards_html += this.render_card({
                title: _t('Contracts'),
                icon: 'fa-file-contract',
                icon_class: 'contract',
                value: data.contracts_count || 0,
                subtitle: _t('Active Contracts'),
                action: 'ejar.contract',
                additional_info: [
                    {label: _t('Expiring Soon'), value: data.expiring_contracts || 0},
                    {label: _t('Expired'), value: data.expired_contracts || 0}
                ]
            });

            // Tenants Card
            cards_html += this.render_card({
                title: _t('Tenants'),
                icon: 'fa-users',
                icon_class: 'tenant',
                value: data.tenants_count || 0,
                subtitle: _t('Total Tenants'),
                action: 'ejar.tenant',
                additional_info: [
                    {label: _t('Verified'), value: data.verified_tenants || 0},
                    {label: _t('Pending'), value: data.pending_tenants || 0}
                ]
            });

            // Sync Status Card
            cards_html += this.render_card({
                title: _t('Sync Status'),
                icon: 'fa-sync',
                icon_class: 'sync',
                value: data.sync_success_rate || '0%',
                subtitle: _t('Success Rate'),
                action: 'ejar.sync.log',
                additional_info: [
                    {label: _t('Last Sync'), value: data.last_sync_time || _t('Never')},
                    {label: _t('Failed'), value: data.failed_syncs || 0}
                ]
            });

            this.$('.ejar-summary-cards').html(cards_html);
        },

        render_card: function(card_data) {
            var additional_info_html = '';
            if (card_data.additional_info) {
                card_data.additional_info.forEach(function(info) {
                    additional_info_html += '<div class="ejar-card-info"><span class="label">' + info.label + ':</span> <span class="value">' + info.value + '</span></div>';
                });
            }

            return `
                <div class="ejar-card" data-action="${card_data.action}">
                    <div class="ejar-card-header">
                        <div class="ejar-card-icon ${card_data.icon_class}">
                            <i class="fa ${card_data.icon}"></i>
                        </div>
                        <div>
                            <h3 class="ejar-card-title">${card_data.title}</h3>
                            <p class="ejar-card-subtitle">${card_data.subtitle}</p>
                        </div>
                    </div>
                    <div class="ejar-metric">${card_data.value}</div>
                    <div class="ejar-additional-info">${additional_info_html}</div>
                </div>
            `;
        },

        render_charts: function() {
            var self = this;
            var data = this.dashboard_data;

            // Render monthly revenue chart
            if (data.monthly_revenue) {
                this.render_revenue_chart(data.monthly_revenue);
            }

            // Render property status pie chart
            if (data.property_status) {
                this.render_property_status_chart(data.property_status);
            }

            // Render sync performance chart
            if (data.sync_performance) {
                this.render_sync_performance_chart(data.sync_performance);
            }
        },

        render_revenue_chart: function(data) {
            var ctx = this.$('#revenueChart')[0];
            if (!ctx) return;

            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: _t('Monthly Revenue'),
                        data: data.values,
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return value.toLocaleString() + ' SAR';
                                }
                            }
                        }
                    }
                }
            });
        },

        render_property_status_chart: function(data) {
            var ctx = this.$('#propertyStatusChart')[0];
            if (!ctx) return;

            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: data.labels,
                    datasets: [{
                        data: data.values,
                        backgroundColor: [
                            '#10b981',
                            '#f59e0b',
                            '#ef4444',
                            '#6b7280'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        },

        render_sync_performance_chart: function(data) {
            var ctx = this.$('#syncPerformanceChart')[0];
            if (!ctx) return;

            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: _t('Successful Syncs'),
                        data: data.success,
                        backgroundColor: '#10b981'
                    }, {
                        label: _t('Failed Syncs'),
                        data: data.failed,
                        backgroundColor: '#ef4444'
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        x: {
                            stacked: true
                        },
                        y: {
                            stacked: true,
                            beginAtZero: true
                        }
                    }
                }
            });
        },

        render_recent_activities: function() {
            var data = this.dashboard_data.recent_activities || [];
            var activities_html = '';

            data.forEach(function(activity) {
                var icon_class = self.get_activity_icon(activity.type);
                var time_ago = self.format_time_ago(activity.date);
                
                activities_html += `
                    <div class="ejar-activity-item">
                        <div class="ejar-activity-icon">
                            <i class="fa ${icon_class}"></i>
                        </div>
                        <div class="ejar-activity-content">
                            <div class="ejar-activity-title">${activity.title}</div>
                            <div class="ejar-activity-description">${activity.description}</div>
                            <div class="ejar-activity-time">${time_ago}</div>
                        </div>
                    </div>
                `;
            });

            this.$('.ejar-recent-activities').html(activities_html);
        },

        render_quick_actions: function() {
            var actions_html = `
                <div class="ejar-quick-actions">
                    <button class="ejar-btn ejar-btn-primary ejar-quick-action" data-action="create_property">
                        <i class="fa fa-plus"></i> ${_t('Add Property')}
                    </button>
                    <button class="ejar-btn ejar-btn-success ejar-quick-action" data-action="create_contract">
                        <i class="fa fa-file-contract"></i> ${_t('New Contract')}
                    </button>
                    <button class="ejar-btn ejar-btn-warning ejar-quick-action" data-action="sync_all">
                        <i class="fa fa-sync"></i> ${_t('Sync All')}
                    </button>
                    <button class="ejar-btn ejar-btn-primary ejar-quick-action" data-action="view_reports">
                        <i class="fa fa-chart-bar"></i> ${_t('Reports')}
                    </button>
                </div>
            `;

            this.$('.ejar-quick-actions-container').html(actions_html);
        },

        get_activity_icon: function(type) {
            var icons = {
                'contract_created': 'fa-file-contract',
                'property_added': 'fa-building',
                'tenant_verified': 'fa-user-check',
                'payment_received': 'fa-money-bill',
                'sync_completed': 'fa-sync',
                'default': 'fa-info-circle'
            };
            return icons[type] || icons['default'];
        },

        format_time_ago: function(date_string) {
            var date = new Date(date_string);
            var now = new Date();
            var diff = now - date;
            var minutes = Math.floor(diff / 60000);
            var hours = Math.floor(minutes / 60);
            var days = Math.floor(hours / 24);

            if (days > 0) return days + ' ' + _t('days ago');
            if (hours > 0) return hours + ' ' + _t('hours ago');
            if (minutes > 0) return minutes + ' ' + _t('minutes ago');
            return _t('Just now');
        },

        refresh_dashboard: function() {
            var self = this;
            this.fetch_dashboard_data().then(function() {
                self.render_dashboard();
                self.show_notification(_t('Dashboard refreshed'), 'success');
            });
        },

        sync_all_data: function() {
            var self = this;
            this.show_notification(_t('Starting sync process...'), 'info');
            
            rpc.query({
                model: 'ejar.sync.helpers',
                method: 'sync_all_data',
                args: [],
                context: session.user_context,
            }).then(function(result) {
                if (result.success) {
                    self.show_notification(_t('Sync completed successfully'), 'success');
                    self.refresh_dashboard();
                } else {
                    self.show_notification(_t('Sync failed: ') + result.message, 'danger');
                }
            }).catch(function(error) {
                self.show_notification(_t('Sync error occurred'), 'danger');
                console.error('Sync error:', error);
            });
        },

        open_related_view: function(event) {
            var $target = $(event.currentTarget);
            var action = $target.data('action');
            
            if (action) {
                this.do_action({
                    type: 'ir.actions.act_window',
                    res_model: action,
                    view_mode: 'tree,form',
                    views: [[false, 'list'], [false, 'form']],
                    target: 'current',
                });
            }
        },

        execute_quick_action: function(event) {
            var $target = $(event.currentTarget);
            var action = $target.data('action');
            
            switch(action) {
                case 'create_property':
                    this.do_action({
                        type: 'ir.actions.act_window',
                        res_model: 'ejar.property',
                        view_mode: 'form',
                        views: [[false, 'form']],
                        target: 'current',
                    });
                    break;
                case 'create_contract':
                    this.do_action({
                        type: 'ir.actions.act_window',
                        res_model: 'ejar.contract',
                        view_mode: 'form',
                        views: [[false, 'form']],
                        target: 'current',
                    });
                    break;
                case 'sync_all':
                    this.sync_all_data();
                    break;
                case 'view_reports':
                    this.do_action({
                        type: 'ir.actions.act_window',
                        res_model: 'ejar.sync.log',
                        view_mode: 'pivot,graph',
                        views: [[false, 'pivot'], [false, 'graph']],
                        target: 'current',
                    });
                    break;
            }
        },

        setup_auto_refresh: function() {
            var self = this;
            // Auto refresh every 5 minutes
            setInterval(function() {
                if (!self.isDestroyed()) {
                    self.fetch_dashboard_data().then(function() {
                        self.render_dashboard();
                    });
                }
            }, 300000);
        },

        show_notification: function(message, type) {
            this.do_notify(_t('Ejar Integration'), message, type === 'danger');
        },

        destroy: function() {
            this._super();
        }
    });

    core.action_registry.add('ejar_dashboard', EjarDashboard);

    return EjarDashboard;
});