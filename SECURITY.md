# Security Policy

## Supported Versions

Use this section to tell people about which versions of your project are
currently being supported with security updates.

| Version | Supported          |
| ------- | ------------------ |
| 5.1.x   | :white_check_mark: |
| 5.0.x   | :x:                |
| 4.0.x   | :white_check_mark: |
| < 4.0   | :x:                |

## Reporting a Vulnerability

Use this section to tell people how to report a vulnerability.

Tell them where to go, how often they can expect to get an update on a
reported vulnerability, what to expect if the vulnerability is accepted or
declined, etc.
Here’s a GitHub-ready **`SECURITY.md`** policy for **Onoma AI Genesis**.

# Security Policy

## Onoma AI Genesis

Onoma AI takes security, privacy, responsible disclosure, and defensive engineering seriously.

This policy explains how to report suspected security vulnerabilities affecting the Onoma AI Genesis codebase, services, APIs, agents, plugins, infrastructure, or related components.

---

## Supported Versions

Security updates are provided for actively maintained releases.

| Version                           | Supported |
| --------------------------------- | --------- |
| Genesis 1.x                       | Yes       |
| Pre-Genesis development builds    | Limited   |
| Unmaintained or archived versions | No        |

Users are encouraged to run the most recent supported release.

---

## Reporting a Vulnerability

Do not publicly disclose a suspected vulnerability before the maintainers have had a reasonable opportunity to investigate and remediate it.

Security reports should include as much of the following information as possible:

* A clear description of the vulnerability
* The affected component, service, endpoint, or file
* The affected version or commit
* Steps required to reproduce the issue
* Expected behavior
* Actual behavior
* Potential security impact
* Proof-of-concept details, when appropriate
* Relevant logs, screenshots, or error messages
* Suggested remediation, if known

Do not include real credentials, API keys, passwords, access tokens, private user data, or unrelated confidential information in a vulnerability report.

---

## Security Issue Categories

Examples of issues that should be reported privately include:

* Authentication bypass
* Authorization or permission failures
* Privilege escalation
* Cross-tenant data exposure
* Sensitive information disclosure
* Remote code execution
* Command injection
* SQL injection
* Server-side request forgery
* Cross-site scripting
* Cross-site request forgery
* Path traversal
* Unsafe file handling
* Arbitrary file access
* Insecure deserialization
* Secret or credential exposure
* Encryption failures
* Sandbox escape
* Agent permission bypass
* Prompt-to-tool authorization bypass
* Plugin isolation failures
* Model or connector credential leakage
* Memory isolation failures
* Knowledge-base access-control failures
* API authentication weaknesses
* Dependency vulnerabilities with meaningful exploitability
* Supply-chain compromise
* Insecure deployment configuration

---

## AI-Specific Security

Onoma AI includes AI models, agents, retrieval systems, memory, tools, plugins, workflows, and external integrations.

Security reports involving AI behavior should focus on violations of actual security boundaries.

Examples include:

* An agent accessing data outside its permissions
* A model triggering tools without required authorization
* Retrieval exposing another user's private information
* Prompt injection bypassing tool or connector security
* Memory data leaking between unrelated users or projects
* A plugin gaining permissions not declared in its manifest
* An AI workflow executing commands outside its approved sandbox
* Secrets being inserted into model context without authorization
* Untrusted content causing privileged actions

A model producing an incorrect answer by itself is generally a quality issue rather than a security vulnerability unless the behavior results in a security boundary failure.

---

## Security Architecture Principles

Onoma AI is designed around the following principles:

### Least Privilege

Agents, services, users, plugins, and integrations should receive only the permissions necessary to perform their assigned functions.

### Explicit Authorization

Sensitive operations should require appropriate authentication and authorization before execution.

### Isolation

User data, project data, agents, plugins, models, and execution environments should remain isolated according to their security boundaries.

### Defense in Depth

Security controls should exist across application, API, infrastructure, model, data, network, and execution layers.

### Secure Defaults

Security-sensitive features should default to restrictive configurations.

### Auditability

