-- ============================================================
-- ДЕНЬ 5. Вариант 12. Рекламное агентство
-- Студент: [ФИО]
-- Группа: [название]
-- ============================================================

-- 1. Чистая среда: удаляем БД, если существует
DROP DATABASE IF EXISTS Variant12_Work;

-- 2. Создаём базу данных
CREATE DATABASE Variant12_Work;

-- 3. Переключаемся на неё
USE Variant12_Work;

-- ============================================================
-- ЗАДАНИЯ 1–5. Создание таблиц
-- ============================================================

-- Таблица клиентов
CREATE TABLE Clients (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    inn VARCHAR(12) UNIQUE NOT NULL,
    contact_person VARCHAR(100)
);

-- Таблица рекламных кампаний
CREATE TABLE Campaigns (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    budget DECIMAL(12,2) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    client_id INT NOT NULL,
    FOREIGN KEY (client_id) REFERENCES Clients(id) ON DELETE CASCADE
);

-- Таблица рекламных площадок
CREATE TABLE Platforms (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    price_per_unit DECIMAL(10,2) NOT NULL
);

-- Таблица размещений (кампания-площадка)
CREATE TABLE Placements (
    id INT PRIMARY KEY AUTO_INCREMENT,
    campaign_id INT NOT NULL,
    platform_id INT NOT NULL,
    cost DECIMAL(12,2) NOT NULL,
    units INT NOT NULL, -- количество единиц (показов, дней и т.д.)
    FOREIGN KEY (campaign_id) REFERENCES Campaigns(id) ON DELETE CASCADE,
    FOREIGN KEY (platform_id) REFERENCES Platforms(id) ON DELETE CASCADE
);

-- Таблица сотрудников
CREATE TABLE Employees (
    id INT PRIMARY KEY AUTO_INCREMENT,
    full_name VARCHAR(150) NOT NULL,
    position VARCHAR(100) NOT NULL,
    commission_percent DECIMAL(5,2) DEFAULT 0 -- процент от сделки
);

-- Таблица задач на кампании
CREATE TABLE CampaignTasks (
    id INT PRIMARY KEY AUTO_INCREMENT,
    employee_id INT NOT NULL,
    campaign_id INT NOT NULL,
    task_description TEXT NOT NULL,
    deadline DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'в работе',
    FOREIGN KEY (employee_id) REFERENCES Employees(id) ON DELETE CASCADE,
    FOREIGN KEY (campaign_id) REFERENCES Campaigns(id) ON DELETE CASCADE
);

-- ============================================================
-- ЗАДАНИЯ 6–10. Вставка тестовых данных
-- ============================================================

-- 6. Вставить 3 клиента
INSERT INTO Clients (name, inn, contact_person) VALUES
('Ромашка', '123456789012', 'Иванов И.И.'),
('Лютик', '234567890123', 'Петрова А.С.'),
('Василёк', '345678901234', 'Сидоров В.П.');

-- 7. Вставить 4 рекламные кампании
INSERT INTO Campaigns (name, budget, start_date, end_date, client_id) VALUES
('Летняя распродажа', 500000.00, '2025-06-01', '2025-08-31', 1),
('Новогодняя кампания', 800000.00, '2024-11-01', '2024-12-31', 1),
('Брендирование города', 300000.00, '2025-03-01', '2025-05-31', 2),
('Digital весна', 450000.00, '2025-02-01', '2025-04-30', 3);

-- 8. Вставить 3 площадки с ценой за единицу
INSERT INTO Platforms (name, price_per_unit) VALUES
('Яндекс.Директ', 15.50),
('VK Реклама', 12.00),
('Наружная реклама (щит)', 2500.00);

-- 9. Создать размещения
INSERT INTO Placements (campaign_id, platform_id, cost, units) VALUES
(1, 1, 155000.00, 10000),   -- Яндекс
(1, 2, 120000.00, 10000),   -- VK
(2, 1, 200000.00, 13000),
(2, 3, 250000.00, 100),     -- наружка
(3, 3, 300000.00, 120),
(4, 2, 180000.00, 15000);

-- 10. Вставить 2 сотрудников
INSERT INTO Employees (full_name, position, commission_percent) VALUES
('Менеджеров Алексей Петрович', 'менеджер', 5.00),
('Дизайнерова Ольга Ивановна', 'дизайнер', 2.00);

-- 11. Назначить задачи на кампании
INSERT INTO CampaignTasks (employee_id, campaign_id, task_description, deadline, status) VALUES
(1, 1, 'Разработать медиаплан', '2025-05-20', 'в работе'),
(1, 2, 'Отчёт по эффективности', '2024-12-10', 'выполнена'),
(2, 3, 'Креативы для наружки', '2025-02-25', 'в работе'),
(1, 4, 'Настройка таргетинга', '2025-01-30', 'выполнена');

-- ============================================================
-- ЗАДАНИЕ 12. Вывести все кампании клиента «Ромашка»
-- ============================================================
SELECT c.*
FROM Campaigns c
JOIN Clients cl ON c.client_id = cl.id
WHERE cl.name = 'Ромашка';

-- ============================================================
-- ЗАДАНИЕ 13. Найти площадку с наибольшей стоимостью размещения (MAX)
-- ============================================================
SELECT p.name, MAX(pl.cost) AS max_cost
FROM Placements pl
JOIN Platforms p ON pl.platform_id = p.id
GROUP BY p.id
ORDER BY max_cost DESC
LIMIT 1;

