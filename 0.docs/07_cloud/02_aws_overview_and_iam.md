# AWS 개요와 IAM

> 클라우드 컴퓨팅의 사실상 표준인 AWS — 글로벌 인프라 구조부터 핵심 서비스 카테고리, 계정 보안, IAM 권한 관리, CLI/SDK 실전 사용법까지, 클라우드 입문자를 위한 완전한 가이드를 제공합니다

---

## 1. AWS 글로벌 인프라

### 클라우드 인프라란 무엇인가

AWS(Amazon Web Services)는 전 세계에 분산된 물리적 데이터센터를 기반으로 수백 가지 클라우드 서비스를 제공하는 플랫폼입니다. 단순한 서버 임대를 넘어, 컴퓨팅·스토리지·네트워킹·데이터베이스·AI/ML까지 현대 애플리케이션에 필요한 모든 인프라를 API를 통해 수분 내에 프로비저닝할 수 있습니다.

AWS 글로벌 인프라를 이해하는 것은 높은 가용성, 낮은 지연시간, 규정 준수를 갖춘 아키텍처를 설계하는 첫 번째 단계입니다.

### 리전(Region) 개념

**리전(Region)**은 독립적인 지리적 위치에 있는 데이터센터 클러스터를 의미합니다. 2025년 기준 AWS는 전 세계 30개 이상의 리전을 운영하고 있으며, 각 리전은 완전히 독립적으로 동작합니다.

| 리전 코드 | 위치 | 특징 |
|-----------|------|------|
| `us-east-1` | 미국 버지니아 북부 | 가장 오래되고 서비스 수가 가장 많음 |
| `us-west-2` | 미국 오레곤 | 미국 서부 주요 리전 |
| `ap-northeast-2` | 한국 서울 | 한국 데이터 주권 요구사항 충족 |
| `ap-northeast-1` | 일본 도쿄 | 아시아 태평양 핵심 리전 |
| `eu-west-1` | 아일랜드 | 유럽 GDPR 규정 준수 |
| `ap-southeast-1` | 싱가포르 | 동남아시아 허브 |

### 리전 선택 기준

리전을 선택할 때는 단순히 가장 가까운 곳을 고르는 것이 아니라, 네 가지 기준을 종합적으로 검토해야 합니다.

| 기준 | 설명 | 체크포인트 |
|------|------|-----------|
| **지연시간(Latency)** | 최종 사용자와의 물리적 거리 | 사용자 대부분이 한국에 있으면 `ap-northeast-2` 선택 |
| **규정 준수(Compliance)** | 데이터 주권 및 법적 요구사항 | 개인정보보호법, GDPR, HIPAA 등 해당 규정 확인 |
| **서비스 가용성** | 신규 서비스가 모든 리전에 동시 출시되지 않음 | 필요한 서비스가 해당 리전에서 지원되는지 확인 |
| **비용** | 리전마다 서비스 가격이 다름 | `us-east-1`이 일반적으로 가장 저렴 |

> **핵심 포인트:** 한국 스타트업의 경우 대부분 `ap-northeast-2(서울)` 리전을 사용합니다. 사용자 지연시간이 낮고 국내 개인정보보호법 규정 준수가 용이하기 때문입니다. 글로벌 서비스를 준비한다면 멀티 리전 전략을 수립해야 합니다.

### 가용 영역(AZ, Availability Zone)

**가용 영역(AZ)**은 리전 내에 독립된 전력, 냉각, 네트워크를 갖춘 하나 이상의 데이터센터 집합입니다. 리전은 최소 2개, 보통 3~6개의 AZ로 구성됩니다.

AZ 간에는 고속 전용망(수 밀리초 미만의 지연시간)으로 연결되어 있어, 한 AZ에 장애가 발생해도 다른 AZ에서 서비스를 지속할 수 있습니다.

- `ap-northeast-2a` — 서울 AZ-A
- `ap-northeast-2b` — 서울 AZ-B
- `ap-northeast-2c` — 서울 AZ-C

고가용성 아키텍처를 설계할 때는 **최소 2개 이상의 AZ에 리소스를 분산**하는 것이 원칙입니다.

### 엣지 로케이션(Edge Location)과 CloudFront

**엣지 로케이션**은 리전보다 훨씬 많은 수(500개 이상)의 소규모 PoP(Point of Presence)입니다. 주로 CDN(Content Delivery Network) 서비스인 **Amazon CloudFront**가 이 엣지 로케이션을 활용하여 정적 콘텐츠(이미지, JS, CSS, 동영상)를 최종 사용자 가까이에서 캐싱하고 빠르게 제공합니다.

| 구성 요소 | 수 (2025 기준) | 주요 목적 |
|----------|----------------|---------|
| 리전 | 33개+ | 대부분의 AWS 서비스 실행 |
| 가용 영역 | 105개+ | 고가용성과 장애 격리 |
| 엣지 로케이션 | 550개+ | CloudFront CDN 캐싱 |
| 로컬 존 | 35개+ | 도심 지역 낮은 지연시간 |

### 로컬 존(Local Zone)

**로컬 존**은 대도시 지역에 배치된 AWS 인프라 확장으로, 해당 도시 사용자에게 한 자릿수 밀리초의 지연시간을 제공합니다. AWS의 컴퓨팅, 스토리지, 데이터베이스 서비스를 도시 근처에서 실행할 수 있어 실시간 게임, 미디어, 의료 등 초저지연이 요구되는 서비스에 적합합니다.

### AWS 글로벌 인프라 계층 구조

