# Architecture Document — Climate Commute Tracker

## Project Overview

Climate Commute Tracker is a web-based GHG (Greenhouse Gas) Protocol emissions inventory management system. It enables organizations to record, calculate, and report greenhouse gas emissions across all three GHG Protocol scopes:

- **Scope 1**: Direct emissions from mobile combustion, stationary combustion, fugitive emissions, and effluent treatment.
- **Scope 2**: Indirect emissions from purchased electricity.
- **Scope 3**: Value chain emissions from business travel.

The system also includes a commuting sub-system ("Track My Carbon") for tracking employee commuting emissions, a public questionnaire feature for anonymous data collection via shareable links, and a consolidated reporting module capable of generating PDF and Excel exports.

Access to system features is controlled through a multi-level authorization model covering system access, emission scopes, and individual emission categories, all enforced at the database level via PostgreSQL Row-Level Security (RLS).

---

## Technology Stack

| Technology | Version | Role |
|---|---|---|
| React | 18.3.1 | UI framework |
| Vite | 5.4.19 | Build tool and development server |
| TypeScript | 5.8.3 | Static typing |
| React Router DOM | 7.12.0 | Client-side routing |
| Supabase JS Client | 2.84.0 | Database access and authentication |
| TanStack React Query | 5.83.0 | Server state management and caching |
| React Hook Form | 7.61.1 | Form state management |
| Zod | 3.25.76 | Schema validation |
| Tailwind CSS | 3.4.17 | Utility-first CSS styling |
| shadcn/ui | — | Component library (built on Radix UI) |
| Radix UI | multiple | Accessible UI primitives |
| Recharts | 2.15.4 | Chart and data visualization |
| jsPDF | 4.0.0 | PDF generation |
| jspdf-autotable | 5.0.7 | Table rendering in PDF exports |
| XLSX | 0.18.5 | Excel file parsing and generation |
| date-fns | 3.6.0 | Date utility functions |
| Sonner | 1.7.4 | Toast notifications |
| lucide-react | 0.462.0 | Icon library |
| qrcode.react | 4.2.0 | QR code generation |
| ESLint | 9.32.0 | Static code analysis |
| @vitejs/plugin-react-swc | 3.11.0 | Fast React compilation via SWC |

---

## Project Structure

```
climate-commute-tracker/
├── src/                    # Application source code
│   ├── App.tsx             # Root component, router configuration
│   ├── main.tsx            # Application entry point
│   ├── pages/              # Page-level components (one per route)
│   ├── components/         # Reusable business components
│   │   └── ui/             # shadcn/ui primitive components (excluded from documentation)
│   ├── contexts/           # React context providers for global state
│   ├── hooks/              # Custom React hooks
│   ├── integrations/
│   │   └── supabase/
│   │       ├── client.ts   # Supabase client initialization
│   │       └── types.ts    # Auto-generated TypeScript types from database schema
│   ├── lib/                # Utility functions
│   └── index.css           # Global styles
├── scripts/                # Utility scripts
├── public/                 # Static assets
├── docker/                 # Docker and container configuration
├── supabase/               # Supabase local configuration
├── package.json            # Dependencies and scripts
├── vite.config.ts          # Vite build configuration
├── tailwind.config.ts      # Tailwind CSS configuration
├── tsconfig.json           # TypeScript configuration
├── tsconfig.app.json       # TypeScript configuration for app code
└── tsconfig.node.json      # TypeScript configuration for Node.js tooling
```

---

## System Components

### Shared / Navigation

**NavLink** (`src/components/NavLink.tsx`)
Navigation link component used in the application's navigation bar. Renders a styled anchor element that integrates with React Router for client-side navigation.

**OrganizacaoSelector** (`src/components/OrganizacaoSelector.tsx`)
Dropdown selector that displays all organizations accessible to the current user. Setting a selection updates the `organizacaoAtual` value in `OrganizacaoContext`, which propagates throughout the application.

