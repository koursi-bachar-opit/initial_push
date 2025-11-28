from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import and_

from .models import Invoice, InvoiceStatus


class InvoiceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    #CRUD
    def create(
        self,
        *,
        organization_id: UUID,
        period_start: datetime,
        period_end: datetime,
        total_amount,
        currency: str,
        status: InvoiceStatus = InvoiceStatus.PENDING,
    ) -> Invoice:
        invoice = Invoice(
            organization_id=organization_id,
            period_start=period_start,
            period_end=period_end,
            total_amount=total_amount,
            currency=currency,
            status=status,
        )
        self.db.add(invoice)
        self.db.flush()  # get id
        return invoice

    def get(self, invoice_id: UUID) -> Optional[Invoice]:
        return self.db.query(Invoice).filter(Invoice.id == invoice_id).first()

    def get_for_period(
        self,
        *,
        organization_id: UUID,
        period_start: datetime,
        period_end: datetime,
    ) -> Optional[Invoice]:
        """
        Simple 'exact match' check. If you want overlapping guarding,
        you can extend this to check any overlap with [period_start, period_end].
        """
        return (
            self.db.query(Invoice)
            .filter(
                Invoice.organization_id == organization_id,
                Invoice.period_start == period_start,
                Invoice.period_end == period_end,
            )
            .first()
        )

    def list_for_org(
        self,
        organization_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Invoice]:
        return (
            self.db.query(Invoice)
            .filter(Invoice.organization_id == organization_id)
            .order_by(Invoice.period_start.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def list_all(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Invoice]:
        return (
            self.db.query(Invoice)
            .order_by(Invoice.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update_status(
        self,
        invoice: Invoice,
        new_status: InvoiceStatus,
    ) -> Invoice:
        invoice.status = new_status
        self.db.add(invoice)
        self.db.flush()
        return invoice