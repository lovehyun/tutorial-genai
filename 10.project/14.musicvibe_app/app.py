import os
import queue
import re
from datetime import datetime
import requests
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vibe.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'super-secret-vibe-key-2026-dynamic-token'

db = SQLAlchemy(app)

# ==========================================
# DATABASE MODELS
# ==========================================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_blocked = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    track_id = db.Column(db.Integer, unique=True, nullable=False)
    track_name = db.Column(db.String(200), nullable=False)
    artist_name = db.Column(db.String(200), nullable=False)
    collection_name = db.Column(db.String(200))
    artwork_url = db.Column(db.String(500))
    preview_url = db.Column(db.String(500))
    description = db.Column(db.Text)
    youtube_id = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('likes', lazy=True, cascade='all, delete-orphan'))
    song = db.relationship('Song', backref=db.backref('likes', lazy=True, cascade='all, delete-orphan'))

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('comments', lazy=True, cascade='all, delete-orphan'))
    song = db.relationship('Song', backref=db.backref('comments', lazy=True, cascade='all, delete-orphan'))

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'), nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    type = db.Column(db.String(50), default='comment')  # 'comment', 'like'
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    recipient = db.relationship('User', foreign_keys=[recipient_id], backref=db.backref('received_notifications', lazy=True, cascade='all, delete-orphan'))
    sender = db.relationship('User', foreign_keys=[sender_id], backref=db.backref('sent_notifications', lazy=True, cascade='all, delete-orphan'))
    song = db.relationship('Song', backref=db.backref('notifications', lazy=True, cascade='all, delete-orphan'))
    comment = db.relationship('Comment', backref=db.backref('notifications', lazy=True, cascade='all, delete-orphan'))

class SongTag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tag = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('tags', lazy=True, cascade='all, delete-orphan'))
    song = db.relationship('Song', backref=db.backref('tags', lazy=True, cascade='all, delete-orphan'))

# ==========================================
# REAL-TIME NOTIFICATIONS MECHANISM (SSE)
# ==========================================

# Maps user_id (int) -> set of queue.Queue objects
sse_clients = {}

def send_realtime_notification(user_id, payload):
    """Sends a notification payload to all active SSE client queues of a user."""
    if user_id in sse_clients:
        for q in list(sse_clients[user_id]):
            try:
                q.put_nowait(payload)
            except queue.Full:
                pass

# ==========================================
# CONTEXT PROCESSORS (Navigation Badges)
# ==========================================

@app.context_processor
def inject_notification_count():
    """Injects the unread notification count into all templates."""
    unread_count = 0
    if 'user_id' in session:
        unread_count = Notification.query.filter_by(
            recipient_id=session['user_id'], is_read=False
        ).count()
    return dict(unread_count=unread_count)

# ==========================================
# UTILITY DECORATORS & HELPERS
# ==========================================

