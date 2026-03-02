# Database Model Document — Climate Commute Tracker

## Overview

The database is hosted on Supabase (managed PostgreSQL). The application accesses it exclusively via the Supabase JavaScript client (`@supabase/supabase-js`), which communicates over REST API for table operations and RPC for custom database functions.

TypeScript types for all tables are auto-generated from the database schema and stored at `src/integrations/supabase/types.ts`. All type definitions in this document are inferred from that file.

Row-Level Security (RLS) policies are enabled on all tables to enforce multi-tenant data isolation. The core RLS predicate is the `user_in_org(org_id)` database function, which returns `true` if the current database session's user belongs to the specified organization.

---

## Entities and Tables

### Organizations and Users

---

#### `organizacoes`

Represents a legal entity that uses the system. The top-level tenant object.

| Field | Type | Nullable | Description |
|---|---|---|---|
| `id` | `string` (uuid) | No | Primary key |
| `nome` | `string` | No | Organization name |
| `ativa` | `boolean` | No | Whether the organization is active (default: `true`) |
| `logo_url` | `string` | Yes | URL of the organization's logo image |
| `cnpj` | `string` | Yes | Brazilian tax registration number |
| `cnae` | `string` | Yes | Brazilian economic activity classification code |
| `endereco` | `string` | Yes | Street address |
| `cidade` | `string` | Yes | City |
| `estado` | `string` | Yes | State |
| `cep` | `string` | Yes | Postal code |
| `pais` | `string` | Yes | Country |
| `email_responsavel` | `string` | Yes | Contact person's email |
| `telefone_responsavel` | `string` | Yes | Contact person's phone number |
| `pessoa_responsavel` | `string` | Yes | Name of the responsible person |
| `num_funcionarios` | `number` | Yes | Number of employees |
| `segmento` | `string` | Yes | Industry segment |
| `descricao_atividades` | `string` | Yes | Description of the organization's activities |
| `website` | `string` | Yes | Organization website URL |
| `organograma_url` | `string` | Yes | URL of the organizational chart document |
| `abordagem_consolidacao` | `string` | Yes | GHG consolidation approach (e.g., equity share, operational control) |
| `justificativa_abordagem` | `string` | Yes | Justification for the chosen consolidation approach |
| `limite_organizacional` | `string` | Yes | Organizational boundary definition |
| `modulo_inventario_habilitado` | `boolean` | No | Whether the Inventário module is enabled for this organization |
| `modulo_deslocamentos_habilitado` | `boolean` | No | Whether the Deslocamentos module is enabled for this organization |
| `created_at` | `string` | No | Record creation timestamp |
| `updated_at` | `string` | No | Record last update timestamp |

**Primary key**: `id`

---

#### `organizacao_usuarios`

Association table linking users to organizations and their roles within each organization.

| Field | Type | Nullable | Description |
|---|---|---|---|
| `id` | `string` (uuid) | No | Primary key |
| `organizacao_id` | `string` | No | Foreign key → `organizacoes.id` |
| `user_id` | `string` | No | Foreign key → `auth.users.id` |
| `papel` | `string` | No | Role within the organization (e.g., `admin`, `user`) |
| `created_at` | `string` | No | Record creation timestamp |
| `granted_by` | `string` | Yes | ID of the user who granted this membership |

**Primary key**: `id`

---

#### `organizacao_usuario_modulos`

Grants a user access to a specific module within an organization membership.

| Field | Type | Nullable | Description |
|---|---|---|---|
| `id` | `string` (uuid) | No | Primary key |
| `organizacao_usuario_id` | `string` | No | Foreign key → `organizacao_usuarios.id` |
| `modulo` | `string` | No | Module name (e.g., `inventario`, `deslocamentos`) |
| `created_at` | `string` | No | Record creation timestamp |
| `granted_by` | `string` | Yes | ID of the user who granted this module access |

**Primary key**: `id`

---

#### `profiles`

Stores public profile information for each authenticated user.

| Field | Type | Nullable | Description |
|---|---|---|---|
| `id` | `string` (uuid) | No | Primary key; foreign key → `auth.users.id` |
| `email` | `string` | Yes | User's email address |
| `full_name` | `string` | Yes | User's full name |
| `created_at` | `string` | Yes | Record creation timestamp |
| `updated_at` | `string` | Yes | Record last update timestamp |

**Primary key**: `id`

---

#### `user_roles`

Stores global system-level roles for users.

| Field | Type | Nullable | Description |
|---|---|---|---|
| `id` | `string` (uuid) | No | Primary key |
| `user_id` | `string` | No | Foreign key → `auth.users.id` |
| `role` | `app_role` (enum) | No | Global role: `admin`, `moderator`, `user`, or `master` |
| `granted_at` | `string` | Yes | Timestamp when the role was granted |
| `granted_by` | `string` | Yes | ID of the user who granted the role |

**Primary key**: `id`

---

#### `user_systems`

Records which top-level systems a user has been granted access to.

| Field | Type | Nullable | Description |
|---|---|---|---|
| `id` | `string` (uuid) | No | Primary key |
| `user_id` | `string` | No | Foreign key → `auth.users.id` |
| `system_name` | `string` | No | System identifier (`inventario` or `deslocamentos`) |
| `granted_at` | `string` | Yes | Timestamp when access was granted |
| `granted_by` | `string` | Yes | ID of the user who granted the access |

