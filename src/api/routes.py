# src/api/routes.py  (añade imports y el nuevo endpoint)
from fastapi import APIRouter, HTTPException
from googleapiclient.errors import HttpError
from src.domain.schemas import ProcessRequest, ProcessResponse, ProcessRequestPDF
from src.services.processing import process_documents
from src.services.pdf_processing import process_pdf_documents

router = APIRouter()

@router.post("/process", response_model=ProcessResponse)
async def process_endpoint(payload: ProcessRequest) -> ProcessResponse:
    try:
        data = process_documents(
            system_instructions_doc_id=payload.system_instructions_doc_id,
            base_prompt_doc_id=payload.base_prompt_doc_id,
            input_doc_id=payload.input_doc_id,
            output_doc_id=payload.output_doc_id,
            additional_params=payload.additional_params,
        )
        return ProcessResponse(**data)
    except HttpError as e:
        detail = getattr(e, "error_details", None) or str(e)
        raise HTTPException(status_code=403, detail=f"Google API error: {detail}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process-pdf", response_model=ProcessResponse)
async def process_pdf_endpoint(payload: ProcessRequestPDF) -> ProcessResponse:
    try:
        data = process_pdf_documents(
            system_instructions_doc_id=payload.system_instructions_doc_id,
            base_prompt_doc_id=payload.base_prompt_doc_id,
            pdf_url=payload.pdf_url,
            output_doc_id=payload.output_doc_id,
            drive_file_id=payload.drive_file_id,
            additional_params=payload.additional_params,
        )
        return ProcessResponse(**data)
    except HttpError as e:
        status = getattr(e, "status_code", 500) or getattr(e.resp, "status", 500)
        detail = getattr(e, "error_details", None) or str(e)
        raise HTTPException(status_code=status, detail=f"Google API error: {detail}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
