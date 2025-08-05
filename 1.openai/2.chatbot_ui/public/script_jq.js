// public/script.js

$(document).ready(function () {
    const chatContainer = $('#chat-container');
    const userInputForm = $('#user-input-form');
    const userInputField = $('#user-input');

    userInputForm.submit(async function (event) {
        event.preventDefault();

        const userInput = userInputField.val();
        if (userInput.trim() === '') return;

        appendMessage('user', userInput);

        const chatGPTResponse = await getChatGPTResponse(userInput);
        appendMessage('chatbot', chatGPTResponse);

        userInputField.val('');
    });

    function appendMessage(role, content) {
        // const messageDiv = $('<div class="message">').addClass(role).text(content);
        const messageDiv = $('<div class="message">').text(content);
        chatContainer.append(messageDiv);
    }

    async function getChatGPTResponse(userInput) {
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ userInput }),
            });

            const data = await response.json();

            console.log(data);
            return data.chatbot;
        } catch (error) {
            console.error('Error making ChatGPT API request:', error.message);
            return '챗봇 응답을 가져오는 도중에 오류가 발생했습니다.';
        }
    }
});