**Primary key**: `id`

---

#### `user_permissoes`

Stores fine-grained, organization-scoped permission grants for users.

| Field | Type | Nullable | Description |
|---|---|---|---|
| `id` | `string` (uuid) | No | Primary key |
| `user_id` | `string` | No | Foreign key → `auth.users.id` |
| `organizacao_id` | `string` | No | Foreign key → `organizacoes.id` |
| `tipo` | `string` | No | Permission type: `sistema`, `escopo`, or `categoria` |
| `referencia` | `string` | No | Target identifier (system name, scope name, or category id) |
| `created_at` | `string` | No | Record creation timestamp |
| `granted_by` | `string` | Yes | ID of the user who granted this permission |

**Primary key**: `id`

---

#### `categorias_permissao`

Reference table listing all available permission categories with display metadata.

| Field | Type | Nullable | Description |
|---|---|---|---|
| `id` | `string` (uuid) | No | Primary key |
| `sistema` | `string` | No | System this category belongs to (e.g., `inventario`) |
| `escopo` | `string` | No | Scope this category belongs to (e.g., `escopo1`) |
| `nome_exibicao` | `string` | No | Human-readable display name |
| `ativa` | `boolean` | No | Whether this category is currently active |

**Primary key**: `id`

---

### Inventories

---

#### `inventarios`

The primary container for emission records. One inventory per organization per base year.

| Field | Type | Nullable | Description |
|---|---|---|---|
| `id` | `string` (uuid) | No | Primary key |
| `organizacao_id` | `string` | No | Foreign key → `organizacoes.id` |
| `nome` | `string` | No | Inventory name |
| `descricao` | `string` | Yes | Optional description |
| `ano_base` | `number` | No | Base year of the inventory |
| `status` | `string` | Yes | Inventory status (e.g., `em_andamento`, `concluido`) |
| `data_inicio` | `string` | Yes | Inventory period start date |
| `data_finalizacao` | `string` | Yes | Inventory period end date |
| `created_at` | `string` | Yes | Record creation timestamp |
| `updated_at` | `string` | Yes | Record last update timestamp |

**Primary key**: `id`

---

### Scope 1 — Mobile Combustion

---

#### `emissoes_combustao_movel`

Stores mobile combustion emission records (Scope 1), including cars, trucks, motorcycles, buses, trains, and airplanes used for organizational activities.

| Field | Type | Nullable | Description |
|---|---|---|---|
| `id` | `string` (uuid) | No | Primary key |
| `inventario_id` | `string` | Yes | Foreign key → `inventarios.id` |
| `organizacao_id` | `string` | Yes | Foreign key → `organizacoes.id` |
| `metodo_calculo` | `string` | No | Calculation method: `veiculo_combustivel`, `combustivel`, or `veiculo_km` |
| `tipo_veiculo` | `string` | Yes | Vehicle type (e.g., `carro`, `caminhao`, `motocicleta`) |
| `ano_veiculo` | `number` | Yes | Vehicle model year |
| `combustivel` | `string` | Yes | Fuel type used |
| `combustivel_fossil` | `string` | Yes | Fossil fraction of the fuel |
| `biocombustivel` | `string` | Yes | Biogenic fraction of the fuel |
| `quantidade` | `number` | No | Total fuel quantity consumed |
| `quantidade_fossil` | `number` | Yes | Fossil fuel quantity |
| `quantidade_biocombustivel` | `number` | Yes | Biogenic fuel quantity |
| `unidade` | `string` | No | Unit of measurement for the quantity |
| `ano` | `number` | No | Year of consumption |
| `mes` | `number` | No | Month of consumption (1–12) |
| `emissoes_co2` | `number` | Yes | Fossil CO₂ emissions (tonnes) |
| `emissoes_ch4` | `number` | Yes | Fossil CH₄ emissions (tonnes) |
| `emissoes_n2o` | `number` | Yes | Fossil N₂O emissions (tonnes) |
| `emissoes_co2_biogenico` | `number` | Yes | Biogenic CO₂ emissions (tonnes) |
| `emissoes_ch4_biogenico` | `number` | Yes | Biogenic CH₄ emissions (tonnes) |
| `emissoes_n2o_biogenico` | `number` | Yes | Biogenic N₂O emissions (tonnes) |
| `emissoes_total_tco2e` | `number` | Yes | Total fossil emissions in tCO₂e |
| `fator_co2` | `number` | Yes | CO₂ emission factor applied |
| `fator_ch4` | `number` | Yes | CH₄ emission factor applied |
| `fator_n2o` | `number` | Yes | N₂O emission factor applied |
| `ano_referencia` | `number` | Yes | Reference year for the emission factor used |
| `descricao` | `string` | Yes | Optional description |
| `created_at` | `string` | No | Record creation timestamp |

**Primary key**: `id`

---

### Scope 1 — Stationary Combustion

---

#### `emissoes_estacionaria`

Stores stationary combustion emission records (Scope 1), covering fixed installations such as boilers, furnaces, and generators.