def get_current_user():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user and not user.is_blocked:
            return user
        else:
            session.clear()
    return None

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if get_current_user() is None:
            return redirect(url_for('login_page', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if user is None or not user.is_admin:
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

def get_or_create_song(track_data):
    """Helper to register a song locally from iTunes API data if it doesn't exist."""
    track_id = int(track_data.get('trackId'))
    song = Song.query.filter_by(track_id=track_id).first()
    if not song:
        # Get high-resolution artwork (replace 100x100 with 600x600)
        art_url = track_data.get('artworkUrl100', '')
        if art_url:
            art_url = art_url.replace('100x100bb.jpg', '600x600bb.jpg')
            
        song = Song(
            track_id=track_id,
            track_name=track_data.get('trackName', 'Unknown Song'),
            artist_name=track_data.get('artistName', 'Unknown Artist'),
            collection_name=track_data.get('collectionName', ''),
            artwork_url=art_url,
            preview_url=track_data.get('previewUrl', '')
        )
        db.session.add(song)
        db.session.commit()
    return song

def get_youtube_video_id(artist, track):
    try:
        query = f"{artist} {track} official mv"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }
        r = requests.get("https://www.youtube.com/results", params={"search_query": query}, headers=headers, timeout=6)
        match = re.search(r'"videoId":"([a-zA-Z0-9_-]{11})"', r.text)
        if match:
            return match.group(1)
    except Exception as e:
        print("YouTube Search error:", e)
    return None

# Extract tags from text (e.g., #chill, #kpop)
def extract_hashtags(text):
    if not text:
        return []
    return re.findall(r'#\w+', text)

# ==========================================
# PUBLIC & SOCIAL ROUTES
# ==========================================

@app.route('/')
def home():
    user = get_current_user()
    
    # Fetch recent activities for the social feed
    recent_comments = Comment.query.order_by(Comment.created_at.desc()).limit(5).all()
    recent_likes = Like.query.order_by(Like.created_at.desc()).limit(5).all()
    
    return render_template('home.html', user=user, recent_comments=recent_comments, recent_likes=recent_likes)

@app.route('/api/search')
def api_search():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])
    
    # 1. Local Hashtag Search
    if query.startswith('#'):
        try:
            # Find songs that contain this hashtag in their description
            songs_desc = Song.query.filter(Song.description.like(f'%{query}%')).all()
            # Find comments containing this hashtag
            comments_tag = Comment.query.filter(Comment.content.like(f'%{query}%')).all()
            # Find dedicated song tags
            dedicated_tags = SongTag.query.filter(SongTag.tag.like(f'%{query}%')).all()
            
            # Extract unique song IDs
            song_ids = {s.id for s in songs_desc}
            song_ids.update({c.song_id for c in comments_tag})
            song_ids.update({t.song_id for t in dedicated_tags})
            
            if not song_ids:
                return jsonify([])
                
            filtered_songs = Song.query.filter(Song.id.in_(song_ids)).all()
            
            formatted = []
            for song in filtered_songs:
                formatted.append({
                    'trackId': song.track_id,
                    'trackName': song.track_name,
                    'artistName': song.artist_name,
                    'collectionName': song.collection_name,
                    'artworkUrl': song.artwork_url,
                    'previewUrl': song.preview_url
                })
            return jsonify(formatted)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
    # 2. iTunes Public Search (Normal string queries)
    try:
        r = requests.get('https://itunes.apple.com/search', params={
            'term': query,
            'media': 'music',
            'limit': 15
        }, timeout=8)
        data = r.json()
        results = data.get('results', [])
        
        # Format and polish artworks
        formatted = []
        for track in results:
            art = track.get('artworkUrl100', '')
            if art:
                art = art.replace('100x100bb.jpg', '600x600bb.jpg')
            formatted.append({
                'trackId': track.get('trackId'),
                'trackName': track.get('trackName'),
                'artistName': track.get('artistName'),
                'collectionName': track.get('collectionName', ''),
                'artworkUrl': art,
                'previewUrl': track.get('previewUrl', '')
            })
        return jsonify(formatted)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/song/<int:track_id>')
def song_detail(track_id):
    user = get_current_user()
    
    # Try local cache first
    song = Song.query.filter_by(track_id=track_id).first()
    
    # If not in local DB, fetch from iTunes API to cache
    if not song:
        try:
            r = requests.get('https://itunes.apple.com/lookup', params={'id': track_id}, timeout=8)
            data = r.json()
            results = data.get('results', [])
            if results:
                song = get_or_create_song(results[0])
            else:
                return "Song not found in iTunes API", 404
        except Exception as e:
            return f"Error contacting iTunes API: {e}", 500

    # User like status
    user_liked = False
    if user:
        user_liked = Like.query.filter_by(user_id=user.id, song_id=song.id).first() is not None

    # Load song comments and total likes
    comments = Comment.query.filter_by(song_id=song.id).order_by(Comment.created_at.desc()).all()
    likes_count = Like.query.filter_by(song_id=song.id).count()

    # Dynamic caching of YouTube Video ID
    if not song.youtube_id:
        song.youtube_id = get_youtube_video_id(song.artist_name, song.track_name)
        if song.youtube_id:
            db.session.commit()

    # Parse and extract all hashtags
    song_tags = set(extract_hashtags(song.description))
    for c in comments:
        song_tags.update(extract_hashtags(c.content))
    # Query dedicated tags
    dedicated_tags = SongTag.query.filter_by(song_id=song.id).all()
    for t in dedicated_tags:
        song_tags.add(t.tag)
    song_tags = sorted(list(song_tags))

    return render_template('song_detail.html', user=user, song=song, user_liked=user_liked, comments=comments, likes_count=likes_count, song_tags=song_tags)