**InventarioSelector** (`src/components/InventarioSelector.tsx`)
Dropdown selector for choosing the active inventory within the currently selected organization. Updates `inventarioAtual` in `InventarioContext`. Only inventories belonging to the current organization are shown.

**Dashboard** (`src/components/Dashboard.tsx`)
Dashboard component for the Deslocamentos (commuting/business travel) system. Displays charts and aggregated analytics for emission records by transport type, period, and total tCO₂e.

**DashboardConsolidado** (`src/components/DashboardConsolidado.tsx`)
Consolidated emissions dashboard for the Inventário system. Displays aggregated emissions across all scopes (Scope 1, 2, and 3) using Recharts charts, grouped by emission category and period.

---

### Access Control

**ProtectedRoute** (`src/components/ProtectedRoute.tsx`)
Base route guard. Redirects unauthenticated users to the login page. Used as the outermost wrapper for all authenticated routes.

**AdminProtectedRoute** (`src/components/AdminProtectedRoute.tsx`)
Extends `ProtectedRoute`. Grants access only to users with the `isAdmin` flag from `useAuth`. Non-admin users are redirected.

**SystemProtectedRoute** (`src/components/SystemProtectedRoute.tsx`)
Grants access based on system-level permission (`inventario` or `deslocamentos`). Reads `systemAccess` from `useAuth` and redirects users who lack access to the requested system.

**OrgAdminProtectedRoute** (`src/components/OrgAdminProtectedRoute.tsx`)
Grants access to organization administrators. Verifies that the current user holds the org admin role for the organization specified in the route parameter.

---

### Scope 1 — Mobile Combustion

**CombustaoMovelModule** (`src/components/CombustaoMovelModule.tsx`)
Full CRUD module for registering mobile combustion emission records (Scope 1). Supports three calculation methods:
- Vehicle + fuel combination
- Fuel quantity only
- Vehicle + kilometer distance

Handles multiple transport types (car, truck, motorcycle, bus, train, airplane, ferry), fossil and biogenic fuel split, and calculates CO₂, CH₄, and N₂O emissions (both fossil and biogenic fractions). Displays a sortable, deletable table of existing records per organization and inventory.

**ImportacaoMassaMovelCard** (`src/components/ImportacaoMassaMovelCard.tsx`)
Card component for bulk-importing mobile combustion records from an Excel file. Parses the uploaded spreadsheet and inserts multiple records into `emissoes_combustao_movel` in a single operation.

---

### Scope 1 — Stationary Combustion

**CombustaoEstacionariaModule** (`src/components/CombustaoEstacionariaModule.tsx`)
CRUD module for registering stationary combustion emission records (Scope 1), such as emissions from boilers, furnaces, and generators. Supports fossil and biogenic fuel split. Fetches stationary-specific emission factors from `fatores_estacionaria`.

---

### Scope 1 — Fugitive Emissions

**EmissoesFugitivasModule** (`src/components/EmissoesFugitivasModule.tsx`)
CRUD module for registering fugitive emission records (Scope 1), such as refrigerant leaks and fire suppressant releases. The user selects a GHG gas and enters the quantity in kilograms; the module calculates tCO₂e using the gas's GWP value from the `gwp` table.

---

### Scope 1 — Effluents

**EfluentesModule** (`src/components/EfluentesModule.tsx`)
CRUD module for calculating and registering CH₄ and N₂O emissions from wastewater and effluent treatment (Scope 1). Implements a seven-step guided form covering effluent type (domestic or industrial), volume, organic load composition, treatment method, CH₄ recovery, sequential treatment, and final environmental disposal. Uses IPCC 2019 methodology.

---

### Scope 2 — Energy

**Escopo2Module** (`src/components/Escopo2Module.tsx`)
CRUD module for energy consumption records (Scope 2). Manages consumer units (`unidades_consumidoras`) and monthly electricity consumption entries (`consumo_energia`). Calculates tCO₂e using grid emission factors from `fatores_emissao_energia` based on year and month.

