# Business Rules Document — Climate Commute Tracker

## Domain Entities

### Organization (`organizacoes`)

An Organization represents a legal entity that uses the system to manage its GHG emissions inventory. Each organization has a unique identifier, a name, CNPJ, CNAE, address data, contact information, and operational metadata such as number of employees, industry segment, and activity description. Organizations can be individually enabled for each system module (`modulo_inventario_habilitado`, `modulo_deslocamentos_habilitado`). Organizations have an active/inactive status (`ativa`).

### Inventory (`inventarios`)

An Inventory is the primary container for all emission records within a given organization and calendar year. Each inventory belongs to exactly one organization and covers exactly one base year (`ano_base`). It has a name, an optional description, a status field, and optional start and end dates. Emission records of all categories are always associated with an inventory.

### User (`profiles`, `user_roles`, `user_systems`, `user_permissoes`)

A User is a person who accesses the system via Supabase Auth. The `profiles` table stores the user's display name and email. Global roles are stored in `user_roles` (values: `admin`, `moderator`, `user`, `master`). System-level access grants are stored in `user_systems`. Organization-scoped permissions are stored in `user_permissoes`, with a `tipo` field classifying each grant as `sistema`, `escopo`, or `categoria`, and a `referencia` field identifying the target system, scope, or category.

### Emission Records

Each emission scope and category is represented by a dedicated table. Records in each table are always linked to an organization (`organizacao_id`) and, in most cases, to an active inventory (`inventario_id`). Raw input values (fuel quantity, distance, volume, etc.) are stored alongside the calculated emission values (CO₂, CH₄, N₂O in tonnes, and the total in tCO₂e). Biogenic emissions are stored in dedicated fields and are not included in the `total_tco2e` sum.

### Emission Factors

Reference tables store the emission factors used in calculations. These include fuel-based factors (`fatores_tipo_combustivel`, `fatores_frota_tipo_combustivel`, `fatores_estacionaria`), energy grid factors (`fatores_emissao_energia`), aerial transport factors (`fatores_emissao_aereas`), bus transport factors (`fatores_transporte_onibus`), and effluent treatment factors (`fatores_tratamento_efluentes`). Emission factors are not modified by end users under normal circumstances; they are managed by system administrators via the Admin import tools.

### Public Questionnaire (`questionarios_salvos`, `questionarios_respondentes`)

A Public Questionnaire is a shareable form linked to an organization, used to collect commuting emission data from individuals (e.g., employees or event participants) without requiring them to authenticate. Each questionnaire has a unique token used to construct the public URL. The `questionarios_respondentes` table records each respondent's name and email. Emission entries submitted via the questionnaire are stored in `questionarios_deslocamentos`.

---

## Business Rules

### Inventory Rules

- An inventory belongs to exactly one organization and one calendar year (`ano_base`). The system does not enforce a uniqueness constraint at the database level, but the expected usage model is one active inventory per organization per year.
- Emission records of all categories are always linked to an active inventory. Records cannot be entered without first selecting an organization and an inventory.
- An inventory's `ano_base` determines which emission factors and energy grid factors are applied during calculation.

### User and Access Rules

- Users can only access data belonging to organizations they are associated with. This rule is enforced at the database level via PostgreSQL RLS policies using the `user_in_org` helper function.
- Access to each emission scope (Scope 1, Scope 2, Scope 3) is controlled separately per user. A user may have access to Scope 1 without having access to Scope 2 or Scope 3.
- Access to each emission category within a scope is controlled separately per user. For example, within Scope 1, a user may have access to mobile combustion (`combustao_movel`) but not to stationary combustion (`estacionaria`).
- System administrators (`role = admin` or `role = master`) have unrestricted access to all organizations, scopes, and categories.
- Organization administrators have full access to all scopes and categories within the organizations they administer, without needing explicit per-category grants.
- Regular users require explicit permission grants for each system (`inventario` or `deslocamentos`), each scope, and each emission category they need to access.

### Public Questionnaire Rules

- Public questionnaires are accessed via unique tokens embedded in the URL (`/q/:token`). No authentication is required to submit a response.
- Rate limiting applies to all public endpoints. The `check_rate_limit` RPC is called before processing any public submission. If the rate limit is exceeded, the submission is rejected.
- A questionnaire can be deactivated (`ativo = false`), at which point the public form becomes inaccessible even if the token URL is known.

### Session Rules

- Users are automatically logged out after 30 minutes of inactivity. Inactivity is detected by the absence of user interaction events tracked by the `useAuth` hook.
- Permission data fetched from the database is cached in `sessionStorage` for 1 hour. After cache expiration, the next permission check triggers a fresh database query.

---

## Workflows

### Entering a New Emission Record