```mermaid
flowchart TB
    subgraph Global["AWS 글로벌 네트워크"]
        subgraph Region["리전 (Region) - 서울 ap-northeast-2"]
            subgraph AZ_A["가용 영역 A (ap-northeast-2a)"]
                DC_A1["데이터센터 1"]
                DC_A2["데이터센터 2"]
            end
            subgraph AZ_B["가용 영역 B (ap-northeast-2b)"]
                DC_B1["데이터센터 3"]
                DC_B2["데이터센터 4"]
            end
            subgraph AZ_C["가용 영역 C (ap-northeast-2c)"]
                DC_C1["데이터센터 5"]
            end
        end

        subgraph Edge["엣지 계층"]
            EL1["엣지 로케이션\n(서울, 부산...)"]
            LZ1["로컬 존\n(대도시 근처)"]
        end
    end

    User["최종 사용자"]
    User -->|"정적 콘텐츠\n(CloudFront)"| EL1
    User -->|"초저지연 앱"| LZ1
    EL1 -->|"오리진 요청"| Region
    LZ1 --> Region

    style DC_A1 fill:#0984e3,stroke:#74b9ff,color:#fff
    style DC_A2 fill:#0984e3,stroke:#74b9ff,color:#fff
    style DC_B1 fill:#0984e3,stroke:#74b9ff,color:#fff
    style DC_B2 fill:#0984e3,stroke:#74b9ff,color:#fff
    style DC_C1 fill:#0984e3,stroke:#74b9ff,color:#fff
    style EL1 fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style LZ1 fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style User fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style AZ_A fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
    style AZ_B fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
    style AZ_C fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
    style Region fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
    style Edge fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
    style Global fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
```

---

## 2. AWS 주요 서비스 카테고리

### 서비스 분류 개요

AWS는 200개 이상의 서비스를 제공합니다. 처음 접하면 압도적으로 느껴지지만, 주요 카테고리별로 정리하면 체계적으로 이해할 수 있습니다.

### 컴퓨팅(Compute)

애플리케이션을 실행하는 CPU/메모리 자원을 제공하는 서비스입니다.

| 서비스 | 설명 | 사용 시나리오 |
|--------|------|-------------|
| **EC2** (Elastic Compute Cloud) | 가상 서버 인스턴스 | 웹 서버, 배치 처리, 레거시 이전 |
| **Lambda** | 서버리스 함수 실행 | 이벤트 기반 처리, API 백엔드 |
| **ECS** (Elastic Container Service) | 컨테이너 관리 | Docker 기반 마이크로서비스 |
| **EKS** (Elastic Kubernetes Service) | 관리형 Kubernetes | 복잡한 컨테이너 오케스트레이션 |
| **Fargate** | 서버리스 컨테이너 | 서버 관리 없이 컨테이너 실행 |

### 스토리지(Storage)

데이터를 저장하고 관리하는 서비스입니다.

| 서비스 | 설명 | 사용 시나리오 |
|--------|------|-------------|
| **S3** (Simple Storage Service) | 객체 스토리지, 무제한 용량 | 파일, 이미지, 정적 웹 호스팅, 백업 |
| **EBS** (Elastic Block Store) | EC2에 연결하는 블록 스토리지 | 데이터베이스, OS 파일시스템 |
| **EFS** (Elastic File System) | 공유 네트워크 파일시스템 | 여러 EC2가 동시에 접근하는 파일 |
| **Glacier** | 장기 아카이브 스토리지 | 규정 준수용 로그, 백업 데이터 |

### 네트워킹(Networking)

클라우드 네트워크를 구성하고 트래픽을 제어하는 서비스입니다.

| 서비스 | 설명 | 사용 시나리오 |
|--------|------|-------------|
| **VPC** (Virtual Private Cloud) | 격리된 가상 네트워크 | 모든 AWS 리소스의 네트워크 기반 |
| **Route 53** | DNS 서비스 | 도메인 관리, 트래픽 라우팅 |
| **CloudFront** | CDN 서비스 | 전 세계 콘텐츠 빠른 전달 |
| **ALB/NLB** | 로드 밸런서 | 트래픽 분산, 헬스 체크 |
| **API Gateway** | REST/WebSocket API 관리 | 서버리스 API, 인증 통합 |

### 데이터베이스(Database)

다양한 유형의 데이터베이스를 관리형으로 제공합니다.

| 서비스 | 유형 | 사용 시나리오 |
|--------|------|-------------|
| **RDS** | 관계형 DB (MySQL, PostgreSQL 등) | 트랜잭션 데이터, OLTP |
| **Aurora** | 고성능 관계형 DB | 고가용성이 필요한 RDS 대체 |
| **DynamoDB** | NoSQL 키-값/문서 DB | 고성능, 자동 확장이 필요한 데이터 |
| **ElastiCache** | 인메모리 캐시 (Redis/Memcached) | 세션, API 캐시, 실시간 리더보드 |
| **OpenSearch** | 검색 엔진 | 로그 분석, 전문 검색 |

### 보안(Security)

클라우드 자원을 안전하게 보호하는 서비스입니다.

| 서비스 | 설명 | 사용 시나리오 |
|--------|------|-------------|
| **IAM** | 접근 권한 관리 | 모든 AWS 리소스 접근 제어 |
| **KMS** | 암호화 키 관리 | 데이터 암호화, 키 순환 |
| **WAF** | 웹 방화벽 | SQL 인젝션, XSS 방어 |
| **Shield** | DDoS 보호 | 분산 서비스 거부 공격 방어 |
| **GuardDuty** | 위협 탐지 | 비정상 활동 자동 감지 |
| **Secrets Manager** | 비밀값 관리 | DB 비밀번호, API 키 안전 저장 |

### AWS 서비스 카테고리 맵

