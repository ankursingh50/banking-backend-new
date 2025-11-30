from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "onboarded_customers" (
    "iqama_id" VARCHAR(10) NOT NULL PRIMARY KEY,
    "full_name" VARCHAR(100),
    "date_of_birth" DATE,
    "expiry_date" DATE,
    "issue_date" DATE,
    "age" INT,
    "gender" VARCHAR(10),
    "nationality" VARCHAR(50),
    "building_number" VARCHAR(10),
    "street" VARCHAR(100),
    "neighbourhood" VARCHAR(100),
    "city" VARCHAR(50),
    "postal_code" VARCHAR(10),
    "country" VARCHAR(50) NOT NULL DEFAULT 'Saudi Arabia',
    "mobile_number" VARCHAR(15),
    "additional_mobile_number" VARCHAR(15),
    "arabic_name" VARCHAR(100),
    "date_of_birth_hijri" VARCHAR(20),
    "expiry_date_hijri" VARCHAR(20),
    "dep_reference_number" VARCHAR(10) NOT NULL UNIQUE,
    "device_id" VARCHAR(100),
    "device_type" VARCHAR(100),
    "location" VARCHAR(255),
    "device_registration_date" DATE,
    "device_registration_time" TIMETZ,
    "password_set_date" DATE,
    "password_set_time" TIMETZ,
    "mpin_set_date" DATE,
    "mpin_set_time" TIMETZ,
    "status" VARCHAR(100) NOT NULL DEFAULT 'in_progress',
    "created_at" TIMESTAMPTZ NOT NULL,
    "updated_at" TIMESTAMPTZ NOT NULL,
    "pep_flag" VARCHAR(3),
    "disability_flag" VARCHAR(3),
    "tax_residency_outside_ksa" VARCHAR(10),
    "account_purpose" VARCHAR(500),
    "estimated_withdrawal" DECIMAL(13,2),
    "mpin" VARCHAR(255),
    "password" VARCHAR(255),
    "current_step" VARCHAR(100),
    "source_of_income" TEXT,
    "employment_sector" VARCHAR(50),
    "employer_industry" VARCHAR(100),
    "business_industry" VARCHAR(100),
    "salary_income" DECIMAL(13,2),
    "business_income" DECIMAL(13,2),
    "investment_income" DECIMAL(13,2),
    "rental_income" DECIMAL(13,2),
    "housewife_allowance" DECIMAL(13,2),
    "student_allowance" DECIMAL(13,2),
    "pension_income" DECIMAL(13,2),
    "hafiz_income" DECIMAL(13,2),
    "unemployed_income" DECIMAL(13,2)
);
        ALTER TABLE "iqama_records" ADD "additional_mobile_number" VARCHAR(10);
        ALTER TABLE "iqama_records" ADD "dob_hijri" DATE;
        ALTER TABLE "iqama_records" ADD "issue_date" DATE;
        ALTER TABLE "iqama_records" ADD "expiry_date_hijri" DATE;
        ALTER TABLE "iqama_records" ADD "age" INT;
        ALTER TABLE "iqama_records" ADD "arabic_name" TEXT;
        CREATE TABLE IF NOT EXISTS "portfolio_summary" (
    "iqama_id" BIGSERIAL NOT NULL PRIMARY KEY,
    "cif_id" BIGINT NOT NULL,
    "account_number_1" BIGINT NOT NULL,
    "account_balance_1" BIGINT NOT NULL,
    "account_type_1" VARCHAR(255) NOT NULL,
    "status_1" VARCHAR(255) NOT NULL,
    "recent_transaction_type_1" VARCHAR(255) NOT NULL,
    "recent_transaction_date_1" VARCHAR(255) NOT NULL,
    "recent_transactions_amount_1" BIGINT NOT NULL,
    "recent_transaction_type_2" VARCHAR(255) NOT NULL,
    "recent_transactions_date_2" VARCHAR(255) NOT NULL,
    "recent_transactions_amount_2" BIGINT NOT NULL,
    "recent_transactions_transaction_type_3" VARCHAR(255) NOT NULL,
    "recent_transactions_date_3" VARCHAR(255) NOT NULL,
    "recent_transactions_amount_3" BIGINT NOT NULL,
    "bill_transaction_type_1" VARCHAR(255) NOT NULL,
    "bill_due_date_1" VARCHAR(255) NOT NULL,
    "bill_service_type_1" VARCHAR(255) NOT NULL,
    "bill_amount_1" BIGINT NOT NULL,
    "bill_transaction_type_2" VARCHAR(255) NOT NULL,
    "bill_due_date_2" VARCHAR(255) NOT NULL,
    "bill_service_type_2" VARCHAR(255) NOT NULL,
    "bill_amount_2" BIGINT NOT NULL,
    "recent_transfers_date_1" DATE,
    "recent_transfers_beneficiary_name_1" VARCHAR(255) NOT NULL,
    "recent_transfers_bank_name_1" VARCHAR(255) NOT NULL,
    "recent_transfers_amount_1" BIGINT NOT NULL,
    "recent_transfers_date_2" DATE,
    "recent_transfers_beneficiary_name_2" VARCHAR(255) NOT NULL,
    "recent_transfers_bank_name_2" VARCHAR(255) NOT NULL,
    "recent_transfers_amount_2" BIGINT NOT NULL,
    "account_number_2" BIGINT NOT NULL,
    "account_balance_2" BIGINT NOT NULL,
    "account_type_2" VARCHAR(255) NOT NULL,
    "status_2" VARCHAR(255) NOT NULL
);
        CREATE TABLE IF NOT EXISTS "account_details" (
    "account_number" VARCHAR(20) NOT NULL PRIMARY KEY,
    "iban_number" VARCHAR(34) NOT NULL,
    "account_balance" INT NOT NULL,
    "account_type" VARCHAR(20) NOT NULL,
    "status" VARCHAR(20) NOT NULL,
    "spending_limit" INT NOT NULL,
    "utilised_limit" INT NOT NULL,
    "account_holder_name" VARCHAR(100) NOT NULL,
    "swift_code" VARCHAR(20) NOT NULL,
    "account_currency" VARCHAR(20) NOT NULL,
    "account_nickname" VARCHAR(50),
    "account_creation_date" DATE
);
        CREATE TABLE IF NOT EXISTS "card_details" (
    "account_number" BIGSERIAL NOT NULL PRIMARY KEY,
    "debit_card_last_four_digits_1" VARCHAR(4) NOT NULL,
    "valid_thru_1" DATE NOT NULL,
    "debit_card_last_four_digits_2" VARCHAR(4) NOT NULL,
    "valid_thru_2" DATE NOT NULL
);
        CREATE TABLE IF NOT EXISTS "transaction_summary" (
    "account_number" BIGSERIAL NOT NULL PRIMARY KEY,
    "recent_transaction_type_1" VARCHAR(255),
    "recent_transaction_date_1" VARCHAR(255),
    "recent_transactions_amount_1" BIGINT,
    "recent_transaction_type_2" VARCHAR(255),
    "recent_transactions_date_2" VARCHAR(255),
    "recent_transactions_amount_2" BIGINT,
    "recent_transactions_transaction_type_3" VARCHAR(255),
    "recent_transactions_date_3" VARCHAR(255),
    "recent_transaction_amount_3" BIGINT,
    "recent_transaction_type_4" VARCHAR(255),
    "recent_transaction_date_4" VARCHAR(255),
    "recent_transactions_amount_4" BIGINT,
    "recent_transaction_type_5" VARCHAR(255),
    "recent_transaction_date_5" VARCHAR(255),
    "recent_transactions_amount_5" BIGINT,
    "recent_transaction_type_6" VARCHAR(255),
    "recent_transaction_date_6" VARCHAR(255),
    "recent_transactions_amount_6" BIGINT,
    "recent_transaction_type_7" VARCHAR(255),
    "recent_transaction_date_7" VARCHAR(255),
    "recent_transactions_amount_7" BIGINT,
    "recent_transaction_type_8" VARCHAR(255),
    "recent_transaction_date_8" DATE,
    "recent_transactions_amount_8" BIGINT,
    "recent_transaction_type_9" VARCHAR(255),
    "recent_transaction_date_9" DATE,
    "recent_transactions_amount_9" BIGINT,
    "recent_transaction_type_10" VARCHAR(255),
    "recent_transaction_date_10" DATE,
    "recent_transactions_amount_10" BIGINT
);
        CREATE TABLE IF NOT EXISTS "transaction_history" (
    "transaction_id" BIGSERIAL NOT NULL PRIMARY KEY,
    "account_number" BIGINT NOT NULL,
    "Transaction type" TEXT NOT NULL,
    "Transaction Date" DATE NOT NULL,
    "Transaction amount" DECIMAL(14,2) NOT NULL,
    "available balance" DECIMAL(14,2),
    "Time of transaction" TIMETZ,
    "Merchant" TEXT,
    "Reference Number" TEXT,
    "Location of transaction" TEXT,
    "Address" TEXT,
    "Transaction category" VARCHAR(255)
);
        CREATE TABLE IF NOT EXISTS "international_transaction_history" (
    "international_transaction_id" BIGSERIAL NOT NULL PRIMARY KEY,
    "account_number" BIGINT NOT NULL,
    "Transaction type" TEXT NOT NULL,
    "Transaction Date" DATE NOT NULL,
    "Transaction amount" DECIMAL(14,2) NOT NULL,
    "available balance" DECIMAL(14,2),
    "Time of transaction" TIMETZ,
    "Merchant" TEXT,
    "Reference Number" TEXT,
    "Location of transaction" TEXT,
    "Address" TEXT,
    "Conversion Rate" DECIMAL(18,8),
    "Currency" TEXT,
    "Currency Amount" DECIMAL(18,4)
);
        CREATE TABLE IF NOT EXISTS "absher_records" (
    "pep_flag" VARCHAR(3) NOT NULL,
    "tax_employer_flag" VARCHAR(3) NOT NULL,
    "disability_flag" VARCHAR(3) NOT NULL,
    "high_risk_flag" VARCHAR(3) NOT NULL,
    "iqama_id" VARCHAR(10) NOT NULL PRIMARY KEY REFERENCES "iqama_records" ("iqama_id") ON DELETE CASCADE
);
        ALTER TABLE "theme_settings" RENAME TO "themesettings";
        ALTER TABLE "themesettings" ADD "secondary_font_size" VARCHAR(10) NOT NULL;
        ALTER TABLE "themesettings" ADD "background_color" VARCHAR(10) NOT NULL;
        ALTER TABLE "themesettings" ADD "primary_font_size" VARCHAR(10) NOT NULL;
        ALTER TABLE "themesettings" ALTER COLUMN "primary_color" TYPE VARCHAR(10) USING "primary_color"::VARCHAR(10);
        ALTER TABLE "themesettings" ALTER COLUMN "secondary_color" TYPE VARCHAR(10) USING "secondary_color"::VARCHAR(10);
        DROP TABLE IF EXISTS "onboarded_customers";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "iqama_records" DROP COLUMN "additional_mobile_number";
        ALTER TABLE "iqama_records" DROP COLUMN "dob_hijri";
        ALTER TABLE "iqama_records" DROP COLUMN "issue_date";
        ALTER TABLE "iqama_records" DROP COLUMN "expiry_date_hijri";
        ALTER TABLE "iqama_records" DROP COLUMN "age";
        ALTER TABLE "iqama_records" DROP COLUMN "arabic_name";
        ALTER TABLE "themesettings" RENAME TO "theme_settings";
        ALTER TABLE "themesettings" DROP COLUMN "secondary_font_size";
        ALTER TABLE "themesettings" DROP COLUMN "background_color";
        ALTER TABLE "themesettings" DROP COLUMN "primary_font_size";
        ALTER TABLE "themesettings" ALTER COLUMN "primary_color" TYPE VARCHAR(20) USING "primary_color"::VARCHAR(20);
        ALTER TABLE "themesettings" ALTER COLUMN "secondary_color" TYPE VARCHAR(20) USING "secondary_color"::VARCHAR(20);
        DROP TABLE IF EXISTS "card_details";
        DROP TABLE IF EXISTS "onboarded_customers";
        DROP TABLE IF EXISTS "transaction_history";
        DROP TABLE IF EXISTS "absher_records";
        DROP TABLE IF EXISTS "international_transaction_history";
        DROP TABLE IF EXISTS "portfolio_summary";
        DROP TABLE IF EXISTS "transaction_summary";
        DROP TABLE IF EXISTS "account_details";"""
