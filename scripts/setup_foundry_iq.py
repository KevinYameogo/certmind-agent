"""Verify CertMind knowledge documents for Foundry IQ ingestion."""

from __future__ import annotations

import os
from logging import getLogger
from pathlib import Path
from urllib.parse import urlparse

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - supports running before deps are installed
    def load_dotenv() -> bool:
        env_path = Path.cwd() / ".env"
        if not env_path.exists():
            return False
        for line in env_path.read_text(encoding="utf-8").splitlines():
            clean = line.strip()
            if not clean or clean.startswith("#") or "=" not in clean:
                continue
            key, value = clean.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
        return False


load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE_DOCS = (
    "cert_guide.md",
    "team_learning_report.md",
    "workload_insights.md",
)


def verify_local_docs() -> list[Path]:
    """Confirm the three markdown docs intended for Foundry IQ exist locally."""
    docs_dir = PROJECT_ROOT / "synthetic-data"
    missing = [name for name in KNOWLEDGE_DOCS if not (docs_dir / name).is_file()]
    if missing:
        raise FileNotFoundError(f"Missing knowledge docs: {', '.join(missing)}")
    return [docs_dir / name for name in KNOWLEDGE_DOCS]


def verify_blob_container() -> list[str] | None:
    """Optionally verify the uploaded docs in Azure Blob Storage."""
    account_url = os.getenv("AZURE_STORAGE_ACCOUNT_URL")
    container_name = os.getenv("AZURE_STORAGE_CONTAINER", "certmind-docs")

    if not account_url:
        print("Skipped Blob verification: AZURE_STORAGE_ACCOUNT_URL is not set.")
        return None

    account_url, container_name = _normalise_blob_settings(
        account_url=account_url,
        container_name=container_name,
    )

    try:
        from azure.identity import DefaultAzureCredential
        from azure.storage.blob import BlobServiceClient
    except ImportError as exc:
        raise RuntimeError(
            "Install azure-storage-blob to verify Azure Blob uploads: "
            "pip install azure-storage-blob"
        ) from exc

    try:
        getLogger("azure.identity").setLevel("CRITICAL")
        blob_service = BlobServiceClient(
            account_url=account_url,
            credential=DefaultAzureCredential(),
        )
        container = blob_service.get_container_client(container_name)
        blob_names = {blob.name for blob in container.list_blobs()}
    except Exception as exc:
        print("Skipped Blob verification: Azure authentication is not available locally.")
        print("To enable it, install Azure CLI and run `az login`, or sign in through VS Code Azure tools.")
        print(f"Blob verification detail: {exc.__class__.__name__}: {exc}")
        return None

    missing = [name for name in KNOWLEDGE_DOCS if name not in blob_names]
    if missing:
        raise FileNotFoundError(
            f"Container {container_name!r} is missing: {', '.join(missing)}"
        )
    return list(KNOWLEDGE_DOCS)


def _normalise_blob_settings(account_url: str, container_name: str) -> tuple[str, str]:
    """Support either a storage account URL or a full container URL."""
    parsed = urlparse(account_url)
    path_parts = [part for part in parsed.path.split("/") if part]
    if path_parts:
        container_name = path_parts[0]
        account_url = f"{parsed.scheme}://{parsed.netloc}"
    return account_url.rstrip("/"), container_name


def main() -> None:
    """Run local and optional Azure Blob verification."""
    local_docs = verify_local_docs()
    print("Local Foundry IQ knowledge docs:")
    for path in local_docs:
        print(f"  - {path.relative_to(PROJECT_ROOT)}")

    verified_blobs = verify_blob_container()
    if verified_blobs is not None:
        print("Azure Blob container contains:")
        for name in verified_blobs:
            print(f"  - {name}")

    kb_id = os.getenv("FOUNDRY_IQ_KNOWLEDGE_BASE_ID")
    if kb_id:
        print(f"Foundry IQ knowledge base configured: {kb_id}")
    else:
        print("FOUNDRY_IQ_KNOWLEDGE_BASE_ID is not set yet.")


if __name__ == "__main__":
    main()
