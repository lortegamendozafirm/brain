# src/services/processing.py
from __future__ import annotations
from typing import Dict, Any

from src.clients.gdocs_client import (
    get_document_content,
    write_to_document,
    write_markdown_to_document,
)
from src.clients.vertex_client import generate_text
from src.utils.logger import get_logger
from src.clients.drive_client import assert_sa_has_access

logger = get_logger(__name__)


def build_prompt(
    system_text: str,
    base_prompt: str,
    input_text: str,
    params: Dict[str, Any],
) -> str:
    prompt = []
    if system_text.strip():
        prompt.append(f"[SYSTEM]\n{system_text.strip()}\n")
    if base_prompt.strip():
        prompt.append(f"[PROMPT_BASE]\n{base_prompt.strip()}\n")
    if input_text.strip():
        prompt.append(f"[INPUT]\n{input_text.strip()}\n")
    if params:
        prompt.append(f"[PARAMS]\n{params}\n")
    return "\n".join(prompt).strip()


def process_documents(
    *,
    system_instructions_doc_id: str,
    base_prompt_doc_id: str,
    input_doc_id: str,
    output_doc_id: str,
    additional_params: Dict[str, Any] = {},
) -> dict:
    """
    1) Lee system/base/input
    2) Prompt
    3) Vertex
    4) Escribe resultado (Markdown nativo si render_markdown = True)
    5) JSON
    """
    logger.info("🚀 Iniciando proceso de IA (Docs → Gemini → Doc)...")

    for fid in (
        system_instructions_doc_id,
        base_prompt_doc_id,
        input_doc_id,
        output_doc_id,
    ):
        assert_sa_has_access(fid)

    system_text = get_document_content(system_instructions_doc_id)
    base_prompt = get_document_content(base_prompt_doc_id)
    input_text = get_document_content(input_doc_id)

    params = additional_params or {}
    logger.info(f"🧩 additional_params recibido: {params!r}")

    full_prompt = build_prompt(system_text, base_prompt, input_text, params)
    logger.info("🧠 Prompt ensamblado. Solicitando respuesta al modelo...")

    ai_output = generate_text(full_prompt) or ""
    logger.info(f"📏 Longitud de salida del modelo: {len(ai_output)} caracteres")

    # === Selector de writer (con logs) ===
    render_flag = params.get("render_markdown", None)

    # Si viene explícito en el JSON, respétalo.
    # Si NO viene, puedes decidir el default (aquí lo dejamos en False para no romper flujo actual).
    if render_flag is None:
        render_md = False
    else:
        render_md = bool(render_flag)

    list_policy = (params.get("list_policy") or "auto").lower()
    clear_before_write = bool(params.get("clear_before_write", True))

    logger.info(
        f"✏️ Writer seleccionado: "
        f"{'markdown→nativo' if render_md else 'texto plano'} | "
        f"list_policy={list_policy!r} | clear_before_write={clear_before_write}"
    )

    if render_md:
        write_markdown_to_document(
            output_doc_id,
            ai_output,
            clear_before_write=clear_before_write,
            list_policy=list_policy,
        )
    else:
        write_to_document(output_doc_id, ai_output)

    output_link = f"https://docs.google.com/document/d/{output_doc_id}/edit"
    logger.info(f"✅ Proceso completado. Output en: {output_link}")
    return {
        "status": "success",
        "message": "El resultado de la IA fue escrito correctamente en el documento.",
        "output_doc_link": output_link,
    }
