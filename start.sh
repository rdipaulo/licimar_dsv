#!/bin/bash
# Quick start script for Licimar MVP
# Usage: ./start.sh OR python start.py (Windows)

if [ "$(uname)" == "Darwin" ]; then
    # macOS
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    # Linux
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
elif [ "$(expr substr $(uname -s) 1 10)" == "MINGW32_NT" ] || [ "$(expr substr $(uname -s) 1 10)" == "MINGW64_NT" ]; then
    # Windows
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
fi

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║      LICIMAR MVP - Quick Start                       ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════╝${NC}\n"

# Check if both terminals needed
echo -e "${YELLOW}Este script abrirá 2 terminais:${NC}"
echo -e "  1. Backend (Python/Flask) na porta 5000"
echo -e "  2. Frontend (React/Vite) na porta 5173\n"

# Backend
echo -e "${GREEN}Iniciando Backend...${NC}"
cd "$SCRIPT_DIR/backend/licimar_mvp_app"
if [ "$(uname)" == "Darwin" ]; then
    open -a Terminal
    python app.py
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    gnome-terminal -- bash -c "cd '$SCRIPT_DIR/backend/licimar_mvp_app'; python app.py; read"
else
    # Windows
    start python app.py
fi

sleep 3

# Frontend
echo -e "${GREEN}Iniciando Frontend...${NC}"
cd "$SCRIPT_DIR/frontend/licimar_mvp_frontend"
if [ "$(uname)" == "Darwin" ]; then
    open -a Terminal
    npm run dev -- --host
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    gnome-terminal -- bash -c "cd '$SCRIPT_DIR/frontend/licimar_mvp_frontend'; npm run dev -- --host; read"
else
    # Windows
    start npm run dev -- --host
fi

echo -e "\n${GREEN}✓ Aplicação iniciada!${NC}"
echo -e "${BLUE}Acesse:${NC} http://localhost:5173\n"
echo -e "${YELLOW}Credenciais:${NC}"
echo -e "  Admin: admin / admin123"
echo -e "  Operador: operador / operador123\n"
