#!/usr/bin/env python3
"""
Saudi Al-Rajhi Real Estate - Cursor Python Development Environment Setup
Enhanced Python development setup for Cursor IDE with Odoo 18.0 support

Author: roottbar
Email: root@tbarholding.com
Date: 2025-01-30
"""

import os
import sys
import subprocess
import platform
import json
from pathlib import Path
from typing import List, Dict, Any

class CursorPythonSetup:
    """Enhanced Python development environment setup for Cursor IDE"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        self.platform = platform.system().lower()
        self.is_windows = self.platform == "windows"
        
    def run_command(self, command: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """Run a command and return the result"""
        try:
            print(f"Running: {' '.join(command)}")
            result = subprocess.run(
                command,
                check=check,
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            if result.stdout:
                print(f"Output: {result.stdout}")
            return result
        except subprocess.CalledProcessError as e:
            print(f"Error running command: {e}")
            if e.stderr:
                print(f"Error output: {e.stderr}")
            if check:
                raise
            return e
    
    def check_python_version(self) -> bool:
        """Check if Python version is compatible"""
        print(f"Checking Python version: {self.python_version}")
        if sys.version_info < (3, 8):
            print("❌ Python 3.8 or higher is required")
            return False
        print("✅ Python version is compatible")
        return True
    
    def check_pip(self) -> bool:
        """Check if pip is available"""
        try:
            self.run_command([sys.executable, "-m", "pip", "--version"])
            print("✅ pip is available")
            return True
        except subprocess.CalledProcessError:
            print("❌ pip is not available")
            return False
    
    def upgrade_pip(self) -> None:
        """Upgrade pip to latest version"""
        print("Upgrading pip...")
        self.run_command([
            sys.executable, "-m", "pip", "install", "--upgrade", "pip"
        ])
        print("✅ pip upgraded successfully")
    
    def install_requirements(self) -> None:
        """Install project requirements"""
        print("Installing project requirements...")
        
        # Install core requirements
        self.run_command([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        
        # Install development requirements
        if self.is_windows:
            self.run_command([
                sys.executable, "-m", "pip", "install", "-e", ".[dev,cursor]"
            ])
        else:
            self.run_command([
                sys.executable, "-m", "pip", "install", "-e", ".[dev,cursor]"
            ])
        
        print("✅ Requirements installed successfully")
    
    def install_cursor_extensions(self) -> None:
        """Install recommended Cursor extensions"""
        print("Installing Cursor extensions...")
        
        extensions = [
            # Python Development
            "ms-python.python",
            "ms-python.pylance",
            "ms-python.debugpy",
            "ms-python.flake8",
            "ms-python.black-formatter",
            "ms-python.isort",
            
            # Odoo Development
            "jigar-patel.OdooSnippets",
            "ms-vscode.xml",
            "redhat.vscode-xml",
            "formulahendry.auto-rename-tag",
            "christian-kohler.path-intellisense",
            
            # GitHub Integration
            "GitHub.vscode-pull-request-github",
            "GitHub.copilot",
            "GitHub.copilot-chat",
            "eamodio.gitlens",
            "mhutchie.git-graph",
            
            # AI & MCP
            "continue.continue",
            "sourcegraph.cody",
            "tabnine.tabnine-vscode",
            "mintlify.document",
            "rubberduck.rubberduck-vscode",
            
            # Database & Development
            "ckolkman.vscode-postgres",
            "humao.rest-client",
            "ms-vscode.vscode-docker",
            
            # Productivity
            "alefragnani.Bookmarks",
            "streetsidesoftware.code-spell-checker",
            "PKief.material-icon-theme",
            "formulahendry.code-runner",
            "Gruntfuggly.todo-tree"
        ]
        
        for extension in extensions:
            try:
                self.run_command([
                    "code", "--install-extension", extension
                ], check=False)
                print(f"✅ Installed: {extension}")
            except FileNotFoundError:
                print(f"⚠️  Cursor/VS Code not found in PATH, skipping: {extension}")
            except subprocess.CalledProcessError:
                print(f"⚠️  Failed to install: {extension}")
    
    def create_vscode_config(self) -> None:
        """Create VS Code configuration files"""
        print("Creating VS Code configuration...")
        
        vscode_dir = self.project_root / ".vscode"
        vscode_dir.mkdir(exist_ok=True)
        
        # Launch configuration
        launch_config = {
            "version": "0.2.0",
            "configurations": [
                {
                    "name": "Odoo Debug",
                    "type": "python",
                    "request": "launch",
                    "program": "${workspaceFolder}/odoo-bin",
                    "args": [
                        "--addons-path=${workspaceFolder}/addons,${workspaceFolder}/custom_addons",
                        "--database=odoo_dev",
                        "--dev=xml,reload,qweb,werkzeug,all"
                    ],
                    "console": "integratedTerminal",
                    "cwd": "${workspaceFolder}",
                    "env": {
                        "PYTHONPATH": "${workspaceFolder}"
                    },
                    "justMyCode": False
                },
                {
                    "name": "Python: Current File",
                    "type": "python",
                    "request": "launch",
                    "program": "${file}",
                    "console": "integratedTerminal",
                    "cwd": "${workspaceFolder}"
                },
                {
                    "name": "Python: Module",
                    "type": "python",
                    "request": "launch",
                    "module": "enter-your-module-name-here",
                    "console": "integratedTerminal",
                    "cwd": "${workspaceFolder}"
                }
            ]
        }
        
        with open(vscode_dir / "launch.json", "w") as f:
            json.dump(launch_config, f, indent=2)
        
        # Tasks configuration
        tasks_config = {
            "version": "2.0.0",
            "tasks": [
                {
                    "label": "Install Requirements",
                    "type": "shell",
                    "command": "python",
                    "args": ["-m", "pip", "install", "-r", "requirements.txt"],
                    "group": "build",
                    "presentation": {
                        "echo": True,
                        "reveal": "always",
                        "focus": False,
                        "panel": "shared"
                    }
                },
                {
                    "label": "Run Tests",
                    "type": "shell",
                    "command": "python",
                    "args": ["-m", "pytest", "tests/", "-v"],
                    "group": "test",
                    "presentation": {
                        "echo": True,
                        "reveal": "always",
                        "focus": False,
                        "panel": "shared"
                    }
                },
                {
                    "label": "Format Code",
                    "type": "shell",
                    "command": "python",
                    "args": ["-m", "black", "."],
                    "group": "build",
                    "presentation": {
                        "echo": True,
                        "reveal": "always",
                        "focus": False,
                        "panel": "shared"
                    }
                },
                {
                    "label": "Lint Code",
                    "type": "shell",
                    "command": "python",
                    "args": ["-m", "flake8", "."],
                    "group": "build",
                    "presentation": {
                        "echo": True,
                        "reveal": "always",
                        "focus": False,
                        "panel": "shared"
                    }
                }
            ]
        }
        
        with open(vscode_dir / "tasks.json", "w") as f:
            json.dump(tasks_config, f, indent=2)
        
        print("✅ VS Code configuration created")
    
    def create_gitignore(self) -> None:
        """Create or update .gitignore file"""
        print("Creating .gitignore...")
        
        gitignore_content = """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