| Field | Type | Nullable | Description |
|---|---|---|---|
| `id` | `string` (uuid) | No | Primary key |
| `organizacao_id` | `string` | Yes | Foreign key → `organizacoes.id` |
| `combustivel` | `string` | No | Fuel type used |
| `combustivel_fossil` | `string` | Yes | Fossil fraction of the fuel |
| `biocombustivel` | `string` | Yes | Biogenic fraction of the fuel |
| `quantidade` | `number` | No | Total fuel quantity consumed |
| `quantidade_fossil` | `number` | Yes | Fossil fuel quantity |
| `quantidade_biocombustivel` | `number` | Yes | Biogenic fuel quantity |
| `unidade` | `string` | No | Unit of measurement for the quantity |
| `ano` | `number` | No | Year of consumption |
| `mes` | `number` | No | Month of consumption (1–12) |
| `emissoes_co2` | `number` | Yes | Fossil CO₂ emissions (tonnes) |
| `emissoes_ch4` | `number` | Yes | Fossil CH₄ emissions (tonnes) |
| `emissoes_n2o` | `number` | Yes | Fossil N₂O emissions (tonnes) |
| `emissoes_co2_biogenico` | `number` | Yes | Biogenic CO₂ emissions (tonnes) |
| `emissoes_ch4_biogenico` | `number` | Yes | Biogenic CH₄ emissions (tonnes) |
| `emissoes_n2o_biogenico` | `number` | Yes | Biogenic N₂O emissions (tonnes) |
| `emissoes_total_tco2e` | `number` | Yes | Total fossil emissions in tCO₂e |
| `fator_co2` | `number` | Yes | CO₂ emission factor applied |
| `fator_ch4` | `number` | Yes | CH₄ emission factor applied |
| `fator_n2o` | `number` | Yes | N₂O emission factor applied |
| `descricao` | `string` | Yes | Optional description |
| `created_at` | `string` | No | Record creation timestamp |

**Primary key**: `id`

---

### Scope 1 — Fugitive Emissions

---

#### `emissoes_fugitivas`

Stores fugitive emission records (Scope 1), such as refrigerant leaks and fire suppressant releases.

| Field | Type | Nullable | Description |
|---|---|---|---|
| `id` | `string` (uuid) | No | Primary key |
| `organizacao_id` | `string` | Yes | Foreign key → `organizacoes.id` |
| `gas` | `string` | No | GHG gas type (e.g., `HFC-134a`, `SF6`) |
| `quantidade` | `number` | No | Quantity of gas released (kg) |
| `gwp_value` | `number` | No | GWP value applied for this gas |
| `emissoes_tco2e` | `number` | No | Calculated total emissions in tCO₂e |
| `ano` | `number` | No | Year of the emission event |
| `mes` | `number` | No | Month of the emission event (1–12) |
| `descricao` | `string` | Yes | Optional description (e.g., equipment identifier) |
| `created_at` | `string` | No | Record creation timestamp |

**Primary key**: `id`

---

### Scope 1 — Effluents

---

#### `emissoes_efluentes`

Stores emission records from wastewater and effluent treatment (Scope 1), following IPCC 2019 methodology.

| Field | Type | Nullable | Description |
|---|---|---|---|
| `id` | `string` (uuid) | No | Primary key |
| `inventario_id` | `string` | Yes | Foreign key → `inventarios.id` |
| `organizacao_id` | `string` | Yes | Foreign key → `organizacoes.id` |
| `tipo_efluente` | `string` | No | Effluent type: `domestico` or `industrial` |
| `tipo_tratamento` | `string` | Yes | Primary treatment method |
| `tipo_tratamento_2` | `string` | Yes | Secondary treatment method (if sequential treatment) |
| `tipo_disposicao_final` | `string` | Yes | Final disposal method (if discharged to environment) |
| `volume_efluente` | `number` | Yes | Total volume of effluent generated (m³/year) |
| `unidade_carga_organica` | `string` | Yes | Organic load measurement unit: `DQO` or `DBO` |
| `carga_organica_entrada` | `number` | Yes | Organic load at inlet (kg/m³) |
| `carga_organica_lodo` | `number` | Yes | Organic load removed in sludge (kg/m³) |
| `nitrogenio_efluente` | `number` | Yes | Nitrogen concentration in effluent (kgN/m³) |
| `efluente_lancado_ambiente` | `boolean` | Yes | Whether treated effluent is discharged to the environment |
| `tratamento_sequencial` | `boolean` | Yes | Whether a second sequential treatment stage is used |
| `mcf_tratamento` | `number` | Yes | MCF for primary treatment |
| `mcf_tratamento_2` | `number` | Yes | MCF for secondary treatment |
| `mcf_disposicao` | `number` | Yes | MCF for final disposal |
| `ch4_recuperado` | `number` | Yes | CH₄ recovered from biogas (tCH₄/year) |
| `ano` | `number` | No | Base year of the inventory |
| `emissoes_ch4` | `number` | Yes | CH₄ emissions (tonnes) |
| `emissoes_co2_biogenico` | `number` | Yes | Biogenic CO₂ from recovered CH₄ combustion (tonnes) |
| `emissoes_n2o` | `number` | Yes | N₂O emissions (tonnes) |
| `emissoes_tco2e` | `number` | Yes | Total emissions in tCO₂e |
| `fator_n2o` | `number` | Yes | N₂O emission factor applied (kgN₂O-N/kgN) |
| `setor_industrial` | `string` | Yes | Industrial sector (for industrial effluents) |
| `descricao` | `string` | Yes | Optional description |
| `created_at` | `string` | No | Record creation timestamp |

