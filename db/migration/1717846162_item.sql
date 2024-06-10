CREATE TABLE item (
    id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description VARCHAR(255),
    quantity INT NOT NULL,
    item_group_name VARCHAR(255) NOT NULL REFERENCES item_group(name),
    price FLOAT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW() ON UPDATE NOW()
);
 
INSERT INTO item (name, description, quantity, item_group_name, price, is_active, is_deleted, created_at, updated_at) VALUES
('Шампунь L''Oreal для сухого волоса', 'Шампунь L''Oreal Professional для сухого и поврежденного волоса. Увлажняет и питает волосы.', 10, 'Шампуни и бальзамы', 500.00, TRUE, FALSE, NOW(), NOW()),
('Бальзам L''Oreal для сухого волоса', 'Бальзам L''Oreal Professional для сухого и поврежденного волоса. Увлажняет и питает волосы.', 10, 'Шампуни и бальзамы', 600.00, TRUE, FALSE, NOW(), NOW()),
('Краска L''Oreal Majirel для волос', 'Постоянная краска для волос L''Oreal Majirel. Богатый цвет и глубокое питание волос.', 5, 'Краски для волос', 1500.00, TRUE, FALSE, NOW(), NOW()),
('Тональный крем BB Cream Erborian', 'Тональный крем BB Cream Erborian с легкой текстурой и средним покрытием. Увлажняет и защищает кожу от вредных воздействий.', 15, 'Косметика для лица', 1200.00, TRUE, FALSE, NOW(), NOW()),
('Гель для душа Dove', 'Гель для душа Dove с ароматом граната и витамином Е. Увлажняет и питает кожу.', 20, 'Косметика для тела', 200.00, TRUE, FALSE, NOW(), NOW()),
('Щетка для волос Tangle Teezer', 'Щетка для волос Tangle Teezer с гибкими зубцами. Распутывает волосы без боли и повреждений.', 10, 'Аксессуары для волос', 1500.00, TRUE, FALSE, NOW(), NOW()),
('Ножницы для маникюра Klipp', 'Ножницы для маникюра Klipp с тонкими и острыми лезвиями. Идеальны для резки ногтей и кутикулы.', 20, 'Аксессуары для маникюра и педикюра', 250.00, TRUE, FALSE, NOW(), NOW()),
('Маска для волос Kerastase', 'Маска для волос Kerastase с питательными ингредиентами. Восстанавливает и увлажняет поврежденные волосы.', 8, 'Шампуни и бальзамы', 2500.00, TRUE, FALSE, NOW(), NOW()),
('Краска Schwarzkopf для волос', 'Постоянная краска для волос Schwarzkopf. Насыщенный цвет и долговечность.', 7, 'Краски для волос', 1200.00, TRUE, FALSE, NOW(), NOW()),
('Тональный крем CC Cream L''Oreal', 'Тональный крем CC Cream L''Oreal с высоким покрытием и SPF 20. Защищает и увлажняет кожу.', 12, 'Косметика для лица', 1000.00, TRUE, FALSE, NOW(), NOW()),
('Скраб для тела The Body Shop', 'Скраб для тела The Body Shop с натуральными ингредиентами. Очищает и увлажняет кожу.', 18, 'Косметика для тела', 800.00, TRUE, FALSE, NOW(), NOW()),
('Резинки для волос Invisibobble', 'Резинки для волос Invisibobble без следов и узлов. Не повреждают волосы.', 25, 'Аксессуары для волос', 300.00, TRUE, FALSE, NOW(), NOW()),
('Набор для маникюра Mavala', 'Набор для маникюра Mavala с инструментами для резки и обработки ногтей. Включает ножницы, пилу, щипцы и оттолкнутель кутикулы.', 10, 'Аксессуары для маникюра и педикюра', 1500.00, TRUE, FALSE, NOW(), NOW());