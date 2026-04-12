export function getToken(): string | null {
  return localStorage.getItem('token');
}

export function getUsername(): string | null {
  return localStorage.getItem('username');
}

export function saveSession(token: string, username: string): void {
  localStorage.setItem('token', token);
  localStorage.setItem('username', username);
}

export function clearSession(): void {
  localStorage.removeItem('token');
  localStorage.removeItem('username');
}

export function isAuthenticated(): boolean {
  return Boolean(getToken());
}
