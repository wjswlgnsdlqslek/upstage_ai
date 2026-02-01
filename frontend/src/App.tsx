import React, { useState, useEffect, useRef } from 'react';
import './App.css';

// 타입 정의
interface ChatMessage {
  id: number;
  type: 'user' | 'bot' | 'system';
  text: string;
  data?: any;
  isLoading?: boolean;
  pendingBusinessCard?: {
    person_data: any;
    company_data: any;
  };
  isConfirmation?: boolean;
  onConfirm?: () => void;
  onEdit?: () => void;
}

interface EditingCardData {
  name: string;
  title: string;
  company: string;
  phone: string;
  email: string;
}

function App() {
  // 상태 관리
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [pendingCardData, setPendingCardData] = useState<any>(null);
  const [isEditingCard, setIsEditingCard] = useState(false);
  const [editingCardData, setEditingCardData] = useState<EditingCardData>({
    name: '',
    title: '',
    company: '',
    phone: '',
    email: ''
  });
  const chatContainerRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // 초기 환영 메시지 설정
  useEffect(() => {
    setChatHistory([
      {
        id: 1,
        type: 'bot',
        text: "안녕하세요! 👋\n\n저는 비즈니스 네트워크 관리 에이전트입니다.\n\n**할 수 있는 일:**\n- 💬 메모 작성 (예: \"내일 김대리와 14시 미팅\")\n- 🔍 정보 검색 (예: \"최대련님 전화번호?\")\n- 📇 명함 등록 (+ 버튼 클릭)\n\n무엇을 도와드릴까요?"
      }
    ]);
  }, []);

  // 채팅 히스토리가 업데이트될 때마다 스크롤을 최신 메시지로 자동 이동하여 항상 최신 내용 표시
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [chatHistory]);

  // 사용자가 명함 이미지를 선택했을 때 호출되는 핸들러
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setSelectedFile(e.target.files[0]);

      // 사용자가 업로드한 명함 파일을 메시지로 표시
      const userMessage: ChatMessage = {
        id: Date.now(),
        type: 'user',
        text: `📇 명함 업로드: ${e.target.files[0].name}`
      };
      setChatHistory(prev => [...prev, userMessage]);

      // 선택된 파일을 즉시 처리하여 명함 정보 추출 시작
      processBusinessCard(e.target.files[0]);
    }
  };

  // 명함 이미지에서 정보를 추출하고 그래프에 저장하는 프로세스
  const processBusinessCard = async (file: File) => {
    setIsLoading(true);

    // 사용자에게 처리 중임을 알려주는 로딩 메시지 표시
    const loadingMessage: ChatMessage = {
      id: Date.now(),
      type: 'bot',
      text: '명함을 분석하고 있습니다...',
      isLoading: true
    };
    setChatHistory(prev => [...prev, loadingMessage]);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('/api/extract-business-card', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) throw new Error('Failed to extract business card');

      const data = await response.json();
      setPendingCardData(data);

      // 추출된 명함 정보를 표시하고 사용자 확인/수정 버튼 제공
      const confirmationId = Date.now();
      setChatHistory(prev => {
        const filtered = prev.filter(msg => !msg.isLoading);
        return [
          ...filtered,
          {
            id: confirmationId,
            type: 'bot',
            text: `📇 명함 정보를 추출했습니다:\n\n**이름:** ${data.person_data?.name || '-'}\n**직책:** ${data.person_data?.title || '-'}\n**회사:** ${data.company_data?.name || '-'}\n**전화:** ${data.person_data?.phone || '-'}\n**이메일:** ${data.person_data?.email || '-'}\n\n이 정보가 맞습니까?`,
            isConfirmation: true,
            onConfirm: () => handleConfirmCard(data),
            onEdit: () => handleEditCard(data)
          }
        ];
      });

    } catch (error: any) {
      setChatHistory(prev => {
        const filtered = prev.filter(msg => !msg.isLoading);
        return [
          ...filtered,
          {
            id: Date.now(),
            type: 'bot',
            text: `❌ 오류가 발생했습니다: ${error.message}`
          }
        ];
      });
    } finally {
      setIsLoading(false);
      setSelectedFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  // 사용자가 명함 정보를 확인했을 때 그래프에 저장하는 함수
  const handleConfirmCard = async (data: any) => {
    setIsLoading(true);

    // 확인 버튼을 제거하고 저장 중임을 나타내는 로딩 메시지로 교체
    setChatHistory(prev => {
      const filtered = prev.filter(msg => !msg.isConfirmation);
      return [
        ...filtered,
        {
          id: Date.now(),
          type: 'bot',
          text: '저장 중...',
          isLoading: true
        }
      ];
    });

    try {
      const saveResponse = await fetch('/api/save-contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });

      if (!saveResponse.ok) throw new Error('Failed to save contact');

      setChatHistory(prev => {
        const filtered = prev.filter(msg => !msg.isLoading);
        return [
          ...filtered,
          {
            id: Date.now(),
            type: 'bot',
            text: `✅ 명함이 저장되었습니다!`
          }
        ];
      });

    } catch (error: any) {
      setChatHistory(prev => {
        const filtered = prev.filter(msg => !msg.isLoading);
        return [
          ...filtered,
          {
            id: Date.now(),
            type: 'bot',
            text: `❌ 저장 실패: ${error.message}`
          }
        ];
      });
    } finally {
      setIsLoading(false);
      setPendingCardData(null);
    }
  };

  // 사용자가 명함 정보를 수정하고자 할 때 편집 폼을 표시하는 함수
  const handleEditCard = (data: any) => {
    // 확인 버튼 메시지를 제거하여 편집 폼을 위한 공간 마련
    setChatHistory(prev => prev.filter(msg => !msg.isConfirmation));

    // 편집 모드 활성화 및 기존 데이터로 폼 초기화
    setIsEditingCard(true);
    setEditingCardData({
      name: data.person_data?.name || '',
      title: data.person_data?.title || '',
      company: data.company_data?.name || '',
      phone: data.person_data?.phone || '',
      email: data.person_data?.email || ''
    });
  };

  // 사용자가 편집한 명함 정보를 그래프에 저장하는 함수
  const handleSaveEditedCard = async () => {
    setIsLoading(true);
    setIsEditingCard(false);

    // 편집된 폼 데이터를 API 요청 형식으로 변환
    const data = {
      person_data: {
        name: editingCardData.name,
        title: editingCardData.title,
        phone: editingCardData.phone,
        email: editingCardData.email
      },
      company_data: editingCardData.company ? { name: editingCardData.company } : {}
    };

    try {
      const saveResponse = await fetch('/api/save-contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });

      if (!saveResponse.ok) throw new Error('Failed to save contact');

      setChatHistory(prev => [
        ...prev,
        {
          id: Date.now(),
          type: 'bot',
          text: `✅ 수정된 명함이 저장되었습니다!`
        }
      ]);

    } catch (error: any) {
      setChatHistory(prev => [
        ...prev,
        {
          id: Date.now(),
          type: 'bot',
          text: `❌ 저장 실패: ${error.message}`
        }
      ]);
    } finally {
      setIsLoading(false);
      setPendingCardData(null);
    }
  };

  // 명함 편집을 취소하고 편집 폼을 닫는 함수
  const handleCancelEdit = () => {
    setIsEditingCard(false);
    setPendingCardData(null);
  };

  // 사용자가 입력한 메시지를 처리하여 메모/쿼리로 분류하고 백엔드에 전송하는 함수
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    // 사용자 입력 메시지를 채팅 히스토리에 추가
    const userMessage: ChatMessage = {
      id: Date.now(),
      type: 'user',
      text: input
    };
    setChatHistory(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    // AI가 응답을 생성하고 있음을 나타내는 로딩 메시지 표시
    const loadingMessage: ChatMessage = {
      id: Date.now() + 1,
      type: 'bot',
      text: '생각 중...',
      isLoading: true
    };
    setChatHistory(prev => [...prev, loadingMessage]);

    try {
      // 사용자 입력이 질문인지 메모인지 판별 (질문 기호나 키워드 포함 여부 확인)
      // 명확한 질문 표시가 있을 때만 질문으로 분류하여 오분류 방지
      const text = userMessage.text;
      const isQuery = (
        text.includes('?') ||
        text.includes('뭐야') ||
        text.includes('알려') ||
        text.includes('찾아') ||
        text.includes('조회') ||
        text.includes('전화번호') ||
        text.includes('이메일') ||
        text.includes('언제야') ||
        text.includes('어디야') ||
        text.includes('누구야') ||
        text.includes('보여') ||
        (text.includes('일정') && (text.includes('뭐') || text.includes('?')))
      );

      let response;
      let botText = '';

      if (isQuery) {
        // 정보 검색 요청: 백엔드의 쿼리 엔드포인트 호출
        response = await fetch('/api/query', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question: userMessage.text })
        });

        if (!response.ok) throw new Error('Query failed');

        const result = await response.json();
        botText = result.answer || '관련 정보를 찾을 수 없습니다.';

      } else {
        // 메모 저장 요청: 자연어를 엔티티로 추출하고 그래프 업데이트
        response = await fetch('/api/memo', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: userMessage.text })
        });

        if (!response.ok) throw new Error('Memo save failed');

        const result = await response.json();
        const entities = result.extracted_data?.entities || [];

        // 추출된 엔티티가 있으면 상세 정보 표시, 없으면 간단한 확인 메시지만 표시
        if (entities.length > 0) {
          const entityList = entities.map((e: any) => {
            if (e.type === 'Event' && e.date) {
              return `- ${e.type}: ${e.name} (${e.date})`;
            }
            return `- ${e.type}: ${e.name}`;
          }).join('\n');
          botText = `✅ 메모가 저장되었습니다!\n\n**추출된 정보:**\n${entityList}`;
        } else {
          botText = '✅ 메모가 저장되었습니다!';
        }
      }

      // 로딩 메시지를 제거하고 AI 응답 메시지로 교체
      setChatHistory(prev => {
        const filtered = prev.filter(msg => !msg.isLoading);
        return [
          ...filtered,
          {
            id: Date.now() + 2,
            type: 'bot',
            text: botText
          }
        ];
      });

    } catch (error: any) {
      setChatHistory(prev => {
        const filtered = prev.filter(msg => !msg.isLoading);
        return [
          ...filtered,
          {
            id: Date.now() + 2,
            type: 'bot',
            text: `❌ 오류가 발생했습니다: ${error.message}`
          }
        ];
      });
    } finally {
      setIsLoading(false);
    }
  };

  // 숨겨진 파일 입력창을 클릭하여 명함 업로드 다이얼로그 열기
  const handleAttachClick = () => {
    fileInputRef.current?.click();
  };

  // 컴포넌트 렌더링: 헤더, 채팅 영역, 입력 폼으로 구성된 UI 반환
  return (
    <div className="app-container">
      <header className="app-header">
        <h1>🧠 Business Network Agent</h1>
      </header>

      <div className="chat-container" ref={chatContainerRef}>
        {chatHistory.map(msg => (
          <div key={msg.id} className={`chat-message ${msg.type}`}>
            <div className="chat-bubble">
              {msg.isLoading ? (
                <div className="loading-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              ) : (
                <>
                  <p className="message-text">{msg.text}</p>
                  {msg.isConfirmation && (
                    <div className="confirmation-buttons">
                      <button
                        onClick={msg.onConfirm}
                        className="confirm-button"
                        disabled={isLoading}
                      >
                        ✅ 확인
                      </button>
                      <button
                        onClick={msg.onEdit}
                        className="edit-button"
                        disabled={isLoading}
                      >
                        ✏️ 수정
                      </button>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        ))}

        {isEditingCard && (
          <div className="edit-card-form">
            <h3>명함 정보 수정</h3>
            <div className="form-group">
              <label>이름 *</label>
              <input
                type="text"
                value={editingCardData.name}
                onChange={(e) => setEditingCardData({...editingCardData, name: e.target.value})}
                placeholder="이름"
              />
            </div>
            <div className="form-group">
              <label>직책</label>
              <input
                type="text"
                value={editingCardData.title}
                onChange={(e) => setEditingCardData({...editingCardData, title: e.target.value})}
                placeholder="직책"
              />
            </div>
            <div className="form-group">
              <label>회사</label>
              <input
                type="text"
                value={editingCardData.company}
                onChange={(e) => setEditingCardData({...editingCardData, company: e.target.value})}
                placeholder="회사명"
              />
            </div>
            <div className="form-group">
              <label>전화</label>
              <input
                type="text"
                value={editingCardData.phone}
                onChange={(e) => setEditingCardData({...editingCardData, phone: e.target.value})}
                placeholder="전화번호"
              />
            </div>
            <div className="form-group">
              <label>이메일</label>
              <input
                type="text"
                value={editingCardData.email}
                onChange={(e) => setEditingCardData({...editingCardData, email: e.target.value})}
                placeholder="이메일"
              />
            </div>
            <div className="form-actions">
              <button onClick={handleSaveEditedCard} className="save-button" disabled={!editingCardData.name || isLoading}>
                💾 저장
              </button>
              <button onClick={handleCancelEdit} className="cancel-button" disabled={isLoading}>
                ❌ 취소
              </button>
            </div>
          </div>
        )}
      </div>

      <div className="input-container">
        <form onSubmit={handleSubmit} className="input-form">
          <button
            type="button"
            className="attach-button"
            onClick={handleAttachClick}
            disabled={isLoading}
            title="명함 업로드"
          >
            📷
          </button>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileSelect}
            accept="image/*"
            style={{ display: 'none' }}
          />
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="메시지를 입력하세요... (메모 작성, 정보 검색)"
            disabled={isLoading}
            className="text-input"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="send-button"
          >
            ➤
          </button>
        </form>
      </div>
    </div>
  );
}

export default App;
