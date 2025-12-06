#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧹 CLEANUP SCRIPT - Remove obsolete files safely
Remove todos os arquivos obsoletos identificados na análise.
SEGURO: Apenas remove arquivos conhecidamente obsoletos.
"""
import os
import shutil
from pathlib import Path

WORKSPACE = r"c:\licimar_dsv"

# Arquivos DEFINITIVAMENTE obsoletos (50+ files)
ROOT_OBSOLETE_FILES = [
    # test_*.py files (50+)
    "test_api_debug.py", "test_api_detailed.py", "test_api_quick.py", "test_api.py",
    "test_backend_simple.py", "test_backend_startup.py", "test_complete_flow.py",
    "test_complete_login.py", "test_comprehensive_flows.py", "test_comprehensive_validation.py",
    "test_create_pedido.py", "test_final.py", "test_login_api.py", "test_login.py",
    "test_password.py", "test_pdf_direct.py", "test_pdf_endpoint.py", "test_pdf_generation.py",
    "test_pdf_with_login.py", "test_persistence.py", "test_post_retorno.py", "test_problems.py",
    "test_quick.py", "test_real_problems.py", "test_retorno_debug.py", "test_saida_error.py",
    "test_simple.py", "test_all_fixes.py", "test_all_problems.py",
    
    # temp_*.py files
    "temp_check_gelo.py", "temp_check_produtos.py", "temp_check_schema.py", "temp_check_tables.py",
    
    # check_*.py files
    "check_all_produtos.py", "check_data.py", "check_db_users.py", "check_gelo.py",
    "check_nao_devolve.py", "check_schema.py", "check_users_db.py", "check_users.py",
    
    # debug_*.py files
    "debug_gelo.py", "debug_pdf.py",
    
    # fix_*.py files
    "fix_datetime_brasilia.py", "fix_nao_devolve.py",
    
    # start_*.py files
    "start_backend.py", "start_and_test.py",
    
    # Other obsolete files
    "remove_duplicates.py", "clean_history.py", "quick_health_check.py",
    "list_db_tables.py", "setup.py", "final_test_all.py",
]

# Backend obsolete files
BACKEND_OBSOLETE_FILES = [
    "app_debug.py",  # Debug version of app
    "check_db.py", "check_test_data.py",  # Debug scripts
    "debug_response.py", "response_debug.txt",  # Debug artifacts
    "init_db.py", "init_db_simple.py", "init_db_native.py", "init_db_standalone.py",  # Old variants
    "init_database.py", "populate_db.py",  # Old database setup
    "migrate_add_divida.py", "migrate_quantities_to_int.py",  # Old migrations
]

# Backend test files (obsolete)
BACKEND_TEST_FILES = [
    "test_quick.py", "test_sqlite.py", "test_login_debug.py", "test_ambulantes_model.py",
]

# Documentation files to consolidate
DOCS_TO_CONSOLIDATE = [
    "FIXES_CURRENT.md", "FIXES_DECEMBER_01.md", "FIXES_FINAL_03_12_2025.md", "FIXES_SUMMARY.md",
    "STATUS.md", "STATUS_FINAL.md",
]


def print_header(title):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"🧹 {title}")
    print("="*70 + "\n")


def safe_delete(file_path, dry_run=True):
    """Safely delete a file with confirmation"""
    if not os.path.exists(file_path):
        return False
    
    action = "[DRY-RUN]" if dry_run else "[DELETE]"
    
    try:
        if dry_run:
            print(f"{action} Would delete: {file_path}")
        else:
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"{action} ✅ Deleted: {file_path}")
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
                print(f"{action} ✅ Deleted directory: {file_path}")
        return True
    except Exception as e:
        print(f"{action} ❌ Error deleting {file_path}: {e}")
        return False


def cleanup(dry_run=True):
    """Execute cleanup"""
    
    print_header("ANALYSIS & CLEANUP - LICIMAR MVP")
    
    if dry_run:
        print("⚠️  DRY-RUN MODE (no files will be deleted)")
        print("To execute cleanup, run with dry_run=False\n")
    
    deleted_count = 0
    
    # 1. Clean root directory
    print_header("1️⃣  ROOT DIRECTORY - Obsolete Test Files")
    print(f"Found {len(ROOT_OBSOLETE_FILES)} obsolete files to remove:\n")
    
    for filename in ROOT_OBSOLETE_FILES:
        file_path = os.path.join(WORKSPACE, filename)
        if safe_delete(file_path, dry_run):
            deleted_count += 1
    
    # 2. Clean backend directory
    print_header("2️⃣  BACKEND - Obsolete Database Setup Files")
    print(f"Found {len(BACKEND_OBSOLETE_FILES)} obsolete files to remove:\n")
    
    backend_path = os.path.join(WORKSPACE, "backend", "licimar_mvp_app")
    for filename in BACKEND_OBSOLETE_FILES:
        file_path = os.path.join(backend_path, filename)
        if safe_delete(file_path, dry_run):
            deleted_count += 1
    
    # 3. Clean backend test files
    print_header("3️⃣  BACKEND - Obsolete Test Files")
    print(f"Found {len(BACKEND_TEST_FILES)} obsolete test files:\n")
    
    for filename in BACKEND_TEST_FILES:
        file_path = os.path.join(backend_path, filename)
        if safe_delete(file_path, dry_run):
            deleted_count += 1
    
    # 4. Document consolidation recommendations
    print_header("4️⃣  DOCUMENTATION - Consolidation Recommendations")
    print("The following documentation files should be consolidated:\n")
    
    for filename in DOCS_TO_CONSOLIDATE:
        file_path = os.path.join(WORKSPACE, filename)
        if os.path.exists(file_path):
            print(f"  • {filename}")
    
    print("\n📋 Recommendation:")
    print("  ✓ Create CHANGELOG.md with history of all fixes")
    print("  ✓ Keep README.md with current status only")
    print("  ✓ Archive old documentation files\n")
    
    # Summary
    print_header("📊 SUMMARY")
    print(f"Files to be removed: {deleted_count}")
    print(f"Root obsolete files: {len(ROOT_OBSOLETE_FILES)}")
    print(f"Backend obsolete files: {len(BACKEND_OBSOLETE_FILES)}")
    print(f"Backend test files: {len(BACKEND_TEST_FILES)}")
    print(f"Documentation files to consolidate: {len(DOCS_TO_CONSOLIDATE)}")
    
    print_header("✅ CLEANUP READY")
    
    if dry_run:
        print("📌 Dry-run completed successfully!")
        print("\n🚀 To EXECUTE cleanup, run:")
        print("   python cleanup_obsolete.py --execute\n")
    else:
        print(f"✅ Successfully removed {deleted_count} obsolete files!")
        print("🎉 Project cleanup completed!\n")


if __name__ == '__main__':
    import sys
    
    dry_run = '--execute' not in sys.argv
    
    cleanup(dry_run=dry_run)
