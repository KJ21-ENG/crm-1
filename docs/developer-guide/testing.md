# Testing

Guide to testing Eshin CRM backend and frontend code.

---

## Backend Testing

### Running Tests

```bash
cd ~/frappe-bench

# Run all tests for CRM app
bench --site eshin.localhost run-tests --app crm

# Run specific test file
bench --site eshin.localhost run-tests \
    --app crm --module crm.fcrm.doctype.crm_lead.test_crm_lead

# Run with verbose output
bench --site eshin.localhost run-tests --app crm -v
```

### Test File Structure

```
crm/fcrm/doctype/crm_lead/
├── crm_lead.json
├── crm_lead.py
└── test_crm_lead.py  # Test file
```

### Writing Tests

```python
# test_crm_lead.py
import frappe
from frappe.tests.utils import FrappeTestCase

class TestCRMLead(FrappeTestCase):
    def setUp(self):
        """Set up test data"""
        self.lead = frappe.get_doc({
            "doctype": "CRM Lead",
            "first_name": "Test",
            "mobile_no": "9876543210"
        })
    
    def test_lead_creation(self):
        """Test basic lead creation"""
        self.lead.insert()
        self.assertTrue(self.lead.name)
    
    def test_lead_validation(self):
        """Test validation rules"""
        self.lead.mobile_no = "123"  # Invalid
        self.assertRaises(frappe.ValidationError, self.lead.insert)
    
    def tearDown(self):
        """Clean up test data"""
        if self.lead.name:
            frappe.delete_doc("CRM Lead", self.lead.name)
```

---

## Linting

### Python Linting (Ruff)

```bash
# Run linter
cd ~/frappe-bench/apps/crm
ruff check crm/

# Fix auto-fixable issues
ruff check --fix crm/
```

Configuration in `pyproject.toml`:
```toml
[tool.ruff]
line-length = 110
target-version = "py310"
```

### JavaScript Linting (ESLint)

```bash
cd ~/frappe-bench/apps/crm/frontend

# Run ESLint
npx eslint src/

# Fix issues
npx eslint src/ --fix
```

### Prettier Formatting

```bash
cd ~/frappe-bench/apps/crm/frontend

# Check formatting
npx prettier --check src/

# Fix formatting
npx prettier --write src/
```

---

## Development Commands

### Bench Commands

```bash
# Start development server
bench start

# Build assets
bench build --app crm

# Clear cache
bench --site eshin.localhost clear-cache

# Open console
bench --site eshin.localhost console

# Run migrations
bench --site eshin.localhost migrate

# Check for issues
bench --site eshin.localhost doctor
```

### Common Development Tasks

```bash
# Watch for changes and rebuild
bench watch

# Generate fixtures
bench --site eshin.localhost export-fixtures

# Import fixtures
bench --site eshin.localhost import-fixtures
```

---

## Test Data

### Creating Test Fixtures

```python
# In console or script
import frappe

# Create test lead
lead = frappe.get_doc({
    "doctype": "CRM Lead",
    "first_name": "Test Lead",
    "mobile_no": "9999999999",
    "lead_source": "Website"
})
lead.insert()
```

### Fixtures Directory

Export test data to `crm/fcrm/fixtures/`:
```bash
bench --site eshin.localhost export-fixtures --doctype "CRM Lead Status"
```

---

## API Testing

### Using curl

```bash
# Login
curl -c cookies.txt -X POST http://localhost:8000/api/method/login \
    -d "usr=Administrator&pwd=admin"

# Make API call
curl -b cookies.txt -X POST http://localhost:8000/api/method/crm.api.doc.get_list \
    -d 'doctype=CRM Lead&fields=["name","first_name"]'
```

### Using Postman

1. Set base URL: `http://localhost:8000`
2. Login to get session cookie
3. Include cookie in subsequent requests

---

## Debugging

### Python Debugging

```python
# Add breakpoint
import pdb; pdb.set_trace()

# Or using frappe
frappe.throw("Debug: " + str(variable))
```

### Frontend Debugging

```javascript
// Console logging
console.log('Debug:', data)

// Vue Devtools (browser extension)
```

### Log Files

```bash
# View logs
tail -f ~/frappe-bench/logs/frappe.log
tail -f ~/frappe-bench/logs/web.error.log
```

---

## Continuous Integration

### Pre-commit Checks

Before committing:
1. Run linter: `ruff check crm/`
2. Run tests: `bench run-tests --app crm`
3. Build frontend: `bench build --app crm`

---

## Best Practices

1. **Write tests for new features**
2. **Run linter before commits**
3. **Use type hints in Python**
4. **Follow existing code patterns**
5. **Document complex logic**