#  Usually these files are written by a python script from a template
#  before PyInstaller builds the exe, so as to inject date/other infos into it.
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# pipenv
#   According to pypa/pipenv#598, it is recommended to include Pipfile.lock in version control.
#   However, in case of collaboration, if having platform-specific dependencies or dependencies
#   having no cross-platform support, pipenv may install dependencies that don't work, or not
#   install all needed dependencies.
#Pipfile.lock

# PEP 582; used by e.g. github.com/David-OConnor/pyflow
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# Odoo specific
*.log
/filestore/
/sessions/
*.pot
*.sql
*.db

# IDE
.vscode/settings.json
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Node modules (for frontend development)
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Temporary files
*.tmp
*.temp
*.bak
*.backup
*.orig

# Cursor specific
.cursor/
.cursorrules
"""
        
        with open(self.project_root / ".gitignore", "w") as f:
            f.write(gitignore_content)
        
        print("✅ .gitignore created")
    
    def create_cursorrules(self) -> None:
        """Create .cursorrules file for AI assistance"""
        print("Creating .cursorrules...")
        
        cursorrules_content = """# Saudi Al-Rajhi Real Estate - Cursor AI Rules

## Project Context
This is an Odoo 18.0 project for Saudi Al-Rajhi Real Estate management system.
- Repository: saudalrajhirealestate
- Developer: roottbar (root@tbarholding.com)
- Python Version: 3.8+
- Framework: Odoo 18.0

## Code Style Guidelines
- Follow PEP 8 with 88 character line length (Black formatter)
- Use type hints for all function parameters and return values
- Write comprehensive docstrings for all classes and functions
- Use meaningful variable and function names
- Follow Odoo coding conventions

## Python Development
- Use f-strings for string formatting
- Prefer list/dict comprehensions over loops when appropriate
- Use pathlib.Path for file operations
- Handle exceptions explicitly with try/except blocks
- Use logging instead of print statements

## Odoo Specific
- Follow Odoo's ORM patterns
- Use proper model inheritance
- Implement proper security rules
- Use proper field types and constraints
- Follow Odoo's naming conventions for models, fields, and methods

## File Organization
- Keep related functionality in the same module
- Use proper imports (standard library, third-party, local)
- Maintain clear separation between models, views, and controllers
- Use proper manifest files with correct dependencies

