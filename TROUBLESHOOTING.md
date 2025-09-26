# RA9 Installation Troubleshooting Guide

## 🚨 "ModuleNotFoundError: No module named 'pydantic'" Fix

If you're getting this error, it means the dependencies weren't installed properly. Here's how to fix it:

### Method 1: Use the Automated Installer (Recommended)

```bash
# Clone the repository
git clone https://github.com/LevelSUB-zero/rA9-Base.git
cd rA9-Base

# Switch to Current branch (has latest fixes)
git checkout Current

# Run the automated installer
python install_current.py
```

### Method 2: Manual Installation

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Upgrade pip and install build tools
python -m pip install --upgrade pip setuptools wheel

# 4. Install core dependencies first
pip install pydantic>=2.0.0 pydantic-settings>=2.0.0 typer structlog

# 5. Install RA9 package
pip install -e .

# 6. Verify installation
python check_deps.py
```

### Method 3: Quick Fix for Existing Installation

If you already have RA9 installed but getting pydantic errors:

```bash
# Activate your virtual environment first
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install missing dependencies
pip install pydantic>=2.0.0 pydantic-settings>=2.0.0

# Verify
python check_deps.py
```

### Method 4: Nuclear Option (Clean Install)

If nothing else works:

```bash
# Remove existing virtual environment
rm -rf venv  # macOS/Linux
# or
rmdir /s venv  # Windows

# Start fresh with automated installer
python install_current.py
```

## 🔍 Troubleshooting Steps

### 1. Check Your Python Version
```bash
python --version
# Should be Python 3.8 or higher
```

### 2. Check if Virtual Environment is Activated
```bash
# You should see (venv) in your prompt
# If not, activate it:
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
```

### 3. Check Dependencies
```bash
python check_deps.py
```

### 4. Test RA9 Import
```bash
python -c "import ra9; print('RA9 imported successfully')"
```

## 🚨 Common Issues

### Issue: "Could not find platform independent libraries"
**Solution**: This usually means Python installation is corrupted. Reinstall Python or use a different Python version.

### Issue: "Permission denied" on Windows
**Solution**: Run Command Prompt as Administrator or use PowerShell.

### Issue: "pip not found"
**Solution**: 
```bash
python -m ensurepip --upgrade
python -m pip install --upgrade pip
```

### Issue: Still getting pydantic errors after installation
**Solution**: Make sure you're using the virtual environment:
```bash
# Check which Python you're using
which python  # macOS/Linux
where python  # Windows

# Should point to your venv directory
```

## ✅ Success Indicators

You'll know it's working when:
- `python check_deps.py` shows all green checkmarks
- `python -c "import ra9"` succeeds without errors
- `python -m ra9.cli --help` shows the help menu

## 🆘 Still Having Issues?

1. **Check the Current branch**: Make sure you're using the latest version
   ```bash
   git checkout Current
   ```

2. **Use the dependency checker**: Run `python check_deps.py` to see exactly what's missing

3. **Check Python version**: RA9 requires Python 3.8+

4. **Use virtual environment**: Always use a virtual environment to avoid conflicts

5. **Contact support**: If nothing works, create an issue on GitHub with:
   - Your Python version (`python --version`)
   - Your operating system
   - The exact error message
   - Output from `python check_deps.py`
