-- Sample seed data for quick dev testing
INSERT INTO brands (name) VALUES ('Generic');
INSERT INTO categories (name) VALUES ('resistor'), ('capacitor'), ('ic'), ('transistor'), ('diode'), ('tool'), ('supply');

INSERT INTO items (sku, name, brand_id, category_id, stock) VALUES
('1','Resistencia 10k', 1, 1, 100),
('2','Capacitor 10uF', 1, 2, 50),
('3','IC 74LS04', 1, 3, 20),
('4','Transistor 2N3904', 1, 4, 40),
('5','LED 5mm rojo', 1, 5, 200);
