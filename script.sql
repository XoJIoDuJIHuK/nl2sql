-- Create tables

CREATE TABLE producers (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) NOT NULL UNIQUE
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    producer_id INT REFERENCES producers(id),
    code VARCHAR(20) NOT NULL,
    label VARCHAR(30) NOT NULL UNIQUE
);

CREATE TABLE product_prerequisites (
    id SERIAL PRIMARY KEY,
    input_product_id INT REFERENCES products(id),
    output_product_id INT REFERENCES products(id),
    amount NUMERIC NOT NULL
);

CREATE TABLE final_demand (
    id SERIAL PRIMARY KEY,
    product_id INT REFERENCES products(id),
    amount INT NOT NULL
);

CREATE TABLE gross_plan (
    id SERIAL PRIMARY KEY,
    product_id INT REFERENCES products(id),
    amount INT NOT NULL
);

-- Insert producers
INSERT INTO producers (code) VALUES ('C1');
INSERT INTO producers (code) VALUES ('C2');
INSERT INTO producers (code) VALUES ('C3');
INSERT INTO producers (code) VALUES ('C4');
INSERT INTO producers (code) VALUES ('C5');
INSERT INTO producers (code) VALUES ('C6');
INSERT INTO producers (code) VALUES ('C7');

-- Insert products (cluster-specific products ri)
INSERT INTO products (producer_id, code, label) VALUES (1, 'PC-A', 'C1/PC-A');
INSERT INTO products (producer_id, code, label) VALUES (1, 'PC-B', 'C1/PC-B');
INSERT INTO products (producer_id, code, label) VALUES (2, 'PC-A', 'C2/PC-A');
INSERT INTO products (producer_id, code, label) VALUES (2, 'PC-B', 'C2/PC-B');
INSERT INTO products (producer_id, code, label) VALUES (3, 'SU-A', 'C3/SU-A');
INSERT INTO products (producer_id, code, label) VALUES (3, 'MB', 'C3/MB');
INSERT INTO products (producer_id, code, label) VALUES (4, 'CPS', 'C4/CPS');
INSERT INTO products (producer_id, code, label) VALUES (5, 'RAM', 'C5/RAM');
INSERT INTO products (producer_id, code, label) VALUES (6, 'MG', 'C6/MG');
INSERT INTO products (producer_id, code, label) VALUES (7, 'WAR', 'C7/WAR');

-- Insert product_prerequisites (from matrix A: input_id for row, output_id for col, amount a_row,col)
-- Non-zero entries only

-- Row 5 (C3/SU-A): 1 for cols 1-4
INSERT INTO product_prerequisites (input_product_id, output_product_id, amount) VALUES (5, 1, 1);
INSERT INTO product_prerequisites (input_product_id, output_product_id, amount) VALUES (5, 2, 1);
INSERT INTO product_prerequisites (input_product_id, output_product_id, amount) VALUES (5, 3, 1);
INSERT INTO product_prerequisites (input_product_id, output_product_id, amount) VALUES (5, 4, 1);

-- Row 6 (C3/MB): 1 for cols 1-5, 0.001 for col 10
INSERT INTO product_prerequisites (input_product_id, output_product_id, amount) VALUES (6, 1, 1);
INSERT INTO product_prerequisites (input_product_id, output_product_id, amount) VALUES (6, 2, 1);
INSERT INTO product_prerequisites (input_product_id, output_product_id, amount) VALUES (6, 3, 1);
INSERT INTO product_prerequisites (input_product_id, output_product_id, amount) VALUES (6, 4, 1);
INSERT INTO product_prerequisites (input_product_id, output_product_id, amount) VALUES (6, 5, 1);
INSERT INTO product_prerequisites (input_product_id, output_product_id, amount) VALUES (6, 10, 0.001);

