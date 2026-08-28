-- ==== SCHEMA ====
CREATE TABLE IF NOT EXISTS "User" (
    gen_id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255),
    active BOOLEAN
);

CREATE TABLE IF NOT EXISTS "Namespace" (
    gen_id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255),
    quota INTEGER,
    sth TIMESTAMP
);

CREATE TABLE IF NOT EXISTS "User_OWNS_Namespace" (
    source_id VARCHAR(255) NOT NULL,
    target_id VARCHAR(255) NOT NULL,
    FOREIGN KEY (source_id) REFERENCES "User"(gen_id),
    FOREIGN KEY (target_id) REFERENCES "Namespace"(gen_id)
);

-- ==== INDEX ====
CREATE INDEX IF NOT EXISTS idx_User_OWNS_Namespace_source ON "User_OWNS_Namespace" (source_id);
CREATE INDEX IF NOT EXISTS idx_User_OWNS_Namespace_target ON "User_OWNS_Namespace" (target_id);

-- ==== DATA ====
-- batch od 20 - User
INSERT INTO "User" (gen_id, name, active) VALUES ('User_0', 'user_0', TRUE);
INSERT INTO "User" (gen_id, name, active) VALUES ('User_1', 'user_1', TRUE);
INSERT INTO "User" (gen_id, name, active) VALUES ('User_2', 'user_2', FALSE);
INSERT INTO "User" (gen_id, name, active) VALUES ('User_3', 'user_3', TRUE);
INSERT INTO "User" (gen_id, name, active) VALUES ('User_4', 'user_4', TRUE);
INSERT INTO "User" (gen_id, name, active) VALUES ('User_5', 'user_5', TRUE);
INSERT INTO "User" (gen_id, name, active) VALUES ('User_6', 'user_6', TRUE);
INSERT INTO "User" (gen_id, name, active) VALUES ('User_7', 'user_7', TRUE);
INSERT INTO "User" (gen_id, name, active) VALUES ('User_8', 'user_8', FALSE);
INSERT INTO "User" (gen_id, name, active) VALUES ('User_9', 'user_9', TRUE);
INSERT INTO "User" (gen_id, name, active) VALUES ('User_10', 'user_10', TRUE);
INSERT INTO "User" (gen_id, name, active) VALUES ('User_11', 'user_11', TRUE);
INSERT INTO "User" (gen_id, name, active) VALUES ('User_12', 'user_12', TRUE);
INSERT INTO "User" (gen_id, name, active) VALUES ('User_13', 'user_13', TRUE);
INSERT INTO "User" (gen_id, name, active) VALUES ('User_14', 'user_14', TRUE);
INSERT INTO "User" (gen_id, name, active) VALUES ('User_15', 'user_15', TRUE);
INSERT INTO "User" (gen_id, name, active) VALUES ('User_16', 'user_16', FALSE);
INSERT INTO "User" (gen_id, name, active) VALUES ('User_17', 'user_17', TRUE);
INSERT INTO "User" (gen_id, name, active) VALUES ('User_18', 'user_18', FALSE);
INSERT INTO "User" (gen_id, name, active) VALUES ('User_19', 'user_19', FALSE);

