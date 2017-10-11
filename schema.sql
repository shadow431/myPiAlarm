create database piAlarm;
use piAlarm;
grant ALL on piAlarm.*
to piAlarm identified by 'myAlarm';

create table temps (
id int auto_increment primary key,
sensorId int,
c float,
f float,
raw int,
time TIMESTAMP
);

create table sensors (
id int auto_increment primary key,
clientId text,
pinNumber int,
type text,
serialNum text,
name text,
description text,
status boolean
);

create table clients(
id int auto_increment primary key,
identifier text,
model text,
name text,
description text,
lastCheckin timestamp
);

create table zones (
id int auto_increment primary key,
status boolean,
triggered boolean,
name text,
description text
);

create table zoneAssignment (
zoneId int,
sensorId int,
primary key (zoneId, sensorId)
);

create table users (
id int auto_increment primary key,
name text,
description text
);

create table codes(
id int auto_increment primary key,
code int,
userId int,
description text,
unique (code)
);

create table codeZones (
codeId int,
zoneId int,
primary key (codeId,zoneId)
);

create table settings (
id int auto_increment primary key,
name text,
value text
);

create table eventLog (
id int auto_increment primary key,
clientId int,
sensorId int,
zoneId int,
userId int,
eventType int,
time timestamp
);

create table events (
id int auto_increment primary key,
name text,
description text
);