**EvidenciasConsumoEnergia** (`src/components/EvidenciasConsumoEnergia.tsx`)
Sub-component for attaching evidence documents (e.g., utility bills) to energy consumption records. Supports file upload to Supabase Storage and stores metadata in `evidencias_consumo_energia`.

---

### Scope 3 — Business Travel

**ViagensNegociosModule** (`src/components/ViagensNegociosModule.tsx`)
CRUD module for business travel emission records (Scope 3). Supports multiple transport modes (airplane, car, bus, train, subway, ferry) and multiple calculation approaches (distance-based, fuel-consumption-based). Calculates CO₂, CH₄, and N₂O emissions using transport-mode-specific emission factors. For air travel, calculates great-circle distance between airport pairs using coordinates from `aeroportos_coordenadas`.

---

### Commuting (Deslocamentos) Questionnaire Flow

These components implement the multi-step wizard used in both the private Deslocamentos system and the public questionnaire (`QuestionarioPublico`).

| Component | Purpose |
|---|---|
| **WelcomeStep** | Collects respondent name, email, and initiates the questionnaire flow |
| **LocationMethodStep** | Asks the user to choose between address-based or manual distance entry |
| **AddressStep** | Collects origin and destination addresses; computes driving distance via an external geocoding/routing service |
| **TransportStep** | Allows the user to select one or more transport modes used for the commute |
| **BusTypeStep** | Collects the specific bus category (urban, interstate, etc.) when bus is selected |
| **VehicleDetailsStep** | Collects vehicle year, fleet type, and fuel type when a motor vehicle is selected |
| **DistanceStep** | Collects distance manually when the user opts out of address lookup |
| **AirplaneReturnStep** | Collects return flight details for air travel entries |
| **LayoverStep** | Handles layover configuration for multi-leg flights |
| **SummaryStep** | Displays a summary of all collected information before final submission |
| **ResultStep** | Displays the calculated total emission result after saving |
| **EmissionForm** | Orchestrates the multi-step wizard for the authenticated Deslocamentos system |
| **PublicEmissionForm** | Orchestrates the multi-step wizard for the public token-based questionnaire |

---

### Admin / Data Import

**ImportAeroportosCard** (`src/components/ImportAeroportosCard.tsx`)
Admin card for importing airport coordinate data from an Excel file into the `aeroportos_coordenadas` table.

**ImportFatoresEnergiaCard** (`src/components/ImportFatoresEnergiaCard.tsx`)
Admin card for importing electricity emission factors from an Excel file into the `fatores_emissao_energia` table.

**ImportSpedCard** (`src/components/ImportSpedCard.tsx`)
Admin card for importing fuel consumption data from SPED (Brazilian tax authority) files, which are then used to populate mobile combustion records.

**ReprocessarEmissoesTab** (within `Admin.tsx`)
Admin interface section that triggers reprocessing of emission calculations across all records when emission factors are updated.

---

### Organizations

**OrganizacoesModule** (`src/components/OrganizacoesModule.tsx`)
Module for listing, creating, and managing organizations. Displays all organizations in the system and provides navigation to each organization's profile page.

---

### User Management

**OrgUserManagement** (`src/components/OrgUserManagement.tsx`)
Manages users within a specific organization. Allows organization administrators to add users, assign roles, and control access to modules, scopes, and emission categories.

**UserPermissionsDialog** (`src/components/UserPermissionsDialog.tsx`)
Modal dialog for editing a specific user's permissions within an organization. Allows granting or revoking access to systems, scopes, and emission categories.

---

### Public Questionnaires

**GerenciarQuestionariosPublicos** (`src/components/GerenciarQuestionariosPublicos.tsx`)
Admin component for creating, listing, and managing public questionnaires. Each questionnaire has a unique token and generates a shareable link and QR code. Displays aggregated statistics (total respondents, total emissions) per questionnaire.

---

## Data Flow

