CREATE TABLE IF NOT EXISTS nodes(
    node_id INT NOT NULL PRIMARY KEY,
    ip_address TEXT,
    node_name TEXT NOT NULL,
    node_description TEXT
);
CREATE TABLE IF NOT EXISTS subsystems(
    subsystem_id INT NOT NULL PRIMARY KEY,
    subsystem_name TEXT NOT NULL,
    node_id INT NOT NULL,
    kind TEXT,
    subsystem_description TEXT,
    is_busy INT,   -- 1 == true, 0 == false, null == unknown status
    FOREIGN KEY (node_id) REFERENCES nodes(node_id)
);
CREATE TABLE IF NOT EXISTS schedules(
    event_id INT NOT NULL PRIMARY KEY,
    subsystem_id INT NOT NULL,
    start INT,     -- Unix timestamp
    finish INT,    -- Unix timestamp
    FOREIGN KEY (subsystem_id) REFERENCES subsystems(subsystem_id)
);
CREATE TABLE IF NOT EXISTS auth(
    id INT NOT NULL PRIMARY KEY,
    user TEXT,
    password TEXT  -- Fernet-encrypted passwords (see: crypto.py)
);
CREATE TABLE IF NOT EXISTS api_auth(
    id INT NOT NULL PRIMARY KEY,
    owner TEXT,
    token TEXT     -- Fernet-encrypted allowed API tokens
);