-- ============================================================
-- ЗАДАНИЕ 14. Отсортировать кампании по бюджету (убывание)
-- ============================================================
SELECT * FROM Campaigns ORDER BY budget DESC;

-- ============================================================
-- ЗАДАНИЕ 15. Вывести сотрудников, которые работают над кампанией №1
-- ============================================================
SELECT e.*
FROM Employees e
JOIN CampaignTasks ct ON e.id = ct.employee_id
WHERE ct.campaign_id = 1;

-- ============================================================
-- ЗАДАНИЕ 16. Подсчитать общую стоимость размещений для каждой кампании
-- ============================================================
SELECT campaign_id, SUM(cost) AS total_cost
FROM Placements
GROUP BY campaign_id;

-- ============================================================
-- ЗАДАНИЕ 17. Найти среднюю стоимость размещения на одной площадке
-- ============================================================
SELECT platform_id, AVG(cost) AS avg_cost_per_placement
FROM Placements
GROUP BY platform_id;

-- ============================================================
-- ЗАДАНИЕ 18. Вывести клиента и сумму потраченных средств на все его кампании
-- ============================================================
SELECT cl.name AS client_name, SUM(p.cost) AS total_spent
FROM Clients cl
JOIN Campaigns c ON cl.id = c.client_id
JOIN Placements p ON c.id = p.campaign_id
GROUP BY cl.id;

-- ============================================================
-- ЗАДАНИЕ 19. Сгруппировать размещения по площадкам, посчитать количество кампаний
-- ============================================================
SELECT pl.id AS platform_id, p.name, COUNT(DISTINCT campaign_id) AS campaigns_count
FROM Placements pl
JOIN Platforms p ON pl.platform_id = p.id
GROUP BY pl.id, p.name;

-- ============================================================
-- ЗАДАНИЕ 20. Найти кампании, которые не имеют размещений (LEFT JOIN)
-- ============================================================
SELECT c.*
FROM Campaigns c
LEFT JOIN Placements p ON c.id = p.campaign_id
WHERE p.id IS NULL;

-- ============================================================
-- ЗАДАНИЕ 21. Увеличить бюджет всех кампаний, начавшихся в 2025 году, на 10%
-- ============================================================
UPDATE Campaigns
SET budget = budget * 1.10
WHERE YEAR(start_date) = 2025;

-- Проверка
SELECT id, name, budget FROM Campaigns;

-- ============================================================
-- ЗАДАНИЕ 22. Удалить задачу со статусом «выполнена» (созданную ранее)
-- ============================================================
DELETE FROM CampaignTasks
WHERE status = 'выполнена';

-- Проверка
SELECT * FROM CampaignTasks;

-- ============================================================
-- ЗАДАНИЕ 23. Добавить столбец email в Employees
-- ============================================================
ALTER TABLE Employees ADD COLUMN email VARCHAR(100);

-- Заполним демо-значениями
UPDATE Employees SET email = CONCAT(LOWER(REPLACE(full_name, ' ', '.')), '@agency.ru');

-- ============================================================
-- ЗАДАНИЕ 24. Создать представление CampaignBudgetUsage
-- ============================================================
CREATE VIEW CampaignBudgetUsage AS
SELECT 
    c.id AS campaign_id,
    c.name AS campaign_name,
    c.budget,
    COALESCE(SUM(p.cost), 0) AS total_spent,
    (c.budget - COALESCE(SUM(p.cost), 0)) AS remaining_or_overspend
FROM Campaigns c
LEFT JOIN Placements p ON c.id = p.campaign_id
GROUP BY c.id, c.name, c.budget;

-- Проверка представления
SELECT * FROM CampaignBudgetUsage;

-- ============================================================
-- ЗАДАНИЕ 25. Сложный запрос: для каждого сотрудника вывести:
-- - общее количество кампаний, в которых он участвует
-- - общую стоимость размещений по этим кампаниям
-- - расчётный доход (процент от суммы размещений, если должность "менеджер")
-- ============================================================
SELECT 
    e.id,
    e.full_name,
    e.position,
    COUNT(DISTINCT ct.campaign_id) AS total_campaigns,
    COALESCE(SUM(p.cost), 0) AS total_placements_cost,
    CASE 
        WHEN e.position = 'менеджер' THEN COALESCE(SUM(p.cost), 0) * e.commission_percent / 100
        ELSE 0
    END AS estimated_income
FROM Employees e
LEFT JOIN CampaignTasks ct ON e.id = ct.employee_id
LEFT JOIN Placements p ON ct.campaign_id = p.campaign_id
GROUP BY e.id, e.full_name, e.position, e.commission_percent;

-- ============================================================
-- Финальная проверка: вывод всех таблиц для самоконтроля
-- ============================================================
SHOW TABLES;
SELECT '=== Clients ===' AS '';
SELECT * FROM Clients;
SELECT '=== Campaigns ===' AS '';
SELECT * FROM Campaigns;
SELECT '=== Platforms ===' AS '';
SELECT * FROM Platforms;
SELECT '=== Placements ===' AS '';
SELECT * FROM Placements;
SELECT '=== Employees ===' AS '';
SELECT * FROM Employees;
SELECT '=== CampaignTasks ===' AS '';
SELECT * FROM CampaignTasks;