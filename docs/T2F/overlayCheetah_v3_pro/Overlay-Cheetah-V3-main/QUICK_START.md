# Overlay Cheetah V3 - Quick Start Guide

## For Immediate Implementation

This guide provides the fastest path from planning to coding. Use this if you're ready to start building NOW.

## Prerequisites

Before starting, ensure you have:
- [ ] Python 3.11+ installed
- [ ] Node.js 20+ installed
- [ ] Docker and Docker Compose installed
- [ ] Git configured
- [ ] GitHub account with repository access
- [ ] API keys ready:
  - [ ] Google Gemini API key
  - [ ] Anthropic Claude API key (optional)
  - [ ] OpenAI API key (optional)

## Phase 0: Foundation Setup (Day 1)

### Step 1: Clone and Initialize Repository

```bash
# Clone the repository
git clone https://github.com/tap919/Overlay-Cheetah-V3.git
cd Overlay-Cheetah-V3

# Create initial project structure
mkdir -p packages/{core,cli,vscode-extension,desktop,web}
mkdir -p scripts docs tests
```

### Step 2: Set Up Python Environment

```bash
# Create Python virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Poetry (dependency management)
pip install poetry

# Initialize Poetry in core package
cd packages/core
poetry init --no-interaction
poetry add fastapi uvicorn langchain chromadb redis sentence-transformers gitpython
poetry add --group dev pytest black ruff mypy pytest-asyncio pytest-cov
cd ../..
```

### Step 3: Set Up Node.js Environment

```bash
# Install pnpm globally
npm install -g pnpm

# Initialize workspace
cat > package.json << EOF
{
  "name": "cheetah-v3-monorepo",
  "private": true,
  "workspaces": [
    "packages/*"
  ],
  "scripts": {
    "dev": "pnpm -r --parallel run dev",
    "build": "pnpm -r run build",
    "test": "pnpm -r run test",
    "lint": "pnpm -r run lint"
  }
}
EOF

# Install root dependencies
pnpm install
```

### Step 4: Set Up Docker Services

```bash
# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8000:8000"
    volumes:
      - chroma_data:/chroma/chroma
    environment:
      - ANONYMIZED_TELEMETRY=False

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

  postgres:
    image: postgres:16-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=cheetah_v3
      - POSTGRES_USER=cheetah
      - POSTGRES_PASSWORD=cheetah_dev_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  chroma_data:
  redis_data:
  postgres_data:
EOF

# Start services
docker-compose up -d

# Verify services are running
docker-compose ps
```

### Step 5: Create Configuration Files

```bash
# Create .env file (don't commit this!)
cat > .env << EOF
# LLM API Keys
GEMINI_API_KEY=your_gemini_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Database URLs
CHROMADB_URL=http://localhost:8000
REDIS_URL=redis://localhost:6379
POSTGRES_URL=postgresql://cheetah:cheetah_dev_password@localhost:5432/cheetah_v3

# Development Settings
DEBUG=true
LOG_LEVEL=DEBUG
EOF

# Create .env.example (safe to commit)
cp .env .env.example
# Edit .env.example to replace actual keys with placeholders

# Add .env to .gitignore
echo ".env" >> .gitignore
echo "venv/" >> .gitignore
echo "node_modules/" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo ".pytest_cache/" >> .gitignore
echo "dist/" >> .gitignore
echo "build/" >> .gitignore
```

### Step 6: Set Up CI/CD Pipeline

```bash
# Create GitHub Actions workflow
mkdir -p .github/workflows

cat > .github/workflows/ci.yml << 'EOF'
name: CI

on: [push, pull_request]

jobs:
  test-python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install Poetry
        run: pip install poetry
      - name: Install dependencies
        run: |
          cd packages/core
          poetry install
      - name: Run tests
        run: |
          cd packages/core
          poetry run pytest --cov --cov-report=xml
      - name: Lint
        run: |
          cd packages/core
          poetry run ruff check .
          poetry run black --check .
          poetry run mypy .

  test-node:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - uses: pnpm/action-setup@v2
        with:
          version: 8
      - name: Install dependencies
        run: pnpm install
      - name: Run tests
        run: pnpm test
      - name: Lint
        run: pnpm lint
EOF
```

## Phase 1: Build Context Manager (Week 1-2)

### Day 2: Core Package Structure

```bash
cd packages/core

# Create package structure
mkdir -p cheetah_v3/{context,models,validation,workflow,git_ops,api}
touch cheetah_v3/__init__.py
touch cheetah_v3/context/__init__.py
touch cheetah_v3/models/__init__.py
touch cheetah_v3/validation/__init__.py
touch cheetah_v3/workflow/__init__.py
touch cheetah_v3/git_ops/__init__.py
touch cheetah_v3/api/__init__.py

# Create tests directory
mkdir -p tests/{context,models,validation,workflow,git_ops,api}
touch tests/__init__.py
```

### Day 3: Context Manager - File Watcher

