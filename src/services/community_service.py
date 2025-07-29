"""
Enhanced Community Service for ClimateCoach
Handles community posts, comments, social interactions, challenges, and gamification
"""

import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import random

class EnhancedCommunityService:
    def __init__(self, db_path: str = "climatecoach.db"):
        self.db_path = db_path
        self.init_community_tables()
    
    def init_community_tables(self):
        """Initialize additional community tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Community challenges table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS community_challenges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                target_co2_savings REAL,
                duration_days INTEGER DEFAULT 7,
                created_by INTEGER,
                start_date DATE,
                end_date DATE,
                participants_count INTEGER DEFAULT 0,
                total_savings REAL DEFAULT 0,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users (id)
            )
        """)
        
        # Challenge participants table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS challenge_participants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                challenge_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                progress_savings REAL DEFAULT 0,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (challenge_id) REFERENCES community_challenges (id),
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(challenge_id, user_id)
            )
        """)
        
        # User achievements table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                achievement_type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                icon TEXT DEFAULT '🏆',
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # User badges table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_badges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                badge_type TEXT NOT NULL,
                badge_name TEXT NOT NULL,
                description TEXT NOT NULL,
                earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                icon TEXT DEFAULT '🎖️',
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def create_post(self, user_id: int, title: str, content: str, category: str = "general") -> bool:
        """Create a new community post"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO community_posts (user_id, title, content, category)
                VALUES (?, ?, ?, ?)
            """, (user_id, title, content, category))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error creating post: {e}")
            return False
    
    def get_posts(self, category: str = None, limit: int = 20) -> List[Dict]:
        """Get community posts with user information"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if category and category != "all":
                cursor.execute("""
                    SELECT p.id, p.title, p.content, p.category, p.likes, p.created_at,
                           u.username, u.full_name
                    FROM community_posts p
                    JOIN users u ON p.user_id = u.id
                    WHERE p.category = ?
                    ORDER BY p.created_at DESC
                    LIMIT ?
                """, (category, limit))
            else:
                cursor.execute("""
                    SELECT p.id, p.title, p.content, p.category, p.likes, p.created_at,
                           u.username, u.full_name
                    FROM community_posts p
                    JOIN users u ON p.user_id = u.id
                    ORDER BY p.created_at DESC
                    LIMIT ?
                """, (limit,))
            
            posts = []
            for row in cursor.fetchall():
                posts.append({
                    'id': row[0],
                    'title': row[1],
                    'content': row[2],
                    'category': row[3],
                    'likes': row[4],
                    'created_at': row[5],
                    'username': row[6],
                    'full_name': row[7]
                })
            
            conn.close()
            return posts
            
        except Exception as e:
            print(f"Error getting posts: {e}")
            return []
    
    def add_comment(self, post_id: int, user_id: int, content: str) -> bool:
        """Add a comment to a post"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO community_comments (post_id, user_id, content)
                VALUES (?, ?, ?)
            """, (post_id, user_id, content))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error adding comment: {e}")
            return False
    
    def get_comments(self, post_id: int) -> List[Dict]:
        """Get comments for a specific post"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT c.id, c.content, c.created_at, u.username, u.full_name
                FROM community_comments c
                JOIN users u ON c.user_id = u.id
                WHERE c.post_id = ?
                ORDER BY c.created_at ASC
            """, (post_id,))
            
            comments = []
            for row in cursor.fetchall():
                comments.append({
                    'id': row[0],
                    'content': row[1],
                    'created_at': row[2],
                    'username': row[3],
                    'full_name': row[4]
                })
            
            conn.close()
            return comments
            
        except Exception as e:
            print(f"Error getting comments: {e}")
            return []
    
    def like_post(self, post_id: int) -> bool:
        """Like a post (increment likes counter)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE community_posts 
                SET likes = likes + 1 
                WHERE id = ?
            """, (post_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error liking post: {e}")
            return False
    
    def get_user_stats(self, user_id: int) -> Dict:
        """Get user community statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get posts count
            cursor.execute("SELECT COUNT(*) FROM community_posts WHERE user_id = ?", (user_id,))
            posts_count = cursor.fetchone()[0]
            
            # Get comments count
            cursor.execute("SELECT COUNT(*) FROM community_comments WHERE user_id = ?", (user_id,))
            comments_count = cursor.fetchone()[0]
            
            # Get total likes received
            cursor.execute("SELECT SUM(likes) FROM community_posts WHERE user_id = ?", (user_id,))
            total_likes = cursor.fetchone()[0] or 0
            
            conn.close()
            
            return {
                'posts_count': posts_count,
                'comments_count': comments_count,
                'total_likes': total_likes
            }
            
        except Exception as e:
            print(f"Error getting user stats: {e}")
            return {'posts_count': 0, 'comments_count': 0, 'total_likes': 0}
    
    def get_trending_topics(self) -> List[Dict]:
        """Get trending topics based on recent posts"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT category, COUNT(*) as post_count, SUM(likes) as total_likes
                FROM community_posts
                WHERE created_at >= date('now', '-7 days')
                GROUP BY category
                ORDER BY post_count DESC, total_likes DESC
                LIMIT 5
            """)
            
            topics = []
            for row in cursor.fetchall():
                topics.append({
                    'category': row[0],
                    'post_count': row[1],
                    'total_likes': row[2]
                })
            
            conn.close()
            return topics
            
        except Exception as e:
            print(f"Error getting trending topics: {e}")
            return []

# Initialize community service
community_service = EnhancedCommunityService()
