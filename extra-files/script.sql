-- Create tables

DROP TABLE IF EXISTS plan_values;
DROP TABLE IF EXISTS production_chains;
DROP TABLE IF EXISTS production_plans;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS producers;
DROP TABLE IF EXISTS abstract_products;

CREATE TABLE abstract_products (
  id SERIAL PRIMARY KEY,
  name VARCHAR NOT NULL UNIQUE
);
COMMENT ON TABLE abstract_products IS 'Abstract products that may be produced by cluster members into concrete products with different properties';

CREATE TABLE producers (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) NOT NULL UNIQUE
);
COMMENT ON TABLE producers IS 'Producers that produce products and supply each other and provide products for external sales';

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    production_id INT NOT NULL REFERENCES abstract_products(id),
    producer_id INT NOT NULL REFERENCES producers(id)
);
COMMENT ON TABLE products IS 'Concrete products produced by specific producer and being "implementations" of abstract products';

CREATE TABLE production_chains (
    id SERIAL PRIMARY KEY,
    input_product_id INT NOT NULL REFERENCES products(id),
    output_product_id INT NOT NULL REFERENCES products(id),
    amount NUMERIC(20, 6) NOT NULL
);
COMMENT ON TABLE production_chains IS 'Shows what products with what amount is needed to produce one unit of specific concrete product';

CREATE TABLE production_plans (
  id SERIAL PRIMARY KEY,
  master_plan_id INT REFERENCES production_plans(id)
);
COMMENT ON TABLE production_plans IS 'Stores data for plans on production (plans without master_plan_id are considered master plans and are meant for export)';

CREATE TABLE plan_values (
  id SERIAL PRIMARY KEY,
  product_id INT NOT NULL REFERENCES products(id),
  plan_id INT NOT NULL REFERENCES production_plans(id),
  value NUMERIC(20, 6) NOT NULL
);
COMMENT ON TABLE plan_values IS 'Concrete values of products needed to be produced according to a specific plan';
COMMIT;

INSERT INTO abstract_products (name) VALUES ('PC-A');
INSERT INTO abstract_products (name) VALUES ('PC-B');
INSERT INTO abstract_products (name) VALUES ('SU-A');
INSERT INTO abstract_products (name) VALUES ('MB');
INSERT INTO abstract_products (name) VALUES ('CPS');
INSERT INTO abstract_products (name) VALUES ('RAM');
INSERT INTO abstract_products (name) VALUES ('MG');
INSERT INTO abstract_products (name) VALUES ('WAR');
COMMIT;

-- Insert producers
INSERT INTO producers (code) VALUES ('C1');
INSERT INTO producers (code) VALUES ('C2');
INSERT INTO producers (code) VALUES ('C3');
INSERT INTO producers (code) VALUES ('C4');
INSERT INTO producers (code) VALUES ('C5');
INSERT INTO producers (code) VALUES ('C6');
INSERT INTO producers (code) VALUES ('C7');
COMMIT;

-- Insert products (cluster-specific products ri)
INSERT INTO products (producer_id, production_id) VALUES (1, 1);
INSERT INTO products (producer_id, production_id) VALUES (1, 2);
INSERT INTO products (producer_id, production_id) VALUES (2, 1);
INSERT INTO products (producer_id, production_id) VALUES (2, 2);
INSERT INTO products (producer_id, production_id) VALUES (3, 3);
INSERT INTO products (producer_id, production_id) VALUES (3, 4);
INSERT INTO products (producer_id, production_id) VALUES (4, 5);
INSERT INTO products (producer_id, production_id) VALUES (5, 6);
INSERT INTO products (producer_id, production_id) VALUES (6, 7);
INSERT INTO products (producer_id, production_id) VALUES (7, 8);
COMMIT;

-- Insert production_chains (from matrix A: input_id for row, output_id for col, amount a_row,col)
-- Non-zero entries only

