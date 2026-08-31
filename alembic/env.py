from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine

from app.core.config import get_settings
from app.db.session import Base
from app import models  # noqa: F401


# ============================================================
# CONFIGURATION ALEMBIC
# ============================================================

config = context.config


# Configuration du logging Alembic
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# ============================================================
# CONFIGURATION APPLICATION
# ============================================================

settings = get_settings()

# Métadonnées SQLAlchemy utilisées par Alembic
target_metadata = Base.metadata


# ============================================================
# URL DE LA BASE DE DONNÉES
# ============================================================

def _database_url() -> str:
    """
    Récupère l'URL PostgreSQL depuis la configuration
    de l'application.

    Le projet utilise psycopg v3 :
        postgresql+psycopg://...
    """
    return settings.database_url


# ============================================================
# MIGRATIONS OFFLINE
# ============================================================

def run_migrations_offline() -> None:
    """
    Exécute les migrations Alembic en mode offline.

    Dans ce mode, Alembic génère les instructions SQL
    sans ouvrir directement une connexion à PostgreSQL.
    """

    url = _database_url()

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named",
        },
    )

    with context.begin_transaction():
        context.run_migrations()


# ============================================================
# MIGRATIONS ONLINE
# ============================================================

def run_migrations_online() -> None:
    """
    Exécute les migrations Alembic avec une connexion
    directe à PostgreSQL.

    IMPORTANT :
    On utilise create_engine() directement avec l'URL
    postgresql+psycopg afin d'utiliser psycopg v3.

    Cela évite qu'Alembic/SQLAlchemy tente d'utiliser
    psycopg2, qui n'est pas installé dans Render.
    """

    database_url = _database_url()

    connectable = create_engine(
        database_url,
        poolclass=None,
    )

    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()

    connectable.dispose()


# ============================================================
# LANCEMENT
# ============================================================

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()