```bash
# Create context_manager.py
cat > cheetah_v3/context/context_manager.py << 'EOF'
"""Context Manager for codebase understanding."""

from pathlib import Path
from typing import List, Optional, Dict, Any
import asyncio
from dataclasses import dataclass
import chromadb
from sentence_transformers import SentenceTransformer
import tree_sitter
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


@dataclass
class CodeContext:
    """Represents a piece of code context."""
    
    content: str
    file_path: str
    start_line: int
    end_line: int
    type: str  # function, class, module, etc.
    metadata: Dict[str, Any]
    relevance_score: float = 0.0


class ContextManager:
    """Manages codebase context and retrieval."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.chroma_client = chromadb.HttpClient(host='localhost', port=8000)
        self.collection = self.chroma_client.get_or_create_collection(
            name="codebase_context"
        )
        
    async def index_codebase(self, force_reindex: bool = False):
        """Index entire codebase."""
        print(f"Indexing codebase at {self.project_root}...")
        
        # TODO: Implement file discovery and parsing
        # TODO: Generate embeddings
        # TODO: Store in ChromaDB
        
        pass
    
    async def retrieve_relevant_context(
        self,
        query: str,
        max_results: int = 10,
        filters: Optional[Dict] = None
    ) -> List[CodeContext]:
        """Retrieve most relevant code snippets for query."""
        
        # Generate query embedding
        query_embedding = self.embedder.encode([query])[0]
        
        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=max_results
        )
        
        # Convert to CodeContext objects
        contexts = []
        # TODO: Parse results and create CodeContext objects
        
        return contexts
    
    async def update_file(self, file_path: str):
        """Update index for specific file."""
        # TODO: Implement incremental update
        pass


class CodebaseWatcher(FileSystemEventHandler):
    """Watches for file changes and triggers updates."""
    
    def __init__(self, context_manager: ContextManager):
        self.context_manager = context_manager
    
    def on_modified(self, event):
        if not event.is_directory:
            # Trigger update asynchronously
            asyncio.create_task(
                self.context_manager.update_file(event.src_path)
            )
EOF

# Create test file
cat > tests/context/test_context_manager.py << 'EOF'
"""Tests for Context Manager."""

import pytest
from pathlib import Path
from cheetah_v3.context.context_manager import ContextManager, CodeContext


@pytest.fixture
def context_manager(tmp_path):
    """Create a context manager for testing."""
    return ContextManager(project_root=str(tmp_path))


@pytest.mark.asyncio
async def test_context_manager_initialization(context_manager):
    """Test that context manager initializes correctly."""
    assert context_manager.project_root.exists()
    assert context_manager.embedder is not None
    assert context_manager.chroma_client is not None


@pytest.mark.asyncio
async def test_retrieve_relevant_context(context_manager):
    """Test retrieving relevant context."""
    # First index some code
    await context_manager.index_codebase()
    
    # Then retrieve
    contexts = await context_manager.retrieve_relevant_context(
        query="create a user class",
        max_results=5
    )
    
    assert isinstance(contexts, list)
    assert all(isinstance(c, CodeContext) for c in contexts)


@pytest.mark.asyncio
async def test_update_file(context_manager, tmp_path):
    """Test updating a single file."""
    # Create a test file
    test_file = tmp_path / "test.py"
    test_file.write_text("def hello(): pass")
    
    # Update it
    await context_manager.update_file(str(test_file))
    
    # Verify it's in the index
    # TODO: Add assertion
EOF
```

### Day 4: Run First Tests

```bash
# Run tests
cd packages/core
poetry run pytest -v

# Run linting
poetry run ruff check .
poetry run black .
poetry run mypy .

# Run with coverage
poetry run pytest --cov=cheetah_v3 --cov-report=html
```

## Quick Command Reference

### Development Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Run Python tests
cd packages/core && poetry run pytest

# Run Node tests
pnpm test

# Lint Python code
cd packages/core && poetry run ruff check . && poetry run black .

# Lint JavaScript/TypeScript
pnpm lint

# Build all packages
pnpm build

# Run development servers
pnpm dev
```

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/context-manager

# Commit with conventional commits
git commit -m "feat(context): implement basic context manager"

# Push and create PR
git push origin feature/context-manager
```

## Next Steps Checklist

- [ ] Complete Phase 0 setup (Day 1)
- [ ] Implement Context Manager foundation (Days 2-4)
- [ ] Write tests for Context Manager (Day 5)
- [ ] Implement file parsing with tree-sitter (Week 2)
- [ ] Integrate ChromaDB fully (Week 2)
- [ ] Add caching layer with Redis (Week 2)
- [ ] Benchmark performance (Week 2)
- [ ] Move to Model Orchestrator (Week 3)

## Troubleshooting

### ChromaDB Not Starting
```bash
docker-compose logs chromadb
# If port conflict, change port in docker-compose.yml
```

### Poetry Dependencies Conflict
```bash
poetry lock --no-update
poetry install
```

### Tests Failing
```bash
# Run with verbose output
poetry run pytest -vv

# Run specific test
poetry run pytest tests/context/test_context_manager.py::test_name -v
```

## Resources

- **Full Documentation**: See `V3_DESIGN_SPEC.md`
- **Roadmap**: See `IMPLEMENTATION_ROADMAP.md`
- **Architecture**: See `BUILDS_ANALYSIS.md`
- **Marketing**: See `MARKETING_STRATEGY.md`

## Support

If you encounter issues:
1. Check the comprehensive documentation
2. Review error messages and logs
3. Search GitHub issues
4. Create new issue with details

---

**Remember**: Start small, test often, iterate quickly. Build the Context Manager first, validate it works, then move to the next component. Don't try to build everything at once.

**Good luck building the ultimate autocoder! 🚀**