```mermaid
flowchart LR
    subgraph Compute["컴퓨팅"]
        direction TB
        EC2["EC2\n가상 서버"]
        Lambda["Lambda\n서버리스"]
        ECS["ECS/EKS\n컨테이너"]
    end

    subgraph Storage["스토리지"]
        direction TB
        S3["S3\n객체 스토리지"]
        EBS["EBS\n블록 스토리지"]
        EFS["EFS\n파일 시스템"]
    end

    subgraph Network["네트워킹"]
        direction TB
        VPC["VPC\n가상 네트워크"]
        R53["Route 53\nDNS"]
        CF["CloudFront\nCDN"]
    end

    subgraph Database["데이터베이스"]
        direction TB
        RDS["RDS\n관계형 DB"]
        DDB["DynamoDB\nNoSQL"]
        EC["ElastiCache\n캐시"]
    end

    subgraph Security["보안"]
        direction TB
        IAM["IAM\n권한 관리"]
        KMS["KMS\n암호화"]
        WAF["WAF\n방화벽"]
    end

    App["애플리케이션"]
    App --> Compute
    App --> Storage
    App --> Network
    App --> Database
    App --> Security

    style EC2 fill:#e17055,stroke:#fab1a0,color:#fff
    style Lambda fill:#e17055,stroke:#fab1a0,color:#fff
    style ECS fill:#e17055,stroke:#fab1a0,color:#fff
    style S3 fill:#0984e3,stroke:#74b9ff,color:#fff
    style EBS fill:#0984e3,stroke:#74b9ff,color:#fff
    style EFS fill:#0984e3,stroke:#74b9ff,color:#fff
    style VPC fill:#00b894,stroke:#55efc4,color:#fff
    style R53 fill:#00b894,stroke:#55efc4,color:#fff
    style CF fill:#00b894,stroke:#55efc4,color:#fff
    style RDS fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style DDB fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style EC fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style IAM fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style KMS fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style WAF fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style App fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
    style Compute fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
    style Storage fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
    style Network fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
    style Database fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
    style Security fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
```

---

## 3. AWS 계정 구조

### AWS 계정 기본 개념

AWS 계정은 모든 서비스와 리소스의 경계(boundary)입니다. 계정마다 독립된 청구, 리소스, 권한 범위를 가집니다. 처음 AWS 계정을 만들면 모든 권한을 가진 **루트 계정(Root Account)**이 생성됩니다.

### Root 계정 보안

루트 계정은 AWS 계정의 최고 관리자 계정으로, 계정 자체를 삭제하거나 결제 정보를 변경하는 등의 작업만 수행하고 **일상적인 작업에는 절대 사용하지 않아야** 합니다.

| 보안 조치 | 설명 | 중요도 |
|----------|------|--------|
| **MFA 활성화** | 루트 계정 로그인 시 OTP 2단계 인증 | 필수 |
| **액세스 키 삭제** | 루트 계정의 프로그래밍 방식 접근 차단 | 필수 |
| **일상 작업 금지** | 루트 대신 IAM 관리자 계정 사용 | 필수 |
| **이메일 알림** | 루트 계정 로그인 시 이메일 통보 설정 | 권장 |
| **강력한 비밀번호** | 20자 이상 복잡한 비밀번호 사용 | 필수 |

> **핵심 포인트:** 루트 계정으로 일상 업무를 하는 것은 회사 서버 관리자 계정으로 인터넷 서핑을 하는 것과 같습니다. 실수 하나가 전체 계정의 모든 리소스에 영향을 미칠 수 있습니다. 처음 AWS 계정을 만들면 제일 먼저 루트 계정에 MFA를 설정하고, IAM 관리자 계정을 별도로 만드세요.

### AWS Organizations

여러 AWS 계정을 중앙에서 관리하는 서비스입니다. 기업 환경에서는 개발(dev)/스테이징(staging)/프로덕션(prod) 환경을 각각 별도 계정으로 분리하는 것이 모범 사례입니다.

| 기능 | 설명 |
|------|------|
| **통합 결제** | 모든 계정의 비용을 한 곳에서 관리 |
| **SCP** (Service Control Policy) | 특정 서비스 사용 제한(예: 특정 리전만 허용) |
| **계정 계층 구조** | OU(Organizational Unit)로 계정 그룹화 |
| **볼륨 할인** | 사용량을 합산하여 할인 적용 |

### 결제 알림 설정

초보자가 AWS 사용 중 가장 빈번하게 발생하는 문제는 **예상치 못한 과금**입니다. 반드시 결제 알림을 설정해야 합니다.

```bash
# AWS CLI로 결제 알림 설정 (Billing Alert)
# 1. 결제 알림 활성화 (콘솔에서 수동으로 활성화해야 함)
# Billing Dashboard → Billing preferences → Receive Billing Alerts 체크

# 2. CloudWatch 알람 생성 (월 $10 초과 시 알림)
aws cloudwatch put-metric-alarm \
  --alarm-name "BillingAlert-10USD" \
  --alarm-description "월 사용 요금 $10 초과 알림" \
  --metric-name EstimatedCharges \
  --namespace AWS/Billing \
  --statistic Maximum \
  --period 86400 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=Currency,Value=USD \
  --evaluation-periods 1 \
  --alarm-actions arn:aws:sns:us-east-1:123456789012:BillingAlert \
  --region us-east-1
```

### AWS 프리 티어(Free Tier)

AWS는 신규 계정에 대해 12개월간 프리 티어를 제공합니다. 학습과 개발 환경 구성에 충분한 무료 자원을 제공합니다.

| 서비스 | 프리 티어 한도 | 유형 |
|--------|--------------|------|
| **EC2** | t2.micro/t3.micro 750시간/월 | 12개월 |
| **S3** | 5 GB 스토리지, GET 20,000건 | 12개월 |
| **RDS** | db.t2.micro 750시간/월 | 12개월 |
| **Lambda** | 100만 요청/월 | 영구 무료 |
| **DynamoDB** | 25 GB 스토리지 | 영구 무료 |
| **CloudFront** | 1 TB 데이터 전송/월 | 12개월 |

---

## 4. IAM 기초

### IAM이란

**IAM(Identity and Access Management)**은 AWS 리소스에 대한 접근을 안전하게 제어하는 서비스입니다. 누가(Who), 어떤 조건에서(Condition), 어떤 자원에(Resource), 어떤 행동을(Action) 할 수 있는지 정의합니다.

