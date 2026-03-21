import { Moon, Sun, LogOut } from "lucide-react";
import { useTheme } from "@/hooks/useTheme";
import { useAuth } from "@/hooks/useAuth";
import styles from "./Header.module.scss";

export default function Header() {
  const { theme, setTheme } = useTheme();
  const { username, logout } = useAuth();

  return (
    <header className={styles.header}>
      <div className={styles.left}>
        <span className={styles.brand}>🐳 Docker Overview</span>
      </div>
      <div className={styles.right}>
        <span className={styles.username}>{username}</span>
        <button
          className={styles.iconBtn}
          onClick={() => setTheme(theme === "light" ? "dark" : "light")}
          title="Changer le thème"
        >
          {theme === "light" ? <Moon size={18} /> : <Sun size={18} />}
        </button>
        <button className={styles.iconBtn} onClick={logout} title="Se déconnecter">
          <LogOut size={18} />
        </button>
      </div>
    </header>
  );
}
