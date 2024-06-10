create table item_order(
    id bigserial primary key,
    user_id bigint not null references user(id),
    item_id bigint not null references item(id),
    quantity int not null default 1,
    comment varchar,
    booked_at timestamp not null,
    created_at timestamp not null default now(),
    updated_at timestamp not null default now()
)