**Primary key**: `id`

---

### Scope 2 — Energy

---

#### `consumo_energia`

Stores monthly electricity consumption records for each consumer unit.

| Field | Type | Nullable | Description |
|---|---|---|---|
| `id` | `string` (uuid) | No | Primary key |
| `organizacao_id` | `string` | Yes | Foreign key → `organizacoes.id` |
| `unidade_consumidora_id` | `string` | Yes | Foreign key → `unidades_consumidoras.id` |
| `consumo_mwh` | `number` | No | Electricity consumed (MWh) |
| `ano` | `number` | No | Year of consumption |
| `mes` | `number` | No | Month of consumption (1–12) |
| `emissoes_energia_tco2e` | `number` | Yes | Calculated Scope 2 emissions in tCO₂e |
| `descricao` | `string` | Yes | Optional description |
| `created_at` | `string` | No | Record creation timestamp |

**Primary key**: `id`

---

#### `unidades_consumidoras`

Represents a physical electricity meter or consumer unit belonging to an organization.

| Field | Type | Nullable | Description |
|---|---|---|---|
| `id` | `string` (uuid) | No | Primary key |
| `organizacao_id` | `string` | No | Foreign key → `organizacoes.id` |
| `nome` | `string` | No | Name or label for this consumer unit |
| `numero_uc` | `string` | Yes | Official consumer unit number from the utility |
| `endereco` | `string` | Yes | Physical address of the consumer unit |
| `distribuidora` | `string` | Yes | Name of the electricity distribution company |
| `ativa` | `boolean` | No | Whether this consumer unit is active |
| `created_at` | `string` | No | Record creation timestamp |

**Primary key**: `id`

---

#### `evidencias_consumo_energia`

Stores evidence documents (e.g., utility bills) attached to energy consumption records.

| Field | Type | Nullable | Description |
|---|---|---|---|
| `id` | `string` (uuid) | No | Primary key |
| `consumo_energia_id` | `string` | No | Foreign key → `consumo_energia.id` |
| `organizacao_id` | `string` | No | Foreign key → `organizacoes.id` |
| `arquivo_url` | `string` | No | URL of the uploaded document in Supabase Storage |
| `nome_arquivo_original` | `string` | No | Original filename of the uploaded document |
| `tipo_documento` | `string` | No | Document type (default: `fatura`) |
| `observacoes` | `string` | Yes | Optional notes |
| `uploaded_by` | `string` | No | ID of the user who uploaded the document |
| `created_at` | `string` | No | Record creation timestamp |

**Primary key**: `id`

---

### Scope 3 — Business Travel

---

#### `emissoes_viagens_negocios`

Stores business travel emission records (Scope 3) for all transport modes.

| Field | Type | Nullable | Description |
|---|---|---|---|
| `id` | `string` (uuid) | No | Primary key |
| `organizacao_id` | `string` | Yes | Foreign key → `organizacoes.id` |
| `tipo_transporte` | `string` | No | Transport mode (e.g., `airplane`, `car`, `bus`, `train`) |
| `ano` | `number` | No | Year of travel |
| `mes` | `number` | No | Month of travel (1–12) |
| `metodo_calculo` | `string` | Yes | Calculation method used |
| `origin` | `string` | Yes | Origin airport code or location |
| `destination` | `string` | Yes | Destination airport code or location |
| `distance` | `number` | Yes | Distance traveled (km) |
| `round_trip` | `boolean` | Yes | Whether the trip is a round trip |
| `tipo_veiculo` | `string` | Yes | Vehicle type |
| `ano_veiculo` | `number` | Yes | Vehicle model year |
| `tipo_frota_de_veiculos` | `string` | Yes | Fleet type |
| `vehicle_subtype` | `string` | Yes | Vehicle sub-type |
| `tipo_onibus` | `string` | Yes | Bus category |
| `combustivel` | `string` | Yes | Fuel type |
| `fuel` | `string` | Yes | Fuel type (alternate field used by some calculation paths) |
| `combustivel_fossil` | `string` | Yes | Fossil fuel type |
| `biocombustivel` | `string` | Yes | Biogenic fuel type |
| `quantidade` | `number` | Yes | Fuel quantity consumed |
| `quantidade_fossil` | `number` | Yes | Fossil fuel quantity |
| `quantidade_biocombustivel` | `number` | Yes | Biogenic fuel quantity |
| `quantidade_passageiros` | `number` | Yes | Number of passengers |
| `unidade` | `string` | Yes | Unit of measurement |
| `emissoes_ch4` | `number` | Yes | Fossil CH₄ emissions (tonnes) |
| `emissoes_co2` | `number` | Yes | Fossil CO₂ emissions (tonnes) |
| `emissoes_n2o` | `number` | Yes | Fossil N₂O emissions (tonnes) |
| `emissoes_ch4_biogenico` | `number` | Yes | Biogenic CH₄ emissions (tonnes) |
| `emissoes_co2_biogenico` | `number` | Yes | Biogenic CO₂ emissions (tonnes) |
| `emissoes_n2o_biogenico` | `number` | Yes | Biogenic N₂O emissions (tonnes) |
| `emissoes_aerea_ch4` | `number` | Yes | Air travel CH₄ emissions (tonnes) |
| `emissoes_aerea_co2` | `number` | Yes | Air travel CO₂ emissions (tonnes) |
| `emissoes_aerea_n2o` | `number` | Yes | Air travel N₂O emissions (tonnes) |
| `emissoes_tco2e_total` | `number` | Yes | Total emissions in tCO₂e |
| `fator_ch4` | `number` | Yes | CH₄ emission factor applied |
| `fator_co2` | `number` | Yes | CO₂ emission factor applied |
| `fator_n2o` | `number` | Yes | N₂O emission factor applied |
| `descricao` | `string` | Yes | Optional description |
| `created_at` | `string` | No | Record creation timestamp |

