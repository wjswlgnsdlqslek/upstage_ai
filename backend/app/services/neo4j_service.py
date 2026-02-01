import os
from neo4j import GraphDatabase
from dotenv import load_dotenv
from tenacity import retry, wait_fixed, stop_after_attempt, before_log, after_log
import logging

load_dotenv()

# 로깅 설정
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class Neo4jService:
    """
    Neo4j 그래프 데이터베이스와의 상호작용을 관리하는 서비스 클래스입니다.
    연결, CRUD 작업, 쿼리 실행 등의 기능을 제공합니다.
    """

    @retry(wait=wait_fixed(2), stop=stop_after_attempt(10),
           before=before_log(logger, logging.INFO),
           after=after_log(logger, logging.INFO))
    def __init__(self):
        """Neo4j 데이터베이스 연결을 초기화하고 제약조건을 생성합니다."""
        uri = os.getenv("NEO4J_URI", "bolt://neo4j:7687")  # Docker Compose에서 neo4j 서비스명 기본값
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")

        logger.info(f"Attempting to connect to Neo4j at {uri} as user {user}")
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.driver.verify_connectivity()  # 연결 확인
        logger.info("Successfully connected to Neo4j.")
        self._create_constraints()

    def close(self):
        """데이터베이스 연결을 종료합니다."""
        self.driver.close()

    def _create_constraints(self):
        """Person과 Company 노드의 name 속성에 유니크 제약조건을 생성합니다."""
        with self.driver.session() as session:
            session.run("CREATE CONSTRAINT person_name IF NOT EXISTS FOR (p:Person) REQUIRE p.name IS UNIQUE")
            session.run("CREATE CONSTRAINT company_name IF NOT EXISTS FOR (c:Company) REQUIRE c.name IS UNIQUE")

    def create_person(self, name: str, properties: dict = None):
        """
        Person 노드를 생성하거나 업데이트합니다.
        이미 존재하는 경우 속성을 업데이트합니다.
        """
        with self.driver.session() as session:
            query = (
                "MERGE (p:Person {name: $name}) "
                "ON CREATE SET p += $properties "
                "ON MATCH SET p += $properties "
                "RETURN p"
            )
            return session.run(query, name=name, properties=properties).single().get("p")

    def create_company(self, name: str, properties: dict = None):
        """
        Company 노드를 생성하거나 업데이트합니다.
        이미 존재하는 경우 속성을 업데이트합니다.
        """
        with self.driver.session() as session:
            query = (
                "MERGE (c:Company {name: $name}) "
                "ON CREATE SET c += $properties "
                "ON MATCH SET c += $properties "
                "RETURN c"
            )
            return session.run(query, name=name, properties=properties).single().get("c")

    def create_event(self, name: str, properties: dict = None):
        """
        Event 노드를 생성하거나 업데이트합니다.
        이미 존재하는 경우 속성을 업데이트합니다.
        """
        with self.driver.session() as session:
            query = (
                "MERGE (e:Event {name: $name}) "
                "ON CREATE SET e += $properties "
                "ON MATCH SET e += $properties "
                "RETURN e"
            )
            return session.run(query, name=name, properties=properties).single().get("e")

    def create_project(self, name: str, properties: dict = None):
        """
        Project 노드를 생성하거나 업데이트합니다.
        이미 존재하는 경우 속성을 업데이트합니다.
        """
        with self.driver.session() as session:
            query = (
                "MERGE (p:Project {name: $name}) "
                "ON CREATE SET p += $properties "
                "ON MATCH SET p += $properties "
                "RETURN p"
            )
            return session.run(query, name=name, properties=properties).single().get("p")

    def create_memo(self, memo_id: str, text: str, timestamp: str, business_related: bool, entities: list = None):
        """
        Memo 노드를 생성합니다.

        Args:
            memo_id: 고유한 메모 ID
            text: 메모 원문
            timestamp: 메모 작성 시간 (ISO 형식)
            business_related: 비즈니스 관련 여부
            entities: 메모에 포함된 엔티티 목록 (선택)
        """
        with self.driver.session() as session:
            query = (
                "MERGE (m:Memo {id: $memo_id}) "
                "ON CREATE SET m.text = $text, m.timestamp = datetime($timestamp), m.business_related = $business_related "
                "RETURN m"
            )
            return session.run(query, memo_id=memo_id, text=text, timestamp=timestamp, business_related=business_related).single().get("m")

    def create_relationship(self, from_node_label: str, from_node_name: str, to_node_label: str, to_node_name: str, relationship_type: str):
        """
        두 노드 간 관계를 생성합니다.

        Args:
            from_node_label: 시작 노드의 레이블 (예: Person, Company)
            from_node_name: 시작 노드의 name 속성값
            to_node_label: 대상 노드의 레이블
            to_node_name: 대상 노드의 name 속성값
            relationship_type: 관계 타입 (예: WORKS_AT, ATTENDED)
        """
        with self.driver.session() as session:
            query = (
                f"MATCH (a:{from_node_label} {{name: $from_node_name}}), (b:{to_node_label} {{name: $to_node_name}}) "
                f"MERGE (a)-[:{relationship_type}]->(b)"
            )
            session.run(query, from_node_name=from_node_name, to_node_name=to_node_name)

    def link_memo_to_entity(self, memo_id: str, entity_type: str, entity_name: str):
        """
        메모와 엔티티를 MENTIONED_IN 관계로 연결합니다.

        Args:
            memo_id: 메모 ID
            entity_type: 엔티티 타입 (Person, Company, Event, Project)
            entity_name: 엔티티 이름
        """
        with self.driver.session() as session:
            query = (
                f"MATCH (m:Memo {{id: $memo_id}}), (e:{entity_type} {{name: $entity_name}}) "
                f"MERGE (e)-[:MENTIONED_IN]->(m)"
            )
            session.run(query, memo_id=memo_id, entity_type=entity_type, entity_name=entity_name)

    def get_person_phone(self, name: str):
        """특정 인물의 전화번호를 조회합니다."""
        with self.driver.session() as session:
            query = "MATCH (p:Person {name: $name}) RETURN p.phone AS phone"
            result = session.run(query, name=name).single()
            return result["phone"] if result else None

    def get_company_people(self, company_name: str):
        """특정 회사에 근무하는 사람들의 목록을 반환합니다."""
        with self.driver.session() as session:
            query = (
                "MATCH (p:Person)-[:WORKS_AT]->(c:Company {name: $company_name}) "
                "RETURN p.name AS name, p.title AS title"
            )
            results = session.run(query, company_name=company_name)
            return [{"name": record["name"], "title": record["title"]} for record in results]

    def run_cypher_query(self, query: str, parameters: dict = None):
        """
        임의의 Cypher 쿼리를 실행하고 결과를 반환합니다.

        Args:
            query: 실행할 Cypher 쿼리 문자열
            parameters: 쿼리에 전달할 파라미터 (선택)

        Returns:
            쿼리 결과를 딕셔너리 리스트로 반환
        """
        with self.driver.session() as session:
            result = session.run(query, parameters)
            return [record.data() for record in result]

    def get_recent_memos(self, limit: int = 10):
        """
        최근 메모 목록을 시간 역순으로 반환합니다.

        Args:
            limit: 반환할 메모 개수 (기본값: 10)

        Returns:
            메모 목록 (id, text, timestamp, business_related, entities)
        """
        with self.driver.session() as session:
            query = (
                "MATCH (m:Memo) "
                "RETURN m.id AS id, m.text AS text, m.timestamp AS timestamp, m.business_related AS business_related "
                "ORDER BY m.timestamp DESC LIMIT $limit"
            )
            results = session.run(query, limit=limit)
            return [
                {
                    "id": record["id"],
                    "text": record["text"],
                    "timestamp": record["timestamp"].isoformat(),
                    "business_related": record["business_related"],
                    "entities": []  # 향후 메모에 연결된 엔티티 추출 예정
                } for record in results
            ]

    def find_node_label(self, name: str):
        """
        노드의 이름으로 레이블(타입)을 찾습니다.
        정확한 매칭을 먼저 시도하고, 실패하면 부분 매칭을 시도합니다.

        Args:
            name: 찾고자 하는 노드의 이름

        Returns:
            노드의 레이블 (Person, Company, Event, Project 등) 또는 None
        """
        with self.driver.session() as session:
            # 먼저 정확한 이름으로 매칭 시도
            query = (
                "MATCH (n) WHERE n.name = $name "
                "RETURN labels(n) AS labels LIMIT 1"
            )
            result = session.run(query, name=name).single()
            if result and result["labels"]:
                return result["labels"][0]

            # 부분 매칭 시도 (이름이 검색어를 포함하거나 검색어가 이름을 포함)
            query = (
                "MATCH (n) WHERE n.name CONTAINS $name OR $name CONTAINS n.name "
                "RETURN labels(n) AS labels, n.name AS matched_name LIMIT 1"
            )
            result = session.run(query, name=name).single()
            if result and result["labels"]:
                logger.info(f"Partial name match: '{name}' matched with '{result['matched_name']}'")
                return result["labels"][0]

            return None

    def find_best_matching_person(self, partial_name: str) -> str:
        """
        부분 이름으로 가장 일치하는 Person 노드를 찾습니다.
        중복 노드 생성을 방지하기 위해 기존 노드를 찾아 정규화합니다.

        동작 방식:
        1. 공백과 "님" 등 접미사를 제거하여 이름 정규화
        2. 부분 매칭으로 기존 Person 노드 검색
        3. 연락처 정보(전화번호, 이메일, 직함)가 있는 노드 우선 선택
        4. 없으면 가장 긴 (구체적인) 이름 선택
        5. 매칭 실패 시 원본 이름 반환

        예시:
        - "인영" -> "이인영" (이인영이 연락처와 함께 존재하는 경우)
        - "효주" -> "이효주" (이효주가 연락처와 함께 존재하는 경우)
        - "홍길동" -> "홍길동" (매칭되는 노드가 없는 경우)

        Args:
            partial_name: 부분 이름 (예: "인영", "인영님", "이인영")

        Returns:
            정규화된 전체 이름
        """
        # 공백과 접미사 제거하여 이름 정규화
        clean_name = partial_name.replace("님", "").replace(" ", "")

        with self.driver.session() as session:
            # 부분 매칭으로 Person 노드 검색
            query = (
                "MATCH (p:Person) "
                "WHERE p.name CONTAINS $clean_name OR $clean_name CONTAINS p.name "
                "RETURN p.name AS name, p.phone AS phone, p.email AS email, p.title AS title "
                "ORDER BY size(p.name) DESC"  # 긴 이름 우선 (더 구체적인 이름)
            )
            results = session.run(query, clean_name=clean_name).data()

            if not results:
                return partial_name  # 매칭 실패 시 원본 반환

            # 연락처 정보(전화번호, 이메일, 직함)가 있는 노드 우선 선택
            for result in results:
                if result['phone'] or result['email'] or result['title']:
                    logger.info(f"Name normalization: '{partial_name}' -> '{result['name']}' (has contact info)")
                    return result['name']

            # 연락처 정보가 없으면 가장 긴 이름 선택
            best_match = results[0]['name']
            if best_match != partial_name:
                logger.info(f"Name normalization: '{partial_name}' -> '{best_match}'")
            return best_match

    def create_relationship_by_names(self, from_name: str, to_name: str, relationship_type: str):
        """
        노드 이름만으로 두 노드 간 관계를 생성합니다.
        노드의 레이블(타입)을 자동으로 찾아서 관계를 생성합니다.

        Args:
            from_name: 시작 노드의 이름
            to_name: 대상 노드의 이름
            relationship_type: 관계 타입 (예: WORKS_AT, ATTENDED)

        Returns:
            성공 시 True, 실패 시 False
        """
        # 노드 이름으로 레이블(타입) 찾기
        from_label = self.find_node_label(from_name)
        to_label = self.find_node_label(to_name)

        if not from_label or not to_label:
            logger.warning(f"Could not find nodes: {from_name} ({from_label}) or {to_name} ({to_label})")
            return False

        # 관계 생성
        with self.driver.session() as session:
            query = (
                f"MATCH (a:{from_label} {{name: $from_name}}), (b:{to_label} {{name: $to_name}}) "
                f"MERGE (a)-[:{relationship_type}]->(b)"
            )
            session.run(query, from_name=from_name, to_name=to_name)
            logger.info(f"Created relationship: ({from_name})-[:{relationship_type}]->({to_name})")
            return True


# Neo4j 서비스 싱글톤 인스턴스
neo4j_service = Neo4jService()