1. The user selects an organization from the `OrganizacaoSelector` dropdown.
2. The user selects an inventory from the `InventarioSelector` dropdown. If no inventory exists, the user must create one first.
3. The user navigates to the Inventário page and selects the appropriate scope tab (Scope 1, 2, or 3) and, within Scope 1, the appropriate category sub-tab.
4. The user fills out the emission entry form within the relevant module component.
5. The component computes emission values client-side using the appropriate emission factors fetched from the database.
6. On form submission, the module inserts a record into the corresponding emission table via the Supabase client.
7. A success toast notification is displayed and the module's record list is refreshed.

### An Administrator Granting Access to a User

1. The administrator navigates to the Admin page or the Organization Profile page.
2. The administrator locates the target user in the user list.
3. The administrator opens the `UserPermissionsDialog` for that user.
4. The administrator selects the system (`inventario` or `deslocamentos`), scopes (`escopo1`, `escopo2`, `escopo3`), and emission categories to grant.
5. On confirmation, the dialog inserts records into `user_permissoes` (for scopes and categories) and `user_systems` (for system-level access) via the Supabase client.
6. The user's permission cache is invalidated on their next session or after the 1-hour TTL expires.

### Submitting the Public Commuting Questionnaire

1. An authenticated user or administrator creates a public questionnaire in the `GerenciarQuestionariosPublicos` component, which generates a unique token and a shareable URL and QR code.
2. An anonymous respondent accesses the public URL (`/q/:token`).
3. The `QuestionarioPublico` page calls `get_public_questionario_by_token` to validate the token and retrieve questionnaire metadata.
4. If the questionnaire is active, the multi-step `PublicEmissionForm` wizard is rendered.
5. The respondent completes the wizard steps: welcome and identification, transport mode selection, location or distance entry, vehicle details (if applicable), and summary review.
6. On final submission, the `insert_public_deslocamento` RPC is called, which inserts the respondent record and the commuting emission entry, and updates the questionnaire's aggregated totals.
7. The `ResultStep` component displays the calculated emission result to the respondent.

### Generating a PDF or Excel Emissions Report

1. The user navigates to the Inventário page and selects the Reports tab.
2. The `RelatorioEmissoesModule` fetches all emission records for the selected organization and inventory across all scopes.
3. The user selects the desired export format (PDF or Excel).
4. For PDF: jsPDF and jspdf-autotable render a formatted report document, which is downloaded by the browser.
5. For Excel: the XLSX library generates a workbook with separate sheets per scope/category, which is downloaded by the browser.

---

## Calculations and Formulas

### Mobile Combustion (Scope 1)

**Inputs**: fuel quantity (with unit), fossil/biogenic fuel split, emission factors for CO₂, CH₄, and N₂O per fuel type and vehicle type, and GWP values.

**Formula**:
```
CO₂ (t)  = quantity_fossil × factor_CO₂
CH₄ (t)  = quantity_fossil × factor_CH₄ × GWP_CH₄ / 1000  [for tCO₂e contribution]
N₂O (t)  = quantity_fossil × factor_N₂O × GWP_N₂O / 1000  [for tCO₂e contribution]

total_tCO₂e = (CO₂_fossil) + (CH₄_fossil × GWP_CH₄) + (N₂O_fossil × GWP_N₂O)

CO₂_biogenic (t) = quantity_biofuel × factor_CO₂_biogenic
CH₄_biogenic (t) = quantity_biofuel × factor_CH₄_biogenic
N₂O_biogenic (t) = quantity_biofuel × factor_N₂O_biogenic
```

Biogenic emissions are stored separately and excluded from `total_tCO₂e`.

When the calculation method is vehicle + kilometers (`veiculo_km`), the fuel consumption equivalent is first derived using the vehicle's fuel economy from `consumo_unidade_medida` before applying the emission factors.

---

### Stationary Combustion (Scope 1)

Same structure as mobile combustion, using stationary-specific emission factors from `fatores_estacionaria` per fuel type and sector. Sector-specific CH₄ and N₂O factors apply based on whether the combustion occurs in energy production, manufacturing, commercial/institutional, or residential/agricultural contexts.

---

### Fugitive Emissions (Scope 1)

**Inputs**: GHG gas type (selected from the `gwp` table), quantity in kilograms.

**Formula**:
```
tCO₂e = quantity_kg × GWP_value / 1000
```

The GWP value is looked up from the `gwp` table for the selected gas. The result is stored as `emissoes_tco2e`.

---

### Effluent Treatment (Scope 1)

Follows the IPCC 2019 Tier 1 methodology for wastewater-related CH₄ and N₂O emissions.

**Inputs**: effluent volume (m³/year), organic load at inlet (kg DQO/m³ or kg DBO/m³), organic load removed in sludge (kg/m³), treatment method and its Methane Conversion Factor (MCF), CH₄ recovered (tCH₄/year), nitrogen concentration in effluent (kgN/m³), and N₂O emission factor (kgN₂O-N/kgN).