**Primary key**: `id`

---

#### `deslocamentos`

Stores commuting emission records for the Deslocamentos system (authenticated users).

| Field | Type | Nullable | Description |
|---|---|---|---|
| `id` | `string` (uuid) | No | Primary key |
| `organizacao_id` | `string` | Yes | Foreign key → `organizacoes.id` |
| `transport` | `string` | No | Transport mode |
| `fuel` | `string` | Yes | Fuel type |
| `origin` | `string` | Yes | Origin location |
| `destination` | `string` | Yes | Destination location |
| `distance` | `number` | Yes | Distance traveled (km) |
| `round_trip` | `boolean` | Yes | Whether the trip is a round trip |
| `year` | `number` | Yes | Year of the commute |
| `tipo_frota_de_veiculos` | `string` | Yes | Fleet type |
| `vehicle_subtype` | `string` | Yes | Vehicle sub-type |
| `combustivel_fossil` | `string` | Yes | Fossil fuel type |
| `biocombustivel` | `string` | Yes | Biogenic fuel type |
| `emissoes_tco2e_total` | `number` | Yes | Total emissions in tCO₂e |
| `created_at` | `string` | No | Record creation timestamp |

**Primary key**: `id`

---

### Emission Factors

---

#### `fatores_tipo_combustivel`

Emission factors per fuel type and transport mode, used for mobile and business travel combustion calculations.

| Field | Type | Nullable | Description |
|---|---|---|---|
| `id` | `string` (uuid) | No | Primary key |
| `combustivel` | `string` | No | Fuel type |
| `ano_referencia` | `number` | No | Reference year for this factor set |
| `tipo_transporte` | `string` | Yes | Applicable transport type |
| `unidade` | `string` | Yes | Unit of measurement |
| `fator_co2` | `number` | Yes | CO₂ emission factor |
| `fator_ch4` | `number` | Yes | CH₄ emission factor |
| `fator_n2o` | `number` | Yes | N₂O emission factor |
| `densidade` | `number` | Yes | Fuel density |
| `poder_calorifico_inferior` | `number` | Yes | Lower heating value |
| `referencia` | `string` | Yes | Source reference for this factor |

**Primary key**: `id`

---

#### `fatores_frota_tipo_combustivel`

CH₄ and N₂O emission factors for vehicle fleet types by model year and fuel combination.

| Field | Type | Nullable | Description |
|---|---|---|---|
| `id` | `string` (uuid) | No | Primary key |
| `tipo_veiculo` | `string` | No | Vehicle type |
| `combustivel` | `string` | No | Fuel type |
| `ano_veiculo` | `number` | No | Vehicle model year |
| `ch4_originais` | `number` | Yes | CH₄ factor for vehicles with original engine |
| `ch4_convertida` | `number` | Yes | CH₄ factor for converted vehicles |
| `n2o_originais` | `number` | Yes | N₂O factor for vehicles with original engine |
| `n2o_convertida` | `number` | Yes | N₂O factor for converted vehicles |

**Primary key**: `id`

---

#### `fatores_estacionaria`

Emission factors for stationary combustion by fuel type and combustion sector.

| Field | Type | Nullable | Description |
|---|---|---|---|
| `id` | `string` (uuid) | No | Primary key |
| `combustivel` | `string` | No | Fuel type |
| `ano_referencia` | `number` | Yes | Reference year |
| `co2` | `number` | No | CO₂ emission factor |
| `unidade` | `string` | No | Unit of measurement |
| `ch4_energia` | `number` | Yes | CH₄ factor for energy production |
| `ch4_manufatura_construcao` | `number` | Yes | CH₄ factor for manufacturing and construction |
| `ch4_comercial_institucional` | `number` | Yes | CH₄ factor for commercial and institutional |
| `ch4_residencial_agro_pesca` | `number` | Yes | CH₄ factor for residential, agriculture, and fishing |
| `n2o_energia` | `number` | Yes | N₂O factor for energy production |
| `n2o_manufatura_construcao` | `number` | Yes | N₂O factor for manufacturing and construction |
| `n2o_comercial_institucional` | `number` | Yes | N₂O factor for commercial and institutional |
| `n2o_residencial_agro_pesca` | `number` | Yes | N₂O factor for residential, agriculture, and fishing |

**Primary key**: `id`

---

#### `fatores_emissao_energia`

Monthly grid electricity emission factors for Scope 2 calculations.

| Field | Type | Nullable | Description |
|---|---|---|---|
| `id` | `string` (uuid) | No | Primary key |
| `ano` | `number` | No | Year |
| `mes` | `number` | No | Month (1–12) |
| `fator_emissao` | `number` | No | Grid emission factor (tCO₂e/MWh) |

**Primary key**: `id`

---

#### `fatores_emissao_aereas`