1. **User Interaction**: The user interacts with a React page or component.
2. **Local State**: Form state is managed by React Hook Form with Zod validation.
3. **Context State**: Organization and inventory selection is held in React Context (`OrganizacaoContext`, `InventarioContext`) and persisted to `localStorage`.
4. **Permission Check**: Before rendering sensitive content, components call `useUserPermissions()` to check category, scope, or system access. Permissions are cached in `sessionStorage` for 1 hour.
5. **Data Fetch**: Read operations use TanStack React Query or direct Supabase queries. The Supabase JavaScript client communicates with the hosted PostgreSQL database via REST API calls.
6. **RLS Enforcement**: All database queries are subject to PostgreSQL Row-Level Security policies. The `user_in_org` function ensures users can only access data belonging to their organizations.
7. **Write Operations**: Form submissions call Supabase insert/update/delete operations directly from component handlers.
8. **Emission Calculation**: Emission values are computed client-side at submission time using emission factors fetched from reference tables (`fatores_*`, `gwp`). Calculated values are stored alongside the raw inputs.
9. **UI Update**: After a successful write, the component refreshes its local data by re-querying or calling a context `refetch()` method. Toast notifications inform the user of success or failure.

---

## API Endpoints

The application communicates with Supabase exclusively. The Supabase project URL is provided via the `VITE_SUPABASE_URL` environment variable. The following Supabase RPC functions are used:

| Function | Signature | Description |
|---|---|---|
| `has_role` | `(user_id uuid, role app_role)` | Returns `true` if the user holds the specified global role (`admin`, `moderator`, `user`, `master`) |
| `has_system_access` | `(user_id uuid, system_name text)` | Returns `true` if the user has been granted access to the named system (`inventario`, `deslocamentos`) |
| `has_escopo_access` | `(user_id uuid, escopo text)` | Returns `true` if the user has been granted access to the specified emission scope (`escopo1`, `escopo2`, `escopo3`) |
| `has_categoria_access` | `(user_id uuid, categoria_id text)` | Returns `true` if the user has been granted access to the specified emission category (e.g., `combustao_movel`, `estacionaria`) |
| `is_org_admin` | `(user_id uuid, org_id uuid)` | Returns `true` if the user is an administrator of the specified organization |
| `user_in_org` | `(org_id uuid)` | RLS helper that returns `true` if the current database user belongs to the specified organization; used in RLS policies to enforce multi-tenant data isolation |
| `get_public_questionario_by_token` | `(token text)` | Retrieves a public questionnaire record by its unique token; accessible without authentication |
| `insert_public_deslocamento` | `(...)` | Inserts a commuting emission record submitted via the public questionnaire form; accessible without authentication |
| `check_rate_limit` | `(key text)` | Checks whether the rate limit threshold for the given key has been exceeded; used to protect public endpoints |
| `cleanup_rate_limits` | `()` | Removes expired rate limit entries from the `rate_limits` table |

In addition to RPC calls, the application performs direct table queries (SELECT, INSERT, UPDATE, DELETE) via the Supabase REST API for all entity tables documented in the database model.

---

## Frontend Pages and Views

| Page | File | Route | Access |
|---|---|---|---|
| Landing | `Landing.tsx` | `/` | Public |
| Login | `Login.tsx` | `/login` | Public |
| Signup | `Signup.tsx` | `/signup` | Public |
| Inventario | `Inventario.tsx` | `/inventario` | `SystemProtectedRoute` (inventario) |
| Deslocamentos | `Deslocamentos.tsx` | `/deslocamentos` | `SystemProtectedRoute` (deslocamentos) |
| Admin | `Admin.tsx` | `/admin` | `AdminProtectedRoute` |
| UserManagement | `UserManagement.tsx` | `/admin/usuarios` | `AdminProtectedRoute` |
| Organizacoes | `Organizacoes.tsx` | `/admin/organizacoes` | `AdminProtectedRoute` |
| OrganizacaoPerfilPage | `OrganizacaoPerfilPage.tsx` | `/organizacao/:id` or `/admin/organizacoes/:id` | `OrgAdminProtectedRoute` or `AdminProtectedRoute` |
| QuestionarioPublico | `QuestionarioPublico.tsx` | `/q/:token` | Public (no authentication) |
| QuestionarioDashboardPublico | `QuestionarioDashboardPublico.tsx` | `/dashboard/:token` | Public (no authentication) |
| Manual | `Manual.tsx` | `/manual` | Authenticated |
| Glossario | `Glossario.tsx` | `/glossario` | Authenticated |
| FAQ | `FAQ.tsx` | `/faq` | Authenticated |
| Ajuda | `Ajuda.tsx` | `/ajuda` | Authenticated |
| NotFound | `NotFound.tsx` | `*` | Public |