Important security events and privileged actions should be traceable through appropriate audit logging.

### Data Minimization

Only data necessary for a requested task should be collected, processed, retained, or exposed.

### Human Control

High-impact actions should support explicit user approval or administrative controls where appropriate.

---

## Authentication

Onoma AI deployments should use secure authentication mechanisms.

Recommended controls include:

* Multi-factor authentication
* Secure session management
* Strong password policies where passwords are used
* Short-lived access tokens
* Token rotation
* Secure OAuth or OpenID Connect integrations
* Protection against brute-force attacks
* Revocation mechanisms

Credentials must never be committed directly to source control.

---

## Authorization

Authorization should be enforced server-side.

Supported authorization models may include:

* Role-Based Access Control
* Attribute-Based Access Control
* Project-level permissions
* Workspace permissions
* Agent permissions
* Plugin permissions
* Tool permissions
* Administrative policies

Frontend visibility must never be treated as an authorization mechanism.

---

## Secrets Management

Sensitive credentials should be stored using approved secret-management systems.

Examples include:

* Environment variables
* Managed cloud secret stores
* Encrypted secret vaults
* Hardware-backed key storage where appropriate

Secrets must not be stored in:

* Source code
* Public GitHub repositories
* Client-side JavaScript
* Documentation examples containing real credentials
* Logs
* Model prompts unless explicitly required and securely handled

---

## Encryption

Sensitive data should be protected both in transit and at rest.

Recommended standards include:

* TLS for network communications
* Modern authenticated encryption for sensitive stored data
* Secure key rotation
* Separation of encryption keys from encrypted data

Custom cryptographic algorithms should not be created when established, reviewed standards are available.

---

## Agent and Tool Security

Every Onoma agent should have a defined security profile.

Example:

```yaml
agent:
  name: ResearchAgent

  permissions:
    read:
      - approved_documents
      - public_search

    write:
      - research_reports

    denied:
      - system_configuration
      - unrestricted_shell
      - unrelated_private_projects
```

Tool access should be validated before every privileged action.

Agents should not inherit unlimited permissions simply because the user can access a broader environment.

---

## Plugin Security

Plugins must declare their required capabilities and permissions.

Plugin manifests should identify:

* Required APIs
* Data-access requirements
* Network access
* File-system access
* External services
* Authentication requirements
* Execution privileges

Plugins should be sandboxed where practical.

A plugin should not be able to silently escalate its own permissions.

---

## Model Provider Security

External AI providers should be accessed through controlled provider adapters.

Provider credentials should be isolated from end users and untrusted prompts.

The Model Router must not expose:

* API keys
* Internal provider credentials
* Hidden authentication headers
* Administrative configuration
* Sensitive provider metadata

---

## Retrieval and Search Security

Onoma Search Engine must respect source-level access controls.

A search result being technically discoverable does not automatically mean the requesting user is authorized to retrieve it.

Retrieval should enforce:

```text
User Identity
      ↓
Source Permission Check
      ↓
Search
      ↓
Document Permission Check
      ↓
Evidence Retrieval
      ↓
Response
```

---

## Memory Security

Onoma Memory Engine must preserve separation between:

* Users
* Organizations
* Workspaces
* Projects
* Agents
* Sessions

Memory should not cross these boundaries unless explicitly authorized.

Sensitive memory should support deletion and retention controls.

---

## Execution Sandboxing

Untrusted code and AI-generated code should execute in restricted environments whenever feasible.

Sandbox controls may include:

* CPU limits
* Memory limits
* Execution time limits
* Restricted networking
* Restricted file-system access
* Read-only system directories
* Process isolation
* Container isolation

Generated code should not automatically receive privileged operating-system access.

---

## Logging

Security-relevant events should be logged appropriately.

Examples include:

* Successful and failed authentication
* Permission changes
* Administrative actions
* Agent tool executions
* Plugin installation
* Secret-management events
* Security configuration changes
* Data exports
* Destructive operations

Logs should avoid recording passwords, authentication tokens, private keys, or unnecessary sensitive user content.

---

## Dependency Security

Dependencies should be:

* Version controlled
* Regularly updated
* Scanned for known vulnerabilities
* Obtained from trusted package sources
* Reviewed before major upgrades

Where practical, dependency lock files and reproducible builds should be used.

---

## Supply-Chain Security

The project should progressively support:

* Signed releases
* Protected branches
* Mandatory code review
* CI security checks
* Dependency scanning
* Secret scanning
* Software bills of materials
* Reproducible build processes
* Artifact integrity verification

---

## Secure Development Lifecycle

Security should be included throughout development.

```text
Requirements
    ↓
Threat Modeling
    ↓
Architecture Review
    ↓
Implementation
    ↓
Static Analysis
    ↓
Testing
    ↓
Security Review
    ↓
Deployment
    ↓
Monitoring
```

---

## Responsible Security Testing

Good-faith security research is welcome when performed responsibly.

Researchers must:

* Avoid accessing data belonging to other users
* Avoid modifying or deleting data
* Avoid degrading service availability
* Avoid denial-of-service testing
* Avoid social engineering
* Avoid physical security testing
* Avoid credential theft
* Avoid persistence on systems
* Stop testing if sensitive information is encountered
* Report discovered vulnerabilities privately

Only test systems for which you have authorization.

---

## Out of Scope

The following generally do not qualify as security vulnerabilities by themselves:

* Missing non-security-related headers with no demonstrated impact
* Best-practice recommendations without exploitable impact
* Self-XSS
* Clickjacking on pages containing no sensitive action
* Rate-limit observations without meaningful security consequences
* Automated scanner results without verification
* Version disclosure without a demonstrated exploit
* AI hallucinations that do not violate a security boundary
* Prompt outputs that are undesirable but do not result in unauthorized access or execution
* Vulnerabilities requiring unsupported or substantially modified deployments

---

## Coordinated Disclosure

Please allow maintainers reasonable time to:

1. Reproduce the vulnerability
2. Assess severity
3. Develop a fix
4. Test the remediation
5. Prepare affected releases
6. Notify users when appropriate

Public disclosure should preferably occur after a fix or mitigation is available.

---

## Severity Assessment

Onoma AI may consider factors including:

* Exploitability
* Required privileges
* User interaction
* Data sensitivity
* Scope of affected users
* Confidentiality impact
* Integrity impact
* Availability impact
* AI agent or tool escalation
* Infrastructure compromise

Established frameworks such as CVSS may be used when appropriate.

---

## Security Response Goals

The project aims to:

* Acknowledge credible reports promptly
* Investigate reproducible vulnerabilities
* Prioritize high-impact issues
* Develop mitigations or fixes
* Communicate security updates clearly

Response times may vary based on complexity, severity, maintainer availability, and deployment environment.

---

## Safe Harbor

Good-faith security research performed in accordance with this policy is intended to improve Onoma AI security.

Researchers should remain within authorized systems and avoid harming users, systems, services, or data.

This policy does not authorize activity prohibited by applicable law or activity against third-party infrastructure.

---

## Security Advisories

Confirmed vulnerabilities may be documented through GitHub Security Advisories or another appropriate coordinated-disclosure mechanism.

Public reports should avoid revealing exploitation details before affected users have had a reasonable opportunity to update.

---

## Security Is a Shared Responsibility

Security applies across the complete Onoma AI platform:

```text
ONOMA AI SECURITY

├── Identity
├── Authentication
├── Authorization
├── Search
├── Memory
├── Knowledge Graph
├── Agents
├── Models
├── Plugins
├── APIs
├── Automation
├── Infrastructure
├── Data
├── Workspaces
└── Developer Platform
```

The goal is to ensure that intelligence remains useful without bypassing security, privacy, authorization, or user control.

---

## Final Security Principle

> **Security before convenience. Least privilege before unrestricted access. Evidence before trust. User authorization before execution.**

**Project:** Onoma AI Genesis
**Document:** `SECURITY.md`
**Version:** 1.0

You can save this directly as **`SECURITY.md`** in the root of the `onoma-ai-genesis` GitHub repository.