Emission factors for air travel, differentiated by distance range.

| Field | Type | Nullable | Description |
|---|---|---|---|
| `id` | `string` (uuid) | No | Primary key |
| `ano_referencia` | `number` | No | Reference year |
| `distancia_aerea` | `string` | No | Distance range category (e.g., `short-haul`, `long-haul`) |
| `acrescimo_rota` | `number` | No | Route deviation multiplier |
| `co2_aereo_passageiro_km` | `number` | No | CO₂ factor (kg/passenger-km) |
| `ch4_aereo_passageiro_km` | `number` | No | CH₄ factor (kg/passenger-km) |
| `n2o_aereo_passageiro_km` | `number` | No | N₂O factor (kg/passenger-km) |

**Primary key**: `id`

---

#### `fatores_transporte_onibus`

Emission factors for bus transport by bus type and fuel.

| Field | Type | Nullable | Description |
|---|---|---|---|
| `id` | `string` (uuid) | No | Primary key |
| `ano` | `number` | No | Reference year |
| `tipo_onibus` | `string` | No | Bus category |
| `diesel_co2_pkm` | `number` | Yes | Diesel CO₂ factor (kg/passenger-km) |
| `diesel_ch4_pkm` | `number` | Yes | Diesel CH₄ factor (kg/passenger-km) |
| `diesel_n2o_pkm` | `number` | Yes | Diesel N₂O factor (kg/passenger-km) |
| `biodiesel_co2_pkm` | `number` | Yes | Biodiesel CO₂ factor (kg/passenger-km) |
| `biodiesel_ch4_pkm` | `number` | Yes | Biodiesel CH₄ factor (kg/passenger-km) |
| `biodiesel_n2o_pkm` | `number` | Yes | Biodiesel N₂O factor (kg/passenger-km) |
| `fator_consumo_l_pkm` | `number` | Yes | Fuel consumption factor (liters/passenger-km) |
| `fator_defra_kgco2e_pkm` | `number` | Yes | DEFRA composite factor (kgCO₂e/passenger-km) |

**Primary key**: `id`

---

#### `fatores_tratamento_efluentes`

Emission factors for wastewater treatment methods, including Methane Conversion Factors (MCF) and N₂O defaults.

| Field | Type | Nullable | Description |
|---|---|---|---|
| `id` | `string` (uuid) | No | Primary key |
| `tipo_tratamento` | `string` | No | Treatment method name |
| `tipo_efluente_aplicavel` | `string` | No | Applicable effluent type (`domestico`, `industrial`, or `ambos`) |
| `categoria` | `string` | No | Category: `tratamento` or `disposicao` |
| `mcf` | `number` | No | Methane Conversion Factor |
| `fator_n2o_default` | `number` | Yes | Default N₂O emission factor |
| `descricao` | `string` | Yes | Description of the treatment method |
| `referencia` | `string` | Yes | Source reference |

**Primary key**: `id`

---

#### `fatores_variaveis_ghg`

Monthly variable GHG percentage factors for blended fuels in Brazil.

| Field | Type | Nullable | Description |
|---|---|---|---|
| `id` | `string` (uuid) | No | Primary key |
| `ano` | `number` | No | Year |
| `mes` | `number` | Yes | Month (1–12); `null` if annual average |
| `perc_etanol_gasolina` | `number` | Yes | Percentage of ethanol in gasoline |
| `perc_biodiesel_diesel` | `number` | Yes | Percentage of biodiesel in diesel |

**Primary key**: `id`

---

### Reference Data

---

#### `gwp`

Global Warming Potential values for each GHG gas.

| Field | Type | Nullable | Description |
|---|---|---|---|
| `id` | `string` (uuid) | No | Primary key |
| `nome_ghg` | `string` | No | GHG gas name |
| `gwp_value` | `number` | No | GWP value (100-year time horizon) |

**Primary key**: `id`

---

#### `composicao_combustiveis`

Maps blended fuel types to their fossil and biogenic component fractions.

| Field | Type | Nullable | Description |
|---|---|---|---|
| `id` | `string` (uuid) | No | Primary key |
| `tipo_combustivel` | `string` | No | Blended fuel type (e.g., `gasolina`, `diesel`) |
| `combustivel_fossil` | `string` | Yes | Fossil component identifier |
| `biocombustivel` | `string` | Yes | Biogenic component identifier |

**Primary key**: `id`

---

#### `consumo_unidade_medida`

Fuel economy reference data for calculating fuel consumption from vehicle distance.

| Field | Type | Nullable | Description |
|---|---|---|---|
| `id` | `string` (uuid) | No | Primary key |
| `tipo_frota_veiculos` | `string` | No | Fleet type |
| `ano_veiculo` | `number` | No | Vehicle model year |
| `media_por_unidade` | `number` | No | Average fuel consumption (liters per km) |

**Primary key**: `id`

---

#### `equivalencia_veiculos`

Maps vehicle types to their fuel and motor combinations for emission factor lookup.

| Field | Type | Nullable | Description |
|---|---|---|---|
| `id` | `string` (uuid) | No | Primary key |
| `transporte` | `string` | No | Transport mode |
| `motor` | `string` | No | Engine type |
| `tipo_combustivel` | `string` | No | Fuel type |
| `equivalencia` | `string` | No | Equivalent vehicle category |

