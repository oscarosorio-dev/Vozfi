import os

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql+psycopg://vozfi:vozfi@postgres:5432/vozfi")