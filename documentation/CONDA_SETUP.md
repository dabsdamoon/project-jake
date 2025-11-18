# JAKE Setup with Conda

## Prerequisites

Make sure you have Conda installed:
- **Miniconda** (recommended): https://docs.conda.io/en/latest/miniconda.html
- **Anaconda**: https://www.anaconda.com/download

Verify installation:
```bash
conda --version
```

---

## 🚀 Quick Start (3 Steps)

### 1. Create Conda Environment

```bash
# Create environment from environment.yml
conda env create -f environment.yml
```

This creates an environment named `jake` with Python 3.11 and all dependencies.

### 2. Set Up API Key

```bash
# Copy example env file
cp .env.example .env

# Edit and add your OpenAI API key
nano .env
# or
vim .env
# or
code .env
```

Add this line:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 3. Run the Server

```bash
# Activate environment
conda activate jake

# Start the server
python -m src.main
```

**Or use the startup script:**
```bash
./start_server.sh
```

The script automatically:
- Checks for conda installation
- Creates/updates the environment
- Activates the environment
- Initializes the database
- Starts the server

---

## 📦 Environment Management

### View Installed Packages

```bash
conda activate jake
conda list
```

### Update Environment

If `environment.yml` changes:
```bash
conda activate jake
conda env update -f environment.yml --prune
```

### Add New Package

**Option 1: Update environment.yml**
```yaml
dependencies:
  - python=3.11
  - pip
  - pip:
      - your-new-package
```

Then update:
```bash
conda env update -f environment.yml
```

**Option 2: Install directly**
```bash
conda activate jake
pip install your-new-package

# Export to requirements.txt
pip freeze > requirements.txt
```

### Remove Environment

```bash
conda deactivate
conda env remove -n jake
```

### Recreate Environment

```bash
conda env remove -n jake
conda env create -f environment.yml
```

---

## 🔄 Multiple Environments

If you want different configurations:

```bash
# Development environment
conda env create -f environment.yml -n jake-dev

# Production environment
conda env create -f environment.yml -n jake-prod

# Activate specific environment
conda activate jake-dev
```

---

## 🐍 Python Version

The environment uses Python 3.11. To change:

Edit `environment.yml`:
```yaml
dependencies:
  - python=3.10  # or 3.9, 3.12, etc.
```

Then recreate:
```bash
conda env remove -n jake
conda env create -f environment.yml
```

---

## 🔧 Troubleshooting

### Conda environment not activating

**Issue**: `conda activate jake` doesn't work

**Solution**:
```bash
# Initialize conda for your shell (one-time setup)
conda init bash  # or zsh, fish, etc.

# Restart terminal or run:
source ~/.bashrc  # or ~/.zshrc
```

### Package conflicts

**Issue**: Dependency resolution errors

**Solution 1**: Use mamba (faster resolver)
```bash
# Install mamba
conda install -n base conda-forge::mamba

# Create environment with mamba
mamba env create -f environment.yml
```

**Solution 2**: Specify channels explicitly
```bash
conda env create -f environment.yml --channel defaults --channel conda-forge
```

### Missing packages after activation

**Issue**: Import errors after activating environment

**Solution**:
```bash
conda activate jake
conda env update -f environment.yml --prune
```

### OpenAI API errors

**Issue**: `openai.error.AuthenticationError`

**Solution**:
1. Check `.env` file exists
2. Verify `OPENAI_API_KEY` is set correctly
3. No spaces around `=` in `.env`
4. API key starts with `sk-`

```bash
# Check if .env is loaded
conda activate jake
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('OPENAI_API_KEY', 'NOT FOUND'))"
```

---

## 📊 Conda vs Pip

**Why use Conda?**
- Better dependency resolution
- Environment isolation
- Cross-platform consistency
- Can install non-Python packages (e.g., system libraries)
- Multiple Python versions easily

**Conda + Pip hybrid** (what we're using):
- Conda for Python and base packages
- Pip for specific ML/AI packages (LangChain, etc.)
- Best of both worlds!

---

## 🚀 Advanced: Multiple Servers

Run multiple instances with different environments:

```bash
# Terminal 1: Development
conda activate jake-dev
python -m src.main --port 8000

# Terminal 2: Testing
conda activate jake-test
python -m src.main --port 8001

# Terminal 3: Production
conda activate jake-prod
python -m src.main --port 8002
```

---

## 📝 Environment Export

Share your exact environment:

```bash
# Export with all dependencies
conda activate jake
conda env export > environment-full.yml

# Export cross-platform (no builds)
conda env export --no-builds > environment.yml

# Someone else can recreate:
conda env create -f environment-full.yml
```

---

## 🎯 Quick Reference

```bash
# Create environment
conda env create -f environment.yml

# Activate
conda activate jake

# Deactivate
conda deactivate

# List environments
conda env list

# Update
conda env update -f environment.yml

# Remove
conda env remove -n jake

# Export
conda env export > environment.yml

# Install package
conda activate jake
pip install package-name

# Run server
python -m src.main
```

---

## ✅ Verification

Check everything is set up correctly:

```bash
# 1. Activate environment
conda activate jake

# 2. Check Python version
python --version  # Should be 3.11.x

# 3. Check packages
python -c "import fastapi, langchain, openai; print('✅ All packages installed')"

# 4. Check .env
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('API Key:', 'Found' if os.getenv('OPENAI_API_KEY') else 'Missing')"

# 5. Run server
python -m src.main
```

If all steps pass, you're ready to go! 🎉

---

## 🔗 Additional Resources

- **Conda User Guide**: https://docs.conda.io/projects/conda/en/latest/user-guide/
- **Managing Environments**: https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html
- **Conda Cheat Sheet**: https://docs.conda.io/projects/conda/en/latest/user-guide/cheatsheet.html