IAM에는 크게 네 가지 핵심 개념이 있습니다.

### IAM 사용자(User)

특정 개인 또는 애플리케이션을 나타내는 AWS 계정 내의 엔티티입니다.

- 콘솔 로그인을 위한 **사용자 이름/비밀번호** 자격증명
- 프로그래밍 방식 접근을 위한 **액세스 키 ID/시크릿 액세스 키** 자격증명
- 하나의 계정에 최대 5,000명의 IAM 사용자 생성 가능

### IAM 그룹(Group)

여러 IAM 사용자의 집합입니다. 그룹에 정책을 연결하면 그룹 내 모든 사용자가 해당 권한을 상속받습니다.

- 예: `Developers` 그룹에 EC2/S3/RDS 접근 정책 부여
- 예: `Admins` 그룹에 전체 관리 권한 부여
- 그룹은 다른 그룹을 포함할 수 없음(1단계 계층)

### IAM 역할(Role)

사용자가 아닌 **AWS 서비스나 외부 ID 제공자**에게 임시 권한을 부여하는 메커니즘입니다.

- EC2 인스턴스가 S3에 접근하기 위해 역할 사용
- Lambda 함수가 DynamoDB에 접근하기 위해 역할 사용
- 타 계정(Cross-Account) 접근 허용
- 임시 자격증명(STS 토큰)을 발급받아 사용

### IAM 정책(Policy)

권한을 정의하는 JSON 문서입니다. **어떤 서비스의 어떤 작업**을 **어떤 리소스**에 대해 허용 또는 거부할지 명시합니다.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowS3ReadOnly",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::my-bucket",
        "arn:aws:s3:::my-bucket/*"
      ]
    }
  ]
}
```

정책의 핵심 구성 요소를 정리하면 다음과 같습니다.

| 요소 | 설명 | 예시 |
|------|------|------|
| `Version` | 정책 언어 버전 | `"2012-10-17"` (고정값) |
| `Statement` | 권한 규칙 목록 (배열) | 여러 규칙 포함 가능 |
| `Sid` | Statement ID (선택적) | 규칙 식별을 위한 이름 |
| `Effect` | 허용 또는 거부 | `"Allow"` 또는 `"Deny"` |
| `Action` | 허용/거부할 AWS API 작업 | `"s3:GetObject"`, `"ec2:*"` |
| `Resource` | 적용 대상 리소스 ARN | `"arn:aws:s3:::bucket-name"` |
| `Condition` | 적용 조건 (선택적) | IP 범위, MFA 여부, 시간대 등 |

### 최소 권한 원칙(Least Privilege)

IAM 설계의 가장 중요한 원칙입니다. **작업에 필요한 최소한의 권한만 부여**하고, 필요 없어진 권한은 즉시 제거합니다.

| 나쁜 예 | 좋은 예 |
|--------|--------|
| 개발자에게 `AdministratorAccess` 부여 | 개발자에게 필요한 서비스만 허용 |
| EC2에 `S3FullAccess` 역할 부여 | EC2에 특정 버킷 읽기 권한만 부여 |
| 임시 작업 후 권한 방치 | 작업 완료 후 임시 권한 즉시 제거 |
| 와일드카드 `*` 남용 | 구체적인 리소스 ARN 명시 |

### IAM 엔티티 관계도

```mermaid
flowchart TB
    subgraph Account["AWS 계정"]
        subgraph Users["IAM 사용자"]
            U1["사용자\nalice"]
            U2["사용자\nbob"]
            U3["사용자\ncharlie"]
        end

        subgraph Groups["IAM 그룹"]
            G1["그룹\nDevelopers"]
            G2["그룹\nAdmins"]
        end

        subgraph Roles["IAM 역할"]
            R1["역할\nEC2-S3-Role"]
            R2["역할\nLambda-DynamoDB-Role"]
            R3["역할\nCrossAccount-Role"]
        end

        subgraph Policies["IAM 정책"]
            P1["정책\nS3ReadOnly"]
            P2["정책\nEC2FullAccess"]
            P3["정책\nAdminPolicy"]
            P4["정책\nDynamoDBWrite"]
        end

        subgraph Resources["AWS 리소스"]
            S3["S3 버킷"]
            EC2_R["EC2 인스턴스"]
            DDB["DynamoDB"]
        end
    end

    U1 -->|"멤버"| G1
    U2 -->|"멤버"| G1
    U3 -->|"멤버"| G2
    G1 -->|"정책 연결"| P1
    G1 -->|"정책 연결"| P2
    G2 -->|"정책 연결"| P3
    R1 -->|"정책 연결"| P1
    R2 -->|"정책 연결"| P4
    P1 -->|"접근 허용"| S3
    P2 -->|"접근 허용"| EC2_R
    P3 -->|"접근 허용"| S3
    P3 -->|"접근 허용"| EC2_R
    P4 -->|"접근 허용"| DDB

    style U1 fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style U2 fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style U3 fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style G1 fill:#0984e3,stroke:#74b9ff,color:#fff
    style G2 fill:#0984e3,stroke:#74b9ff,color:#fff
    style R1 fill:#e17055,stroke:#fab1a0,color:#fff
    style R2 fill:#e17055,stroke:#fab1a0,color:#fff
    style R3 fill:#e17055,stroke:#fab1a0,color:#fff
    style P1 fill:#00b894,stroke:#55efc4,color:#fff
    style P2 fill:#00b894,stroke:#55efc4,color:#fff
    style P3 fill:#00b894,stroke:#55efc4,color:#fff
    style P4 fill:#00b894,stroke:#55efc4,color:#fff
    style S3 fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style EC2_R fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style DDB fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style Users fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
    style Groups fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
    style Roles fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
    style Policies fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
    style Resources fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
    style Account fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
