"""create all

Revision ID: 6bd810dff9b9
Revises: 
Create Date: 2020-05-27 02:45:28.659126

"""
import sys

sys.path.append(".")
sys.path.append("/teleshares")
from src.db_utils.models import create_all

# revision identifiers, used by Alembic.
revision = '6bd810dff9b9'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    create_all()


def downgrade():
    pass
