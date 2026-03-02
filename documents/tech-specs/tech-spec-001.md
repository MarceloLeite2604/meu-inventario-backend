# Technical Specification 001

## General Definitions

- The project under `../../tiagosj-hash/climate-commute-tracker` will be referred as "Original Project" on this document.

---

## Implementation Decisions

The following decisions were made during the planning phase and must be followed throughout the implementation:

| Topic | Decision |
|---|---|
| Document language | **English** |
| React component documentation scope | **Business components only** — exclude all components under `src/components/ui/` (shadcn/ui primitives) |
| Database table coverage | **All tables** — infer field definitions, types, and nullability from the auto-generated TypeScript types file (`src/integrations/supabase/types.ts`) |
| Commuting module depth | **High-level summary only** — describe the commuting sub-system briefly, without full table-level or business-rule-level detail |

---

## Climate Commute Tracker Architecture Analysis

All documents described on this section must be written under `documents/architecture/original` directory.

### Source Files to Read

The following files from the Original Project must be read before writing any document:

- `src/App.tsx` — routing configuration and page structure
- `src/integrations/supabase/types.ts` — all table definitions with field names, types, and nullability
- `src/hooks/useAuth.ts` — authentication and role checking logic
- `src/hooks/useUserPermissions.ts` — permission checking logic
- `src/contexts/InventarioContext.tsx` — inventory state management
- `src/contexts/OrganizacaoContext.tsx` — organization state management
- `src/pages/*.tsx` — all page components
- `src/components/*.tsx` — all business components (excluding `src/components/ui/`)
- `package.json` — technology stack and dependency versions
- `vite.config.ts` — build configuration
- `README.md` — project overview and setup instructions

### Original Project Reading

Before writing any document, read and understand the Original Project thoroughly:

- Read all source code files, configuration files, and dependency manifests.
- Identify all domains, business entities, and their relationships.
- Understand all API endpoints, their purposes, and expected request/response formats.
- Understand all frontend pages, their purposes, and the data they collect or display.
- Understand the data flow between all components of the system.
- Understand the data persistence model, including the database structure and its relationships.
- Identify all external dependencies, third-party services, and integrations.
- Identify how authentication and authorization are handled.

### Architecture Document (`architecture.md`)

Write a detailed document describing the Original Project architecture. The document must cover the following sections:

- **Project Overview**: Purpose (GHG Protocol emissions inventory management), goals, and high-level description of what the system does.
- **Technology Stack**: All languages, frameworks, libraries, and tools used in the project, including their versions. The following are known to be present and must be included:
  - React 18, Vite, TypeScript
  - Supabase (PostgreSQL + Auth)
  - Tailwind CSS, shadcn/ui, Radix UI
  - TanStack React Query
  - React Router DOM
  - React Hook Form + Zod
  - Recharts
  - jsPDF + jspdf-autotable
  - XLSX
  - ESLint
- **Project Structure**: Directory and module organization, explaining the role of each major directory and file group. The top-level structure includes: `src/`, `scripts/`, `public/`, `docker/`.
- **System Components**: Description of each business component (exclude `src/components/ui/` shadcn primitives), grouped by domain:
  - **Shared / Navigation**: `NavLink`, `InventarioSelector`, `OrganizacaoSelector`, `Dashboard`, `DashboardConsolidado`
  - **Access Control**: `ProtectedRoute`, `AdminProtectedRoute`, `OrgAdminProtectedRoute`, `SystemProtectedRoute`
  - **Scope 1 — Mobile Combustion**: `CombustaoMovelModule`, `ImportacaoMassaMovelCard`
  - **Scope 1 — Stationary Combustion**: `CombustaoEstacionariaModule`
  - **Scope 1 — Fugitive Emissions**: `EmissoesFugitivasModule`
  - **Scope 1 — Effluents**: `EfluentesModule`
  - **Scope 2 — Energy**: `Escopo2Module`, `EvidenciasConsumoEnergia`
  - **Scope 3 — Business Travel**: `ViagensNegociosModule`
  - **Commuting (Deslocamentos) Questionnaire Flow**: `WelcomeStep`, `LocationMethodStep`, `AddressStep`, `TransportStep`, `BusTypeStep`, `VehicleDetailsStep`, `DistanceStep`, `AirplaneReturnStep`, `LayoverStep`, `SummaryStep`, `ResultStep`, `EmissionForm`, `PublicEmissionForm`
  - **Admin / Data Import**: `ImportAeroportosCard`, `ImportFatoresEnergiaCard`, `ImportSpedCard`, `ReprocessarEmissoesTab`
  - **Organizations**: `OrganizacoesModule`
  - **User Management**: `OrgUserManagement`, `UserPermissionsDialog`
  - **Public Questionnaires**: `GerenciarQuestionariosPublicos`
