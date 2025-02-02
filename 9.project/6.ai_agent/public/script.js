async function sendMessage() {
    const userInput = document.getElementById("userInput").value;
    if (!userInput) return;

    const response = await fetch("/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: userInput })
    });

    const data = await response.json();
    document.getElementById("chat").innerHTML += `<p><strong>사용자:</strong> ${userInput}</p>`;
    document.getElementById("chat").innerHTML += `<p><strong>GPT:</strong> ${data.response}</p>`;

    document.getElementById("userInput").value = "";
}

async function clearChat() {
    await fetch("/clear", { method: "POST" });
    document.getElementById("chat").innerHTML = "<p>대화 기록이 초기화되었습니다.</p>";
}

function handleKeyPress(event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault(); // 기본 엔터 동작(줄바꿈) 방지
        sendMessage();
    }
}