**Primary key**: `id`

---

#### `aeroportos_coordenadas`

Geographic coordinates for airports, used to calculate great-circle distances for air travel emissions.

| Field | Type | Nullable | Description |
|---|---|---|---|
| `id` | `string` (uuid) | No | Primary key |
| `sigla` | `string` | No | IATA airport code |
| `nome` | `string` | Yes | Airport name |
| `latitude` | `number` | No | Decimal latitude |
| `longitude` | `number` | No | Decimal longitude |
| `graus_lat` | `number` | Yes | Latitude degrees component |
| `minutos_lat` | `number` | Yes | Latitude minutes component |
| `segundos_lat` | `number` | Yes | Latitude seconds component |
| `direcao_lat` | `string` | Yes | Latitude hemisphere (`N` or `S`) |
| `graus_lon` | `number` | Yes | Longitude degrees component |
| `minutos_lon` | `number` | Yes | Longitude minutes component |
| `segundos_lon` | `number` | Yes | Longitude seconds component |
| `direcao_lon` | `string` | Yes | Longitude hemisphere (`E` or `W`) |
| `created_at` | `string` | No | Record creation timestamp |

**Primary key**: `id`

---

#### `tipos_efluentes_industriais`

Default organic load values (DQO) by industrial sector for effluent emission calculations.

| Field | Type | Nullable | Description |
|---|---|---|---|
| `id` | `string` (uuid) | No | Primary key |
| `setor_industrial` | `string` | No | Industrial sector name |
| `dqo_default` | `number` | No | Default DQO concentration (kg/m³) |
| `dqo_minimo` | `number` | Yes | Minimum DQO concentration |
| `dqo_maximo` | `number` | Yes | Maximum DQO concentration |
| `referencia` | `string` | Yes | Source reference |

**Primary key**: `id`

---

#### `transporte_metro`

Emission factors for subway (metro) transport.

| Field | Type | Nullable | Description |
|---|---|---|---|
| `id` | `string` (uuid) | No | Primary key |
| `ano` | `number` | No | Reference year |
| `g_co2_passageiro_km` | `number` | No | CO₂ factor (gCO₂/passenger-km) |

**Primary key**: `id`

---

#### `transporte_trem`

Emission factors for train transport.

| Field | Type | Nullable | Description |
|---|---|---|---|
| `id` | `string` (uuid) | No | Primary key |
| `ano` | `number` | No | Reference year |
| `g_co2_passageiro_km` | `number` | No | CO₂ factor (gCO₂/passenger-km) |

**Primary key**: `id`

---

### Public Questionnaires

---

#### `questionarios_salvos`

A public questionnaire linked to an organization, accessible via a unique token.

| Field | Type | Nullable | Description |
|---|---|---|---|
| `id` | `string` (uuid) | No | Primary key |
| `nome` | `string` | No | Questionnaire name |
| `descricao` | `string` | Yes | Optional description |
| `organizacao_id` | `string` | Yes | Foreign key → `organizacoes.id` |
| `token` | `string` | No | Unique public access token |
| `ativo` | `boolean` | No | Whether the questionnaire is accepting responses |
| `total_deslocamentos` | `number` | Yes | Aggregated count of submitted trip entries |
| `total_emissoes` | `number` | Yes | Aggregated total emissions (tCO₂e) from all responses |
| `created_by` | `string` | Yes | ID of the user who created the questionnaire |
| `created_at` | `string` | No | Record creation timestamp |

**Primary key**: `id`

---

#### `questionarios_respondentes`

Records the identity of each person who submitted a response to a public questionnaire.

| Field | Type | Nullable | Description |
|---|---|---|---|
| `id` | `string` (uuid) | No | Primary key |
| `questionario_id` | `string` | No | Foreign key → `questionarios_salvos.id` |
| `nome` | `string` | No | Respondent's name |
| `email` | `string` | No | Respondent's email address |
| `created_at` | `string` | No | Submission timestamp |

**Primary key**: `id`

---

#### `questionarios_deslocamentos`

Stores individual trip emission entries submitted via a public questionnaire.

| Field | Type | Nullable | Description |
|---|---|---|---|
| `id` | `string` (uuid) | No | Primary key |
| `questionario_id` | `string` | No | Foreign key → `questionarios_salvos.id` |
| `respondente_id` | `string` | Yes | Foreign key → `questionarios_respondentes.id` |
| `transport` | `string` | No | Transport mode |
| `fuel` | `string` | Yes | Fuel type |
| `origin` | `string` | Yes | Origin location |
| `destination` | `string` | Yes | Destination location |
| `distance` | `number` | Yes | Distance traveled (km) |
| `round_trip` | `boolean` | Yes | Whether the trip is a round trip |
| `year` | `number` | Yes | Year of the trip |
| `tipo_frota_de_veiculos` | `string` | Yes | Fleet type |
| `vehicle_subtype` | `string` | Yes | Vehicle sub-type |
| `combustivel_fossil` | `string` | Yes | Fossil fuel type |
| `biocombustivel` | `string` | Yes | Biogenic fuel type |
| `emissoes_tco2e_total` | `number` | Yes | Total calculated emissions (tCO₂e) |
| `created_at` | `string` | No | Submission timestamp |

**Primary key**: `id`

---

### Commuting Sub-system

