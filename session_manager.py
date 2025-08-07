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
    
    def authenticate_user(self, apstra_username: str, apstra_password: str, 
                         apstra_server: str, apstra_port: str = "443") -> Tuple[bool, str, Optional[str]]:
        """
        Authenticate user against Apstra server
        
        Args:
            apstra_username: Apstra username
            apstra_password: Apstra password  
            apstra_server: Apstra server hostname/IP
            apstra_port: Apstra server port
            
        Returns:
            Tuple of (success, message, session_token)
        """
        try:
            # Prepare user credentials for validation
            user_credentials = {
                'apstra_username': apstra_username,
                'apstra_password': apstra_password,
                'apstra_server': apstra_server,
                'apstra_port': apstra_port
            }
            
            # Validate credentials by attempting authentication with Apstra
            print(f"DEBUG: Validating credentials for {apstra_username} against {apstra_server}:{apstra_port}", file=sys.stderr)
            headers, server = apstra_core.auth(user_credentials=user_credentials)
            
            # If we get here, authentication was successful
            session_token = self._generate_session_token()
            
            # Store session with user credentials
            self.sessions[session_token] = {
                'apstra_username': apstra_username,
                'apstra_password': apstra_password,
                'apstra_server': apstra_server,
                'apstra_port': apstra_port,
                'created_at': time.time(),
                'last_accessed': time.time(),
                'auth_headers': headers,
                'server': server
            }
            
            print(f"DEBUG: Session created for {apstra_username}: {session_token[:16]}...", file=sys.stderr)
            return True, "Authentication successful", session_token
            
        except Exception as e:
            error_msg = f"Authentication failed: {str(e)}"
            print(f"DEBUG: {error_msg}", file=sys.stderr)
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
            print(f"DEBUG: Session expired for {session_info['apstra_username']}: {session_token[:16]}...", file=sys.stderr)
            del self.sessions[session_token]
            return None
        
        # Update last accessed time
        session_info['last_accessed'] = time.time()
        
        # Return user credentials for Apstra API calls
        return {
            'apstra_username': session_info['apstra_username'],
            'apstra_password': session_info['apstra_password'],
            'apstra_server': session_info['apstra_server'],
            'apstra_port': session_info['apstra_port']
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
            username = self.sessions[session_token]['apstra_username']
            del self.sessions[session_token]
            print(f"DEBUG: Session logged out for {username}: {session_token[:16]}...", file=sys.stderr)
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
            username = self.sessions[token]['apstra_username']
            del self.sessions[token]
            print(f"DEBUG: Cleaned up expired session for {username}: {token[:16]}...", file=sys.stderr)
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
            'apstra_username': session['apstra_username'],
            'apstra_server': session['apstra_server'],
            'apstra_port': session['apstra_port'],
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
                    'apstra_username': session_info['apstra_username'],
                    'apstra_server': session_info['apstra_server'],
                    'created_at': session_info['created_at'],
                    'last_accessed': session_info['last_accessed'],
                    'expires_in': self.session_timeout - (current_time - session_info['last_accessed'])
                }
        
        return active_sessions


# Global session manager instance
session_manager = SessionManager(session_timeout=3600)  # 1 hour timeout