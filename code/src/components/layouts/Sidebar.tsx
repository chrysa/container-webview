import { useState } from "react";
import { NavLink, useParams } from "react-router-dom";
import {
  LayoutDashboard,
  GitBranch,
  Server,
  ScrollText,
  BarChart2,
  Bell,
  ChevronLeft,
  ChevronRight,
  FolderOpen,
} from "lucide-react";
import styles from "./Sidebar.module.scss";

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const { projectId } = useParams<{ projectId?: string }>();

  const projectLinks = projectId
    ? [
        { to: `/projects/${projectId}/topology`, icon: <GitBranch size={20} />, label: "Topologie" },
        { to: `/projects/${projectId}/services`, icon: <Server size={20} />, label: "Services" },
        { to: `/projects/${projectId}/logs`, icon: <ScrollText size={20} />, label: "Logs" },
        { to: `/projects/${projectId}/metrics`, icon: <BarChart2 size={20} />, label: "Métriques" },
      ]
    : [];

  return (
    <aside className={`${styles.sidebar} ${collapsed ? styles.collapsed : ""}`}>
      <div className={styles.top}>
        <span className={styles.logo}>{!collapsed && "Navigation"}</span>
        <button className={styles.toggleBtn} onClick={() => setCollapsed(!collapsed)}>
          {collapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
        </button>
      </div>

      <nav className={styles.nav}>
        <NavLink to="/projects" className={({ isActive }) => `${styles.link} ${isActive ? styles.active : ""}`}>
          <FolderOpen size={20} />
          {!collapsed && <span>Projets</span>}
        </NavLink>

        <NavLink to="/alerts" className={({ isActive }) => `${styles.link} ${isActive ? styles.active : ""}`}>
          <Bell size={20} />
          {!collapsed && <span>Alertes</span>}
        </NavLink>

        {projectLinks.length > 0 && (
          <>
            {!collapsed && <div className={styles.separator} />}
            {!collapsed && <span className={styles.sectionLabel}>Projet actif</span>}
            {projectLinks.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                className={({ isActive }) => `${styles.link} ${isActive ? styles.active : ""}`}
              >
                {link.icon}
                {!collapsed && <span>{link.label}</span>}
              </NavLink>
            ))}
          </>
        )}
      </nav>

      {!collapsed && (
        <div className={styles.footer}>
          <LayoutDashboard size={14} />
          <span>Docker Overview v1.0</span>
        </div>
      )}
    </aside>
  );
}
