-- Create Metabase user and database
CREATE ROLE jobanalytics WITH LOGIN PASSWORD 'jobanalytics';
CREATE DATABASE metabase OWNER jobanalytics;