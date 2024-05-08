CREATE SCHEMA if not exists core;

create table if not exists core.users (
	id serial primary key not null,
	name varchar(254) not null,
	email varchar(254) not null,
	phone_number varchar(254) not null,		
	picture_url varchar(254) not null,
	registration_at timestamptz not null,
	created_at timestamptz default current_timestamp not null
);