-- Row 7 (C4/CPS): 1 for cols 1-5, 0.001 for cols 6,10
INSERT INTO product_prerequisites (input_product_id, output_product_id, amount) VALUES (7, 1, 1);
INSERT INTO product_prerequisites (input_product_id, output_product_id, amount) VALUES (7, 2, 1);
INSERT INTO product_prerequisites (input_product_id, output_product_id, amount) VALUES (7, 3, 1);
INSERT INTO product_prerequisites (input_product_id, output_product_id, amount) VALUES (7, 4, 1);
INSERT INTO product_prerequisites (input_product_id, output_product_id, amount) VALUES (7, 5, 1);
INSERT INTO product_prerequisites (input_product_id, output_product_id, amount) VALUES (7, 6, 0.001);
INSERT INTO product_prerequisites (input_product_id, output_product_id, amount) VALUES (7, 10, 0.001);

-- Row 8 (C5/RAM): 2 for col1, 4 for col2, 4 for col3, 2 for col4, 0.001 for col6, 1 for col7
INSERT INTO product_prerequisites (input_product_id, output_product_id, amount) VALUES (8, 1, 2);
INSERT INTO product_prerequisites (input_product_id, output_product_id, amount) VALUES (8, 2, 4);
INSERT INTO product_prerequisites (input_product_id, output_product_id, amount) VALUES (8, 3, 4);
INSERT INTO product_prerequisites (input_product_id, output_product_id, amount) VALUES (8, 4, 2);
INSERT INTO product_prerequisites (input_product_id, output_product_id, amount) VALUES (8, 6, 0.001);
INSERT INTO product_prerequisites (input_product_id, output_product_id, amount) VALUES (8, 7, 1);

-- Row 9 (C6/MG): 1 for cols 1-4
INSERT INTO product_prerequisites (input_product_id, output_product_id, amount) VALUES (9, 1, 1);
INSERT INTO product_prerequisites (input_product_id, output_product_id, amount) VALUES (9, 2, 1);
INSERT INTO product_prerequisites (input_product_id, output_product_id, amount) VALUES (9, 3, 1);
INSERT INTO product_prerequisites (input_product_id, output_product_id, amount) VALUES (9, 4, 1);

-- Row 10 (C7/WAR): 1 for cols 1-4, 0.005 for col 10
INSERT INTO product_prerequisites (input_product_id, output_product_id, amount) VALUES (10, 1, 1);
INSERT INTO product_prerequisites (input_product_id, output_product_id, amount) VALUES (10, 2, 1);
INSERT INTO product_prerequisites (input_product_id, output_product_id, amount) VALUES (10, 3, 1);
INSERT INTO product_prerequisites (input_product_id, output_product_id, amount) VALUES (10, 4, 1);
INSERT INTO product_prerequisites (input_product_id, output_product_id, amount) VALUES (10, 10, 0.005);

-- Insert final_demand (vector Y from Fig 3)
INSERT INTO final_demand (product_id, amount) VALUES (1, 10000);
INSERT INTO final_demand (product_id, amount) VALUES (2, 15000);
INSERT INTO final_demand (product_id, amount) VALUES (3, 20000);
INSERT INTO final_demand (product_id, amount) VALUES (4, 10000);
INSERT INTO final_demand (product_id, amount) VALUES (5, 5000);
INSERT INTO final_demand (product_id, amount) VALUES (6, 1000);
INSERT INTO final_demand (product_id, amount) VALUES (7, 2000);
INSERT INTO final_demand (product_id, amount) VALUES (8, 10000);
INSERT INTO final_demand (product_id, amount) VALUES (9, 5000);
INSERT INTO final_demand (product_id, amount) VALUES (10, 0);

-- Insert gross_plan (vector X computed in the paper, for later use)
INSERT INTO gross_plan (product_id, amount) VALUES (1, 10000);
INSERT INTO gross_plan (product_id, amount) VALUES (2, 15000);
INSERT INTO gross_plan (product_id, amount) VALUES (3, 20000);
INSERT INTO gross_plan (product_id, amount) VALUES (4, 10000);
INSERT INTO gross_plan (product_id, amount) VALUES (5, 25000);
INSERT INTO gross_plan (product_id, amount) VALUES (6, 61000);
INSERT INTO gross_plan (product_id, amount) VALUES (7, 18000);
INSERT INTO gross_plan (product_id, amount) VALUES (8, 180000);
INSERT INTO gross_plan (product_id, amount) VALUES (9, 30000);
INSERT INTO gross_plan (product_id, amount) VALUES (10, 50000);
