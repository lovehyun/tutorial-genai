// public/script.js

document.addEventListener('DOMContentLoaded', function () {
    const chatContainer = document.getElementById('chat-container');
    const userInputForm = document.getElementById('user-input-form');
    const userInputField = document.getElementById('user-input');
    const loadingIndicator = document.getElementById('loading-indicator');
    const submitButton = document.getElementById('submit-button');

    submitButton.addEventListener('click', function () {
        submitUserInput();
    });

    userInputForm.addEventListener('submit', function (event) {
        event.preventDefault();
        submitUserInput();
    });

    async function submitUserInput() {
        const userInput = userInputField.value;
        if (userInput.trim() === '') return;

        showLoadingIndicator();
        appendMessage('user', userInput);

        try {
            await getChatGPTResponseStream(userInput);
            hideLoadingIndicator();
        } catch (error) {
            hideLoadingIndicator();
            console.error('Error making ChatGPT API request:', error.message);
            appendMessage('chatbot', '챗봇 응답을 가져오는 도중에 오류가 발생했습니다.');
        }

        userInputField.value = '';
        scrollToBottom();
    }

    function appendMessage(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${role}`;
        messageDiv.innerHTML = '<div class="message-content">' + content + '</div>';
        chatContainer.appendChild(messageDiv);
    }

    function showLoadingIndicator() {
        loadingIndicator.style.display = 'flex';
    }

    function hideLoadingIndicator() {
        loadingIndicator.style.display = 'none';
    }

    async function getChatGPTResponse(userInput) {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ userInput }),
        });

        const data = await response.json();
        return data.chatGPTResponse;
    }

    function scrollToBottom() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    // 개행 문자(\n)를 <br> 태그로 변환하는 함수
    function formatResponseForHTML(response) {
        return response.replace(/\n/g, '<br>');
    }

    // 스트림 처리용 함수 새로 추가
    async function getChatGPTResponseStream(userInput) {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ userInput })
        });

        if (!response.body) {
            throw new Error("Response body is null");
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let chatMessage = '';

        const messageDiv = document.createElement('div');
        messageDiv.className = 'chat-message chatbot';
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        messageDiv.appendChild(contentDiv);
        chatContainer.appendChild(messageDiv);

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            const chunk = decoder.decode(value, { stream: true });
            chatMessage += chunk;
            contentDiv.innerHTML = chatMessage.replace(/\n/g, '<br>');
            scrollToBottom();
        }

        hideLoadingIndicator();
    }

});
