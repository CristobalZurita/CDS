INSERT OR IGNORE INTO user_roles (id, name) VALUES
  (1, 'admin'),
  (2, 'technician'),
  (3, 'client');

INSERT OR IGNORE INTO users (id, email, username, hashed_password, first_name, last_name, role_id, is_active, is_verified, created_at, updated_at)
VALUES
  (1, 'admin@cirujanodesintetizadores.cl', 'admin', '$2b$12$WRYXGsi1OsLSvzKFroBOQ.OlqGKveYiWjx5Q85UZ2u2Ls0LLhQhpW', 'Admin', 'User', 1, 1, 1, datetime('now'), datetime('now'));
