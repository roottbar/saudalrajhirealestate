# -*- coding: utf-8 -*-

import json
import logging
from datetime import datetime, timedelta
from collections import defaultdict

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class EjarSyncHelpers:
    """Helper functions for Ejar synchronization operations"""

    @staticmethod
    def create_sync_log(env, model_name, record_id, operation, status='pending', error_message=None, ejar_response=None):
        """Create a synchronization log entry"""
        try:
            sync_log = env['ejar.sync.log'].create({
                'model_name': model_name,
                'record_id': record_id,
                'operation': operation,
                'status': status,
                'error_message': error_message,
                'ejar_response': json.dumps(ejar_response) if ejar_response else None,
                'sync_date': fields.Datetime.now(),
            })
            return sync_log
        except Exception as e:
            _logger.error("Failed to create sync log: %s", str(e))
            return None

    @staticmethod
    def update_sync_log(sync_log, status, error_message=None, ejar_response=None):
        """Update an existing synchronization log"""
        try:
            update_vals = {
                'status': status,
                'sync_date': fields.Datetime.now(),
            }
            
            if error_message:
                update_vals['error_message'] = error_message
            
            if ejar_response:
                update_vals['ejar_response'] = json.dumps(ejar_response)
            
            sync_log.write(update_vals)
            return True
        except Exception as e:
            _logger.error("Failed to update sync log: %s", str(e))
            return False

    @staticmethod
    def get_pending_syncs(env, model_name=None, limit=100):
        """Get pending synchronization records"""
        domain = [('status', '=', 'pending')]
        if model_name:
            domain.append(('model_name', '=', model_name))
        
        return env['ejar.sync.log'].search(domain, limit=limit, order='create_date asc')

    @staticmethod
    def get_failed_syncs(env, model_name=None, limit=100):
        """Get failed synchronization records"""
        domain = [('status', '=', 'failed')]
        if model_name:
            domain.append(('model_name', '=', model_name))
        
        return env['ejar.sync.log'].search(domain, limit=limit, order='create_date desc')

    @staticmethod
    def retry_failed_sync(env, sync_log_id):
        """Retry a failed synchronization"""
        sync_log = env['ejar.sync.log'].browse(sync_log_id)
        if not sync_log.exists():
            raise UserError(_("Sync log not found"))
        
        if sync_log.status != 'failed':
            raise UserError(_("Only failed syncs can be retried"))
        
        # Reset status to pending
        sync_log.write({
            'status': 'pending',
            'error_message': None,
            'retry_count': sync_log.retry_count + 1,
        })
        
        # Trigger sync based on model and operation
        record = env[sync_log.model_name].browse(sync_log.record_id)
        if record.exists():
            return EjarSyncHelpers.sync_record_to_ejar(record, sync_log.operation)
        else:
            sync_log.write({
                'status': 'failed',
                'error_message': _("Record no longer exists"),
            })
            return False

    @staticmethod
    def sync_record_to_ejar(record, operation='create'):
        """Sync a single record to Ejar platform"""
        try:
            model_name = record._name
            
            # Get the appropriate sync method based on model
            sync_methods = {
                'ejar.property': '_sync_property_to_ejar',
                'ejar.contract': '_sync_contract_to_ejar',
                'ejar.tenant': '_sync_tenant_to_ejar',
                'ejar.landlord': '_sync_landlord_to_ejar',
                'ejar.broker': '_sync_broker_to_ejar',
                'ejar.payment': '_sync_payment_to_ejar',
                'ejar.notification': '_sync_notification_to_ejar',
            }
            
            sync_method = sync_methods.get(model_name)
            if not sync_method:
                _logger.warning("No sync method found for model: %s", model_name)
                return False
            
            # Call the sync method
            if hasattr(record, sync_method):
                return getattr(record, sync_method)(operation)
            else:
                _logger.error("Sync method %s not found in model %s", sync_method, model_name)
                return False
                
        except Exception as e:
            _logger.error("Failed to sync record %s[%s]: %s", record._name, record.id, str(e))
            return False

    @staticmethod
    def batch_sync_records(env, model_name, record_ids, operation='create', batch_size=10):
        """Sync multiple records in batches"""
        results = {
            'success': 0,
            'failed': 0,
            'errors': []
        }
        
        records = env[model_name].browse(record_ids)
        
        # Process records in batches
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            
            for record in batch:
                try:
                    if EjarSyncHelpers.sync_record_to_ejar(record, operation):
                        results['success'] += 1
                    else:
                        results['failed'] += 1
                        results['errors'].append(f"Failed to sync {record.display_name}")
                except Exception as e:
                    results['failed'] += 1
                    results['errors'].append(f"Error syncing {record.display_name}: {str(e)}")
            
            # Add small delay between batches to avoid overwhelming the API
            import time
            time.sleep(1)
        
        return results

    @staticmethod
    def check_sync_status(env, model_name=None, days_back=7):
        """Check synchronization status for the last N days"""
        date_from = fields.Datetime.now() - timedelta(days=days_back)
        
        domain = [('create_date', '>=', date_from)]
        if model_name:
            domain.append(('model_name', '=', model_name))
        
        sync_logs = env['ejar.sync.log'].search(domain)
        
        stats = defaultdict(int)
        for log in sync_logs:
            stats[f"{log.model_name}_{log.status}"] += 1
            stats[f"total_{log.status}"] += 1
            stats['total'] += 1
        
        return dict(stats)

    @staticmethod
    def cleanup_old_sync_logs(env, days_to_keep=30):
        """Clean up old synchronization logs"""
        cutoff_date = fields.Datetime.now() - timedelta(days=days_to_keep)
        
        old_logs = env['ejar.sync.log'].search([
            ('create_date', '<', cutoff_date),
            ('status', 'in', ['success', 'failed'])
        ])
        
        count = len(old_logs)
        old_logs.unlink()
        
        _logger.info("Cleaned up %d old sync logs", count)
        return count

    @staticmethod
    def get_sync_statistics(env, model_name=None, period='week'):
        """Get detailed synchronization statistics"""
        # Calculate date range based on period
        now = fields.Datetime.now()
        if period == 'day':
            date_from = now - timedelta(days=1)
        elif period == 'week':
            date_from = now - timedelta(weeks=1)
        elif period == 'month':
            date_from = now - timedelta(days=30)
        else:
            date_from = now - timedelta(weeks=1)  # Default to week
        
        domain = [('create_date', '>=', date_from)]
        if model_name:
            domain.append(('model_name', '=', model_name))
        
        sync_logs = env['ejar.sync.log'].search(domain)
        
        # Group by model and status
        stats = {}
        for log in sync_logs:
            model = log.model_name
            if model not in stats:
                stats[model] = {
                    'pending': 0,
                    'success': 0,
                    'failed': 0,
                    'total': 0
                }
            
            stats[model][log.status] += 1
            stats[model]['total'] += 1
        
        # Calculate success rates
        for model_stats in stats.values():
            total = model_stats['total']
            if total > 0:
                model_stats['success_rate'] = (model_stats['success'] / total) * 100
            else:
                model_stats['success_rate'] = 0
        
        return stats

    @staticmethod
    def schedule_sync(env, model_name, record_id, operation='create', delay_minutes=0):
        """Schedule a synchronization for later execution"""
        scheduled_date = fields.Datetime.now() + timedelta(minutes=delay_minutes)
        
        return env['ejar.sync.queue'].create({
            'model_name': model_name,
            'record_id': record_id,
            'operation': operation,
            'scheduled_date': scheduled_date,
            'status': 'scheduled',
        })

    @staticmethod
    def process_sync_queue(env, limit=50):
        """Process scheduled synchronizations"""
        now = fields.Datetime.now()
        
        queued_syncs = env['ejar.sync.queue'].search([
            ('status', '=', 'scheduled'),
            ('scheduled_date', '<=', now)
        ], limit=limit, order='scheduled_date asc')
        
        results = {
            'processed': 0,
            'success': 0,
            'failed': 0,
            'errors': []
        }
        
        for sync_item in queued_syncs:
            try:
                sync_item.write({'status': 'processing'})
                
                record = env[sync_item.model_name].browse(sync_item.record_id)
                if record.exists():
                    if EjarSyncHelpers.sync_record_to_ejar(record, sync_item.operation):
                        sync_item.write({'status': 'completed'})
                        results['success'] += 1
                    else:
                        sync_item.write({'status': 'failed'})
                        results['failed'] += 1
                else:
                    sync_item.write({
                        'status': 'failed',
                        'error_message': _("Record no longer exists")
                    })
                    results['failed'] += 1
                
                results['processed'] += 1
                
            except Exception as e:
                error_msg = str(e)
                sync_item.write({
                    'status': 'failed',
                    'error_message': error_msg
                })
                results['failed'] += 1
                results['errors'].append(f"Error processing {sync_item.model_name}[{sync_item.record_id}]: {error_msg}")
        
        return results

    @staticmethod
    def validate_sync_dependencies(record):
        """Validate that all dependencies are synced before syncing a record"""
        model_name = record._name
        
        # Define dependency rules
        dependencies = {
            'ejar.contract': ['ejar.property', 'ejar.tenant', 'ejar.landlord'],
            'ejar.payment': ['ejar.contract'],
            'ejar.notification': [],  # No dependencies
        }
        
        required_models = dependencies.get(model_name, [])
        missing_deps = []
        
        for dep_model in required_models:
            if dep_model == 'ejar.property' and hasattr(record, 'property_id'):
                if not record.property_id.ejar_synced:
                    missing_deps.append(_("Property must be synced first"))
            
            elif dep_model == 'ejar.tenant' and hasattr(record, 'tenant_id'):
                if not record.tenant_id.ejar_synced:
                    missing_deps.append(_("Tenant must be synced first"))
            
            elif dep_model == 'ejar.landlord' and hasattr(record, 'landlord_id'):
                if not record.landlord_id.ejar_synced:
                    missing_deps.append(_("Landlord must be synced first"))
            
            elif dep_model == 'ejar.contract' and hasattr(record, 'contract_id'):
                if not record.contract_id.ejar_synced:
                    missing_deps.append(_("Contract must be synced first"))
        
        if missing_deps:
            raise ValidationError('\n'.join(missing_deps))
        
        return True

    @staticmethod
    def auto_sync_dependencies(record):
        """Automatically sync dependencies before syncing the main record"""
        model_name = record._name
        
        # Define dependency sync order
        sync_order = {
            'ejar.contract': ['property_id', 'tenant_id', 'landlord_id', 'broker_id'],
            'ejar.payment': ['contract_id'],
        }
        
        dependencies = sync_order.get(model_name, [])
        
        for dep_field in dependencies:
            if hasattr(record, dep_field):
                dep_record = getattr(record, dep_field)
                if dep_record and not dep_record.ejar_synced:
                    _logger.info("Auto-syncing dependency %s for %s", dep_field, record.display_name)
                    EjarSyncHelpers.sync_record_to_ejar(dep_record, 'create')

    @staticmethod
    def handle_sync_conflict(env, local_record, ejar_data):
        """Handle synchronization conflicts between local and Ejar data"""
        conflicts = []
        
        # Compare key fields and identify conflicts
        field_mappings = {
            'name': 'name',
            'status': 'status',
            'monthly_rent': 'monthly_rent',
            'start_date': 'start_date',
            'end_date': 'end_date',
        }
        
        for local_field, ejar_field in field_mappings.items():
            if hasattr(local_record, local_field) and ejar_field in ejar_data:
                local_value = getattr(local_record, local_field)
                ejar_value = ejar_data[ejar_field]
                
                if local_value != ejar_value:
                    conflicts.append({
                        'field': local_field,
                        'local_value': local_value,
                        'ejar_value': ejar_value,
                    })
        
        if conflicts:
            # Log the conflict
            _logger.warning("Sync conflict detected for %s[%s]: %s", 
                          local_record._name, local_record.id, conflicts)
            
            # Create conflict resolution record
            env['ejar.sync.conflict'].create({
                'model_name': local_record._name,
                'record_id': local_record.id,
                'conflicts': json.dumps(conflicts),
                'ejar_data': json.dumps(ejar_data),
                'status': 'pending',
            })
            
            return False  # Don't proceed with sync
        
        return True  # No conflicts, proceed with sync

    @staticmethod
    def resolve_sync_conflict(env, conflict_id, resolution='local'):
        """Resolve a synchronization conflict"""
        conflict = env['ejar.sync.conflict'].browse(conflict_id)
        if not conflict.exists():
            raise UserError(_("Conflict not found"))
        
        record = env[conflict.model_name].browse(conflict.record_id)
        if not record.exists():
            conflict.write({'status': 'resolved', 'resolution': 'record_deleted'})
            return True
        
        conflicts_data = json.loads(conflict.conflicts)
        ejar_data = json.loads(conflict.ejar_data)
        
        if resolution == 'ejar':
            # Update local record with Ejar data
            update_vals = {}
            for conflict_item in conflicts_data:
                field = conflict_item['field']
                ejar_value = conflict_item['ejar_value']
                update_vals[field] = ejar_value
            
            record.write(update_vals)
            
        elif resolution == 'local':
            # Keep local data and sync to Ejar
            EjarSyncHelpers.sync_record_to_ejar(record, 'update')
        
        conflict.write({
            'status': 'resolved',
            'resolution': resolution,
            'resolved_date': fields.Datetime.now(),
        })
        
        return True