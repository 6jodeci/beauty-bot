CREATE TABLE service_group (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

INSERT INTO service_group (name, description, is_active, is_deleted)
VALUES
    ('Прически', 'Услуги по укладке, стрижке и окрашиванию волос', true, false),
    ('Маникюр и педикюр', 'Уход за ногтями, включая маникюр, педикюр и нанесение дизайна', true, false),
    ('Уход за кожей', 'Лицевые и тело уходовые процедуры для улучшения здоровья и внешнего вида кожи', true, false),
    ('Массаж', 'Расслабляющие и терапевтические массажи для разрядки мышечной напряженности и улучшения самочувствия', true, false),
    ('Макияж', 'Профессиональное нанесение макияжа для специальных случаев или ежедневного ношения', true, false),
    ('Депиляция', 'Удаление волос с помощью воска', true, false);
