import os
import requests
from dotenv import load_dotenv
from app.core.logger import get_logger
from fastapi import HTTPException

# LangSmith 추적을 위한 LangChain import
try:
    from langchain_upstage import ChatUpstage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logger = get_logger(__name__)
    logger.warning("langchain-upstage not available, LangSmith tracing will not work")

load_dotenv()
logger = get_logger(__name__)

class UpstageService:
    """
    Upstage API와 상호작용하는 서비스 클래스입니다.
    Solar Pro (LLM), Document Parse (OCR), Information Extraction 기능을 제공합니다.
    """

    def __init__(self):
        """Upstage API 키를 로드하고 LangChain ChatUpstage를 초기화합니다."""
        self.api_key = os.getenv("UPSTAGE_API_KEY")
        if not self.api_key:
            logger.warning("UPSTAGE_API_KEY is not set in environment variables. Upstage API calls will fail.")

        self.headers_base = {
            "Authorization": f"Bearer {self.api_key}",
        }

        # LangSmith 추적을 위한 ChatUpstage 초기화
        if LANGCHAIN_AVAILABLE and self.api_key:
            try:
                self.chat_upstage = ChatUpstage(
                    api_key=self.api_key,
                    model="solar-pro"
                )
                logger.info("ChatUpstage initialized for LangSmith tracing")
            except Exception as e:
                logger.error(f"Failed to initialize ChatUpstage: {e}")
                self.chat_upstage = None
        else:
            self.chat_upstage = None

    def _get_headers(self, content_type: str = None):
        """
        API 요청에 사용할 헤더를 생성합니다.

        Args:
            content_type: Content-Type 헤더 값 (선택)

        Returns:
            HTTP 헤더 딕셔너리
        """
        if not self.api_key:
            raise HTTPException(status_code=500, detail="Upstage API Key is not configured. Please set UPSTAGE_API_KEY in .env file.")

        headers = self.headers_base.copy()
        if content_type:
            headers["Content-Type"] = content_type
        return headers

    def solar_pro(self, messages):
        """
        Solar Pro LLM을 호출합니다.
        LangChain을 통해 호출하여 LangSmith 추적을 지원하며,
        실패 시 직접 API 호출로 폴백합니다.

        Args:
            messages: OpenAI 형식의 메시지 리스트
                      [{"role": "system|user|assistant", "content": "..."}]

        Returns:
            OpenAI 호환 형식의 응답 딕셔너리
        """
        # LangChain이 사용 가능한 경우 LangSmith 추적과 함께 호출
        if self.chat_upstage:
            try:
                from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

                # OpenAI 형식 메시지를 LangChain 형식으로 변환
                lc_messages = []
                for msg in messages:
                    role = msg.get("role")
                    content = msg.get("content")
                    if role == "system":
                        lc_messages.append(SystemMessage(content=content))
                    elif role == "user":
                        lc_messages.append(HumanMessage(content=content))
                    elif role == "assistant":
                        lc_messages.append(AIMessage(content=content))

                # ChatUpstage 호출 (LangSmith에서 추적됨)
                logger.info(f"Calling Solar Pro via LangChain with {len(lc_messages)} messages")
                response = self.chat_upstage.invoke(lc_messages)

                # LangChain 응답을 OpenAI 형식으로 변환하여 호환성 유지
                return {
                    "choices": [
                        {
                            "message": {
                                "content": response.content,
                                "role": "assistant"
                            }
                        }
                    ]
                }
            except Exception as e:
                logger.error(f"LangChain call failed, falling back to direct API: {e}")
                # 직접 API 호출로 폴백

        # LangChain 사용 불가 또는 실패 시 직접 API 호출
        headers = self._get_headers("application/json")
        url = "https://api.upstage.ai/v1/solar/chat/completions"
        data = {
            "model": "solar-pro3-260126",
            "messages": messages
        }
        response = requests.post(url, headers=headers, json=data)
        logger.info(f"Solar Pro API Response Status: {response.status_code}, Body: {response.text}")
        response.raise_for_status()
        return response.json()

    def document_parse(self, file_path):
        """
        Document Parse API를 사용하여 문서(명함, PDF 등)에서 텍스트를 추출합니다.

        Args:
            file_path: 파싱할 문서 파일 경로

        Returns:
            파싱 결과 JSON (elements 리스트 포함)
        """
        headers = self._get_headers()  # requests가 multipart/form-data 헤더를 자동으로 설정
        url = "https://api.upstage.ai/v1/document-digitization"
        files = {'document': open(file_path, 'rb')}
        data = {"ocr": "force", "model": "document-parse"}

        response = requests.post(url, headers=headers, files=files, data=data)
        logger.info(f"Document Digitization API Response Status: {response.status_code}, Body: {response.text}")
        response.raise_for_status()
        return response.json()

    def information_extraction(self, document_id):
        """
        Information Extraction API를 사용하여 문서에서 구조화된 정보를 추출합니다.

        Args:
            document_id: Document Parse API에서 반환된 문서 ID

        Returns:
            추출된 정보 JSON
        """
        headers = self._get_headers()
        url = f"https://api.upstage.ai/v1/document-ai/information-extraction/{document_id}"
        response = requests.get(url, headers=headers)
        logger.info(f"Information Extraction API Response Status: {response.status_code}, Body: {response.text}")
        response.raise_for_status()
        return response.json()


# Upstage 서비스 싱글톤 인스턴스
# UPSTAGE_API_KEY 환경 변수가 설정되어 있을 때만 생성
upstage_service = None
if os.getenv("UPSTAGE_API_KEY"):
    try:
        upstage_service = UpstageService()
    except Exception as e:
        logger.error(f"Failed to initialize UpstageService: {e}")
        upstage_service = None