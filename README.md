# Proxy Inteligente para Generación de Pruebas Unitarias

Este proyecto es una aplicación "Proxy Inteligente" diseñada para actuar como intermediario entre un cliente y un motor de inferencia (LLM) local a través de Ollama. Su objetivo principal es transformar funciones de código crudo en pruebas unitarias funcionales, estructuradas y deterministas.

## Funcionalidades

- **Transformación de Código**: Convierte funciones en múltiples lenguajes (Python, Java, JavaScript, etc.) en pruebas unitarias.
- **Paradigma DOP**: Implementación basada en Programación Orientada a Datos utilizando estructuras inmutables.
- **Inyección de System Prompt**: Configuración optimizada para forzar al modelo a devolver exclusivamente código fuente.
- **Validación Robusta**: Verificación estricta de entrada (campos vacíos) y de salida (coherencia de código).
- **Observabilidad**: Sistema de logs en consola con timestamp, lenguaje, latencia y estatus.

## Tecnologías Usadas

- **Backend**: [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **Servidor ASGI**: [Uvicorn](https://www.uvicorn.org/)
- **Cliente HTTP**: [HTTPX](https://www.python-httpx.org/) (Asíncrono)
- **Validación de Datos**: [Pydantic V2](https://docs.pydantic.dev/) (Modelos inmutables)
- **Motor de Inferencia**: [Ollama](https://ollama.com/) (Modelo Qwen 2.5 Coder 1.5B)
- **Pruebas**: [Pytest](https://docs.pytest.org/)

## Requisitos

1.  Python 3.10+
2.  Ollama instalado y corriendo.
3.  Modelo descargado: `ollama pull qwen2.5-coder:1.5b`

## Instalación y Uso

1.  **Clonar el repositorio**:
    ```bash
    git clone <url-del-repositorio>
    cd examenIAII
    ```

2.  **Configurar el entorno virtual**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Ejecutar la aplicación**:
    ```bash
    python main.py
    ```

4.  **Ejemplo de Petición (cURL)**:
    ```bash
    curl -X POST http://localhost:8000/generate-test \
         -H "Content-Type: application/json" \
         -d '{
               "lenguaje": "Python",
               "codigo": "def sumar(a, b): return a + b"
             }'
    ```

## Formato de Logs

El servidor imprimirá en consola cada petición con el siguiente formato:
`Timestamp | Lenguaje | Latencia (ms) | Status`

## Manejo de Errores

- **Error 400/422**: Petición mal formada o campos vacíos.
- **Error 500**: Fallo en la comunicación con Ollama, timeout del modelo o respuesta no coherente.
