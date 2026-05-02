import pytest
from fastapi.testclient import TestClient
from main import app, CodeRequest, InboundLogData
from pydantic import ValidationError
import json

client = TestClient(app)

def test_validate_input_empty_fields():
    """Prueba que el backend rechace peticiones con campos vacíos."""
    # Pydantic V2 raises 422 for min_length validation
    response = client.post("/generate-test", json={"lenguaje": "", "codigo": ""})
    assert response.status_code == 422

def test_validate_input_invalid_json():
    """Prueba que el backend rechace un body inválido."""
    response = client.post("/generate-test", content="invalid json")
    assert response.status_code == 422

def test_dop_immutability():
    """Verifica que las estructuras de datos sean inmutables (DOP)."""
    # Test Pydantic frozen
    req = CodeRequest(lenguaje="Python", codigo="def add(a,b): return a+b")
    with pytest.raises(ValidationError):
        req.lenguaje = "Java"
    
    # Test Dataclass frozen
    log = InboundLogData(timestamp="now", lenguaje="Python", latencia_ms=10.0, status="Éxito")
    with pytest.raises(AttributeError):
        log.status = "Fallo"

def test_error_handling_ollama_unavailable(monkeypatch):
    """Simula que Ollama no está disponible (Error 500)."""
    async def mock_call_ollama(*args, **kwargs):
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail="Error de conexión con Ollama")
    
    import main
    monkeypatch.setattr(main, "call_ollama", mock_call_ollama)
    
    response = client.post("/generate-test", json={"lenguaje": "Python", "codigo": "x=1"})
    assert response.status_code == 500
    assert "Error de conexión con Ollama" in response.json()["detail"]

if __name__ == "__main__":
    pytest.main([__file__])
