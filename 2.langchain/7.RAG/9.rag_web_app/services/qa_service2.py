# services/qa_service.py
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class QAService:
    """
    VectorStore(RAG) + LLM 조합 Q&A 서비스
    - threshold: 거리(score) 임계값. 작을수록 유사. None이면 점수 미사용.
    - k: 검색 문서 개수
    - debug: True면 검색 결과/점수 디버그 출력
    """
    def __init__(
        self,
        vectorstore,                 # services.vectorstore.VectorStore 인스턴스
        model: str = "gpt-4o-mini",  # 또는 "gpt-3.5-turbo"
        temperature: float = 0.2,
        k: int = 5,
        threshold: Optional[float] = None,
        debug: bool = False,
    ):
        self.vs = vectorstore
        self.k = k
        self.threshold = threshold
        self.debug = debug

        # 컨텍스트는 system에, 질문은 human에
        self.prompt = ChatPromptTemplate.from_messages([
            ("system",
             "당신은 문서 기반 질문 응답 시스템입니다."
             "아래 문서를 기반으로 답하세요. 문서가 없으면 반드시 '모르겠습니다'라고 답하세요.\n\n"
             "문서:\n{context}\n"),
            ("human", "{question}")
        ])

        self.llm = ChatOpenAI(model=model, temperature=temperature)
        self.chain = self.prompt | self.llm | StrOutputParser()
        
    def _build_context(self, question: str) -> str:
        """질문으로 검색 → (옵션) 임계값으로 필터 → 컨텍스트 문자열 생성"""
        if not self.vs or not self.vs.store:
            return ""

        # 점수 사용 여부에 따라 분기
        if self.threshold is None:
            docs = self.vs.search(question, k=self.k)
            if self.debug:
                print(f"[DEBUG] top-{len(docs)} docs (no score)")
                for i, d in enumerate(docs, 1):
                    prev = d.page_content[:80].replace("\n", " ")
                    print(f"  {i}. preview='{prev}'")
                    
            return "\n\n---\n\n".join(d.page_content for d in docs)

        # 점수 포함 검색 (작을수록 유사)
        results = self.vs.search_with_score(question, k=self.k)
        if self.debug:
            print("[DEBUG] 검색 결과 (거리 score: 작을수록 유사):")
            for i, (doc, score) in enumerate(results, 1):
                prev = doc.page_content[:80].replace("\n", " ")
                print(f"  {i}. score={score:.4f} | preview='{prev}'")

        filtered_docs = [doc for doc, score in results if score < self.threshold]
        if self.debug:
            print(f"[DEBUG] 임계값 {self.threshold} 미만 문서 수: {len(filtered_docs)}")

        return "\n\n---\n\n".join(d.page_content for d in filtered_docs)
    
    def answer(self, question: str) -> str:
        """최종 Q&A 실행"""
        if not self.vs or not self.vs.store:
            return "문서가 로드되지 않았습니다. 먼저 PDF를 업로드해주세요."

        context = self._build_context(question)

        try:
            result = self.chain.invoke({"context": context, "question": question})
        except Exception as e:
            return f"GPT 처리 중 오류: {e}"

        return f"질문: {question}\n응답: {result}"
