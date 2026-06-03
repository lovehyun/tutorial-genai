# 원격 MCP(Simple Net) – Docker + Nginx(TLS) 배포 & Claude Desktop 커넥터 연결 가이드

이 문서는 **Streamable HTTP 전송의 MCP 서버**를 Docker와 Nginx(TLS)로 **항시 가동** 배포하고, **Claude Desktop → Settings → Connectors**에서 **커스텀 커넥터**로 연결해 사용하는 전 과정을 정리한 것입니다.

> 엔드포인트 기본 경로는 **`/mcp`** 입니다.

---

## 사전 준비물

* 도메인(예: `yourdomain.com`)이 서버 공인 IP를 가리키도록 **DNS A 레코드** 설정
* 서버 방화벽에서 **80/443** 포트 허용
* 서버에 **Docker**, **Docker Compose** 설치
* 프로젝트에 아래 파일들이 준비되어 있다고 가정

  * `simple_net_server_http.py` (MCP HTTP 서버)
  * `Dockerfile`
  * `docker-compose.yml`
  * `nginx/conf.d/mcp.conf`
  * `nginx/certbot/conf/`, `nginx/certbot/www/` (인증서 디렉터리/웹루트)

---

## 배포 절차

### 1) 컨테이너 기동

```bash
docker compose up -d
```

> 이때 Nginx는 80/443 대기, 애플리케이션 컨테이너는 8080에서 MCP 서버(`/mcp`) 대기합니다.

---

### 2) 최초 인증서 발급 (HTTP-01)

```bash
docker compose run --rm certbot certonly \
  --webroot -w /var/www/certbot \
  -d YOUR_DOMAIN \
  -m YOUR_EMAIL --agree-tos --no-eff-email
```

* `YOUR_DOMAIN` / `YOUR_EMAIL`을 실제 값으로 바꿔주세요.
* HTTP-01 챌린지는 **포트 80**의 `/.well-known/acme-challenge/*` 경로를 사용합니다.

---

### 3) Nginx 재로드

```bash
docker compose exec nginx nginx -s reload
```

* 발급된 인증서(`fullchain.pem`, `privkey.pem`)를 읽어 \*\*HTTPS(443)\*\*에 적용합니다.
* 이후 `https://YOUR_DOMAIN/mcp` 가 **원격 MCP 엔드포인트**가 됩니다.

---

## Claude Desktop 커넥터 등록

**Settings → Connectors → Add custom connector**

* **Name**: `simple-net-remote` (아무 이름)
* **URL**: `https://YOUR_DOMAIN/mcp`

저장 후 **연결 테스트**를 실행합니다. 성공 시 **Tools 패널**에 서버가 나타나며, 대화 중 툴처럼 호출할 수 있습니다.

> 원격 MCP는 \*\*커넥터(Connectors)\*\*에서 추가해야 하며, 로컬 JSON 설정(`claude_desktop_config.json`)만으로는 연결되지 않습니다.

---

## 바로 써보는 프롬프트

* **핑 테스트**
  `simple-net-remote`의 `ping_host`로 `example.com` 3회 핑해줘.

* **주요 포트 상태**
  `check_common_ports`로 `example.com`의 22/80/443/3000/5000/8000 열림/닫힘 확인.

* **페이지 내용(80/5000)**
  `fetch_page`로 host=`example.com`, port=80, path=`/`의 내용 일부 보여줘.

---

## 운영 팁 & 보안

* **항시 가동 권장**: 원격 커넥터는 **URL이 즉시 응답 가능**해야 합니다. (서버리스는 콜드스타트 주의)
* **접근 제어**: 필요 시 **Nginx 레벨**에서 IP allowlist, Basic Auth, 토큰 검증 등 **추가 인증**을 적용하세요.
* **로그 정책**: \*\*프로토콜용 응답(HTTP)\*\*과 \*\*서버 로그(logging/stderr)\*\*를 **엄격히 분리**하세요. `print()`로 stdout 로그 출력 금지.
* **엔드포인트**: FastMCP HTTP 전송은 \*\*단일 엔드포인트 `/mcp`\*\*를 사용합니다.

---

## 트러블슈팅 체크리스트

* **HTTPS 접속 불가**

  * DNS A 레코드가 올바른지, 80/443 방화벽이 열려 있는지 확인
  * `docker compose logs nginx` / `docker compose logs certbot` 확인

* **인증서 발급 실패**

  * 80 포트에서 `/.well-known/acme-challenge/`가 제대로 응답되는지 확인
  * 기존 인증서/설정 충돌 여부 점검

* **커넥터 연결 실패**

  * `curl -i https://YOUR_DOMAIN/mcp`로 네트워크/프록시/경로 확인
  * Nginx의 location 매핑이 애플리케이션 `/mcp`와 **정확히 일치**하는지 확인

* **404/405 등 경로 이슈**

  * 슬래시(`/mcp` vs `/mcp/`)가 프록시/백엔드 모두 **일관**되게 설정되었는지 확인

---

## 참고 설정 예시(발췌)

**Nginx 프록시 (슬래시 일치 권장)**

```nginx
# 80: 인증서 발급 & HTTPS 리다이렉트
server {
    listen 80;
    server_name YOUR_DOMAIN;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    location / {
        return 301 https://$host$request_uri;
    }
}

# 443: TLS + MCP 역프록시
server {
    listen 443 ssl http2;
    server_name YOUR_DOMAIN;

    ssl_certificate     /etc/letsencrypt/live/YOUR_DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/YOUR_DOMAIN/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # MCP 엔드포인트
    location /mcp/ {
        proxy_pass http://app:8080/mcp/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**앱 컨테이너(발췌)**

```dockerfile
# Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY simple_net_server_http.py /app/
RUN pip install --no-cache-dir "mcp[cli]"
EXPOSE 8080
CMD ["python", "simple_net_server_http.py"]
```

---

## 요약 체크리스트

1. `docker compose up -d`
2. `certbot`로 인증서 발급 → `nginx -s reload`
3. 브라우저/`curl`로 `https://YOUR_DOMAIN/mcp` 확인
4. Claude → **Settings → Connectors → Add custom connector**

   * Name: 자유
   * URL: `https://YOUR_DOMAIN/mcp`
5. 대화에서 툴 호출 (`ping_host`, `check_common_ports`, `fetch_page`)
