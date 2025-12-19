# src/api/routes.py  (añade imports y el nuevo endpoint)
from fastapi import APIRouter, HTTPException, BackgroundTasks
from googleapiclient.errors import HttpError
from src.api.schemas import ProcessRequest, ProcessResponse, ProcessRequestPDF
from src.services.processing import process_documents
from src.services.pdf_processing import process_pdf_documents
from src.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

@router.post("/process")
async def process_endpoint(payload: ProcessRequest, background_tasks: BackgroundTasks):
    """
    Endpoint asíncrono que inicia la auditoría de documentos en segundo plano.
    """
    try:
        # Iniciamos la tarea en segundo plano
        background_tasks.add_task(
            process_documents,
            system_instructions_doc_id=payload.system_instructions_doc_id,
            base_prompt_doc_id=payload.base_prompt_doc_id,
            input_doc_id=payload.input_doc_id,
            output_doc_id=payload.output_doc_id,
            additional_params=payload.additional_params,
        )
        
        return {
            "status": "accepted",
            "message": "Proceso de auditoría iniciado en segundo plano. El resultado aparecerá en el documento de salida una vez finalizado.",
            "output_doc_link": f"https://docs.google.com/document/d/{payload.output_doc_id}/edit"
        }
    except Exception as e:
        logger.error(f"Error al encolar tarea de procesamiento: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process-pdf")
async def process_pdf_endpoint(payload: ProcessRequestPDF, background_tasks: BackgroundTasks):
    """
    Endpoint asíncrono que inicia la auditoría de PDF en segundo plano.
    """
    try:
        background_tasks.add_task(
            process_pdf_documents,
            system_instructions_doc_id=payload.system_instructions_doc_id,
            base_prompt_doc_id=payload.base_prompt_doc_id,
            pdf_url=payload.pdf_url,
            output_doc_id=payload.output_doc_id,
            drive_file_id=payload.drive_file_id,
            additional_params=payload.additional_params,
        )
        
        return {
            "status": "accepted",
            "message": "Proceso de PDF iniciado en segundo plano.",
            "output_doc_link": f"https://docs.google.com/document/d/{payload.output_doc_id}/edit"
        }
    except Exception as e:
        logger.error(f"Error al encolar tarea de PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))