-- batch od 30 - Namespace
INSERT INTO "Namespace" (gen_id, name, quota, sth) VALUES ('Namespace_0', 'ns_0', 1, '2021-10-15T00:00:00');
INSERT INTO "Namespace" (gen_id, name, quota, sth) VALUES ('Namespace_1', 'ns_1', 90, '2024-09-27T00:00:00');
INSERT INTO "Namespace" (gen_id, name, quota, sth) VALUES ('Namespace_2', 'ns_2', 44, '2023-02-12T00:00:00');
INSERT INTO "Namespace" (gen_id, name, quota, sth) VALUES ('Namespace_3', 'ns_3', 20, '2022-05-31T00:00:00');
INSERT INTO "Namespace" (gen_id, name, quota, sth) VALUES ('Namespace_4', 'ns_4', 98, '2023-10-10T00:00:00');
INSERT INTO "Namespace" (gen_id, name, quota, sth) VALUES ('Namespace_5', 'ns_5', 14, '2021-01-14T00:00:00');
INSERT INTO "Namespace" (gen_id, name, quota, sth) VALUES ('Namespace_6', 'ns_6', 49, '2021-01-31T00:00:00');
INSERT INTO "Namespace" (gen_id, name, quota, sth) VALUES ('Namespace_7', 'ns_7', 46, '2023-11-09T00:00:00');
INSERT INTO "Namespace" (gen_id, name, quota, sth) VALUES ('Namespace_8', 'ns_8', 78, '2022-12-19T00:00:00');
INSERT INTO "Namespace" (gen_id, name, quota, sth) VALUES ('Namespace_9', 'ns_9', 6, '2025-02-24T00:00:00');
INSERT INTO "Namespace" (gen_id, name, quota, sth) VALUES ('Namespace_10', 'ns_10', 69, '2021-05-26T00:00:00');
INSERT INTO "Namespace" (gen_id, name, quota, sth) VALUES ('Namespace_11', 'ns_11', 49, '2020-11-18T00:00:00');
INSERT INTO "Namespace" (gen_id, name, quota, sth) VALUES ('Namespace_12', 'ns_12', 71, '2023-04-15T00:00:00');
INSERT INTO "Namespace" (gen_id, name, quota, sth) VALUES ('Namespace_13', 'ns_13', 81, '2024-01-21T00:00:00');
INSERT INTO "Namespace" (gen_id, name, quota, sth) VALUES ('Namespace_14', 'ns_14', 74, '2022-02-26T00:00:00');
INSERT INTO "Namespace" (gen_id, name, quota, sth) VALUES ('Namespace_15', 'ns_15', 91, '2020-10-11T00:00:00');
INSERT INTO "Namespace" (gen_id, name, quota, sth) VALUES ('Namespace_16', 'ns_16', 6, '2022-07-22T00:00:00');
INSERT INTO "Namespace" (gen_id, name, quota, sth) VALUES ('Namespace_17', 'ns_17', 99, '2023-03-31T00:00:00');
INSERT INTO "Namespace" (gen_id, name, quota, sth) VALUES ('Namespace_18', 'ns_18', 11, '2022-08-11T00:00:00');
INSERT INTO "Namespace" (gen_id, name, quota, sth) VALUES ('Namespace_19', 'ns_19', 13, '2024-04-05T00:00:00');
INSERT INTO "Namespace" (gen_id, name, quota, sth) VALUES ('Namespace_20', 'ns_20', 36, '2025-01-31T00:00:00');
INSERT INTO "Namespace" (gen_id, name, quota, sth) VALUES ('Namespace_21', 'ns_21', 82, '2024-02-03T00:00:00');
INSERT INTO "Namespace" (gen_id, name, quota, sth) VALUES ('Namespace_22', 'ns_22', 21, '2024-02-25T00:00:00');
INSERT INTO "Namespace" (gen_id, name, quota, sth) VALUES ('Namespace_23', 'ns_23', 46, '2022-05-08T00:00:00');
INSERT INTO "Namespace" (gen_id, name, quota, sth) VALUES ('Namespace_24', 'ns_24', 86, '2022-12-29T00:00:00');
INSERT INTO "Namespace" (gen_id, name, quota, sth) VALUES ('Namespace_25', 'ns_25', 90, '2020-10-19T00:00:00');
INSERT INTO "Namespace" (gen_id, name, quota, sth) VALUES ('Namespace_26', 'ns_26', 78, '2021-12-01T00:00:00');
INSERT INTO "Namespace" (gen_id, name, quota, sth) VALUES ('Namespace_27', 'ns_27', 69, '2022-09-29T00:00:00');
INSERT INTO "Namespace" (gen_id, name, quota, sth) VALUES ('Namespace_28', 'ns_28', 21, '2025-03-08T00:00:00');
INSERT INTO "Namespace" (gen_id, name, quota, sth) VALUES ('Namespace_29', 'ns_29', 49, '2023-01-10T00:00:00');

