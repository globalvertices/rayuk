"""initial

Revision ID: e6b316fcf5b6
Revises:
Create Date: 2026-02-16 01:12:42.103114

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e6b316fcf5b6'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Standalone tables (no FKs) ---
    op.create_table('countries',
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=3), nullable=False),
        sa.Column('currency_code', sa.String(length=3), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )

    op.create_table('users',
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=True),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('auth_provider', sa.String(length=20), nullable=False),
        sa.Column('oauth_provider_id', sa.String(length=255), nullable=True),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),
        sa.Column('is_email_verified', sa.Boolean(), nullable=False),
        sa.Column('is_identity_verified', sa.Boolean(), nullable=False),
        sa.Column('is_contactable', sa.Boolean(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_role'), 'users', ['role'], unique=False)

    # --- Tables depending on users ---
    op.create_table('wallets',
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('balance_credits', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('user_id')
    )

    op.create_table('ledger_entries',
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('entry_type', sa.String(length=20), nullable=False),
        sa.Column('ref_type', sa.String(length=30), nullable=True),
        sa.Column('ref_id', sa.UUID(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ledger_entries_user_id'), 'ledger_entries', ['user_id'], unique=False)

    op.create_table('stripe_topups',
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('credits_amount', sa.Integer(), nullable=False),
        sa.Column('amount_cents', sa.Integer(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('stripe_checkout_session_id', sa.String(length=255), nullable=True),
        sa.Column('stripe_payment_intent_id', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('metadata_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('stripe_checkout_session_id'),
        sa.UniqueConstraint('stripe_payment_intent_id')
    )
    op.create_index(op.f('ix_stripe_topups_user_id'), 'stripe_topups', ['user_id'], unique=False)

    op.create_table('email_verification_tokens',
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('token', sa.String(length=255), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token')
    )

    op.create_table('password_reset_tokens',
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('token', sa.String(length=255), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token')
    )

    op.create_table('refresh_tokens',
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('token_hash', sa.String(length=255), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('device_info', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token_hash')
    )

    op.create_table('reports',
        sa.Column('reporter_user_id', sa.UUID(), nullable=False),
        sa.Column('target_type', sa.String(length=30), nullable=False),
        sa.Column('target_id', sa.UUID(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['reporter_user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # --- Location hierarchy ---
    op.create_table('cities',
        sa.Column('country_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['country_id'], ['countries.id']),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('communities',
        sa.Column('city_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('slug', sa.String(length=200), nullable=False),
        sa.Column('latitude', sa.Numeric(precision=10, scale=7), nullable=True),
        sa.Column('longitude', sa.Numeric(precision=10, scale=7), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['city_id'], ['cities.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )

    op.create_table('buildings',
        sa.Column('community_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('address_line', sa.String(length=500), nullable=True),
        sa.Column('total_units', sa.Integer(), nullable=True),
        sa.Column('year_built', sa.Integer(), nullable=True),
        sa.Column('latitude', sa.Numeric(precision=10, scale=7), nullable=True),
        sa.Column('longitude', sa.Numeric(precision=10, scale=7), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['community_id'], ['communities.id']),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('properties',
        sa.Column('building_id', sa.UUID(), nullable=True),
        sa.Column('community_id', sa.UUID(), nullable=False),
        sa.Column('property_type', sa.String(length=20), nullable=False),
        sa.Column('unit_number', sa.String(length=50), nullable=True),
        sa.Column('utility_reference', sa.String(length=50), nullable=True),
        sa.Column('bedrooms', sa.SmallInteger(), nullable=True),
        sa.Column('bathrooms', sa.SmallInteger(), nullable=True),
        sa.Column('size_sqft', sa.Integer(), nullable=True),
        sa.Column('year_built', sa.Integer(), nullable=True),
        sa.Column('address_line', sa.String(length=500), nullable=False),
        sa.Column('latitude', sa.Numeric(precision=10, scale=7), nullable=True),
        sa.Column('longitude', sa.Numeric(precision=10, scale=7), nullable=True),
        sa.Column('avg_property_rating', sa.Numeric(precision=3, scale=2), nullable=False),
        sa.Column('avg_landlord_rating', sa.Numeric(precision=3, scale=2), nullable=False),
        sa.Column('review_count', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_by', sa.UUID(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['building_id'], ['buildings.id']),
        sa.ForeignKeyConstraint(['community_id'], ['communities.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_properties_building_id'), 'properties', ['building_id'], unique=False)
    op.create_index(op.f('ix_properties_community_id'), 'properties', ['community_id'], unique=False)
    op.create_index(op.f('ix_properties_utility_reference'), 'properties', ['utility_reference'], unique=False)

    # --- Property ownership + tenancy ---
    op.create_table('property_ownership_claims',
        sa.Column('property_id', sa.UUID(), nullable=False),
        sa.Column('landlord_id', sa.UUID(), nullable=False),
        sa.Column('verification_status', sa.String(length=20), nullable=False),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('verified_by', sa.UUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['landlord_id'], ['users.id']),
        sa.ForeignKeyConstraint(['property_id'], ['properties.id']),
        sa.ForeignKeyConstraint(['verified_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('tenancy_records',
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('property_id', sa.UUID(), nullable=False),
        sa.Column('move_in_date', sa.Date(), nullable=True),
        sa.Column('move_out_date', sa.Date(), nullable=True),
        sa.Column('is_current_tenant', sa.Boolean(), nullable=False),
        sa.Column('verification_status', sa.String(length=20), nullable=False),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('verified_by', sa.UUID(), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['property_id'], ['properties.id']),
        sa.ForeignKeyConstraint(['tenant_id'], ['users.id']),
        sa.ForeignKeyConstraint(['verified_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # --- Reviews ---
    op.create_table('property_reviews',
        sa.Column('property_id', sa.UUID(), nullable=False),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('tenancy_record_id', sa.UUID(), nullable=False),
        sa.Column('rating_plumbing', sa.SmallInteger(), nullable=True),
        sa.Column('rating_electricity', sa.SmallInteger(), nullable=True),
        sa.Column('rating_water', sa.SmallInteger(), nullable=True),
        sa.Column('rating_it_cabling', sa.SmallInteger(), nullable=True),
        sa.Column('rating_hvac', sa.SmallInteger(), nullable=True),
        sa.Column('rating_amenity_stove', sa.SmallInteger(), nullable=True),
        sa.Column('rating_amenity_washer', sa.SmallInteger(), nullable=True),
        sa.Column('rating_amenity_fridge', sa.SmallInteger(), nullable=True),
        sa.Column('rating_infra_water_tank', sa.SmallInteger(), nullable=True),
        sa.Column('rating_infra_irrigation', sa.SmallInteger(), nullable=True),
        sa.Column('rating_health_dust', sa.SmallInteger(), nullable=True),
        sa.Column('rating_health_breathing', sa.SmallInteger(), nullable=True),
        sa.Column('rating_health_sewage', sa.SmallInteger(), nullable=True),
        sa.Column('overall_rating', sa.Numeric(precision=3, scale=2), nullable=False),
        sa.Column('review_text', sa.Text(), nullable=False),
        sa.Column('public_excerpt', sa.String(length=300), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='draft'),
        sa.Column('verification_status', sa.String(length=20), nullable=False, server_default='unverified'),
        sa.Column('is_flagged', sa.Boolean(), nullable=False),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['property_id'], ['properties.id']),
        sa.ForeignKeyConstraint(['tenancy_record_id'], ['tenancy_records.id']),
        sa.ForeignKeyConstraint(['tenant_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('property_id', 'tenant_id', name='uq_property_review_tenant')
    )
    op.create_index(op.f('ix_property_reviews_property_id'), 'property_reviews', ['property_id'], unique=False)
    op.create_index(op.f('ix_property_reviews_tenant_id'), 'property_reviews', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_property_reviews_status'), 'property_reviews', ['status'], unique=False)

    op.create_table('landlord_reviews',
        sa.Column('landlord_id', sa.UUID(), nullable=False),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('property_id', sa.UUID(), nullable=False),
        sa.Column('tenancy_record_id', sa.UUID(), nullable=False),
        sa.Column('rating_responsiveness', sa.SmallInteger(), nullable=True),
        sa.Column('rating_demeanor', sa.SmallInteger(), nullable=True),
        sa.Column('rating_repair_payments', sa.SmallInteger(), nullable=True),
        sa.Column('rating_availability', sa.SmallInteger(), nullable=True),
        sa.Column('rating_payment_flexibility', sa.SmallInteger(), nullable=True),
        sa.Column('overall_rating', sa.Numeric(precision=3, scale=2), nullable=False),
        sa.Column('review_text', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='draft'),
        sa.Column('verification_status', sa.String(length=20), nullable=False, server_default='unverified'),
        sa.Column('is_flagged', sa.Boolean(), nullable=False),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['landlord_id'], ['users.id']),
        sa.ForeignKeyConstraint(['property_id'], ['properties.id']),
        sa.ForeignKeyConstraint(['tenancy_record_id'], ['tenancy_records.id']),
        sa.ForeignKeyConstraint(['tenant_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_landlord_reviews_landlord_id'), 'landlord_reviews', ['landlord_id'], unique=False)
    op.create_index(op.f('ix_landlord_reviews_tenant_id'), 'landlord_reviews', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_landlord_reviews_status'), 'landlord_reviews', ['status'], unique=False)

    op.create_table('property_review_photos',
        sa.Column('review_id', sa.UUID(), nullable=False),
        sa.Column('file_url', sa.String(length=500), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('sort_order', sa.SmallInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['review_id'], ['property_reviews.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('verification_documents',
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('tenancy_record_id', sa.UUID(), nullable=True),
        sa.Column('ownership_claim_id', sa.UUID(), nullable=True),
        sa.Column('document_type', sa.String(length=30), nullable=False),
        sa.Column('file_url', sa.String(length=500), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file_size_bytes', sa.Integer(), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=False),
        sa.Column('verification_status', sa.String(length=20), nullable=False),
        sa.Column('admin_notes', sa.Text(), nullable=True),
        sa.Column('reviewed_by', sa.UUID(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['ownership_claim_id'], ['property_ownership_claims.id']),
        sa.ForeignKeyConstraint(['reviewed_by'], ['users.id']),
        sa.ForeignKeyConstraint(['tenancy_record_id'], ['tenancy_records.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # --- Disputes & responses ---
    op.create_table('review_disputes',
        sa.Column('property_review_id', sa.UUID(), nullable=True),
        sa.Column('landlord_review_id', sa.UUID(), nullable=True),
        sa.Column('disputed_by', sa.UUID(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('evidence_urls', postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('admin_notes', sa.Text(), nullable=True),
        sa.Column('resolved_by', sa.UUID(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['disputed_by'], ['users.id']),
        sa.ForeignKeyConstraint(['landlord_review_id'], ['landlord_reviews.id']),
        sa.ForeignKeyConstraint(['property_review_id'], ['property_reviews.id']),
        sa.ForeignKeyConstraint(['resolved_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('landlord_responses',
        sa.Column('property_review_id', sa.UUID(), nullable=True),
        sa.Column('landlord_review_id', sa.UUID(), nullable=True),
        sa.Column('landlord_id', sa.UUID(), nullable=False),
        sa.Column('response_text', sa.Text(), nullable=False),
        sa.Column('is_published', sa.Boolean(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['landlord_id'], ['users.id']),
        sa.ForeignKeyConstraint(['landlord_review_id'], ['landlord_reviews.id']),
        sa.ForeignKeyConstraint(['property_review_id'], ['property_reviews.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # --- Unlocks (per review, tiered) ---
    op.create_table('unlocks',
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('review_id', sa.UUID(), nullable=False),
        sa.Column('tier', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['review_id'], ['property_reviews.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_unlocks_user_id'), 'unlocks', ['user_id'], unique=False)
    op.create_index(op.f('ix_unlocks_review_id'), 'unlocks', ['review_id'], unique=False)

    # --- Messaging ---
    op.create_table('contact_requests',
        sa.Column('requester_id', sa.UUID(), nullable=False),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('property_id', sa.UUID(), nullable=False),
        sa.Column('review_id', sa.UUID(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('responded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['property_id'], ['properties.id']),
        sa.ForeignKeyConstraint(['requester_id'], ['users.id']),
        sa.ForeignKeyConstraint(['review_id'], ['property_reviews.id']),
        sa.ForeignKeyConstraint(['tenant_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('threads',
        sa.Column('contact_request_id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['contact_request_id'], ['contact_requests.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('contact_request_id')
    )

    op.create_table('messages',
        sa.Column('thread_id', sa.UUID(), nullable=False),
        sa.Column('sender_id', sa.UUID(), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['thread_id'], ['threads.id']),
        sa.ForeignKeyConstraint(['sender_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_messages_thread_id'), 'messages', ['thread_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_messages_thread_id'), table_name='messages')
    op.drop_table('messages')
    op.drop_table('threads')
    op.drop_table('contact_requests')
    op.drop_index(op.f('ix_unlocks_review_id'), table_name='unlocks')
    op.drop_index(op.f('ix_unlocks_user_id'), table_name='unlocks')
    op.drop_table('unlocks')
    op.drop_table('landlord_responses')
    op.drop_table('review_disputes')
    op.drop_table('verification_documents')
    op.drop_table('property_review_photos')
    op.drop_index(op.f('ix_landlord_reviews_status'), table_name='landlord_reviews')
    op.drop_index(op.f('ix_landlord_reviews_tenant_id'), table_name='landlord_reviews')
    op.drop_index(op.f('ix_landlord_reviews_landlord_id'), table_name='landlord_reviews')
    op.drop_table('landlord_reviews')
    op.drop_index(op.f('ix_property_reviews_status'), table_name='property_reviews')
    op.drop_index(op.f('ix_property_reviews_tenant_id'), table_name='property_reviews')
    op.drop_index(op.f('ix_property_reviews_property_id'), table_name='property_reviews')
    op.drop_table('property_reviews')
    op.drop_table('tenancy_records')
    op.drop_table('property_ownership_claims')
    op.drop_index(op.f('ix_properties_utility_reference'), table_name='properties')
    op.drop_index(op.f('ix_properties_community_id'), table_name='properties')
    op.drop_index(op.f('ix_properties_building_id'), table_name='properties')
    op.drop_table('properties')
    op.drop_table('buildings')
    op.drop_table('communities')
    op.drop_table('cities')
    op.drop_table('reports')
    op.drop_table('refresh_tokens')
    op.drop_table('password_reset_tokens')
    op.drop_table('email_verification_tokens')
    op.drop_index(op.f('ix_stripe_topups_user_id'), table_name='stripe_topups')
    op.drop_table('stripe_topups')
    op.drop_index(op.f('ix_ledger_entries_user_id'), table_name='ledger_entries')
    op.drop_table('ledger_entries')
    op.drop_table('wallets')
    op.drop_index(op.f('ix_users_role'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_table('countries')