**CH₄ formula**:
```
organic_load_net (kg/year) = volume × (organic_load_inlet − organic_load_sludge)
B₀ = 0.25 (if DQO) or 0.60 (if DBO)   [maximum CH₄ production capacity, kgCH₄/kg]

CH₄_primary (kg) = organic_load_net × B₀ × MCF_treatment_1

If sequential treatment:
  residual_load = organic_load_net × (1 − MCF_treatment_1)
  CH₄_secondary (kg) = residual_load × B₀ × MCF_treatment_2
  CH₄_total (kg) = CH₄_primary + CH₄_secondary

If effluent discharged to environment:
  residual_load = organic_load_net × (1 − MCF_treatment_1) × (1 − MCF_treatment_2 if sequential)
  CH₄_disposal (kg) = residual_load × B₀ × MCF_disposal
  CH₄_total (kg) += CH₄_disposal

CH₄ (t) = max(0, CH₄_total / 1000 − CH₄_recovered)
```

**N₂O formula**:
```
N₂O_kg = volume × nitrogen_concentration × emission_factor_N₂O × (44/28)
N₂O (t) = N₂O_kg / 1000
```

**Total**:
```
tCO₂e = (CH₄_t × 28) + (N₂O_t × 265)
```

**Biogenic CO₂**:
```
CO₂_biogenic (t) = CH₄_recovered × (44/16)   [if CH₄ is burned; molecular weight conversion]
```

---

### Energy Consumption (Scope 2)

**Inputs**: electricity consumed (MWh), grid emission factor for the applicable year and month (from `fatores_emissao_energia`).

**Formula**:
```
tCO₂e = MWh_consumed × grid_emission_factor
```

The emission factor varies by the year and month of consumption, reflecting changes in the Brazilian national electricity grid emission factor over time.

---

### Business Travel (Scope 3)

**Inputs**: transport mode, distance (km), number of passengers, emission factors per transport mode.

**Base formula**:
```
CO₂ (t) = distance × passengers × factor_CO₂ / 1000
CH₄ (t) = distance × passengers × factor_CH₄ / 1000
N₂O (t) = distance × passengers × factor_N₂O / 1000
tCO₂e   = (CO₂ × 1) + (CH₄ × GWP_CH₄) + (N₂O × GWP_N₂O)
```

For **air travel**, distance is calculated as the great-circle distance between origin and destination airport coordinates (from `aeroportos_coordenadas`), multiplied by a route deviation factor (`acrescimo_rota`) from `fatores_emissao_aereas`. The emission factors are differentiated by distance range (`distancia_aerea`): short-haul, medium-haul, and long-haul.

For **bus travel**, emission factors are sourced from `fatores_transporte_onibus`, differentiated by bus type and fuel (diesel vs. biodiesel).

For **subway and metro**, emission factors are sourced from `transporte_metro` and `transporte_trem` tables respectively.

---

### Biogenic Emissions

Biogenic CO₂, CH₄, and N₂O emissions arise from the combustion of biofuels (e.g., ethanol, biodiesel). These are calculated using biogenic-specific emission factors and stored in dedicated fields (`emissoes_co2_biogenico`, `emissoes_ch4_biogenico`, `emissoes_n2o_biogenico`). Biogenic emissions are **never summed into** the `total_tco2e` figure. They are reported separately in compliance with GHG Protocol accounting rules.

---

## Edge Cases

### Commuting Module Access

The commuting sub-system (`deslocamentos`) is optional. Access requires an explicit system-level grant (`user_systems` entry with `system_name = 'deslocamentos'`). Organizations can also independently enable or disable the module via `modulo_deslocamentos_habilitado`. Users without this access see the Deslocamentos system tab but are redirected by `SystemProtectedRoute` if they attempt to navigate directly to it.

### Biogenic Emissions Exclusion

Biogenic emissions are tracked and stored but are intentionally excluded from the total tCO₂e figure used for GHG Protocol reporting. The distinction between fossil and biogenic fractions is enforced in all module components that handle fuels with a biogenic component (ethanol, biodiesel, blended fuels like gasoline and flex-fuel vehicles).

### Missing or Unavailable Emission Factors

When an emission factor cannot be found for the selected fuel type, vehicle type, year, or grid region, the module displays an error or warning to the user and prevents form submission. Calculated emission fields are set to `null` in such cases, rather than defaulting to zero, to avoid silently underreporting emissions.

### Fuel Composition for Blended Fuels

Brazil's fuel market uses blended fuels (e.g., gasoline with mandatory ethanol content, diesel with mandatory biodiesel content). The `composicao_combustiveis` table and the `fatores_variaveis_ghg` table store the percentage composition of ethanol in gasoline and biodiesel in diesel by year and month. Mobile combustion calculations automatically split the fuel quantity into fossil and biogenic fractions based on these composition factors.

### Rate Limiting on Public Endpoints

All operations on the public questionnaire (`/q/:token`) route are subject to rate limiting enforced via the `check_rate_limit` RPC function. The rate limit key is typically derived from the client IP address. Submissions that exceed the rate limit threshold are rejected with an error response. Expired rate limit entries are cleaned up periodically via the `cleanup_rate_limits` RPC.
