CREATE TABLE IF NOT EXISTS loan_data (
	person_age INTEGER,
	person_gender VARCHAR(6),
	person_education VARCHAR(30),
	person_income INTEGER,
	person_emp_exp INTEGER,
	person_home_ownership VARCHAR(20),
	loan_amnt INTEGER,
	loan_intent VARCHAR(30),
	loan_int_rate FLOAT,
	loan_percent_income FLOAT,
	cb_person_cred_hist_length INTEGER,
	credit_score INTEGER,
	previous_loan_defaults_on_file BOOLEAN,
	loan_status INTEGER,
	CONSTRAINT chk_loan_status CHECK (loan_status IN (0, 1))
);