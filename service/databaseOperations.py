from schemas.DataModels import Receipt, ReceiptItem
from datetime import datetime
from config.database import SessionLocal,init_db


class DatabaseOperations:
    def __init__(self):
        init_db()
        self.db = SessionLocal()

    def save_receipt(self, data: dict)->int:
        receipt = Receipt(
            merchant_name=data["merchant_name"],
            receipt_date=datetime.strptime(data["receipt_date"], "%Y-%m-%d").date(),
            total_amount=data["total_amount"],
            tax_amount=data["tax_amount"],
            currency=data["currency"]
        )
        self.db.add(receipt)
        self.db.commit()
        self.db.refresh(receipt)

        for item in data["items"]:
            db_item = ReceiptItem(
                receipt_id=receipt.id,
                item_name=item["item_name"],
                quantity=item["quantity"],
                unit_price=item["unit_price"],
                total_price=item["total_price"]
            )
            self.db.add(db_item)

        self.db.commit()
        return receipt.id
    
    def __del__(self):
        self.db.close()
