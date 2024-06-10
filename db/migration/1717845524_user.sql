create table user (
    id bigint auto_increment primary key,
    phone_number varchar(20) not null,
    email varchar(100) not null,
    full_name varchar(100) not null,
    is_admin boolean default FALSE,
    created_at timestamp not null default now(),
    updated_at timestamp not null default now()
);
