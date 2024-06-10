CREATE TABLE item_group (
    id BIGINT NOT NULL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

INSERT INTO item_group (id, name, description, is_active, is_deleted, created_at, updated_at) VALUES
(1, 'Шампуни и бальзамы', 'Средства для ухода за волосами: шампуни, бальзамы, маски и кондиционеры', TRUE, FALSE, NOW(), NOW()),
(2, 'Краски для волос', 'Краски для волос различных брендов и цветов', TRUE, FALSE, NOW(), NOW()),
(3, 'Косметика для лица', 'Косметика для ухода за лицом: тональные кремы, пудра, румяна, тень для век и карандаши для бровей', TRUE, FALSE, NOW(), NOW()),
(4, 'Косметика для тела', 'Косметика для ухода за телом: гели для душа, скрабы, кремы и масла для тела', TRUE, FALSE, NOW(), NOW()),
(5, 'Аксессуары для волос', 'Аксессуары для волос: щетки, гребни, заколки, резинки и шпильки', TRUE, FALSE, NOW(), NOW()),
(6, 'Аксессуары для маникюра и педикюра', 'Аксессуары для маникюра и педикюра: ножницы, пилы, наборы для маникюра и педикюра', TRUE, FALSE, NOW(), NOW());
