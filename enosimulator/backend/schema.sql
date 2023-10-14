DROP TABLE IF EXISTS vminfo;

CREATE TABLE vminfo (
    name TEXT NOT NULL,
    status TEXT NOT NULL,
    uptime TEXT NOT NULL,
    cpuusage REAL NOT NULL,
    ramusage REAL NOT NULL,
    netusage REAL NOT NULL,
    measuretime TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (name, measuretime)
);