The commuting sub-system ("Track My Carbon") is an optional module that enables individual employee commute tracking with gamification features (points, streaks, badges). It is documented at a high level only.

| Table | Purpose |
|---|---|
| `commuting_empresas` | Companies enrolled in the commuting tracking module |
| `commuting_colaboradores` | Individual employees within each company, with points and streak counters |
| `commuting_registros` | Weekly commute records submitted by each employee |
| `commuting_transportes_habituais` | Each employee's usual commute transport preferences |
| `commuting_medalhas` | Available badge definitions with criteria and bonus points |
| `commuting_colaborador_medalhas` | Badges earned by each employee |

---

### Utility

---

#### `rate_limits`

Tracks rate-limiting state for public endpoints.

| Field | Type | Nullable | Description |
|---|---|---|---|
| `id` | `string` (uuid) | No | Primary key |
| `client_ip` | `string` | No | Client IP address |
| `function_name` | `string` | No | Name of the rate-limited function or endpoint |
| `created_at` | `string` | No | Timestamp of the request |

**Primary key**: `id`

---

#### `user_trial_status`

Tracks trial access periods granted to users.

| Field | Type | Nullable | Description |
|---|---|---|---|
| `id` | `string` (uuid) | No | Primary key |
| `user_id` | `string` | No | Foreign key → `auth.users.id` |
| `trial_start` | `string` | No | Trial period start timestamp |
| `trial_end` | `string` | No | Trial period end timestamp |
| `active` | `boolean` | No | Whether the trial is currently active |
| `extended_count` | `number` | No | Number of times the trial period has been extended |
| `created_at` | `string` | No | Record creation timestamp |
| `updated_at` | `string` | No | Record last update timestamp |
| `granted_by` | `string` | Yes | ID of the user who granted the trial |

**Primary key**: `id`

---

## Relationships

| Relationship | Nature | Description |
|---|---|---|
| `organizacoes` → `inventarios` | One-to-many | One organization has many inventories (one per base year) |
| `organizacoes` → `organizacao_usuarios` | One-to-many | One organization has many user memberships |
| `organizacao_usuarios` → `organizacao_usuario_modulos` | One-to-many | One membership can grant access to multiple modules |
| `organizacoes` → `user_permissoes` | One-to-many | Permissions are scoped per organization |
| `inventarios` → `emissoes_combustao_movel` | One-to-many | One inventory holds many mobile combustion records |
| `inventarios` → `emissoes_estacionaria` | One-to-many | One inventory holds many stationary combustion records |
| `inventarios` → `emissoes_efluentes` | One-to-many | One inventory holds many effluent records |
| `organizacoes` → `emissoes_fugitivas` | One-to-many | Fugitive emission records are linked directly to organizations (no inventory FK) |
| `organizacoes` → `consumo_energia` | One-to-many | One organization has many energy consumption records |
| `unidades_consumidoras` → `consumo_energia` | One-to-many | One consumer unit has many monthly consumption records |
| `consumo_energia` → `evidencias_consumo_energia` | One-to-many | One energy consumption record can have many evidence documents |
| `organizacoes` → `emissoes_viagens_negocios` | One-to-many | One organization has many business travel records |
| `organizacoes` → `deslocamentos` | One-to-many | One organization has many commuting records |
| `organizacoes` → `questionarios_salvos` | One-to-many | One organization can have many public questionnaires |
| `questionarios_salvos` → `questionarios_respondentes` | One-to-many | One questionnaire has many respondents |
| `questionarios_respondentes` → `questionarios_deslocamentos` | One-to-many | One respondent can submit multiple trip entries |
| `questionarios_salvos` → `questionarios_deslocamentos` | One-to-many | One questionnaire accumulates many trip entries |
| `commuting_empresas` → `commuting_colaboradores` | One-to-many | One company has many employee commuting profiles |
| `commuting_colaboradores` → `commuting_registros` | One-to-many | One employee has many weekly commute records |
| `commuting_colaboradores` → `commuting_transportes_habituais` | One-to-many | One employee can have multiple usual transport configurations |
| `commuting_colaboradores` → `commuting_colaborador_medalhas` | One-to-many | One employee can earn many badges |
| `commuting_medalhas` → `commuting_colaborador_medalhas` | One-to-many | One badge definition can be earned by many employees |

---

## Indexes

Primary key indexes (B-tree) exist on all tables via the `id` column. Additional index definitions (e.g., indexes on foreign key columns or frequently filtered fields) cannot be confirmed from the available source files, as no database migration files are present in the project repository. This limitation should be noted when performing performance analysis.

---

## Data Lifecycle

### Creation

All emission records are created by authenticated users via the corresponding module form components. Public questionnaire submissions are created via the `insert_public_deslocamento` RPC, which runs in a security-definer context to allow unauthenticated inserts.

### Updates

Inventories can be updated by organization administrators. Organization profile data (`organizacoes`) is updated via the Organization Profile page. Emission records do not support in-place editing in the current implementation; users must delete and re-enter incorrect records.

### Deletion

Emission records support deletion from the module's record table via a delete button. Deletion is a hard delete (permanent removal from the database). No soft-deletion patterns (e.g., `deleted_at` timestamp fields) are observed in the codebase.

### Archiving

No data archiving strategy is implemented. Inventories with a `status` of `concluido` (concluded) are treated as historical records but remain fully accessible and modifiable.
