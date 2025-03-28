import json
import os, getpass
from typing import Any
from langchain import hub
from datetime import datetime
from sqlalchemy import inspect
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage
from typing_extensions import Annotated, TypedDict
from langgraph.graph import START, StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_community.utilities import SQLDatabase
from langchain_core.runnables.config import RunnableConfig

def _set_env(var: str):
    if not os.environ.get(var):
        # os.environ[var] = getpass.getpass(f"{var}: ")
        os.environ[var] = "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"

_set_env("NVIDIA_API_KEY")

model = ChatNVIDIA(model="meta/llama-3.3-70b-instruct")
db = SQLDatabase.from_uri("postgresql://anc2:admin@localhost:5432/finycsdb")
query_prompt_template = hub.pull("langchain-ai/sql-query-system-prompt")

# print("FINYCS DB==>", query_prompt_template)

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
      "inferred_relationships": {}
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
    "numbers_app_historicalparentaccount": {
      "columns": {
        "id": "BigIntegerField",
        "name": "CharField",
        "account_type": "CharField",
        "is_custom": "BooleanField",
        "account_number": "CharField",
        "meta_data": "JSONField",
        "history_change_reason": "TextField",
        "parent_account": "ForeignKey",
        "business": "ForeignKey",
        "history_id": "AutoField",
        "history_date": "DateTimeField",
        "history_type": "CharField",
        "history_user": "ForeignKey"
      },
      "foreign_keys": {
        "parent_account": "numbers_app_parentaccount",
        "business": "numbers_app_business",
        "history_user": "numbers_app_user"
      },
      "choices": {
        "account_type": {
          "ASSET": "Asset",
          "LIABILITY": "Liability",
          "INCOME": "Income",
          "EXPENSE": "Expense",
          "EQUITY": "Equity"
        },
        "history_type": {
          "+": "Created",
          "~": "Changed",
          "-": "Deleted"
        }
      },
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
      "inferred_relationships": {}
    },
    "numbers_app_historicalaccount": {
      "columns": {
        "id": "BigIntegerField",
        "name": "CharField",
        "is_custom": "BooleanField",
        "history_change_reason": "TextField",
        "parent_account": "ForeignKey",
        "history_id": "AutoField",
        "history_date": "DateTimeField",
        "history_type": "CharField",
        "history_user": "ForeignKey"
      },
      "foreign_keys": {
        "parent_account": "numbers_app_parentaccount",
        "history_user": "numbers_app_user"
      },
      "choices": {
        "history_type": {
          "+": "Created",
          "~": "Changed",
          "-": "Deleted"
        }
      },
      "inferred_relationships": {}
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
      "inferred_relationships": {}
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
      "inferred_relationships": {}
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
      "inferred_relationships": {}
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
      "inferred_relationships": {}
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
      }
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
      "inferred_relationships": {}
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
      }
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
    "numbers_app_historicalparty": {
      "columns": {
        "id": "BigIntegerField",
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
        "preferred_payment_method": "CharField",
        "opening_balance": "DecimalField",
        "opening_balance_transaction_type": "CharField",
        "opening_balance_as_on_date": "DateTimeField",
        "gstin": "CharField",
        "tpin": "CharField",
        "gst_registration_type": "CharField",
        "other_details": "TextField",
        "is_inactive": "BooleanField",
        "is_tds_applicable": "BooleanField",
        "note": "TextField",
        "attachment": "TextField",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField",
        "meta_data": "JSONField",
        "history_change_reason": "TextField",
        "currency": "ForeignKey",
        "payment_term": "ForeignKey",
        "billing_address": "ForeignKey",
        "shipping_address": "ForeignKey",
        "account": "ForeignKey",
        "business": "ForeignKey",
        "opening_balance_journal_entry": "ForeignKey",
        "created_by": "ForeignKey",
        "updated_by": "ForeignKey",
        "history_id": "AutoField",
        "history_date": "DateTimeField",
        "history_type": "CharField",
        "history_user": "ForeignKey"
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
        "updated_by": "numbers_app_user",
        "history_user": "numbers_app_user"
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
        },
        "history_type": {
          "+": "Created",
          "~": "Changed",
          "-": "Deleted"
        }
      },
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
      "inferred_relationships": {}
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
    "numbers_app_historicaltax": {
      "columns": {
        "id": "BigIntegerField",
        "tax_type": "CharField",
        "rate": "DecimalField",
        "name": "CharField",
        "is_custom": "BooleanField",
        "is_removed": "BooleanField",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField",
        "history_change_reason": "TextField",
        "business": "ForeignKey",
        "created_by": "ForeignKey",
        "updated_by": "ForeignKey",
        "history_id": "AutoField",
        "history_date": "DateTimeField",
        "history_type": "CharField",
        "history_user": "ForeignKey"
      },
      "foreign_keys": {
        "business": "numbers_app_business",
        "created_by": "numbers_app_user",
        "updated_by": "numbers_app_user",
        "history_user": "numbers_app_user"
      },
      "choices": {
        "tax_type": {
          "GST": "GST",
          "IGST": "IGST",
          "CESS": "CESS"
        },
        "history_type": {
          "+": "Created",
          "~": "Changed",
          "-": "Deleted"
        }
      },
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
    "numbers_app_historicalitems": {
      "columns": {
        "id": "BigIntegerField",
        "item_type": "CharField",
        "name": "CharField",
        "description": "TextField",
        "for_purchase": "BooleanField",
        "for_sales": "BooleanField",
        "is_purchase_inclusive": "BooleanField",
        "is_sales_inclusive": "BooleanField",
        "hsn_sac_code": "CharField",
        "cost_price": "DecimalField",
        "selling_price": "DecimalField",
        "gst_rate": "DecimalField",
        "cess_rate": "DecimalField",
        "opening_stock": "DecimalField",
        "current_stock": "DecimalField",
        "as_of_date": "DateTimeField",
        "is_low_stock_reminder_active": "BooleanField",
        "low_stock_value": "DecimalField",
        "stock_item_code": "CharField",
        "is_removed": "BooleanField",
        "attachment": "TextField",
        "is_low_stock_reminder_sent": "BooleanField",
        "is_negative_stock_reminder_sent": "BooleanField",
        "meta_data": "JSONField",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField",
        "history_change_reason": "TextField",
        "unit": "ForeignKey",
        "purchase_account": "ForeignKey",
        "sales_account": "ForeignKey",
        "tax": "ForeignKey",
        "business": "ForeignKey",
        "created_by": "ForeignKey",
        "updated_by": "ForeignKey",
        "history_id": "AutoField",
        "history_date": "DateTimeField",
        "history_type": "CharField",
        "history_user": "ForeignKey"
      },
      "foreign_keys": {
        "unit": "numbers_app_units",
        "purchase_account": "numbers_app_chartofaccount",
        "sales_account": "numbers_app_chartofaccount",
        "tax": "numbers_app_tax",
        "business": "numbers_app_business",
        "created_by": "numbers_app_user",
        "updated_by": "numbers_app_user",
        "history_user": "numbers_app_user"
      },
      "choices": {
        "item_type": {
          "goods": "Goods",
          "service": "Service"
        },
        "history_type": {
          "+": "Created",
          "~": "Changed",
          "-": "Deleted"
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
      "inferred_relationships": {}
    },
    "numbers_app_historicalitemstockadjustment": {
      "columns": {
        "id": "BigIntegerField",
        "is_stock_in": "BooleanField",
        "reason": "TextField",
        "adjustment_date": "DateTimeField",
        "stock_adjustment_value": "DecimalField",
        "is_removed": "BooleanField",
        "is_manual": "BooleanField",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField",
        "history_change_reason": "TextField",
        "item": "ForeignKey",
        "created_by": "ForeignKey",
        "updated_by": "ForeignKey",
        "history_id": "AutoField",
        "history_date": "DateTimeField",
        "history_type": "CharField",
        "history_user": "ForeignKey"
      },
      "foreign_keys": {
        "item": "numbers_app_items",
        "created_by": "numbers_app_user",
        "updated_by": "numbers_app_user",
        "history_user": "numbers_app_user"
      },
      "choices": {
        "history_type": {
          "+": "Created",
          "~": "Changed",
          "-": "Deleted"
        }
      },
      "inferred_relationships": {}
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
      "inferred_relationships": {}
    },
    "numbers_app_historicalrecurringinvoice": {
      "columns": {
        "profile_name": "CharField",
        "repeat_every": "IntegerField",
        "repeat_frequency": "CharField",
        "preference": "CharField",
        "invoice_data": "JSONField",
        "attachment": "TextField",
        "starts_on": "DateTimeField",
        "ends_on": "DateTimeField",
        "never_expires": "BooleanField",
        "is_active": "BooleanField",
        "is_removed": "BooleanField",
        "last_run_at": "DateTimeField",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField",
        "history_change_reason": "TextField",
        "business": "ForeignKey",
        "customer": "ForeignKey",
        "periodic_task": "ForeignKey",
        "created_by": "ForeignKey",
        "updated_by": "ForeignKey",
        "history_id": "AutoField",
        "history_date": "DateTimeField",
        "history_type": "CharField",
        "history_user": "ForeignKey"
      },
      "foreign_keys": {
        "business": "numbers_app_business",
        "customer": "numbers_app_party",
        "periodic_task": "django_celery_beat_periodictask",
        "created_by": "numbers_app_user",
        "updated_by": "numbers_app_user",
        "history_user": "numbers_app_user"
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
        },
        "history_type": {
          "+": "Created",
          "~": "Changed",
          "-": "Deleted"
        }
      },
      "inferred_relationships": {}
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
      "inferred_relationships": {}
    },
    "numbers_app_historicalinvoice": {
      "columns": {
        "id": "BigIntegerField",
        "business_address": "JSONField",
        "invoice_title": "CharField",
        "invoice_sub_heading": "CharField",
        "customer_emails": "JSONField",
        "invoice_number": "CharField",
        "invoice_date": "DateTimeField",
        "due_date": "DateTimeField",
        "order_number": "CharField",
        "place_of_supply": "JSONField",
        "tax_applied": "CharField",
        "payment_status": "CharField",
        "payment_method": "CharField",
        "received_payment_amount": "DecimalField",
        "last_payment_date": "DateTimeField",
        "shipping_address": "TextField",
        "billing_address": "TextField",
        "attachment": "TextField",
        "note": "TextField",
        "subtotal": "DecimalField",
        "discount": "DecimalField",
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
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField",
        "exchange_rate": "DecimalField",
        "is_recurring": "BooleanField",
        "history_change_reason": "TextField",
        "business": "ForeignKey",
        "journal_entry": "ForeignKey",
        "customer": "ForeignKey",
        "payment_term": "ForeignKey",
        "sales_person": "ForeignKey",
        "terms_and_conditions": "ForeignKey",
        "tds_tcs": "ForeignKey",
        "created_by": "ForeignKey",
        "updated_by": "ForeignKey",
        "currency": "ForeignKey",
        "recurring_invoice": "ForeignKey",
        "history_id": "AutoField",
        "history_date": "DateTimeField",
        "history_type": "CharField",
        "history_user": "ForeignKey"
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
        "recurring_invoice": "numbers_app_recurringinvoice",
        "history_user": "numbers_app_user"
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
        },
        "history_type": {
          "+": "Created",
          "~": "Changed",
          "-": "Deleted"
        }
      },
      "inferred_relationships": {}
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
      "inferred_relationships": {}
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
      "inferred_relationships": {}
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
    "numbers_app_historicalbill": {
      "columns": {
        "id": "BigIntegerField",
        "business_address": "JSONField",
        "bill_title": "CharField",
        "bill_sub_heading": "CharField",
        "order_number": "CharField",
        "bill_number": "CharField",
        "bill_date": "DateTimeField",
        "due_date": "DateTimeField",
        "source_of_supply": "JSONField",
        "tax_applied": "CharField",
        "payment_status": "CharField",
        "payment_method": "CharField",
        "paid_payment_amount": "DecimalField",
        "last_payment_date": "DateTimeField",
        "mailing_address": "TextField",
        "attachment": "TextField",
        "note": "TextField",
        "subtotal": "DecimalField",
        "discount": "DecimalField",
        "tax": "JSONField",
        "tds_tcs_choice": "CharField",
        "tds_tcs_amount": "DecimalField",
        "total_amount": "DecimalField",
        "is_draft": "BooleanField",
        "is_removed": "BooleanField",
        "has_rcm": "BooleanField",
        "reason_for_update": "TextField",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField",
        "exchange_rate": "DecimalField",
        "history_change_reason": "TextField",
        "business": "ForeignKey",
        "journal_entry": "ForeignKey",
        "vendor": "ForeignKey",
        "payment_term": "ForeignKey",
        "tds_tcs": "ForeignKey",
        "created_by": "ForeignKey",
        "updated_by": "ForeignKey",
        "currency": "ForeignKey",
        "history_id": "AutoField",
        "history_date": "DateTimeField",
        "history_type": "CharField",
        "history_user": "ForeignKey"
      },
      "foreign_keys": {
        "business": "numbers_app_business",
        "journal_entry": "numbers_app_journalentry",
        "vendor": "numbers_app_party",
        "payment_term": "numbers_app_paymentterms",
        "tds_tcs": "numbers_app_tdstcsdetails",
        "created_by": "numbers_app_user",
        "updated_by": "numbers_app_user",
        "currency": "numbers_app_currency",
        "history_user": "numbers_app_user"
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
        },
        "history_type": {
          "+": "Created",
          "~": "Changed",
          "-": "Deleted"
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
      "inferred_relationships": {}
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
      "inferred_relationships": {}
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
    "numbers_app_historicalsalesorder": {
      "columns": {
        "id": "BigIntegerField",
        "business_address": "JSONField",
        "customer_emails": "JSONField",
        "sales_order_number": "CharField",
        "sales_order_date": "DateTimeField",
        "expected_shipment_date": "DateTimeField",
        "reference_number": "CharField",
        "place_of_supply": "JSONField",
        "tax_applied": "CharField",
        "shipping_address": "TextField",
        "billing_address": "TextField",
        "delivery_method": "CharField",
        "attachment": "TextField",
        "note": "TextField",
        "subtotal": "DecimalField",
        "discount": "DecimalField",
        "tax": "JSONField",
        "total_amount": "DecimalField",
        "is_draft": "BooleanField",
        "is_sent": "BooleanField",
        "is_removed": "BooleanField",
        "is_converted_to_invoice": "BooleanField",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField",
        "exchange_rate": "DecimalField",
        "history_change_reason": "TextField",
        "business": "ForeignKey",
        "customer": "ForeignKey",
        "payment_term": "ForeignKey",
        "sales_person": "ForeignKey",
        "terms_and_conditions": "ForeignKey",
        "invoice": "ForeignKey",
        "created_by": "ForeignKey",
        "updated_by": "ForeignKey",
        "currency": "ForeignKey",
        "history_id": "AutoField",
        "history_date": "DateTimeField",
        "history_type": "CharField",
        "history_user": "ForeignKey"
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
        "currency": "numbers_app_currency",
        "history_user": "numbers_app_user"
      },
      "choices": {
        "tax_applied": {
          "inclusive": "Inclusive",
          "exclusive": "Exclusive",
          "no_tax": "No Tax"
        },
        "history_type": {
          "+": "Created",
          "~": "Changed",
          "-": "Deleted"
        }
      },
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
      "inferred_relationships": {}
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
      "inferred_relationships": {}
    },
    "numbers_app_historicalpurchaseorder": {
      "columns": {
        "id": "BigIntegerField",
        "business_address": "JSONField",
        "vendor_emails": "JSONField",
        "purchase_order_number": "CharField",
        "purchase_order_date": "DateTimeField",
        "expected_delivery_date": "DateTimeField",
        "reference_number": "CharField",
        "source_of_supply": "JSONField",
        "tax_applied": "CharField",
        "mailing_address": "TextField",
        "shipment_preference": "CharField",
        "attachment": "TextField",
        "note": "TextField",
        "subtotal": "DecimalField",
        "discount": "DecimalField",
        "tax": "JSONField",
        "total_amount": "DecimalField",
        "is_draft": "BooleanField",
        "is_sent": "BooleanField",
        "is_removed": "BooleanField",
        "is_converted_to_bill": "BooleanField",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField",
        "exchange_rate": "DecimalField",
        "history_change_reason": "TextField",
        "business": "ForeignKey",
        "vendor": "ForeignKey",
        "payment_term": "ForeignKey",
        "terms_and_conditions": "ForeignKey",
        "bill": "ForeignKey",
        "created_by": "ForeignKey",
        "updated_by": "ForeignKey",
        "currency": "ForeignKey",
        "history_id": "AutoField",
        "history_date": "DateTimeField",
        "history_type": "CharField",
        "history_user": "ForeignKey"
      },
      "foreign_keys": {
        "business": "numbers_app_business",
        "vendor": "numbers_app_party",
        "payment_term": "numbers_app_paymentterms",
        "terms_and_conditions": "numbers_app_termsandconditions",
        "bill": "numbers_app_bill",
        "created_by": "numbers_app_user",
        "updated_by": "numbers_app_user",
        "currency": "numbers_app_currency",
        "history_user": "numbers_app_user"
      },
      "choices": {
        "tax_applied": {
          "inclusive": "Inclusive",
          "exclusive": "Exclusive",
          "no_tax": "No Tax"
        },
        "history_type": {
          "+": "Created",
          "~": "Changed",
          "-": "Deleted"
        }
      },
      "inferred_relationships": {}
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
      "inferred_relationships": {}
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
      "inferred_relationships": {}
    },
    "numbers_app_historicalpayment": {
      "columns": {
        "id": "BigIntegerField",
        "payment_type": "CharField",
        "payment_method": "CharField",
        "payment_date": "DateTimeField",
        "reference": "CharField",
        "total_amount": "DecimalField",
        "total_payment_amount": "DecimalField",
        "balance_amount": "DecimalField",
        "refunded_amount": "DecimalField",
        "note": "TextField",
        "attachment": "TextField",
        "is_sent": "BooleanField",
        "is_removed": "BooleanField",
        "exchange_rate": "DecimalField",
        "is_tds_applicable": "BooleanField",
        "has_rcm": "BooleanField",
        "is_advance": "BooleanField",
        "tax_summary": "JSONField",
        "place_of_supply": "JSONField",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField",
        "history_change_reason": "TextField",
        "business": "ForeignKey",
        "journal_entry": "ForeignKey",
        "party": "ForeignKey",
        "account": "ForeignKey",
        "tds_account": "ForeignKey",
        "currency": "ForeignKey",
        "tax": "ForeignKey",
        "created_by": "ForeignKey",
        "updated_by": "ForeignKey",
        "history_id": "AutoField",
        "history_date": "DateTimeField",
        "history_type": "CharField",
        "history_user": "ForeignKey"
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
        "updated_by": "numbers_app_user",
        "history_user": "numbers_app_user"
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
        },
        "history_type": {
          "+": "Created",
          "~": "Changed",
          "-": "Deleted"
        }
      },
      "inferred_relationships": {}
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
      "inferred_relationships": {}
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
    "numbers_app_historicalestimate": {
      "columns": {
        "id": "BigIntegerField",
        "business_address": "JSONField",
        "customer_emails": "JSONField",
        "estimate_number": "CharField",
        "estimate_date": "DateTimeField",
        "expiry_date": "DateTimeField",
        "reference_number": "CharField",
        "place_of_supply": "JSONField",
        "tax_applied": "CharField",
        "shipping_address": "TextField",
        "billing_address": "TextField",
        "attachment": "TextField",
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
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField",
        "exchange_rate": "DecimalField",
        "history_change_reason": "TextField",
        "business": "ForeignKey",
        "customer": "ForeignKey",
        "sales_person": "ForeignKey",
        "terms_and_conditions": "ForeignKey",
        "invoice": "ForeignKey",
        "sales_order": "ForeignKey",
        "created_by": "ForeignKey",
        "updated_by": "ForeignKey",
        "currency": "ForeignKey",
        "history_id": "AutoField",
        "history_date": "DateTimeField",
        "history_type": "CharField",
        "history_user": "ForeignKey"
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
        "currency": "numbers_app_currency",
        "history_user": "numbers_app_user"
      },
      "choices": {
        "tax_applied": {
          "inclusive": "Inclusive",
          "exclusive": "Exclusive",
          "no_tax": "No Tax"
        },
        "history_type": {
          "+": "Created",
          "~": "Changed",
          "-": "Deleted"
        }
      },
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
      "inferred_relationships": {}
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
      "inferred_relationships": {}
    },
    "numbers_app_historicalexportedfiles": {
      "columns": {
        "id": "BigIntegerField",
        "description": "CharField",
        "document": "TextField",
        "document_type": "CharField",
        "durations_start_date": "DateTimeField",
        "duration_end_date": "DateTimeField",
        "meta_data": "JSONField",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField",
        "history_change_reason": "TextField",
        "business": "ForeignKey",
        "created_by": "ForeignKey",
        "updated_by": "ForeignKey",
        "history_id": "AutoField",
        "history_date": "DateTimeField",
        "history_type": "CharField",
        "history_user": "ForeignKey"
      },
      "foreign_keys": {
        "business": "numbers_app_business",
        "created_by": "numbers_app_user",
        "updated_by": "numbers_app_user",
        "history_user": "numbers_app_user"
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
        },
        "history_type": {
          "+": "Created",
          "~": "Changed",
          "-": "Deleted"
        }
      },
      "inferred_relationships": {}
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
    "numbers_app_historicalcreditnote": {
      "columns": {
        "id": "BigIntegerField",
        "business_address": "JSONField",
        "customer_emails": "JSONField",
        "credit_note_number": "CharField",
        "credit_note_date": "DateTimeField",
        "place_of_supply": "JSONField",
        "tax_applied": "CharField",
        "reason": "CharField",
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
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField",
        "exchange_rate": "DecimalField",
        "history_change_reason": "TextField",
        "business": "ForeignKey",
        "journal_entry": "ForeignKey",
        "customer": "ForeignKey",
        "sales_person": "ForeignKey",
        "terms_and_conditions": "ForeignKey",
        "against_invoice": "ForeignKey",
        "created_by": "ForeignKey",
        "updated_by": "ForeignKey",
        "currency": "ForeignKey",
        "history_id": "AutoField",
        "history_date": "DateTimeField",
        "history_type": "CharField",
        "history_user": "ForeignKey"
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
        "currency": "numbers_app_currency",
        "history_user": "numbers_app_user"
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
        },
        "history_type": {
          "+": "Created",
          "~": "Changed",
          "-": "Deleted"
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
      "inferred_relationships": {}
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
      "inferred_relationships": {}
    },
    "numbers_app_historicaldebitnote": {
      "columns": {
        "id": "BigIntegerField",
        "business_address": "JSONField",
        "vendor_emails": "JSONField",
        "debit_note_number": "CharField",
        "debit_note_date": "DateTimeField",
        "source_of_supply": "JSONField",
        "tax_applied": "CharField",
        "reason": "CharField",
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
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField",
        "exchange_rate": "DecimalField",
        "history_change_reason": "TextField",
        "business": "ForeignKey",
        "journal_entry": "ForeignKey",
        "vendor": "ForeignKey",
        "terms_and_conditions": "ForeignKey",
        "against_bill": "ForeignKey",
        "created_by": "ForeignKey",
        "updated_by": "ForeignKey",
        "currency": "ForeignKey",
        "history_id": "AutoField",
        "history_date": "DateTimeField",
        "history_type": "CharField",
        "history_user": "ForeignKey"
      },
      "foreign_keys": {
        "business": "numbers_app_business",
        "journal_entry": "numbers_app_journalentry",
        "vendor": "numbers_app_party",
        "terms_and_conditions": "numbers_app_termsandconditions",
        "against_bill": "numbers_app_bill",
        "created_by": "numbers_app_user",
        "updated_by": "numbers_app_user",
        "currency": "numbers_app_currency",
        "history_user": "numbers_app_user"
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
        },
        "history_type": {
          "+": "Created",
          "~": "Changed",
          "-": "Deleted"
        }
      },
      "inferred_relationships": {}
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
      "inferred_relationships": {}
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
      "inferred_relationships": {}
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
    "numbers_app_historicaldeliverychallan": {
      "columns": {
        "id": "BigIntegerField",
        "business_address": "JSONField",
        "delivery_challan_number": "CharField",
        "delivery_challan_date": "DateTimeField",
        "reference_number": "CharField",
        "place_of_supply": "JSONField",
        "tax_applied": "CharField",
        "shipping_address": "TextField",
        "billing_address": "TextField",
        "challan_type": "CharField",
        "attachment": "TextField",
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
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField",
        "exchange_rate": "DecimalField",
        "history_change_reason": "TextField",
        "business": "ForeignKey",
        "customer": "ForeignKey",
        "terms_and_conditions": "ForeignKey",
        "invoice": "ForeignKey",
        "created_by": "ForeignKey",
        "updated_by": "ForeignKey",
        "currency": "ForeignKey",
        "history_id": "AutoField",
        "history_date": "DateTimeField",
        "history_type": "CharField",
        "history_user": "ForeignKey"
      },
      "foreign_keys": {
        "business": "numbers_app_business",
        "customer": "numbers_app_party",
        "terms_and_conditions": "numbers_app_termsandconditions",
        "invoice": "numbers_app_invoice",
        "created_by": "numbers_app_user",
        "updated_by": "numbers_app_user",
        "currency": "numbers_app_currency",
        "history_user": "numbers_app_user"
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
        },
        "history_type": {
          "+": "Created",
          "~": "Changed",
          "-": "Deleted"
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
      "inferred_relationships": {}
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
    "numbers_app_historicalexpense": {
      "columns": {
        "id": "BigIntegerField",
        "expense_date": "DateTimeField",
        "expense_type": "CharField",
        "exchange_rate": "DecimalField",
        "source_of_supply": "JSONField",
        "destination_of_supply": "JSONField",
        "gst_registration_type": "CharField",
        "gstin_number": "CharField",
        "reference_invoice_number": "CharField",
        "tax_applied": "CharField",
        "subtotal": "DecimalField",
        "tax": "JSONField",
        "total_amount": "DecimalField",
        "attachment": "TextField",
        "has_rcm": "BooleanField",
        "is_billable": "BooleanField",
        "mark_up_percent": "DecimalField",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField",
        "is_recurring": "BooleanField",
        "history_change_reason": "TextField",
        "is_removed": "BooleanField",
        "business": "ForeignKey",
        "vendor": "ForeignKey",
        "customer": "ForeignKey",
        "journal_entry": "ForeignKey",
        "paid_through_account": "ForeignKey",
        "currency": "ForeignKey",
        "invoice": "ForeignKey",
        "created_by": "ForeignKey",
        "updated_by": "ForeignKey",
        "recurring_expense": "ForeignKey",
        "history_id": "AutoField",
        "history_date": "DateTimeField",
        "history_type": "CharField",
        "history_user": "ForeignKey"
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
        "recurring_expense": "numbers_app_recurringexpense",
        "history_user": "numbers_app_user"
      },
      "choices": {
        "tax_applied": {
          "inclusive": "Inclusive",
          "exclusive": "Exclusive",
          "no_tax": "No Tax"
        },
        "history_type": {
          "+": "Created",
          "~": "Changed",
          "-": "Deleted"
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
      "inferred_relationships": {}
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
      "inferred_relationships": {}
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
    "numbers_app_historicalrecurringexpense": {
      "columns": {
        "profile_name": "CharField",
        "repeat_every": "IntegerField",
        "repeat_frequency": "CharField",
        "preference": "CharField",
        "expense_data": "JSONField",
        "attachment": "TextField",
        "starts_on": "DateTimeField",
        "ends_on": "DateTimeField",
        "never_expires": "BooleanField",
        "is_active": "BooleanField",
        "is_removed": "BooleanField",
        "last_run_at": "DateTimeField",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField",
        "history_change_reason": "TextField",
        "business": "ForeignKey",
        "vendor": "ForeignKey",
        "periodic_task": "ForeignKey",
        "created_by": "ForeignKey",
        "updated_by": "ForeignKey",
        "history_id": "AutoField",
        "history_date": "DateTimeField",
        "history_type": "CharField",
        "history_user": "ForeignKey"
      },
      "foreign_keys": {
        "business": "numbers_app_business",
        "vendor": "numbers_app_party",
        "periodic_task": "django_celery_beat_periodictask",
        "created_by": "numbers_app_user",
        "updated_by": "numbers_app_user",
        "history_user": "numbers_app_user"
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
        },
        "history_type": {
          "+": "Created",
          "~": "Changed",
          "-": "Deleted"
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
      "inferred_relationships": {}
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
    "numbers_app_historicalschedulereport": {
      "columns": {
        "repeat_frequency": "CharField",
        "starts_on": "DateTimeField",
        "report_data": "JSONField",
        "is_active": "BooleanField",
        "report_name": "CharField",
        "last_runtime": "DateTimeField",
        "created_at": "DateTimeField",
        "updated_at": "DateTimeField",
        "history_change_reason": "TextField",
        "business": "ForeignKey",
        "periodic_task": "ForeignKey",
        "history_id": "AutoField",
        "history_date": "DateTimeField",
        "history_type": "CharField",
        "history_user": "ForeignKey"
      },
      "foreign_keys": {
        "business": "numbers_app_business",
        "periodic_task": "django_celery_beat_periodictask",
        "history_user": "numbers_app_user"
      },
      "choices": {
        "history_type": {
          "+": "Created",
          "~": "Changed",
          "-": "Deleted"
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
    "numbers_app_historicaldocumentlinkdata": {
      "columns": {
        "id": "BigIntegerField",
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
        "updated_at": "DateTimeField",
        "history_change_reason": "TextField",
        "business": "ForeignKey",
        "history_id": "AutoField",
        "history_date": "DateTimeField",
        "history_type": "CharField",
        "history_user": "ForeignKey"
      },
      "foreign_keys": {
        "business": "numbers_app_business",
        "history_user": "numbers_app_user"
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
        },
        "history_type": {
          "+": "Created",
          "~": "Changed",
          "-": "Deleted"
        }
      },
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

# state definition
class State(TypedDict):
    user_query: str
    sql_query: str
    sql_query_result: str
    query_rows: list
    attempts: int
    relevance: str
    sql_error: bool
    readable_resp: Any
    chart_type: str
    output_format: str
    formatted_chart_data : Any
    current_user: str
    current_business: int

def get_database_schema(db):
    """
    Returns a detailed database schema representation.
    
    Args:
        db: SQLDatabase instance
    
    Returns:
        str: A string representation of the database schema
    """

    inspector = inspect(db._engine)
    
    schema = ""
    for table_name in inspector.get_table_names():
        schema += f"Table: {table_name}\n"
        
        # Get columns
        for column in inspector.get_columns(table_name):
            col_name = column["name"]
            col_type = str(column["type"])
            
            # Check if it's a primary key
            pk_constraint = inspector.get_pk_constraint(table_name)
            if pk_constraint and col_name in pk_constraint.get('constrained_columns', []):
                col_type += ", Primary Key"
            
            # Check for foreign keys
            fk_constraints = inspector.get_foreign_keys(table_name)
            for fk in fk_constraints:
                if col_name in fk.get('constrained_columns', []):
                    referred_table = fk.get('referred_table')
                    referred_columns = fk.get('referred_columns')
                    if referred_table and referred_columns:
                        col_type += f", Foreign Key to {referred_table}.{referred_columns[0]}"
            
            schema += f"- {col_name}: {col_type}\n"
        
        schema += "\n"
    
    print("Retrieved detailed database schema.")
    return schema

# def get_database_schema(db):
#     """Returns the database schema in JSON format."""
#     inspector = inspect(db._engine)
    
#     schema = {}
#     for table_name in inspector.get_table_names():
#         columns = []
#         for column in inspector.get_columns(table_name):
#             col_info = {
#                 "name": column["name"],
#                 "type": str(column["type"]),
#                 "primary_key": column["name"] in inspector.get_pk_constraint(table_name).get("constrained_columns", []),
#                 "foreign_key": None,
#             }
#             fk_constraints = inspector.get_foreign_keys(table_name)
#             for fk in fk_constraints:
#                 if column["name"] in fk.get("constrained_columns", []):
#                     col_info["foreign_key"] = f"{fk.get('referred_table')}.{fk.get('referred_columns')[0]}"
            
#             columns.append(col_info)
        
#         schema[table_name] = columns
#     # print("NEW SCHEMA", schema)
#     return json.dumps(schema, indent=4)

# Node 1: Get Current User
class GetCurrentUser(BaseModel):
    current_user: str = Field(
        description="The name of the current user based on the provided user ID."
    )

def get_current_user(state:State, config: RunnableConfig):
    print("Retrieving the current user based on user ID.")
    user_id = config["configurable"].get("current_user_id", None)
    user_id = 5
    if not user_id:
        state["current_user"] = "User not found"
        print("No user ID provided in the configuration.")
        return state
    # Execute SQL to get user info
    try:
        query = f"SELECT name FROM numbers_app_user WHERE id = {user_id}"
        result = db.run(query)
        
        if result and result.strip():
            state["current_user"] = result.strip()
            state["current_business"] = 198
            print(f"Current user set to: {state['current_user']}")
        else:
            state["current_user"] = "User not found"
            print("User not found in the database.")
    except Exception as e:
        state["current_user"] = "Error retrieving user"
        print(f"Error retrieving user: {str(e)}")
    
    return state

# Node 1: Check Relevance
class RelevanceOutput(BaseModel):
    """Determines if the query is relevant to the database schema."""
    relevance: str = Field(
        description="Indicates whether the question is related to the database schema. 'relevant' or 'not_relevant'."
    )

def check_relevance(state: State):
    """Check if the user query is relevant to the database schema and ensures it is a read-only query."""
    print(f"Checking relevance of the question: {state['user_query']}")
    # detailed_schema = get_database_schema(db)
    detailed_schema = database_schema

    messages = [
        HumanMessage(content=f"""
        You are an assistant that determines whether a given question is related to the following database schema and ensures it is a read-only query.

        **Schema:**
        {detailed_schema}

        **Question:** {state['user_query']}
        
        **Rules:**
        1. If the question requires retrieving data (e.g., SELECT queries for viewing records), respond with **"relevant"**.
        2. If the question suggests modifying the database (e.g., inserting, updating, deleting, or altering data), respond with **"non_relevant"**.
        3. If the intent of the question is unclear but hints at data manipulation, assume it is **"non_relevant"**.

        **Examples:**
        - "What was my revenue last quarter?" → **relevant**
        - "How many sales did I make last month?" → **relevant**
        - "Delete my last invoice." → **non_relevant**
        - "Update my revenue data for Q1." → **non_relevant**
        - "Insert a new transaction for $500." → **non_relevant**

        **Respond with ONLY "relevant" or "non_relevant" and nothing else.**
        """)
    ]

    structured_llm = model.with_structured_output(RelevanceOutput)
    result = structured_llm.invoke(messages)
    state["relevance"] = result.relevance
    print(f"Relevance determined: {state['relevance']}")

    # Initialize attempts counter
    state["attempts"] = 0
    state["sql_error"] = False
    state["query_rows"] = []
    
    return state

class OutputFormat(BaseModel):
    """Determines what should be the output type for the user question."""
    output_format: str
    
def determine_output_format(state: State):
    """Determine if the response should be in text or graph format."""
    print(f"Determining output format for: {state['user_query']}")

    messages = [
        HumanMessage(content=f"""
        You are an assistant that determines whether the output format for a given question should be **text** or **graph**.
        Question: {state["user_query"]}
        
        **Rules:**
        1. If the question asks for a **trend, comparison, growth rate, distribution, or any form of analytical insights**, respond with **"graph"**.
        2. If the question asks for a **single value, a count, a straightforward metric, or a direct lookup**, respond with **"text"**.
        3. Assume the user expects an easily interpretable response in the most suitable format.
        
        **Examples:**
        - "What is sales growth for the last 3 months?" → **graph**
        - "Compare revenue of Q1 and Q2 this year." → **graph**
        - "Show me the trend of expenses in the last 6 months." → **graph**
        - "How many invoices were created last month?" → **text**
        - "What was my total revenue last quarter?" → **text**
        - "How many transactions were recorded today?" → **text**

        **Respond with ONLY "graph" or "text" and nothing else.**
        """)
    ]

    structured_llm = model.with_structured_output(OutputFormat)
    result = structured_llm.invoke(messages)
    state["output_format"] = result.output_format
    print(f"Output format determined: {state['output_format']}")

    return state

class ChartType(BaseModel):
    chart_type: str

def determine_chart_type(state: State):
    """Determine the most appropriate chart type based on the query intent."""
    print(f"Determining chart type for: {state['user_query']}")

    messages = [
        HumanMessage(content=f"""
        You are an assistant that determines the best **chart type** for visualizing financial data based on a given question.
        
        Question: {state["user_query"]}

        **Rules:**
        - **Line Chart** → For trends over time (e.g., "Show sales trend for the last 6 months").
        - **Bar Chart** → For comparisons across categories (e.g., "Compare revenue of Q1, Q2, Q3").
        - **Pie Chart** → For distribution of a whole (e.g., "What is the percentage of expenses by category?").
        
        **Examples:**
        - "What is sales growth for the last 3 months?" → **line_chart**
        - "Compare revenue of Q1 and Q2 this year." → **bar_chart**
        - "Show me expense breakdown by category." → **pie_chart**

        **Respond with ONLY "line_chart", "bar_chart", or "pie_chart".**
        """)
    ]

    structured_llm = model.with_structured_output(ChartType)
    result = structured_llm.invoke(messages)
    state["chart_type"] = result.chart_type
    print(f"Chart type determined ===>: {state['chart_type']}")

    return state

# def format_chart_data(state: State):
#     """Formats SQL query result into a Highcharts-compatible format based on chart type."""
    
#     query_result = state["query_rows"]
#     chart_type = state["chart_type"]

#     # If no results, return an empty dataset
#     if not query_result:
#         state["readable_resp"] = []
#         print("No data available for chart generation.")
#         return state

#     formatted_data = []

#     for row in query_result:
#         try:
#             formatted_data.append({
#                 "result": float(row.get("result", 0)),
#                 "tooltip": row.get("tooltip", None),
#                 "from_date": datetime.strptime(row["from_date"], "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d"),
#                 "to_date": datetime.strptime(row["to_date"], "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d"),
#             })
#         except Exception as e:
#             print(f"Error formatting row {row}: {e}")

#     state["readable_resp"] = formatted_data
#     print("Formatted data for Highcharts:", json.dumps(formatted_data, indent=2))
    
#     return state

# TODO: remove unecessary data. 
# add a period field to show the range of the data. 
# add name field as the data point name.
# store the result to show in a key called barChartData
# returns all data wrapped in a list
def format_chart_data(state: State):
    """Use LLM to format the query result into the required structure."""
    
    print(f"Formatting query result using LLM for output type: {state['output_format']}")
    print(state["query_rows"])
    messages = [
        HumanMessage(content=f"""
        You are an assistant that formats financial query results into the appropriate output format.
        
        **User Query:** {state["user_query"]}
        **Output Format:** {state["output_format"]}
        
        **Instructions:**
        - If the output format is **"text"**, return the result as a simple, human-readable string.
        - If the output format is **"graph"**, structure the response as a JSON list where:
          - Each entry represents a time period (e.g., month, quarter, or year).
          - Fields:
            - `"result"`: The numerical result (formatted as a string with two decimal places).
            - `"tooltip"`: Provide any additional helpful information (or `null` if not needed).
            - `"from_date"`: The start date of the period in `YYYY-MM-DDTHH:MM:SS` format.
            - `"to_date"`: The end date of the period in `YYYY-MM-DDTHH:MM:SS` format.
            - `"period"`: based on the from_date and to_date choose an appropriate name
        
        **Examples:**
        - If asked "What is sales growth for the last 3 months?", the response should be:
          ```json
          [
              {{"result": "3451687.00", "tooltip": null, "from_date": "2024-04-01T00:00:00", "to_date": "2024-04-30T00:00:00","period": "Jan 2024"}},
              {{"result": "2469717.00", "tooltip": null, "from_date": "2024-05-01T00:00:00", "to_date": "2024-05-31T00:00:00","period": "Feb 2024"}},
              {{"result": "2897087.00", "tooltip": null, "from_date": "2024-06-01T00:00:00", "to_date": "2024-06-30T00:00:00","period": "March 2024"}}
          ]
          ```
        - If asked "How many invoices were created last month?", return a simple string:
          `"There were 325 invoices created in February 2025."`
        
        **Query Result:**
        ```json
        {state["query_rows"]}
        ```
        
        **Generate ONLY the formatted output. Do NOT include explanations.**
        """)
    ]

    # structured_llm = model.with_structured_output(dict)  # Ensure output is JSON
    result = model.invoke(messages)

    # Store formatted output in state
    state["readable_resp"] = result['result']
    print("Formatted output successfully stored.")

    return state

# Node 2: Generate SQL Query
class QueryOutput(BaseModel):
    """Generated SQL query."""
    query: str = Field(..., description="Syntactically valid SQL query.")

# def generate_sql_query(state: State):
#     """Generate SQL query to fetch information."""
#     print(f"Converting question to SQL: {state['user_query']}")
#     detailed_schema = get_database_schema(db)

#     prompt = query_prompt_template.invoke(
#         {
#             "dialect": db.dialect,
#             "top_k": 10,
#             "table_info": detailed_schema,
#             "input": state['user_query'],
#         }
#     )
#     structured_llm = model.with_structured_output(QueryOutput)
#     result = structured_llm.invoke(prompt)
#     state["sql_query"] = result.query
#     print(f"Generated SQL query: {state['sql_query']}")
#     return state

def generate_sql_query(state: State):
    """Generate SQL query to fetch information."""
    # print(f"Converting question to SQL for user '{state['current_user']}' and business ID '{state['current_business']}': {state['user_query']}")
    # detailed_schema = get_database_schema(db)
    detailed_schema = database_schema
    
    # Modify the prompt to include both user and business context
    messages = [
        HumanMessage(content=f"""
        You are an intelligent SQL query generator and validator. Provided database schema belongs to financial accounting.
        Given an input question, create a syntactically correct {db.dialect} query to run to help find the answer.

        IMPORTANT: The current user is '{state['current_user']}' with user id 5 ignore the brackets and store only 
        the user name to make it suitable to use in further sql queries and the current business ID is 
        {state['current_business']}.
        Always scope your query to this specific user and business where applicable by adding appropriate WHERE clauses 
        that filter for both the current user's data and the current business.
        
        Unless the user specifies in their question a specific number of examples they wish to obtain, always limit your query 
        to at most {10} results. You can order the results by a relevant column to return the most interesting examples in the database.
        
        Never query for all the columns from a specific table, only ask for the few relevant columns given the question.
        
        Pay attention to use only the column names that you can see in the schema description. Be careful to not query for 
        columns that do not exist. Also, pay attention to which column is in which table.
        
        **Foreign Key Validation:**
           - **Check all foreign key constraints** against the schema and ensure correct joins.  
           - If a direct foreign key does not exist, determine the correct table **through inferred relationships**:
           - For financial transactions, **determine account type from parent_account table** (`INCOME`, `EXPENSE`) using:  
             - For financial transactions, **determine account type** (`INCOME`, `EXPENSE`) using:  
               `numbers_app_transaction.business_account → numbers_app_chartofaccount.account → numbers_app_parentaccount.account_type`.  
             - If querying business details, **link through** `numbers_app_business.id`.  
             - Use numbers_app_journalentry.transaction_date for filtering by financial year.
             - If filtering by **business name**, use `'legal_name'` instead of business_id.  
           - Fields ending in `_id` (e.g., `party_id`) **should be referenced as `.id`**.  
           - Foreign key fields not ending with _id you have to add _id for that foreign key field.
           
        **Query Optimization:**  
           - Ensure the query follows best practices for performance and accuracy.  
           - Avoid unnecessary subqueries or redundant joins.  
           - Use indexed columns where possible to optimize filtering.  
           
        **Additional Query Conditions for Financial Data:**
            1. Start from the `numbers_app_parentaccount` table to filter transactions based on `account_type`.
            2. Join `numbers_app_account`, `numbers_app_chartofaccount`, and `numbers_app_transaction` to link transactions to their respective accounts.
            3. Classify transactions as follows:
               - **Income Calculation:**
                 - Transactions where `account_type = 'INCOME'`:
                   - **Positive Value:** `transaction_type = 'CREDIT'`
                   - **Negative Value:** `transaction_type = 'DEBIT'` (subtract from total income)
               - **Expense Calculation:**
                 - Transactions where `account_type = 'EXPENSE'`:
                   - **Positive Value:** `transaction_type = 'DEBIT'`
                   - **Negative Value:** `transaction_type = 'CREDIT'` (subtract from total expenses)
            4. Filter transactions for the previous fiscal year using `date_trunc('year', NOW() - INTERVAL '1 year')`.
            5. Group results by month (`date_trunc('month', transaction_date)`) and order them in descending order.
            6. The query should be optimized for performance and avoid unnecessary joins.
            
        **Fiscal Year Handling (Country-Specific):**
            - The fiscal year **varies by country**. The current and previous fiscal years should be determined dynamically from the `numbers_app_fiscalyear` table.
            - The `numbers_app_fiscalyear` table stores fiscal year data as `month_range` for each `business_id`.
            - **Determine the fiscal year dynamically** based on today's date and retrieve the start and end dates from `numbers_app_fiscalyear` for the given business.
            - **Example for India (April - March Fiscal Year):**
              - If the query is about the **current fiscal year**, filter data from `2024-04-01` to `2025-03-31`.
              - If the query is about the **previous fiscal year**, filter data from `2023-04-01` to `2024-03-31`.
            - Use `numbers_app_journalentry.transaction_date` to filter transactions within the fiscal year.
            - When the query involves a fiscal year, ensure **exactly 12 monthly records** are retrieved.
           
        **Output Type Handling:**
             - If the user's question requires a **chart-based output**, structure the SQL response accordingly.
             - **Output Type: 'bar_chart'**
               - On SQL query execution, **generate the response in JSON format**.
               - Example output structure:
                 ```
                 [
                     {{ "income": income_amount, 
                        "expense": expense_amount, 
                        "start_date": month_name_and_year 
                     }},
                     ...
                 ]
                 ```
               - Ensure the response correctly **aggregates income and expense data** by month.
               - `start_date` should be formatted as `Month Year` (e.g., `"April 2024"`).
        When both user and business filters are applicable, make sure to include both conditions 
        (e.g., "WHERE user_id = X AND business_id = Y").
        
        Database Schema:
        {detailed_schema}
        
        User Question: {state['user_query']}
        """)
    ]
    
    structured_llm = model.with_structured_output(QueryOutput)
    result = structured_llm.invoke(messages)
    print("QUERY RESULT=====>",result)
    state["sql_query"] = result.query
    print(f"Generated SQL query: {state['sql_query']}")
    return state


# Node 3: Execute SQL Query
def execute_sql_query(state: State):
    """Execute the generated SQL query and store results."""
    sql_query = state["sql_query"].strip()
    print(f"Executing SQL query: {sql_query}")
    
    try:
        # Execute the query
        result = db.run(sql_query)
        # Parse the result to determine if it's empty
        if not result or result.strip() == "":
            state["query_rows"] = []
            state["sql_query_result"] = "No results found."
        else:
            state["sql_query_result"] = result
            state["query_rows"] = [{"result": result}]
            
        state["sql_error"] = False
        print("SQL query executed successfully.")
        
    except Exception as e:
        state["sql_query_result"] = f"Error executing query: {str(e)}"
        state["sql_error"] = True
        print(f"Error executing SQL query: {str(e)}")
    
    return state

# Node 4: Generate Funny Response (for irrelevant questions)
def generate_funny_response(state: State):
    """Generate a playful response for irrelevant questions."""
    print("Generating a funny response for an unrelated question.")
    
    messages = [
        HumanMessage(content="""
        You are a charming and funny assistant who responds in a playful manner.
        
        I can't help with that database query, as it doesn't seem related to our database schema.
        Please provide a friendly, humorous response encouraging the user to ask database-related questions instead.
        Make it brief and charming.
        """)
    ]
    
    response = model.invoke(messages)
    state["readable_resp"] = response.content
    print("Generated funny response.")
    
    return state

# Node 5: Regenerate Query
class RewrittenQuestion(BaseModel):
    """Rewritten version of the original question."""
    question: str = Field(description="The rewritten question to generate a better SQL query.")

def regenerate_query(state: State):
    """Rewrite the question to generate a better SQL query."""
    print("Regenerating the SQL query by rewriting the question.")
    
    messages = [
        HumanMessage(content=f"""
        You are an assistant that reformulates an original question to enable more precise SQL queries.
        
        Original Question: {state['user_query']}
        Error with previous query: {state['sql_query_result']}
        
        Reformulate the question to enable more precise SQL queries, ensuring all necessary details are preserved.
        Focus on fixing the specific error encountered.
        """)
    ]
    
    structured_llm = model.with_structured_output(RewrittenQuestion)
    result = structured_llm.invoke(messages)
    
    state["user_query"] = result.question
    state["attempts"] += 1
    print(f"Rewritten question (attempt {state['attempts']}): {state['user_query']}")
    
    return state

# Node 6: Generate Readable Response
def generate_readable_resp(state: State):
    """Generate a human-readable response based on the SQL query results."""
    print("Generating a human-readable answer.")
    
    messages = [
        HumanMessage(content=f"""
        You are a helpful assistant that converts SQL query results into clear, natural language responses.
        Start the response with a friendly greeting that includes the user's name.
        
        Current user: {state["current_user"]}
        User query: {state["user_query"]}
        SQL query used: {state["sql_query"]}
        Query result: {state["sql_query_result"]}
        
        Please generate a clear, concise response that answers the user's original question based on the SQL query results.
        Start with "Hello {state["current_user"]}," and then provide the requested information in a friendly manner.ignore the brackets and show only the user name
        """)
    ]
    
    response = model.invoke(messages)
    state["readable_resp"] = response.content
    print("Generated human-readable answer.")
    
    return state

# Node 7: Max Attempts Reached
def end_max_iterations(state: State):
    """Handle case when maximum attempts are reached."""
    print("Maximum attempts reached. Ending the workflow.")
    
    messages = [
        HumanMessage(content=f"""
        The system has tried multiple times to answer the following question but keeps encountering errors:
        
        Question: {state["user_query"]}
        
        Latest error: {state["sql_query_result"]}
        
        Please generate a polite message explaining that we couldn't process their request after multiple attempts.
        Suggest that they try rephrasing their question to be more specific about the database tables they want to query.
        """)
    ]
    
    response = model.invoke(messages)
    state["readable_resp"] = response.content
    
    return state

# Router functions
def relevance_router(state: State):
    """Route based on query relevance."""
    if state["relevance"].lower() == "relevant":
        return "generate_sql_query"
    else:
        return "generate_funny_response"

def execute_sql_router(state: State):
    """Route based on SQL execution result."""
    if not state.get("sql_error", False):
        return "determine_output_format"
    else:
        return "regenerate_query"

def output_format_router(state: State):
    """Route based on output format type."""
    if state["output_format"].lower() == "graph":
        return "determine_chart_type"
    else:
        return "generate_readable_resp"

def check_attempts_router(state: State):
    """Route based on number of attempts."""
    if state["attempts"] < 3:
        return "generate_sql_query"
    else:
        return "end_max_iterations"

# Defining workflow
workflow = StateGraph(State)

# Add nodes
workflow.add_node("get_current_user", get_current_user)
workflow.add_node("check_relevance", check_relevance)
workflow.add_node("generate_sql_query", generate_sql_query)
workflow.add_node("execute_sql_query", execute_sql_query)
workflow.add_node("determine_output_format", determine_output_format)
workflow.add_node("determine_chart_type", determine_chart_type)
workflow.add_node("format_chart_data", format_chart_data)
workflow.add_node("generate_readable_resp", generate_readable_resp)
workflow.add_node("regenerate_query", regenerate_query)
workflow.add_node("generate_funny_response", generate_funny_response)
workflow.add_node("end_max_iterations", end_max_iterations)

# Add edges
workflow.add_edge(START, "get_current_user")
workflow.add_edge("get_current_user", "check_relevance")

# Conditional routing after relevance check
workflow.add_conditional_edges(
    "check_relevance",
    relevance_router,
    {
        "generate_sql_query": "generate_sql_query",
        "generate_funny_response": "generate_funny_response",
    },
)

workflow.add_edge("generate_sql_query", "execute_sql_query")

# Conditional routing after SQL execution
workflow.add_conditional_edges(
    "execute_sql_query",
    execute_sql_router,
    {
        "determine_output_format": "determine_output_format",
        "regenerate_query": "regenerate_query",
    },
)

# Conditional routing after determining output format
workflow.add_conditional_edges(
    "determine_output_format",
    output_format_router,
    {
        "generate_readable_resp": "generate_readable_resp",
        "determine_chart_type": "determine_chart_type",
    },
)

workflow.add_edge("determine_chart_type", "generate_readable_resp")

# Conditional routing after query regeneration
workflow.add_conditional_edges(
    "regenerate_query",
    check_attempts_router,
    {
        "generate_sql_query": "generate_sql_query",
        "end_max_iterations": "end_max_iterations",
    },
)

# Final edges to END
workflow.add_edge("generate_readable_resp", END)
workflow.add_edge("generate_funny_response", END)
workflow.add_edge("end_max_iterations", END)
workflow.add_edge("format_chart_data", END)

# Compile the graph
graph = workflow.compile()

# Example usage
def run_query(user_query):
    """Run a query through the agent."""
    initial_state = State(user_query=user_query)
    final_state = graph.invoke(initial_state)
    
    print(f"\nOriginal Query: {user_query}")
    print(f"\nQuery Relevance: {final_state.get('relevance', 'Not checked')}")
    print(f"\nNumber of Attempts: {final_state.get('attempts', 0)}")
    
    if 'sql_query' in final_state:
        print(f"\nGenerated SQL: {final_state['sql_query']}")
        print(f"\nSQL Result: {final_state['sql_query_result']}")
    
    print(f"\nFinal Response: {final_state['readable_resp']}")
    
    return final_state

# sample_query = "what was the total sales of the user named Ajay pal last month ?."
# sample_query = "what was the total number of invoices of the user named Ajay pal last month ?."
# sample_query = "what is the name of the user who has user id 28 ?."
# sample_query = "print the row storing the data of the user named Ajay Pal ?."
# sample_query = "what were my orders last month?"
# sample_query = "how many business does the user with user id 5 has?"
# sample_query = "what is total sum amount of the invoices created last month?."
# sample_query = "what is my business name?."
# sample_query = "Which customer has made the most purchases for the Manika Alora Pvt. Lmt business?."
# sample_query = "What were the total sales of my business. for the current year?."
# sample_query = "what was my income and expense in the last year ?"
# sample_query = "What is the difference in the number of invoices created between this month and last month?"
sample_query = "What are the income and expensses of the current fiscal year by month for my business?"
# sample_query = "What is number of invoices created month by month in previous year for my business?"


run_query(sample_query)


