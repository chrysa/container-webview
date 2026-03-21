import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { useLogin } from "@/domain/auth/queries";
import styles from "./LoginForm.module.scss";

export default function LoginForm() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();
  const { mutate, isPending, error } = useLogin();

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    mutate(
      { username, password },
      { onSuccess: () => navigate("/projects") },
    );
  };

  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <span className={styles.icon}>🐳</span>
        <h1 className={styles.title}>Docker Overview</h1>
        <p className={styles.subtitle}>Connectez-vous pour accéder à vos projets</p>
      </div>

      <form onSubmit={handleSubmit} className={styles.form}>
        <div className={styles.field}>
          <label htmlFor="username" className={styles.label}>Nom d&apos;utilisateur</label>
          <input
            id="username"
            type="text"
            className={styles.input}
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            autoComplete="username"
            autoFocus
          />
        </div>

        <div className={styles.field}>
          <label htmlFor="password" className={styles.label}>Mot de passe</label>
          <input
            id="password"
            type="password"
            className={styles.input}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            autoComplete="current-password"
          />
        </div>

        {error && (
          <div className={styles.error}>
            Identifiants incorrects. Veuillez réessayer.
          </div>
        )}

        <button type="submit" className={styles.btn} disabled={isPending}>
          {isPending ? "Connexion…" : "Se connecter"}
        </button>
      </form>
    </div>
  );
}
