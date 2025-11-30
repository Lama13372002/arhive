"""Initial migration

Revision ID: 0001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('telegram_id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=255), nullable=True),
        sa.Column('first_name', sa.String(length=255), nullable=True),
        sa.Column('last_name', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('locale', sa.Enum('RU', 'KZ', 'EN', name='userlanguage'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_telegram_id'), 'users', ['telegram_id'], unique=True)

    # Create orders table
    op.create_table('orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('DRAFT', 'PENDING_LYRICS', 'LYRICS_READY', 'USER_EDITING', 'APPROVED', 'GENERATING', 'DELIVERED', 'CANCELED', name='orderstatus'), nullable=False),
        sa.Column('language', sa.Enum('RU', 'KZ', 'EN', name='orderlanguage'), nullable=False),
        sa.Column('genre', sa.String(length=100), nullable=True),
        sa.Column('mood', sa.String(length=100), nullable=True),
        sa.Column('tempo', sa.String(length=100), nullable=True),
        sa.Column('occasion', sa.String(length=255), nullable=True),
        sa.Column('recipient', sa.String(length=255), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('payment_status', sa.Enum('NONE', 'PENDING', 'PAID', 'FAILED', 'REFUNDED', name='paymentstatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_orders_id'), 'orders', ['id'], unique=False)
    op.create_index(op.f('ix_orders_user_id'), 'orders', ['user_id'], unique=False)
    op.create_index(op.f('ix_orders_status'), 'orders', ['status'], unique=False)

    # Create lyrics_versions table
    op.create_table('lyrics_versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('gpt_model', sa.String(length=100), nullable=True),
        sa.Column('prompt_used', sa.JSON(), nullable=True),
        sa.Column('tokens_in', sa.Integer(), nullable=True),
        sa.Column('tokens_out', sa.Integer(), nullable=True),
        sa.Column('quality_score', sa.Float(), nullable=True),
        sa.Column('status', sa.Enum('DRAFT', 'READY', 'REJECTED', name='lyricsstatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_lyrics_versions_id'), 'lyrics_versions', ['id'], unique=False)
    op.create_index(op.f('ix_lyrics_versions_order_id'), 'lyrics_versions', ['order_id'], unique=False)

    # Create audio_assets table
    op.create_table('audio_assets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('kind', sa.Enum('PREVIEW', 'FULL', name='audiokind'), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=True),
        sa.Column('duration_sec', sa.Float(), nullable=True),
        sa.Column('provider', sa.Enum('NONE', 'SUNO', 'INNER', name='audioprovider'), nullable=False),
        sa.Column('meta', sa.JSON(), nullable=True),
        sa.Column('status', sa.Enum('QUEUED', 'GENERATING', 'READY', 'FAILED', name='audiostatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audio_assets_id'), 'audio_assets', ['id'], unique=False)
    op.create_index(op.f('ix_audio_assets_order_id'), 'audio_assets', ['order_id'], unique=False)

    # Create payments table
    op.create_table('payments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('provider', sa.Enum('STRIPE', 'KASPI', 'YUKASSA', name='paymentprovider'), nullable=False),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('external_id', sa.String(length=255), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'PAID', 'FAILED', 'REFUNDED', 'CANCELED', name='paymentstatus'), nullable=False),
        sa.Column('paid_at', sa.DateTime(), nullable=True),
        sa.Column('meta', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_payments_id'), 'payments', ['id'], unique=False)
    op.create_index(op.f('ix_payments_order_id'), 'payments', ['order_id'], unique=False)
    op.create_index(op.f('ix_payments_external_id'), 'payments', ['external_id'], unique=False)

    # Create events_audit table
    op.create_table('events_audit',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('type', sa.String(length=100), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_events_audit_id'), 'events_audit', ['id'], unique=False)
    op.create_index(op.f('ix_events_audit_order_id'), 'events_audit', ['order_id'], unique=False)
    op.create_index(op.f('ix_events_audit_user_id'), 'events_audit', ['user_id'], unique=False)
    op.create_index(op.f('ix_events_audit_type'), 'events_audit', ['type'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_events_audit_type'), table_name='events_audit')
    op.drop_index(op.f('ix_events_audit_user_id'), table_name='events_audit')
    op.drop_index(op.f('ix_events_audit_order_id'), table_name='events_audit')
    op.drop_index(op.f('ix_events_audit_id'), table_name='events_audit')
    op.drop_table('events_audit')
    
    op.drop_index(op.f('ix_payments_external_id'), table_name='payments')
    op.drop_index(op.f('ix_payments_order_id'), table_name='payments')
    op.drop_index(op.f('ix_payments_id'), table_name='payments')
    op.drop_table('payments')
    
    op.drop_index(op.f('ix_audio_assets_order_id'), table_name='audio_assets')
    op.drop_index(op.f('ix_audio_assets_id'), table_name='audio_assets')
    op.drop_table('audio_assets')
    
    op.drop_index(op.f('ix_lyrics_versions_order_id'), table_name='lyrics_versions')
    op.drop_index(op.f('ix_lyrics_versions_id'), table_name='lyrics_versions')
    op.drop_table('lyrics_versions')
    
    op.drop_index(op.f('ix_orders_status'), table_name='orders')
    op.drop_index(op.f('ix_orders_user_id'), table_name='orders')
    op.drop_index(op.f('ix_orders_id'), table_name='orders')
    op.drop_table('orders')
    
    op.drop_index(op.f('ix_users_telegram_id'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS userlanguage')
    op.execute('DROP TYPE IF EXISTS orderstatus')
    op.execute('DROP TYPE IF EXISTS orderlanguage')
    op.execute('DROP TYPE IF EXISTS paymentstatus')
    op.execute('DROP TYPE IF EXISTS lyricsstatus')
    op.execute('DROP TYPE IF EXISTS audiokind')
    op.execute('DROP TYPE IF EXISTS audioprovider')
    op.execute('DROP TYPE IF EXISTS audiostatus')
    op.execute('DROP TYPE IF EXISTS paymentprovider')

