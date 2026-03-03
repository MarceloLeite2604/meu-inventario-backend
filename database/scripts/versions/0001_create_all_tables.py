"""Create all tables

Revision ID: 0001
Revises:
Create Date: 2026-03-01

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "organizacoes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("nome", sa.String(255), nullable=False),
        sa.Column("ativa", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("logo_url", sa.Text()),
        sa.Column("cnpj", sa.String(20)),
        sa.Column("cnae", sa.String(10)),
        sa.Column("endereco", sa.Text()),
        sa.Column("cidade", sa.String(100)),
        sa.Column("estado", sa.String(50)),
        sa.Column("cep", sa.String(10)),
        sa.Column("pais", sa.String(100)),
        sa.Column("email_responsavel", sa.String(255)),
        sa.Column("telefone_responsavel", sa.String(30)),
        sa.Column("pessoa_responsavel", sa.String(255)),
        sa.Column("num_funcionarios", sa.Integer()),
        sa.Column("segmento", sa.String(100)),
        sa.Column("descricao_atividades", sa.Text()),
        sa.Column("website", sa.String(255)),
        sa.Column("organograma_url", sa.Text()),
        sa.Column("abordagem_consolidacao", sa.String(100)),
        sa.Column("justificativa_abordagem", sa.Text()),
        sa.Column("limite_organizacional", sa.Text()),
        sa.Column("modulo_inventario_habilitado", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("modulo_deslocamentos_habilitado", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "organizacao_usuarios",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organizacao_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("organizacoes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.String(255), nullable=False),
        sa.Column("papel", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("granted_by", sa.String(255)),
    )
    op.create_index("ix_organizacao_usuarios_organizacao_id", "organizacao_usuarios", ["organizacao_id"])
    op.create_index("ix_organizacao_usuarios_user_id", "organizacao_usuarios", ["user_id"])

    op.create_table(
        "organizacao_usuario_modulos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organizacao_usuario_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("organizacao_usuarios.id", ondelete="CASCADE"), nullable=False),
        sa.Column("modulo", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("granted_by", sa.String(255)),
    )
    op.create_index("ix_organizacao_usuario_modulos_organizacao_usuario_id",
                    "organizacao_usuario_modulos", ["organizacao_usuario_id"])

    op.create_table(
        "profiles",
        sa.Column("id", sa.String(255), primary_key=True),
        sa.Column("email", sa.String(255)),
        sa.Column("full_name", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "user_roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", sa.String(255), nullable=False),
        sa.Column("role", sa.String(50), nullable=False),
        sa.Column("granted_at", sa.DateTime(timezone=True)),
        sa.Column("granted_by", sa.String(255)),
    )
    op.create_index("ix_user_roles_user_id", "user_roles", ["user_id"])

    op.create_table(
        "user_systems",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", sa.String(255), nullable=False),
        sa.Column("system_name", sa.String(50), nullable=False),
        sa.Column("granted_at", sa.DateTime(timezone=True)),
        sa.Column("granted_by", sa.String(255)),
    )
    op.create_index("ix_user_systems_user_id", "user_systems", ["user_id"])

    op.create_table(
        "user_permissoes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", sa.String(255), nullable=False),
        sa.Column("organizacao_id", sa.String(255), nullable=False),
        sa.Column("tipo", sa.String(50), nullable=False),
        sa.Column("referencia", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("granted_by", sa.String(255)),
    )
    op.create_index("ix_user_permissoes_user_id", "user_permissoes", ["user_id"])
    op.create_index("ix_user_permissoes_organizacao_id", "user_permissoes", ["organizacao_id"])

    op.create_table(
        "categorias_permissao",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("sistema", sa.String(50), nullable=False),
        sa.Column("escopo", sa.String(50), nullable=False),
        sa.Column("nome_exibicao", sa.String(255), nullable=False),
        sa.Column("ativa", sa.Boolean(), nullable=False, server_default="true"),
    )

    op.create_table(
        "user_trial_status",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", sa.String(255), nullable=False),
        sa.Column("trial_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("trial_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("extended_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("granted_by", sa.String(255)),
    )
    op.create_index("ix_user_trial_status_user_id", "user_trial_status", ["user_id"])

    op.create_table(
        "inventarios",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organizacao_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("organizacoes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("nome", sa.String(255), nullable=False),
        sa.Column("descricao", sa.Text()),
        sa.Column("ano_base", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(50)),
        sa.Column("data_inicio", sa.String(20)),
        sa.Column("data_finalizacao", sa.String(20)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_inventarios_organizacao_id", "inventarios", ["organizacao_id"])

    op.create_table(
        "emissoes_combustao_movel",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("inventario_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("inventarios.id", ondelete="SET NULL")),
        sa.Column("organizacao_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("organizacoes.id", ondelete="SET NULL")),
        sa.Column("metodo_calculo", sa.String(50), nullable=False),
        sa.Column("tipo_veiculo", sa.String(100)),
        sa.Column("ano_veiculo", sa.Integer()),
        sa.Column("combustivel", sa.String(100)),
        sa.Column("combustivel_fossil", sa.String(100)),
        sa.Column("biocombustivel", sa.String(100)),
        sa.Column("quantidade", sa.Float(), nullable=False),
        sa.Column("quantidade_fossil", sa.Float()),
        sa.Column("quantidade_biocombustivel", sa.Float()),
        sa.Column("unidade", sa.String(50), nullable=False),
        sa.Column("ano", sa.Integer(), nullable=False),
        sa.Column("mes", sa.Integer(), nullable=False),
        sa.Column("emissoes_co2", sa.Float()),
        sa.Column("emissoes_ch4", sa.Float()),
        sa.Column("emissoes_n2o", sa.Float()),
        sa.Column("emissoes_co2_biogenico", sa.Float()),
        sa.Column("emissoes_ch4_biogenico", sa.Float()),
        sa.Column("emissoes_n2o_biogenico", sa.Float()),
        sa.Column("emissoes_total_tco2e", sa.Float()),
        sa.Column("fator_co2", sa.Float()),
        sa.Column("fator_ch4", sa.Float()),
        sa.Column("fator_n2o", sa.Float()),
        sa.Column("ano_referencia", sa.Integer()),
        sa.Column("descricao", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_emissoes_combustao_movel_inventario_id", "emissoes_combustao_movel", ["inventario_id"])
    op.create_index("ix_emissoes_combustao_movel_organizacao_id", "emissoes_combustao_movel", ["organizacao_id"])

    op.create_table(
        "emissoes_estacionaria",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organizacao_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("organizacoes.id", ondelete="SET NULL")),
        sa.Column("combustivel", sa.String(100), nullable=False),
        sa.Column("combustivel_fossil", sa.String(100)),
        sa.Column("biocombustivel", sa.String(100)),
        sa.Column("quantidade", sa.Float(), nullable=False),
        sa.Column("quantidade_fossil", sa.Float()),
        sa.Column("quantidade_biocombustivel", sa.Float()),
        sa.Column("unidade", sa.String(50), nullable=False),
        sa.Column("ano", sa.Integer(), nullable=False),
        sa.Column("mes", sa.Integer(), nullable=False),
        sa.Column("emissoes_co2", sa.Float()),
        sa.Column("emissoes_ch4", sa.Float()),
        sa.Column("emissoes_n2o", sa.Float()),
        sa.Column("emissoes_co2_biogenico", sa.Float()),
        sa.Column("emissoes_ch4_biogenico", sa.Float()),
        sa.Column("emissoes_n2o_biogenico", sa.Float()),
        sa.Column("emissoes_total_tco2e", sa.Float()),
        sa.Column("fator_co2", sa.Float()),
        sa.Column("fator_ch4", sa.Float()),
        sa.Column("fator_n2o", sa.Float()),
        sa.Column("descricao", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_emissoes_estacionaria_organizacao_id", "emissoes_estacionaria", ["organizacao_id"])

    op.create_table(
        "emissoes_fugitivas",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organizacao_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("organizacoes.id", ondelete="SET NULL")),
        sa.Column("gas", sa.String(100), nullable=False),
        sa.Column("quantidade", sa.Float(), nullable=False),
        sa.Column("gwp_value", sa.Float(), nullable=False),
        sa.Column("emissoes_tco2e", sa.Float(), nullable=False),
        sa.Column("ano", sa.Integer(), nullable=False),
        sa.Column("mes", sa.Integer(), nullable=False),
        sa.Column("descricao", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_emissoes_fugitivas_organizacao_id", "emissoes_fugitivas", ["organizacao_id"])

    op.create_table(
        "emissoes_efluentes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("inventario_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("inventarios.id", ondelete="SET NULL")),
        sa.Column("organizacao_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("organizacoes.id", ondelete="SET NULL")),
        sa.Column("tipo_efluente", sa.String(50), nullable=False),
        sa.Column("tipo_tratamento", sa.String(100)),
        sa.Column("tipo_tratamento_2", sa.String(100)),
        sa.Column("tipo_disposicao_final", sa.String(100)),
        sa.Column("volume_efluente", sa.Float()),
        sa.Column("unidade_carga_organica", sa.String(10)),
        sa.Column("carga_organica_entrada", sa.Float()),
        sa.Column("carga_organica_lodo", sa.Float()),
        sa.Column("nitrogenio_efluente", sa.Float()),
        sa.Column("efluente_lancado_ambiente", sa.Boolean()),
        sa.Column("tratamento_sequencial", sa.Boolean()),
        sa.Column("mcf_tratamento", sa.Float()),
        sa.Column("mcf_tratamento_2", sa.Float()),
        sa.Column("mcf_disposicao", sa.Float()),
        sa.Column("ch4_recuperado", sa.Float()),
        sa.Column("ano", sa.Integer(), nullable=False),
        sa.Column("emissoes_ch4", sa.Float()),
        sa.Column("emissoes_co2_biogenico", sa.Float()),
        sa.Column("emissoes_n2o", sa.Float()),
        sa.Column("emissoes_tco2e", sa.Float()),
        sa.Column("fator_n2o", sa.Float()),
        sa.Column("setor_industrial", sa.String(100)),
        sa.Column("descricao", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_emissoes_efluentes_inventario_id", "emissoes_efluentes", ["inventario_id"])
    op.create_index("ix_emissoes_efluentes_organizacao_id", "emissoes_efluentes", ["organizacao_id"])

    op.create_table(
        "unidades_consumidoras",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organizacao_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("organizacoes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("nome", sa.String(255), nullable=False),
        sa.Column("numero_uc", sa.String(100)),
        sa.Column("endereco", sa.Text()),
        sa.Column("distribuidora", sa.String(255)),
        sa.Column("ativa", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_unidades_consumidoras_organizacao_id", "unidades_consumidoras", ["organizacao_id"])

    op.create_table(
        "consumo_energia",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organizacao_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("organizacoes.id", ondelete="SET NULL")),
        sa.Column("unidade_consumidora_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("unidades_consumidoras.id", ondelete="SET NULL")),
        sa.Column("consumo_mwh", sa.Float(), nullable=False),
        sa.Column("ano", sa.Integer(), nullable=False),
        sa.Column("mes", sa.Integer(), nullable=False),
        sa.Column("emissoes_energia_tco2e", sa.Float()),
        sa.Column("descricao", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_consumo_energia_organizacao_id", "consumo_energia", ["organizacao_id"])
    op.create_index("ix_consumo_energia_unidade_consumidora_id", "consumo_energia", ["unidade_consumidora_id"])

    op.create_table(
        "evidencias_consumo_energia",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("consumo_energia_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("consumo_energia.id", ondelete="CASCADE"), nullable=False),
        sa.Column("organizacao_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("organizacoes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("arquivo_url", sa.Text(), nullable=False),
        sa.Column("nome_arquivo_original", sa.String(500), nullable=False),
        sa.Column("tipo_documento", sa.String(50), nullable=False, server_default="fatura"),
        sa.Column("observacoes", sa.Text()),
        sa.Column("uploaded_by", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_evidencias_consumo_energia_consumo_energia_id",
                    "evidencias_consumo_energia", ["consumo_energia_id"])
    op.create_index("ix_evidencias_consumo_energia_organizacao_id",
                    "evidencias_consumo_energia", ["organizacao_id"])

    op.create_table(
        "emissoes_viagens_negocios",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organizacao_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("organizacoes.id", ondelete="SET NULL")),
        sa.Column("tipo_transporte", sa.String(50), nullable=False),
        sa.Column("ano", sa.Integer(), nullable=False),
        sa.Column("mes", sa.Integer(), nullable=False),
        sa.Column("metodo_calculo", sa.String(50)),
        sa.Column("origin", sa.String(10)),
        sa.Column("destination", sa.String(10)),
        sa.Column("distance", sa.Float()),
        sa.Column("round_trip", sa.Boolean()),
        sa.Column("tipo_veiculo", sa.String(100)),
        sa.Column("ano_veiculo", sa.Integer()),
        sa.Column("tipo_frota_de_veiculos", sa.String(100)),
        sa.Column("vehicle_subtype", sa.String(100)),
        sa.Column("tipo_onibus", sa.String(100)),
        sa.Column("combustivel", sa.String(100)),
        sa.Column("fuel", sa.String(100)),
        sa.Column("combustivel_fossil", sa.String(100)),
        sa.Column("biocombustivel", sa.String(100)),
        sa.Column("quantidade", sa.Float()),
        sa.Column("quantidade_fossil", sa.Float()),
        sa.Column("quantidade_biocombustivel", sa.Float()),
        sa.Column("quantidade_passageiros", sa.Integer()),
        sa.Column("unidade", sa.String(50)),
        sa.Column("emissoes_ch4", sa.Float()),
        sa.Column("emissoes_co2", sa.Float()),
        sa.Column("emissoes_n2o", sa.Float()),
        sa.Column("emissoes_ch4_biogenico", sa.Float()),
        sa.Column("emissoes_co2_biogenico", sa.Float()),
        sa.Column("emissoes_n2o_biogenico", sa.Float()),
        sa.Column("emissoes_aerea_ch4", sa.Float()),
        sa.Column("emissoes_aerea_co2", sa.Float()),
        sa.Column("emissoes_aerea_n2o", sa.Float()),
        sa.Column("emissoes_tco2e_total", sa.Float()),
        sa.Column("fator_ch4", sa.Float()),
        sa.Column("fator_co2", sa.Float()),
        sa.Column("fator_n2o", sa.Float()),
        sa.Column("descricao", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_emissoes_viagens_negocios_organizacao_id",
                    "emissoes_viagens_negocios", ["organizacao_id"])

    op.create_table(
        "deslocamentos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organizacao_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("organizacoes.id", ondelete="SET NULL")),
        sa.Column("transport", sa.String(50), nullable=False),
        sa.Column("fuel", sa.String(100)),
        sa.Column("origin", sa.Text()),
        sa.Column("destination", sa.Text()),
        sa.Column("distance", sa.Float()),
        sa.Column("round_trip", sa.Boolean()),
        sa.Column("year", sa.Integer()),
        sa.Column("tipo_frota_de_veiculos", sa.String(100)),
        sa.Column("vehicle_subtype", sa.String(100)),
        sa.Column("combustivel_fossil", sa.String(100)),
        sa.Column("biocombustivel", sa.String(100)),
        sa.Column("emissoes_tco2e_total", sa.Float()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_deslocamentos_organizacao_id", "deslocamentos", ["organizacao_id"])

    op.create_table(
        "commuting_empresas",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("nome", sa.String(255), nullable=False),
        sa.Column("dominio_email", sa.String(255), nullable=False, unique=True),
        sa.Column("logo_url", sa.Text()),
        sa.Column("cidade", sa.String(100)),
        sa.Column("estado", sa.String(50)),
        sa.Column("ativa", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("created_by", sa.String(255)),
    )

    op.create_table(
        "commuting_colaboradores",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", sa.String(255), nullable=False),
        sa.Column("empresa_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("commuting_empresas.id", ondelete="CASCADE"), nullable=False),
        sa.Column("nome", sa.String(255), nullable=False),
        sa.Column("departamento", sa.String(100)),
        sa.Column("avatar_url", sa.Text()),
        sa.Column("pontos_total", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("nivel", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("streak_semanas", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "empresa_id", name="uq_colaborador_user_empresa"),
    )
    op.create_index("ix_commuting_colaboradores_user_id", "commuting_colaboradores", ["user_id"])
    op.create_index("ix_commuting_colaboradores_empresa_id", "commuting_colaboradores", ["empresa_id"])

    op.create_table(
        "commuting_transportes_habituais",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("colaborador_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("commuting_colaboradores.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tipo_transporte", sa.String(50), nullable=False),
        sa.Column("combustivel", sa.String(100)),
        sa.Column("subtipo_veiculo", sa.String(100)),
        sa.Column("distancia_km", sa.Float(), nullable=False),
        sa.Column("ida_e_volta", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("dias_por_semana", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("principal", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_commuting_transportes_habituais_colaborador_id",
                    "commuting_transportes_habituais", ["colaborador_id"])

    op.create_table(
        "commuting_registros",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("colaborador_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("commuting_colaboradores.id", ondelete="CASCADE"), nullable=False),
        sa.Column("semana_inicio", sa.Date(), nullable=False),
        sa.Column("tipo_transporte", sa.String(50), nullable=False),
        sa.Column("combustivel", sa.String(100)),
        sa.Column("distancia_km", sa.Float(), nullable=False),
        sa.Column("dias_utilizados", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("emissoes_tco2e", sa.Float()),
        sa.Column("pontos_ganhos", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("colaborador_id", "semana_inicio", "tipo_transporte",
                            name="uq_registro_colaborador_semana_transporte"),
    )
    op.create_index("ix_commuting_registros_colaborador_id", "commuting_registros", ["colaborador_id"])

    op.create_table(
        "commuting_medalhas",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("nome", sa.String(255), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=False),
        sa.Column("icone", sa.String(10), nullable=False, server_default="🏅"),
        sa.Column("criterio", sa.String(100), nullable=False),
        sa.Column("pontos_bonus", sa.Integer(), nullable=False, server_default="50"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "commuting_colaborador_medalhas",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("colaborador_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("commuting_colaboradores.id", ondelete="CASCADE"), nullable=False),
        sa.Column("medalha_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("commuting_medalhas.id", ondelete="CASCADE"), nullable=False),
        sa.Column("conquistada_em", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("colaborador_id", "medalha_id", name="uq_colaborador_medalha"),
    )
    op.create_index("ix_commuting_colaborador_medalhas_colaborador_id",
                    "commuting_colaborador_medalhas", ["colaborador_id"])
    op.create_index("ix_commuting_colaborador_medalhas_medalha_id",
                    "commuting_colaborador_medalhas", ["medalha_id"])

    op.create_table(
        "questionarios_salvos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("nome", sa.String(255), nullable=False),
        sa.Column("descricao", sa.Text()),
        sa.Column("organizacao_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("organizacoes.id", ondelete="SET NULL")),
        sa.Column("token", sa.String(255), nullable=False, unique=True),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("total_deslocamentos", sa.Integer()),
        sa.Column("total_emissoes", sa.Float()),
        sa.Column("created_by", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_questionarios_salvos_token", "questionarios_salvos", ["token"])
    op.create_index("ix_questionarios_salvos_organizacao_id", "questionarios_salvos", ["organizacao_id"])

    op.create_table(
        "questionarios_respondentes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("questionario_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("questionarios_salvos.id", ondelete="CASCADE"), nullable=False),
        sa.Column("nome", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_questionarios_respondentes_questionario_id",
                    "questionarios_respondentes", ["questionario_id"])

    op.create_table(
        "questionarios_deslocamentos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("questionario_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("questionarios_salvos.id", ondelete="CASCADE"), nullable=False),
        sa.Column("respondente_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("questionarios_respondentes.id", ondelete="SET NULL")),
        sa.Column("transport", sa.String(50), nullable=False),
        sa.Column("fuel", sa.String(100)),
        sa.Column("origin", sa.Text()),
        sa.Column("destination", sa.Text()),
        sa.Column("distance", sa.Float()),
        sa.Column("round_trip", sa.Boolean()),
        sa.Column("year", sa.Integer()),
        sa.Column("tipo_frota_de_veiculos", sa.String(100)),
        sa.Column("vehicle_subtype", sa.String(100)),
        sa.Column("combustivel_fossil", sa.String(100)),
        sa.Column("biocombustivel", sa.String(100)),
        sa.Column("emissoes_tco2e_total", sa.Float()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_questionarios_deslocamentos_questionario_id",
                    "questionarios_deslocamentos", ["questionario_id"])
    op.create_index("ix_questionarios_deslocamentos_respondente_id",
                    "questionarios_deslocamentos", ["respondente_id"])

    op.create_table(
        "rate_limits",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("key", sa.String(500), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_rate_limits_key", "rate_limits", ["key"])

    op.create_table(
        "fatores_tipo_combustivel",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("combustivel", sa.String(100), nullable=False),
        sa.Column("ano_referencia", sa.Integer(), nullable=False),
        sa.Column("tipo_transporte", sa.String(100)),
        sa.Column("unidade", sa.String(50)),
        sa.Column("fator_co2", sa.Float()),
        sa.Column("fator_ch4", sa.Float()),
        sa.Column("fator_n2o", sa.Float()),
        sa.Column("densidade", sa.Float()),
        sa.Column("poder_calorifico_inferior", sa.Float()),
        sa.Column("referencia", sa.Text()),
    )

    op.create_table(
        "fatores_frota_tipo_combustivel",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tipo_veiculo", sa.String(100), nullable=False),
        sa.Column("combustivel", sa.String(100), nullable=False),
        sa.Column("ano_veiculo", sa.Integer(), nullable=False),
        sa.Column("ch4_originais", sa.Float()),
        sa.Column("ch4_convertida", sa.Float()),
        sa.Column("n2o_originais", sa.Float()),
        sa.Column("n2o_convertida", sa.Float()),
    )

    op.create_table(
        "fatores_estacionaria",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("combustivel", sa.String(100), nullable=False),
        sa.Column("ano_referencia", sa.Integer()),
        sa.Column("co2", sa.Float(), nullable=False),
        sa.Column("unidade", sa.String(50), nullable=False),
        sa.Column("ch4_energia", sa.Float()),
        sa.Column("ch4_manufatura_construcao", sa.Float()),
        sa.Column("ch4_comercial_institucional", sa.Float()),
        sa.Column("ch4_residencial_agro_pesca", sa.Float()),
        sa.Column("n2o_energia", sa.Float()),
        sa.Column("n2o_manufatura_construcao", sa.Float()),
        sa.Column("n2o_comercial_institucional", sa.Float()),
        sa.Column("n2o_residencial_agro_pesca", sa.Float()),
    )

    op.create_table(
        "fatores_emissao_energia",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("ano", sa.Integer(), nullable=False),
        sa.Column("mes", sa.Integer(), nullable=False),
        sa.Column("fator_emissao", sa.Float(), nullable=False),
    )

    op.create_table(
        "fatores_emissao_aereas",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("ano_referencia", sa.Integer(), nullable=False),
        sa.Column("distancia_aerea", sa.String(50), nullable=False),
        sa.Column("acrescimo_rota", sa.Float(), nullable=False),
        sa.Column("co2_aereo_passageiro_km", sa.Float(), nullable=False),
        sa.Column("ch4_aereo_passageiro_km", sa.Float(), nullable=False),
        sa.Column("n2o_aereo_passageiro_km", sa.Float(), nullable=False),
    )

    op.create_table(
        "fatores_transporte_onibus",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("ano", sa.Integer(), nullable=False),
        sa.Column("tipo_onibus", sa.String(100), nullable=False),
        sa.Column("diesel_co2_pkm", sa.Float()),
        sa.Column("diesel_ch4_pkm", sa.Float()),
        sa.Column("diesel_n2o_pkm", sa.Float()),
        sa.Column("biodiesel_co2_pkm", sa.Float()),
        sa.Column("biodiesel_ch4_pkm", sa.Float()),
        sa.Column("biodiesel_n2o_pkm", sa.Float()),
        sa.Column("fator_consumo_l_pkm", sa.Float()),
        sa.Column("fator_defra_kgco2e_pkm", sa.Float()),
    )

    op.create_table(
        "fatores_tratamento_efluentes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tipo_tratamento", sa.String(100), nullable=False),
        sa.Column("tipo_efluente_aplicavel", sa.String(50), nullable=False),
        sa.Column("categoria", sa.String(50), nullable=False),
        sa.Column("mcf", sa.Float(), nullable=False),
        sa.Column("fator_n2o_default", sa.Float()),
        sa.Column("descricao", sa.Text()),
        sa.Column("referencia", sa.Text()),
    )

    op.create_table(
        "fatores_variaveis_ghg",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("ano", sa.Integer(), nullable=False),
        sa.Column("mes", sa.Integer()),
        sa.Column("perc_etanol_gasolina", sa.Float()),
        sa.Column("perc_biodiesel_diesel", sa.Float()),
    )

    op.create_table(
        "gwp",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("nome_ghg", sa.String(100), nullable=False),
        sa.Column("gwp_value", sa.Float(), nullable=False),
    )

    op.create_table(
        "composicao_combustiveis",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tipo_combustivel", sa.String(100), nullable=False),
        sa.Column("combustivel_fossil", sa.String(100)),
        sa.Column("biocombustivel", sa.String(100)),
    )

    op.create_table(
        "consumo_unidade_medida",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tipo_frota_veiculos", sa.String(100), nullable=False),
        sa.Column("ano_veiculo", sa.Integer(), nullable=False),
        sa.Column("media_por_unidade", sa.Float(), nullable=False),
    )

    op.create_table(
        "equivalencia_veiculos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("transporte", sa.String(100), nullable=False),
        sa.Column("motor", sa.String(100), nullable=False),
        sa.Column("tipo_combustivel", sa.String(100), nullable=False),
        sa.Column("equivalencia", sa.String(100), nullable=False),
    )

    op.create_table(
        "aeroportos_coordenadas",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("sigla", sa.String(10), nullable=False),
        sa.Column("nome", sa.String(255)),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("graus_lat", sa.Float()),
        sa.Column("minutos_lat", sa.Float()),
        sa.Column("segundos_lat", sa.Float()),
        sa.Column("direcao_lat", sa.String(1)),
        sa.Column("graus_lon", sa.Float()),
        sa.Column("minutos_lon", sa.Float()),
        sa.Column("segundos_lon", sa.Float()),
        sa.Column("direcao_lon", sa.String(1)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_aeroportos_coordenadas_sigla", "aeroportos_coordenadas", ["sigla"])

    op.create_table(
        "tipos_efluentes_industriais",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("setor_industrial", sa.String(255), nullable=False),
        sa.Column("dqo_default", sa.Float(), nullable=False),
        sa.Column("dqo_minimo", sa.Float()),
        sa.Column("dqo_maximo", sa.Float()),
        sa.Column("referencia", sa.Text()),
    )

    op.create_table(
        "transporte_metro",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("ano", sa.Integer(), nullable=False),
        sa.Column("g_co2_passageiro_km", sa.Float(), nullable=False),
    )

    op.create_table(
        "transporte_trem",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("ano", sa.Integer(), nullable=False),
        sa.Column("g_co2_passageiro_km", sa.Float(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("transporte_trem")
    op.drop_table("transporte_metro")
    op.drop_table("tipos_efluentes_industriais")
    op.drop_index("ix_aeroportos_coordenadas_sigla", table_name="aeroportos_coordenadas")
    op.drop_table("aeroportos_coordenadas")
    op.drop_table("equivalencia_veiculos")
    op.drop_table("consumo_unidade_medida")
    op.drop_table("composicao_combustiveis")
    op.drop_table("gwp")
    op.drop_table("fatores_variaveis_ghg")
    op.drop_table("fatores_tratamento_efluentes")
    op.drop_table("fatores_transporte_onibus")
    op.drop_table("fatores_emissao_aereas")
    op.drop_table("fatores_emissao_energia")
    op.drop_table("fatores_estacionaria")
    op.drop_table("fatores_frota_tipo_combustivel")
    op.drop_table("fatores_tipo_combustivel")
    op.drop_index("ix_rate_limits_key", table_name="rate_limits")
    op.drop_table("rate_limits")
    op.drop_index("ix_questionarios_deslocamentos_respondente_id", table_name="questionarios_deslocamentos")
    op.drop_index("ix_questionarios_deslocamentos_questionario_id", table_name="questionarios_deslocamentos")
    op.drop_table("questionarios_deslocamentos")
    op.drop_index("ix_questionarios_respondentes_questionario_id", table_name="questionarios_respondentes")
    op.drop_table("questionarios_respondentes")
    op.drop_index("ix_questionarios_salvos_token", table_name="questionarios_salvos")
    op.drop_index("ix_questionarios_salvos_organizacao_id", table_name="questionarios_salvos")
    op.drop_table("questionarios_salvos")
    op.drop_index("ix_commuting_colaborador_medalhas_medalha_id", table_name="commuting_colaborador_medalhas")
    op.drop_index("ix_commuting_colaborador_medalhas_colaborador_id", table_name="commuting_colaborador_medalhas")
    op.drop_table("commuting_colaborador_medalhas")
    op.drop_table("commuting_medalhas")
    op.drop_index("ix_commuting_registros_colaborador_id", table_name="commuting_registros")
    op.drop_table("commuting_registros")
    op.drop_index("ix_commuting_transportes_habituais_colaborador_id", table_name="commuting_transportes_habituais")
    op.drop_table("commuting_transportes_habituais")
    op.drop_index("ix_commuting_colaboradores_empresa_id", table_name="commuting_colaboradores")
    op.drop_index("ix_commuting_colaboradores_user_id", table_name="commuting_colaboradores")
    op.drop_table("commuting_colaboradores")
    op.drop_table("commuting_empresas")
    op.drop_index("ix_deslocamentos_organizacao_id", table_name="deslocamentos")
    op.drop_table("deslocamentos")
    op.drop_index("ix_emissoes_viagens_negocios_organizacao_id", table_name="emissoes_viagens_negocios")
    op.drop_table("emissoes_viagens_negocios")
    op.drop_index("ix_evidencias_consumo_energia_organizacao_id", table_name="evidencias_consumo_energia")
    op.drop_index("ix_evidencias_consumo_energia_consumo_energia_id", table_name="evidencias_consumo_energia")
    op.drop_table("evidencias_consumo_energia")
    op.drop_index("ix_consumo_energia_unidade_consumidora_id", table_name="consumo_energia")
    op.drop_index("ix_consumo_energia_organizacao_id", table_name="consumo_energia")
    op.drop_table("consumo_energia")
    op.drop_index("ix_unidades_consumidoras_organizacao_id", table_name="unidades_consumidoras")
    op.drop_table("unidades_consumidoras")
    op.drop_index("ix_emissoes_efluentes_organizacao_id", table_name="emissoes_efluentes")
    op.drop_index("ix_emissoes_efluentes_inventario_id", table_name="emissoes_efluentes")
    op.drop_table("emissoes_efluentes")
    op.drop_index("ix_emissoes_fugitivas_organizacao_id", table_name="emissoes_fugitivas")
    op.drop_table("emissoes_fugitivas")
    op.drop_index("ix_emissoes_estacionaria_organizacao_id", table_name="emissoes_estacionaria")
    op.drop_table("emissoes_estacionaria")
    op.drop_index("ix_emissoes_combustao_movel_organizacao_id", table_name="emissoes_combustao_movel")
    op.drop_index("ix_emissoes_combustao_movel_inventario_id", table_name="emissoes_combustao_movel")
    op.drop_table("emissoes_combustao_movel")
    op.drop_index("ix_inventarios_organizacao_id", table_name="inventarios")
    op.drop_table("inventarios")
    op.drop_table("user_trial_status")
    op.drop_table("categorias_permissao")
    op.drop_index("ix_user_permissoes_organizacao_id", table_name="user_permissoes")
    op.drop_index("ix_user_permissoes_user_id", table_name="user_permissoes")
    op.drop_table("user_permissoes")
    op.drop_index("ix_user_systems_user_id", table_name="user_systems")
    op.drop_table("user_systems")
    op.drop_index("ix_user_roles_user_id", table_name="user_roles")
    op.drop_table("user_roles")
    op.drop_table("profiles")
    op.drop_index("ix_organizacao_usuario_modulos_organizacao_usuario_id",
                  table_name="organizacao_usuario_modulos")
    op.drop_table("organizacao_usuario_modulos")
    op.drop_index("ix_organizacao_usuarios_user_id", table_name="organizacao_usuarios")
    op.drop_index("ix_organizacao_usuarios_organizacao_id", table_name="organizacao_usuarios")
    op.drop_table("organizacao_usuarios")
    op.drop_table("organizacoes")
