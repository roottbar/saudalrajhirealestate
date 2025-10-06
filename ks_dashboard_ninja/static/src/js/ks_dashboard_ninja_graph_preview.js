/** @odoo-module **/

import { Component, useState, useRef, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { useService } from "@web/core/utils/hooks";
import { loadJS, loadCSS } from "@web/core/assets";
import { session } from "@web/session";
import { _t } from "@web/core/l10n/translation";
import { KsGlobalFunction } from "./ks_global_functions";

const fieldRegistry = registry.category("fields");

export class KsGraphPreview extends Component {
    static template = "ks_graph_preview_template";
    static props = {
        ...standardFieldProps,
    };

    setup() {
        this.rpc = useService("rpc");
        this.notification = useService("notification");
        
        this.state = useState({
            chartData: null,
            chartType: 'bar',
            isLoading: false,
            error: null,
        });
        
        this.chartRef = useRef("chartContainer");
        this.chartInstance = null;
        this.shouldRenderChart = false;
        
        onMounted(() => {
            this.loadChartLibraries().then(() => {
                this.initializeChart();
            });
        });
        
        onWillUnmount(() => {
            this.destroyChart();
        });
    }

    async loadChartLibraries() {
        try {
            await Promise.all([
                loadJS('/ks_dashboard_ninja/static/lib/js/Chart.bundle.min.js'),
                loadJS('/ks_dashboard_ninja/static/lib/js/chartjs-plugin-datalabels.js'),
                loadCSS('/ks_dashboard_ninja/static/lib/css/Chart.min.css')
            ]);
            
            // Unregister ChartDataLabels plugin globally
            if (window.Chart && window.ChartDataLabels) {
                window.Chart.plugins.unregister(window.ChartDataLabels);
            }
        } catch (error) {
            console.error('Failed to load chart libraries:', error);
            this.state.error = 'Failed to load chart libraries';
        }
    }

    initializeChart() {
        this.setDefaultChartView();
        this.shouldRenderChart = true;
        
        if (this.chartRef.el) {
            this.renderChart();
        }
    }

    setDefaultChartView() {
        if (!window.Chart) return;
        
        // Register custom plugin for empty chart message
        window.Chart.plugins.register({
            afterDraw: (chart) => {
                if (chart.data.labels.length === 0) {
                    const ctx = chart.chart.ctx;
                    const width = chart.chart.width;
                    const height = chart.chart.height;
                    
                    chart.clear();
                    ctx.save();
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.font = "16px normal 'Helvetica Nueue'";
                    ctx.fillText(_t('No data to display'), width / 2, height / 2);
                    ctx.restore();
                }
            }
        });
    }

    destroyChart() {
        if (this.chartInstance) {
            this.chartInstance.destroy();
            this.chartInstance = null;
        }
    }

    async renderChart() {
        if (!this.chartRef.el || !window.Chart) {
            return;
        }
        
        this.destroyChart();
        
        try {
            const chartData = await this.getChartData();
            if (!chartData) {
                return;
            }
            
            const ctx = this.chartRef.el.getContext('2d');
            const config = this.getChartConfig(chartData);
            
            this.chartInstance = new window.Chart(ctx, config);
        } catch (error) {
            console.error('Error rendering chart:', error);
            this.state.error = 'Error rendering chart';
        }
    }

    async getChartData() {
        if (!this.props.record || !this.props.record.data) {
            return null;
        }
        
        const recordData = this.props.record.data;
        
        // Extract chart configuration from record
        const chartType = recordData.ks_dashboard_item_type || 'bar';
        const modelName = recordData.ks_model_name;
        const domain = recordData.ks_domain || '[]';
        
        if (!modelName) {
            return null;
        }
        
        try {
            this.state.isLoading = true;
            
            const result = await this.rpc('/web/dataset/call_kw', {
                model: 'ks.dashboard.ninja.item',
                method: 'ks_get_chart_data',
                args: [recordData.id || 0],
                kwargs: {
                    context: session.user_context,
                }
            });
            
            this.state.isLoading = false;
            return result;
            
        } catch (error) {
            this.state.isLoading = false;
            console.error('Error fetching chart data:', error);
            return null;
        }
    }

    getChartConfig(chartData) {
        const chartType = this.getChartType(chartData.chart_type);
        
        const config = {
            type: chartType,
            data: {
                labels: chartData.labels || [],
                datasets: chartData.datasets || []
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            generateLabels: (chart) => {
                                const original = window.Chart.defaults.plugins.legend.labels.generateLabels;
                                const labels = original.call(this, chart);
                                
                                labels.forEach(label => {
                                    if (label.text && label.text.length > 25) {
                                        label.text = label.text.substring(0, 22) + '...';
                                    }
                                });
                                
                                return labels;
                            }
                        }
                    },
                    tooltip: {
                        enabled: true,
                        mode: 'index',
                        intersect: false,
                    }
                },
                scales: this.getScalesConfig(chartType),
                animation: {
                    duration: 1000,
                    easing: 'easeInOutQuart'
                }
            }
        };
        
        return config;
    }

    getChartType(type) {
        const typeMap = {
            'ks_bar_chart': 'bar',
            'ks_horizontalBar_chart': 'horizontalBar',
            'ks_line_chart': 'line',
            'ks_area_chart': 'line',
            'ks_pie_chart': 'pie',
            'ks_doughnut_chart': 'doughnut',
            'ks_polarArea_chart': 'polarArea',
            'ks_radar_chart': 'radar'
        };
        
        return typeMap[type] || 'bar';
    }

    getScalesConfig(chartType) {
        if (['pie', 'doughnut', 'polarArea', 'radar'].includes(chartType)) {
            return {};
        }
        
        return {
            x: {
                display: true,
                grid: {
                    display: true
                }
            },
            y: {
                display: true,
                grid: {
                    display: true
                },
                beginAtZero: true
            }
        };
    }

    get isReadonly() {
        return this.props.readonly;
    }

    get hasError() {
        return !!this.state.error;
    }

    get isChartLoading() {
        return this.state.isLoading;
    }

    refreshChart() {
        this.renderChart();
    }

    updateChartType(newType) {
        this.state.chartType = newType;
        this.renderChart();
    }
}

KsGraphPreview.supportedTypes = ["char"];

fieldRegistry.add("ks_dashboard_graph_preview", KsGraphPreview);