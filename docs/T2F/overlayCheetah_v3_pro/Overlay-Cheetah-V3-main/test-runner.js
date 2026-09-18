#!/usr/bin/env node

const fs = require("fs");
const path = require("path");
const { execSync, spawn } = require("child_process");

class TestRunner {
  constructor(projectPath, projectType = "web") {
    this.projectPath = projectPath;
    this.projectType = projectType;
    this.results = {
      build: { success: false, output: "", error: "" },
      test: { success: false, output: "", error: "" },
      lint: { success: false, output: "", error: "" },
      typeCheck: { success: false, output: "", error: "" },
      overall: { success: false, score: 0 },
    };
  }

  /**
   * Run all tests
   */
  async runAll() {
    console.log(`🧪 Running automated tests for project: ${this.projectPath}`);

    try {
      // Check if package.json exists
      const packageJsonPath = path.join(this.projectPath, "package.json");
      if (!fs.existsSync(packageJsonPath)) {
        throw new Error("No package.json found in project directory");
      }

      // Install dependencies
      console.log("📦 Installing dependencies...");
      this.runCommand("npm install", { cwd: this.projectPath });

      // Run build
      await this.runBuild();

      // Run tests
      await this.runTests();

      // Run linting
      await this.runLint();

      // Run type checking
      await this.runTypeCheck();

      // Calculate overall score
      this.calculateOverallScore();

      console.log(
        `✅ Test run completed. Overall success: ${this.results.overall.success}`,
      );
      return this.results;
    } catch (error) {
      console.error(`❌ Test run failed: ${error.message}`);
      this.results.overall.success = false;
      this.results.overall.error = error.message;
      return this.results;
    }
  }

  /**
   * Run build command
   */
  async runBuild() {
    console.log("🔨 Running build...");
    try {
      const output = this.runCommand("npm run build", {
        cwd: this.projectPath,
      });
      this.results.build.success = true;
      this.results.build.output = output;
      console.log("✅ Build successful");
    } catch (error) {
      this.results.build.success = false;
      this.results.build.error = error.message;
      console.log("❌ Build failed");
    }
  }

  /**
   * Run test command
   */
  async runTests() {
    console.log("🧪 Running tests...");
    try {
      const output = this.runCommand("npm test", { cwd: this.projectPath });
      this.results.test.success = true;
      this.results.test.output = output;
      console.log("✅ Tests passed");
    } catch (error) {
      this.results.test.success = false;
      this.results.test.error = error.message;
      console.log("❌ Tests failed");
    }
  }

  /**
   * Run linting
   */
  async runLint() {
    console.log("🔍 Running linter...");
    try {
      const output = this.runCommand("npm run lint", { cwd: this.projectPath });
      this.results.lint.success = true;
      this.results.lint.output = output;
      console.log("✅ Linting passed");
    } catch (error) {
      // Linting might not be configured, so don't fail completely
      this.results.lint.success = false;
      this.results.lint.error = error.message;
      console.log("⚠️  Linting failed or not configured");
    }
  }

  /**
   * Run TypeScript type checking
   */
  async runTypeCheck() {
    console.log("🔧 Running type check...");
    try {
      const output = this.runCommand("npx tsc --noEmit", {
        cwd: this.projectPath,
      });
      this.results.typeCheck.success = true;
      this.results.typeCheck.output = output;
      console.log("✅ Type check passed");
    } catch (error) {
      this.results.typeCheck.success = false;
      this.results.typeCheck.error = error.message;
      console.log("❌ Type check failed");
    }
  }

  /**
   * Calculate overall score
   */
  calculateOverallScore() {
    const checks = [
      this.results.build,
      this.results.test,
      this.results.lint,
      this.results.typeCheck,
    ];
    const passed = checks.filter((check) => check.success).length;
    const total = checks.length;

    this.results.overall.score = Math.round((passed / total) * 100);
    this.results.overall.success = passed === total; // All must pass for overall success
  }

  /**
   * Run a command and return output
   */
  runCommand(command, options = {}) {
    try {
      const result = execSync(command, {
        encoding: "utf8",
        timeout: 300000, // 5 minutes timeout
        maxBuffer: 1024 * 1024 * 10, // 10MB buffer
        ...options,
      });
      return result;
    } catch (error) {
      // Re-throw with more context
      const errorMessage = error.stdout
        ? `${error.stdout}\n${error.stderr}`
        : error.message;
      const enhancedError = new Error(errorMessage);
      enhancedError.code = error.status;
      throw enhancedError;
    }
  }

  /**
   * Get results as JSON string
   */
  toJSON() {
    return JSON.stringify(this.results, null, 2);
  }
}

// CLI interface
if (require.main === module) {
  const args = process.argv.slice(2);
  const projectPath = args[0];
  const projectType = args[1] || "web";

  if (!projectPath) {
    console.error("Usage: node test-runner.js <project-path> [project-type]");
    console.error("Project types: web, api, mobile, desktop");
    process.exit(1);
  }

  const runner = new TestRunner(projectPath, projectType);
  runner
    .runAll()
    .then((results) => {
      console.log("\n📊 Test Results Summary:");
      console.log(`Build: ${results.build.success ? "✅" : "❌"}`);
      console.log(`Tests: ${results.test.success ? "✅" : "❌"}`);
      console.log(`Lint: ${results.lint.success ? "✅" : "❌"}`);
      console.log(`Type Check: ${results.typeCheck.success ? "✅" : "❌"}`);
      console.log(`Overall Score: ${results.overall.score}%`);

      // Output JSON for parsing by other tools
      console.log("\n📄 JSON Output:");
      console.log(runner.toJSON());

      process.exit(results.overall.success ? 0 : 1);
    })
    .catch((error) => {
      console.error("Test runner failed:", error);
      process.exit(1);
    });
}

module.exports = TestRunner;
