create table outline_users(
    key_id text null primary key,
    name text null,
    password text null,
    server_port text null,
    method text null,
    access_url text null,
    data_limit numeric null,
    create_dt timestamp not null
);
