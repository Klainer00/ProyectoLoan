-- Tabla 1: Datos Crudos (Originales y Sucios)
-- Se usan tipos de datos flexibles (VARCHAR) para aceptar nulos, textos mal formateados y errores temporales.
CREATE TABLE IF NOT EXISTS loan_data_raw (
    id_loan SERIAL PRIMARY KEY,
    person_age VARCHAR(50),
    person_gender VARCHAR(50),
    person_education VARCHAR(50),
    person_income VARCHAR(50),
    person_emp_exp VARCHAR(50),
    person_home_ownership VARCHAR(50),
    loan_amnt VARCHAR(50),
    loan_intent VARCHAR(50),
    loan_int_rate VARCHAR(50),
    loan_percent_income VARCHAR(50),
    cb_person_cred_hist_length VARCHAR(50),
    credit_score VARCHAR(50),
    previous_loan_defaults_on_file VARCHAR(50),
    loan_status VARCHAR(50)
);

-- Tabla 2: Datos Limpios (Procesados)
-- Tipos de datos estrictos y validados por el pipeline DataOps.
CREATE TABLE IF NOT EXISTS loan_data_clean (
    id_loan SERIAL PRIMARY KEY,
    person_age INTEGER,
    person_gender VARCHAR(6),
    person_education VARCHAR(30),
    person_income INTEGER,
    person_emp_exp INTEGER,
    person_home_ownership VARCHAR(30),
    loan_amnt INTEGER,
    loan_intent VARCHAR(30),
    loan_int_rate FLOAT,
    loan_percent_income FLOAT,
    cb_person_cred_hist_length INTEGER,
    credit_score INTEGER,
    previous_loan_defaults_on_file BOOLEAN,
    loan_status BOOLEAN
);