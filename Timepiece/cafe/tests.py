from django.test import TestCase
from django.core.management import call_command

# Just redirect to the tests package
# This file is kept to maintain backward compatibility
# All actual test cases are in the tests/ directory

def setUpModule():
    # Load fixtures before running tests
    call_command('loaddata', 'cafe/fixtures/categories.json')
    call_command('loaddata', 'cafe/fixtures/menu_items.json')
    call_command('loaddata', 'cafe/fixtures/users.json')

# Create your tests here.