@app.route('/song/<int:track_id>/edit-vibe', methods=['POST'])
@login_required
def edit_vibe(track_id):
    user = get_current_user()
    song = Song.query.filter_by(track_id=track_id).first_or_404()
    
    description = request.form.get('description', '').strip()
    song.description = description
    db.session.commit()
    return redirect(url_for('song_detail', track_id=track_id))

@app.route('/song/<int:track_id>/like', methods=['POST'])
@login_required
def toggle_like(track_id):
    user = get_current_user()
    song = Song.query.filter_by(track_id=track_id).first_or_404()
    
    existing_like = Like.query.filter_by(user_id=user.id, song_id=song.id).first()
    if existing_like:
        db.session.delete(existing_like)
        db.session.commit()
        liked = False
    else:
        new_like = Like(user_id=user.id, song_id=song.id)
        db.session.add(new_like)
        db.session.commit()
        liked = True
        
        # When liked, if there's an author of custom description, notify them
        # Let's see if this song has been commented or liked by others.
        # Generally we focus on commenting notifications as requested, but we can log like events too.
        
    likes_count = Like.query.filter_by(song_id=song.id).count()
    return jsonify({'liked': liked, 'likes_count': likes_count})

@app.route('/song/<int:track_id>/comment', methods=['POST'])
@login_required
def add_comment(track_id):
    user = get_current_user()
    song = Song.query.filter_by(track_id=track_id).first_or_404()
    
    content = request.form.get('content', '').strip()
    if not content:
        return redirect(url_for('song_detail', track_id=track_id))
        
    # Save comment
    comment = Comment(user_id=user.id, song_id=song.id, content=content)
    db.session.add(comment)
    db.session.commit()
    
    # --- Real-Time Notification Logic ---
    # Find all users who liked this song (excluding the commenter)
    likers = Like.query.filter_by(song_id=song.id).filter(Like.user_id != user.id).all()
    
    for l in likers:
        # Check if notification already exists to avoid redundant flood, or just create it
        notification = Notification(
            recipient_id=l.user_id,
            sender_id=user.id,
            song_id=song.id,
            comment_id=comment.id,
            type='comment',
            is_read=False
        )
        db.session.add(notification)
        db.session.commit()
        
        # Push dynamic SSE notification to user's screen in real-time
        payload = {
            'id': notification.id,
            'sender': user.username,
            'song_title': song.track_name,
            'song_id': song.track_id,
            'artwork_url': song.artwork_url,
            'message': f"님이 내가 좋아요 한 '{song.track_name}'에 댓글을 남겼습니다.",
            'timestamp': datetime.utcnow().strftime('%H:%M:%S')
        }
        send_realtime_notification(l.user_id, payload)

    return redirect(url_for('song_detail', track_id=track_id))

@app.route('/song/<int:track_id>/tag', methods=['POST'])
@login_required
def add_tag(track_id):
    user = get_current_user()
    song = Song.query.filter_by(track_id=track_id).first_or_404()
    
    tag_val = request.form.get('tag', '').strip()
    if not tag_val:
        return redirect(url_for('song_detail', track_id=track_id))
        
    # Standardize tag (e.g. must start with #, remove spacing)
    if not tag_val.startswith('#'):
        tag_val = '#' + tag_val
        
    # Remove any internal spaces or invalid characters
    tag_val = '#' + tag_val[1:].replace(' ', '')
    
    # Check if this exact tag already exists for this song
    existing = SongTag.query.filter_by(song_id=song.id, tag=tag_val).first()
    if not existing:
        new_tag = SongTag(song_id=song.id, user_id=user.id, tag=tag_val)
        db.session.add(new_tag)
        db.session.commit()
        
    return redirect(url_for('song_detail', track_id=track_id))

@app.route('/top-likes')
def top_likes():
    user = get_current_user()
    
    # Query songs ordered by likes count
    from sqlalchemy import func
    top_songs = db.session.query(Song, func.count(Like.id).label('like_count'))\
        .join(Like, Like.song_id == Song.id)\
        .group_by(Song.id)\
        .order_by(func.count(Like.id).desc())\
        .limit(20).all()
        
    return render_template('top_likes.html', user=user, top_songs=top_songs)

