# QUICK START EXAMPLE - Real Estate CRM

Let's say your client is a **Real Estate Agency**. Here's exactly what to do:

## STEP 1: IMMEDIATE ACTIONS (30 minutes)

### A) Login to your CRM instance
```
URL: http://your-site:8000/crm
Login as Administrator
```

### B) Set up custom statuses
**Go to: Search > "Lead Status"**
```
DELETE: Junk, Unqualified (not relevant for real estate)

MODIFY EXISTING:
- "New" → "New Inquiry" 
- "Contacted" → "First Contact Made"
- "Nurture" → "Following Up"
- "Qualified" → "Ready to View Property"

ADD NEW:
- "Property Viewed" (Green color, position 5)
- "Offer Made" (Orange color, position 6)  
- "Deal Closed" (Blue color, position 7)
- "Lost to Competitor" (Red color, position 8)
```

**Go to: Search > "Deal Status"**
```
MODIFY EXISTING:
- "Qualification" → "Initial Interest"
- "Demo/Making" → "Property Showing"  
- "Proposal/Quotation" → "Offer Preparation"
- "Negotiation" → "Price Negotiation"
- "Ready to Close" → "Documentation"
- Keep: "Won", "Lost"
```

### C) Add custom fields to CRM Lead
**Go to: Search > "Customize Form" > Select "CRM Lead"**

**Add these fields:**
```
1. Property Type
   - Fieldname: property_type
   - Fieldtype: Select
   - Options: 
     Apartment
     Villa
     Commercial
     Land

2. Budget Range  
   - Fieldname: budget_range
   - Fieldtype: Select
   - Options:
     Under $100K
     $100K - $250K
     $250K - $500K  
     $500K - $1M
     Above $1M

3. Preferred Location
   - Fieldname: preferred_location
   - Fieldtype: Data
   - Label: Preferred Location

4. Financing Required
   - Fieldname: financing_required
   - Fieldtype: Check
   - Label: Financing Required
```

**Save the form**

## STEP 2: LAYOUT CUSTOMIZATION (20 minutes)

### Modify Quick Entry Layout
**Go to: Search > "CRM Fields Layout" > Find "CRM Lead-Quick Entry"**

**Click Edit, modify the JSON layout:**
```json
[
  {
    "name": "contact_section",
    "label": "Contact Information", 
    "columns": [
      {
        "name": "column_1",
        "fields": ["first_name", "email", "mobile_no"]
      },
      {
        "name": "column_2",
        "fields": ["last_name", "phone", "whatsapp_no"]
      }
    ]
  },
  {
    "name": "property_section",
    "label": "Property Requirements",
    "columns": [
      {
        "name": "column_3", 
        "fields": ["property_type", "budget_range"]
      },
      {
        "name": "column_4",
        "fields": ["preferred_location", "financing_required"]
      }
    ]
  },
  {
    "name": "lead_section",
    "label": "Lead Details",
    "columns": [
      {
        "name": "column_5",
        "fields": ["status", "lead_owner", "source"]
      }
    ]
  }
]
```

**Save**

## STEP 3: HIDE UNWANTED FIELDS (10 minutes)

**Go back to: "Customize Form" > "CRM Lead"**

**Hide these fields (check "Hidden" checkbox):**
```
- Annual Revenue (not relevant for individual buyers)
- No of Employees (not relevant)
- Job Title (optional, can keep if needed)
- Industry (not relevant for individuals)
```

**Change Labels:**
```
- "Lead Owner" → "Sales Agent"
- "Organization" → "Company" (for corporate buyers)
```

**Save**

## STEP 4: TEST YOUR CHANGES (10 minutes)

1. **Go to Leads list** 
2. **Click "Create" button**
3. **You should see your new layout with:**
   - Contact Information section
   - Property Requirements section  
   - Lead Details section
4. **Test creating a lead with new fields**
5. **Check that statuses show your custom options**

## STEP 5: CREATE SAMPLE DATA (15 minutes)

**Create 3 test leads:**

**Lead 1:**
```
Name: John Smith
Email: john@email.com
Mobile: +1-555-0123
Property Type: Apartment
Budget Range: $250K - $500K
Preferred Location: Downtown
Status: New Inquiry
Sales Agent: (your user)
```

**Lead 2:**
```
Name: Sarah Johnson  
Email: sarah@email.com
Mobile: +1-555-0124
Property Type: Villa
Budget Range: $500K - $1M
Preferred Location: Suburbs
Status: First Contact Made  
Sales Agent: (your user)
```

**Lead 3:**
```
Name: ABC Corp
Email: contact@abc.com
Mobile: +1-555-0125
Property Type: Commercial
Budget Range: Above $1M
Preferred Location: Business District
Status: Ready to View Property
Sales Agent: (your user)
```

## STEP 6: TEST LEAD CONVERSION (10 minutes)

1. **Open Lead 3 (ABC Corp)**
2. **Click "Convert" button** 
3. **You'll see the deal creation form**
4. **Complete the conversion**
5. **Check that deal was created with proper information**

## WHAT YOU'VE ACCOMPLISHED (1.5 hours total)

✅ **Customized lead/deal statuses for real estate workflow**
✅ **Added industry-specific fields (property type, budget, etc.)**  
✅ **Modified form layouts for better usability**
✅ **Hidden irrelevant fields**
✅ **Changed labels to match client terminology**
✅ **Tested the complete workflow**
✅ **Created sample data for demonstration**

## NEXT STEPS FOR CLIENT PRESENTATION

1. **Show the customized lead creation process**
2. **Demonstrate the sales pipeline with real estate statuses**  
3. **Show lead-to-deal conversion**
4. **Explain what can be further customized**
5. **Discuss integration needs (website forms, etc.)**

## FOR CLIENT HANDOVER

**Client gets access to:**
- ✅ Modify lead/deal statuses as needed
- ✅ Add new territories (neighborhoods/areas)
- ✅ Add new lead sources  
- ✅ Manage user accounts
- ✅ Import/export data
- ✅ Generate reports

**Client CANNOT modify:**
- ❌ Custom fields (need to request through you)
- ❌ Form layouts (handled by you)
- ❌ System settings
- ❌ Database structure

## BUSINESS BENEFITS TO PRESENT

1. **Industry-Specific**: Tailored for real estate workflows
2. **Lead Pipeline**: Clear progression from inquiry to sale
3. **Team Management**: Multiple agents can work together
4. **Mobile Ready**: Agents can update on-the-go
5. **Integration Ready**: Can connect to website forms
6. **Scalable**: Add unlimited users as team grows
7. **Cost-Effective**: No per-user licensing

This approach gives you a concrete example to work with and demonstrates the power of the system while keeping complexity manageable.