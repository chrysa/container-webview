export interface AuthContextType {
  token: string | null
  username: string
  isAuthenticated: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => void
}
