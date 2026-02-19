from enum import Enum


class UserRole(str, Enum):
    TENANT = "tenant"
    LANDLORD = "landlord"
    LEAD = "lead"
    ADMIN = "admin"


class AuthProvider(str, Enum):
    EMAIL = "email"
    GOOGLE = "google"
    APPLE = "apple"


class PropertyType(str, Enum):
    VILLA = "villa"
    APARTMENT = "apartment"
    TOWNHOUSE = "townhouse"
    STUDIO = "studio"


class ReviewStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    PUBLISHED = "published"
    DISPUTED = "disputed"
    REMOVED = "removed"


class VerificationStatus(str, Enum):
    UNVERIFIED = "unverified"
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class DocumentType(str, Enum):
    TENANCY_CONTRACT = "tenancy_contract"
    LEASE_AGREEMENT = "lease_agreement"
    UTILITY_BILL = "utility_bill"
    BANK_STATEMENT = "bank_statement"
    TITLE_DEED = "title_deed"
    MANAGEMENT_AGREEMENT = "management_agreement"
    OTHER = "other"


class DisputeStatus(str, Enum):
    OPEN = "open"
    UNDER_REVIEW = "under_review"
    UPHELD = "upheld"
    REJECTED = "rejected"
    PARTIALLY_UPHELD = "partially_upheld"


class UnlockTier(str, Enum):
    SUMMARY = "summary"
    DETAILED = "detailed"
    FULL = "full"


class LedgerEntryType(str, Enum):
    TOPUP = "topup"
    CHARGE = "charge"
    REFUND = "refund"


class ContactRequestStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"


class MessageStatus(str, Enum):
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
