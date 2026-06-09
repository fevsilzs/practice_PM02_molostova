"""
БД: Variant12_Work (Рекламное агентство)
Автор: Студент [Молсотвоа Мария]
Дата: 2026-06-09
"""

import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error
import csv
from datetime import datetime



def connect_db():
    """Подключение к базе данных MySQL (Рекламное агентство)"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",           # Ваш пользователь MySQL
            password="1234",     # Ваш пароль
            database="Variant12_Work"   # БД из предыдущего задания
        )
        return connection
    except Error as e:
        messagebox.showerror("Ошибка БД", f"Не удалось подключиться:\n{e}")
        return None



class DatabaseApp:
    def __init__(self, root, table_name, columns):
        """
        Инициализация приложения
        
        Параметры:
        - root: главное окно Tkinter
        - table_name: имя таблицы в БД (например, 'Campaigns')
        - columns: список словарей с описанием колонок
                  [
                    {'name': 'id', 'label': 'ID', 'pk': True, 'auto_increment': True},
                    {'name': 'name', 'label': 'Название', 'required': True},
                    ...
                  ]
        """
        self.root = root
        self.table_name = table_name
        self.columns = columns
        
        # Настройка главного окна
        self.root.title(f"Рекламное агентство - Управление: {table_name}")
        self.root.geometry("900x600")
        self.root.resizable(True, True)
        
        # Создаём интерфейс
        self.create_widgets()
        
        # Добавляем поиск (доп. задание)
        self.add_search()
        
        # Добавляем кнопку экспорта (доп. задание)
        self.add_export_button()
        
        # Загружаем данные
        self.refresh_table()
    
    
    def create_widgets(self):
        
        # === Рамка для полей ввода ===
        input_frame = tk.LabelFrame(self.root, text="Данные записи", padx=10, pady=10)
        input_frame.pack(pady=10, padx=10, fill=tk.X)
        
        self.entries = {}
        
        # Создаём поля для каждого столбца (кроме PK с AUTO_INCREMENT)
        row = 0
        col_index = 0
        for col in self.columns:
            # Пропускаем первичный ключ с auto_increment
            if col.get('pk') and col.get('auto_increment'):
                continue
            
            # Метка
            label = tk.Label(input_frame, text=f"{col['label']}:", font=('Arial', 10, 'bold'))
            label.grid(row=row, column=col_index*2, padx=5, pady=5, sticky="e")
            
            # Поле ввода
            entry = tk.Entry(input_frame, width=30, font=('Arial', 10))
            entry.grid(row=row, column=col_index*2+1, padx=5, pady=5)
            self.entries[col['name']] = entry
            
            col_index += 1
            # Размещаем по 2 поля в строке
            if col_index % 2 == 0:
                row += 1
                col_index = 0
        
        # === Рамка для кнопок ===
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="➕ Добавить", command=self.add_record,
                  bg="#90EE90", width=12, font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="✏️ Обновить", command=self.update_record,
                  bg="#FFD700", width=12, font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="🗑️ Удалить", command=self.delete_record,
                  bg="#FF6347", width=12, font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="🧹 Очистить", command=self.clear_entries,
                  width=12, font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="🔄 Показать всех", command=self.refresh_table,
                  width=15, font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        
        # === Рамка для таблицы Treeview ===
        tree_frame = tk.Frame(self.root)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Скроллбары
        scroll_y = tk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scroll_x = tk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Определяем колонки для Treeview
        columns_display = [col['name'] for col in self.columns]
        
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns_display,
            show="headings",
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set
        )
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)
        
        # Настраиваем заголовки и ширину колонок
        for col in self.columns:
            self.tree.heading(col['name'], text=col['label'])
            # Устанавливаем ширину в зависимости от типа
            if col.get('pk'):
                width = 50
            elif col['name'] in ['budget', 'total_spent']:
                width = 120
            else:
                width = 150
            self.tree.column(col['name'], width=width, anchor="center", minwidth=80)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Привязываем событие выбора строки
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
    
    def add_search(self):
        """Добавление строки поиска (дополнительное задание 6.1)"""
        search_frame = tk.LabelFrame(self.root, text="Поиск", padx=10, pady=5)
        search_frame.pack(pady=5, padx=10, fill=tk.X)
        
        tk.Label(search_frame, text="Ключевое слово:").pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(search_frame, width=40)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="🔍 Найти", command=self.search,
                  bg="#87CEEB").pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Сбросить", command=self.refresh_table,
                  bg="#D3D3D3").pack(side=tk.LEFT, padx=5)
    
    def add_export_button(self):
        """Добавление кнопки экспорта (дополнительное задание 6.2)"""
        export_frame = tk.Frame(self.root)
        export_frame.pack(pady=5)
        tk.Button(export_frame, text="📎 Экспорт в CSV", command=self.export_to_csv,
                  bg="#DDA0DD", width=15).pack()
    
    
    def refresh_table(self):
        """Обновить данные в таблице Treeview"""
        # Очищаем текущие данные
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        conn = connect_db()
        if not conn:
            return
        
        cursor = conn.cursor()
        
        # Формируем запрос SELECT
        columns_names = [col['name'] for col in self.columns]
        query = f"SELECT {', '.join(columns_names)} FROM {self.table_name}"
        
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            
            for row in rows:
                self.tree.insert("", tk.END, values=row)
            
            # Статистика
            self.root.title(f"Рекламное агентство - {self.table_name} (всего записей: {len(rows)})")
            
        except Error as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные:\n{e}")
        finally:
            cursor.close()
            conn.close()
    
    def search(self):
        """Поиск по ключевому слову (доп. задание 6.1)"""
        keyword = self.search_entry.get().strip()
        if not keyword:
            self.refresh_table()
            return
        
        conn = connect_db()
        if not conn:
            return
        
        cursor = conn.cursor()
        
        # Находим текстовые колонки (не PK)
        text_columns = [col['name'] for col in self.columns 
                        if not col.get('pk') and col['name'] not in ['budget', 'client_id']]
        
        if not text_columns:
            messagebox.showinfo("Инфо", "Нет текстовых колонок для поиска")
            return
        
        conditions = " OR ".join([f"{col} LIKE %s" for col in text_columns])
        query = f"SELECT * FROM {self.table_name} WHERE {conditions}"
        
        try:
            cursor.execute(query, tuple([f"%{keyword}%"] * len(text_columns)))
            rows = cursor.fetchall()
            
            # Очищаем таблицу
            for row in self.tree.get_children():
                self.tree.delete(row)
            
            # Заполняем результатами поиска
            for row in rows:
                self.tree.insert("", tk.END, values=row)
            
            self.root.title(f"Результаты поиска: '{keyword}' (найдено: {len(rows)})")
            
        except Error as e:
            messagebox.showerror("Ошибка", str(e))
        finally:
            cursor.close()
            conn.close()
    
    def export_to_csv(self):
        """Экспорт данных в CSV (доп. задание 6.2)"""
        filename = f"{self.table_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        conn = connect_db()
        if not conn:
            return
        
        cursor = conn.cursor()
        columns_names = [col['name'] for col in self.columns]
        query = f"SELECT * FROM {self.table_name}"
        
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            
            with open(filename, 'w', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file)
                # Заголовки на русском
                writer.writerow([col['label'] for col in self.columns])
                writer.writerows(rows)
            
            messagebox.showinfo("Успех", f"Данные экспортированы в файл:\n{filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
        finally:
            cursor.close()
            conn.close()
    
    def on_select(self, event):
        """При выборе строки в таблице — заполняем поля ввода"""
        selected = self.tree.selection()
        if not selected:
            return
        
        values = self.tree.item(selected[0])['values']
        
        # Заполняем поля ввода
        for i, col in enumerate(self.columns):
            col_name = col['name']
            if col_name in self.entries:
                self.entries[col_name].delete(0, tk.END)
                self.entries[col_name].insert(0, str(values[i]) if values[i] is not None else "")
    
    def get_pk_name(self):
        """Вернуть имя первичного ключа"""
        for col in self.columns:
            if col.get('pk'):
                return col['name']
        return None
    
    def add_record(self):
        """Добавить новую запись"""
        # Собираем значения из полей ввода
        values = {}
        for col_name, entry in self.entries.items():
            values[col_name] = entry.get().strip()
        
        # Проверяем обязательные поля
        for col in self.columns:
            col_name = col['name']
            if col.get('required') and col_name in self.entries and not values[col_name]:
                messagebox.showwarning("Ошибка", f"Поле '{col['label']}' обязательно для заполнения")
                return
        
        conn = connect_db()
        if not conn:
            return
        
        cursor = conn.cursor()
        
        # Формируем INSERT-запрос
        columns_names = list(values.keys())
        placeholders = ", ".join(["%s"] * len(columns_names))
        query = f"INSERT INTO {self.table_name} ({', '.join(columns_names)}) VALUES ({placeholders})"
        
        try:
            cursor.execute(query, list(values.values()))
            conn.commit()
            messagebox.showinfo("Успех", "Запись успешно добавлена")
            self.clear_entries()
            self.refresh_table()
        except Error as e:
            messagebox.showerror("Ошибка БД", str(e))
        finally:
            cursor.close()
            conn.close()
    
    def update_record(self):
        """Обновить выбранную запись"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Сначала выберите запись для обновления")
            return
        
        pk_name = self.get_pk_name()
        if not pk_name:
            messagebox.showerror("Ошибка", "Не найден первичный ключ")
            return
        
        # Получаем ID выбранной записи
        values_current = self.tree.item(selected[0])['values']
        pk_index = [col['name'] for col in self.columns].index(pk_name)
        pk_value = values_current[pk_index]
        
        # Собираем новые значения из полей
        new_values = {}
        for col_name, entry in self.entries.items():
            new_values[col_name] = entry.get().strip()
        
        conn = connect_db()
        if not conn:
            return
        
        cursor = conn.cursor()
        
        # Формируем UPDATE-запрос
        set_clause = ", ".join([f"{col} = %s" for col in new_values.keys()])
        query = f"UPDATE {self.table_name} SET {set_clause} WHERE {pk_name} = %s"
        
        try:
            params = list(new_values.values()) + [pk_value]
            cursor.execute(query, params)
            conn.commit()
            messagebox.showinfo("Успех", f"Запись с ID={pk_value} обновлена")
            self.refresh_table()
        except Error as e:
            messagebox.showerror("Ошибка БД", str(e))
        finally:
            cursor.close()
            conn.close()
    
    def delete_record(self):
        """Удалить выбранную запись"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Сначала выберите запись для удаления")
            return
        
        # Подтверждение удаления
        if not messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить эту запись?\nУдаление необратимо!"):
            return
        
        pk_name = self.get_pk_name()
        if not pk_name:
            return
        
        values = self.tree.item(selected[0])['values']
        pk_index = [col['name'] for col in self.columns].index(pk_name)
        pk_value = values[pk_index]
        
        conn = connect_db()
        if not conn:
            return
        
        cursor = conn.cursor()
        query = f"DELETE FROM {self.table_name} WHERE {pk_name} = %s"
        
        try:
            cursor.execute(query, (pk_value,))
            conn.commit()
            messagebox.showinfo("Успех", f"Запись с ID={pk_value} удалена")
            self.clear_entries()
            self.refresh_table()
        except Error as e:
            messagebox.showerror("Ошибка БД", str(e))
        finally:
            cursor.close()
            conn.close()
    
    def clear_entries(self):
        """Очистить все поля ввода"""
        for entry in self.entries.values():
            entry.delete(0, tk.END)

def main():
    root = tk.Tk()
    
    # Конфигурация для таблицы "Campaigns" (Рекламные кампании)
    # Из базы данных Variant12_Work
    columns = [
        {"name": "id", "label": "ID", "pk": True, "auto_increment": True},
        {"name": "name", "label": "Название кампании", "required": True},
        {"name": "budget", "label": "Бюджет (руб.)", "required": True},
        {"name": "start_date", "label": "Дата начала", "required": True},
        {"name": "end_date", "label": "Дата окончания", "required": True},
        {"name": "client_id", "label": "ID клиента", "required": True},
    ]
    
    app = DatabaseApp(root, table_name="Campaigns", columns=columns)
    root.mainloop()


if __name__ == "__main__":
    main()