@app.route('/hashtags')
def hashtags():
    user = get_current_user()
    
    # Get all comments and extract hashtags
    all_comments = Comment.query.all()
    all_songs = Song.query.all()
    
    hashtag_counts = {}
    
    # Extract from descriptions & comments
    for s in all_songs:
        for tag in extract_hashtags(s.description):
            hashtag_counts[tag] = hashtag_counts.get(tag, 0) + 1
            
    for c in all_comments:
        for tag in extract_hashtags(c.content):
            hashtag_counts[tag] = hashtag_counts.get(tag, 0) + 1
            
    # Sort hashtags by popularity
    popular_tags = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)[:30]
    
    # If filtering by a specific hashtag
    selected_tag = request.args.get('tag', '').strip()
    filtered_songs = []
    
    if selected_tag:
        if not selected_tag.startswith('#'):
            selected_tag = '#' + selected_tag
            
        # Find all songs with tag in description
        songs_with_tag = Song.query.filter(Song.description.like(f'%{selected_tag}%')).all()
        # Find comments with tag
        comments_with_tag = Comment.query.filter(Comment.content.like(f'%{selected_tag}%')).all()
        
        # Gather song IDs
        song_ids = {s.id for s in songs_with_tag}
        song_ids.update({c.song_id for c in comments_with_tag})
        
        if song_ids:
            filtered_songs = Song.query.filter(Song.id.in_(song_ids)).all()

    return render_template('hashtags.html', user=user, popular_tags=popular_tags, selected_tag=selected_tag, filtered_songs=filtered_songs)

