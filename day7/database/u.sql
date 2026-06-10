-- Создание базы данных (если нужно)
CREATE DATABASE IF NOT EXISTS pizzeria_db;
USE pizzeria_db;

-- Создание таблицы пользователей
CREATE TABLE IF NOT EXISTS Пользователи (
    id_пользователя INT PRIMARY KEY AUTO_INCREMENT,
    логин VARCHAR(50) UNIQUE NOT NULL,
    пароль_hash VARCHAR(255) NOT NULL,
    роль ENUM('admin', 'worker') DEFAULT 'worker',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Добавление тестовых пользователей (пароли будут перезаписаны скриптом)
INSERT INTO Пользователи (логин, пароль_hash, роль) VALUES 
('admin', 'temp', 'admin'),
('worker', 'temp', 'worker')
ON DUPLICATE KEY UPDATE логин=логин; 