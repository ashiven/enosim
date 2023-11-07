DROP TABLE IF EXISTS vminfo;

CREATE TABLE vminfo (
    name TEXT NOT NULL,
    ip TEXT NOT NULL,
    cpu TEXT NOT NULL,
    ram TEXT NOT NULL,
    disk TEXT NOT NULL,
    status TEXT NOT NULL,
    uptime REAL NOT NULL,
    cpuusage REAL NOT NULL,
    ramusage REAL NOT NULL,
    netrx REAL NOT NULL,
    nettx REAL NOT NULL,
    measuretime DATETIME DEFAULT (datetime('now','localtime')) NOT NULL,
    PRIMARY KEY (name, measuretime)
);

CREATE INDEX name_measuretime_vms ON vminfo (name, measuretime);


DROP TABLE IF EXISTS containerinfo;

CREATE TABLE containerinfo (
    name TEXT NOT NULL,
    cpuusage REAL NOT NULL,
    ramusage REAL NOT NULL,
    netrx REAL NOT NULL,
    nettx REAL NOT NULL,
    measuretime DATETIME DEFAULT (datetime('now','localtime')) NOT NULL,
    PRIMARY KEY (name, measuretime)
);

CREATE INDEX name_measuretime_containers ON containerinfo (name, measuretime);