# ==========================================
# AUTHENTICATION ROUTES
# ==========================================

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if get_current_user():
        return redirect(url_for('home'))
        
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            if user.is_blocked:
                error = "이 계정은 관리자에 의해 정지되었습니다."
            else:
                session.clear()
                session['user_id'] = user.id
                session['username'] = user.username
                session['is_admin'] = user.is_admin
                return redirect(url_for('home'))
        else:
            error = "아이디 또는 비밀번호가 올바르지 않습니다."
            
    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if get_current_user():
        return redirect(url_for('home'))
        
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        if not username or not password:
            error = "모든 필드를 입력해 주세요."
        elif len(username) < 3:
            error = "아이디는 3자 이상이어야 합니다."
        elif len(password) < 4:
            error = "비밀번호는 4자 이상이어야 합니다."
        elif password != confirm_password:
            error = "비밀번호 확인이 일치하지 않습니다."
        elif User.query.filter_by(username=username).first():
            error = "이미 사용 중인 아이디입니다."
        else:
            hashed = generate_password_hash(password)
            new_user = User(username=username, password_hash=hashed)
            db.session.add(new_user)
            db.session.commit()
            
            # Auto-login
            session['user_id'] = new_user.id
            session['username'] = new_user.username
            session['is_admin'] = False
            return redirect(url_for('home'))
            
    return render_template('register.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# ==========================================
# USER PROFILE ROUTE
# ==========================================

@app.route('/profile')
@login_required
def profile():
    user = get_current_user()
    
    # Load all user likes and comments
    user_likes = Like.query.filter_by(user_id=user.id).order_by(Like.created_at.desc()).all()
    user_comments = Comment.query.filter_by(user_id=user.id).order_by(Comment.created_at.desc()).all()
    
    return render_template('profile.html', user=user, likes=user_likes, comments=user_comments)

@app.route('/api/profile/update', methods=['POST'])
@login_required
def api_update_profile():
    user = get_current_user()
    username = request.form.get('username', '').strip()
    
    if not username:
        return jsonify({'success': False, 'message': '닉네임을 입력해 주세요.'}), 400
    if len(username) < 3:
        return jsonify({'success': False, 'message': '닉네임은 3자 이상이어야 합니다.'}), 400
    if username.lower() == 'admin' and not user.is_admin:
        return jsonify({'success': False, 'message': '허용되지 않는 닉네임입니다.'}), 400
        
    # Check if duplicate username exists (excluding themselves)
    existing_user = User.query.filter(User.username == username, User.id != user.id).first()
    if existing_user:
        return jsonify({'success': False, 'message': '이미 사용 중인 닉네임입니다.'}), 400
        
    # Update username
    user.username = username
    db.session.commit()
    
    # Update login session info
    session['username'] = username
    
    return jsonify({
        'success': True,
        'message': '닉네임이 성공적으로 변경되었습니다!',
        'new_username': username,
        'avatar_char': username[0].upper()
    })

# ==========================================
# NOTIFICATIONS PAGE & SSE STREAM
# ==========================================

@app.route('/notifications')
@login_required
def notifications_page():
    user = get_current_user()
    
    # Fetch all notifications for the user
    user_notifications = Notification.query.filter_by(recipient_id=user.id).order_by(Notification.created_at.desc()).all()
    
    return render_template('notifications.html', user=user, notifications=user_notifications)

@app.route('/api/notifications/read-all', methods=['POST'])
@login_required
def read_all_notifications():
    user = get_current_user()
    Notification.query.filter_by(recipient_id=user.id, is_read=False).update({Notification.is_read: True})
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/notifications/read/<int:notif_id>', methods=['POST'])
@login_required
def mark_read_notification(notif_id):
    user = get_current_user()
    notification = Notification.query.filter_by(id=notif_id, recipient_id=user.id).first_or_404()
    notification.is_read = True
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/notifications/stream')
def sse_notification_stream():
    """Server-Sent Events endpoint to stream real-time toasts to the current logged-in user."""
    user_id = session.get('user_id')
    if not user_id:
        # Stream empty ping for unauthenticated or end connection
        def dummy():
            yield "data: {}\n\n"
        return Response(dummy(), mimetype='text/event-stream')
        
    q = queue.Queue(maxsize=15)
    
    if user_id not in sse_clients:
        sse_clients[user_id] = set()
    sse_clients[user_id].add(q)
    
    def event_generator():
        try:
            # Yield an initial connected event
            yield f"event: connect\ndata: Connected to real-time notification stream for User {user_id}\n\n"
            
            while True:
                # Blocks until a notification event comes in
                payload = q.get(block=True)
                import json
                yield f"data: {json.dumps(payload)}\n\n"
        except GeneratorExit:
            pass
        finally:
            if user_id in sse_clients:
                sse_clients[user_id].discard(q)
                if not sse_clients[user_id]:
                    del sse_clients[user_id]
                    
    return Response(event_generator(), mimetype='text/event-stream')

# ==========================================
# ADMINISTRATOR ROUTES
# ==========================================

@app.route('/admin')
@admin_required
def admin_dashboard():
    user = get_current_user()
    
    # Admin metrics
    total_users = User.query.count()
    total_songs = Song.query.count()
    total_comments = Comment.query.count()
    total_likes = Like.query.count()
    
    # Moderation grids
    users_list = User.query.filter(User.username != 'admin').order_by(User.created_at.desc()).all()
    comments_list = Comment.query.order_by(Comment.created_at.desc()).all()
    songs_list = Song.query.order_by(Song.created_at.desc()).all()
    
    return render_template('admin.html', user=user, 
                           users=users_list, 
                           comments=comments_list, 
                           songs=songs_list,
                           total_users=total_users, 
                           total_songs=total_songs, 
                           total_comments=total_comments, 
                           total_likes=total_likes)

@app.route('/admin/users/<int:target_id>/toggle-block', methods=['POST'])
@admin_required
def admin_toggle_block_user(target_id):
    target_user = User.query.get_or_404(target_id)
    if target_user.username == 'admin':
        return jsonify({'error': 'Cannot block default admin'}), 400
        
    target_user.is_blocked = not target_user.is_blocked
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/comments/<int:comment_id>/delete', methods=['POST'])
@admin_required
def admin_delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/songs/<int:song_id>/delete', methods=['POST'])
@admin_required
def admin_delete_song(song_id):
    song = Song.query.get_or_404(song_id)
    db.session.delete(song)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

# ==========================================
# APP INITIALIZATION & DEFAULT SEEDING
# ==========================================

# Use app context to initialize SQLite Tables and default admin account
with app.app_context():
    db.create_all()
    
    # Check if admin user exists, if not, create it
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        hashed_password = generate_password_hash('admin123')
        admin_user = User(
            username='admin',
            password_hash=hashed_password,
            is_admin=True
        )
        db.session.add(admin_user)
    
    # Seed user1
    u1 = User.query.filter_by(username='user1').first()
    if not u1:
        db.session.add(User(
            username='user1',
            password_hash=generate_password_hash('password1')
        ))
        
    # Seed user2
    u2 = User.query.filter_by(username='user2').first()
    if not u2:
        db.session.add(User(
            username='user2',
            password_hash=generate_password_hash('password2')
        ))
        
    db.session.commit()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
