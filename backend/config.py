import logging
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("daton")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/daton.db")
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "daton")

CHROMA_PERSIST_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "chroma")
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "uploads")
DATASETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "datasets")
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

ALLOWED_DOC_EXTENSIONS = {".pdf", ".txt", ".docx", ".csv"}
ALLOWED_DATASET_EXTENSIONS = {".csv", ".xlsx", ".xls"}
MAX_FILE_SIZE_MB = 50

SQL_BLOCKED_KEYWORDS = {"DROP", "DELETE", "TRUNCATE", "ALTER", "UPDATE", "INSERT", "CREATE", "GRANT", "REVOKE"}