-- batch od 39 - OWNS
INSERT INTO "User_OWNS_Namespace" (source_id, target_id) VALUES ('User_0', 'Namespace_22');
INSERT INTO "User_OWNS_Namespace" (source_id, target_id) VALUES ('User_0', 'Namespace_17');
INSERT INTO "User_OWNS_Namespace" (source_id, target_id) VALUES ('User_0', 'Namespace_7');
INSERT INTO "User_OWNS_Namespace" (source_id, target_id) VALUES ('User_1', 'Namespace_10');
INSERT INTO "User_OWNS_Namespace" (source_id, target_id) VALUES ('User_1', 'Namespace_26');
INSERT INTO "User_OWNS_Namespace" (source_id, target_id) VALUES ('User_1', 'Namespace_24');
INSERT INTO "User_OWNS_Namespace" (source_id, target_id) VALUES ('User_2', 'Namespace_7');
INSERT INTO "User_OWNS_Namespace" (source_id, target_id) VALUES ('User_3', 'Namespace_25');
INSERT INTO "User_OWNS_Namespace" (source_id, target_id) VALUES ('User_4', 'Namespace_12');
INSERT INTO "User_OWNS_Namespace" (source_id, target_id) VALUES ('User_4', 'Namespace_8');
INSERT INTO "User_OWNS_Namespace" (source_id, target_id) VALUES ('User_5', 'Namespace_6');
INSERT INTO "User_OWNS_Namespace" (source_id, target_id) VALUES ('User_6', 'Namespace_28');
INSERT INTO "User_OWNS_Namespace" (source_id, target_id) VALUES ('User_6', 'Namespace_22');
INSERT INTO "User_OWNS_Namespace" (source_id, target_id) VALUES ('User_6', 'Namespace_10');
INSERT INTO "User_OWNS_Namespace" (source_id, target_id) VALUES ('User_7', 'Namespace_20');
INSERT INTO "User_OWNS_Namespace" (source_id, target_id) VALUES ('User_8', 'Namespace_12');
INSERT INTO "User_OWNS_Namespace" (source_id, target_id) VALUES ('User_8', 'Namespace_28');
INSERT INTO "User_OWNS_Namespace" (source_id, target_id) VALUES ('User_9', 'Namespace_14');
INSERT INTO "User_OWNS_Namespace" (source_id, target_id) VALUES ('User_9', 'Namespace_4');
INSERT INTO "User_OWNS_Namespace" (source_id, target_id) VALUES ('User_9', 'Namespace_8');
INSERT INTO "User_OWNS_Namespace" (source_id, target_id) VALUES ('User_10', 'Namespace_7');
INSERT INTO "User_OWNS_Namespace" (source_id, target_id) VALUES ('User_11', 'Namespace_17');
INSERT INTO "User_OWNS_Namespace" (source_id, target_id) VALUES ('User_11', 'Namespace_8');
INSERT INTO "User_OWNS_Namespace" (source_id, target_id) VALUES ('User_11', 'Namespace_23');
INSERT INTO "User_OWNS_Namespace" (source_id, target_id) VALUES ('User_12', 'Namespace_13');
INSERT INTO "User_OWNS_Namespace" (source_id, target_id) VALUES ('User_12', 'Namespace_28');
INSERT INTO "User_OWNS_Namespace" (source_id, target_id) VALUES ('User_12', 'Namespace_18');
INSERT INTO "User_OWNS_Namespace" (source_id, target_id) VALUES ('User_13', 'Namespace_11');
INSERT INTO "User_OWNS_Namespace" (source_id, target_id) VALUES ('User_13', 'Namespace_7');
INSERT INTO "User_OWNS_Namespace" (source_id, target_id) VALUES ('User_14', 'Namespace_16');
INSERT INTO "User_OWNS_Namespace" (source_id, target_id) VALUES ('User_15', 'Namespace_2');
INSERT INTO "User_OWNS_Namespace" (source_id, target_id) VALUES ('User_15', 'Namespace_24');
INSERT INTO "User_OWNS_Namespace" (source_id, target_id) VALUES ('User_16', 'Namespace_27');
INSERT INTO "User_OWNS_Namespace" (source_id, target_id) VALUES ('User_17', 'Namespace_4');
INSERT INTO "User_OWNS_Namespace" (source_id, target_id) VALUES ('User_18', 'Namespace_5');
INSERT INTO "User_OWNS_Namespace" (source_id, target_id) VALUES ('User_18', 'Namespace_25');
INSERT INTO "User_OWNS_Namespace" (source_id, target_id) VALUES ('User_18', 'Namespace_21');
INSERT INTO "User_OWNS_Namespace" (source_id, target_id) VALUES ('User_19', 'Namespace_19');
INSERT INTO "User_OWNS_Namespace" (source_id, target_id) VALUES ('User_19', 'Namespace_2');

