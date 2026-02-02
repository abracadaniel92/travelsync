# TravelSync Scripts

This directory contains utility scripts for the TravelSync project.

## Scripts

### Setup Scripts
- `quick_setup.sh` - Quick setup script
- `deploy_pi.sh` - Deploy to Raspberry Pi
- `start_server.ps1` - Start development server (Windows)

### Utility Scripts
- `create_user.py` - Create a new user
- `set_admin_password.py` - Set admin password
- `test_upload.py` - Test document upload

### Build & Monitoring
- `check_build.sh` - Check build status
- `monitor_build.sh` - Monitor build process

## Usage

### Windows
```powershell
.\scripts\start_server.ps1
```

### Linux/Mac
```bash
./scripts/quick_setup.sh
./scripts/deploy_pi.sh
```

### Python Scripts
```bash
python scripts/create_user.py
python scripts/set_admin_password.py
python scripts/test_upload.py
```
