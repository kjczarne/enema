CREATE TABLE IF NOT EXISTS nodes(
    node_id INT NOT NULL PRIMARY KEY,
    ip_address TEXT,
    name TEXT NOT NULL,
    description TEXT
);
CREATE TABLE IF NOT EXISTS subsystems(
    subsystem_id INT NOT NULL PRIMARY KEY,
    node_id INT NOT NULL,
    kind TEXT,
    description TEXT,
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
