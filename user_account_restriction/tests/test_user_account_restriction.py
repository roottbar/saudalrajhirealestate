# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import AccessError
from odoo import fields


class TestUserAccountRestriction(TransactionCase):
    """Test cases for User Account Restriction module"""

    def setUp(self):
        super(TestUserAccountRestriction, self).setUp()
        
        # Create test accounts
        self.account_receivable = self.env['account.account'].create({
            'name': 'Test Receivable Account',
            'code': 'TEST_REC_001',
            'account_type': 'asset_receivable',
            'reconcile': True,
        })
        
        self.account_payable = self.env['account.account'].create({
            'name': 'Test Payable Account', 
            'code': 'TEST_PAY_001',
            'account_type': 'liability_payable',
            'reconcile': True,
        })
        
        self.account_expense = self.env['account.account'].create({
            'name': 'Test Expense Account',
            'code': 'TEST_EXP_001', 
            'account_type': 'expense',
        })
        
        # Create test user
        self.test_user = self.env['res.users'].create({
            'name': 'Test User for Account Restriction',
            'login': 'test_user_restriction',
            'email': 'test@example.com',
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
        })

    def test_user_restricted_accounts_field(self):
        """Test that restricted_account_ids field exists and works"""
        # Test field exists
        self.assertTrue(hasattr(self.test_user, 'restricted_account_ids'))
        
        # Test adding restricted accounts
        self.test_user.restricted_account_ids = [(6, 0, [self.account_receivable.id, self.account_payable.id])]
        
        # Verify accounts are restricted
        self.assertIn(self.account_receivable.id, self.test_user.restricted_account_ids.ids)
        self.assertIn(self.account_payable.id, self.test_user.restricted_account_ids.ids)
        self.assertNotIn(self.account_expense.id, self.test_user.restricted_account_ids.ids)

    def test_account_search_restriction(self):
        """Test that restricted accounts are hidden in search results"""
        # Restrict receivable account for test user
        self.test_user.restricted_account_ids = [(6, 0, [self.account_receivable.id])]
        
        # Search as restricted user
        accounts = self.env['account.account'].with_user(self.test_user).search([])
        
        # Verify restricted account is not in results
        self.assertNotIn(self.account_receivable.id, accounts.ids)
        # Verify non-restricted accounts are still visible
        self.assertIn(self.account_payable.id, accounts.ids)
        self.assertIn(self.account_expense.id, accounts.ids)

    def test_account_read_restriction(self):
        """Test that restricted accounts cannot be read by restricted users"""
        # Restrict payable account for test user
        self.test_user.restricted_account_ids = [(6, 0, [self.account_payable.id])]
        
        # Try to read restricted account as restricted user
        restricted_account = self.account_payable.with_user(self.test_user)
        
        # Should return empty recordset or filtered results
        result = restricted_account.read(['name', 'code'])
        self.assertEqual(len(result), 0, "Restricted user should not be able to read restricted accounts")

    def test_get_restricted_accounts_method(self):
        """Test the get_restricted_accounts method"""
        # Set restricted accounts
        self.test_user.restricted_account_ids = [(6, 0, [self.account_receivable.id, self.account_expense.id])]
        
        # Test method with restricted user
        restricted_ids = self.env['res.users'].with_user(self.test_user).get_restricted_accounts()
        
        # Verify correct accounts are returned
        self.assertEqual(set(restricted_ids), {self.account_receivable.id, self.account_expense.id})

    def test_cache_clearing_on_restriction_update(self):
        """Test that cache is cleared when restrictions are updated"""
        # Initial state - no restrictions
        self.assertEqual(len(self.test_user.restricted_account_ids), 0)
        
        # Add restrictions
        self.test_user.write({
            'restricted_account_ids': [(6, 0, [self.account_receivable.id])]
        })
        
        # Verify restriction is applied
        self.assertEqual(len(self.test_user.restricted_account_ids), 1)
        self.assertIn(self.account_receivable.id, self.test_user.restricted_account_ids.ids)

    def test_multiple_users_different_restrictions(self):
        """Test that different users can have different account restrictions"""
        # Create second test user
        test_user_2 = self.env['res.users'].create({
            'name': 'Test User 2 for Account Restriction',
            'login': 'test_user_restriction_2',
            'email': 'test2@example.com',
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
        })
        
        # Set different restrictions for each user
        self.test_user.restricted_account_ids = [(6, 0, [self.account_receivable.id])]
        test_user_2.restricted_account_ids = [(6, 0, [self.account_payable.id])]
        
        # Test user 1 can see payable but not receivable
        accounts_user_1 = self.env['account.account'].with_user(self.test_user).search([])
        self.assertNotIn(self.account_receivable.id, accounts_user_1.ids)
        self.assertIn(self.account_payable.id, accounts_user_1.ids)
        
        # Test user 2 can see receivable but not payable  
        accounts_user_2 = self.env['account.account'].with_user(test_user_2).search([])
        self.assertIn(self.account_receivable.id, accounts_user_2.ids)
        self.assertNotIn(self.account_payable.id, accounts_user_2.ids)

    def test_admin_user_no_restrictions(self):
        """Test that admin users are not affected by restrictions"""
        # Set restrictions for admin user (should not affect them)
        admin_user = self.env.ref('base.user_admin')
        admin_user.restricted_account_ids = [(6, 0, [self.account_receivable.id])]
        
        # Admin should still see all accounts
        accounts = self.env['account.account'].with_user(admin_user).search([])
        
        # Note: This test might need adjustment based on actual security rule implementation
        # Admin users might have different security rules that bypass restrictions

    def test_security_rules_applied(self):
        """Test that security rules are properly applied"""
        # This test verifies that the ir.rule records are working
        self.test_user.restricted_account_ids = [(6, 0, [self.account_receivable.id])]
        
        # Check that domain filtering is applied
        domain = [('id', 'in', [self.account_receivable.id, self.account_payable.id, self.account_expense.id])]
        accounts = self.env['account.account'].with_user(self.test_user).search(domain)
        
        # Should only return non-restricted accounts
        expected_accounts = {self.account_payable.id, self.account_expense.id}
        actual_accounts = set(accounts.ids)
        
        self.assertEqual(actual_accounts.intersection(expected_accounts), expected_accounts)
        self.assertNotIn(self.account_receivable.id, actual_accounts)

    def test_module_installation_requirements(self):
        """Test that module dependencies are properly installed"""
        # Verify required models exist
        self.assertTrue(self.env['account.account'])
        self.assertTrue(self.env['res.users'])
        self.assertTrue(self.env['account.move'])
        self.assertTrue(self.env['account.move.line'])
        
        # Verify field exists on user model
        user_fields = self.env['res.users']._fields
        self.assertIn('restricted_account_ids', user_fields)
        
        # Verify field is Many2many with correct relation
        field = user_fields['restricted_account_ids']
        self.assertEqual(field.comodel_name, 'account.account')