import os

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}

def validate_uploaded_file(file) -> tuple[bool, str | None]:
    """Validates file format and size boundaries prior to chunking and storage."""
    name = file.name
    ext = os.path.splitext(name)[1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        return False, f"File '{name}' has unsupported format '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"

    if file.size > MAX_FILE_SIZE_BYTES:
        size_mb = file.size / (1024 * 1024)
        return False, f"File '{name}' exceeds 10MB limit ({size_mb:.2f} MB)."

    return True, None