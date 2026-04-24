import { afterEach, describe, expect, it } from 'vitest';
import { clearSession, getToken, getUsername, isAuthenticated, saveSession } from './auth';

describe('auth utils', () => {
  afterEach(() => {
    localStorage.clear();
  });

  describe('saveSession', () => {
    it('stores token and username in localStorage', () => {
      saveSession('my-token', 'john');
      expect(localStorage.getItem('token')).toBe('my-token');
      expect(localStorage.getItem('username')).toBe('john');
    });
  });

  describe('getToken', () => {
    it('returns null when no token is stored', () => {
      expect(getToken()).toBeNull();
    });

    it('returns the stored token', () => {
      localStorage.setItem('token', 'abc123');
      expect(getToken()).toBe('abc123');
    });
  });

  describe('getUsername', () => {
    it('returns null when no username is stored', () => {
      expect(getUsername()).toBeNull();
    });

    it('returns the stored username', () => {
      localStorage.setItem('username', 'alice');
      expect(getUsername()).toBe('alice');
    });
  });

  describe('clearSession', () => {
    it('removes token and username from localStorage', () => {
      localStorage.setItem('token', 'tok');
      localStorage.setItem('username', 'bob');
      clearSession();
      expect(localStorage.getItem('token')).toBeNull();
      expect(localStorage.getItem('username')).toBeNull();
    });

    it('does not throw when nothing is stored', () => {
      expect(() => clearSession()).not.toThrow();
    });
  });

  describe('isAuthenticated', () => {
    it('returns false when no token is stored', () => {
      expect(isAuthenticated()).toBe(false);
    });

    it('returns true when a token is stored', () => {
      localStorage.setItem('token', 'valid-token');
      expect(isAuthenticated()).toBe(true);
    });

    it('returns false after clearSession', () => {
      saveSession('tok', 'user');
      clearSession();
      expect(isAuthenticated()).toBe(false);
    });
  });
});
