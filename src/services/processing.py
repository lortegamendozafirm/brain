#src/services/processing.py
from __future__ import annotations
from typing import Dict, Any

from src.clients.gdocs_client import get_document_content
from src.clients.vertex_client import generate_text
from src.clients.writer_api_client import send_to_writer_service
from src.utils.logger import get_logger
from src.clients.drive_client import assert_sa_has_access

logger = get_logger(__name__)

def build_prompt(system_text: str, base_prompt: str, input_text: str, params: Dict[str, Any]) -> str:
    prompt = []
    if system_text.strip(): prompt.append(f"[SYSTEM]\n{system_text.strip()}\n")
    if base_prompt.strip(): prompt.append(f"[PROMPT_BASE]\n{base_prompt.strip()}\n")
    if input_text.strip(): prompt.append(f"[INPUT]\n{input_text.strip()}\n")
    if params: prompt.append(f"[PARAMS]\n{params}\n")
    return "\n".join(prompt).strip()


def process_documents(
    *,
    system_instructions_doc_id: str,
    base_prompt_doc_id: str,
    input_doc_id: str,
    output_doc_id: str,
    additional_params: Dict[str, Any] = {},
) -> dict:
    # Envolvemos todo en un try-except general para el log de fondo
    try:
        logger.info("🚀 [Fondo] Iniciando proceso de IA...")
        
        # 1. Validar accesos
        for fid in (system_instructions_doc_id, base_prompt_doc_id, input_doc_id, output_doc_id):
            assert_sa_has_access(fid)

        # 2. Leer contenidos
        system_text = get_document_content(system_instructions_doc_id)
        base_prompt = get_document_content(base_prompt_doc_id)
        input_text = get_document_content(input_doc_id)

        # 3. Prompt y Vertex
        full_prompt = build_prompt(system_text, base_prompt, input_text, additional_params)
        ai_output = generate_text(full_prompt) or ""
        
        if not ai_output:
            logger.error("❌ La IA no devolvió contenido.")
            return {"status": "error"}

        # 4. Enviar a Writer Service (Asegúrate de que el timeout en writer_api_client sea de 180s)
        success = send_to_writer_service(output_doc_id, ai_output)
        
        if success:
            logger.info(f"✅ Proceso completado con éxito para el doc: {output_doc_id}")
        else:
            logger.warning(f"⚠️ El Writer Service falló para el doc: {output_doc_id}")

    except Exception as e:
        logger.error(f"❌ Error crítico en la tarea de fondo: {str(e)}", exc_info=True)    