- **Data Flow**: How data moves through the system, from user interaction through React state (Context + TanStack Query) to Supabase REST/RPC calls, PostgreSQL, and back to the UI.
- **API Endpoints**: The Original Project communicates with Supabase exclusively. Document all Supabase RPC functions, including:
  - `has_role(user_id, role)` — checks if a user has a given role
  - `has_system_access(user_id, system_name)` — checks if a user has access to a given system
  - `has_escopo_access(user_id, escopo)` — checks if a user has access to a given emission scope
  - `has_categoria_access(user_id, categoria_id)` — checks if a user has access to a given category
  - `is_org_admin(user_id, org_id)` — checks if a user is an organization administrator
  - `user_in_org(org_id)` — RLS policy helper to filter data by user's organizations
  - `get_public_questionario_by_token(token)` — retrieves a public questionnaire by its unique token
  - `insert_public_deslocamento(...)` — inserts a commuting record submitted via the public questionnaire
  - `check_rate_limit(key)` — checks whether the rate limit for a given key has been exceeded
  - `cleanup_rate_limits()` — cleans up expired rate limit entries
- **Frontend Pages and Views**: All pages found under `src/pages/`, including:
  - `Landing.tsx` — public landing page
  - `Login.tsx` — authentication page
  - `Signup.tsx` — user registration page
  - `Inventario.tsx` — main emissions inventory interface (Scopes 1, 2, 3 entry and reporting)
  - `Deslocamentos.tsx` — commuting emissions management
  - `Organizacoes.tsx` — organizations listing and management
  - `OrganizacaoPerfilPage.tsx` — organization profile and settings
  - `UserManagement.tsx` — user management interface
  - `Admin.tsx` — system administration dashboard
  - `QuestionarioPublico.tsx` — public commuting questionnaire (anonymous access via token)
  - `QuestionarioDashboardPublico.tsx` — public dashboard for questionnaire results
  - `Ajuda.tsx` — help page
  - `Manual.tsx` — user manual page
  - `Glossario.tsx` — glossary page
  - `FAQ.tsx` — frequently asked questions page
  - `NotFound.tsx` — 404 not found page
- **External Dependencies**: Supabase (hosted PostgreSQL database and authentication). Document the Supabase project URL and any other external services identified during reading.
- **Authentication and Authorization**: Supabase Auth is used for user identity. The authorization model is multi-level:
  - **Roles**: system admin, organization admin, regular user
  - **System access**: `inventario`, `deslocamentos` — users must be explicitly granted access to each system
  - **Scope access**: `escopo1`, `escopo2`, `escopo3` — users must be explicitly granted access to each emission scope
  - **Category access**: fine-grained access per emission category (e.g., `combustao_movel`, `estacionaria`)
  - **Permission caching**: permissions are cached in the browser for 1 hour to reduce database queries
  - **Row-Level Security (RLS)**: all data access is enforced at the database level via PostgreSQL RLS policies
  - **Inactivity logout**: users are automatically logged out after 30 minutes of inactivity

### Business Rules Document (`business-rules.md`)

Write a detailed document describing the Original Project business rules. The document must cover the following sections:

- **Domain Entities**: All business entities recognized by the system, their meanings, and their attributes. At minimum, the following entities must be covered:
  - Organization (`organizacoes`)
  - Inventory (`inventarios`) — one per organization per calendar year
  - User (`profiles`, `user_roles`, `user_systems`, `user_permissoes`)
  - Emission records — one per emission category per scope
  - Emission factors — reference data used for calculations
  - Public Questionnaire (`questionarios_salvos`, `questionarios_respondentes`)
