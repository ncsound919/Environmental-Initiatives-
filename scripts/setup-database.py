#!/usr/bin/env python3
"""
ECOS Database Setup Script
Level 2/3: Database persistence with TimescaleDB hypertables
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Run a shell command and handle errors"""
    print(f"\n{'='*60}")
    print(f"📦 {description}")
    print(f"{'='*60}")
    print(f"Running: {cmd}\n")
    
    result = subprocess.run(cmd, shell=True, capture_output=False, text=True)
    if result.returncode != 0:
        print(f"❌ Error: {description} failed")
        return False
    print(f"✅ Success: {description} completed")
    return True

def main():
    """Setup ECOS database with TimescaleDB"""
    
    repo_root = Path(__file__).parent.parent
    os.chdir(repo_root)
    
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║           ECOS Database Setup - Level 2/3 Readiness          ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    # Check if .env file exists
    if not (repo_root / ".env").exists():
        print("⚠️  No .env file found. Copying from .env.example...")
        if (repo_root / ".env.example").exists():
            run_command("cp .env.example .env", "Copy environment template")
            print("⚠️  Please edit .env with your database credentials before continuing")
            print("    Default: postgresql://ecos:ecos_password@localhost:5432/ecos_db")
            response = input("\n✓ Press Enter when ready to continue, or 'q' to quit: ")
            if response.lower() == 'q':
                sys.exit(0)
        else:
            print("❌ Error: .env.example not found")
            sys.exit(1)
    
    # Load environment
    print("\n📋 Loading environment configuration...")
    from dotenv import load_dotenv
    load_dotenv()
    
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ Error: DATABASE_URL not set in .env")
        sys.exit(1)
    print(f"✓ Database URL: {db_url.split('@')[1] if '@' in db_url else 'configured'}")
    
    # Step 1: Generate Prisma client
    if not run_command(
        "cd packages/core/database-schema && npx prisma generate",
        "Generate Prisma Client"
    ):
        print("⚠️  Warning: Prisma client generation failed. Continuing anyway...")
    
    # Step 2: Create migration
    print("\n🔄 Creating database migration...")
    print("    This will create tables based on schema.prisma")
    
    migration_name = "init_ecos_schema"
    if not run_command(
        f"cd packages/core/database-schema && npx prisma migrate dev --name {migration_name}",
        "Create Prisma Migration"
    ):
        print("❌ Migration failed. Make sure:")
        print("   1. PostgreSQL is running")
        print("   2. DATABASE_URL in .env is correct")
        print("   3. Database user has CREATE privileges")
        sys.exit(1)
    
    # Step 3: Enable TimescaleDB hypertables
    print("\n⏰ Converting tables to TimescaleDB hypertables...")
    print("    This optimizes time-series queries for telemetry data")
    
    hypertables = [
        ("telemetry", "timestamp"),
        ("bulb_telemetry", "timestamp"),
        ("water_generation", "timestamp"),
        ("solar_generation", "timestamp"),
        ("hydro_generation", "timestamp"),
        ("geothermal_flow", "timestamp"),
        ("bioreactor_readings", "timestamp"),
        ("soil_readings", "timestamp"),
        ("prediction_logs", "timestamp"),
        ("audit_logs", "timestamp"),
    ]
    
    for table, time_column in hypertables:
        # This is a safe operation - it will skip if already a hypertable
        sql = f"SELECT create_hypertable('{table}', '{time_column}', if_not_exists => TRUE);"
        cmd = f'psql "{db_url}" -c "{sql}"'
        if run_command(cmd, f"Create hypertable: {table}"):
            print(f"   ✓ {table} is now optimized for time-series queries")
    
    # Step 4: Create performance indexes
    print("\n📊 Creating performance indexes...")
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_telemetry_project_time ON telemetry (sourceSystem, timestamp DESC);",
        "CREATE INDEX IF NOT EXISTS idx_telemetry_device_time ON telemetry (sensorId, timestamp DESC);",
        "CREATE INDEX IF NOT EXISTS idx_bulb_device_time ON bulb_telemetry (bulbId, timestamp DESC);",
        "CREATE INDEX IF NOT EXISTS idx_water_device_time ON water_generation (deviceId, timestamp DESC);",
        "CREATE INDEX IF NOT EXISTS idx_solar_array_time ON solar_generation (arrayId, timestamp DESC);",
        "CREATE INDEX IF NOT EXISTS idx_hydro_turbine_time ON hydro_generation (turbineId, timestamp DESC);",
    ]
    
    for sql in indexes:
        run_command(f'psql "{db_url}" -c "{sql}"', "Create index")
    
    # Success message
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║                 ✅ DATABASE SETUP COMPLETE                    ║
    ║                                                               ║
    ║  Your ECOS database is ready for Level 2/3 operations:       ║
    ║  • PostgreSQL + TimescaleDB hypertables                       ║
    ║  • 16 project-specific tables                                 ║
    ║  • Time-series optimization for telemetry                     ║
    ║  • Performance indexes created                                ║
    ║                                                               ║
    ║  Next steps:                                                  ║
    ║  1. Start API: cd apps/api-gateway && python main.py         ║
    ║  2. Start Web: cd apps/web && npm run dev                     ║
    ║  3. View data: npx prisma studio                              ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Setup failed with error: {e}")
        sys.exit(1)
