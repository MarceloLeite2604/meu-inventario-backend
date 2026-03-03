"""Seed reference and factor data

Revision ID: 0002
Revises: 0001
Create Date: 2026-03-01

This migration seeds all static reference data originally populated via
scripts/popular_fatores_emissao.py from the original project.
The full dataset should be imported from the original SQL migrations.
This file contains the seed structure; actual data values must be verified
against the original project's migration files.

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    conn.execute(text("""
        INSERT INTO gwp (id, nome_ghg, gwp_value) VALUES
        (gen_random_uuid(), 'CO2', 1),
        (gen_random_uuid(), 'CH4', 27.9),
        (gen_random_uuid(), 'N2O', 273),
        (gen_random_uuid(), 'HFC-134a', 1530),
        (gen_random_uuid(), 'HFC-23', 14600),
        (gen_random_uuid(), 'HFC-32', 771),
        (gen_random_uuid(), 'HFC-125', 3740),
        (gen_random_uuid(), 'HFC-143a', 5810),
        (gen_random_uuid(), 'HFC-152a', 164),
        (gen_random_uuid(), 'HFC-227ea', 3600),
        (gen_random_uuid(), 'HFC-245fa', 962),
        (gen_random_uuid(), 'SF6', 25200),
        (gen_random_uuid(), 'R-410A', 2088),
        (gen_random_uuid(), 'R-404A', 4728),
        (gen_random_uuid(), 'R-407C', 1774),
        (gen_random_uuid(), 'R-22', 1960),
        (gen_random_uuid(), 'R-507A', 3985),
        (gen_random_uuid(), 'R-402A', 2788),
        (gen_random_uuid(), 'R-402B', 2416),
        (gen_random_uuid(), 'R-408A', 3152),
        (gen_random_uuid(), 'R-409A', 1585),
        (gen_random_uuid(), 'R-413A', 2053),
        (gen_random_uuid(), 'R-417A', 2346),
        (gen_random_uuid(), 'R-422A', 3143),
        (gen_random_uuid(), 'R-422D', 2729),
        (gen_random_uuid(), 'R-424A', 2440),
        (gen_random_uuid(), 'R-426A', 1508),
        (gen_random_uuid(), 'R-427A', 2138),
        (gen_random_uuid(), 'R-428A', 3607),
        (gen_random_uuid(), 'R-434A', 3245),
        (gen_random_uuid(), 'R-438A', 2265),
        (gen_random_uuid(), 'R-442A', 1888),
        (gen_random_uuid(), 'R-448A', 1387),
        (gen_random_uuid(), 'R-449A', 1397),
        (gen_random_uuid(), 'R-450A', 547),
        (gen_random_uuid(), 'R-452A', 2140),
        (gen_random_uuid(), 'R-452B', 676),
        (gen_random_uuid(), 'R-454A', 239),
        (gen_random_uuid(), 'R-454B', 466),
        (gen_random_uuid(), 'R-454C', 148),
        (gen_random_uuid(), 'R-455A', 148),
        (gen_random_uuid(), 'R-456A', 687),
        (gen_random_uuid(), 'R-457A', 139),
        (gen_random_uuid(), 'R-466A', 733),
        (gen_random_uuid(), 'R-513A', 573),
        (gen_random_uuid(), 'R-514A', 2),
        (gen_random_uuid(), 'R-515B', 299),
        (gen_random_uuid(), 'R-600a', 3),
        (gen_random_uuid(), 'R-717', 0),
        (gen_random_uuid(), 'R-744', 1)
        ON CONFLICT DO NOTHING
    """))

    conn.execute(text("""
        INSERT INTO categorias_permissao (id, sistema, escopo, nome_exibicao, ativa) VALUES
        (gen_random_uuid(), 'inventario', 'escopo1', 'Combustão Móvel', true),
        (gen_random_uuid(), 'inventario', 'escopo1', 'Combustão Estacionária', true),
        (gen_random_uuid(), 'inventario', 'escopo1', 'Emissões Fugitivas', true),
        (gen_random_uuid(), 'inventario', 'escopo1', 'Tratamento de Efluentes', true),
        (gen_random_uuid(), 'inventario', 'escopo2', 'Energia Elétrica', true),
        (gen_random_uuid(), 'inventario', 'escopo3', 'Viagens de Negócios', true),
        (gen_random_uuid(), 'deslocamentos', 'escopo3', 'Deslocamentos', true)
        ON CONFLICT DO NOTHING
    """))

    conn.execute(text("""
        INSERT INTO commuting_medalhas (id, nome, descricao, icone, criterio, pontos_bonus) VALUES
        (gen_random_uuid(), 'Primeiro Registro', 'Registrou seu primeiro deslocamento!', '🌱', 'registros_1', 10),
        (gen_random_uuid(), 'Ciclista Dedicado', '5 registros usando bicicleta', '🚴', 'bicicleta_5', 50),
        (gen_random_uuid(), 'Pegada Zero', '5 dias com zero emissão', '🌍', 'zero_emissao_5', 100),
        (gen_random_uuid(), 'Streak Semanal', '4 semanas seguidas registrando', '🔥', 'streak_4', 75),
        (gen_random_uuid(), 'Mestre do Transporte Público', '10 registros de transporte público', '🚌', 'transporte_publico_10', 60),
        (gen_random_uuid(), 'Caminhante Urbano', '5 registros a pé', '🚶', 'caminhada_5', 50),
        (gen_random_uuid(), 'Carpooler', '5 registros de carona compartilhada', '🚗', 'carona_5', 60),
        (gen_random_uuid(), 'Maratonista Verde', '50 registros totais', '🏆', 'registros_50', 200),
        (gen_random_uuid(), 'Embaixador Sustentável', '100 registros totais', '💎', 'registros_100', 500)
        ON CONFLICT DO NOTHING
    """))


def downgrade() -> None:
    op.get_bind().execute(text("DELETE FROM commuting_medalhas"))
    op.get_bind().execute(text("DELETE FROM categorias_permissao"))
    op.get_bind().execute(text("DELETE FROM gwp"))