## Testing
- Write unit tests for all business logic
- Use pytest for testing
- Mock external dependencies
- Test edge cases and error conditions

## Documentation
- Write clear README files for each module
- Document complex business logic
- Keep comments up to date
- Use proper docstring formats

## Security
- Validate all user inputs
- Use proper authentication and authorization
- Follow OWASP guidelines
- Sanitize data before database operations

## Performance
- Optimize database queries
- Use proper indexing
- Avoid N+1 query problems
- Use caching where appropriate

## Error Handling
- Use proper exception handling
- Log errors appropriately
- Provide meaningful error messages
- Handle edge cases gracefully

## Git Workflow
- Use descriptive commit messages
- Create feature branches for new functionality
- Use pull requests for code review
- Keep commits atomic and focused

## AI Assistance Guidelines
- Always consider the Odoo context when suggesting code
- Provide complete, working code examples
- Explain complex business logic
- Suggest improvements for performance and security
- Help with debugging and troubleshooting
"""
        
        with open(self.project_root / ".cursorrules", "w") as f:
            f.write(cursorrules_content)
        
        print("✅ .cursorrules created")
    
    def create_development_scripts(self) -> None:
        """Create development helper scripts"""
        print("Creating development scripts...")
        
        # Windows batch script
        if self.is_windows:
            dev_script = """@echo off
echo Saudi Al-Rajhi Real Estate - Development Environment
echo ================================================

echo Activating Python virtual environment...
call python -m venv venv
call venv\\Scripts\\activate

echo Installing requirements...
call python -m pip install --upgrade pip
call python -m pip install -r requirements.txt
call python -m pip install -e .[dev,cursor]

echo Setting up pre-commit hooks...
call python -m pip install pre-commit
call pre-commit install

echo Development environment ready!
echo Run 'python -m pytest' to run tests
echo Run 'python -m black .' to format code
echo Run 'python -m flake8 .' to lint code
pause
"""
            with open(self.project_root / "setup_dev_env.bat", "w") as f:
                f.write(dev_script)
        
        # Unix shell script
        dev_script_sh = """#!/bin/bash
echo "Saudi Al-Rajhi Real Estate - Development Environment"
echo "================================================"

echo "Activating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "Installing requirements..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .[dev,cursor]

echo "Setting up pre-commit hooks..."
python -m pip install pre-commit
pre-commit install

echo "Development environment ready!"
echo "Run 'python -m pytest' to run tests"
echo "Run 'python -m black .' to format code"
echo "Run 'python -m flake8 .' to lint code"
"""
        
        with open(self.project_root / "setup_dev_env.sh", "w") as f:
            f.write(dev_script_sh)
        
        # Make shell script executable
        if not self.is_windows:
            os.chmod(self.project_root / "setup_dev_env.sh", 0o755)
        
        print("✅ Development scripts created")
    
    def setup_pre_commit_hooks(self) -> None:
        """Set up pre-commit hooks for code quality"""
        print("Setting up pre-commit hooks...")
        
        pre_commit_config = """repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: debug-statements

  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.1
    hooks:
      - id: mypy
        additional_dependencies: [types-requests, types-PyYAML]
        args: [--ignore-missing-imports]

  - repo: https://github.com/pycqa/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: [-r, ., -f, json, -o, bandit-report.json]
"""
        
        with open(self.project_root / ".pre-commit-config.yaml", "w") as f:
            f.write(pre_commit_config)
        
        print("✅ Pre-commit hooks configured")
    
    def run_setup(self) -> None:
        """Run the complete setup process"""
        print("🚀 Starting Cursor Python Development Environment Setup")
        print("=" * 60)
        
        # Check prerequisites
        if not self.check_python_version():
            sys.exit(1)
        
        if not self.check_pip():
            sys.exit(1)
        
        # Upgrade pip
        self.upgrade_pip()
        
        # Install requirements
        self.install_requirements()
        
        # Create configuration files
        self.create_vscode_config()
        self.create_gitignore()
        self.create_cursorrules()
        self.create_development_scripts()
        self.setup_pre_commit_hooks()
        
        # Install Cursor extensions
        self.install_cursor_extensions()
        
        print("\n" + "=" * 60)
        print("✅ Setup completed successfully!")
        print("\nNext steps:")
        print("1. Restart Cursor IDE")
        print("2. Open the project folder in Cursor")
        print("3. Select the Python interpreter (Ctrl+Shift+P -> 'Python: Select Interpreter')")
        print("4. Run 'python setup_dev_env.bat' (Windows) or './setup_dev_env.sh' (Unix) to set up the development environment")
        print("5. Start coding with enhanced Python support!")
        print("\nHappy coding! 🎉")

def main():
    """Main entry point"""
    setup = CursorPythonSetup()
    setup.run_setup()

if __name__ == "__main__":
    main()