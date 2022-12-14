"""create transaction table

Revision ID: b9d113a1bb6a
Revises: 98bae705bad5
Create Date: 2022-10-08 20:09:41.641894

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b9d113a1bb6a'
down_revision = '98bae705bad5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('transactions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=512), nullable=False),
    sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('category', sa.String(length=32), nullable=False),
    sa.Column('is_archived', sa.Boolean(), server_default='False', nullable=False),
    sa.Column('is_income', sa.Boolean(), server_default='False', nullable=False),
    sa.Column('is_expense', sa.Boolean(), server_default='False', nullable=False),
    sa.Column('is_recurring', sa.Boolean(), server_default='False', nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('transactions')
    # ### end Alembic commands ###
