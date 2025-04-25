
database_schema =  {
    "numbers_app_task": {
      "columns": {
        "id": "BigAutoField",
        "title": "CharField",
        "description": "TextField",
        "embedding": "VectorField",
        "created_at": "DateTimeField",
        "project_name": "CharField",
        "status": "CharField",
        "employee_name": "CharField"
      },
      "foreign_keys": {},
      "choices": {},
      "inferred_relationships": {}
    },
    "numbers_app_industry": {
      "columns": {
        "id": "BigAutoField",
        "name": "CharField"
      },
      "foreign_keys": {},
      "choices": {},
      "inferred_relationships": {}
    },
    "numbers_app_currency": {
      "columns": {
        "id": "BigAutoField",
        "name": "CharField",
        "currency_code": "CharField",
        "symbol": "CharField"
      },
      "foreign_keys": {},
      "choices": {},
      "inferred_relationships": {}
    },
    "numbers_app_timezone": {
      "columns": {
        "id": "BigAutoField",
        "time_zone": "CharField",
        "sort_index": "IntegerField"
      },
      "foreign_keys": {},
      "choices": {},
      "inferred_relationships": {}
    },
    "numbers_app_dateformat": {
      "columns": {
        "id": "BigAutoField",
        "date_format": "CharField"
      },
      "foreign_keys": {},
      "choices": {},
      "inferred_relationships": {}
    },
    "numbers_app_fiscalyear": {
      "columns": {
        "id": "BigAutoField",
        "month_range": "CharField"
      },
      "foreign_keys": {},
      "choices": {},
      "inferred_relationships": {}
    },
    "numbers_app_country": {
      "columns": {
        "id": "BigAutoField",
        "name": "CharField",
        "alpha_2": "CharField",
        "alpha_3": "CharField",
        "currency": "ForeignKey",
        "financial_year_last_day": "DateTimeField",
        "date_format": "ForeignKey",
        "fiscal_year": "ForeignKey"
      },
      "foreign_keys": {
        "currency": "numbers_app_currency",
        "date_format": "numbers_app_dateformat",
        "fiscal_year": "numbers_app_fiscalyear"
      },
      "choices": {},
      "inferred_relationships": {},
      "description": "The Country model stores country-specific configurations used in the financial system — including currency, time zones, fiscal settings, and formatting preferences. Relationships: Currency: Foreign key to Currency model (nullable) TimeZone: Many-to-Many link to TimeZone (e.g., a country might span multiple zones) DateFormat: Optional link to how dates should be formatted (e.g., DD/MM/YYYY) FiscalYear: Link to fiscal year configuration used in accounting"
    },
    "numbers_app_state": {
      "columns": {
        "id": "BigAutoField",
        "country": "ForeignKey",
        "name": "CharField",
        "code": "CharField",
        "gst_code": "CharField"
      },
      "foreign_keys": {
        "country": "numbers_app_country"
      },
      "choices": {},
      "inferred_relationships": {}
    },
    "numbers_app_parentaccount": {
      "columns": {
        "id": "BigAutoField",
        "name": "CharField",
        "account_type": "CharField",
        "parent_account": "ForeignKey",
        "is_custom": "BooleanField",
        "account_number": "CharField",
        "business": "ForeignKey",
        "meta_data": "JSONField"
      },
      "foreign_keys": {
        "parent_account": "numbers_app_parentaccount",
        "business": "numbers_app_business"
      },
      "choices": {
        "account_type": {
          "ASSET": "Asset",
          "LIABILITY": "Liability",
          "INCOME": "Income",
          "EXPENSE": "Expense",
          "EQUITY": "Equity"
        }
      },
      "inferred_relationships": {},
      "description":"This model defines top-level financial account categories in a business’s chart of accounts. Relationships: 1.parent_account ForeignKey Allows accounts to be nested (tree structure) with Self-FK.2.business ForeignKey Indicates ownership of this account definition by a business."
    },
    "numbers_app_account": {
      "columns": {
        "id": "BigAutoField",
        "name": "CharField",
        "parent_account": "ForeignKey",
        "is_custom": "BooleanField"
      },
      "foreign_keys": {
        "parent_account": "numbers_app_parentaccount"
      },
      "choices": {},
      "inferred_relationships": {},
      "description": "This model represents individual financial accounts that belong to a broader Parent Account category. These are the leaf-level accounts used for tracking specific income, expenses, assets, etc., in accounting transactions. Relationships: 1. parent_account FK Every Account must be grouped under a ParentAccount, allowing roll-ups for reporting (like total expenses). 2. Via ParentAccount Inherited indirectly from ParentAccount.business. Accounts are implicitly scoped by business context.Examples: Parent Account Operating Expenses => Account like Travel, Meals, Office supplies Parent Account Income => Account like Product sales, Service income"
    },
    "numbers_app_business": {
      "columns": {
        "id": "BigAutoField",
        "logo": "FileField",
        "signature": "FileField",
        "legal_name": "CharField",
        "industry": "ForeignKey",
        "address_line1": "TextField",
        "address_line2": "TextField",
        "city": "CharField",
        "state": "ForeignKey",
        "zip_code": "CharField",
        "country": "ForeignKey",
        "currency": "ForeignKey",
        "financial_year_last_day": "DateTimeField",
        "number_of_employees": "BigIntegerField",
        "pan_number": "CharField",
        "phone_number": "CharField",
        "gstin_number": "CharField",
        "company_registration_number": "CharField",
        "fiscal_year": "ForeignKey",
        "time_zone": "ForeignKey",
        "date_format": "ForeignKey",
        "is_business_registered": "BooleanField",
        "customer": "ForeignKey",
        "migration_date": "DateField",
        "integration_mode": "CharField",
        "is_tally_sync_enabled": "BooleanField",
        "is_removed": "BooleanField",
        "meta_data": "JSONField",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField"
      },
      "foreign_keys": {
        "industry": "numbers_app_industry",
        "state": "numbers_app_state",
        "country": "numbers_app_country",
        "currency": "numbers_app_currency",
        "fiscal_year": "numbers_app_fiscalyear",
        "time_zone": "numbers_app_timezone",
        "date_format": "numbers_app_dateformat",
        "customer": "numbers_app_customer"
      },
      "choices": {
        "integration_mode": {
          "numbers": "numbers",
          "tally": "tally"
        }
      },
      "inferred_relationships": {},
      "description": "The Business model stores all the core details about a business or company, including contact info, 		compliance identifiers, financial settings, and integration preferences. This model is central to the entire accounting system — everything from user transactions to reporting and compliance links back to this model. Relationships: * Industry: Each business belongs to one Industry * State, Country, Currency: Linked to geo and finance reference data * FiscalYear, TimeZone, DateFormat: For proper reporting settings * Customer: Optionally associated with a customer record * Accounts: Through the ChartofAccount model (acts as the bridge between Business and individual accounts)"
    },
    "numbers_app_businesscontacts": {
      "columns": {
        "id": "BigAutoField",
        "business": "ForeignKey",
        "contact_type": "CharField",
        "first_name": "CharField",
        "last_name": "CharField",
        "email": "CharField",
        "mobile_number": "CharField"
      },
      "foreign_keys": {
        "business": "numbers_app_business"
      },
      "choices": {
        "contact_type": {
          "primary": "primary",
          "secondary": "Secondary"
        }
      },
      "inferred_relationships": {},
      "description": "Stores individual contact details associated with a specific business—useful for managing primary or secondary points of contact for that business. Relationships: business → ForeignKey to the Business model Each contact is linked to one business. A business can have multiple contacts (1-to-many)."
    },
    "numbers_app_userrole": {
      "columns": {
        "id": "BigAutoField"
      },
      "foreign_keys": {},
      "choices": {},
      "inferred_relationships": {}
    },
    "numbers_app_user": {
      "columns": {
        "id": "BigAutoField",
        "password": "CharField",
        "last_login": "DateTimeField",
        "is_superuser": "BooleanField",
        "email": "CharField",
        "name": "CharField",
        "first_name": "CharField",
        "last_name": "CharField",
        "gender": "CharField",
        "date_of_birth": "DateField",
        "country": "ForeignKey",
        "state": "ForeignKey",
        "city": "CharField",
        "zip_code": "CharField",
        "mobile_number": "CharField",
        "is_active": "BooleanField",
        "is_staff": "BooleanField",
        "user_role": "CharField",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField"
      },
      "foreign_keys": {
        "country": "numbers_app_country",
        "state": "numbers_app_state"
      },
      "choices": {
        "gender": {
          "male": "male",
          "female": "female",
          "other": "other"
        },
        "user_role": {
          "dashboard_user": "Dashboard Analyst",
          "regular_user": "Regular User"
        }
      },
      "inferred_relationships": {}
    },
    "numbers_app_customer": {
      "columns": {
        "id": "BigAutoField",
        "user": "ForeignKey",
        "business_limit": "PositiveIntegerField",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField"
      },
      "foreign_keys": {
        "user": "numbers_app_user"
      },
      "choices": {},
      "inferred_relationships": {},
      "description": "Represents a customer user account that can be associated with one or more businesses, while tracking limits and timestamps.Primarily used to extend user functionality for business management. business_limit can be used to implement plan-based restrictions (e.g., free vs premium users). Relationships: 1.user -> ForeignKey User. The user account for the customer."
    },
    "numbers_app_userbusinessrole": {
      "columns": {
        "id": "BigAutoField",
        "user": "ForeignKey",
        "business": "ForeignKey",
        "role": "CharField",
        "inviter": "ForeignKey",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField"
      },
      "foreign_keys": {
        "user": "numbers_app_user",
        "business": "numbers_app_business",
        "inviter": "numbers_app_user"
      },
      "choices": {
        "role": {
          "admin": "admin",
          "accountant": "accountant",
          "analyst": "analyst"
        }
      },
      "inferred_relationships": {}
    },
    "numbers_app_chartofaccount": {
      "columns": {
        "id": "BigAutoField",
        "business": "ForeignKey",
        "account": "ForeignKey",
        "balance_amount": "DecimalField",
        "opening_balance_date": "DateField",
        "meta_data": "JSONField",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField"
      },
      "foreign_keys": {
        "business": "numbers_app_business",
        "account": "numbers_app_account"
      },
      "choices": {},
      "inferred_relationships": {
        "parent_account": {
          "source_table": "numbers_app_chartofaccount",
          "source_column": "account",
          "target_table": "numbers_app_parentaccount",
          "target_column": "id",
          "through_table": "numbers_app_account",
          "through_column_source": "id",
          "through_column_target": "parent_account"
        }
      },
      "description": "This model links a specific account to a business, along with the account’s balance and other related info. 	It acts as a bridge table between Business and Account, representing how accounts are used by each business. Relationships: 1. business FK The business that owns/uses the account. 2. account FKThe actual financial account being used by this business. Constraints: unique_together = ('business', 'account')"
    },
    "numbers_app_journalentry": {
      "columns": {
        "id": "BigAutoField",
        "created_by": "ForeignKey",
        "updated_by": "ForeignKey",
        "business": "ForeignKey",
        "contra_entry_for": "ForeignKey",
        "is_contra": "BooleanField",
        "transaction_date": "DateTimeField",
        "note": "TextField",
        "description": "TextField",
        "transaction_amount": "DecimalField",
        "meta_data": "JSONField",
        "is_posted": "BooleanField",
        "is_removed": "BooleanField",
        "source": "CharField",
        "currency": "ForeignKey",
        "attachment": "FileField",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField"
      },
      "foreign_keys": {
        "created_by": "numbers_app_user",
        "updated_by": "numbers_app_user",
        "business": "numbers_app_business",
        "contra_entry_for": "numbers_app_journalentry",
        "currency": "numbers_app_currency"
      },
      "choices": {
        "source": {
          "manual": "Manual",
          "uncategorized": "Uncategorized",
          "statement": "Statement",
          "invoice": "Invoice",
          "bill": "Bill",
          "payment": "Payment",
          "opening_balance": "Opening Balance",
          "customer_opening_balance": "Customer Opening Balance",
          "vendor_opening_balance": "Vendor Opening Balance",
          "credit_note_refund": "Credit Notes Refund",
          "credit_note": "Credit Note",
          "refund_payment": "Refund Payment"
        }
      },
      "inferred_relationships": {},
      "description": "This model represents a financial transaction entry in the system — like recording income, expenses, 		adjustments, etc. Each entry includes who created it, what business it belongs to, how much it was for, and other contextual data. Relationships: 1. The user who created this journal entry. 2. The user who last updated the entry (can be null). 3. The business this journal entry belongs to.4. A link to another journal entry if this is a contra entry (a reversing or balancing entry). 5. The currency used in the transaction (e.g., USD, EUR). User ↔ JournalEntry ↔ Business ↔ Currency Fields:  transaction_amount: The amount involved in this journal entry. transaction_date: When the transaction occurred. is_contra: Indicates if this entry is a contra (reverse) transaction. is_removed: Soft delete flag."
    },
    "numbers_app_transaction": {
      "columns": {
        "id": "BigAutoField",
        "journal_entry": "ForeignKey",
        "business_account": "ForeignKey",
        "amount": "DecimalField",
        "transaction_type": "CharField",
        "currency": "ForeignKey"
      },
      "foreign_keys": {
        "journal_entry": "numbers_app_journalentry",
        "business_account": "numbers_app_chartofaccount",
        "currency": "numbers_app_currency"
      },
      "choices": {
        "transaction_type": {
          "DEBIT": "Dr",
          "CREDIT": "Cr"
        }
      },
      "inferred_relationships": {
        "account_type": {
          "source_table": "numbers_app_transaction",
          "source_column": "business_account",
          "target_table": "numbers_app_parentaccount",
          "target_column": "account_type",
          "through_table": "numbers_app_chartofaccount",
          "through_column_source": "id",
          "through_column_target": "account"
        }
      },
      "description": "This model represents an individual debit or credit entry that is part of a JournalEntry. Each JournalEntry 	can have multiple Transactions (i.e., multiple lines in an accounting entry, like a typical double-entry bookkeeping system). Relationships: 1. journal_entry(JournalEntry) Links the transaction to a specific journal entry (like a header). 2.business_account(ChartofAccount) Specifies the account (like Cash, Revenue, Expense) the transaction 	affects. JournalEntry ➝ Transaction ➝ ChartofAccount ➝ Account ➝ ParentAccount"
    },
    "numbers_app_chartofaccountstemplates": {
      "columns": {
        "id": "BigAutoField",
        "industry": "ForeignKey"
      },
      "foreign_keys": {
        "industry": "numbers_app_industry"
      },
      "choices": {},
      "inferred_relationships": {}
    },
    "numbers_app_dynamicmapping": {
      "columns": {
        "id": "BigAutoField",
        "business": "ForeignKey",
        "name": "CharField",
        "description": "TextField",
        "mapping_for": "CharField",
        "created_by": "ForeignKey",
        "updated_by": "ForeignKey",
        "mapping": "TextField",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField"
      },
      "foreign_keys": {
        "business": "numbers_app_business",
        "created_by": "numbers_app_user",
        "updated_by": "numbers_app_user"
      },
      "choices": {
        "mapping_for": {
          "sourced_transactions": "Sourced Transaction",
          "journal_entry": "Journal Entry",
          "opening_balance": "Opening Balance",
          "customer": "Customer",
          "vendor": "Vendor",
          "item": "Item"
        }
      },
      "inferred_relationships": {}
    },
    "numbers_app_sourcedtransactionsfile": {
      "columns": {
        "id": "BigAutoField",
        "business": "ForeignKey",
        "statement_file": "FileField",
        "created_at": "DateTimeField"
      },
      "foreign_keys": {
        "business": "numbers_app_business"
      },
      "choices": {},
      "inferred_relationships": {}
    },
    "numbers_app_sourcedtransactions": {
      "columns": {
        "id": "BigAutoField",
        "business": "ForeignKey",
        "statement_file": "ForeignKey",
        "transaction_date": "DateTimeField",
        "value_date": "DateTimeField",
        "description": "TextField",
        "reference_number": "CharField",
        "credit_amount": "DecimalField",
        "debit_amount": "DecimalField",
        "balance": "DecimalField",
        "journal_entry": "OneToOneField",
        "mapping_used": "ForeignKey",
        "source": "CharField",
        "is_removed": "BooleanField",
        "created_by": "ForeignKey",
        "updated_by": "ForeignKey",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField"
      },
      "foreign_keys": {
        "business": "numbers_app_business",
        "statement_file": "numbers_app_sourcedtransactionsfile",
        "journal_entry": "numbers_app_journalentry",
        "mapping_used": "numbers_app_dynamicmapping",
        "created_by": "numbers_app_user",
        "updated_by": "numbers_app_user"
      },
      "choices": {
        "source": {
          "manual": "Manual",
          "uncategorized": "Uncategorized",
          "statement": "Statement",
          "invoice": "Invoice",
          "bill": "Bill",
          "payment": "Payment",
          "opening_balance": "Opening Balance",
          "customer_opening_balance": "Customer Opening Balance",
          "vendor_opening_balance": "Vendor Opening Balance",
          "credit_note_refund": "Credit Notes Refund",
          "credit_note": "Credit Note",
          "refund_payment": "Refund Payment"
        }
      },
      "inferred_relationships": {}
    },
    "numbers_app_sourcedtransactionpreference": {
      "columns": {
        "id": "BigAutoField",
        "business": "ForeignKey",
        "name": "CharField",
        "description": "TextField",
        "transaction_type": "CharField",
        "note": "TextField",
        "debit_account": "ForeignKey",
        "credit_account": "ForeignKey",
        "currency": "ForeignKey",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField"
      },
      "foreign_keys": {
        "business": "numbers_app_business",
        "debit_account": "numbers_app_chartofaccount",
        "credit_account": "numbers_app_chartofaccount",
        "currency": "numbers_app_currency"
      },
      "choices": {
        "transaction_type": {
          "DEBIT": "Dr",
          "CREDIT": "Cr"
        }
      },
      "inferred_relationships": {}
    },
    "numbers_app_partyaddress": {
      "columns": {
        "id": "BigAutoField",
        "business": "ForeignKey",
        "address_type": "CharField",
        "address_line1": "TextField",
        "address_line2": "TextField",
        "country": "CharField",
        "city": "CharField",
        "state": "CharField",
        "zip_code": "CharField",
        "contact_number": "CharField",
        "created_by": "ForeignKey",
        "updated_by": "ForeignKey",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField"
      },
      "foreign_keys": {
        "business": "numbers_app_business",
        "created_by": "numbers_app_user",
        "updated_by": "numbers_app_user"
      },
      "choices": {
        "address_type": {
          "billing": "Billing",
          "shipping": "Shipping"
        }
      },
      "inferred_relationships": {}
    },
    "numbers_app_paymentterms": {
      "columns": {
        "id": "BigAutoField",
        "business": "ForeignKey",
        "name": "CharField",
        "number_of_days": "IntegerField",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField"
      },
      "foreign_keys": {
        "business": "numbers_app_business"
      },
      "choices": {},
      "inferred_relationships": {}
    },
    "numbers_app_party": {
      "columns": {
        "id": "BigAutoField",
        "role": "CharField",
        "party_type": "CharField",
        "primary_contact_name": "CharField",
        "company_name": "CharField",
        "display_name": "CharField",
        "email": "CharField",
        "phone_number": "CharField",
        "fax_number": "CharField",
        "website": "CharField",
        "PAN": "CharField",
        "currency": "ForeignKey",
        "preferred_payment_method": "CharField",
        "opening_balance": "DecimalField",
        "opening_balance_transaction_type": "CharField",
        "opening_balance_as_on_date": "DateTimeField",
        "payment_term": "ForeignKey",
        "billing_address": "ForeignKey",
        "shipping_address": "ForeignKey",
        "gstin": "CharField",
        "tpin": "CharField",
        "gst_registration_type": "CharField",
        "account": "ForeignKey",
        "other_details": "TextField",
        "is_inactive": "BooleanField",
        "is_tds_applicable": "BooleanField",
        "note": "TextField",
        "business": "ForeignKey",
        "opening_balance_journal_entry": "ForeignKey",
        "created_by": "ForeignKey",
        "updated_by": "ForeignKey",
        "attachment": "FileField",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField",
        "meta_data": "JSONField"
      },
      "foreign_keys": {
        "currency": "numbers_app_currency",
        "payment_term": "numbers_app_paymentterms",
        "billing_address": "numbers_app_partyaddress",
        "shipping_address": "numbers_app_partyaddress",
        "account": "numbers_app_chartofaccount",
        "business": "numbers_app_business",
        "opening_balance_journal_entry": "numbers_app_journalentry",
        "created_by": "numbers_app_user",
        "updated_by": "numbers_app_user"
      },
      "choices": {
        "role": {
          "customer": "customer",
          "vendor": "vendor"
        },
        "party_type": {
          "business": "Business",
          "individual": "Individual"
        },
        "preferred_payment_method": {
          "cash": "Cash",
          "bank_transfer": "Bank Transfer",
          "cheque": "Cheque",
          "upi": "UPI",
          "card": "Card",
          "net_banking": "Net Banking"
        },
        "opening_balance_transaction_type": {
          "CREDIT": "CREDIT",
          "DEBIT": "DEBIT"
        }
      },
      "inferred_relationships": {},
      "description": "The Party model represents an entity the business interacts with—either a customer or a vendor. It stores comprehensive details about the party including identification, contact info, financial settings, payment preferences, and taxation details.Used across modules like invoices, payments, purchases, and receipts, this model acts as a central node for any party-related transaction or ledger entry in the system. Relationships: 1.business →ForeignKey Business. Associates the party with a specific business 2.account →ForeignKey ChartofAccount. Ledger account associated with this party 3.opening_balance_journal_entry →ForeignKey JournalEntry. Journal entry linked to the party’s opening balance 4.created_by, updated_by →ForeignKey User. Tracks who created or updated the party"
    },
    "numbers_app_partyattachment": {
      "columns": {
        "id": "BigAutoField",
        "business": "ForeignKey",
        "party": "ForeignKey",
        "attachment": "FileField",
        "is_removed": "BooleanField"
      },
      "foreign_keys": {
        "business": "numbers_app_business",
        "party": "numbers_app_party"
      },
      "choices": {},
      "inferred_relationships": {}
    },
    "numbers_app_partycontacts": {
      "columns": {
        "id": "BigAutoField",
        "party": "ForeignKey",
        "contact_type": "CharField",
        "salutation": "CharField",
        "first_name": "CharField",
        "middle_name": "CharField",
        "last_name": "CharField",
        "name": "CharField",
        "email": "CharField",
        "mobile_number": "CharField",
        "created_by": "ForeignKey",
        "updated_by": "ForeignKey",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField"
      },
      "foreign_keys": {
        "party": "numbers_app_party",
        "created_by": "numbers_app_user",
        "updated_by": "numbers_app_user"
      },
      "choices": {
        "contact_type": {
          "primary": "primary",
          "sales_person": "sales_person",
          "secondary": "secondary"
        }
      },
      "inferred_relationships": {}
    },
    "numbers_app_units": {
      "columns": {
        "id": "BigAutoField",
        "name": "CharField",
        "code": "CharField",
        "uqc": "CharField"
      },
      "foreign_keys": {},
      "choices": {
        "uqc": {
          "BAG": "Bags (BAG)",
          "BAL": "Bale (BAL)",
          "BDL": "Bundles (BDL)",
          "BKL": "Buckles (BKL)",
          "BOU": "Billions of Units (BOU)",
          "BOX": "Box (BOX)",
          "BTL": "Bottles (BTL)",
          "BUN": "Bunches (BUN)",
          "CAN": "Cans (CAN)",
          "CBM": "Cubic Meter (CBM)",
          "CCM": "Cubic Centimeter (CCM)",
          "CMS": "Centimeter (CMS)",
          "CTN": "Cartons (CTN)",
          "DOZ": "Dozen (DOZ)",
          "DRM": "Drum (DRM)",
          "GGR": "Great Gross (GGR)",
          "GMS": "Grams (GMS)",
          "GRS": "Gross (GRS)",
          "GYD": "Gross Yards (GYD)",
          "KGS": "Kilograms (KGS)",
          "KLR": "Kilolitre (KLR)",
          "KME": "Kilometre (KME)",
          "MLT": "Millilitre (MLT)",
          "MTR": "Meters (MTR)",
          "MTS": "Metric Ton (MTS)",
          "NOS": "Numbers (NOS)",
          "PAC": "Packs (PAC)",
          "PCS": "Pieces (PCS)",
          "PRS": "Pairs (PRS)",
          "QTL": "Quintal (QTL)",
          "ROL": "Rolls (ROL)",
          "SET": "Sets (SET)",
          "SQF": "Square Feet (SQF)",
          "SQM": "Square Meters (SQM)",
          "SQY": "Square Yards (SQY)",
          "TBS": "Tablets (TBS)",
          "TGM": "Ten Grams (TGM)",
          "THD": "Thousands (THD)",
          "TON": "Tonnes (TON)",
          "TUB": "Tubes (TUB)",
          "UGS": "US Gallons (UGS)",
          "UNT": "Units (UNT)",
          "YDS": "Yards (YDS)",
          "OTH": "Others (OTH)"
        }
      },
      "inferred_relationships": {}
    },
    "numbers_app_tdstcssection": {
      "columns": {
        "id": "BigAutoField",
        "name": "CharField",
        "formatted_name": "CharField",
        "tax_name": "CharField",
        "tax_type": "CharField"
      },
      "foreign_keys": {},
      "choices": {
        "tax_type": {
          "tcs": "TCS",
          "tds": "TDS"
        }
      },
      "inferred_relationships": {}
    },
    "numbers_app_tdstcsdetails": {
      "columns": {
        "id": "BigAutoField",
        "business": "ForeignKey",
        "name": "CharField",
        "rate": "DecimalField",
        "section": "ForeignKey",
        "payable_account": "ForeignKey",
        "receivable_account": "ForeignKey",
        "is_rate_high": "BooleanField",
        "is_custom": "BooleanField",
        "is_inactive": "BooleanField"
      },
      "foreign_keys": {
        "business": "numbers_app_business",
        "section": "numbers_app_tdstcssection",
        "payable_account": "numbers_app_chartofaccount",
        "receivable_account": "numbers_app_chartofaccount"
      },
      "choices": {},
      "inferred_relationships": {}
    },
    "numbers_app_tax": {
      "columns": {
        "id": "BigAutoField",
        "business": "ForeignKey",
        "tax_type": "CharField",
        "rate": "DecimalField",
        "name": "CharField",
        "is_custom": "BooleanField",
        "is_removed": "BooleanField",
        "created_by": "ForeignKey",
        "updated_by": "ForeignKey",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField"
      },
      "foreign_keys": {
        "business": "numbers_app_business",
        "created_by": "numbers_app_user",
        "updated_by": "numbers_app_user"
      },
      "choices": {
        "tax_type": {
          "GST": "GST",
          "IGST": "IGST",
          "CESS": "CESS"
        }
      },
      "inferred_relationships": {}
    },
    "numbers_app_items": {
      "columns": {
        "id": "BigAutoField",
        "item_type": "CharField",
        "name": "CharField",
        "description": "TextField",
        "unit": "ForeignKey",
        "for_purchase": "BooleanField",
        "for_sales": "BooleanField",
        "is_purchase_inclusive": "BooleanField",
        "is_sales_inclusive": "BooleanField",
        "hsn_sac_code": "CharField",
        "cost_price": "DecimalField",
        "selling_price": "DecimalField",
        "purchase_account": "ForeignKey",
        "sales_account": "ForeignKey",
        "tax": "ForeignKey",
        "gst_rate": "DecimalField",
        "cess_rate": "DecimalField",
        "business": "ForeignKey",
        "opening_stock": "DecimalField",
        "current_stock": "DecimalField",
        "as_of_date": "DateTimeField",
        "is_low_stock_reminder_active": "BooleanField",
        "low_stock_value": "DecimalField",
        "stock_item_code": "CharField",
        "is_removed": "BooleanField",
        "created_by": "ForeignKey",
        "updated_by": "ForeignKey",
        "attachment": "FileField",
        "is_low_stock_reminder_sent": "BooleanField",
        "is_negative_stock_reminder_sent": "BooleanField",
        "meta_data": "JSONField",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField"
      },
      "foreign_keys": {
        "unit": "numbers_app_units",
        "purchase_account": "numbers_app_chartofaccount",
        "sales_account": "numbers_app_chartofaccount",
        "tax": "numbers_app_tax",
        "business": "numbers_app_business",
        "created_by": "numbers_app_user",
        "updated_by": "numbers_app_user"
      },
      "choices": {
        "item_type": {
          "goods": "Goods",
          "service": "Service"
        }
      },
      "inferred_relationships": {},
      "description": "The Items model represents products or services available for purchase, sale, or inventory management 	within a business. It supports detailed tracking of pricing, taxation, stock levels, and classification. Sales or 	purchase invoices. Inventory and stock tracking. Tax-inclusive/inventory alert systems. Relationships: 1.business →ForeignKey Business. Business to which this item belongs 2.purchase_account, sales_account →ForeignKey ChartofAccount. Linked accounts for purchase/sales transactions 3.created_by, updated_by  →ForeignKey User. User audit tracking"
    },
    "numbers_app_itemstockadjustment": {
      "columns": {
        "id": "BigAutoField",
        "item": "ForeignKey",
        "is_stock_in": "BooleanField",
        "reason": "TextField",
        "adjustment_date": "DateTimeField",
        "stock_adjustment_value": "DecimalField",
        "is_removed": "BooleanField",
        "is_manual": "BooleanField",
        "created_by": "ForeignKey",
        "updated_by": "ForeignKey",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField"
      },
      "foreign_keys": {
        "item": "numbers_app_items",
        "created_by": "numbers_app_user",
        "updated_by": "numbers_app_user"
      },
      "choices": {},
      "inferred_relationships": {}
    },
    "numbers_app_itemattachment": {
      "columns": {
        "id": "BigAutoField",
        "business": "ForeignKey",
        "item": "ForeignKey",
        "attachment": "FileField",
        "is_removed": "BooleanField"
      },
      "foreign_keys": {
        "business": "numbers_app_business",
        "item": "numbers_app_items"
      },
      "choices": {},
      "inferred_relationships": {}
    },
    "numbers_app_termsandconditions": {
      "columns": {
        "id": "BigAutoField",
        "name": "CharField",
        "content": "TextField",
        "business": "ForeignKey",
        "created_by": "ForeignKey",
        "updated_by": "ForeignKey",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField"
      },
      "foreign_keys": {
        "business": "numbers_app_business",
        "created_by": "numbers_app_user",
        "updated_by": "numbers_app_user"
      },
      "choices": {},
      "inferred_relationships": {}
    },
    "numbers_app_salesperson": {
      "columns": {
        "id": "BigAutoField",
        "business": "ForeignKey",
        "first_name": "CharField",
        "last_name": "CharField",
        "email": "CharField"
      },
      "foreign_keys": {
        "business": "numbers_app_business"
      },
      "choices": {},
      "inferred_relationships": {},
      "description": "Represents a sales representative associated with a specific business, primarily used for tracking sales activities or assignments. Assigning sales reps to customers, invoices, or deals. Tracking sales performance or lead ownership. Email communication with sales contacts Relationships: 1.business →ForeignKey Business. Links the salesperson to a specific business entity"
    },
    "numbers_app_recurringinvoice": {
      "columns": {
        "business": "ForeignKey",
        "profile_name": "CharField",
        "repeat_every": "IntegerField",
        "repeat_frequency": "CharField",
        "preference": "CharField",
        "invoice_data": "JSONField",
        "customer": "ForeignKey",
        "attachment": "FileField",
        "starts_on": "DateTimeField",
        "ends_on": "DateTimeField",
        "never_expires": "BooleanField",
        "is_active": "BooleanField",
        "periodic_task": "OneToOneField",
        "is_removed": "BooleanField",
        "created_by": "ForeignKey",
        "updated_by": "ForeignKey",
        "last_run_at": "DateTimeField",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField"
      },
      "foreign_keys": {
        "business": "numbers_app_business",
        "customer": "numbers_app_party",
        "periodic_task": "django_celery_beat_periodictask",
        "created_by": "numbers_app_user",
        "updated_by": "numbers_app_user"
      },
      "choices": {
        "repeat_frequency": {
          "day": "Day(s)",
          "week": "Week(s)",
          "month": "Month(s)",
          "year": "Year(s)"
        },
        "preference": {
          "create_and_draft": "Create Invoices as Drafts",
          "create_and_send": "Create and Send Invoices",
          "create_and_save": "Create and save"
        }
      },
      "inferred_relationships": {},
      "description": "This model defines automated, repeating invoices for customers based on a schedule.Manages invoice 	templates that generate recurring invoices.Stores frequency, schedule, and preferences for automated 	billing.Tracks lifecycle (start, end, status) and history of recurring invoices. Relationships: 1.business -> ForeignKey Business. the owning business. 2.customer  -> ForeignKey Customer. the recipient party."
    },
    "numbers_app_invoice": {
      "columns": {
        "id": "BigAutoField",
        "business": "ForeignKey",
        "business_address": "JSONField",
        "journal_entry": "ForeignKey",
        "invoice_title": "CharField",
        "invoice_sub_heading": "CharField",
        "customer": "ForeignKey",
        "customer_emails": "JSONField",
        "invoice_number": "CharField",
        "invoice_date": "DateTimeField",
        "due_date": "DateTimeField",
        "order_number": "CharField",
        "payment_term": "ForeignKey",
        "sales_person": "ForeignKey",
        "place_of_supply": "JSONField",
        "tax_applied": "CharField",
        "terms_and_conditions": "ForeignKey",
        "payment_status": "CharField",
        "payment_method": "CharField",
        "received_payment_amount": "DecimalField",
        "last_payment_date": "DateTimeField",
        "shipping_address": "TextField",
        "billing_address": "TextField",
        "attachment": "FileField",
        "note": "TextField",
        "subtotal": "DecimalField",
        "discount": "DecimalField",
        "tds_tcs": "ForeignKey",
        "tds_tcs_choice": "CharField",
        "tds_tcs_amount": "DecimalField",
        "tax": "JSONField",
        "total_amount": "DecimalField",
        "is_draft": "BooleanField",
        "is_pro_forma": "BooleanField",
        "is_sent": "BooleanField",
        "is_pro_forma_sent": "BooleanField",
        "is_removed": "BooleanField",
        "reason_for_update": "TextField",
        "created_by": "ForeignKey",
        "updated_by": "ForeignKey",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField",
        "currency": "ForeignKey",
        "exchange_rate": "DecimalField",
        "is_recurring": "BooleanField",
        "recurring_invoice": "ForeignKey"
      },
      "foreign_keys": {
        "business": "numbers_app_business",
        "journal_entry": "numbers_app_journalentry",
        "customer": "numbers_app_party",
        "payment_term": "numbers_app_paymentterms",
        "sales_person": "numbers_app_salesperson",
        "terms_and_conditions": "numbers_app_termsandconditions",
        "tds_tcs": "numbers_app_tdstcsdetails",
        "created_by": "numbers_app_user",
        "updated_by": "numbers_app_user",
        "currency": "numbers_app_currency",
        "recurring_invoice": "numbers_app_recurringinvoice"
      },
      "choices": {
        "tax_applied": {
          "inclusive": "Inclusive",
          "exclusive": "Exclusive",
          "no_tax": "No Tax"
        },
        "payment_status": {
          "paid": "Paid",
          "unpaid": "Unpaid",
          "partially_paid": "Partially Paid"
        },
        "payment_method": {
          "cash": "Cash",
          "bank_transfer": "Bank Transfer",
          "cheque": "Cheque",
          "upi": "UPI",
          "card": "Card",
          "net_banking": "Net Banking"
        },
        "tds_tcs_choice": {
          "tds": "TDS",
          "tcs": "TCS",
          "no_tax": "No Tax"
        }
      },
      "inferred_relationships": {},
      "description": "This model represents a sales invoice generated by a business for a customer, capturing all transactional, tax, and accounting details.Records invoice details for goods/services sold.Tracks payments, taxes, discounts, and TDS/TCS. Supports multi-currency invoicing, recurring billing, and credit note adjustments. Relationships: 1.business -> ForeignKey Business. issuing business. 2.customer  -> ForeignKey Customer. party being invoiced. 3.journal_entry ->  ForeignKey JournalEntry.links to accounting journal. 4.recurring_invoice ->	ForeignKey RecurringInvoice.links to recurring template, if applicable."
    },
    "numbers_app_creditnoteinvoicepayment": {
      "columns": {
        "id": "BigAutoField",
        "invoice": "ForeignKey",
        "credit_note": "ForeignKey",
        "credit_amount_applied": "DecimalField"
      },
      "foreign_keys": {
        "invoice": "numbers_app_invoice",
        "credit_note": "numbers_app_creditnote"
      },
      "choices": {},
      "inferred_relationships": {}
    },
    "numbers_app_excesspaymentinvoicepayment": {
      "columns": {
        "id": "BigAutoField",
        "invoice": "ForeignKey",
        "customer": "ForeignKey",
        "journal_entry": "ForeignKey",
        "payment_date": "DateTimeField",
        "is_removed": "BooleanField",
        "credit_amount_applied": "DecimalField"
      },
      "foreign_keys": {
        "invoice": "numbers_app_invoice",
        "customer": "numbers_app_party",
        "journal_entry": "numbers_app_journalentry"
      },
      "choices": {},
      "inferred_relationships": {}
    },
    "numbers_app_taxdetail": {
      "columns": {
        "id": "BigAutoField",
        "short_name": "CharField",
        "tax": "ForeignKey",
        "tax_account": "CharField",
        "rate": "DecimalField"
      },
      "foreign_keys": {
        "tax": "numbers_app_tax"
      },
      "choices": {
        "tax_account": {
          "CGST": "CGST",
          "SGST": "SGST",
          "IGST": "IGST"
        }
      },
      "inferred_relationships": {}
    },
    "numbers_app_invoiceitems": {
      "columns": {
        "id": "BigAutoField",
        "item_order": "IntegerField",
        "item": "ForeignKey",
        "description": "TextField",
        "expense_category": "ForeignKey",
        "quantity": "DecimalField",
        "unit": "ForeignKey",
        "rate": "DecimalField",
        "tax": "ForeignKey",
        "item_level_discount": "DecimalField",
        "is_item_discount_in_percentage": "BooleanField",
        "amount": "DecimalField",
        "sales_invoice": "ForeignKey"
      },
      "foreign_keys": {
        "item": "numbers_app_items",
        "expense_category": "numbers_app_chartofaccount",
        "unit": "numbers_app_units",
        "tax": "numbers_app_tax",
        "sales_invoice": "numbers_app_invoice"
      },
      "choices": {},
      "inferred_relationships": {},
      "description": "This model captures line item details within a sales invoice, representing individual goods or services billed. Represents each itemized entry in a sales invoice.Supports discounts at the item level, not just invoice level.Helps in financial reporting by mapping items to Chart of Accounts.Tracks tax per item for granular taxation. Relationships: 1.sales_invoice → ForeignKey Invoice. parent Invoice to which the item belongs. 2.item → ForeignKey Item. reference to the product/service being billed. 3.expense_category → ForeignKey ChartofAccount. account categorization (e.g., for cost tracking)."
    },
    "numbers_app_hsnsaccode": {
      "columns": {
        "id": "BigAutoField",
        "item_type": "CharField",
        "hsn_sac_code": "CharField",
        "gst_rate": "DecimalField",
        "description": "TextField"
      },
      "foreign_keys": {},
      "choices": {
        "item_type": {
          "goods": "Goods",
          "service": "Service"
        }
      },
      "inferred_relationships": {}
    },
    "numbers_app_bill": {
      "columns": {
        "id": "BigAutoField",
        "business": "ForeignKey",
        "business_address": "JSONField",
        "journal_entry": "ForeignKey",
        "bill_title": "CharField",
        "bill_sub_heading": "CharField",
        "vendor": "ForeignKey",
        "order_number": "CharField",
        "bill_number": "CharField",
        "bill_date": "DateTimeField",
        "due_date": "DateTimeField",
        "payment_term": "ForeignKey",
        "source_of_supply": "JSONField",
        "tax_applied": "CharField",
        "payment_status": "CharField",
        "payment_method": "CharField",
        "paid_payment_amount": "DecimalField",
        "last_payment_date": "DateTimeField",
        "mailing_address": "TextField",
        "attachment": "FileField",
        "note": "TextField",
        "subtotal": "DecimalField",
        "discount": "DecimalField",
        "tax": "JSONField",
        "tds_tcs": "ForeignKey",
        "tds_tcs_choice": "CharField",
        "tds_tcs_amount": "DecimalField",
        "total_amount": "DecimalField",
        "is_draft": "BooleanField",
        "is_removed": "BooleanField",
        "has_rcm": "BooleanField",
        "reason_for_update": "TextField",
        "created_by": "ForeignKey",
        "updated_by": "ForeignKey",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField",
        "currency": "ForeignKey",
        "exchange_rate": "DecimalField"
      },
      "foreign_keys": {
        "business": "numbers_app_business",
        "journal_entry": "numbers_app_journalentry",
        "vendor": "numbers_app_party",
        "payment_term": "numbers_app_paymentterms",
        "tds_tcs": "numbers_app_tdstcsdetails",
        "created_by": "numbers_app_user",
        "updated_by": "numbers_app_user",
        "currency": "numbers_app_currency"
      },
      "choices": {
        "tax_applied": {
          "inclusive": "Inclusive",
          "exclusive": "Exclusive",
          "no_tax": "No Tax"
        },
        "payment_status": {
          "paid": "Paid",
          "unpaid": "Unpaid",
          "partially_paid": "Partially Paid"
        },
        "payment_method": {
          "cash": "Cash",
          "bank_transfer": "Bank Transfer",
          "cheque": "Cheque",
          "upi": "UPI",
          "card": "Card",
          "net_banking": "Net Banking"
        },
        "tds_tcs_choice": {
          "tds": "TDS",
          "tcs": "TCS",
          "no_tax": "No Tax"
        }
      },
      "inferred_relationships": {},
      "description": "Represents a purchase bill issued by a vendor to a business, including line items, tax details, payment info, and accounting linkage. Stores detailed tax breakdown (CGST, SGST, IGST) in JSON. Allows linking multiple DebitNotes for partial/full payments. Relationships: 1.business (ForeignKey → Business) The business receiving the bill. 2.journal_entry (ForeignKey → JournalEntry) Links the bill to its accounting entry. 3.vendor (ForeignKey → Party) The vendor issuing the bill. 4.created_by (ForeignKey → User) User who created the bill. A Bill is a central document in purchase workflows. Closely tied to accounting (JournalEntry) and reporting (via Tax, Currency, etc.). Each bill can have multiple BillItems (linked by purchase_bill in BillItems model)."
    },
    "numbers_app_debitnotebillpayment": {
      "columns": {
        "id": "BigAutoField",
        "bill": "ForeignKey",
        "debit_note": "ForeignKey",
        "credit_amount_applied": "DecimalField"
      },
      "foreign_keys": {
        "bill": "numbers_app_bill",
        "debit_note": "numbers_app_debitnote"
      },
      "choices": {},
      "inferred_relationships": {}
    },
    "numbers_app_billitems": {
      "columns": {
        "id": "BigAutoField",
        "item_order": "IntegerField",
        "item": "ForeignKey",
        "description": "TextField",
        "expense_category": "ForeignKey",
        "quantity": "DecimalField",
        "unit": "ForeignKey",
        "rate": "DecimalField",
        "tax": "ForeignKey",
        "item_level_discount": "DecimalField",
        "is_item_discount_in_percentage": "BooleanField",
        "amount": "DecimalField",
        "purchase_bill": "ForeignKey"
      },
      "foreign_keys": {
        "item": "numbers_app_items",
        "expense_category": "numbers_app_chartofaccount",
        "unit": "numbers_app_units",
        "tax": "numbers_app_tax",
        "purchase_bill": "numbers_app_bill"
      },
      "choices": {},
      "inferred_relationships": {},
      "description": "Represents individual line items in a purchase bill, detailing product/service purchased, pricing, quantity, tax, and expense classification. Each BillItems entry belongs to a single Bill but can reference various other 	models like Items, Units, and Tax. Supports flexible discounting and tax per item. Ideal for detailed purchase bill records with accounting and inventory linkage. Relationships: 1.item ForeignKey → Items The product or service purchased. 2.expense_category ForeignKey → ChartofAccount The account under which this item’s expense is categorized. 3.purchase_bill ForeignKey → Bill The bill to which this item belongs"
    },
    "numbers_app_excesspaymentbillpayment": {
      "columns": {
        "id": "BigAutoField",
        "bill": "ForeignKey",
        "vendor": "ForeignKey",
        "journal_entry": "ForeignKey",
        "payment_date": "DateTimeField",
        "is_removed": "BooleanField",
        "credit_amount_applied": "DecimalField"
      },
      "foreign_keys": {
        "bill": "numbers_app_bill",
        "vendor": "numbers_app_party",
        "journal_entry": "numbers_app_journalentry"
      },
      "choices": {},
      "inferred_relationships": {}
    },
    "numbers_app_salesorder": {
      "columns": {
        "id": "BigAutoField",
        "business": "ForeignKey",
        "business_address": "JSONField",
        "customer": "ForeignKey",
        "customer_emails": "JSONField",
        "sales_order_number": "CharField",
        "sales_order_date": "DateTimeField",
        "expected_shipment_date": "DateTimeField",
        "reference_number": "CharField",
        "payment_term": "ForeignKey",
        "sales_person": "ForeignKey",
        "place_of_supply": "JSONField",
        "tax_applied": "CharField",
        "terms_and_conditions": "ForeignKey",
        "invoice": "ForeignKey",
        "shipping_address": "TextField",
        "billing_address": "TextField",
        "delivery_method": "CharField",
        "attachment": "FileField",
        "note": "TextField",
        "subtotal": "DecimalField",
        "discount": "DecimalField",
        "tax": "JSONField",
        "total_amount": "DecimalField",
        "is_draft": "BooleanField",
        "is_sent": "BooleanField",
        "is_removed": "BooleanField",
        "is_converted_to_invoice": "BooleanField",
        "created_by": "ForeignKey",
        "updated_by": "ForeignKey",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField",
        "currency": "ForeignKey",
        "exchange_rate": "DecimalField"
      },
      "foreign_keys": {
        "business": "numbers_app_business",
        "customer": "numbers_app_party",
        "payment_term": "numbers_app_paymentterms",
        "sales_person": "numbers_app_salesperson",
        "terms_and_conditions": "numbers_app_termsandconditions",
        "invoice": "numbers_app_invoice",
        "created_by": "numbers_app_user",
        "updated_by": "numbers_app_user",
        "currency": "numbers_app_currency"
      },
      "choices": {
        "tax_applied": {
          "inclusive": "Inclusive",
          "exclusive": "Exclusive",
          "no_tax": "No Tax"
        }
      },
      "inferred_relationships": {},
      "description": "Represents a sales order issued by a business to a customer, detailing product/service commitments, delivery expectations, and financial terms.Captures customer commitments before invoicing.Acts as a preliminary agreement outlining products/services to be delivered and terms. Relationships: 1.business -> ForeignKey Business. issuing business. 2.customer  -> ForeignKey Customer. party receiving the order. 3.invoice ->  ForeignKey Invoice. linked invoice if the order is converted. 4.created_by / updated_by → ForeignKey User.  users managing the order. "
    },
    "numbers_app_salesorderitems": {
      "columns": {
        "id": "BigAutoField",
        "item_order": "IntegerField",
        "item": "ForeignKey",
        "description": "TextField",
        "quantity": "DecimalField",
        "unit": "ForeignKey",
        "rate": "DecimalField",
        "tax": "ForeignKey",
        "item_level_discount": "DecimalField",
        "is_item_discount_in_percentage": "BooleanField",
        "amount": "DecimalField",
        "sales_order": "ForeignKey"
      },
      "foreign_keys": {
        "item": "numbers_app_items",
        "unit": "numbers_app_units",
        "tax": "numbers_app_tax",
        "sales_order": "numbers_app_salesorder"
      },
      "choices": {},
      "inferred_relationships": {},
      "description": "Represents individual line items listed in a SalesOrder. Each instance corresponds to a specific product/service ordered by the customer. Tracks the items and associated details in a sales order. Relationships: 1.item → ForeignKey Item. the product or service being ordered. 2.sales_order →ForeignKey SalesOrder. parent order to which this item belongs."
    },
    "numbers_app_purchaseorder": {
      "columns": {
        "id": "BigAutoField",
        "business": "ForeignKey",
        "business_address": "JSONField",
        "vendor": "ForeignKey",
        "vendor_emails": "JSONField",
        "purchase_order_number": "CharField",
        "purchase_order_date": "DateTimeField",
        "expected_delivery_date": "DateTimeField",
        "reference_number": "CharField",
        "payment_term": "ForeignKey",
        "source_of_supply": "JSONField",
        "tax_applied": "CharField",
        "terms_and_conditions": "ForeignKey",
        "bill": "ForeignKey",
        "mailing_address": "TextField",
        "shipment_preference": "CharField",
        "attachment": "FileField",
        "note": "TextField",
        "subtotal": "DecimalField",
        "discount": "DecimalField",
        "tax": "JSONField",
        "total_amount": "DecimalField",
        "is_draft": "BooleanField",
        "is_sent": "BooleanField",
        "is_removed": "BooleanField",
        "is_converted_to_bill": "BooleanField",
        "created_by": "ForeignKey",
        "updated_by": "ForeignKey",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField",
        "currency": "ForeignKey",
        "exchange_rate": "DecimalField"
      },
      "foreign_keys": {
        "business": "numbers_app_business",
        "vendor": "numbers_app_party",
        "payment_term": "numbers_app_paymentterms",
        "terms_and_conditions": "numbers_app_termsandconditions",
        "bill": "numbers_app_bill",
        "created_by": "numbers_app_user",
        "updated_by": "numbers_app_user",
        "currency": "numbers_app_currency"
      },
      "choices": {
        "tax_applied": {
          "inclusive": "Inclusive",
          "exclusive": "Exclusive",
          "no_tax": "No Tax"
        }
      },
      "inferred_relationships": {},
      "description": "The PurchaseOrder model is used to represent an order placed by a business to a vendor for goods or services. It contains all necessary commercial and logistical information such as vendor details, items, tax information, delivery expectations, and total costs. It serves as a pre-bill (pre-invoice) document that can later be converted into a Bill. Send formal purchase requests to vendors. Track outstanding purchase orders. Manage vendor terms and delivery tracking. Relationships: 1.business →ForeignKey Business. The business entity placing the order 2.vendor  →ForeignKey Party. The vendor (usually with role = vendor) to whom the PO is issued 3.bill →ForeignKey Bill. Reference to the bill once the PO is converted 4.created_by, updated_by →ForeignKey User. Tracks who created and last updated the PO"
    },
    "numbers_app_purchaseorderitems": {
      "columns": {
        "id": "BigAutoField",
        "item_order": "IntegerField",
        "item": "ForeignKey",
        "description": "TextField",
        "expense_category": "ForeignKey",
        "quantity": "DecimalField",
        "unit": "ForeignKey",
        "rate": "DecimalField",
        "tax": "ForeignKey",
        "item_level_discount": "DecimalField",
        "is_item_discount_in_percentage": "BooleanField",
        "amount": "DecimalField",
        "purchase_order": "ForeignKey"
      },
      "foreign_keys": {
        "item": "numbers_app_items",
        "expense_category": "numbers_app_chartofaccount",
        "unit": "numbers_app_units",
        "tax": "numbers_app_tax",
        "purchase_order": "numbers_app_purchaseorder"
      },
      "choices": {},
      "inferred_relationships": {},
      "description": "The PurchaseOrderItems model represents individual line items in a PurchaseOrder. Each entry corresponds to one item ordered from a vendor, including pricing, tax, quantity, and discount information. Relationships: 1.purchase_order →ForeignKey PurchaseOrder. Links this item to a specific purchase order 2.item →ForeignKey Items. The product or service being ordered 3.expense_category →ForeignKey ChartofAccount. Accounting category for the expense"
    },
    "numbers_app_payment": {
      "columns": {
        "id": "BigAutoField",
        "business": "ForeignKey",
        "journal_entry": "ForeignKey",
        "party": "ForeignKey",
        "payment_type": "CharField",
        "payment_method": "CharField",
        "payment_date": "DateTimeField",
        "account": "ForeignKey",
        "reference": "CharField",
        "total_amount": "DecimalField",
        "total_payment_amount": "DecimalField",
        "balance_amount": "DecimalField",
        "refunded_amount": "DecimalField",
        "note": "TextField",
        "attachment": "FileField",
        "is_sent": "BooleanField",
        "is_removed": "BooleanField",
        "exchange_rate": "DecimalField",
        "tds_account": "ForeignKey",
        "is_tds_applicable": "BooleanField",
        "currency": "ForeignKey",
        "has_rcm": "BooleanField",
        "is_advance": "BooleanField",
        "tax_summary": "JSONField",
        "place_of_supply": "JSONField",
        "tax": "ForeignKey",
        "created_by": "ForeignKey",
        "updated_by": "ForeignKey",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField"
      },
      "foreign_keys": {
        "business": "numbers_app_business",
        "journal_entry": "numbers_app_journalentry",
        "party": "numbers_app_party",
        "account": "numbers_app_chartofaccount",
        "tds_account": "numbers_app_chartofaccount",
        "currency": "numbers_app_currency",
        "tax": "numbers_app_tax",
        "created_by": "numbers_app_user",
        "updated_by": "numbers_app_user"
      },
      "choices": {
        "payment_type": {
          "receive": "Receive",
          "pay": "Pay"
        },
        "payment_method": {
          "cash": "Cash",
          "bank_transfer": "Bank Transfer",
          "cheque": "Cheque",
          "upi": "UPI",
          "card": "Card",
          "net_banking": "Net Banking"
        }
      },
      "inferred_relationships": {},
      "description": "The Payment table tracks all incoming (receive) and outgoing (pay) financial transactions related to a business. It records payment details, accounting metadata, tax implications, and maintains audit history. This model supports features like multi-currency, TDS (Tax Deducted at Source), reverse charge, and payment attachments, making it robust for general accounting and compliance workflows. Relationships: 1.business -> Many-to-One (FK) Business. Links payment to a specific business entity. 2.journal_entry -> Optional Many-to-One (FK) JournalEntry. Associates the payment with an accounting journal entry. 3.party -> Optional Many-to-One (FK) Party. Represents the customer or vendor the payment is associated with. 4.account -> Optional Many-to-One (FK) ChartofAccount. The ledger account where the payment is posted. 5.tds_account -> Optional Many-to-One (FK) ChartofAccount. Used when TDS (Tax Deducted at Source) is applicable. 6.created_by / updated_by -> Optional Many-to-One (FK) User. Tracks who created or last modified the record."
    },
    "numbers_app_paymentfor": {
      "columns": {
        "id": "BigAutoField",
        "payment": "ForeignKey",
        "reference_id": "IntegerField",
        "reference_type": "CharField",
        "reference_number": "CharField",
        "date": "DateTimeField",
        "due_date": "DateTimeField",
        "amount": "DecimalField",
        "amount_due": "DecimalField",
        "withholding_tax": "DecimalField",
        "payment_amount": "DecimalField"
      },
      "foreign_keys": {
        "payment": "numbers_app_payment"
      },
      "choices": {
        "reference_type": {
          "invoice": "Invoice",
          "bill": "Bill"
        }
      },
      "inferred_relationships": {}
    },
    "numbers_app_openingbalanceadjustment": {
      "columns": {
        "id": "BigAutoField",
        "business": "ForeignKey",
        "journal_entry": "ForeignKey",
        "account_amount_data": "TextField",
        "created_by": "ForeignKey",
        "created_at": "DateTimeField"
      },
      "foreign_keys": {
        "business": "numbers_app_business",
        "journal_entry": "numbers_app_journalentry",
        "created_by": "numbers_app_user"
      },
      "choices": {},
      "inferred_relationships": {}
    },
    "numbers_app_estimate": {
      "columns": {
        "id": "BigAutoField",
        "business": "ForeignKey",
        "business_address": "JSONField",
        "customer": "ForeignKey",
        "customer_emails": "JSONField",
        "estimate_number": "CharField",
        "estimate_date": "DateTimeField",
        "expiry_date": "DateTimeField",
        "reference_number": "CharField",
        "sales_person": "ForeignKey",
        "place_of_supply": "JSONField",
        "tax_applied": "CharField",
        "terms_and_conditions": "ForeignKey",
        "invoice": "ForeignKey",
        "sales_order": "ForeignKey",
        "shipping_address": "TextField",
        "billing_address": "TextField",
        "attachment": "FileField",
        "note": "TextField",
        "subtotal": "DecimalField",
        "discount": "DecimalField",
        "tax": "JSONField",
        "total_amount": "DecimalField",
        "is_draft": "BooleanField",
        "is_sent": "BooleanField",
        "is_removed": "BooleanField",
        "is_converted_to_invoice": "BooleanField",
        "is_converted_to_sales_order": "BooleanField",
        "created_by": "ForeignKey",
        "updated_by": "ForeignKey",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField",
        "currency": "ForeignKey",
        "exchange_rate": "DecimalField"
      },
      "foreign_keys": {
        "business": "numbers_app_business",
        "customer": "numbers_app_party",
        "sales_person": "numbers_app_salesperson",
        "terms_and_conditions": "numbers_app_termsandconditions",
        "invoice": "numbers_app_invoice",
        "sales_order": "numbers_app_salesorder",
        "created_by": "numbers_app_user",
        "updated_by": "numbers_app_user",
        "currency": "numbers_app_currency"
      },
      "choices": {
        "tax_applied": {
          "inclusive": "Inclusive",
          "exclusive": "Exclusive",
          "no_tax": "No Tax"
        }
      },
      "inferred_relationships": {},
      "description": "To create and manage price estimates or quotations for customers.Acts as a non-binding proposal that 	can later be converted into an invoice or sales order.When a customer requests a price quote before committing to purchase.To keep track of proposals that may later turn into sales orders or invoices. Helps streamline the sales pipeline and ensures consistency in customer communications. Relationships: 1. business -> ForeignKey Business. tthe business issuing the estimate. 2. customer -> ForeignKey Customer. the recipient of the estimate. 3.sales_person -> ForeignKey SalesPerson. employee handling the estimate. 4.invoice -> ForeignKey Invoice. linked if the estimate was converted to an invoice. 5.sales_order -> ForeignKey SalesOrder. linked if it became a sales order."
    },
    "numbers_app_estimateitems": {
      "columns": {
        "id": "BigAutoField",
        "item_order": "IntegerField",
        "item": "ForeignKey",
        "description": "TextField",
        "quantity": "DecimalField",
        "unit": "ForeignKey",
        "rate": "DecimalField",
        "tax": "ForeignKey",
        "item_level_discount": "DecimalField",
        "is_item_discount_in_percentage": "BooleanField",
        "amount": "DecimalField",
        "estimate": "ForeignKey"
      },
      "foreign_keys": {
        "item": "numbers_app_items",
        "unit": "numbers_app_units",
        "tax": "numbers_app_tax",
        "estimate": "numbers_app_estimate"
      },
      "choices": {},
      "inferred_relationships": {},
      "description": "This model represents the individual items listed in a sales estimate. It stores details like the item, quantity, rate, tax, discount, and total amount. Used for calculating the total value of the estimate. Provides detailed breakdowns for customer visibility and record-keeping.Whenever an estimate is created, EstimateItems are added to list all included products/services. Relationships: 1.item -> ForeignKey Items. the product or service being estimated. 2.estimate -> ForeignKey Estimate. The parent estimate this item belongs to."
    },
    "numbers_app_exportedfiles": {
      "columns": {
        "id": "BigAutoField",
        "business": "ForeignKey",
        "description": "CharField",
        "document": "FileField",
        "document_type": "CharField",
        "durations_start_date": "DateTimeField",
        "duration_end_date": "DateTimeField",
        "meta_data": "JSONField",
        "created_by": "ForeignKey",
        "updated_by": "ForeignKey",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField"
      },
      "foreign_keys": {
        "business": "numbers_app_business",
        "created_by": "numbers_app_user",
        "updated_by": "numbers_app_user"
      },
      "choices": {
        "document_type": {
          "report": "Report",
          "profit_and_loss": "Profit and Loss",
          "balance_sheet": "Balance Sheet",
          "cash_flow": "Cash Flow",
          "customer_statement": "Customer Statement",
          "vendor_statement": "Vender Statement",
          "account_statement": "Account statement"
        }
      },
      "inferred_relationships": {}
    },
    "numbers_app_creditnote": {
      "columns": {
        "id": "BigAutoField",
        "business": "ForeignKey",
        "business_address": "JSONField",
        "journal_entry": "ForeignKey",
        "customer": "ForeignKey",
        "customer_emails": "JSONField",
        "credit_note_number": "CharField",
        "credit_note_date": "DateTimeField",
        "sales_person": "ForeignKey",
        "place_of_supply": "JSONField",
        "tax_applied": "CharField",
        "terms_and_conditions": "ForeignKey",
        "reason": "CharField",
        "against_invoice": "ForeignKey",
        "against_invoice_type": "CharField",
        "credit_utilization_status": "CharField",
        "refunded_amount": "DecimalField",
        "applied_as_payment_amount": "DecimalField",
        "last_credit_utilization_date": "DateTimeField",
        "shipping_address": "TextField",
        "billing_address": "TextField",
        "note": "TextField",
        "subtotal": "DecimalField",
        "discount": "DecimalField",
        "tax": "JSONField",
        "total_amount": "DecimalField",
        "is_draft": "BooleanField",
        "is_sent": "BooleanField",
        "is_removed": "BooleanField",
        "reason_for_update": "TextField",
        "created_by": "ForeignKey",
        "updated_by": "ForeignKey",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField",
        "currency": "ForeignKey",
        "exchange_rate": "DecimalField"
      },
      "foreign_keys": {
        "business": "numbers_app_business",
        "journal_entry": "numbers_app_journalentry",
        "customer": "numbers_app_party",
        "sales_person": "numbers_app_salesperson",
        "terms_and_conditions": "numbers_app_termsandconditions",
        "against_invoice": "numbers_app_invoice",
        "created_by": "numbers_app_user",
        "updated_by": "numbers_app_user",
        "currency": "numbers_app_currency"
      },
      "choices": {
        "tax_applied": {
          "inclusive": "Inclusive",
          "exclusive": "Exclusive",
          "no_tax": "No Tax"
        },
        "reason": {
          "sales_return": "Sales Return",
          "post_sale_discount": "Post Sale Discount",
          "deficiency_in_service": "Deficiency in Service",
          "correction_in_invoice": "Correction in Invoice",
          "change_in_pos": "Change in POS",
          "finalization_of_provisional_assessment": "Finalization of Provisional Assessment",
          "other": "Other"
        },
        "against_invoice_type": {
          "gst_registered_regular": "GST registered- Regular",
          "gst_registered_composition": "GST registered- Composition",
          "gst_unregistered": "GST unregistered",
          "consumer": "Consumer",
          "overseas": "Overseas",
          "sez": "SEZ",
          "deemed_exports": "Deemed exports- EOU's, STP's, EHTP's etc"
        },
        "credit_utilization_status": {
          "utilized": "Utilized",
          "unutilized": "Unutilized",
          "partially_utilized": "Partially Utilized"
        }
      },
      "inferred_relationships": {},
      "description": "Represents a credit note issued to a customer, typically due to sales returns, post-sale discounts, or corrections in previously issued invoices. It can be used for refunds or applied as a payment against future 	invoices.Acts as a financial document to adjust or reverse charges on an invoice.Integrates with accounting (JournalEntry) and tracks utilization status (refunded, applied, etc.). RelationShips: . business -> ForeignKey Business. The business issuing the credit note. 2.journal_entry -> ForeignKey JournalEntry. Linked journal entry for accounting. 3.customer -> ForeignKey Party. The customer receiving the credit note. 4.sales_person -> ForeignKey SalesPerson. Sales representative associated with the transaction. 5.against_invoice -ForeignKey Invoice. The original invoice being credited. 6.created_by / updated_by User tracking for creation and updates. subtotal, discount, tax, total_amount: Standard credit note amount breakdown."
    },
    "numbers_app_creditnoteitems": {
      "columns": {
        "id": "BigAutoField",
        "item_order": "IntegerField",
        "item": "ForeignKey",
        "description": "TextField",
        "expense_category": "ForeignKey",
        "quantity": "DecimalField",
        "unit": "ForeignKey",
        "rate": "DecimalField",
        "tax": "ForeignKey",
        "item_level_discount": "DecimalField",
        "is_item_discount_in_percentage": "BooleanField",
        "amount": "DecimalField",
        "credit_note": "ForeignKey"
      },
      "foreign_keys": {
        "item": "numbers_app_items",
        "expense_category": "numbers_app_chartofaccount",
        "unit": "numbers_app_units",
        "tax": "numbers_app_tax",
        "credit_note": "numbers_app_creditnote"
      },
      "choices": {},
      "inferred_relationships": {},
      "description": ""
    },
    "numbers_app_debitnote": {
      "columns": {
        "id": "BigAutoField",
        "business": "ForeignKey",
        "business_address": "JSONField",
        "journal_entry": "ForeignKey",
        "vendor": "ForeignKey",
        "vendor_emails": "JSONField",
        "debit_note_number": "CharField",
        "debit_note_date": "DateTimeField",
        "source_of_supply": "JSONField",
        "tax_applied": "CharField",
        "terms_and_conditions": "ForeignKey",
        "reason": "CharField",
        "against_bill": "ForeignKey",
        "against_bill_type": "CharField",
        "credit_utilization_status": "CharField",
        "refunded_amount": "DecimalField",
        "applied_as_payment_amount": "DecimalField",
        "last_credit_utilization_date": "DateTimeField",
        "mailing_address": "TextField",
        "note": "TextField",
        "subtotal": "DecimalField",
        "discount": "DecimalField",
        "tax": "JSONField",
        "has_rcm": "BooleanField",
        "total_amount": "DecimalField",
        "is_draft": "BooleanField",
        "is_sent": "BooleanField",
        "is_removed": "BooleanField",
        "reason_for_update": "TextField",
        "created_by": "ForeignKey",
        "updated_by": "ForeignKey",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField",
        "currency": "ForeignKey",
        "exchange_rate": "DecimalField"
      },
      "foreign_keys": {
        "business": "numbers_app_business",
        "journal_entry": "numbers_app_journalentry",
        "vendor": "numbers_app_party",
        "terms_and_conditions": "numbers_app_termsandconditions",
        "against_bill": "numbers_app_bill",
        "created_by": "numbers_app_user",
        "updated_by": "numbers_app_user",
        "currency": "numbers_app_currency"
      },
      "choices": {
        "tax_applied": {
          "inclusive": "Inclusive",
          "exclusive": "Exclusive",
          "no_tax": "No Tax"
        },
        "reason": {
          "purchase_return": "Purchase Return",
          "post_purchase_discount": "Post Purchase Discount",
          "deficiency_in_service": "Deficiency in Service",
          "correction_in_bill": "Correction in Bill",
          "change_in_pos": "Change in POS",
          "finalization_of_provisional_assessment": "Finalization of Provisional Assessment",
          "other": "Other"
        },
        "against_bill_type": {
          "gst_registered_regular": "GST registered- Regular",
          "gst_registered_composition": "GST registered- Composition",
          "gst_unregistered": "GST unregistered",
          "consumer": "Consumer",
          "overseas": "Overseas",
          "sez": "SEZ",
          "deemed_exports": "Deemed exports- EOU's, STP's, EHTP's etc"
        },
        "credit_utilization_status": {
          "utilized": "Utilized",
          "unutilized": "Unutilized",
          "partially_utilized": "Partially Utilized"
        }
      },
      "inferred_relationships": {},
      "description": "Represents a vendor-related debit note in the accounting system, issued typically for purchase returns,post-purchase adjustments, or corrections.Used for reversing or adjusting vendor bills. Integrates tightly with taxation, accounting, and currency conversion. Supports detailed tracking of how the note is applied or refunded. Relationships: 1.business -> ForeignKey Business. Business to which the debit note belongs. 2.journal_entry -> ForeignKey JournalEntry. Associated journal entry for accounting linkage. 3.vendor -> ForeignKey Party. Vendor to whom the debit note is issued. 4.against_bill -> ForeignKey Bill. Original bill the debit note is issued against. 5.created_by / updated_by -> User. Tracks user activity on record creation/update."
    },
    "numbers_app_debitnoteitems": {
      "columns": {
        "id": "BigAutoField",
        "item_order": "IntegerField",
        "item": "ForeignKey",
        "description": "TextField",
        "expense_category": "ForeignKey",
        "quantity": "DecimalField",
        "unit": "ForeignKey",
        "rate": "DecimalField",
        "tax": "ForeignKey",
        "item_level_discount": "DecimalField",
        "is_item_discount_in_percentage": "BooleanField",
        "amount": "DecimalField",
        "debit_note": "ForeignKey"
      },
      "foreign_keys": {
        "item": "numbers_app_items",
        "expense_category": "numbers_app_chartofaccount",
        "unit": "numbers_app_units",
        "tax": "numbers_app_tax",
        "debit_note": "numbers_app_debitnote"
      },
      "choices": {},
      "inferred_relationships": {},
      "description": "Represents individual item-level details associated with a vendor Debit Note, including quantity, rate, taxes, and discounts. Used to capture granular breakdown of a debit note for accounting and tax purposes. Supports both fixed and percentage discounts per item. Relationships: 1. item -> ForeignKey Items. The specific item included in the debit note. 2. expense_category -> ForeignKey ChartofAccount. Chart of account for categorizing the item."
    },
    "numbers_app_refundpayment": {
      "columns": {
        "id": "BigAutoField",
        "business": "ForeignKey",
        "journal_entry": "ForeignKey",
        "party": "ForeignKey",
        "payment_type": "CharField",
        "payment_method": "CharField",
        "refund_date": "DateTimeField",
        "account": "ForeignKey",
        "credit_note": "ForeignKey",
        "debit_note": "ForeignKey",
        "payment": "ForeignKey",
        "total_refund_amount": "DecimalField",
        "note": "TextField",
        "is_removed": "BooleanField",
        "exchange_rate": "DecimalField",
        "currency": "ForeignKey",
        "created_by": "ForeignKey",
        "updated_by": "ForeignKey",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField"
      },
      "foreign_keys": {
        "business": "numbers_app_business",
        "journal_entry": "numbers_app_journalentry",
        "party": "numbers_app_party",
        "account": "numbers_app_chartofaccount",
        "credit_note": "numbers_app_creditnote",
        "debit_note": "numbers_app_debitnote",
        "payment": "numbers_app_payment",
        "currency": "numbers_app_currency",
        "created_by": "numbers_app_user",
        "updated_by": "numbers_app_user"
      },
      "choices": {
        "payment_type": {
          "receive": "Receive",
          "pay": "Pay"
        },
        "payment_method": {
          "cash": "Cash",
          "bank_transfer": "Bank Transfer",
          "cheque": "Cheque",
          "upi": "UPI",
          "card": "Card",
          "net_banking": "Net Banking"
        }
      },
      "inferred_relationships": {}
    },
    "numbers_app_deliverychallan": {
      "columns": {
        "id": "BigAutoField",
        "business": "ForeignKey",
        "business_address": "JSONField",
        "customer": "ForeignKey",
        "delivery_challan_number": "CharField",
        "delivery_challan_date": "DateTimeField",
        "reference_number": "CharField",
        "place_of_supply": "JSONField",
        "tax_applied": "CharField",
        "terms_and_conditions": "ForeignKey",
        "invoice": "ForeignKey",
        "shipping_address": "TextField",
        "billing_address": "TextField",
        "challan_type": "CharField",
        "attachment": "FileField",
        "note": "TextField",
        "subtotal": "DecimalField",
        "discount": "DecimalField",
        "tax": "JSONField",
        "total_amount": "DecimalField",
        "is_draft": "BooleanField",
        "is_delivered": "BooleanField",
        "is_returned": "BooleanField",
        "is_removed": "BooleanField",
        "invoiced_status": "CharField",
        "created_by": "ForeignKey",
        "updated_by": "ForeignKey",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField",
        "currency": "ForeignKey",
        "exchange_rate": "DecimalField"
      },
      "foreign_keys": {
        "business": "numbers_app_business",
        "customer": "numbers_app_party",
        "terms_and_conditions": "numbers_app_termsandconditions",
        "invoice": "numbers_app_invoice",
        "created_by": "numbers_app_user",
        "updated_by": "numbers_app_user",
        "currency": "numbers_app_currency"
      },
      "choices": {
        "tax_applied": {
          "inclusive": "Inclusive",
          "exclusive": "Exclusive",
          "no_tax": "No Tax"
        },
        "challan_type": {
          "supply_of_liquid_gas": "Supply of Liquid Gas",
          "job_work": "Job Work",
          "supply_on_approval": "Supply on Approval",
          "others": "Others"
        },
        "invoiced_status": {
          "not_invoiced": "Not Invoiced",
          "invoiced": "Invoiced",
          "partially_invoiced": "Partially Invoiced"
        }
      },
      "inferred_relationships": {},
      "description": "This model stores the individual items listed in a delivery challan. Each record represents a specific item being delivered as part of a larger delivery document (DeliveryChallan). To record detailed item-level information for each delivery challan.Helps in tracking what exactly was sent in the delivery (item, quantity, rate, tax, etc.). Relationships: 1.item -> ForeignKey Item. the actual product/item being delivered. 2.delivery_challan -> ForeignKey DeliveryChallan. the parent delivery challan this item belongs to. Useful for managing itemized delivery data for inventory, tracking, and legal purposes."
    },
    "numbers_app_deliverychallanitems": {
      "columns": {
        "id": "BigAutoField",
        "item_order": "IntegerField",
        "item": "ForeignKey",
        "description": "TextField",
        "quantity": "DecimalField",
        "unit": "ForeignKey",
        "rate": "DecimalField",
        "tax": "ForeignKey",
        "item_level_discount": "DecimalField",
        "is_item_discount_in_percentage": "BooleanField",
        "amount": "DecimalField",
        "delivery_challan": "ForeignKey"
      },
      "foreign_keys": {
        "item": "numbers_app_items",
        "unit": "numbers_app_units",
        "tax": "numbers_app_tax",
        "delivery_challan": "numbers_app_deliverychallan"
      },
      "choices": {},
      "inferred_relationships": {}
    },
    "numbers_app_contactusquerycategory": {
      "columns": {
        "id": "BigAutoField",
        "category": "CharField"
      },
      "foreign_keys": {},
      "choices": {},
      "inferred_relationships": {}
    },
    "numbers_app_supportticket": {
      "columns": {
        "id": "BigAutoField",
        "business": "ForeignKey",
        "query_category": "ForeignKey",
        "subject": "CharField",
        "description": "TextField",
        "email": "CharField",
        "name": "CharField",
        "phone_number": "CharField",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField"
      },
      "foreign_keys": {
        "business": "numbers_app_business",
        "query_category": "numbers_app_contactusquerycategory"
      },
      "choices": {},
      "inferred_relationships": {}
    },
    "numbers_app_invoicereminder": {
      "columns": {
        "id": "BigAutoField",
        "business": "ForeignKey",
        "name": "CharField",
        "from_email": "CharField",
        "remind_to": "CharField",
        "other_email": "JSONField",
        "subject": "CharField",
        "days": "IntegerField",
        "relative_due": "CharField",
        "is_active": "BooleanField",
        "created_by": "ForeignKey",
        "updated_by": "ForeignKey",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField"
      },
      "foreign_keys": {
        "business": "numbers_app_business",
        "created_by": "numbers_app_user",
        "updated_by": "numbers_app_user"
      },
      "choices": {
        "remind_to": {
          "me": "ME",
          "customer": "CUSTOMER",
          "both": "BOTH"
        },
        "relative_due": {
          "before": "BEFORE",
          "after": "AFTER"
        }
      },
      "inferred_relationships": {}
    },
    "numbers_app_billreminder": {
      "columns": {
        "id": "BigAutoField",
        "business": "ForeignKey",
        "name": "CharField",
        "to_email": "JSONField",
        "days": "IntegerField",
        "relative_due": "CharField",
        "is_active": "BooleanField",
        "created_by": "ForeignKey",
        "updated_by": "ForeignKey",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField"
      },
      "foreign_keys": {
        "business": "numbers_app_business",
        "created_by": "numbers_app_user",
        "updated_by": "numbers_app_user"
      },
      "choices": {
        "relative_due": {
          "before": "BEFORE",
          "after": "AFTER"
        }
      },
      "inferred_relationships": {}
    },
    "numbers_app_expense": {
      "columns": {
        "id": "BigAutoField",
        "business": "ForeignKey",
        "vendor": "ForeignKey",
        "customer": "ForeignKey",
        "expense_date": "DateTimeField",
        "expense_type": "CharField",
        "exchange_rate": "DecimalField",
        "journal_entry": "ForeignKey",
        "source_of_supply": "JSONField",
        "destination_of_supply": "JSONField",
        "gst_registration_type": "CharField",
        "gstin_number": "CharField",
        "reference_invoice_number": "CharField",
        "paid_through_account": "ForeignKey",
        "currency": "ForeignKey",
        "tax_applied": "CharField",
        "subtotal": "DecimalField",
        "tax": "JSONField",
        "invoice": "ForeignKey",
        "total_amount": "DecimalField",
        "attachment": "FileField",
        "has_rcm": "BooleanField",
        "is_billable": "BooleanField",
        "mark_up_percent": "DecimalField",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField",
        "created_by": "ForeignKey",
        "updated_by": "ForeignKey",
        "is_recurring": "BooleanField",
        "recurring_expense": "ForeignKey",
        "is_removed": "BooleanField"
      },
      "foreign_keys": {
        "business": "numbers_app_business",
        "vendor": "numbers_app_party",
        "customer": "numbers_app_party",
        "journal_entry": "numbers_app_journalentry",
        "paid_through_account": "numbers_app_chartofaccount",
        "currency": "numbers_app_currency",
        "invoice": "numbers_app_invoice",
        "created_by": "numbers_app_user",
        "updated_by": "numbers_app_user",
        "recurring_expense": "numbers_app_recurringexpense"
      },
      "choices": {
        "tax_applied": {
          "inclusive": "Inclusive",
          "exclusive": "Exclusive",
          "no_tax": "No Tax"
        }
      },
      "inferred_relationships": {},
      "description": "This model tracks business expenses such as purchases, vendor payments, or billable costs. It captures all related information like the vendor, customer, tax, currency, and payment source.To record and manage expenses incurred by the business.Supports both billable and non-billable expenses. Handles tax details (CGST, SGST, IGST) and supports GST compliance.Can be linked to invoices and journal entries. Relationship: 1.business -> ForeignKey Business. the company to which the expense belongs. 2.vendor -> ForeignKey Party.  the party from whom goods/services were purchased. 3.customer  -> ForeignKey Customer. linked if the expense is billable to a customer. 4.invoice -> ForeignKey Invoice. optional invoice related to this expense. 5.journal_entry -> ForeignKey JournalEntry  connects to the accounting journal entry. 6.paid_through_account -> ForeignKey ChartofAccount. account used to pay the expense (from Chart of Accounts) 7.recurring_expense -> ForeignKey RecurringInvoice.  links to a parent recurring expense entry, if applicable."
    },
    "numbers_app_expenseaccount": {
      "columns": {
        "id": "BigAutoField",
        "expense": "ForeignKey",
        "account": "ForeignKey",
        "note": "TextField",
        "tax": "ForeignKey",
        "hsn_sac_code": "CharField",
        "amount": "DecimalField"
      },
      "foreign_keys": {
        "expense": "numbers_app_expense",
        "account": "numbers_app_chartofaccount",
        "tax": "numbers_app_tax"
      },
      "choices": {},
      "inferred_relationships": {},
      "description": "This model captures account-wise breakdowns of an expense. It is used when a single expense is split 	across different accounts or categories for accounting and tax purposes. To allocate an expense to a specific Chart of Account. Allows tax tracking and classification using HSN/SAC codes.Supports multi-	account allocation for a single expense.When an expense needs to be categorized into different accounts.For accurate financial reporting and GST compliance.Useful in multi-line expenses (e.g.,partial amounts for office rent, utilities, etc.). Relationships: 1. expense  -> ForeignKey Expense. expense – links to the main Expense record this account line belongs to. 2.account  -> ForeignKey ChartofAccount .the specific ChartofAccount used for the expense. 3.tax applied tax on this particular account line (optional)."
    },
    "numbers_app_businesspreference": {
      "columns": {
        "id": "BigAutoField",
        "business": "OneToOneField",
        "general": "JSONField",
        "item": "JSONField",
        "customer": "JSONField",
        "estimate": "JSONField",
        "invoice": "JSONField",
        "delivery_challan": "JSONField",
        "recurring_invoice": "JSONField",
        "sales_order": "JSONField",
        "credit_note": "JSONField",
        "payment_received": "JSONField",
        "vendor": "JSONField",
        "bill": "JSONField",
        "purchase_order": "JSONField",
        "debit_note": "JSONField",
        "payment_made": "JSONField",
        "transaction_lock": "JSONField"
      },
      "foreign_keys": {
        "business": "numbers_app_business"
      },
      "choices": {},
      "inferred_relationships": {}
    },
    "numbers_app_userpreference": {
      "columns": {
        "id": "BigAutoField",
        "user": "ForeignKey",
        "default_business": "ForeignKey"
      },
      "foreign_keys": {
        "user": "numbers_app_user",
        "default_business": "numbers_app_business"
      },
      "choices": {},
      "inferred_relationships": {}
    },
    "numbers_app_linkvalidationrecord": {
      "columns": {
        "id": "BigAutoField",
        "link": "TextField",
        "email": "CharField",
        "link_type": "CharField",
        "valid_till": "IntegerField",
        "resend_count": "IntegerField",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField",
        "business": "ForeignKey"
      },
      "foreign_keys": {
        "business": "numbers_app_business"
      },
      "choices": {
        "link_type": {
          "verify_email": "Verify Email",
          "reset_password": "Resend Password",
          "user_invitation": "User Invitation"
        }
      },
      "inferred_relationships": {}
    },
    "numbers_app_tallysyncbatch": {
      "columns": {
        "id": "BigAutoField",
        "business": "ForeignKey",
        "batch_number": "UUIDField",
        "total_records": "IntegerField",
        "records_synced": "IntegerField",
        "start_time": "DateTimeField",
        "end_time": "DateTimeField",
        "status": "CharField",
        "groups_synced": "BooleanField",
        "ledgers_synced": "BooleanField",
        "party_synced": "BooleanField",
        "stocks_synced": "BooleanField",
        "vouchers_synced": "BooleanField",
        "stock_ledgers_synced": "BooleanField",
        "error_message": "TextField"
      },
      "foreign_keys": {
        "business": "numbers_app_business"
      },
      "choices": {
        "status": {
          "in_progress": "In Progress",
          "success": "Success",
          "failed": "Failed"
        }
      },
      "inferred_relationships": {}
    },
    "numbers_app_tallysyncholdrecord": {
      "columns": {
        "id": "BigAutoField",
        "start_datetime": "DateTimeField",
        "end_datetime": "DateTimeField",
        "reason": "TextField"
      },
      "foreign_keys": {},
      "choices": {},
      "inferred_relationships": {}
    },
    "numbers_app_demorequest": {
      "columns": {
        "id": "BigAutoField",
        "name": "CharField",
        "email": "CharField",
        "phone_number": "CharField",
        "help_needed": "TextField",
        "status": "CharField",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField"
      },
      "foreign_keys": {},
      "choices": {
        "status": {
          "pending": "Pending",
          "completed": "Completed",
          "cancelled": "Cancelled"
        }
      },
      "inferred_relationships": {}
    },
    "numbers_app_recurringexpense": {
      "columns": {
        "business": "ForeignKey",
        "profile_name": "CharField",
        "repeat_every": "IntegerField",
        "repeat_frequency": "CharField",
        "preference": "CharField",
        "expense_data": "JSONField",
        "vendor": "ForeignKey",
        "attachment": "FileField",
        "starts_on": "DateTimeField",
        "ends_on": "DateTimeField",
        "never_expires": "BooleanField",
        "is_active": "BooleanField",
        "periodic_task": "OneToOneField",
        "is_removed": "BooleanField",
        "last_run_at": "DateTimeField",
        "created_by": "ForeignKey",
        "updated_by": "ForeignKey",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField"
      },
      "foreign_keys": {
        "business": "numbers_app_business",
        "vendor": "numbers_app_party",
        "periodic_task": "django_celery_beat_periodictask",
        "created_by": "numbers_app_user",
        "updated_by": "numbers_app_user"
      },
      "choices": {
        "repeat_frequency": {
          "day": "Day(s)",
          "week": "Week(s)",
          "month": "Month(s)",
          "year": "Year(s)"
        },
        "preference": {
          "create_and_draft": "Create Invoices as Drafts",
          "create_and_send": "Create and Send Invoices",
          "create_and_save": "Create and save"
        }
      },
      "inferred_relationships": {},
      "description": "The RecurringExpense model is used to define and manage automated, repeatable expense entries in the system. It schedules expenses to recur at a set frequency (e.g., monthly rent, utility bills). Relationships: 1.business →ForeignKey Business. Ties the expense to a business entity 2.vendor →ForeignKey Party. The vendor (supplier) associated with the recurring expense 3.created_by, updated_by →ForeignKey User. Tracks who created or last modified the record"
    },
    "numbers_app_reportmapping": {
      "columns": {
        "id": "BigAutoField",
        "business": "ForeignKey",
        "integration_mode": "CharField",
        "report": "CharField",
        "mapping": "JSONField",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField"
      },
      "foreign_keys": {
        "business": "numbers_app_business"
      },
      "choices": {
        "integration_mode": {
          "numbers": "numbers",
          "tally": "tally"
        },
        "report": {
          "profit_and_loss": "Profit and Loss",
          "balance_sheet": "Balance Sheet",
          "cash_flow": "Cash Flow"
        }
      },
      "inferred_relationships": {}
    },
    "numbers_app_schedulereport": {
      "columns": {
        "business": "ForeignKey",
        "repeat_frequency": "CharField",
        "starts_on": "DateTimeField",
        "report_data": "JSONField",
        "is_active": "BooleanField",
        "report_name": "CharField",
        "periodic_task": "OneToOneField",
        "last_runtime": "DateTimeField",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField"
      },
      "foreign_keys": {
        "business": "numbers_app_business",
        "periodic_task": "django_celery_beat_periodictask"
      },
      "choices": {},
      "inferred_relationships": {}
    },
    "numbers_app_datapoint": {
      "columns": {
        "id": "BigAutoField",
        "name": "CharField",
        "slug_name": "SlugField",
        "description": "TextField",
        "is_calculated": "BooleanField",
        "is_custom": "BooleanField",
        "accounts_key": "CharField",
        "account_type": "CharField",
        "calculation_formula": "TextField",
        "calculation_type": "CharField",
        "additional_params": "JSONField",
        "category": "ForeignKey",
        "is_insight_result": "BooleanField",
        "business": "ForeignKey",
        "is_removed": "BooleanField",
        "unit": "CharField",
        "created_by": "ForeignKey",
        "updated_by": "ForeignKey",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField"
      },
      "foreign_keys": {
        "category": "numbers_app_datapointcategory",
        "business": "numbers_app_business",
        "created_by": "numbers_app_user",
        "updated_by": "numbers_app_user"
      },
      "choices": {
        "is_calculated": {
          "false": "Account Balance",
          "true": "Calculated Data Point"
        },
        "account_type": {
          "raw": "Raw",
          "composite": "Composite"
        },
        "calculation_type": {
          "equation": "Direct Equation",
          "function": "Function"
        },
        "unit": {
          "base_currency": "Base Currency",
          "percentage": "Percentage",
          "none": "None"
        }
      },
      "inferred_relationships": {}
    },
    "numbers_app_datapointcategory": {
      "columns": {
        "id": "BigAutoField",
        "name": "CharField"
      },
      "foreign_keys": {},
      "choices": {},
      "inferred_relationships": {}
    },
    "numbers_app_insighttab": {
      "columns": {
        "id": "BigAutoField",
        "name": "CharField",
        "business": "ForeignKey"
      },
      "foreign_keys": {
        "business": "numbers_app_business"
      },
      "choices": {},
      "inferred_relationships": {}
    },
    "numbers_app_insightsection": {
      "columns": {
        "id": "BigAutoField",
        "name": "CharField",
        "tab": "ForeignKey",
        "business": "ForeignKey",
        "data_point_ids": "JSONField",
        "section_type": "CharField"
      },
      "foreign_keys": {
        "tab": "numbers_app_insighttab",
        "business": "numbers_app_business"
      },
      "choices": {
        "section_type": {
          "list_view": "List",
          "pie_chart": "Pie Chart",
          "line_chart": "Line Chart",
          "bar_graph": "Bar Graph",
          "scatter_chart": "Scatter Chart"
        }
      },
      "inferred_relationships": {}
    },
    "numbers_app_businesstaborder": {
      "columns": {
        "id": "BigAutoField",
        "business": "OneToOneField",
        "order": "JSONField"
      },
      "foreign_keys": {
        "business": "numbers_app_business"
      },
      "choices": {},
      "inferred_relationships": {}
    },
    "numbers_app_businesssectionorder": {
      "columns": {
        "id": "BigAutoField",
        "business": "ForeignKey",
        "insight_tab": "OneToOneField",
        "order": "JSONField"
      },
      "foreign_keys": {
        "business": "numbers_app_business",
        "insight_tab": "numbers_app_insighttab"
      },
      "choices": {},
      "inferred_relationships": {}
    },
    "numbers_app_otp": {
      "columns": {
        "id": "BigAutoField",
        "user": "ForeignKey",
        "otp": "CharField",
        "created_at": "DateTimeField",
        "expires_at": "DateTimeField",
        "is_used": "BooleanField",
        "reason": "CharField"
      },
      "foreign_keys": {
        "user": "numbers_app_user"
      },
      "choices": {
        "reason": {
          "login": "Login",
          "reset_password": "Reset Password",
          "account_deletion": "Account Deletion"
        }
      },
      "inferred_relationships": {}
    },
    "numbers_app_otpsession": {
      "columns": {
        "id": "BigAutoField",
        "session_id": "UUIDField",
        "email_otp": "CharField",
        "mobile_otp": "CharField",
        "mobile_number": "CharField",
        "email": "CharField",
        "is_email_otp_verified": "BooleanField",
        "is_mobile_otp_verified": "BooleanField",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField"
      },
      "foreign_keys": {},
      "choices": {},
      "inferred_relationships": {}
    },
    "numbers_app_otaupdates": {
      "columns": {
        "id": "BigAutoField",
        "version_code": "IntegerField",
        "version_name": "CharField",
        "release_notes": "TextField",
        "force_update": "BooleanField"
      },
      "foreign_keys": {},
      "choices": {},
      "inferred_relationships": {}
    },
    "numbers_app_marketingpagemetadata": {
      "columns": {
        "id": "BigAutoField",
        "params": "JSONField",
        "created_at": "DateTimeField"
      },
      "foreign_keys": {},
      "choices": {},
      "inferred_relationships": {}
    },
    "numbers_app_userinvite": {
      "columns": {
        "id": "BigAutoField",
        "business": "ForeignKey",
        "email": "CharField",
        "first_name": "CharField",
        "last_name": "CharField",
        "role": "CharField",
        "inviter": "ForeignKey",
        "invited_on": "DateTimeField",
        "is_accepted": "BooleanField"
      },
      "foreign_keys": {
        "business": "numbers_app_business",
        "inviter": "numbers_app_user"
      },
      "choices": {},
      "inferred_relationships": {}
    },
    "numbers_app_documentlinkdata": {
      "columns": {
        "id": "BigAutoField",
        "business": "ForeignKey",
        "link_uid": "SlugField",
        "document_type": "CharField",
        "secure_by": "CharField",
        "password": "CharField",
        "document_id": "IntegerField",
        "mobile_number": "CharField",
        "email": "JSONField",
        "is_restricted": "BooleanField",
        "seen_count": "IntegerField",
        "document_data": "JSONField",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField"
      },
      "foreign_keys": {
        "business": "numbers_app_business"
      },
      "choices": {
        "document_type": {
          "invoice": "Invoice",
          "sales_order": "Sales Order",
          "purchase_order": "Purchase Order",
          "credit_note": "Credit Note",
          "debit_note": "Debit Note",
          "estimate": "Estimate",
          "payment": "Payment"
        },
        "secure_by": {
          "otp": "Otp",
          "password": "Password",
          "input_validation": "Mobile or Email Input"
        }
      },
      "inferred_relationships": {}
    },
    "numbers_app_userfcmtokenmapping": {
      "columns": {
        "id": "BigAutoField",
        "user": "ForeignKey",
        "registration_token": "CharField",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField"
      },
      "foreign_keys": {
        "user": "numbers_app_user"
      },
      "choices": {},
      "inferred_relationships": {}
    },
    "numbers_app_notificationtype": {
      "columns": {
        "id": "BigAutoField",
        "name": "CharField",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField"
      },
      "foreign_keys": {},
      "choices": {},
      "inferred_relationships": {}
    },
    "numbers_app_notificationtopic": {
      "columns": {
        "id": "BigAutoField",
        "name": "CharField",
        "description": "TextField",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField"
      },
      "foreign_keys": {},
      "choices": {},
      "inferred_relationships": {}
    },
    "numbers_app_notification": {
      "columns": {
        "id": "BigAutoField",
        "title": "CharField",
        "body": "CharField",
        "type": "ForeignKey",
        "topic": "ForeignKey",
        "is_publish": "BooleanField",
        "schedule": "DateTimeField",
        "send_now": "BooleanField",
        "image": "FileField",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField"
      },
      "foreign_keys": {
        "type": "numbers_app_notificationtype",
        "topic": "numbers_app_notificationtopic"
      },
      "choices": {},
      "inferred_relationships": {}
    },
    "numbers_app_notificationtemplate": {
      "columns": {
        "id": "BigAutoField",
        "type": "ForeignKey",
        "title": "CharField",
        "content": "CharField",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField"
      },
      "foreign_keys": {
        "type": "numbers_app_notificationtype"
      },
      "choices": {},
      "inferred_relationships": {}
    },
    "django_admin_log": {
      "columns": {
        "id": "AutoField",
        "action_time": "DateTimeField",
        "user": "ForeignKey",
        "content_type": "ForeignKey",
        "object_id": "TextField",
        "object_repr": "CharField",
        "action_flag": "PositiveSmallIntegerField",
        "change_message": "TextField"
      },
      "foreign_keys": {
        "user": "numbers_app_user",
        "content_type": "django_content_type"
      },
      "choices": {
        "action_flag": {
          "1": "Addition",
          "2": "Change",
          "3": "Deletion"
        }
      },
      "inferred_relationships": {}
    },
    "auth_permission": {
      "columns": {
        "id": "AutoField",
        "name": "CharField",
        "content_type": "ForeignKey",
        "codename": "CharField"
      },
      "foreign_keys": {
        "content_type": "django_content_type"
      },
      "choices": {},
      "inferred_relationships": {}
    },
    "auth_group": {
      "columns": {
        "id": "AutoField",
        "name": "CharField"
      },
      "foreign_keys": {},
      "choices": {},
      "inferred_relationships": {}
    },
    "django_content_type": {
      "columns": {
        "id": "AutoField",
        "app_label": "CharField",
        "model": "CharField"
      },
      "foreign_keys": {},
      "choices": {},
      "inferred_relationships": {}
    },
    "django_session": {
      "columns": {
        "session_key": "CharField",
        "session_data": "TextField",
        "expire_date": "DateTimeField"
      },
      "foreign_keys": {},
      "choices": {},
      "inferred_relationships": {}
    }
  }