-- Row 5 (C3/SU-A): 1 for cols 1-4
INSERT INTO production_chains (input_product_id, output_product_id, amount) VALUES (5, 1, 1);
INSERT INTO production_chains (input_product_id, output_product_id, amount) VALUES (5, 2, 1);
INSERT INTO production_chains (input_product_id, output_product_id, amount) VALUES (5, 3, 1);
INSERT INTO production_chains (input_product_id, output_product_id, amount) VALUES (5, 4, 1);

-- Row 6 (C3/MB): 1 for cols 1-5, 0.001 for col 10
INSERT INTO production_chains (input_product_id, output_product_id, amount) VALUES (6, 1, 1);
INSERT INTO production_chains (input_product_id, output_product_id, amount) VALUES (6, 2, 1);
INSERT INTO production_chains (input_product_id, output_product_id, amount) VALUES (6, 3, 1);
INSERT INTO production_chains (input_product_id, output_product_id, amount) VALUES (6, 4, 1);
INSERT INTO production_chains (input_product_id, output_product_id, amount) VALUES (6, 5, 1);
INSERT INTO production_chains (input_product_id, output_product_id, amount) VALUES (6, 10, 0.001);

-- Row 7 (C4/CPS): 1 for cols 1-5, 0.001 for cols 6,10
INSERT INTO production_chains (input_product_id, output_product_id, amount) VALUES (7, 1, 1);
INSERT INTO production_chains (input_product_id, output_product_id, amount) VALUES (7, 2, 1);
INSERT INTO production_chains (input_product_id, output_product_id, amount) VALUES (7, 3, 1);
INSERT INTO production_chains (input_product_id, output_product_id, amount) VALUES (7, 4, 1);
INSERT INTO production_chains (input_product_id, output_product_id, amount) VALUES (7, 5, 1);
INSERT INTO production_chains (input_product_id, output_product_id, amount) VALUES (7, 6, 0.001);
INSERT INTO production_chains (input_product_id, output_product_id, amount) VALUES (7, 10, 0.001);

-- Row 8 (C5/RAM): 2 for col1, 4 for col2, 4 for col3, 2 for col4, 0.001 for col6, 1 for col7
INSERT INTO production_chains (input_product_id, output_product_id, amount) VALUES (8, 1, 2);
INSERT INTO production_chains (input_product_id, output_product_id, amount) VALUES (8, 2, 4);
INSERT INTO production_chains (input_product_id, output_product_id, amount) VALUES (8, 3, 4);
INSERT INTO production_chains (input_product_id, output_product_id, amount) VALUES (8, 4, 2);
INSERT INTO production_chains (input_product_id, output_product_id, amount) VALUES (8, 6, 0.001);
INSERT INTO production_chains (input_product_id, output_product_id, amount) VALUES (8, 7, 1);

-- Row 9 (C6/MG): 1 for cols 1-4
INSERT INTO production_chains (input_product_id, output_product_id, amount) VALUES (9, 1, 1);
INSERT INTO production_chains (input_product_id, output_product_id, amount) VALUES (9, 2, 1);
INSERT INTO production_chains (input_product_id, output_product_id, amount) VALUES (9, 3, 1);
INSERT INTO production_chains (input_product_id, output_product_id, amount) VALUES (9, 4, 1);

-- Row 10 (C7/WAR): 1 for cols 1-4, 0.005 for col 10
INSERT INTO production_chains (input_product_id, output_product_id, amount) VALUES (10, 1, 1);
INSERT INTO production_chains (input_product_id, output_product_id, amount) VALUES (10, 2, 1);
INSERT INTO production_chains (input_product_id, output_product_id, amount) VALUES (10, 3, 1);
INSERT INTO production_chains (input_product_id, output_product_id, amount) VALUES (10, 4, 1);
INSERT INTO production_chains (input_product_id, output_product_id, amount) VALUES (10, 10, 0.005);
