/* ==========================================================================
   VIBE MUSIC SNS - CLIENT SIDE ORCHESTRATION
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    initThemeToggler();
    initLanguageToggler();
    initRealtimeNotifications();
    initMusicSearch();
    initCustomAudioPlayer();
    initLikeButtons();
    initNotificationActions();
});

// ==========================================
// 1. REAL-TIME SSE NOTIFICATION LISTENER
// ==========================================
function initRealtimeNotifications() {
    const badge = document.getElementById('notif-badge');
    const toastContainer = document.getElementById('toast-container');
    
    // Connect to Server-Sent Events (SSE) notification stream
    const source = new EventSource('/api/notifications/stream');
    
    source.addEventListener('connect', (e) => {
        console.log('SSE Stream: Connected to real-time notification engine.');
    });
    
    source.onmessage = (event) => {
        const payload = JSON.parse(event.data);
        if (!payload || !payload.sender) return;
        
        console.log('SSE Stream: New notification received:', payload);
        
        // 1. Increment Navigation badge count
        if (badge) {
            let count = parseInt(badge.textContent.trim()) || 0;
            count += 1;
            badge.textContent = count;
            badge.style.display = 'inline-block';
        }
        
        // Load current language to translate notifications dynamically
        const currentLang = localStorage.getItem('lang') || 'ko';
        const msgText = currentLang === 'ko'
            ? `님이 내가 좋아요 한 '${payload.song_title}'에 댓글을 남겼습니다.`
            : ` left a comment on '${payload.song_title}' which you liked.`;
            
        // 2. Spawn a beautiful Toast alert
        if (toastContainer) {
            const toast = document.createElement('div');
            toast.className = 'toast-alert';
            toast.innerHTML = `
                <img class="toast-artwork" src="${payload.artwork_url || 'https://via.placeholder.com/60'}" alt="cover">
                <div class="toast-content">
                    <div class="toast-msg"><strong>${payload.sender}</strong> ${msgText}</div>
                    <div class="toast-time">${payload.timestamp}</div>
                </div>
                <button class="toast-close">&times;</button>
            `;
            
            // Close toast button
            toast.querySelector('.toast-close').addEventListener('click', () => {
                toast.remove();
            });
            
            // Clicking the toast redirects to the song detail
            toast.addEventListener('click', (e) => {
                if (!e.target.classList.contains('toast-close')) {
                    window.location.href = `/song/${payload.song_id}`;
                }
            });
            
            toastContainer.appendChild(toast);
            
            // Play a soft dynamic system note (non-blocking)
            try {
                const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.frequency.setValueAtTime(587.33, audioCtx.currentTime); // D5
                osc.frequency.exponentialRampToValueAtTime(880, audioCtx.currentTime + 0.15); // A5
                gain.gain.setValueAtTime(0.08, audioCtx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.3);
                osc.start();
                osc.stop(audioCtx.currentTime + 0.3);
            } catch (err) {
                // Ignore audio context blocker
            }
            
            // Self-destruct toast after 7.5 seconds
            setTimeout(() => {
                toast.style.animation = 'slideIn 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) reverse forwards';
                setTimeout(() => toast.remove(), 300);
            }, 7500);
        }
        
        // 3. Dynamic reload of notifications page if currently open
        const notifPageList = document.getElementById('notifications-page-list');
        if (notifPageList) {
            // Prepend a fresh item to the list
            const emptyState = document.getElementById('notif-empty-state');
            if (emptyState) emptyState.remove();
            
            const li = document.createElement('li');
            li.className = 'comment-card unread-notif';
            
            if (currentLang === 'ko') {
                li.innerHTML = `
                    <div class="comment-meta">
                        <span class="comment-author">${payload.sender}</span>
                        <span class="comment-time">${payload.timestamp}</span>
                    </div>
                    <div class="comment-body" data-i18n-notif-comment="${payload.song_title}" data-song-url="/song/${payload.song_id}">
                        내가 좋아요 한 노래 <a href="/song/${payload.song_id}" style="color: var(--primary-cyan); font-weight: 600;">${payload.song_title}</a>에 새로운 댓글을 남겼습니다.
                    </div>
                `;
            } else {
                li.innerHTML = `
                    <div class="comment-meta">
                        <span class="comment-author">${payload.sender}</span>
                        <span class="comment-time">${payload.timestamp}</span>
                    </div>
                    <div class="comment-body" data-i18n-notif-comment="${payload.song_title}" data-song-url="/song/${payload.song_id}">
                        left a new comment on <a href="/song/${payload.song_id}" style="color: var(--primary-cyan); font-weight: 600;">${payload.song_title}</a> which you liked.
                    </div>
                `;
            }
            notifPageList.insertBefore(li, notifPageList.firstChild);
        }
    };
    
    source.onerror = (error) => {
        console.warn('SSE Stream: Disconnected or server closed. ReadyState:', source.readyState);
    };
}

// ==========================================
// 2. SEARCH BOX & AUTO-COMPLETE DEBOUNCER
// ==========================================
function initMusicSearch() {
    const input = document.getElementById('search-input');
    const spinner = document.getElementById('search-spinner');
    const container = document.getElementById('search-results-container');
    const exploreFeed = document.getElementById('explore-feed');
    
    if (!input || !container) return;
    
    let debounceTimer;
    
    input.addEventListener('input', (e) => {
        const query = e.target.value.trim();
        clearTimeout(debounceTimer);
        
        if (query.length < 2) {
            container.innerHTML = '';
            if (exploreFeed) exploreFeed.style.display = 'block';
            return;
        }
        
        if (spinner) spinner.style.display = 'block';
        if (exploreFeed) exploreFeed.style.display = 'none';
        
        debounceTimer = setTimeout(() => {
            fetch(`/api/search?q=${encodeURIComponent(query)}`)
                .then(res => res.json())
                .then(data => {
                    if (spinner) spinner.style.display = 'none';
                    renderSearchResults(data);
                })
                .catch(err => {
                    if (spinner) spinner.style.display = 'none';
                    console.error('Search failed:', err);
                });
        }, 350);
    });
}

function renderSearchResults(tracks) {
    const container = document.getElementById('search-results-container');
    if (!container) return;
    
    if (!tracks || tracks.length === 0) {
        container.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; color: var(--text-muted); padding: 3rem 0;">
                검색 결과가 없습니다. 다른 곡을 검색해 보세요.
            </div>
        `;
        return;
    }
    
    container.innerHTML = tracks.map(track => `
        <div class="song-card">
            <div class="artwork-wrapper">
                <img class="artwork-image" src="${track.artworkUrl || 'https://via.placeholder.com/300'}" alt="${track.trackName}">
            </div>
            <div class="song-info">
                <h4 class="song-title" title="${track.trackName}">${track.trackName}</h4>
                <div class="song-artist" title="${track.artistName}">${track.artistName}</div>
                <div class="song-album" title="${track.collectionName}">${track.collectionName}</div>
            </div>
            <div class="song-card-actions">
                <a href="/song/${track.trackId}" class="view-btn">Vibe 보기 &rarr;</a>
            </div>
        </div>
    `).join('');
}

// ==========================================
// 3. INLINE HTML5 AUDIO PREVIEW CONTROLLER
// ==========================================
let globalAudio = null;
let currentPlayButton = null;

function initCustomAudioPlayer() {
    const playBtn = document.getElementById('detail-play-btn');
    const vinyl = document.getElementById('vinyl-disc');
    
    if (!playBtn) return;
    
    const previewUrl = playBtn.dataset.previewUrl;
    
    playBtn.addEventListener('click', () => {
        if (!previewUrl) {
            alert('이 곡은 1분 미리듣기를 제공하지 않습니다.');
            return;
        }
        
        // Stop current audio if playing elsewhere
        if (globalAudio && currentPlayButton !== playBtn) {
            globalAudio.pause();
            if (currentPlayButton) {
                currentPlayButton.innerHTML = '&#9658;'; // Play symbol
            }
            const activeVinyls = document.querySelectorAll('.vinyl-disc');
            activeVinyls.forEach(v => v.classList.remove('playing'));
        }
        
        if (globalAudio && !globalAudio.paused && currentPlayButton === playBtn) {
            // Already playing this song, pause it
            globalAudio.pause();
            playBtn.innerHTML = '&#9658;'; // Play symbol
            if (vinyl) vinyl.classList.remove('playing');
        } else {
            // Play or resume
            if (!globalAudio || currentPlayButton !== playBtn) {
                globalAudio = new Audio(previewUrl);
                currentPlayButton = playBtn;
            }
            
            globalAudio.play()
                .then(() => {
                    playBtn.innerHTML = '&#10074;&#10074;'; // Pause symbol
                    if (vinyl) vinyl.classList.add('playing');
                })
                .catch(err => {
                    console.error('Audio failed to play:', err);
                    alert('미리듣기 재생에 실패했습니다.');
                });
                
            globalAudio.onended = () => {
                playBtn.innerHTML = '&#9658;';
                if (vinyl) vinyl.classList.remove('playing');
            };
        }
    });
}

// ==========================================
// 4. AJAX LIKE TOGGLE SYSTEM
// ==========================================
function initLikeButtons() {
    const likeBtn = document.getElementById('like-btn');
    if (!likeBtn) return;
    
    likeBtn.addEventListener('click', (e) => {
        e.preventDefault();
        const trackId = likeBtn.dataset.trackId;
        
        fetch(`/song/${trackId}/like`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(res => {
            if (res.redirected) {
                // If flask redirects us, it means login is required
                window.location.href = res.url;
                return;
            }
            return res.json();
        })
        .then(data => {
            if (!data) return;
            
            const likeIcon = document.getElementById('like-icon');
            const countLabel = document.getElementById('likes-count-label');
            
            if (data.liked) {
                likeBtn.classList.add('liked');
                if (likeIcon) likeIcon.innerHTML = '&#9829;'; // Filled heart
                likeBtn.style.color = '#ff1744';
            } else {
                likeBtn.classList.remove('liked');
                if (likeIcon) likeIcon.innerHTML = '&#9825;'; // Empty heart
                likeBtn.style.color = 'var(--text-white)';
            }
            
            if (countLabel) {
                countLabel.textContent = `${data.likes_count} Likes`;
            }
        })
        .catch(err => console.error('Like toggle failed:', err));
    });
}

// ==========================================
// 5. NOTIFICATION READ STATE AXIS
// ==========================================
function initNotificationActions() {
    const markAllBtn = document.getElementById('mark-all-read-btn');
    if (markAllBtn) {
        markAllBtn.addEventListener('click', () => {
            fetch('/api/notifications/read-all', { method: 'POST' })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        // Mark all UI lists as read
                        const unreads = document.querySelectorAll('.unread-notif');
                        unreads.forEach(el => el.classList.remove('unread-notif'));
                        
                        // Set badge to 0 or hide
                        const badge = document.getElementById('notif-badge');
                        if (badge) badge.style.display = 'none';
                    }
                })
                .catch(err => console.error('Read-all notification failed:', err));
        });
    }
}

// ==========================================
// 6. GLOBAL UTILITY TOAST NOTIFIER
// ==========================================
window.showToast = function(message, type = 'success') {
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) return;
    
    const toast = document.createElement('div');
    toast.className = 'toast-alert';
    if (type === 'error') {
        toast.style.border = '1px solid var(--danger)';
        toast.style.boxShadow = '0 10px 25px rgba(0, 0, 0, 0.5), 0 0 20px rgba(255, 23, 68, 0.25)';
    } else {
        toast.style.border = '1px solid var(--border-active)';
        toast.style.boxShadow = '0 10px 25px rgba(0, 0, 0, 0.5), var(--shadow-cyan)';
    }
    
    const now = new Date();
    const timeString = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`;
    const icon = type === 'error' ? '❌' : '✅';
    
    toast.innerHTML = `
        <div style="font-size: 1.2rem; padding: 0.2rem 0.4rem;">${icon}</div>
        <div class="toast-content">
            <div class="toast-msg">${message}</div>
            <div class="toast-time">${timeString}</div>
        </div>
        <button class="toast-close">&times;</button>
    `;
    
    toast.querySelector('.toast-close').addEventListener('click', () => {
        toast.remove();
    });
    
    toastContainer.appendChild(toast);
    
    try {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        if (type === 'error') {
            osc.frequency.setValueAtTime(300, audioCtx.currentTime);
            osc.frequency.linearRampToValueAtTime(150, audioCtx.currentTime + 0.2);
            gain.gain.setValueAtTime(0.08, audioCtx.currentTime);
            gain.gain.linearRampToValueAtTime(0.01, audioCtx.currentTime + 0.25);
        } else {
            osc.frequency.setValueAtTime(587.33, audioCtx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(880, audioCtx.currentTime + 0.15);
            gain.gain.setValueAtTime(0.08, audioCtx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.3);
        }
        osc.start();
        osc.stop(audioCtx.currentTime + 0.3);
    } catch (err) {}
    
    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) reverse forwards';
        setTimeout(() => toast.remove(), 300);
    }, 5000);
};

// ==========================================
// 7. DYNAMIC THEME SWITCHER CONTROLLER
// ==========================================
function initThemeToggler() {
    const btn = document.getElementById('theme-toggle-btn');
    if (!btn) return;
    
    // Set initial icon
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
    btn.innerHTML = currentTheme === 'dark' ? '☀️' : '🌙';
    
    btn.addEventListener('click', () => {
        const activeTheme = document.documentElement.getAttribute('data-theme') || 'dark';
        const nextTheme = activeTheme === 'dark' ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-theme', nextTheme);
        localStorage.setItem('theme', nextTheme);
        btn.innerHTML = nextTheme === 'dark' ? '☀️' : '🌙';
        
        if (window.showToast) {
            const currentLang = localStorage.getItem('lang') || 'ko';
            const msg = nextTheme === 'dark' 
                ? (currentLang === 'ko' ? '다크 모드로 전환되었습니다.' : 'Switched to Dark Mode.')
                : (currentLang === 'ko' ? '라이트 모드로 전환되었습니다.' : 'Switched to Light Mode.');
            window.showToast(msg, 'success');
        }
    });
}

// ==========================================
// 8. BILINGUAL i18n TRANSLATION MODULE
// ==========================================
const i18nDictionary = {
    ko: {
        "nav_home": "홈",
        "nav_top_likes": "인기 Vibe",
        "nav_hashtags": "해시태그",
        "nav_notifications": "알림 피드",
        "nav_profile": "내 프로필 ({username})",
        "nav_logout": "로그아웃",
        "nav_login": "로그인",
        "nav_admin": "관리자",
        "footer_text": "© 2026 Vibe. GenAI Labs 최초 제작. iTunes 검색 제공. Vanilla JS/CSS로 디자인되었습니다.",
        
        "hero_title": "Discover Your Vibe",
        "hero_subtitle": "실시간으로 음악을 검색하고, 당신의 소중한 감상평(Vibe)을 남겨 다른 사람들과 소통해 보세요.",
        "search_placeholder": "노래 제목, 아티스트 이름 등으로 검색해 보세요...",
        "feed_title_music": "🎵 실시간 음악 피드",
        "feed_title_likes": "💖 최근 좋아요 소식",
        "feed_no_comments": "아직 피드 글이 없습니다. 첫 Vibe를 남겨보세요!",
        "feed_no_likes": "아직 하트 신호가 없습니다. 곡을 탐색하고 하트를 꾹 눌러보세요!",
        "view_vibe": "Vibe 보기 &rarr;",
        
        "preview_title": "30초 미리듣기 재생",
        "preview_desc": "클릭 시 레코드가 회전하며 음악이 스트리밍됩니다.",
        "vibe_title": "✨ Music Vibe & Description",
        "no_description_alert": "이 노래에 등록된 소개글이 아직 없습니다. 아래에서 첫 음악적 감상을 등록해 보세요!",
        "edit_description_btn": "📝 소개글 작성/수정하기",
        "edit_description_placeholder": "이 음악의 스토리나 당신의 특별한 감성 피드, 해시태그(예: #chill #신나는)를 적어주세요...",
        "cancel": "취소",
        "save": "저장하기",
        "login_prompt_vibe": "💡 <a href=\"/login\" style=\"color: var(--primary-cyan); text-decoration: none;\">로그인</a> 후 이 노래의 감상글과 해시태그를 수정할 수 있습니다.",
        "youtube_title": "📺 Official YouTube Video",
        "youtube_empty": "📺 해당 곡의 유튜브 영상을 불러오는 중이거나 찾을 수 없습니다.",
        "youtube_bottom": "🎵 VIBE YouTube Integration: 아티스트와 노래를 매칭하여 최적의 뮤직비디오/영상을 실시간으로 가져옵니다.",
        "comments_title": "💬 댓글 ({count})",
        "comment_placeholder": "이 곡에 대해 자유롭게 이야기해 보세요! 해시태그도 사용 가능해요 (#추천 #드라이브)...",
        "add_comment_btn": "댓글 남기기",
        "login_prompt_comment": "💬 댓글을 달고 싶으신가요? <a href=\"/login\" style=\"color: var(--primary-cyan); text-decoration: none; font-weight: 600;\">로그인</a>이 필요합니다.",
        "no_comments_alert": "아직 댓글 대화가 없습니다. 따뜻한 이야기를 먼저 시작해 보세요!",
        
        "add_tag_placeholder": "#태그 추가...",
        "add_tag_btn": "추가",
        
        "hashtags_page_title": "🏷️ Vibe Hashtags Explorer",
        "hashtags_page_desc": "음악 설명글과 댓글에서 추출한 감성 태그로 노래들을 모아 탐색할 수 있습니다.",
        "no_hashtags_alert": "아직 커뮤니티에 등록된 해시태그가 없습니다. 노래 설명이나 댓글에 #태그를 적어 보세요!",
        "hashtag_search_result": "🔍 {tag} 검색 결과 ({count})",
        "clear_filter": "필터 지우기 &times;",
        "no_tag_songs_alert": "지정된 태그를 포함한 활성 데이터가 유실되었거나 없습니다.",
        "hashtags_page_prompt": "상단의 해시태그를 클릭하여 음악적 테마를 탐색해 보세요! #드라이브 #퇴근길 #새벽감성 #신나는 등 원하는 분위기를 필터링할 수 있습니다.",
        
        "top_likes_title": "🔥 Top Loved Vibes",
        "top_likes_desc": "전체 커뮤니티에서 가장 많은 하트 신호를 받은 노래들을 모아 보여줍니다.",
        "no_top_likes_alert": "아직 하트 신호를 기록한 곡이 없습니다. 원하는 노래에 하트를 눌러보세요!",
        
        "notif_page_title": "🔔 Real-Time Action Notifications",
        "notif_page_desc": "실시간 소셜 피드 알림입니다. 내가 좋아요 한 노래의 새로운 소식을 확인해 보세요.",
        "mark_all_read": "✔️ 모두 읽음으로 표시",
        "no_notifs_alert": "아직 새로운 알림이 없습니다. 활발한 커뮤니티 활동을 즐겨보세요!",
        
        "profile_title": "👤 내 감성 프로필",
        "profile_joined": "가입일: {date}",
        "profile_edit_btn": "✏️ 수정",
        "profile_nickname_placeholder": "새로운 닉네임 입력...",
        "profile_likes_tab": "💖 좋아요 한 곡 ({count})",
        "profile_comments_tab": "💬 남긴 댓글 ({count})",
        "no_profile_likes": "아직 좋아요 한 곡이 없습니다. 마음에 드는 곡에 하트를 꾹 눌러보세요!",
        "no_profile_comments": "아직 남긴 댓글이 없습니다. 음악 감상평을 먼저 남겨보세요!",
        
        "login_title": "🔑 VIBE 로그인",
        "login_subtitle": "음악으로 하나 되는 공간, 바이브에 로그인하세요.",
        "login_id": "아이디",
        "login_id_placeholder": "아이디를 입력해 주세요",
        "login_pw": "비밀번호",
        "login_pw_placeholder": "비밀번호를 입력해 주세요",
        "login_submit": "로그인",
        "login_footer": "아직 계정이 없으신가요? <a href=\"/register\" style=\"color: var(--primary-cyan); text-decoration: none; font-weight: 600;\">회원가입 하기</a>",
        
        "register_title": "📝 VIBE 회원가입",
        "register_subtitle": "지금 가입하고 실시간 음악 소식과 감성을 공유해 보세요.",
        "register_id": "사용할 아이디",
        "register_id_placeholder": "3자 이상 입력하세요",
        "register_pw": "비밀번호",
        "register_pw_placeholder": "4자 이상 입력하세요",
        "register_pw_confirm": "비밀번호 확인",
        "register_pw_confirm_placeholder": "동일한 비밀번호를 다시 입력하세요",
        "register_submit": "회원가입 완료",
        "register_footer": "이미 계정이 있으신가요? <a href=\"/login\" style=\"color: var(--primary-cyan); text-decoration: none; font-weight: 600;\">로그인 하기</a>",
        
        "admin_title": "⚙️ Admin Control Cockpit",
        "admin_desc": "커뮤니티 모니터링, 악성 유저 정지, 유해 콘텐츠(댓글, 캐싱 음악) 영구 삭제 등 관리 제어 권한을 행사합니다.",
        "admin_kpi_users": "총 가입 유저",
        "admin_kpi_songs": "DB 저장 음악",
        "admin_kpi_comments": "등록된 댓글",
        "admin_kpi_likes": "누적 좋아요 수",
        "admin_sec_users": "👤 가입 사용자 제어 및 관리",
        "admin_th_num": "번호",
        "admin_th_user": "사용자 아이디",
        "admin_th_joined": "가입 시각",
        "admin_th_role": "관리자 여부",
        "admin_th_status": "상태 (정지 유무)",
        "admin_th_actions": "제어 작업",
        "admin_role_user": "일반 유저",
        "admin_status_active": "✅ 활성",
        "admin_status_blocked": "🛑 정지됨",
        "admin_btn_block": "계정 정지",
        "admin_btn_unblock": "정지 해제",
        "admin_sec_comments": "💬 커뮤니티 댓글 필터링 및 악플 차단",
        "admin_th_song": "연결 노래",
        "admin_th_comment_body": "댓글 본문 내용",
        "admin_btn_delete": "강제 삭제",
        "admin_sec_songs": "💿 DB 인덱싱 노래 캐시 관리",
        "admin_th_track_artist": "곡명 및 아티스트",
        "admin_th_vibe_body": "소개글(Vibe) 본문",
        "admin_th_likes_count": "좋아요 수",
        "admin_no_users": "가입한 일반 사용자가 아직 없습니다.",
        "admin_no_comments": "최근 등록된 댓글이 없습니다.",
        "admin_no_description": "소개 없음",
        "admin_btn_db_delete": "DB 삭제",
        "admin_no_songs": "인덱싱된 곡 정보가 없습니다."
    },
    en: {
        "nav_home": "Home",
        "nav_top_likes": "Top Likes",
        "nav_hashtags": "Hashtags",
        "nav_notifications": "Notifications",
        "nav_profile": "Profile ({username})",
        "nav_logout": "Logout",
        "nav_login": "Login",
        "nav_admin": "Admin",
        "footer_text": "© 2026 Vibe. Originally Crafted by GenAI Labs. Powered by iTunes Search. Built beautifully with Vanilla JS/CSS.",
        
        "hero_title": "Discover Your Vibe",
        "hero_subtitle": "Search for music in real-time, share your personal music vibe, and connect with other listeners.",
        "search_placeholder": "Search songs, artists, vibes...",
        "feed_title_music": "🎵 Live Music Feed",
        "feed_title_likes": "💖 Recent Hearts",
        "feed_no_comments": "No vibe comments yet. Be the first to share!",
        "feed_no_likes": "No likes yet. Explore songs and tap the heart!",
        "view_vibe": "View Vibe &rarr;",
        
        "preview_title": "30s Preview Player",
        "preview_desc": "Click to spin the record and stream music live.",
        "vibe_title": "✨ Music Vibe & Description",
        "no_description_alert": "No custom vibes or story registered for this track. Write one below!",
        "edit_description_btn": "📝 Write/Edit Vibe Story",
        "edit_description_placeholder": "Share the story of this song, your special feelings, or hashtag vibes (e.g. #chill #happy)...",
        "cancel": "Cancel",
        "save": "Save",
        "login_prompt_vibe": "💡 <a href=\"/login\" style=\"color: var(--primary-cyan); text-decoration: none;\">Log in</a> to edit this song's commentary and hashtags.",
        "youtube_title": "📺 Official YouTube Video",
        "youtube_empty": "📺 Loading or unable to find YouTube video for this track.",
        "youtube_bottom": "🎵 VIBE YouTube Integration: Real-time matched official music video based on artist & song name.",
        "comments_title": "💬 Comments ({count})",
        "comment_placeholder": "Talk about this song! Hashtags are fully supported (#vibe #kpop)...",
        "add_comment_btn": "Add Comment",
        "login_prompt_comment": "💬 Want to leave a comment? <a href=\"/login\" style=\"color: var(--primary-cyan); text-decoration: none; font-weight: 600;\">Login</a> is required.",
        "no_comments_alert": "No comments yet. Start a warm conversation!",
        
        "add_tag_placeholder": "#add tag...",
        "add_tag_btn": "Add",
        
        "hashtags_page_title": "🏷️ Vibe Hashtags Explorer",
        "hashtags_page_desc": "Explore collections of songs aggregated by emotional tags extracted from stories and comments.",
        "no_hashtags_alert": "No hashtags registered yet. Write #tags in song descriptions or comments!",
        "hashtag_search_result": "🔍 Results for {tag} ({count})",
        "clear_filter": "Clear Filter &times;",
        "no_tag_songs_alert": "No active songs matched this tag.",
        "hashtags_page_prompt": "Click on a hashtag above to explore musical themes! Filter by moods like #chill, #drive, #happy, and more.",
        
        "top_likes_title": "🔥 Top Loved Vibes",
        "top_likes_desc": "Curated collection of the most liked songs across the entire Vibe community.",
        "no_top_likes_alert": "No liked tracks yet. Find a song you love and give it a heart!",
        
        "notif_page_title": "🔔 Real-Time Action Notifications",
        "notif_page_desc": "Social updates and notification stream. Stay updated on tracks you liked.",
        "mark_all_read": "✔️ Mark All as Read",
        "no_notifs_alert": "No notifications yet. Connect with other music lovers!",
        
        "profile_title": "👤 User Vibe Profile",
        "profile_joined": "Joined: {date}",
        "profile_edit_btn": "✏️ Edit",
        "profile_nickname_placeholder": "Enter new nickname...",
        "profile_likes_tab": "💖 Liked Tracks ({count})",
        "profile_comments_tab": "💬 Comments Written ({count})",
        "no_profile_likes": "No liked tracks yet. Tap a heart on tracks you enjoy!",
        "no_profile_comments": "No comments written yet. Share your thoughts on a track!",
        
        "login_title": "🔑 VIBE Member Login",
        "login_subtitle": "Step into the space united by music. Log in to Vibe.",
        "login_id": "Username",
        "login_id_placeholder": "Enter your username",
        "login_pw": "Password",
        "login_pw_placeholder": "Enter your password",
        "login_submit": "Login",
        "login_footer": "Don't have an account? <a href=\"/register\" style=\"color: var(--primary-cyan); text-decoration: none; font-weight: 600;\">Sign Up</a>",
        
        "register_title": "📝 Create VIBE Account",
        "register_subtitle": "Join now to share real-time music feeds and emotional vibes.",
        "register_id": "Username",
        "register_id_placeholder": "Enter 3 characters or more",
        "register_pw": "Password",
        "register_pw_placeholder": "Enter 4 characters or more",
        "register_pw_confirm": "Confirm Password",
        "register_pw_confirm_placeholder": "Re-enter the same password",
        "register_submit": "Sign Up",
        "register_footer": "Already have an account? <a href=\"/login\" style=\"color: var(--primary-cyan); text-decoration: none; font-weight: 600;\">Login</a>",
        
        "admin_title": "⚙️ Admin Control Cockpit",
        "admin_desc": "Perform administrative controls such as monitoring community activity, suspending users, and deleting contents.",
        "admin_kpi_users": "Total Users",
        "admin_kpi_songs": "Songs in DB",
        "admin_kpi_comments": "Comments",
        "admin_kpi_likes": "Total Likes",
        "admin_sec_users": "👤 User Moderation & Control",
        "admin_th_num": "No.",
        "admin_th_user": "Username",
        "admin_th_joined": "Date Joined",
        "admin_th_role": "Is Admin",
        "admin_th_status": "Status",
        "admin_th_actions": "Controls",
        "admin_role_user": "Regular User",
        "admin_status_active": "✅ Active",
        "admin_status_blocked": "🛑 Suspended",
        "admin_btn_block": "Suspend",
        "admin_btn_unblock": "Unsuspend",
        "admin_sec_comments": "💬 Comment Filtering & Moderation",
        "admin_th_song": "Song Track",
        "admin_th_comment_body": "Comment Body",
        "admin_btn_delete": "Force Delete",
        "admin_sec_songs": "💿 Song Cache Index Management",
        "admin_th_track_artist": "Song & Artist",
        "admin_th_vibe_body": "Vibe Description",
        "admin_th_likes_count": "Likes",
        "admin_no_users": "No registered regular users yet.",
        "admin_no_comments": "No recent comments available.",
        "admin_no_description": "No Description",
        "admin_btn_db_delete": "Delete DB",
        "admin_no_songs": "No cached tracks registered in database."
    }
};

function updateLanguageUI(lang) {
    const translation = i18nDictionary[lang];
    if (!translation) return;

    // 1. Text elements: data-i18n
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        let text = translation[key];
        
        if (text) {
            // Context injection values
            if (key === 'nav_profile') {
                const username = el.getAttribute('data-username');
                text = text.replace('{username}', username);
            }
            if (key === 'profile_joined') {
                const date = el.getAttribute('data-date');
                text = text.replace('{date}', date);
            }
            if (key === 'comments_title' || key === 'profile_likes_tab' || key === 'profile_comments_tab') {
                const count = el.getAttribute('data-count');
                text = text.replace('{count}', count);
            }
            if (key === 'hashtag_search_result') {
                const tag = el.getAttribute('data-tag');
                const count = el.getAttribute('data-count');
                text = text.replace('{tag}', tag).replace('{count}', count);
            }
            
            // Keep dynamic symbols if not included (e.g. arrows)
            el.innerHTML = text;
        }
    });

    // 2. Input Placeholders: data-i18n-placeholder
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const key = el.getAttribute('data-i18n-placeholder');
        const text = translation[key];
        if (text) {
            el.setAttribute('placeholder', text);
        }
    });

    // 3. Dynamic notifications timelines
    document.querySelectorAll('[data-i18n-notif-comment]').forEach(el => {
        const songTitle = el.getAttribute('data-i18n-notif-comment');
        const url = el.getAttribute('data-song-url');
        
        if (lang === 'ko') {
            el.innerHTML = `내가 좋아요 한 노래 <a href="${url}" style="color: var(--primary-cyan); font-weight: 600;">${songTitle}</a>에 새로운 댓글을 남겼습니다.`;
        } else {
            el.innerHTML = `left a new comment on <a href="${url}" style="color: var(--primary-cyan); font-weight: 600;">${songTitle}</a> which you liked.`;
        }
    });
}

function initLanguageToggler() {
    const btn = document.getElementById('lang-toggle-btn');
    if (!btn) return;
    
    // Retrieve setting
    const currentLang = localStorage.getItem('lang') || 'ko';
    updateLanguageUI(currentLang);
    btn.textContent = currentLang === 'ko' ? 'EN' : 'KO';
    
    btn.addEventListener('click', () => {
        const activeLang = localStorage.getItem('lang') || 'ko';
        const nextLang = activeLang === 'ko' ? 'en' : 'ko';
        
        localStorage.setItem('lang', nextLang);
        updateLanguageUI(nextLang);
        btn.textContent = nextLang === 'ko' ? 'EN' : 'KO';
        
        if (window.showToast) {
            const toastMsg = nextLang === 'ko' ? '한국어로 언어가 변경되었습니다.' : 'Language has been changed to English.';
            window.showToast(toastMsg, 'success');
        }
    });
}
