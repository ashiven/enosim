DROP TABLE IF EXISTS vminfo;

CREATE TABLE vminfo (
    name TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    uptime TEXT NOT NULL,
    cpuusage REAL NOT NULL,
    ramusage REAL NOT NULL,
    netusage REAL NOT NULL,
    measuretime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);