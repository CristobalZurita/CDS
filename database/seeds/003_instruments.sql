INSERT OR IGNORE INTO instruments (id, brand_id, name, model, type, year, description, valor_estimado, image, created_at, updated_at) VALUES
  (1, 1, 'Roland', 'Juno-106', 'synthesizer', 1984, 'Sintetizador analogico clasico', 1500000, NULL, datetime('now'), datetime('now')),
  (2, 2, 'Korg', 'MS-20', 'synthesizer', 1978, 'Sintetizador semi-modular', 1200000, NULL, datetime('now'), datetime('now')),
  (3, 3, 'Yamaha', 'DX7', 'synthesizer', 1983, 'Sintetizador FM', 900000, NULL, datetime('now'), datetime('now'));
