CREATE TABLE service (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    service_group_name VARCHAR(255) NOT NULL,
    price FLOAT NOT NULL,
    gender ENUM('male', 'female', 'all') NOT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (service_group_name) REFERENCES service_group(name)
);

INSERT INTO service (name, description, service_group_name, price, gender, is_deleted, is_active)
VALUES
    ('Стрижка мужская', 'Стрижка для мужчин любой сложности', 'Прически', 500.00, 'male', false, true),
    ('Стрижка женская', 'Стрижка для женщин любой сложности', 'Прически', 1000.00, 'female', false, true),
    ('Окрашивание волос', 'Окрашивание волос в любой цвет', 'Прически', 2000.00, 'all', false, true),
    ('Маникюр классический', 'Классический маникюр с уходом за ногтями', 'Маникюр и педикюр', 700.00, 'all', false, true),
    ('Маникюр с дизайном', 'Маникюр с нанесением дизайна на ногти', 'Маникюр и педикюр', 1500.00, 'all', false, true),
    ('Педикюр классический', 'Классический педикюр с уходом за ногтями', 'Маникюр и педикюр', 800.00, 'all', false, true),
    ('Уход за лицом', 'Лицевые процедуры для улучшения здоровья и внешнего вида кожи', 'Уход за кожей', 1500.00, 'all', false, true),
    ('Классический массаж', 'Расслабляющий массаж для разрядки мышечной напряженности', 'Массаж', 1500.00, 'all', false, true),
    ('Макияж дневной', 'Профессиональное нанесение макияжа для ежедневного ношения', 'Макияж', 1000.00, 'all', false, true),
    ('Макияж вечерний', 'Профессиональное нанесение макияжа для специальных случаев', 'Макияж', 2000.00, 'all', false, true),
    ('Депиляция воском', 'Удаление волос с помощью воска', 'Депиляция', 500.00, 'all', false, true);
