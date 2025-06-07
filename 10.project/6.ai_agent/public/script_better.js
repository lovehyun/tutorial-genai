document.addEventListener("DOMContentLoaded", function () {
    const inputEl = document.getElementById("userInput");
    const sendButton = document.getElementById("sendButton");
    const clearButton = document.getElementById("clearButton");

    // Enter 키 입력 시 메시지 전송
    inputEl.addEventListener("keydown", function (event) {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    });

    // 버튼 클릭 시 메시지 전송
    sendButton.addEventListener("click", sendMessage);
    clearButton.addEventListener("click", clearChat);
});

async function sendMessage() {
    const inputEl = document.getElementById("userInput");
    const chatEl = document.getElementById("chat");
    const sendButton = document.getElementById("sendButton");
    const userInput = inputEl.value.trim();

    if (!userInput) return;

    inputEl.value = "";
    sendButton.disabled = true;

    chatEl.innerHTML += `<p><strong>사용자:</strong> ${userInput}</p>`;
    chatEl.innerHTML += `<p id="loading">GPT: 생각중...</p>`;
    chatEl.scrollTop = chatEl.scrollHeight;

    try {
        const response = await fetch("/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question: userInput })
        });

        const data = await response.json();
        document.getElementById("loading").remove();
        chatEl.innerHTML += `<p><strong>GPT:</strong> ${data.response}</p>`;
        chatEl.scrollTop = chatEl.scrollHeight;
    } catch (error) {
        document.getElementById("loading").remove();
        chatEl.innerHTML += `<p><strong>GPT:</strong> 오류가 발생했습니다.</p>`;
    }

    sendButton.disabled = false;
}

async function clearChat() {
    await fetch("/clear", { method: "POST" });
    document.getElementById("chat").innerHTML = "<p>대화 기록이 초기화되었습니다.</p>";
}
