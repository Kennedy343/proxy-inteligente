import time
import logging
import httpx
from datetime import datetime
from dataclasses import dataclass
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ConfigDict

# 1. Configuración de Logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("proxy-logger")

# 2. Estructuras de Datos Inmutables (Paradigma DOP)
class CodeRequest(BaseModel):
    model_config = ConfigDict(frozen=True)  # Inmutabilidad en Pydantic V2
    
    lenguaje: str = Field(..., min_length=1)
    codigo: str = Field(..., min_length=1)

@dataclass(frozen=True)
class InboundLogData:
    timestamp: str
    lenguaje: str
    latencia_ms: float
    status: str

# 3. Aplicación FastAPI
app = FastAPI(title="Proxy Inteligente de Pruebas Unitarias")

OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"
DEFAULT_MODEL = "qwen2.5-coder:1.5b"
TIMEOUT = 300.0

async def call_ollama(lenguaje: str, codigo: str):
    system_prompt = (
        f"Eres un experto ingeniero de software especializado en pruebas de código. "
        f"Tu única tarea es recibir una función y devolver una prueba unitaria válida para ella. "
        f"1. Identifica la librería de pruebas estándar apropiada para el lenguaje {lenguaje}. "
        f"2. DEBES devolver ÚNICAMENTE el código fuente de la prueba. Nada de texto introductorio, "
        f"ni explicaciones, ni saludos, ni formato markdown fuera del bloque de código. Solo código."
    )
    
    prompt = f"Lenguaje: {lenguaje}\nCódigo:\n{codigo}"
    
    payload = {
        "model": DEFAULT_MODEL,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False,
        "options": {
            "temperature": 0.0
        }
    }

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            response = await client.post(OLLAMA_API_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()
        except httpx.TimeoutException:
            raise HTTPException(status_code=500, detail="Timeout: El modelo de inferencia tardó demasiado en responder.")
        except httpx.RequestError as exc:
            raise HTTPException(status_code=500, detail=f"Error de conexión con Ollama: {exc}")

def validate_output(response_text: str) -> bool:
    """Verificación básica de coherencia de código."""
    test_keywords = ["import", "test", "assert", "expect", "require", "def ", "class ", "public class"]
    content_lower = response_text.lower()
    has_keywords = any(kw in content_lower for kw in test_keywords)
    is_not_empty = len(response_text) > 20
    return has_keywords and is_not_empty

@app.post("/generate-test")
async def generate_test(test_req: CodeRequest):
    start_time = time.time()
    status = "Fallo"
    
    try:
        if not test_req.lenguaje.strip() or not test_req.codigo.strip():
            status = "Fallo"
            raise HTTPException(status_code=400, detail="Los campos 'lenguaje' y 'codigo' no pueden estar vacíos.")

        raw_response = await call_ollama(test_req.lenguaje, test_req.codigo)
        
        clean_response = raw_response
        if "```" in raw_response:
            parts = raw_response.split("```")
            if len(parts) >= 3:
                clean_response = parts[1].split("\n", 1)[-1] if "\n" in parts[1] else parts[1]
            else:
                clean_response = raw_response.replace("```", "").strip()

        if not validate_output(clean_response):
            status = "Fallo"
            raise HTTPException(status_code=500, detail="La respuesta del modelo no parece ser un código de prueba válido.")

        status = "Éxito"
        return {"prueba_unitaria": clean_response.strip()}

    except HTTPException as he:
        raise he
    except Exception as e:
        status = "Fallo"
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")
    
    finally:
        end_time = time.time()
        latencia = (end_time - start_time) * 1000
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {test_req.lenguaje} | {round(latencia, 2)} ms | {status}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
