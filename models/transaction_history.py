# models/transaction_history.py
from tortoise import fields, models

class TransactionHistory(models.Model):
    class Meta:
        table = "transaction_history"

    transaction_id = fields.BigIntField(pk=True, source_field="transaction_id")
    account_number = fields.BigIntField(source_field="account_number")

    transaction_type = fields.TextField(source_field="Transaction type")
    transaction_date = fields.DateField(source_field="Transaction Date")
    transaction_amount = fields.DecimalField(max_digits=14, decimal_places=2, source_field="Transaction amount")

    available_balance = fields.DecimalField(max_digits=14, decimal_places=2, null=True, source_field="available balance")
    time_of_transaction = fields.TimeField(null=True, source_field="Time of transaction")

    merchant = fields.TextField(null=True, source_field="Merchant")
    reference_number = fields.TextField(null=True, source_field="Reference Number")
    location_of_transaction = fields.TextField(null=True, source_field="Location of transaction")
    address = fields.TextField(null=True, source_field="Address")

    transaction_category = fields.CharField(max_length=255, null=True, source_field='Transaction category')
