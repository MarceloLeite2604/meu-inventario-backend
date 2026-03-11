# Mercado Net Zero - Project Constitution

This document defines the standards, conventions, and best practices for all Mercado Net Zero projects.

---

## Table of Contents

- [General Guidelines](#general-guidelines)
  - [Version Control](#version-control)
  - [Project Initialization](#project-initialization)
  - [Development Environment](#development-environment)
  - [Documentation Standards](#documentation-standards)
  - [Environment Variables](#environment-variables)
  - [Infrastructure Scripts Integration](#infrastructure-scripts-integration)
  - [Project Build](#project-build)
  - [Project Execution](#project-execution)
- [Code Writing and Style](#code-writing-and-style)
  - [General Principles](#general-principles)
  - [Naming Conventions](#naming-conventions)
  - [Logging](#logging)
- [Project Contribution](#project-contribution)
  - [Manual Contributions](#manual-contributions)
  - [GitHub Copilot Contributions](#github-copilot-contributions)
- [Docker and Containerization](#docker-and-containerization)
  - [Docker Directory Structure](#docker-directory-structure)
  - [Dockerfile Best Practices](#dockerfile-best-practices)
  - [Docker Compose Configuration](#docker-compose-configuration)
- [Backend Projects](#backend-projects)
  - [Technology Stack](#technology-stack)
  - [Environment Setup](#environment-setup)
  - [Type Checking](#type-checking)
  - [VSCode Configuration](#vscode-configuration)
  - [REST API](#rest-api)
  - [Docker Configuration for Backend](#docker-configuration-for-backend)
  - [Tests](#tests)
  - [Debugging](#debugging)
- [Frontend Projects](#frontend-projects)
  - [Technology Stack](#technology-stack-1)
  - [Code Writing](#code-writing)
  - [VSCode Configuration](#vscode-configuration-1)
  - [Configuration Files](#configuration-files)
  - [Docker Configuration for Frontend](#docker-configuration-for-frontend)
  - [Tests](#tests-1)
  - [Version Control](#version-control-1)
- [Claude Code](#claude-code)
  - [Settings](#settings)
  - [Plan Execution Rules](#plan-execution-rules)

---

## General Guidelines

The following items are general instructions to be followed when working on any project.

### Version Control

- Projects must use **git** to manage their code.
- Git main branch must be named as `main`.

### Project Initialization

- When creating a new project, **always** use `isinit` command to initialize the project according to Mercado Net Zero standards.
- `infrastructure-scripts` project is available locally at `/home/marcelo/Documents/git/Mercado-Net-Zero/infrastructure-scripts`.

### Development Environment

- Projects will use **VSCode** as its editor.

### Documentation Standards

- When elaborating the `README.md` document, there is no need to add sections explaining the project structure.
- Do not mention `isstart` command in documentation. Projects must be executed through `iscomp` command.
- There is no need for the reader to execute `isinit` command in the README.md. This is done when a new project is created.
- Unless explicitly mentioned by the user, **do not** modify any technical specification document (`tech-spec-<nnn>.md` files) as well as additional resources located at `documents/tech-specs` directory.

### Environment Variables

All environment variables used by the project must be defined with the prefix `MNZ_<PROJECT_CODE>_`, where `<PROJECT_CODE>` is a code which identifies the project. Examples:

- workbook-to-bundles-converter: `W2BC`
- pdf-to-markdown-converter: `P2MDC`
- netinho-backend: `NB`
- netinho-frontend: `NF`

#### Environment Variables Detection

When elaborating project documentation, be sure to inform how environment variables detection works:

- **`docker/.env.compose`**: Used when building Docker images and spinning up containers.
- **`.env`**: Used for project execution in all environments (`dev-native`, `dev-container`, and `production`).
- **`.env.<environment>`**: Used for project execution in specific environments (e.g., `.env.dev-native`, `.env.dev-container`, `.env.production`).
- Additional environment variables might be defined and used throughout other commands. It is necessary to check `infrastructure-scripts` documentation to understand which they are and when they are used.

#### Infrastructure Scripts Managed Variables

Some environment variables are automatically defined by `infrastructure-scripts` commands and do not need to be manually set by the user:

- `HOST_UID`: Automatically set to the host user ID
- `HOST_GID`: Automatically set to the host group ID
- `HOST_USERNAME`: Automatically set to the host username
- `IMAGE_TAG`: Automatically set based on the selected environment

#### User-Defined Variables

- **`ENVIRONMENT`**: Must be defined by the user and is critical for correct environment selection. Valid values are `dev-native`, `dev-container`, or `production`.

### Infrastructure Scripts Integration

The following items are instructions about how to integrate Mercado Net Zero Infrastructure Scripts in the project:

- `infrastructure-scripts` project is available on GitHub at `https://github.com/Mercado-Net-Zero/infrastructure-scripts`.
- Do not mention local filesystem addresses in documentation. If necessary, mention its GitHub project location.
- Before elaborating any documentation related with `infrastructure-scripts` project integration, read its documentation available in the project README.md and the help documentation available through `ishelp -h` to understand how to use it.
- The project build and execution must be done through Mercado Net Zero (MNZ) `infrastructure-scripts`.
- Check `infrastructure-scripts` documentation at `README.md` and `ishelp` command.
- Projects built and executed with `infrastructure-scripts` have three different environments:
  - **`dev-native`**: Project is executed with the native operating system. Generally does not build anything.
  - **`dev-container`**: Project is built and executed in a Docker container for development. Use `isbuild` to create the Docker image.
  - **`production`**: Project is built and executed in a Docker container for production. Use `isbuild` to create the Docker image.
### Project Build

All build types must be covered when elaborating project documentation (if applicable).

Projects can be built for different environments using the `isbuild` command from `infrastructure-scripts`:

- **`dev-native`**: Generally does not build anything. The project is executed directly with the native operating system.
- **`dev-container`**: When `isbuild` is executed with this environment selected, the output is a Docker image to execute the project in development environments.
- **`production`**: When `isbuild` is executed with this environment selected, the output is a Docker image to execute the project in production environments.

#### Build Output

When elaborating project documentation, be sure to write what is the output of the build:

- How docker image is named and tagged.
- Pay special attention to frontend projects, where the tag is elaborated informing for which environment the Docker image was created.

#### Build Environment Selection

Check `infrastructure-scripts` documentation to understand how build environment is selected and present it in the project documentation.

**Important:** Although build commands are based in Docker and Docker Compose, do not mention such programs as an alternative to build the projects. The only way to build them must be through `infrastructure-scripts` commands.

#### Build Prerequisites

Before building the project, it is necessary to create a `docker/.env.compose` file based on `docker/.env.compose.template` file and fill all environment variables defined on it before executing.

**For frontend projects**, it is also necessary to fill `.env` and `.env.<environment>` files:

- If the project has a `.env.template`, then it is necessary to create a copy named `.env` and fill all the environment variable values for it.
- If the project has a `.env.environment.template`, then it is necessary to create a copy named `.env.<environment>`, where `<environment>` is the desired environment for which the project will be built: `dev-container` or `production` (`dev-native` does not generate a build).

### Project Execution

All execution types must be covered when elaborating project documentation (if applicable).

Projects can be executed in different environments:

- **`dev-native`**: Generally does not have a `iscomp`-script related command. Instead, it uses a project-specific command to execute it locally. For example:
  - **Python-based projects**: Are executed by first activating a virtual environment (usually created at the project directory itself) and then executing the project with either `python src/main.py` or `python -m src.main`.
  - **NPM-based projects**: Are executed by a command `npm run dev`.
  - It is necessary to check the project and understand which command is executed to run the project locally.

- **`dev-container` and `production`**: Are executed through `iscomp` informing the Docker Compose arguments related with the project:
  - It is not necessary to inform the Docker Compose file location. By default, its location is `docker/compose.yml`.
  - All other arguments must be informed. Examples:
    - `iscomp up` - Will create the Docker image (if not available yet) and spin up a container for the environment defined, similar to what `docker compose -f docker/compose.yml` would do.
    - `iscomp up -d` - Will create the Docker image (if not available yet) and spin up a container for the environment defined in the background, similar to what `docker compose -f docker/compose.yml up -d` would do.
    - `iscomp logs -f` - Will display the docker container logs and follow it, just like what `docker compose -f docker/compose.yml logs -f` would do.

#### Execution Environment Selection

Check `infrastructure-scripts` documentation to understand how execution environment is selected and present it in the project documentation.

**Important:** Although execution commands are based in Docker and Docker Compose, do not mention such programs as an alternative to execute the projects. The only way to execute them must be through `infrastructure-scripts` commands.

#### Execution Prerequisites

Before executing the project, it is necessary to fill `.env` and `.env.<environment>` files:

- If the project has a `.env.template`, then it is necessary to create a copy named `.env` and fill all the environment variable values for it.
- If the project has a `.env.environment.template`, then it is necessary to create a copy named `.env.<environment>`, where `<environment>` is the desired environment for which the project will be executed: `dev-native`, `dev-container` or `production`.

---

## Code Writing and Style

The following items are general instructions for code writing and style to be followed when working on any project.

### General Principles

- Do not write comments on the code.

### Naming Conventions

- Always prefer complete names instead of abbreviations.
  - For example:
    - "configuration" instead of "config"
    - "authentication" instead of "auth"
    - "exception" instead of "e"
    - "database" instead of "db"

### Logging

- Use log events to provide information of what is happening in the project.

---

## Project Contribution

Contributions for MNZ projects can be done in two different ways: **Manual** and **GitHub Copilot-based**.

### Manual Contributions

Manual contributions are straightforward:

1. A new working branch is created.
2. Modifications are implemented.
3. A pull request is opened.
4. Once reviewed and approved by the team, the pull request is merged.

### GitHub Copilot Contributions

GitHub Copilot contributions are GitHub Copilot-based workflows designed to streamline development.

#### Prerequisites

- **GitHub Copilot** or **VSCode with GitHub Copilot extension** is necessary for this strategy.
- **MNZ Copilot prompts** must be installed:
  - Prompts are available at `https://github.com/Mercado-Net-Zero/documents` under the `prompts` directory.
  - They can be installed through the `install-github-copilot-prompts.sh` script.

#### Instructions

1. The elaboration must be done under a clean copy of the project main branch. All changes must be either committed, stashed, or discarded.

2. Elaborate a technical specification (Markdown format) under the `documentation/tech-specs` directory:
   - The document name must follow the format `tech-spec-<index>.md`, where `<index>` is the document index. For example: `tech-spec-001.md`.
   - If additional files are necessary for the technical specification, all of them must be under a directory following the naming convention `tech-spec-<index>`, where `<index>` is the document index. For example: `tech-spec-002`.
   - Underneath this directory must be all the files necessary for the technical specification, including the technical specification itself.

3. Once all technical specification files are elaborated, commit the changes.

4. Use the `/mnz-implement-tech-spec` GitHub Copilot prompt to request Copilot to implement the technical specification.

5. Once Copilot completes its execution, review the generated output to check if it makes sense, modifying if necessary.

6. Once all the changes are done, push the branch and open a pull request describing it.

7. Once reviewed and approved by the team, the pull request is merged.

---

## Docker and Containerization

The following items are general instructions to be followed when working on any project.

### Docker Directory Structure

Projects must have a `docker` directory with:

- A `Dockerfile` used to deploy the project.
- A Docker compose `compose.yml` file.
- All environment variables necessary by the `compose.yml` must be defined at `.env.compose` file.
- If shell commands are necessary at `Dockerfile`, elaborate shell scripts and store them at `scripts` directory.

### Dockerfile Best Practices

The `Dockerfile`:

- Must not contain comments explaining each step.
- Must use arguments to configure the image build.
- Must be elaborated taking into consideration build speed and minimal size for the final image.
- Dependency installations must use caching feature to optimize speed.
- Use small base images (preferably Alpine-based).

### Docker Compose Configuration

The Docker Compose file must define resource reservations and limits for the container. Default values are:

```yaml
deploy:
  resources:
    limits:
      cpus: 0.25
      memory: 64M
    reservations:
      cpus: 0.125
      memory: 32M
```

---

## Backend Projects

The following items are instructions to be followed when working on backend projects.

### Technology Stack

- Must use **Python 3.13.5 or later**.

### Environment Setup

- Must contain a virtual environment available at `.venv` directory.
- The project main entry must be at `src/main.py`.
- The project must be created as a module, so it can be executed through `python -m src.main`. Do not modify system paths for it. Instead, resolve modules with relative paths (if necessary).

### Type Checking

- Must use `pyright` for type check.
- Pyright mode must be standard.

### VSCode Configuration

#### Settings (`.vscode/settings.json`)

The following JSON is the minimal structure for Visual Studio Code project settings:

```json
{
    "[python]": {
        "editor.rulers": [90],
        "editor.defaultFormatter": "ms-python.autopep8",
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.organizeImports": "explicit",
            "source.fixAll": "always",
            "source.fixAll.ruff": "always"
        }
    },
    "isort.args":["--profile", "black"],
    "files.exclude": {
        "**/__pycache__": true
    },
    "terminal.integrated.scrollback": 50000,
    "files.associations": {
        ".env*": "properties"
    }
}
```

#### Extension Recommendations (`.vscode/extensions.json`)

The following JSON is the minimal structure for Visual Studio Code extension recommendations:

```json
{
    "recommendations": [
        "ms-python.autopep8",
        "github.copilot-chat",
        "ms-python.vscode-pylance",
        "ms-python.python",
        "ms-python.debugpy",
        "sonarsource.sonarlint-vscode",
        "naumovs.color-highlight",
        "ms-python.isort",
        "charliermarsh.ruff"
    ]
}
```

#### Launch Configuration (`.vscode/launch.json`)

The following JSON is the minimal structure for Visual Studio Code launch file:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug \"main.py\"",
            "type": "debugpy",
            "request": "launch",
            "program": "${workspaceFolder}/src/main.py",
            "console": "integratedTerminal",
            "justMyCode": false
        },
        {
            "name": "Debug \"main.py\" (justMyCode)",
            "type": "debugpy",
            "request": "launch",
            "program": "${workspaceFolder}/src/main.py",
            "console": "integratedTerminal",
            "justMyCode": true
        },
        {
            "name": "Remote Debug \"main.py\" (Docker)",
            "type": "debugpy",
            "request": "attach",
            "connect": {
                "host": "localhost",
                "port": "<project-remote-debug-port>"
            },
            "pathMappings": [
                {
                    "localRoot": "${workspaceFolder}",
                    "remoteRoot": "/opt/mercado-net-zero/<project-name>"
                }
            ],
            "justMyCode": false
        }
    ]
}
```

Where:
- `<project-remote-debug-port>` must be the remote debug TCP port defined for the project.
- `<project-name>` must be replaced with the actual project name.

#### Tasks Configuration (`.vscode/tasks.json`)

The following JSON is the minimal structure for Visual Studio Code tasks file:

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Run \"main.py\"",
            "type": "shell",
            "command": "python",
            "args": [
                "${workspaceFolder}/src/main.py"
            ],
            "group": {
                "kind": "build",
                "isDefault": true
            },
            "problemMatcher": [],
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared",
                "showReuseMessage": true,
                "clear": false
            }
        }
    ]
}
```

### REST API

- All HTTP endpoints must have OpenAPI documentation.
- Once an HTTP endpoint has been created, its OpenAPI documentation must be created.
- Once an HTTP endpoint has been updated, its documentation must be updated as well.

#### HTTP Response Bodies

The HTTP response body for `400 - Bad Request` must follow the structure below:

```json
{
    "details": {
        "code": "<errorCode>",
        "message": "<defaultMessage>",
        "properties": {
            "<property1>": "<value1>",
            "<property2>": "<value2>"
        }
    }
}
```

Where:
- `<errorCode>`: A code to identify the error. For example: `"maximumFilesReached"`, `"maximumStorageSizeReached"`.
- `<defaultMessage>`: A human-readable message to be displayed when the interface does not know how to handle the error.
- `properties`: A JSON object containing additional properties that might help the interface elaborate its own message. For example:

  ```json
  {
      "maximumFiles": 3
  }
  ```

  or

  ```json
  {
      "maximumStorageSize": 12582912
  }
  ```

### Docker Configuration for Backend

#### Dockerfile

- The Dockerfile must use two stages: one to build the project and another to be deployed, generating the final image.
- The build stage must use `uv` to install its dependencies. The local environment execution can use `pip` to manage its dependencies.
- The Python project dependencies must be defined at `requirements.txt` file.

#### Docker Compose (`docker/compose.yml`)

The project Docker Compose file `docker/compose.yml` must be based on the following template:

```yaml
name: mnz
services:
  <project-name>: # Must be replaced by the actual project name.
    user: "${HOST_UID:-0}:${HOST_GID:-0}"
    build:
      context: ../.
      dockerfile: ./docker/Dockerfile
      # If no args are necessary to build the image, then this section can be skipped.
      args:
          # All arguments must be filled by an environment variable with the same name as the argument itself, using "undefined" as default value is not set.

    # If no volumes are necessary to create the container, then this section can be skipped.
    volumes:
    # All volumes must be defined using environment variables.
    env_file:
      - path: ../.env
          required: false
      - path: ../.env.${ENVIRONMENT}
          required: false
    environment:
      - ENVIRONMENT=${ENVIRONMENT}
    image: mnz-<project-name>:${IMAGE_TAG} # Where <project-name> must be replaced with the actual project name.
```

### Tests

- For Python projects, `pytest` library must be used to elaborate tests.
- `pytest-cov` library must be included to generate coverage report.
- Coverage must be reported at the end of `pytest` execution.
- Test reports and files must be added to `.gitignore` and `.dockerignore` files.
- Monkeypatch must be used for patches.
- Apply test writing best practices when elaborating tests.
- Production code writing rules are also applied for test code writing.

### Debugging

Backend projects must support remote debugging via TCP. The following rules apply:

- A dedicated TCP port must be defined to allow the project to be debugged remotely.
- The project must use a `MNZ_<project-code>_REMOTE_DEBUG` environment variable to enable remote debugging:
  - When the value is `true` (case-insensitive), remote debug must be enabled.
  - Any other value or the absence of the variable must deactivate remote debugging.
- The project must use a `MNZ_<project-code>_WAIT_DEBUGGER` environment variable to control whether execution waits for the debugger to attach before initializing:
  - When the value is `true` (case-insensitive), the project must wait for the remote debugger to attach before starting.
  - Any other value or the absence of the variable must start the project without waiting.

---

## Frontend Projects

The following items are instructions to be followed when working on frontend projects.

### Technology Stack

Frontend projects use:

- **Node 22 or later**
- **NPM** to manage its packages
- **React Framework 19 or later**
- **TypeScript 5.8 or later**
- **Tailwind CSS 3.4 or later**
- **Vite 6.3 or later**
- **ESLint 9.29 or later**

### Code Writing

- Elaborate types to define JSX methods arguments.

- Use (and make the most of) the following libraries when writing code:
  - React Redux
  - React DOM
  - React Markdown
  - React Redux
  - React Router DOM
  - reduxjs

#### CSS Styling Best Practices

When applying CSS styles on a component, if it has more than two properties, group them in a React `CSSProperties` object and use it at the component. For example:

```typescript
const style: CSSProperties = {
  minWidth: "16rem",
  maxWidth: "16rem",
  width: "16rem",
  flexBasis: "16rem",
  flexShrink: 0,
  flexGrow: 0,
};

export const Drawer = () => {
  return (
    <div style={style}>
      // Component content.
    </div>
  );
};
```

When applying CSS class names on a component (e.g., Tailwind classes), if it has more than two properties:

- Group them in an array, then elaborate a single string joining them with a blank space (` `).
- If additional class names must be added according to a logic, elaborate a new constant based on the original class name constant and apply the logic to either include the class names or not.
- For example:

```typescript
// Base class names to be added on the component
const baseClassName = [
  "flex",
  "flex-col",
  "h-full",
  "border-r",
  "ease-in-out",
  "md:block",
].join(" ");

export const Drawer = () => {

  // Additional class names to be added conditionally.
  const className = `${baseClassName} ${
      isOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"
    }`;

  return (
    <div className={className}>
      // Component content.
    </div>
  );
};
```

### VSCode Configuration

#### Extension Recommendations (`.vscode/extensions.json`)

The following VSCode extension recommendations must be used as base for frontend projects:

```json
{
  "recommendations": [
    "esbenp.prettier-vscode",
    "dbaeumer.vscode-eslint",
    "bradlc.vscode-tailwindcss",
    "foxundermoon.shell-format"
  ]
}
```

#### Settings (`.vscode/settings.json`)

The following VSCode settings must be used as base for frontend projects:

```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "[json]": {
    "editor.defaultFormatter": "vscode.json-language-features",
    "editor.formatOnSave": true
  },
  "[jsonc]": {
    "editor.defaultFormatter": "vscode.json-language-features",
    "editor.formatOnSave": true
  },
  "files.associations": {
    "*.css": "tailwindcss",
    ".env*": "properties"
  },
  "[javascript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode",
    "editor.formatOnSave": true
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode",
    "editor.formatOnSave": true
  },
  "[javascriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode",
    "editor.formatOnSave": true
  },
  "[typescriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode",
    "editor.formatOnSave": true
  },
  "[shellscript]": {
    "editor.formatOnSave": true
  },
  "[dockerfile]": {
    "editor.defaultFormatter": "ms-azuretools.vscode-containers",
    "editor.formatOnSave": true
  },
  "eslint.validate": [
    "javascript",
    "typescript",
    "typescriptreact",
    "javascriptreact"
  ],
  "editor.codeActionsOnSave": {
    "source.fixAll": "always",
    "source.fixAll.eslint": "always"
  },
  "editor.tabSize": 2,
  "editor.insertSpaces": true
}
```

#### Tasks Configuration (`.vscode/tasks.json`)

The following VSCode tasks must be used as base for frontend projects:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "type": "shell",
      "label": "Run Vite Dev Server",
      "command": "npx",
      "args": ["vite", "dev"],
      "group": {
        "kind": "build",
        "isDefault": true
      },
      "presentation": {
        "reveal": "always",
        "panel": "shared",
        "clear": true,
        "echo": true,
        "focus": false
      },
      "isBackground": true,
      "problemMatcher": []
    }
  ]
}
```

### Configuration Files

#### ESLint Configuration (`eslint.config.mjs`)

ESLint configuration must be stored in a modular JavaScript file (`.mjs`) and its content must be based on the following code block:

```javascript
// @ts-check

import tseslint from "typescript-eslint";

export default tseslint.config(tseslint.configs.strict);
```

#### PostCSS Configuration (`postcss.config.js`)

PostCSS configuration file must be stored as a Javascript file (`.js`) and its content must be based on the following code block:

```javascript
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
```

#### TypeScript Configuration (`tsconfig.json`)

TypeScript configuration must be stored as a JSON file (`.json`) and its content must be based on the following code block:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["DOM", "DOM.Iterable", "ES2020"],
    "module": "es2022",
    "moduleResolution": "bundler",
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "skipLibCheck": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "react-jsx",
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@hooks": ["src/hooks"],
      "@hooks/*": ["src/hooks/*"],
      "@types": ["src/types"],
      "@types/*": ["src/types/*"],
      "@providers": ["src/providers"],
      "@providers/*": ["src/providers/*"],
      "@utils": ["src/utils"],
      "@utils/*": ["src/utils/*"]
    }
  },
  "include": ["src"],
  "exclude": ["node_modules", "dist"]
}
```

#### Vite Configuration (`vite.config.mjs`)

Vite configuration file must be stored in a modular JavaScript file (`.mjs`) and its content must be based on the following code block:

```javascript
import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import tsconfigPaths from "vite-tsconfig-paths";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  return {
    plugins: [react(), tsconfigPaths()],
    server: {
      port: 5173,
      open: true,
    },
    base: env.VITE_<project-code>_BASE_PATH,
  };
});
```

Where `<project-code>` is the project code.

### Docker Configuration for Frontend

The project Docker Compose file `docker/compose.yml` must be based on the following template:

```yaml
name: mnz
services:
  <project-name>: # Must be replaced by the project name.
    build:
      context: ../.
      dockerfile: ./docker/Dockerfile
      # If no args are necessary to build the image, then this section can be skipped.
      args:
        # All arguments must be filled by an environment variable with the same name as the argument itself, using "undefined" as default value is not set.
    ports:
      - "${MNZ_<project-code>_SERVER_PORT}:$NETINHO_<project-code>_SERVER_PORT" # Replace <project-code> by the project code.
    image: mnz-<project-name>:$IMAGE_TAG # Replace <project-name> by the project name.
    restart: unless-stopped
```

### Tests

- For TypeScript/React projects:
  - `vitest` must be used for unit tests elaboration.
  - `playwright` must be used for integration tests.
- Test reports and files must be added to `.gitignore` and `.dockerignore` files.
- Apply test writing best practices when elaborating tests.
- Production code writing rules are also applied for test code writing.

### Version Control

The project `.gitignore` must be based on the following code block:

```gitignore
# Logs
logs
*.log
npm-debug.log*

node_modules
dist
dist-ssr
*.local

# Editor directories and files
.vscode/*
!.vscode/settings.json
!.vscode/extensions.json

# Ignore all .env files except the templates
.env*
!.env*.template
```

---

## Claude Code

The following items are instructions for tasks done through Claude Code only.

### Settings

The Claude Code settings must be defined at `.claude/settings.json` with the following configuration:

```json
{
  "plansDirectory": "./.claude/plans"
}
```

### Plan Execution Rules

Rules to follow after a plan has been created and its implementation accepted:

1. **Pre-execution Git check**: Before any change, check the changes done at the Git project.
   - Claude Code must proceed with the plan execution only if the changes detected by Git are at `.claude` and `.vscode` directories (and their subdirectories).
   - As a special rule, there might be cases where changes at `documents/tech-specs/tech-spec-<index>` directory might be found. Contents at this directory are considered additional resources for the plan elaboration so, as long as these files are referenced in the plan, they are acceptable to not be committed yet. If files under this directory exist but are not mentioned in the plan, the execution must be interrupted and a message reporting it must be presented to the user.
   - Any other change outside of these directories and files must cancel the task execution.
   - If the task has been cancelled by this rule, Claude Code must report it to the user.

2. **Technical specification copy**: A copy of the plan must be created at `documents/tech-specs` directory with the name `tech-spec-<index>.md`, where `<index>` is the next technical specification index available.
   - For example: If the latest technical specification was `tech-spec-008.md`, then the file created must be named `tech-spec-009.md`.
   - Before creating the copy, Claude Code must check if there is not a technical specification file which already covers the changes at the plan. If so, there is no need to create a new technical specification, but Claude Code must report this to the user and inform which technical specification will be implemented.

3. **Branch check**: Claude Code must verify that the current branch is `main`.
   - If the current branch is not `main`, then the task execution must be interrupted. Claude Code must report it to the user.

4. **Commit the technical specification**: After creating the technical specification, all changes inside the Git project must be committed with the following commit message template:

   ```
   [Claude Code] Created technical specification <index>
   ```

   Replacing `<index>` with the technical specification index used for the new file. Optionally, any other useful information about this commit may be added on subsequent lines.

5. **Create a new branch**: After committing all pending changes, a new branch must be created named `tech-spec-<index>`.

6. **Clear session memory**: Claude Code session memory must be cleared at this point.

7. **Proceed with implementation**: Claude Code can proceed with the plan implementation following the instructions defined in this constitution (`documents/CONSTITUTION.md`).

8. **Review and commit**: Once the plan execution is complete, **do not commit changes** (this will allow the user to review the changes done). Instead, provide a command to commit the changes with the commit message prefixed with `[Claude Code]`. For example:

   ```
   [Claude Code] Implemented users deletion

   - Added `DELETE /user/{id}` REST endpoint
   - Applied business rule to cascade delete all remaining users information
   - Added a message at audit table informing about the user deletion
   ```

---

*Last updated: March 11, 2026*
