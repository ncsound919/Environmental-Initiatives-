To scale these 13 projects efficiently, you need a standardized "Definition of Done" for every stage of development. This prevents feature creep and ensures every line of code written by an LLM fits into your specific Monorepo architecture.

Here is the **Universal Readiness Checklist**, the **LLM Context Block** (to paste into your AI coding tool), and the **Strict Coding Rules** to prevent errors.

---

### Part 1: The "ECOS" Readiness Checklist (Steps to Readiness)

Every project (from #1 Foam Homes to #13 Micro-Hydro) must pass these 5 gates. Do not move to the next step until the boxes are checked.

#### **Level 1: The "Digital Brain" (Software Logic)**
*Focus: Can we simulate the result before building hardware?*
*   [ ] **Input Defined:** specific data types defined in Prisma Schema (e.g., `soil_moisture: float`, `reactor_temp: float`) (see Prisma schema and data-typing standards).
*   [ ] **Logic Isolated:** The core optimization (Python) is written as a standalone function in `packages/ecosystem-brains/` (see "ecosystem-brains" package structure guidelines).
*   [ ] **Unit Test Passed:** The logic returns a valid prediction/decision on mock data (e.g., "If humidity is 80%, turn on AWG").
*   [ ] **API Exposed:** The logic is wrapped in a FastAPI/NestJS endpoint (see API service standards).

#### **Level 2: The "Digital Body" (Interface & Connectivity)**
*Focus: Can a user or device talk to the Brain?*
*   [ ] **IoT Pipeline:** MQTT topic established (`ecos/{project_id}/telemetry`) (see IoT/MQTT topic conventions).
*   [ ] **Shared Auth:** The app uses the universal `@ecosystem/auth-module` (no custom login forms) (see auth-module integration guide).
*   [ ] **UI Component:** Dashboard uses shared `@ecosystem/ui-components` (Chart, Map, Gauge) (see shared UI component library standards).
*   [ ] **Billing Hook:** The service is connected to the Shared Billing Engine (Stripe/Token) (see shared billing integration guide).

#### **Level 3: The "Physical Twin" (Prototype)**
*Focus: Does the code work on hardware?*
*   [ ] **Firmware Flash:** Code successfully flashes to the target MCU (ESP32/STM32) via the shared OTA pipeline (see OTA firmware deployment pipeline).
*   [ ] **Telemetry Flow:** Real sensor data appears in the shared PostgreSQL database (see telemetry ingestion and storage standards).
*   [ ] **Control Loop:** A command sent from the UI triggers a physical relay/action within 200ms.

#### **Level 4: The "RegenCity" Integration (Field Test)**
*Focus: Does it work in the 20-acre ecosystem?*
*   [ ] **Zone Deployment:** Hardware installed in its designated zone (e.g., Bulb in Zone A, Reactor Sim in Zone D) (see RegenCity zone layout and deployment plan).
*   [ ] **Synergy Check:** The system consumes inputs from another project (e.g., AWG uses Solar forecasts) (see inter-project data dependency map).
*   [ ] **Data Lake Verify:** Data is accessible to the "RegenCity Digital Twin" for global optimization.

#### **Level 5: Scale & Monetization**
*   [ ] **SaaS Tiering:** Feature flags enabled for "Free," "Pro," and "Enterprise" tiers.
*   [ ] **Regulatory Log:** Immutable audit trails enabled (required for Nuclear/Bio) (see regulatory compliance logging standards).
*   [ ] **Documentation:** API docs generated automatically via Swagger/OpenAPI.

---

### Part 2: Context for LLM Coding (The "System Prompt")

When using an LLM (Cursor, Copilot, ChatGPT) to write code for this project, paste the following **Context Block** at the start of the session. This ensures the AI understands your Monorepo structure and doesn't hallucinate non-existent folders.

```markdown
# SYSTEM CONTEXT: ECOS MONOREPO
You are a Senior Full-Stack Engineer working on the "ECOS" Monorepo.
We are building 13 interconnected climate-tech startups sharing a single infrastructure.

## ARCHITECTURE
- **Monorepo Manager:** Turborepo / Nx
- **Backend:** Node.js (NestJS) for APIs, Python (FastAPI) for ML/Optimization.
- **Frontend:** Next.js (React) with Tailwind CSS.
- **Database:** PostgreSQL (Prisma ORM) + TimescaleDB (Time-series).
- **IoT:** MQTT for telemetry, ESP32/C++ for firmware.

## DIRECTORY STRUCTURE
/apps
  /foam-homes          # Project 1 (Next.js + NestJS)
  /symbiosis-fungi     # Project 2
  /closed-loop-farm    # Project 3
  ... (up to /micro-hydro #13)
  /api-gateway         # Main entry point

/packages
  /core
    /auth-module       # Shared Auth0/Web3 login
    /database-schema   # Shared Prisma schema (Single Source of Truth)
    /billing-engine    # Stripe + Token logic
  /ui-components       # Shared React components (Chart, Map, Button)
  /hardware-sdk        # Shared MQTT/Firmware logic
  /ecosystem-brains    # SHARED PYTHON LOGIC (Do not duplicate!)
    /forecasting       # Prophet/LSTM models
    /solvers           # OR-Tools/Linear Programming

## KEY CONSTRAINTS
1. NEVER create a new database schema. Use the shared `packages/core/database-schema`.
2. NEVER write custom optimization logic inside an `app`. Put it in `packages/ecosystem-brains` and import it.
3. ALWAYS use `import { Component } from '@ecosystem/ui-components'` for UI.
4. All IoT devices must publish to topic `ecos/{project_type}/{device_id}/telemetry`.
```

---

### Part 3: Coding Rules to Avoid Hallucinations

Give these rules to the LLM to prevent syntax errors and "imaginary" imports.

#### **Rule 1: The "Single Source of Truth" Rule**
*   **Instruction:** "Do not define TypeScript interfaces for Database models manually. You MUST import them from the Prisma client."
*   **Why:** Prevents the code from drifting away from the actual database structure defined in Source [1].
*   **Correct Syntax:**
    ```typescript
    import { SensorReading } from '@ecosystem/database-schema';
    // vs
    // interface SensorReading { ... } // DO NOT DO THIS
    ```

#### **Rule 2: The "Brain/Body" Separation Rule**
*   **Instruction:** "Frontend code (React) must NEVER calculate heavy math or optimizations. It must call the API, which calls the Python Brain."
*   **Why:** Prevents the LLM from trying to run complex Python libraries like `scikit-learn` inside a web browser environment [3].
*   **Correct Flow:**
    `UI (Next.js) -> API (NestJS) -> Brain (Python Service) -> Return Result`

#### **Rule 3: The "Strict Typing" Rule**
*   **Instruction:** "All code must be strictly typed. No `any`. Zod schemas must be defined for all API inputs."
*   **Why:** Prevents "syntax hallucinations" where the LLM assumes data exists that isn't actually there.
*   **Validation:** Always call `schema.parse(input)` or `schema.safeParse(input)` at API boundaries (e.g., request handlers or validation middleware) to enforce runtime type safety. Convert validation failures into a 4xx response with a clear error message. Use `z.infer<typeof Schema>` to derive TypeScript types from your Zod schemas.
*   **Example:**
    ```typescript
    import { z } from 'zod';
    const TelemetrySchema = z.object({
      temperature: z.number(),
      humidity: z.number(),
      deviceId: z.string()
    });
    
    // In your API handler:
    try {
      const validatedData = TelemetrySchema.parse(request.body);
      // validatedData is now strongly typed
    } catch (error) {
      return response.status(400).json({ error: error.message });
    }
    ```

#### **Rule 4: The "Existing Component" Rule**
*   **Instruction:** "Before creating a UI component, check `@ecosystem/ui-components`. Do not style raw HTML `divs` if a styled component exists."
*   **Why:** Keeps the look uniform across all 13 projects and reduces CSS bloat [7].

#### **Rule 5: The "Simulated Hardware" Rule**
*   **Instruction:** "When writing Firmware code (C++), always include a `#ifdef SIMULATION` block that allows the code to run on a local machine without physical hardware."
*   **Why:** Allows you to test the logic for the **Centennial Bulb (#8)** or **Reactor (#6)** continuously without needing to flash a physical chip every time [9].
*   **Example:**
    ```cpp
    void readSensor() {
      #ifdef SIMULATION
        temperature = mockTemperature();  // Use mock data for local testing
      #else
        temperature = sensor.read();      // Read from physical hardware
      #endif
    }
    ```

### Summary of Workflow
1.  **Check Readiness:** Look at Part 1 to see which phase you are in.
2.  **Paste Context:** Put Part 2 into your IDE.
3.  **Enforce Rules:** Apply Part 3 to every code review.

This structure allows you to build **one** system that just happens to have 13 different faces, drastically reducing the complexity of the code.

---

### References

1. **Prisma Schema Documentation** - `packages/core/database-schema/schema.prisma` - Centralized database schema definitions
2. **Database Model Definitions** - Data type specifications for sensor readings and environmental metrics
3. **Ecosystem Brains Package** - `packages/ecosystem-brains/` - Shared Python optimization and ML logic
4. **API Documentation** - FastAPI/NestJS endpoint specifications in `apps/api-gateway/`
5. **MQTT Topic Structure** - IoT messaging protocol documentation for telemetry data
6. **Authentication Module** - `packages/core/auth-module/` - Shared Auth0/Web3 login implementation
7. **UI Components Library** - `packages/ui-components/` - Reusable React components (Chart, Map, Gauge, Button)
8. **Billing Engine** - `packages/core/billing-engine/` - Stripe and token-based payment integration
9. **OTA Pipeline Documentation** - Over-the-air firmware update system for ESP32/STM32 devices
10. **Database Integration** - PostgreSQL + TimescaleDB connection and data flow architecture
11. **RegenCity Zone Map** - Physical deployment zones (A: Living, B: Infrastructure, C: Agriculture, D: R&D)
12. **Project Synergy Matrix** - Inter-project dependencies and data flow connections
13. **Regulatory Compliance** - Audit trail and logging requirements for Nuclear/Bio projects
