CREATE SCHEMA meetperry;

CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS
$$
BEGIN
    NEW.updated_date = NOW();
    RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';

CREATE TABLE meetperry.task (
    id BIGSERIAL PRIMARY KEY,
    external_id text NOT NULL UNIQUE,
    user_id text NOT NULL,
    content text NOT NULL,
    completed_date timestamp with time zone NULL,
    deleted_date timestamp with time zone NULL,
    created_date timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_date timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER set_timestamp
BEFORE UPDATE ON meetperry.task
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();

