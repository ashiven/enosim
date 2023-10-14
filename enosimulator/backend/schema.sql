DROP TABLE IF EXISTS vminfo;
DROP TABLE IF EXISTS vmconfig;

CREATE TABLE vminfo (
    name TEXT NOT NULL,
    ip TEXT NOT NULL,
    cpu TEXT NOT NULL,
    ram TEXT NOT NULL,
    disk TEXT NOT NULL,
    status TEXT NOT NULL,
    uptime TEXT NOT NULL,
    cpuusage REAL NOT NULL,
    ramusage REAL NOT NULL,
    netusage REAL NOT NULL,
    measuretime DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (name, measuretime)
);
