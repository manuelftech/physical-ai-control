from pathlib import Path
import structlog
logger = structlog.get_logger()

def read_file(file_path):
    lambda_root_path = Path(__file__).resolve().parent.parent
    try:
        absolute_path = lambda_root_path.joinpath(file_path).resolve()
        return Path(absolute_path).read_text(encoding="utf-8")
    except FileNotFoundError as e:
        logger.error("File not found. %s", file_path)
        raise e
