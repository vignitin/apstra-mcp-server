#!/usr/bin/env python3
"""
Session-based authentication manager for Apstra MCP Server
Validates user credentials against Apstra and manages sessions
"""

import secrets
import time
import json
import sys
from typing import Dict, Optional, Tuple
import apstra_core
from logger_config import setup_logger

logger = setup_logger(__name__)


class SessionManager:
    def __init__(self, session_timeout: int = 3600):
        """
        Initialize session manager
        
        Args:
            session_timeout: Session timeout in seconds (default: 1 hour)
        """
        self.sessions: Dict[str, Dict] = {}
        self.session_timeout = session_timeout
    
    def _generate_session_token(self) -> str:
        """Generate a secure session token"""
        return secrets.token_urlsafe(32)
    
    def _is_session_expired(self, session_info: Dict) -> bool:
        """Check if session has expired"""
        return time.time() - session_info['last_accessed'] > self.session_timeout
    
    def authenticate_user(self, username: str, password: str, 
                         server: str, port: str = "443") -> Tuple[bool, str, Optional[str]]:
        """
        Authenticate user against Apstra server
        
        Args:
            username: Apstra username
            password: Apstra password  
            server: Apstra server hostname/IP
            port: Apstra server port
            
        Returns:
            Tuple of (success, message, session_token)
        """
        try:
            # Prepare user credentials for validation
            user_credentials = {
                'username': username,
                'password': password,
                'server': server,
                'port': port
            }
            
            # Validate credentials by attempting authentication with Apstra
            logger.debug(f"Validating credentials for {username} against {server}:{port}")
            headers, auth_server_with_port = apstra_core.auth(user_credentials=user_credentials)
            
            # If we get here, authentication was successful
            session_token = self._generate_session_token()
            
            # Store session with user credentials (keep original server/port separate for future use)
            self.sessions[session_token] = {
                'username': username,
                'password': password,
                'server': server,  # Original server without port
                'port': port,      # Original port
                'created_at': time.time(),
                'last_accessed': time.time(),
                'auth_headers': headers,
                'auth_server_with_port': auth_server_with_port  # Combined server:port from auth
            }
            
            logger.debug(f"Session created for {username}: {session_token[:16]}...")
            return True, "Authentication successful", session_token
            
        except Exception as e:
            error_msg = f"Authentication failed: {str(e)}"
            logger.debug(error_msg)
            return False, error_msg, None
    
    def validate_session(self, session_token: str) -> Optional[Dict]:
        """
        Validate session token and return user credentials
        
        Args:
            session_token: Session token to validate
            
        Returns:
            User credentials dict if valid, None if invalid
        """
        if not session_token or session_token not in self.sessions:
            return None
        
        session_info = self.sessions[session_token]
        
        # Check if session has expired
        if self._is_session_expired(session_info):
            logger.debug(f"Session expired for {session_info['username']}: {session_token[:16]}...")
            del self.sessions[session_token]
            return None
        
        # Update last accessed time
        session_info['last_accessed'] = time.time()
        
        # Return user credentials for Apstra API calls
        return {
            'username': session_info['username'],
            'password': session_info['password'],
            'server': session_info['server'],
            'port': session_info['port']
        }
    
    def logout_session(self, session_token: str) -> bool:
        """
        Logout/invalidate a session
        
        Args:
            session_token: Session token to logout
            
        Returns:
            True if session was found and removed, False otherwise
        """
        if session_token in self.sessions:
            username = self.sessions[session_token]['username']
            del self.sessions[session_token]
            logger.debug(f"Session logged out for {username}: {session_token[:16]}...")
            return True
        return False
    
    def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions
        
        Returns:
            Number of sessions cleaned up
        """
        expired_sessions = []
        current_time = time.time()
        
        for token, session_info in self.sessions.items():
            if current_time - session_info['last_accessed'] > self.session_timeout:
                expired_sessions.append(token)
        
        count = 0
        for token in expired_sessions:
            username = self.sessions[token]['username']
            del self.sessions[token]
            logger.debug(f"Cleaned up expired session for {username}: {token[:16]}...")
            count += 1
        
        return count
    
    def get_session_info(self, session_token: str) -> Optional[Dict]:
        """
        Get session information (without credentials)
        
        Args:
            session_token: Session token
            
        Returns:
            Session info dict without sensitive data
        """
        if session_token not in self.sessions:
            return None
        
        session = self.sessions[session_token]
        
        if self._is_session_expired(session):
            return None
        
        return {
            'username': session['username'],
            'server': session['server'],
            'port': session['port'],
            'created_at': session['created_at'],
            'last_accessed': session['last_accessed'],
            'expires_in': self.session_timeout - (time.time() - session['last_accessed'])
        }
    
    def list_active_sessions(self) -> Dict:
        """
        List all active sessions (for debugging/monitoring)
        
        Returns:
            Dict with session information
        """
        active_sessions = {}
        current_time = time.time()
        
        for token, session_info in self.sessions.items():
            if not self._is_session_expired(session_info):
                active_sessions[token[:16] + "..."] = {
                    'username': session_info['username'],
                    'server': session_info['server'],
                    'created_at': session_info['created_at'],
                    'last_accessed': session_info['last_accessed'],
                    'expires_in': self.session_timeout - (current_time - session_info['last_accessed'])
                }
        
        return active_sessions


# Global session manager instance
session_manager = SessionManager(session_timeout=3600)  # 1 hour timeout