```

### ARN(Amazon Resource Name) 이해

AWS의 모든 리소스는 고유한 ARN을 가집니다. 정책에서 리소스를 특정할 때 사용합니다.

```
arn:partition:service:region:account-id:resource-type/resource-id

예시:
arn:aws:s3:::my-bucket                          # S3 버킷
arn:aws:s3:::my-bucket/images/*                 # 버킷 내 images 폴더
arn:aws:ec2:ap-northeast-2:123456789012:instance/i-1234567890abcdef0
arn:aws:iam::123456789012:user/alice             # IAM 사용자
arn:aws:iam::123456789012:role/EC2-S3-Role       # IAM 역할
```

---

## 5. IAM 실전

### 개발자용 IAM 정책 설계 예시

실제 개발 환경에서 활용할 수 있는 세분화된 IAM 정책 예시들을 살펴봅니다.

#### S3 읽기 전용 정책

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ListAllBuckets",
      "Effect": "Allow",
      "Action": "s3:ListAllMyBuckets",
      "Resource": "*"
    },
    {
      "Sid": "ReadSpecificBucket",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:GetObjectVersion",
        "s3:ListBucket",
        "s3:GetBucketLocation"
      ],
      "Resource": [
        "arn:aws:s3:::my-app-bucket",
        "arn:aws:s3:::my-app-bucket/*"
      ]
    }
  ]
}
```

#### 특정 리전 EC2 관리 정책

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "EC2SeoulRegionOnly",
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances",
        "ec2:StartInstances",
        "ec2:StopInstances",
        "ec2:RebootInstances"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "aws:RequestedRegion": "ap-northeast-2"
        }
      }
    },
    {
      "Sid": "DenyOtherRegions",
      "Effect": "Deny",
      "Action": "ec2:*",
      "Resource": "*",
      "Condition": {
        "StringNotEquals": {
          "aws:RequestedRegion": "ap-northeast-2"
        }
      }
    }
  ]
}
```

#### 태그 기반 리소스 접근 정책

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "EC2TagBasedAccess",
      "Effect": "Allow",
      "Action": [
        "ec2:StartInstances",
        "ec2:StopInstances"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "ec2:ResourceTag/Environment": "development",
          "ec2:ResourceTag/Team": "${aws:username}"
        }
      }
    }
  ]
}
```

### MFA(다중 인증) 설정

MFA는 비밀번호 외에 추가 인증 수단을 요구하여 계정 보안을 크게 강화합니다.

```bash
# AWS CLI로 MFA 디바이스 확인
aws iam list-mfa-devices --user-name alice

# MFA 가상 디바이스 생성 (Google Authenticator 등 사용)
aws iam create-virtual-mfa-device \
  --virtual-mfa-device-name alice-mfa \
  --outfile ./alice-mfa.png \
  --bootstrap-method QRCodePNG

# MFA 디바이스 활성화 (OTP 연속 2회 입력 필요)
aws iam enable-mfa-device \
  --user-name alice \
  --serial-number arn:aws:iam::123456789012:mfa/alice-mfa \
  --authentication-code1 123456 \
  --authentication-code2 789012
```

MFA를 필수로 요구하는 정책을 추가하면, MFA 없이 로그인한 경우 모든 작업을 거부할 수 있습니다.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyWithoutMFA",
      "Effect": "Deny",
      "NotAction": [
        "iam:CreateVirtualMFADevice",
        "iam:EnableMFADevice",
        "iam:GetUser",
        "iam:ListMFADevices",
        "sts:GetSessionToken"
      ],
      "Resource": "*",
      "Condition": {
        "BoolIfExists": {
          "aws:MultiFactorAuthPresent": "false"
        }
      }
    }
  ]
}
```

### 임시 자격증명(STS AssumeRole)

**AWS STS(Security Token Service)**는 임시 보안 자격증명을 생성하는 서비스입니다. 장기 자격증명(액세스 키) 대신 수명이 짧은 임시 토큰을 사용하는 것이 보안상 훨씬 안전합니다.

```python
# assume_role_example.py -- STS AssumeRole로 임시 자격증명 획득
import boto3
import json

# STS 클라이언트 생성
sts_client = boto3.client('sts')

# 역할 Assume (임시 자격증명 획득)
response = sts_client.assume_role(
    RoleArn='arn:aws:iam::123456789012:role/EC2-S3-Role',
    RoleSessionName='my-session',
    DurationSeconds=3600  # 1시간 유효
)

credentials = response['Credentials']
print(f"AccessKeyId: {credentials['AccessKeyId']}")
print(f"Expiration: {credentials['Expiration']}")

# 임시 자격증명으로 S3 접근
s3_client = boto3.client(
    's3',
    aws_access_key_id=credentials['AccessKeyId'],
    aws_secret_access_key=credentials['SecretAccessKey'],
    aws_session_token=credentials['SessionToken']
)

response = s3_client.list_buckets()
for bucket in response['Buckets']:
    print(f"버킷: {bucket['Name']}")
```

### 교차 계정(Cross-Account) 접근

여러 AWS 계정을 운영할 때, 계정 A에서 계정 B의 리소스에 접근하는 패턴입니다. 개발 계정에서 프로덕션 계정의 읽기 전용 데이터에 접근하는 경우 등에 활용합니다.

```bash
# 1. 프로덕션 계정(계정 B)에서 역할 생성
# Trust Policy: 개발 계정(계정 A)이 이 역할을 Assume할 수 있도록 허용
cat > trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::111111111111:root"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "Bool": {
          "aws:MultiFactorAuthPresent": "true"
        }
      }
    }
  ]
}
EOF

aws iam create-role \
  --role-name CrossAccountReadOnly \
  --assume-role-policy-document file://trust-policy.json

# 2. 역할에 권한 정책 연결
aws iam attach-role-policy \
  --role-name CrossAccountReadOnly \
  --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess

# 3. 개발 계정(계정 A)에서 역할 Assume
aws sts assume-role \
  --role-arn arn:aws:iam::222222222222:role/CrossAccountReadOnly \
  --role-session-name dev-access \
  --serial-number arn:aws:iam::111111111111:mfa/alice \
  --token-code 123456
```

### IAM 인증 흐름

```mermaid
flowchart TB
    User["사용자"] -->|"요청"| Cred["자격증명 제시"]
    Cred --> MFA{"MFA 필요?"}
    MFA -->|"Yes"| OTP["OTP 입력"] --> IAM["IAM 정책 평가"]
    MFA -->|"No"| IAM
    IAM --> Deny_Check{"Deny 존재?"}
    Deny_Check -->|"Yes"| Deny["거부 403"]
    Deny_Check -->|"No"| Allow_Check{"Allow 존재?"}
    Allow_Check -->|"No"| Deny
    Allow_Check -->|"Yes"| Allow["허용"] --> Resource["AWS 리소스"]

    style User fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style Cred fill:#0984e3,stroke:#74b9ff,color:#fff
    style MFA fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style OTP fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style IAM fill:#0984e3,stroke:#74b9ff,color:#fff
    style Deny_Check fill:#e17055,stroke:#fab1a0,color:#fff
    style Allow_Check fill:#e17055,stroke:#fab1a0,color:#fff
    style Deny fill:#e17055,stroke:#fab1a0,color:#fff
    style Allow fill:#00b894,stroke:#55efc4,color:#fff
    style Resource fill:#00b894,stroke:#55efc4,color:#fff
```

> **핵심 포인트:** IAM 정책 평가 순서는 명시적 Deny → 명시적 Allow → 묵시적 Deny(기본 거부)입니다. AWS는 기본적으로 모든 접근을 거부하며, Allow 정책이 명시된 경우에만 허용됩니다. Deny 정책은 Always Allow를 덮어씁니다.

---

## 6. AWS CLI와 SDK

### AWS CLI 설치

AWS CLI(Command Line Interface)는 터미널에서 AWS 서비스를 제어하는 도구입니다. 자동화 스크립트 작성, 배포 파이프라인 구성, 빠른 리소스 조회에 필수적입니다.

```bash
# macOS (Homebrew)
brew install awscli

# Linux (공식 설치 스크립트)
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Windows (MSI 설치 파일)
# https://awscli.amazonaws.com/AWSCLIV2.msi 다운로드 후 실행

# 설치 확인
aws --version
# aws-cli/2.x.x Python/3.x.x ...
```

### aws configure 설정

AWS CLI를 처음 설치한 뒤 자격증명과 기본 설정을 입력합니다.

```bash
aws configure
# AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
# AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
# Default region name [None]: ap-northeast-2
# Default output format [None]: json
```

설정이 완료되면 아래 파일들이 생성됩니다.

```ini
# ~/.aws/credentials
[default]
aws_access_key_id = AKIAIOSFODNN7EXAMPLE
aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

# ~/.aws/config
[default]
region = ap-northeast-2
output = json
```

### 복수 프로파일 설정

개인 계정과 회사 계정, 개발/프로덕션 환경을 분리할 때 **명명 프로파일(Named Profile)**을 사용합니다.

```bash
# 프로파일 추가
aws configure --profile company-dev
aws configure --profile company-prod

# 결과로 생성되는 ~/.aws/credentials
```

```ini
# ~/.aws/credentials (멀티 프로파일 예시)
[default]
aws_access_key_id = AKIAI_PERSONAL_KEY
aws_secret_access_key = personal_secret_key

[company-dev]
aws_access_key_id = AKIAI_DEV_KEY
aws_secret_access_key = dev_secret_key

[company-prod]
aws_access_key_id = AKIAI_PROD_KEY
aws_secret_access_key = prod_secret_key
```

```ini
# ~/.aws/config (멀티 프로파일 설정)
[default]
region = ap-northeast-2
output = json

[profile company-dev]
region = ap-northeast-2
output = json

[profile company-prod]
region = us-east-1
output = table
```

```bash
# 프로파일을 지정하여 명령 실행
aws s3 ls --profile company-dev
aws ec2 describe-instances --profile company-prod

# 환경변수로 프로파일 지정
export AWS_PROFILE=company-dev
aws s3 ls  # company-dev 프로파일 사용

# 환경변수로 임시 자격증명 직접 지정
export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG
export AWS_DEFAULT_REGION=ap-northeast-2
```

### 자주 사용하는 AWS CLI 명령

```bash
# ── S3 명령 ──
# 버킷 목록 조회
aws s3 ls

# 특정 버킷 내용 조회
aws s3 ls s3://my-bucket/

# 파일 업로드
aws s3 cp local-file.txt s3://my-bucket/path/file.txt

# 폴더 동기화
aws s3 sync ./local-dir s3://my-bucket/remote-dir

# 파일 다운로드
aws s3 cp s3://my-bucket/file.txt ./local-file.txt

# ── EC2 명령 ──
# 인스턴스 목록 (JSON)
aws ec2 describe-instances

# 실행 중인 인스턴스만 조회
aws ec2 describe-instances \
  --filters "Name=instance-state-name,Values=running"

# 특정 인스턴스 시작/정지
aws ec2 start-instances --instance-ids i-1234567890abcdef0
aws ec2 stop-instances --instance-ids i-1234567890abcdef0

# ── IAM 명령 ──
# 사용자 목록
aws iam list-users

# 현재 자격증명 확인
aws sts get-caller-identity

# ── 결과 필터링 (--query 옵션) ──
# 인스턴스 ID와 퍼블릭 IP만 출력
aws ec2 describe-instances \
  --query "Reservations[].Instances[].[InstanceId, PublicIpAddress]" \
  --output table
```

### boto3 Python SDK 설치와 기본 사용

**boto3**는 Python에서 AWS 서비스를 사용하기 위한 공식 SDK입니다. AWS CLI와 동일한 `~/.aws/credentials` 설정을 사용합니다.

```bash
pip install boto3
```

### boto3 S3 예제

```python
# boto3_s3_example.py -- S3 버킷 목록 조회 및 파일 업로드/다운로드
import boto3
from botocore.exceptions import ClientError
import os

# S3 클라이언트 생성
# 자격증명은 ~/.aws/credentials 또는 환경변수에서 자동으로 로드됨
s3 = boto3.client('s3', region_name='ap-northeast-2')

# ── 버킷 목록 조회 ──
def list_buckets():
    response = s3.list_buckets()
    print("=== S3 버킷 목록 ===")
    for bucket in response['Buckets']:
        print(f"  {bucket['Name']} (생성: {bucket['CreationDate'].strftime('%Y-%m-%d')})")

# ── 버킷 내 객체 목록 ──
def list_objects(bucket_name, prefix=''):
    response = s3.list_objects_v2(
        Bucket=bucket_name,
        Prefix=prefix
    )
    if 'Contents' not in response:
        print(f"버킷 '{bucket_name}'에 객체가 없습니다.")
        return

    print(f"=== {bucket_name}/{prefix} 객체 목록 ===")
    for obj in response['Contents']:
        size_kb = obj['Size'] / 1024
        print(f"  {obj['Key']} ({size_kb:.1f} KB)")

# ── 파일 업로드 ──
def upload_file(local_path, bucket_name, s3_key):
    try:
        s3.upload_file(local_path, bucket_name, s3_key)
        print(f"업로드 완료: {local_path} -> s3://{bucket_name}/{s3_key}")
    except ClientError as e:
        print(f"업로드 실패: {e}")

# ── 파일 다운로드 ──
def download_file(bucket_name, s3_key, local_path):
    try:
        s3.download_file(bucket_name, s3_key, local_path)
        print(f"다운로드 완료: s3://{bucket_name}/{s3_key} -> {local_path}")
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            print(f"객체를 찾을 수 없음: {s3_key}")
        else:
            print(f"다운로드 실패: {e}")

# ── Presigned URL 생성 (임시 공개 링크) ──
def generate_presigned_url(bucket_name, s3_key, expiration=3600):
    url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket_name, 'Key': s3_key},
        ExpiresIn=expiration
    )
    print(f"Presigned URL (유효: {expiration}초):")
    print(url)
    return url

# 실행 예시
if __name__ == '__main__':
    BUCKET = 'my-app-bucket'

    list_buckets()
    list_objects(BUCKET, prefix='images/')
    upload_file('./logo.png', BUCKET, 'images/logo.png')
    download_file(BUCKET, 'images/logo.png', '/tmp/logo_downloaded.png')
    generate_presigned_url(BUCKET, 'images/logo.png', expiration=300)
```

### boto3 EC2 예제

```python
# boto3_ec2_example.py -- EC2 인스턴스 조회 및 제어
import boto3
from datetime import datetime

ec2 = boto3.client('ec2', region_name='ap-northeast-2')
ec2_resource = boto3.resource('ec2', region_name='ap-northeast-2')

# ── 인스턴스 목록 조회 ──
def list_instances():
    response = ec2.describe_instances()
    print("=== EC2 인스턴스 목록 ===")

    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            # 태그에서 이름 추출
            name = ''
            for tag in instance.get('Tags', []):
                if tag['Key'] == 'Name':
                    name = tag['Value']

            print(f"  ID: {instance['InstanceId']}")
            print(f"  이름: {name}")
            print(f"  타입: {instance['InstanceType']}")
            print(f"  상태: {instance['State']['Name']}")
            print(f"  퍼블릭 IP: {instance.get('PublicIpAddress', 'N/A')}")
            print()

# ── 실행 중인 인스턴스만 필터 ──
def list_running_instances():
    response = ec2.describe_instances(
        Filters=[
            {'Name': 'instance-state-name', 'Values': ['running']},
            {'Name': 'tag:Environment', 'Values': ['production']}
        ]
    )

    instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instances.append({
                'id': instance['InstanceId'],
                'type': instance['InstanceType'],
                'ip': instance.get('PublicIpAddress', 'N/A')
            })
    return instances

# ── 인스턴스 시작/정지 ──
def control_instance(instance_id, action):
    if action == 'start':
        ec2.start_instances(InstanceIds=[instance_id])
        print(f"인스턴스 {instance_id} 시작 요청 완료")
    elif action == 'stop':
        ec2.stop_instances(InstanceIds=[instance_id])
        print(f"인스턴스 {instance_id} 정지 요청 완료")

# ── 인스턴스 시작 대기 ──
def wait_for_running(instance_id):
    print(f"인스턴스 {instance_id} 실행 대기 중...")
    waiter = ec2.get_waiter('instance_running')
    waiter.wait(InstanceIds=[instance_id])
    print("인스턴스 실행 완료!")

if __name__ == '__main__':
    list_instances()
    running = list_running_instances()
    print(f"프로덕션 실행 중 인스턴스: {len(running)}개")
```

### boto3 IAM 예제

```python
# boto3_iam_example.py -- IAM 사용자 및 정책 관리
import boto3
import json

iam = boto3.client('iam')

# ── IAM 사용자 목록 조회 ──
def list_iam_users():
    response = iam.list_users()
    print("=== IAM 사용자 목록 ===")
    for user in response['Users']:
        print(f"  사용자명: {user['UserName']}")
        print(f"  ARN: {user['Arn']}")
        print(f"  생성일: {user['CreateDate'].strftime('%Y-%m-%d')}")
        print()

# ── 현재 자격증명 정보 확인 ──
def get_caller_identity():
    sts = boto3.client('sts')
    identity = sts.get_caller_identity()
    print("=== 현재 자격증명 정보 ===")
    print(f"  계정 ID: {identity['Account']}")
    print(f"  사용자 ARN: {identity['Arn']}")
    print(f"  UserID: {identity['UserId']}")

# ── 사용자의 연결된 정책 조회 ──
def list_user_policies(username):
    # 직접 연결된 정책
    attached = iam.list_attached_user_policies(UserName=username)
    print(f"=== {username}의 연결된 정책 ===")
    for policy in attached['AttachedPolicies']:
        print(f"  정책명: {policy['PolicyName']}")
        print(f"  ARN: {policy['PolicyArn']}")

    # 인라인 정책
    inline = iam.list_user_policies(UserName=username)
    if inline['PolicyNames']:
        print(f"  인라인 정책: {', '.join(inline['PolicyNames'])}")

if __name__ == '__main__':
    get_caller_identity()
    list_iam_users()
```

### 세션과 리소스 vs 클라이언트

boto3에는 두 가지 추상화 레벨이 있습니다.

| 항목 | Client | Resource |
|------|--------|----------|
| **레벨** | 저수준 (Low-level) | 고수준 (High-level) |
| **응답 형식** | 딕셔너리(JSON) | Python 객체 |
| **모든 서비스 지원** | 모두 지원 | 일부 서비스만 지원 |
| **사용 예시** | `boto3.client('s3')` | `boto3.resource('s3')` |

```python
import boto3

# Client 방식 (저수준)
s3_client = boto3.client('s3')
response = s3_client.get_object(Bucket='my-bucket', Key='file.txt')
content = response['Body'].read().decode('utf-8')

# Resource 방식 (고수준, 더 직관적)
s3_resource = boto3.resource('s3')
bucket = s3_resource.Bucket('my-bucket')
obj = bucket.Object('file.txt')
content = obj.get()['Body'].read().decode('utf-8')

# 특정 프로파일로 세션 생성
session = boto3.Session(profile_name='company-dev')
s3 = session.client('s3')
```

---

## 7. 핵심 정리

### 이번 강의 요약

| 주제 | 핵심 내용 | 실무 적용 포인트 |
|------|-----------|----------------|
| **AWS 글로벌 인프라** | 리전 > AZ > 엣지 로케이션 계층 구조 | 서울 리전 + 멀티 AZ로 고가용성 설계 |
| **리전 선택** | 지연시간, 규정 준수, 서비스 가용성, 비용 | 한국 서비스는 `ap-northeast-2` 기본 |
| **AWS 서비스 카테고리** | 컴퓨팅/스토리지/네트워킹/DB/보안 | 필요한 서비스를 카테고리로 탐색 |
| **계정 보안** | 루트 계정 MFA, IAM 관리자 분리 | 루트 계정 일상 사용 절대 금지 |
| **IAM 핵심 4요소** | 사용자, 그룹, 역할, 정책 | 그룹에 정책 연결, 사용자는 그룹에 배치 |
| **최소 권한 원칙** | 필요한 최소 권한만 부여 | 와일드카드 `*` 최소화, 구체적 ARN 사용 |
| **임시 자격증명** | STS AssumeRole로 단기 토큰 발급 | 장기 액세스 키보다 역할 사용 권장 |
| **AWS CLI/boto3** | 터미널과 Python에서 AWS 제어 | `~/.aws/credentials` 프로파일 분리 |

### IAM 설계 체크리스트

클라우드 프로젝트를 시작할 때 반드시 확인해야 할 IAM 관련 항목들입니다.

| 체크 항목 | 이유 |
|----------|------|
| 루트 계정 MFA 활성화 | 루트 계정 탈취 시 전체 계정 위험 |
| 루트 계정 액세스 키 삭제 | 프로그래밍 방식 루트 접근 차단 |
| IAM 관리자 계정 별도 생성 | 루트 대신 일상 관리에 사용 |
| 개발자/운영자 그룹 분리 | 역할별 적절한 권한 관리 |
| 프로덕션 IAM 사용자 최소화 | 역할 사용 권장 |
| 미사용 IAM 사용자/키 정리 | 불필요한 공격 표면 제거 |
| CloudTrail 활성화 | 모든 API 호출 감사 로그 |
| 결제 알림 설정 | 예상치 못한 과금 방지 |

### 자주 발생하는 AWS 초보자 실수

| 실수 | 결과 | 예방 방법 |
|------|------|----------|
| 루트 계정으로 모든 작업 | 계정 전체 보안 위험 | IAM 관리자 계정 사용 |
| 액세스 키를 코드에 하드코딩 | 키 노출 시 과금 폭탄 | 환경변수 또는 IAM 역할 사용 |
| 결제 알림 미설정 | 월말 예상치 못한 고액 청구 | 처음 계정 생성 즉시 설정 |
| 테스트 후 리소스 미삭제 | 불필요한 비용 지속 발생 | 실습 후 반드시 리소스 정리 |
| 퍼블릭 S3 버킷 무심코 설정 | 민감 데이터 외부 노출 | S3 퍼블릭 액세스 차단 설정 |
| 단일 AZ 배포 | AZ 장애 시 서비스 전체 중단 | 최소 2개 AZ에 분산 배포 |

---

### 다음 단계

이번 강의에서 AWS의 전체적인 그림과 IAM 권한 관리의 핵심을 학습했습니다. 다음 강의에서는 AWS의 가장 기본 컴퓨팅 서비스인 EC2를 깊이 있게 다룹니다.

**다음 파일:** `03_ec2_deep_dive.md`

다음 강의에서 다룰 내용:
- EC2 인스턴스 타입과 선택 기준 (범용, 컴퓨팅 최적화, 메모리 최적화, GPU)
- AMI(Amazon Machine Image)와 인스턴스 생성
- 보안 그룹(Security Group)과 키 페어(Key Pair)
- EBS 볼륨 연결과 스냅샷
- 탄력적 IP(Elastic IP)와 퍼블릭/프라이빗 접근
- Auto Scaling Group과 Launch Template
- EC2 비용 최적화: 온디맨드 vs 예약 인스턴스 vs 스팟

---
