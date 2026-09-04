"""migrate image config to multi model

Revision ID: 1a2b3c4d5e6f
Revises: 872c7e62d54a
Create Date: 2026-09-02

"""
import json
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '1a2b3c4d5e6f'
down_revision = '872c7e62d54a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    
    # 1. Alte Config-Werte aus der 'config'-Tabelle auslesen
    results = bind.execute(
        sa.text("SELECT key, value FROM config WHERE key IN ('image_generation.model', 'image_generation.engine', 'image_generation.size')")
    ).fetchall()
    
    # In ein Dictionary umwandeln
    old_config = {}
    for row in results:
        key, val = row[0], row[1]
        # Je nachdem, wie die DB JSON speichert (String oder bereits geparstes Objekt)
        if isinstance(val, str):
            try:
                val = json.loads(val)
            except Exception:
                pass
        old_config[key] = val

    # 2. Prüfen, ob bereits Werte vorhanden waren
    old_model = old_config.get('image_generation.model')
    old_engine = old_config.get('image_generation.engine', 'openai')
    old_size = old_config.get('image_generation.size', '1024x1024')

    # Falls ein altes Modell existiert, erzeugen wir das neue Modell-Objekt
    if old_model:
        sizes = [old_size] if old_size else ["1024x1024"]
        
        new_models_value = [
            {
                "id": str(old_model),
                "name": str(old_model),
                "engine": str(old_engine) if old_engine else "openai",
                "sizes": sizes
            }
        ]

        # 3. Den neuen Key 'image_generation.models' in die DB einfügen/aktualisieren (UPSERT)
        json_payload = json.dumps(new_models_value)
        
        # SQLite / PostgreSQL / MySQL-kompatibler UPSERT-Ansatz:
        # Zuerst alten Key löschen (falls vorhanden), dann neu einfügen
        bind.execute(
            sa.text("DELETE FROM config WHERE key = 'image_generation.models'")
        )
        bind.execute(
            sa.text("INSERT INTO config (key, value) VALUES (:key, :value)"),
            {"key": "image_generation.models", "value": json_payload}
        )
        
        # Optional: Alte Keys aufräumen / löschen
        bind.execute(
            sa.text("DELETE FROM config WHERE key IN ('image_generation.model', 'image_generation.engine')")
        )


def downgrade() -> None:
    bind = op.get_bind()
    
    # Liest das erste Modell aus der neuen Liste und stellt die alten Keys wieder her
    result = bind.execute(
        sa.text("SELECT value FROM config WHERE key = 'image_generation.models'")
    ).fetchone()

    if result and result[0]:
        val = result[0]
        if isinstance(val, str):
            val = json.loads(val)
            
        if isinstance(val, list) and len(val) > 0:
            first_model = val[0]
            model_id = json.dumps(first_model.get("id", ""))
            engine = json.dumps(first_model.get("engine", "openai"))
            sizes = first_model.get("sizes", ["1024x1024"])
            size = json.dumps(sizes[0] if sizes else "1024x1024")

            # Alte Keys wiederherstellen
            bind.execute(sa.text("DELETE FROM config WHERE key IN ('image_generation.model', 'image_generation.engine', 'image_generation.size')"))
            bind.execute(sa.text("INSERT INTO config (key, value) VALUES ('image_generation.model', :val)"), {"val": model_id})
            bind.execute(sa.text("INSERT INTO config (key, value) VALUES ('image_generation.engine', :val)"), {"val": engine})
            bind.execute(sa.text("INSERT INTO config (key, value) VALUES ('image_generation.size', :val)"), {"val": size})

    # Neuen Key entfernen
    bind.execute(sa.text("DELETE FROM config WHERE key = 'image_generation.models'"))