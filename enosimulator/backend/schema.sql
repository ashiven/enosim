DROP TABLE IF EXISTS vminfo;
DROP TABLE IF EXISTS vmconfig;

CREATE TABLE vminfo (
    name TEXT NOT NULL,
    status TEXT NOT NULL,
    uptime TEXT NOT NULL,
    cpuusage REAL NOT NULL,
    ramusage REAL NOT NULL,
    netusage REAL NOT NULL,
    measuretime DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (name, measuretime)
);

CREATE TABLE vmconfig (
    name TEXT NOT NULL,
    cpu INTEGER NOT NULL,
    ram INTEGER NOT NULL,
    disk INTEGER NOT NULL,
    ip TEXT NOT NULL,
    PRIMARY KEY (name)
);