**Inventario.tsx** is the primary interface for GHG inventory management. It renders a tabbed interface with tabs for Scope 1 (sub-tabbed by category), Scope 2, Scope 3, a consolidated dashboard, and a report generation tab. Tabs visible to a user are determined by their permission set.

**Deslocamentos.tsx** provides the business travel and commuting interface, with tabs for the emission entry form and the analytics dashboard.

**Admin.tsx** is the system administration hub, providing access to user management, organization management, public questionnaire management, and data import tools (emission factors, airport coordinates, SPED files).

**QuestionarioPublico.tsx** hosts the public commuting questionnaire. It is accessed via a token-based URL (`/q/:token`) with no authentication requirement. The questionnaire token is validated via the `get_public_questionario_by_token` RPC before the form is rendered.

**QuestionarioDashboardPublico.tsx** displays the aggregated results of a public questionnaire accessible via `/dashboard/:token`, also without authentication.

---

## External Dependencies

| Service | Role |
|---|---|
| **Supabase** | Hosted PostgreSQL database, authentication, REST API, RPC functions, Row-Level Security, and file storage |

The Supabase project URL and public API key are provided at build time via the environment variables `VITE_SUPABASE_URL` and `VITE_SUPABASE_PUBLISHABLE_KEY`. These values are embedded in the built JavaScript bundle by Vite.

No other external services are called by the application.

---

## Authentication and Authorization

### Authentication

Authentication is handled entirely by Supabase Auth. The Supabase client is initialized with `persistSession: true` and `autoRefreshToken: true`, with session tokens stored in `localStorage`. The `useAuth` hook subscribes to the Supabase auth state and exposes the current `user` object and derived permission flags to the rest of the application.

**Inactivity logout**: Users are automatically signed out after 30 minutes of inactivity. The `useAuth` hook tracks user interaction events and triggers `supabase.auth.signOut()` when the inactivity threshold is reached.

### Authorization Model

The system implements a five-level authorization hierarchy:

| Level | Description |
|---|---|
| **Global role** | `admin`, `moderator`, `user`, `master` — stored in `user_roles`; checked via the `has_role` RPC |
| **System access** | `inventario` or `deslocamentos` — stored in `user_systems`; checked via `has_system_access` |
| **Organization membership** | Stored in `organizacao_usuarios`; enforced by RLS via `user_in_org` |
| **Scope access** | `escopo1`, `escopo2`, `escopo3` — stored in `user_permissoes`; checked via `has_escopo_access` |
| **Category access** | Per emission category (e.g., `combustao_movel`, `estacionaria`) — stored in `user_permissoes`; checked via `has_categoria_access` |

**Full access**: Users with the system admin role or the organization admin role receive full access to all scopes and categories within their scope of authority.

**Permission caching**: Permission check results are cached in `sessionStorage` with a 1-hour TTL. Cache is keyed by user ID and organization ID to prevent cross-user or cross-organization leakage.

**Row-Level Security (RLS)**: All data access is enforced at the PostgreSQL level via RLS policies. The `user_in_org` function is used as the core predicate in RLS policies for organization-scoped tables, ensuring that users can never read or write data outside their authorized organizations regardless of client-side checks.
