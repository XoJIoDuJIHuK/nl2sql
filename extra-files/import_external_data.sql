-- Import script for external data from PlanXSQLServer
-- Run this after script.sql

-- Helper function to find product ID by dynamically computed label
-- Label format: {producer_code}/{abstract_product_name}
CREATE OR REPLACE FUNCTION get_product_id_by_label(product_label TEXT)
RETURNS INT AS $$
DECLARE
    parts TEXT[];
    producer_code TEXT;
    abstract_name TEXT;
BEGIN
    parts := string_to_array(product_label, '/');
    producer_code := parts[1];
    abstract_name := parts[2];
    
    RETURN (
        SELECT p.id
        FROM products p
        JOIN producers pr ON p.producer_id = pr.id
        JOIN abstract_products ap ON p.production_id = ap.id
        WHERE pr.code = producer_code AND ap.name = abstract_name
        LIMIT 1
    );
END;
$$ LANGUAGE plpgsql;

-- Create external consumer plan and get its ID using a DO block
DO $$
DECLARE
    v_plan_id INT;
BEGIN
    INSERT INTO production_plans(master_plan_id)
    VALUES (NULL)
    RETURNING id INTO v_plan_id;

    -- Insert plan values for the external plan
    INSERT INTO plan_values(product_id, plan_id, value) VALUES
        (get_product_id_by_label('C1/PC-A'), v_plan_id, 10000),
        (get_product_id_by_label('C1/PC-B'), v_plan_id, 15000),
        (get_product_id_by_label('C2/PC-A'), v_plan_id, 20000),
        (get_product_id_by_label('C2/PC-B'), v_plan_id, 10000),
        (get_product_id_by_label('C3/SU-A'),  v_plan_id, 5000),
        (get_product_id_by_label('C3/MB'),   v_plan_id, 1000),
        (get_product_id_by_label('C4/CPS'),  v_plan_id, 2000),
        (get_product_id_by_label('C5/RAM'), v_plan_id, 10000),
        (get_product_id_by_label('C6/MG'),   v_plan_id, 5000);
END $$;

-- Drop the helper function after use
DROP FUNCTION IF EXISTS get_product_id_by_label(TEXT);

COMMIT;
