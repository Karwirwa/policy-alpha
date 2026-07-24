"""Milestone 2 models migration

Revision ID: milestone2_models_20260724
Revises: 468f9787dda7
Create Date: 2026-07-24
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'milestone2_models_20260724'
down_revision = '468f9787dda7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Countries
    op.create_table(
        'countries',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=8), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    # Government sources
    op.create_table(
        'government_sources',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('url', sa.String(length=2000), nullable=True),
        sa.Column('country_id', sa.String(length=36), sa.ForeignKey('countries.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    # Documents
    op.create_table(
        'documents',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('title', sa.String(length=1000), nullable=True),
        sa.Column('source_url', sa.String(length=2000), nullable=True),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('government_source_id', sa.String(length=36), sa.ForeignKey('government_sources.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    # Document chunks
    op.create_table(
        'document_chunks',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('document_id', sa.String(length=36), sa.ForeignKey('documents.id'), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('start_char', sa.Integer(), nullable=True),
        sa.Column('end_char', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    # Companies
    op.create_table(
        'companies',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('name', sa.String(length=1000), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    # Bills
    op.create_table(
        'bills',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('title', sa.String(length=1000), nullable=False),
        sa.Column('identifier', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    # Mentions
    op.create_table(
        'mentions',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('document_id', sa.String(length=36), sa.ForeignKey('documents.id'), nullable=False),
        sa.Column('company_id', sa.String(length=36), sa.ForeignKey('companies.id'), nullable=True),
        sa.Column('bill_id', sa.String(length=36), sa.ForeignKey('bills.id'), nullable=True),
        sa.Column('snippet', sa.Text(), nullable=True),
        sa.Column('start_char', sa.Integer(), nullable=True),
        sa.Column('end_char', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    # AI analyses
    op.create_table(
        'ai_analyses',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('document_id', sa.String(length=36), sa.ForeignKey('documents.id'), nullable=True),
        sa.Column('company_id', sa.String(length=36), nullable=True),
        sa.Column('model_name', sa.String(length=255), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('ai_analyses')
    op.drop_table('mentions')
    op.drop_table('bills')
    op.drop_table('companies')
    op.drop_table('document_chunks')
    op.drop_table('documents')
    op.drop_table('government_sources')
    op.drop_table('countries')
