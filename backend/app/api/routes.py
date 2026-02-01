import re
import shutil
import json
from datetime import datetime
from fastapi import APIRouter, File, UploadFile, HTTPException
from app.services.upstage import upstage_service
from app.services.neo4j_service import neo4j_service
from app.models.schemas import MemoInput, QueryInput, ContactInput
from app.core.logger import get_logger
import os

router = APIRouter()
logger = get_logger(__name__)

@router.post("/extract-business-card")
async def extract_business_card(file: UploadFile = File(...)):
    """
    명함 이미지 파일을 업로드하여 텍스트를 추출하고 구조화된 정보로 변환합니다.

    Args:
        file: 업로드된 명함 이미지 파일

    Returns:
        person_data: 추출된 인물 정보 (이름, 직함, 전화번호, 이메일)
        company_data: 추출된 회사 정보
    """
    temp_file_path = f"temp_{file.filename}"
    try:
        # 업로드된 파일을 임시 파일로 저장
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Document Parse API를 사용하여 명함 텍스트 추출
        parsed_document = upstage_service.document_parse(temp_file_path)

        # HTML 태그를 제거하고 순수 텍스트만 추출
        all_text_content = ""
        for element in parsed_document.get("elements", []):
            html_content = element.get("content", {}).get("html", "")
            text_content = re.sub(r'<[^>]+>', '', html_content).replace('<br>', '\n').strip()
            all_text_content += text_content + "\n"

        # LLM을 사용하여 명함 정보 구조화
        system_prompt = """You are an expert assistant that extracts key information from business card text.
        The user will provide the text content of a business card.
        Extract the following fields: name, title, company, phone, email.
        Handle various phone number formats including international ones like '82 10-0000-0000'.
        Return the output in a clean JSON format. For example:
        {
          "name": "김성길",
          "title": "과장",
          "company": "ABC상사",
          "phone": "010-2222-1234",
          "email": "kim@abc.com"
        }
        If a field is not found, omit it from the JSON. The name must be in Korean.
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": all_text_content.strip()}
        ]
        
        response = upstage_service.solar_pro(messages)
        logger.info(f"Solar Pro for BizCard Raw Response: {response}")

        try:
            extracted_data_content = response["choices"][0]["message"]["content"]

            # Markdown 코드 블록 제거 (```json 또는 ``` 감싸진 부분 파싱)
            if "```json" in extracted_data_content:
                start = extracted_data_content.find("```json") + len("```json")
                end = extracted_data_content.find("```", start)
                if end != -1:
                    extracted_data_content = extracted_data_content[start:end].strip()
            elif "```" in extracted_data_content:
                start = extracted_data_content.find("```") + len("```")
                end = extracted_data_content.find("```", start)
                if end != -1:
                    extracted_data_content = extracted_data_content[start:end].strip()

            extracted_data = json.loads(extracted_data_content)

            # 인물 정보 추출 (값이 있는 필드만 포함)
            person_data = {
                "name": extracted_data.get("name"),
                "title": extracted_data.get("title"),
                "phone": extracted_data.get("phone"),
                "email": extracted_data.get("email"),
            }
            person_data = {k: v for k, v in person_data.items() if v}

            # 회사 정보 추출
            company_data = {"name": extracted_data.get("company")} if extracted_data.get("company") else {}

        except (KeyError, IndexError, json.JSONDecodeError) as e:
            logger.error(f"Failed to parse LLM response for business card: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to extract information from business card using LLM.")

        return {"person_data": person_data, "company_data": company_data}
    finally:
        # 임시 파일 삭제
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@router.post("/save-contact")
async def save_contact(contact: ContactInput):
    """
    추출된 연락처 정보를 Neo4j 그래프 데이터베이스에 저장합니다.

    Args:
        contact: 인물 및 회사 정보를 포함하는 연락처 입력

    Returns:
        저장 성공 메시지
    """
    person_data = contact.person_data.dict()
    company_data = contact.company_data.dict() if contact.company_data else {}

    logger.info(f"Saving Person Data: {json.dumps(person_data, indent=2, ensure_ascii=False)}")
    logger.info(f"Saving Company Data: {json.dumps(company_data, indent=2, ensure_ascii=False)}")

    if person_data.get("name"):
        # 일관된 검색을 위해 이름에서 공백 제거
        person_data["name"] = person_data["name"].replace(" ", "")

        # Person 노드 생성 또는 업데이트
        neo4j_service.create_person(
            name=person_data["name"],
            properties={k: v for k, v in person_data.items() if k != "name"}
        )

        # 회사 정보가 있으면 Company 노드 생성 및 관계 설정
        if company_data.get("name"):
            neo4j_service.create_company(
                name=company_data["name"],
                properties={}
            )
            neo4j_service.create_relationship(
                from_node_label="Person",
                from_node_name=person_data["name"],
                to_node_label="Company",
                to_node_name=company_data["name"],
                relationship_type="WORKS_AT"
            )
        return {"status": "Contact successfully saved to Neo4j."}

    raise HTTPException(status_code=400, detail="Person name is required to save a contact.")

@router.post("/memo")
async def create_memo(memo_input: MemoInput):
    """
    메모 텍스트에서 엔티티와 관계를 추출하여 Neo4j에 저장합니다.

    Args:
        memo_input: 사용자가 입력한 메모 텍스트

    Returns:
        처리 상태 및 추출된 데이터
    """
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M")

    # LLM을 사용하여 메모에서 엔티티와 관계 추출
    messages = [
        {"role": "system", "content": f"""You are a helpful assistant that extracts entities and relationships from a given memo.
        The entities can be Person, Company, Event, Project.
        The relationships can be WORKS_AT, ATTENDED, DISCUSSED.

        IMPORTANT: Current date is {current_date} and current time is {current_time}.
        When extracting dates and times, convert relative dates to absolute dates:
        - "오늘" → {current_date}
        - "내일" → add 1 day to {current_date}
        - "모레" → add 2 days to {current_date}
        - "다음주 월요일" → calculate next Monday from {current_date}

        For times, convert to 24-hour format:
        - "14시" → "14:00"
        - "오후 3시" → "15:00"
        - "오전 9시" → "09:00"

        For Event entities, include both date and time in ISO format if available:
        - If only date: "2026-02-02"
        - If date and time: "2026-02-02T14:00:00"

        Return the output in JSON format, following this schema:
        {{
          "entities": [
            {{ "type": "Person", "name": "김성길", "title": "과장", "phone": "010-1234-5678", "email": "kim@abc.com" }},
            {{ "type": "Company", "name": "ABC상사" }},
            {{ "type": "Event", "name": "미팅", "date": "2026-02-02T14:00:00" }},
            {{ "type": "Project", "name": "신규 프로젝트" }}
          ],
          "relationships": [
            {{ "from": "김성길", "to": "ABC상사", "type": "WORKS_AT" }},
            {{ "from": "김성길", "to": "미팅", "type": "ATTENDED" }},
            {{ "from": "미팅", "to": "신규 프로젝트", "type": "DISCUSSED" }}
          ],
          "business_related": true
        }}
        If the memo is not business related, set "business_related" to false and return empty entities and relationships.
        """},
        {"role": "user", "content": memo_input.text}
    ]


    response = upstage_service.solar_pro(messages)
    logger.info(f"Solar Pro raw response: {response}")

    try:
        extracted_data_content = response["choices"][0]["message"]["content"]

        # Markdown 코드 블록 제거 (```json 또는 ``` 감싸진 부분 파싱)
        if "```json" in extracted_data_content:
            start = extracted_data_content.find("```json") + len("```json")
            end = extracted_data_content.find("```", start)
            if end != -1:
                extracted_data_content = extracted_data_content[start:end].strip()
        elif "```" in extracted_data_content:
            start = extracted_data_content.find("```") + len("```")
            end = extracted_data_content.find("```", start)
            if end != -1:
                extracted_data_content = extracted_data_content[start:end].strip()

        extracted_data = json.loads(extracted_data_content)
    except (KeyError, IndexError):
        logger.error(f"LLM response structure not as expected: {response}", exc_info=True)
        raise HTTPException(status_code=500, detail="LLM response structure not as expected.")
    except json.JSONDecodeError:
        logger.error(f"JSON decoding failed for content: '{extracted_data_content}'", exc_info=True)
        raise HTTPException(status_code=500, detail="JSON decoding failed from LLM response.")
    except Exception as e:
        logger.error(f"An unexpected error occurred during LLM response parsing: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred during LLM response parsing.")

    business_related = extracted_data.get("business_related", False)

    # 비즈니스 관련 메모가 아닌 경우 그래프에 저장하지 않음
    if not business_related:
        return {"status": "Non-business memo processed", "extracted_data": extracted_data}

    # 고유한 메모 ID 생성
    memo_id = f"memo_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    timestamp = datetime.now().isoformat()

    # Memo 노드 생성
    neo4j_service.create_memo(memo_id, memo_input.text, timestamp, business_related)

    # 엔티티 이름 정규화 (특히 Person 이름)
    # 중복 노드 생성 방지 (예: "인영", "인영님", "이인영" 등을 하나로 통합)
    name_mapping = {}  # 원본 이름 -> 정규화된 이름 매핑
    normalized_entities = []

    for entity in extracted_data.get("entities", []):
        entity_type = entity.get("type")
        entity_name = entity.get("name")

        if entity_type == "Person" and entity_name:
            # 기존에 존재하는 유사한 이름의 Person 찾기
            normalized_name = neo4j_service.find_best_matching_person(entity_name)
            name_mapping[entity_name] = normalized_name
            entity["name"] = normalized_name
            logger.info(f"Person name normalized: '{entity_name}' -> '{normalized_name}'")

        normalized_entities.append(entity)

    # 정규화된 엔티티로 업데이트
    extracted_data["entities"] = normalized_entities

    # 관계에서도 이름 정규화 적용
    for relationship in extracted_data.get("relationships", []):
        from_name = relationship.get("from")
        to_name = relationship.get("to")

        # 매핑에 존재하면 정규화된 이름으로 교체
        if from_name in name_mapping:
            relationship["from"] = name_mapping[from_name]
            logger.info(f"Relationship 'from' normalized: '{from_name}' -> '{name_mapping[from_name]}'")
        if to_name in name_mapping:
            relationship["to"] = name_mapping[to_name]
            logger.info(f"Relationship 'to' normalized: '{to_name}' -> '{name_mapping[to_name]}'")

    # 엔티티 처리 및 Neo4j 저장
    for entity in normalized_entities:
        entity_type = entity.get("type")
        entity_name = entity.get("name")
        if entity_type and entity_name:
            # type과 name을 제외한 속성들만 저장
            properties_to_save = {k: v for k, v in entity.items() if k not in ["type", "name"] and v is not None}
            if entity_type == "Person":
                neo4j_service.create_person(entity_name, properties_to_save)
            elif entity_type == "Company":
                neo4j_service.create_company(entity_name, properties_to_save)
            elif entity_type == "Event":
                neo4j_service.create_event(entity_name, properties_to_save)
            elif entity_type == "Project":
                neo4j_service.create_project(entity_name, properties_to_save)
            # 메모와 엔티티 연결
            neo4j_service.link_memo_to_entity(memo_id, entity_type, entity_name)

    # 관계 처리 및 Neo4j 저장
    for relationship in extracted_data.get("relationships", []):
        from_name = relationship.get("from")
        to_name = relationship.get("to")
        rel_type = relationship.get("type")

        if from_name and to_name and rel_type:
            try:
                success = neo4j_service.create_relationship_by_names(from_name, to_name, rel_type)
                if success:
                    logger.info(f"Created relationship: {from_name} -[{rel_type}]-> {to_name}")
                else:
                    logger.warning(f"Failed to create relationship: {from_name} -[{rel_type}]-> {to_name}")
            except Exception as e:
                logger.error(f"Error creating relationship {from_name} -[{rel_type}]-> {to_name}: {e}")

    return {"status": "Memo processed and saved to Neo4j", "extracted_data": extracted_data}

@router.post("/query")
async def query_graph(query_input: QueryInput):
    """
    자연어 질문을 받아 Cypher 쿼리로 변환하고 Neo4j에서 실행하여 자연어 답변을 생성합니다.

    Args:
        query_input: 사용자의 자연어 질문

    Returns:
        자연어 답변, 쿼리 결과, 생성된 Cypher 쿼리
    """
    # Step 1: LLM을 사용하여 Cypher 쿼리 생성
    system_message = """You are an expert in Cypher query language and Neo4j graph databases.
    Given a user's natural language question, generate a Cypher query that answers the question based on the following graph schema:

    Nodes:
    - Person {name: string, title: string, phone: string, email: string}
    - Company {name: string}
    - Event {name: string, date: string}
    - Project {name: string}
    - Memo {id: string, text: string, timestamp: datetime, business_related: boolean}

    Relationships:
    - (Person)-[:WORKS_AT]->(Company)
    - (Person)-[:ATTENDED]->(Event)
    - (Person)-[:MENTIONED_IN]->(Memo)
    - (Company)-[:MENTIONED_IN]->(Memo)
    - (Event)-[:DISCUSSED]->(Project)
    - (Person)-[:INTRODUCED_BY]->(Person)

    IMPORTANT: For person names, use partial matching with CONTAINS to support both full names and given names.
    Example: "최대련" and "대련" should both match. Use: WHERE p.name CONTAINS "대련"

    Return ONLY the Cypher query, without any additional text or explanations.
    Ensure the query is valid and executable.
    Example queries:
    - "김성길 전화번호?": MATCH (p:Person) WHERE p.name CONTAINS "김성길" RETURN p.phone;
    - "대련님 전화번호?": MATCH (p:Person) WHERE p.name CONTAINS "대련" RETURN p.phone;
    - "ABC상사에 누가 있지?": MATCH (p:Person)-[:WORKS_AT]->(c:Company {name:"ABC상사"}) RETURN p.name, p.title;
    - "최근에 누구 만났지?": MATCH (p:Person)-[:MENTIONED_IN]->(m:Memo) WHERE m.timestamp > datetime() - duration('P7D') RETURN p.name, m.timestamp ORDER BY m.timestamp DESC;
    - "내일 일정 뭐야?": MATCH (e:Event) WHERE e.date STARTS WITH "2026-02-02" RETURN e.name, e.date;
    - "최대련님과 뭘 해야하지?": MATCH (p:Person)-[:ATTENDED]->(e:Event) WHERE p.name CONTAINS "대련" RETURN e.name, e.date ORDER BY e.date;
    """
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": query_input.question}
    ]
    response = upstage_service.solar_pro(messages)

    try:
        cypher_query = response["choices"][0]["message"]["content"].strip()
        # Markdown 코드 블록 제거
        if cypher_query.startswith("```") and cypher_query.endswith("```"):
            lines = cypher_query.split('\n')
            cypher_query = '\n'.join(lines[1:-1]).strip()

        # 기본적인 Cypher 쿼리 유효성 검증
        if not cypher_query.upper().startswith("MATCH") and not cypher_query.upper().startswith("CALL"):
            raise ValueError("Generated response is not a valid Cypher query.")
    except (KeyError, IndexError, ValueError) as e:
        logger.error(f"Failed to generate Cypher query: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate a valid Cypher query.")

    # Step 2: Cypher 쿼리 실행
    try:
        query_results = neo4j_service.run_cypher_query(cypher_query)
    except Exception as e:
        logger.error(f"Failed to execute Cypher query: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to execute Cypher query: {str(e)}")

    # Step 3: 쿼리 결과를 자연어로 변환
    nl_system_message = """You are a helpful assistant that converts database query results into natural language responses.
    Given the user's question and the query results, provide a clear, concise answer in Korean.
    If there are no results, say "관련 정보를 찾을 수 없습니다."
    Be conversational and friendly.
    """
    nl_messages = [
        {"role": "system", "content": nl_system_message},
        {"role": "user", "content": f"Question: {query_input.question}\n\nQuery Results: {json.dumps(query_results, ensure_ascii=False, indent=2)}"}
    ]

    try:
        nl_response = upstage_service.solar_pro(nl_messages)
        natural_answer = nl_response["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError) as e:
        logger.error(f"Failed to generate natural language response: {e}")
        # 자연어 생성 실패 시 원본 결과를 반환
        natural_answer = f"검색 결과: {json.dumps(query_results, ensure_ascii=False, indent=2)}"

    return {
        "status": "Query executed",
        "answer": natural_answer,
        "query_results": query_results,
        "cypher_query": cypher_query
    }

@router.get("/memos")
async def get_memos():
    """
    최근 메모 목록을 시간 역순으로 반환합니다.

    Returns:
        최근 메모 목록 (최대 10개)
    """
    memos = neo4j_service.get_recent_memos()
    return {
        "success": True,
        "data": memos,
        "total": len(memos),
        "page": 1,
    }

