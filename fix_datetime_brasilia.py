#!/usr/bin/env python3
"""Substituir datetime.utcnow por get_brasilia_now"""
import re

models_file = "backend/licimar_mvp_app/src/models.py"

with open(models_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Substitui datetime.utcnow por get_brasilia_now
content = content.replace('default=datetime.utcnow', 'default=get_brasilia_now')
content = content.replace('onupdate=datetime.utcnow', 'onupdate=get_brasilia_now')

with open(models_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Todas as referências a datetime.utcnow foram substituídas por get_brasilia_now")
