document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("checkForm");

    form.addEventListener("submit", function(event) {
        event.preventDefault();

        // 결과 초기화
        const errorElem = document.getElementById("error");
        const codeContainer = document.getElementById("codeContainer");
        const analysisElem = document.getElementById("analysis");
        
        errorElem.innerText = "";
        codeContainer.innerText = "";
        analysisElem.innerText = "";

        const githubUrl = document.getElementById("github_url").value;

        fetch("/api/check", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ github_url: githubUrl })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                errorElem.innerText = data.error;
            } else {
                const codeLines = data.code.split("\n");

                // 각 라인을 순회하며 DOM 요소를 생성하여 추가
                /*
                codeLines.forEach((line, index) => {
                    // 새 div 생성
                    const lineDiv = document.createElement("div");
                    lineDiv.className = "code-line";
                    // 라인 번호를 표시할 span 생성
                    const lineNumberSpan = document.createElement("span");
                    lineNumberSpan.className = "line-number";
                    lineNumberSpan.innerText = (index + 1) + " ";

                    // 코드 내용은 textNode를 이용해 추가 (innerText/innerHTML 미사용)
                    const codeText = document.createTextNode(line);

                    // 생성한 요소들을 div에 추가
                    lineDiv.appendChild(lineNumberSpan);
                    lineDiv.appendChild(codeText);
                    
                    // 완성된 라인 div를 codeContainer에 추가
                    codeContainer.appendChild(lineDiv);
                });
                */

                // 분석 결과도 innerText를 이용해 추가 (분석 결과는 이미 텍스트로 반환된다고 가정)
                analysisElem.innerText = data.analysis;

                
                // 위에 긴~~ 코드를 아래 간결하게 정리 (그러나 innerHTML 로 하면 태그 이스케이핑 이슈가 있음)
                // 줄번호 + 코드 조합
                function escapeHTML(str) {
                    return str
                        .replace(/&/g, "&amp;")
                        .replace(/</g, "&lt;")
                        .replace(/>/g, "&gt;")
                        .replace(/"/g, "&quot;");
                }

                const html = codeLines.map((line, index) => {
                    return `<div class="code-line"><span class="line-number">${index + 1}</span> ${escapeHTML(line)}</div>`;
                }).join("");

                // 한번에 출력
                codeContainer.innerHTML = html;
            }
        })
        .catch(error => {
            errorElem.innerText = "요청 처리 중 에러 발생: " + error;
        });
    });
});
