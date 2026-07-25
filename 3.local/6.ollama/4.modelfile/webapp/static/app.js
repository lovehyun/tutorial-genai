// 입력 → /chat 스트리밍(NDJSON) → 생각/답변 컬럼에 실시간 분배
const $q = document.getElementById("q");
const $send = document.getElementById("send");
const $status = document.getElementById("status");
const $think = document.getElementById("think");
const $answerRaw = document.getElementById("answerRaw");
const $answerMd = document.getElementById("answerMd");

let answerText = "";   // 답변 raw 누적 (md 렌더용)

function renderMd() {
  // marked 가 있으면 마크다운 렌더, 없으면(오프라인) raw 그대로
  if (window.marked) {
    $answerMd.innerHTML = marked.parse(answerText);
  } else {
    $answerMd.textContent = answerText;
  }
  $answerMd.scrollTop = $answerMd.scrollHeight;
}

async function ask() {
  const question = $q.value.trim();
  if (!question) return;

  // 초기화
  $think.textContent = "";
  $answerRaw.textContent = "";
  $answerMd.innerHTML = "";
  answerText = "";
  $send.disabled = true;
  $status.textContent = "생성 중…";

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    if (!res.ok) throw new Error("서버 오류 " + res.status);

    // NDJSON 스트림을 줄 단위로 읽는다
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buf = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buf += decoder.decode(value, { stream: true });

      let nl;
      while ((nl = buf.indexOf("\n")) !== -1) {
        const line = buf.slice(0, nl).trim();
        buf = buf.slice(nl + 1);
        if (!line) continue;

        const evt = JSON.parse(line);
        if (evt.col === "think") {
          $think.textContent += evt.text;
          $think.scrollTop = $think.scrollHeight;
        } else if (evt.col === "answer") {
          answerText += evt.text;
          $answerRaw.textContent = answerText;   // 위: raw
          $answerRaw.scrollTop = $answerRaw.scrollHeight;
          renderMd();                            // 아래: 마크다운 렌더
        } else if (evt.col === "done") {
          $status.textContent = "완료";
        }
      }
    }
    if (!$status.textContent) $status.textContent = "완료";
  } catch (e) {
    $status.textContent = "에러: " + e.message;
  } finally {
    $send.disabled = false;
  }
}

$send.addEventListener("click", ask);
// Ctrl/⌘+Enter 로 전송
$q.addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") ask();
});
