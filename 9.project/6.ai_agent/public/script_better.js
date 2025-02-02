document.addEventListener("DOMContentLoaded", function () {
    const userInput = document.getElementById("userInput");
    const sendButton = document.getElementById("sendButton");
    const clearButton = document.getElementById("clearButton");

    // Enter 키 입력 시 메시지 전송
    userInput.addEventListener("keydown", function (event) {
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
    const userInput = document.getElementById("userInput").value;
    if (!userInput) return;

    document.getElementById("userInput").value = "";

    const response = await fetch("/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: userInput })
    });

    const data = await response.json();
    document.getElementById("chat").innerHTML += `<p><strong>사용자:</strong> ${userInput}</p>`;
    document.getElementById("chat").innerHTML += `<p><strong>GPT:</strong> ${data.response}</p>`;
}

async function clearChat() {
    await fetch("/clear", { method: "POST" });
    document.getElementById("chat").innerHTML = "<p>대화 기록이 초기화되었습니다.</p>";
}
