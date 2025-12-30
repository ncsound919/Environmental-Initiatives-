#!/usr/bin/env python3
"""
ECOS Level 1 Structure Validation
Validates that all 13 projects have the required structure for 20% readiness
"""

import os

def check_file_exists(path):
    """Check if a file exists"""
    return os.path.exists(path)

def validate_structure():
    """Validate the monorepo structure"""
    print("\n" + "=" * 60)
    print("ECOS LEVEL 1 STRUCTURE VALIDATION")
    print("=" * 60 + "\n")
    
    # Use relative path or environment variable for better portability
    base_path = os.environ.get('ECOS_BASE_PATH', os.path.dirname(os.path.abspath(__file__)))
    results = {}
    
    # ============================================
    # SHARED INFRASTRUCTURE
    # ============================================
    print("📦 Shared Infrastructure:")
    
    checks = [
        ("package.json", "Root package.json"),
        ("turbo.json", "Turborepo config"),
        ("tsconfig.json", "TypeScript config"),
        (".gitignore", "Git ignore file"),
        ("packages/core/database-schema/schema.prisma", "Prisma schema"),
        ("packages/core/database-schema/package.json", "Database schema package"),
        ("packages/core/auth-module/src/index.ts", "Auth module"),
        ("packages/core/auth-module/package.json", "Auth package"),
        ("packages/ui-components/src/index.tsx", "UI components"),
        ("packages/ui-components/package.json", "UI components package"),
        ("packages/hardware-sdk/src/index.ts", "Hardware SDK"),
        ("packages/hardware-sdk/package.json", "Hardware SDK package"),
        ("packages/ecosystem-brains/__init__.py", "Ecosystem brains module"),
        ("packages/ecosystem-brains/forecasting/__init__.py", "Forecasting module"),
        ("packages/ecosystem-brains/solvers/__init__.py", "Solvers module"),
        ("packages/ecosystem-brains/dispatcher/__init__.py", "Dispatcher module"),
        ("packages/ecosystem-brains/pyproject.toml", "Python package config"),
        ("apps/api-gateway/main.py", "FastAPI gateway"),
        ("apps/api-gateway/package.json", "API gateway package"),
    ]
    
    infrastructure_pass = 0
    for file_path, description in checks:
        full_path = os.path.join(base_path, file_path)
        exists = check_file_exists(full_path)
        status = "✅" if exists else "❌"
        print(f"  {status} {description}")
        if exists:
            infrastructure_pass += 1
    
    results['INFRASTRUCTURE'] = f"{infrastructure_pass}/{len(checks)}"
    
    # ============================================
    # DATABASE SCHEMA VALIDATION
    # ============================================
    print("\n📊 Database Schema Validation:")
    
    schema_path = os.path.join(base_path, "packages/core/database-schema/schema.prisma")
    if check_file_exists(schema_path):
        with open(schema_path, 'r') as f:
            schema_content = f.read()
        
        # Check for all 13 project models
        project_models = [
            ("FoamHome", "Project #1: Foam Homes"),
            ("SoilReading", "Project #2: Symbiosis"),
            ("FarmCycle", "Project #3: Closed-Loop Farm"),
            ("MaterialTest", "Project #4: Hemp Lab"),
            ("LightRecipe", "Project #5: Greenhouse"),
            ("ReactorSimulation", "Project #6: Fast Reactor"),
            ("BioreactorReading", "Project #7: Bioreactor"),
            ("BulbTelemetry", "Project #8: Centennial Bulb"),
            ("WaterGeneration", "Project #9: AWG"),
            ("GeothermalFlow", "Project #10: Geothermal"),
            ("SolarGeneration", "Project #12: Solar"),
            ("HydroGeneration", "Project #13: Micro-Hydro"),
        ]
        
        schema_pass = 0
        for model, description in project_models:
            exists = f"model {model}" in schema_content
            status = "✅" if exists else "❌"
            print(f"  {status} {description}")
            if exists:
                schema_pass += 1
        
        # Check for core models
        core_models = ["User", "Device", "Telemetry", "Subscription"]
        for model in core_models:
            exists = f"model {model}" in schema_content
            if exists:
                schema_pass += 1
        
        results['DATABASE_SCHEMA'] = f"{schema_pass}/{len(project_models) + len(core_models)}"
    else:
        print("  ❌ Schema file not found")
        results['DATABASE_SCHEMA'] = "0/16"
    
    # ============================================
    # PYTHON MODULES VALIDATION
    # ============================================
    print("\n🐍 Python Modules Validation:")
    
    python_modules = [
        ("packages/ecosystem-brains/forecasting/__init__.py", "Forecasting module", 
         ["forecast_stream_flow", "forecast_solar_irradiance", "forecast_humidity", "predict_bulb_failure"]),
        ("packages/ecosystem-brains/solvers/__init__.py", "Solvers module",
         ["optimize_nutrient_cycle", "optimize_awg_schedule", "optimize_geothermal_flow", "optimize_fungal_match"]),
        ("packages/ecosystem-brains/dispatcher/__init__.py", "Dispatcher module",
         ["EcosDispatcher", "dispatch"]),
    ]
    
    python_pass = 0
    for file_path, description, functions in python_modules:
        full_path = os.path.join(base_path, file_path)
        if check_file_exists(full_path):
            with open(full_path, 'r') as f:
                content = f.read()
            
            all_functions_exist = all(f"def {func}" in content or f"class {func}" in content for func in functions)
            status = "✅" if all_functions_exist else "⚠️"
            print(f"  {status} {description}")
            if all_functions_exist:
                python_pass += 1
        else:
            print(f"  ❌ {description}")
    
    results['PYTHON_MODULES'] = f"{python_pass}/{len(python_modules)}"
    
    # ============================================
    # API ENDPOINTS VALIDATION
    # ============================================
    print("\n🌐 API Gateway Validation:")
    
    api_path = os.path.join(base_path, "apps/api-gateway/main.py")
    if check_file_exists(api_path):
        with open(api_path, 'r') as f:
            api_content = f.read()
        
        endpoints = [
            ("/health", "Health check"),
            ("/projects", "List projects"),
            ("/api/hydro/forecast", "Project #13: Hydro forecast"),
            ("/api/solar/forecast", "Project #12: Solar forecast"),
            ("/api/awg/forecast", "Project #9: AWG forecast"),
            ("/api/awg/optimize", "Project #9: AWG optimize"),
            ("/api/bulb/predict", "Project #8: Bulb predict"),
            ("/api/farm/optimize", "Project #3: Farm optimize"),
            ("/api/geothermal/optimize", "Project #10: Geothermal optimize"),
            ("/api/symbiosis/recommend", "Project #2: Symbiosis recommend"),
            ("/api/dispatch", "Dispatcher"),
        ]
        
        api_pass = 0
        for endpoint, description in endpoints:
            exists = endpoint in api_content
            status = "✅" if exists else "❌"
            print(f"  {status} {description}")
            if exists:
                api_pass += 1
        
        results['API_ENDPOINTS'] = f"{api_pass}/{len(endpoints)}"
    else:
        print("  ❌ API gateway not found")
        results['API_ENDPOINTS'] = "0/11"
    
    # ============================================
    # DOCUMENTATION VALIDATION
    # ============================================
    print("\n📚 Documentation Validation:")
    
    docs = [
        ("README.md", "Main README"),
        ("IMPLEMENTATION_STATUS.md", "Implementation status"),
        ("Business-Outline.md", "Business outline"),
        ("Checklist-System.md", "Checklist system"),
    ]
    
    docs_pass = 0
    for file_path, description in docs:
        full_path = os.path.join(base_path, file_path)
        exists = check_file_exists(full_path)
        status = "✅" if exists else "❌"
        print(f"  {status} {description}")
        if exists:
            docs_pass += 1
    
    results['DOCUMENTATION'] = f"{docs_pass}/{len(docs)}"
    
    # ============================================
    # SUMMARY
    # ============================================
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60 + "\n")
    
    for category, score in results.items():
        print(f"{category}: {score}")
    
    # Calculate overall readiness
    total_checks = sum(int(score.split('/')[1]) for score in results.values())
    passed_checks = sum(int(score.split('/')[0]) for score in results.values())
    completion_rate = (passed_checks / total_checks) * 100 if total_checks > 0 else 0
    
    print(f"\n{'=' * 60}")
    print(f"OVERALL COMPLETION: {completion_rate:.1f}%")
    print(f"Checks Passed: {passed_checks} / {total_checks}")
    print(f"{'=' * 60}\n")
    
    if completion_rate >= 90:
        print("🎉 STRUCTURE VALIDATION: SUCCESS")
        print("All required files and structures are in place!\n")
        return 0
    else:
        print("⚠️  STRUCTURE VALIDATION: INCOMPLETE")
        print(f"Current completion: {completion_rate:.1f}% (target: 90%+)\n")
        return 1


if __name__ == '__main__':
    import sys
    exit_code = validate_structure()
    sys.exit(exit_code)
