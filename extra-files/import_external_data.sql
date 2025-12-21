-- Import script for external data from PlanXSQLServer
-- Run this after migration_script.sql

-- Insert external consumer plans
INSERT INTO ext_consumer_plan(id, period, comment)
VALUES ('0000000001', 1, 'test')
ON CONFLICT (id) DO NOTHING;

-- Helper function to find product ID by label
CREATE OR REPLACE FUNCTION get_product_id_by_label(product_label TEXT)
RETURNS INT AS $$
BEGIN
    RETURN (SELECT id FROM products WHERE label = product_label LIMIT 1);
END;
$$ LANGUAGE plpgsql;

-- Insert plan values
-- Note: These map to your existing products using the updated labels
INSERT INTO plan_value(id_product, value, id_extconsumerplan) VALUES
    (get_product_id_by_label('C1/PCA'), 10000, '0000000001'),
    (get_product_id_by_label('C1/PCB'), 15000, '0000000001'),
    (get_product_id_by_label('C2/PCA'), 20000, '0000000001'),
    (get_product_id_by_label('C2/PCB'), 10000, '0000000001'),
    (get_product_id_by_label('C3/SUA'),  5000, '0000000001'),
    (get_product_id_by_label('C3/MB'),   1000, '0000000001'),
    (get_product_id_by_label('C4/CPS'),  2000, '0000000001'),
    (get_product_id_by_label('C5/RAM'), 10000, '0000000001'),
    (get_product_id_by_label('C6/MG'),   5000, '0000000001')
ON CONFLICT (id_product, id_extconsumerplan) DO NOTHING;

-- Clear existing cost data and insert new cost coefficients
DELETE FROM cost;

INSERT INTO cost(id_product_resource, id_product_result, coefficient) VALUES
    -- C3/SUA costs
    (get_product_id_by_label('C3/SUA'), get_product_id_by_label('C2/PCA'), 1),

    -- C3/MB costs
    (get_product_id_by_label('C3/MB'),  get_product_id_by_label('C1/PCA'), 1),
    (get_product_id_by_label('C3/MB'),  get_product_id_by_label('C1/PCB'), 1),
    (get_product_id_by_label('C3/MB'),  get_product_id_by_label('C2/PCB'), 1),
    (get_product_id_by_label('C3/MB'),  get_product_id_by_label('C3/SUA'), 1),
    (get_product_id_by_label('C3/MB'),  get_product_id_by_label('C7/WAR'), 0.001),

    -- C4/CPS costs
    (get_product_id_by_label('C4/CPS'),  get_product_id_by_label('C1/PCA'), 1),
    (get_product_id_by_label('C4/CPS'),  get_product_id_by_label('C1/PCB'), 1),
    (get_product_id_by_label('C4/CPS'),  get_product_id_by_label('C2/PCB'), 1),
    (get_product_id_by_label('C4/CPS'),  get_product_id_by_label('C3/SUA'), 1),
    (get_product_id_by_label('C4/CPS'),  get_product_id_by_label('C7/WAR'), 0.01),

    -- C5/RAM costs
    (get_product_id_by_label('C5/RAM'),  get_product_id_by_label('C1/PCA'), 2),
    (get_product_id_by_label('C5/RAM'),  get_product_id_by_label('C1/PCB'), 4),
    (get_product_id_by_label('C5/RAM'),  get_product_id_by_label('C2/PCB'), 4),
    (get_product_id_by_label('C5/RAM'),  get_product_id_by_label('C3/SUA'), 2),
    (get_product_id_by_label('C5/RAM'),  get_product_id_by_label('C7/WAR'), 0.001),

    -- C6/MG costs
    (get_product_id_by_label('C6/MG'),  get_product_id_by_label('C1/PCA'), 1),
    (get_product_id_by_label('C6/MG'),  get_product_id_by_label('C1/PCB'), 1),
    (get_product_id_by_label('C6/MG'),  get_product_id_by_label('C2/PCA'), 1),
    (get_product_id_by_label('C6/MG'),  get_product_id_by_label('C2/PCB'), 1),
    (get_product_id_by_label('C6/MG'),  get_product_id_by_label('C7/WAR'), 0.005),

    -- C7/WAR costs
    (get_product_id_by_label('C7/WAR'),  get_product_id_by_label('C1/PCA'), 1),
    (get_product_id_by_label('C7/WAR'),  get_product_id_by_label('C1/PCB'), 1),
    (get_product_id_by_label('C7/WAR'),  get_product_id_by_label('C2/PCA'), 1),
    (get_product_id_by_label('C7/WAR'),  get_product_id_by_label('C2/PCB'), 1);

-- Drop the helper function after use
DROP FUNCTION IF EXISTS get_product_id_by_label(TEXT);

COMMIT;