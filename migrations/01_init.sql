CREATE SCHEMA if not exists core;

create table if not exists core.chunks (
	id serial primary key not null,
	content VARCHAR(32512) not null,
	company_name VARCHAR(254),
	created_at timestamptz default current_timestamp not null
);
