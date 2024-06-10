create table service_booking (
    id bigserial primary key,
    user_id bigint not null references users(id),
    service_id bigint not null references service(id),
    booked_at timestamp not null,
    created_at timestamp not null default now(),
    updated_at timestamp not null default now()
)