`../../tiagosj-hash/climate-commute-tracker/`# Technical Specification 001

## General Definitions

- The project under `../../tiagosj-hash/climate-commute-tracker` will be referred as "Original Project" on this document.
- More details about Netinho platform as well as Mercado Net Zero (MNZ) systems can be found at `../documents` project.
- Check the document `documents/CONSTITUION.md` to understand MNZ system's constitution.
- A detailed description of Original Project architecture can be found at `documents/architecture/original/architecture.md`
- A detailed description of Original Project business rules can be found at `documents/architecture/original/business-rules.md`
- A detailed description of Original Project database model can be found at `documents/architecture/original/database-model.md`

---

## Climate Commute Tracker Migration Plan Elaboration

I need to elaborate a migration plan from current Climate Commute Tracker project (written through Lovable) to Mercado Net Zero Systems platform.
- The new project name will be "Meu Inventario"
- This project ("meu-inventario-backend") must focus only on the backend layer (database and business rules)
  - **Do not include any frontend logic on it.** This will be managed by another project.
  - The project must be written in Python
  - REST APIs must be written to allow interaction with the project
- A new Postgres database must be created for the project
  - Follow the models at `../containers` project to create a new database.
  - The project must contain the same model as the original one.
  - If there are data scripts, migrate them (rewriting if necessary) to `database/scripts` directory, and use a recommended script version controller (eG. Liquibase) to check scripts execution.
- Authentication and authorization rules must be migrated to Keycloak
  - The Keycloak instance can be found at `../container` project.
  - Check other projects such as `netinho-backend` and `file-storage` to understand how current authentication and authorization is done.
- Properly split the logic in domains
  - REST API routes must be based on these domains.
- The project must configure CORS
  - Check other projects such as `netinho-backend` and `file-storage` to understand how CORS is defined.

Ask me additional questions to improve this migration plan.