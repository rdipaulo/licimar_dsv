from src.main import create_app
from src.database import db
from src.models import Ambulante

app = create_app()
app.app_context().push()

# Query ambulantes
ambulantes = Ambulante.query.all()
print(f"Total ambulantes: {len(ambulantes)}")

for amb in ambulantes:
    print(f"\n{amb.nome}")
    print(f"  ID: {amb.id}")
    print(f"  Status: {amb.status}")
    print(f"  Divida: {amb.divida_acumulada} (type: {type(amb.divida_acumulada)})")
    
    # Try to convert to dict
    try:
        data = amb.to_dict()
        print(f"  to_dict() SUCCESS: {data}")
    except Exception as e:
        print(f"  to_dict() ERROR: {e}")
