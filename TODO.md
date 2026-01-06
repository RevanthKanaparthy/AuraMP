# TODO: Remove Unnecessary Files from Repository

## Steps to Complete
- [x] Identify and list all unnecessary files to remove
- [x] Use Git commands to remove the files from the repository (git rm --cached for tracked files)
- [ ] Commit the changes with a descriptive message
- [ ] Push the changes to the GitHub repository

## Files to Remove
- All test_*.py files (e.g., test_chunking_improvements.py, test_hash_match.py, test_login_fix.py, etc.)
- All temp_*.py files (e.g., temp_inspect_embeddings.py, temp_read.py, temp_delete_endpoint.py, etc.)
- All debug_*.py files (e.g., debug_password.py, debug_file_processing.py)
- All fix_*.py files (e.g., fix_passwords.py)
- All check_*.py files (e.g., check_passwords.py)
- All generate_*.py files (e.g., generate_hashes.py)
- All update_*.py files (e.g., update_excel.py, update_db_schema.py)
- All reupload_*.py files (e.g., reupload_excel.py)
- upload_test.py
- test_upload.xlsx
- test_upload.docx
- Other potentially unnecessary files: reset_admin_password.py, logging_config.py, middleware.py, query, read_cnn_pdf.py, read_papers.py, aura_admin_system.tsx, package-lock.json, create_report.py, test_xlsx_upload.py

## Essential Files Retained
- backend_complete.py
- requirements.txt
- database_schema.sql
- docker-compose.yml
- README.md
- .gitignore
- .gitattributes
- aura-frontend/ directory
- eval/ directory
- Other core files
