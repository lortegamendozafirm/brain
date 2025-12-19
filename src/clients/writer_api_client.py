import requests
from src.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


def send_to_writer_service(document_id: str, markdown_content: str) -> bool:
    """
    Envía el contenido procesado al microservicio externo de escritura.
    """
    payload = {
        "markdown_content": markdown_content,
        "document_id": document_id
    }
    
    try:
        logger.info(f"📡 Enviando contenido a Writer Service para el doc: {document_id}")
        response = requests.post(settings.writer_service_url, json=payload, timeout=300)
        
        if response.status_code == 200:
            logger.info("✅ Microservicio de escritura respondió exitosamente.")
            return True
        else:
            logger.error(f"❌ Error en Writer Service: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error de conexión con Writer Service: {str(e)}")
        return False