- **Business Rules**: All rules that govern the system behavior, including:
  - Validation rules applied to data inputs.
  - Constraints and conditions on operations.
  - Rules for state transitions.
  - At minimum, the following rules must be documented:
    - An inventory belongs to exactly one organization and one calendar year.
    - Users can only access data belonging to organizations they are associated with.
    - Access to each emission scope (1, 2, 3) is controlled separately per user.
    - Access to each emission category is controlled separately per user.
    - Emission records are always linked to an active inventory.
    - Public questionnaires are accessed via unique tokens; no authentication is required.
    - Rate limiting applies to all public endpoints.
    - Users are automatically logged out after 30 minutes of inactivity.
    - Permission data is cached for 1 hour.
- **Workflows**: Step-by-step descriptions of the main user journeys, including at minimum:
  - Entering a new emission record (select organization → select inventory → select scope and category → fill form → save)
  - An administrator granting system, scope, or category access to a user
  - Submitting the public commuting questionnaire (anonymous access via token-based URL)
  - Generating a PDF or Excel emissions report
- **Calculations and Formulas**: All GHG Protocol emission formulas applied in the system, with inputs, outputs, and logic. At minimum, the following must be documented:
  - **Mobile Combustion (Scope 1)**: `fuel_quantity × emission_factor(CO2, CH4, N2O) × GWP`
  - **Stationary Combustion (Scope 1)**: same structure as mobile combustion, using stationary-specific emission factors per fuel type
  - **Fugitive Emissions (Scope 1)**: document the specific formula used
  - **Effluent Treatment (Scope 1)**: `volume × nitrogen_content × treatment_method_factor`
  - **Energy Consumption (Scope 2)**: `MWh_consumed × grid_emission_factor` (factor varies by grid region and year)
  - **Business Travel (Scope 3)**: `distance × passenger_count × transport_mode_factor`
  - **Biogenic emissions**: tracked separately; not summed into the total tCO2e figure
- **Edge Cases**: Identified edge cases and how the system handles them. At minimum:
  - Commuting module is optional; not all users have access to it.
  - Biogenic emissions are excluded from the total tCO2e sum.
  - Missing or unavailable emission factors.

### Database Model Document (`database-model.md`)

Write a detailed document describing the Original Project database model. The document must cover the following sections:

- **Overview**: Supabase-hosted PostgreSQL. Accessed via the Supabase JavaScript client using REST API and RPC calls. TypeScript types are auto-generated from the database schema and available at `src/integrations/supabase/types.ts`. Row-Level Security (RLS) policies enforce multi-tenant data isolation.
- **Entities and Tables**: All tables must be individually documented. For each table, provide:
  - The purpose of the entity.
  - All fields with their names, data types, nullability, and a description of what they represent.
  - The primary key.
  - Field definitions must be inferred from `src/integrations/supabase/types.ts`.

  Tables must be grouped by domain:
  - **Organizations and Users**: `organizacoes`, `organizacao_usuarios`, `profiles`, `user_roles`, `user_systems`, `user_permissoes`, `categorias_permissao`
  - **Inventories**: `inventarios`
  - **Scope 1 — Mobile Combustion**: `emissoes_combustao_movel` and any related tables
  - **Scope 1 — Stationary Combustion**: `emissoes_estacionaria` and any related tables
  - **Scope 1 — Fugitive Emissions**: `emissoes_fugitivas` and any related tables
  - **Scope 1 — Effluents**: `emissoes_efluentes` and any related tables
  - **Scope 2 — Energy**: `consumo_energia`, `evidencias_consumo_energia`, `unidades_consumidoras` and any related tables
  - **Scope 3 — Business Travel**: `emissoes_viagens_negocios` and any related tables
  - **Emission Factors**: all `fatores_*` tables
  - **Reference Data**: `gwp`, `composicao_combustiveis`, `equivalencia_veiculos`, `aeroportos_coordenadas`, `tipos_efluentes_industriais`
  - **Public Questionnaires**: `questionarios_salvos`, `questionarios_respondentes`
  - **Commuting Sub-system**: all `commuting_*` tables (documented at a high level)
  - **Utility**: `rate_limits` and any other auxiliary tables
- **Relationships**: All relationships between entities, inferred from the TypeScript types and component code, including:
  - The nature of each relationship (one-to-one, one-to-many, many-to-many).
  - Foreign key references.
  - Any join or association tables used.
- **Indexes**: Primary key indexes are present on all tables. Additional index definitions cannot be confirmed from the available source files (no database migration files are present). This limitation must be noted in the document.
- **Data Lifecycle**: How data is created, updated, and deleted within the system. Note whether any soft-deletion patterns or archiving strategies are observed in the code.
