import os
from dotenv import load_dotenv
from fastapi import FastAPI
from app.api import routes
from app.core.logger import get_logger

# 환경 변수 로드
load_dotenv()

logger = get_logger(__name__)

# LangSmith 추적 설정
langsmith_api_key = os.getenv("LANGSMITH_API_KEY", "")
langsmith_project = os.getenv("LANGSMITH_PROJECT", "business-network-graph")
tracing_enabled = os.getenv("LANGCHAIN_TRACING_V2", "true")

os.environ["LANGCHAIN_TRACING_V2"] = tracing_enabled
os.environ["LANGCHAIN_API_KEY"] = langsmith_api_key
os.environ["LANGCHAIN_PROJECT"] = langsmith_project

# LangSmith 설정 로깅
if tracing_enabled == "true" and langsmith_api_key:
    logger.info(f"LangSmith tracing enabled for project: {langsmith_project}")
else:
    logger.warning("LangSmith tracing is disabled or API key is missing")

app = FastAPI(
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@2.0.0-rc.69/bundles/redoc.standalone.js",
    swagger_ui_bundle_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.31.0/swagger-ui-bundle.js",
    swagger_ui_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.31.0/swagger-ui.css"
)

app.include_router(routes.router, prefix="/api")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/")
def read_root():
    return {"Hello": "World"}
