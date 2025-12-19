# src/settings.py
from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración central del proyecto brain/"""

    # ✅ Config v2: aquí defines .env y qué hacer con extras
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",          # ignora variables en .env que no estén como campo
        # case_sensitive=False   # por defecto; GCP_PROJECT_ID se mapea a gcp_project_id
    )

    # --- Identidad del proyecto ---
    gcp_project_id: str
    gcp_location: str = "us-central1"

    # --- Cuenta de servicio ---
    sa_email: Optional[str] = None
    google_application_credentials: Optional[str] = None
    dwd_subject: Optional[str] = None

    # --- Vertex AI ---
    vertex_model_id: str = "gemini-2.5-flash"

    # --- Google Workspace / Drive ---
    shared_folder_id: Optional[str] = None
    existing_doc_id: Optional[str] = None
    existing_sheet_id: Optional[str] = None
    doc_name: Optional[str] = None
    sheet_name: Optional[str] = None

    # --- Sistema / Logs ---
    log_level: str = "INFO"
    environment: str = "local"

    # --- PDFs ---
    pdf_staging_bucket: Optional[str] = None
    pdf_max_pages_per_chunk: int = 60
    pdf_use_file_api: bool = True

    # --- Nuevos campos que vienen en tu .env ---
    docs_text_chunk: int = 50_000
    docs_text_chunk_sleep_ms: int = 150
    app_version: str = "dev"

    # --- URL del endpoint del servicio que pasa de markdown to google docs
    writer_service_url: str = "https://m2gdw-223080314602.us-central1.run.app/api/v1/write"

    # --- Helpers de conveniencia ---
    @property
    def use_adc(self) -> bool:
        """Detecta si se debe usar ADC (auth de Cloud Run o gcloud local)."""
        return not bool(self.google_application_credentials)

    @property
    def vertex_model(self) -> str:
        """Devuelve el modelo Vertex AI activo."""
        return self.vertex_model_id or "gemini-2.5-flash"

    @property
    def is_local(self) -> bool:
        """Retorna True si se ejecuta fuera de Cloud Run."""
        return self.environment.lower() in ("local", "dev", "development")


@lru_cache()
def get_settings() -> Settings:
    """Caché global de configuración."""
    return Settings()


# Instancia singleton
settings = get_settings()

if __name__ == "__main__":
    s = get_settings()
    print("gcp_project_id:", s.gcp_project_id)
    print("gcp_location:", s.gcp_location)
    print("sa_email:", s.sa_email)
    print("google_application_credentials:", s.google_application_credentials)
    print("log_level:", s.log_level)
    print("vertex_model:", s.vertex_model)
    print("pdf_staging_bucket:", s.pdf_staging_bucket)
    print("docs_text_chunk:", s.docs_text_chunk)
    print("docs_text_chunk_sleep_ms:", s.docs_text_chunk_sleep_ms)
    print("app_version:", s.app_version)
    print("url_servicie_m2gd:", s.writer_service_url)
