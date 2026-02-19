from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import ContactRequestStatus
from app.core.exceptions import BadRequestError, ForbiddenError, NotFoundError
from app.models.message import ContactRequest, Message, Report, Thread
from app.models.user import User
from app.services.payment_service import refund_contact_request


async def get_user_contact_requests(user_id: UUID, db: AsyncSession) -> list[ContactRequest]:
    result = await db.execute(
        select(ContactRequest)
        .where(or_(ContactRequest.requester_id == user_id, ContactRequest.tenant_id == user_id))
        .order_by(ContactRequest.created_at.desc())
    )
    return list(result.scalars().all())


async def respond_to_contact_request(
    request_id: UUID, user_id: UUID, status: str, db: AsyncSession
) -> ContactRequest:
    result = await db.execute(
        select(ContactRequest).where(ContactRequest.id == request_id)
    )
    cr = result.scalar_one_or_none()
    if not cr:
        raise NotFoundError("Contact request not found")

    if cr.tenant_id != user_id:
        raise ForbiddenError("Only the contacted tenant can respond")

    if cr.status != ContactRequestStatus.PENDING.value:
        raise BadRequestError("Contact request is no longer pending")

    if cr.expires_at < datetime.now(timezone.utc):
        cr.status = ContactRequestStatus.EXPIRED.value
        raise BadRequestError("Contact request has expired")

    cr.status = status
    cr.responded_at = datetime.now(timezone.utc)

    # If accepted, create a thread for messaging
    if status == ContactRequestStatus.ACCEPTED.value:
        thread = Thread(contact_request_id=cr.id)
        db.add(thread)

    # If declined, refund the requester's credits
    if status == ContactRequestStatus.DECLINED.value:
        await refund_contact_request(cr.id, cr.requester_id, db)

    await db.flush()
    return cr


async def get_conversations(user_id: UUID, db: AsyncSession) -> list[ContactRequest]:
    result = await db.execute(
        select(ContactRequest)
        .where(
            or_(ContactRequest.requester_id == user_id, ContactRequest.tenant_id == user_id),
            ContactRequest.status == ContactRequestStatus.ACCEPTED.value,
        )
        .order_by(ContactRequest.created_at.desc())
    )
    return list(result.scalars().all())


async def get_messages(contact_request_id: UUID, user_id: UUID, db: AsyncSession) -> list[Message]:
    cr_result = await db.execute(
        select(ContactRequest).where(ContactRequest.id == contact_request_id)
    )
    cr = cr_result.scalar_one_or_none()
    if not cr:
        raise NotFoundError("Contact request not found")

    if cr.requester_id != user_id and cr.tenant_id != user_id:
        raise ForbiddenError("Not a participant in this conversation")

    if cr.status != ContactRequestStatus.ACCEPTED.value:
        raise BadRequestError("Contact request has not been accepted")

    # Get thread
    thread_result = await db.execute(
        select(Thread).where(Thread.contact_request_id == contact_request_id)
    )
    thread = thread_result.scalar_one_or_none()
    if not thread:
        return []

    result = await db.execute(
        select(Message).where(Message.thread_id == thread.id).order_by(Message.created_at.asc())
    )
    return list(result.scalars().all())


async def send_message(
    contact_request_id: UUID, sender_id: UUID, body: str, db: AsyncSession
) -> Message:
    cr_result = await db.execute(
        select(ContactRequest).where(ContactRequest.id == contact_request_id)
    )
    cr = cr_result.scalar_one_or_none()
    if not cr:
        raise NotFoundError("Contact request not found")

    if cr.requester_id != sender_id and cr.tenant_id != sender_id:
        raise ForbiddenError("Not a participant in this conversation")

    if cr.status != ContactRequestStatus.ACCEPTED.value:
        raise BadRequestError("Contact request has not been accepted")

    # Get or create thread
    thread_result = await db.execute(
        select(Thread).where(Thread.contact_request_id == contact_request_id)
    )
    thread = thread_result.scalar_one_or_none()
    if not thread:
        thread = Thread(contact_request_id=contact_request_id)
        db.add(thread)
        await db.flush()

    message = Message(thread_id=thread.id, sender_id=sender_id, body=body)
    db.add(message)
    await db.flush()
    return message


async def create_report(
    reporter_user_id: UUID, target_type: str, target_id: UUID, reason: str, db: AsyncSession
) -> Report:
    report = Report(
        reporter_user_id=reporter_user_id,
        target_type=target_type,
        target_id=target_id,
        reason=reason,
    )
    db.add(report)
    await db.flush()
    return report


async def get_reports(db: AsyncSession) -> list[Report]:
    result = await db.execute(select(Report).order_by(Report.created_at.desc()))
    return list(result.scalars().all())
