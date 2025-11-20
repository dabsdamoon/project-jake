#!/bin/bash
# JAKE API Server Startup Script (Conda Version)

# Default port
PORT="${1:-8000}"

echo "🚀 Starting JAKE API Server..."
echo "📍 Port: $PORT"
echo ""

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo "❌ Conda is not installed!"
    echo "Please install Miniconda or Anaconda first:"
    echo "  https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "📝 Creating from .env.example..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo ""
    echo "❗ IMPORTANT: Edit .env and add your OPENAI_API_KEY"
    echo "   Run: nano .env"
    echo ""
    read -p "Press Enter after you've added your API key..."
fi

# Check if conda environment exists
if ! conda env list | grep -q "^jake "; then
    echo "📦 Creating conda environment 'jake'..."
    conda env create -f environment.yml
    echo "✅ Conda environment created!"
else
    echo "✅ Conda environment 'jake' already exists"
fi

# Activate conda environment
echo "🔧 Activating conda environment..."
eval "$(conda shell.bash hook)"
conda activate jake

# Update dependencies (in case environment.yml changed)
echo "📚 Updating dependencies..."
conda env update -f environment.yml --prune

# Initialize database
echo "🗄️  Initializing database..."
python -c "from src.database.connection import init_db; init_db()" 2>/dev/null || echo "Database already initialized"

echo ""
echo "✅ Setup complete!"
echo ""
echo "📡 Starting server on http://localhost:$PORT"
echo "📖 API Docs will be available at http://localhost:$PORT/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
uvicorn src.main:app --host 0.0.0.0 --port $PORT
