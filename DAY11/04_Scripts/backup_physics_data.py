import os
import subprocess
import shutil
import hashlib
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# КОНФИГУРАЦИЯ (ИЗМЕНИТЕ ПОД СВОЮ СРЕДУ)
DATA_SOURCE = "./test_data/"  # Локальная папка для Windows
TAPE_TARGET = "./tape_library/"
LOCAL_BACKUP_DIR = "./local_backups/"
METADATA_DB = "./files_checksums.json"
IMMUTABLE_DAYS = 30

def check_disk_space():
    """Проверка свободного места (работает в Windows)"""
    try:
        # Используем shutil.disk_usage вместо os.statvfs
        usage = shutil.disk_usage(os.path.dirname(DATA_SOURCE) or '.')
        free_gb = usage.free / (1024**3)
        
        if free_gb < 1:  # Минимум 1 ГБ свободно (для теста)
            raise Exception(f"Недостаточно места: {free_gb:.2f} ГБ")
        logger.info(f"Свободно: {free_gb:.2f} ГБ")
        return free_gb
    except Exception as e:
        logger.warning(f"Не удалось проверить диск: {e}")
        return 10  # Возвращаем значение по умолчанию для теста

def calculate_sha256(file_path):
    """Вычисление SHA-256 контрольной суммы"""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
    except Exception as e:
        logger.error(f"Ошибка чтения файла {file_path}: {e}")
        return None
    return sha256_hash.hexdigest()

def create_test_data():
    """Создание тестовых данных, если их нет"""
    os.makedirs(DATA_SOURCE, exist_ok=True)
    
    # Создаем тестовые ROOT-файлы
    for i in range(1, 6):
        file_path = f"{DATA_SOURCE}/test_data_{i}.root"
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                f.write(f"=== ЭКСПЕРИМЕНТАЛЬНЫЕ ДАННЫЕ ===\n")
                f.write(f"Файл: test_data_{i}\n")
                f.write(f"Создан: {datetime.now()}\n")
                f.write("Данные: " + "X"*100 + "\n")
                f.write(f"Run: 2026-06-17\n")
                f.write(f"Event: {i*1000}\n")
            logger.info(f"Создан тестовый файл: {file_path}")
    
    # Создаем HDF5 файлы
    for i in range(1, 4):
        file_path = f"{DATA_SOURCE}/calibration_{i}.h5"
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                f.write(f"=== КАЛИБРОВКИ ===\n")
                f.write(f"Набор: {i}\n")
                f.write(f"Параметры: {i*100}\n")
                f.write(f"Дата: {datetime.now()}\n")
            logger.info(f"Создан HDF5 файл: {file_path}")

def copy_to_tape(source_file, date_str):
    """Копирование на ленту (эмуляция)"""
    os.makedirs(TAPE_TARGET, exist_ok=True)
    tape_archive = f"{TAPE_TARGET}/backup_{date_str}.tar"
    
    # Добавляем запись в архив
    with open(tape_archive, 'a') as f:
        f.write(f"FILE: {source_file}\n")
        f.write(f"BACKUP_TIME: {datetime.now()}\n")
        f.write("-"*50 + "\n")
    
    logger.info(f"✅ Файл добавлен на ленту: {source_file}")
    return tape_archive

def upload_to_local(file_path, s3_key):
    """Эмуляция загрузки в S3 - сохраняем локально"""
    os.makedirs(LOCAL_BACKUP_DIR, exist_ok=True)
    dest_file = f"{LOCAL_BACKUP_DIR}/{os.path.basename(s3_key)}"
    
    try:
        with open(file_path, 'rb') as src:
            with open(dest_file, 'wb') as dst:
                dst.write(src.read())
        logger.info(f"✅ Сохранен локально: {dest_file}")
        return dest_file
    except Exception as e:
        logger.error(f"Ошибка копирования: {e}")
        return None

def verify_worm_integrity(file_path):
    """Проверка WORM-целостности"""
    current_checksum = calculate_sha256(file_path)
    if current_checksum is None:
        return False
    
    if os.path.exists(METADATA_DB):
        try:
            with open(METADATA_DB, 'r') as f:
                checksums = json.load(f)
        except:
            checksums = {}
    else:
        checksums = {}
    
    if file_path in checksums:
        old_checksum = checksums[file_path]
        if old_checksum != current_checksum:
            logger.error(f"❌ WORM-нарушение! Файл изменен: {file_path}")
            return False
    else:
        checksums[file_path] = current_checksum
        with open(METADATA_DB, 'w') as f:
            json.dump(checksums, f, indent=2)
        logger.info(f"📝 Записан хеш для нового файла: {file_path}")
    
    return True

def create_parity_shard(file_path):
    """Создание четностного шарда для Reed-Solomon (эмуляция)"""
    parity_file = f"{file_path}.parity"
    try:
        with open(file_path, 'rb') as f_in:
            data = f_in.read()
            # Простая XOR-имитация четности
            parity = bytes([b ^ 0xFF for b in data])
        with open(parity_file, 'wb') as f_out:
            f_out.write(parity)
        logger.info(f"📊 Создан четностной шард: {parity_file}")
        return parity_file
    except Exception as e:
        logger.error(f"Ошибка создания шарда: {e}")
        return None

def cleanup_local(days=7):
    """Удаление локальных файлов старше 7 дней"""
    cutoff = datetime.now() - timedelta(days=days)
    deleted = 0
    
    for dir_path in [LOCAL_BACKUP_DIR, TAPE_TARGET]:
        if os.path.exists(dir_path):
            for f in os.listdir(dir_path):
                fpath = os.path.join(dir_path, f)
                try:
                    if os.path.getctime(fpath) < cutoff.timestamp():
                        os.remove(fpath)
                        deleted += 1
                        logger.info(f"🗑️ Удален: {fpath}")
                except:
                    pass
    
    logger.info(f"Удалено {deleted} старых файлов")

def backup_physics_data():
    """Основная функция бэкапа"""
    logger.info("🚀 ЗАПУСК БЭКАПА ФИЗИЧЕСКИХ ДАННЫХ")
    
    try:
        # Создаем тестовые данные
        create_test_data()
        
        # Проверяем диск
        check_disk_space()
        
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_log = []
        
        # Находим все ROOT-файлы
        all_files = list(Path(DATA_SOURCE).glob('**/*.root'))
        logger.info(f"📁 Найдено файлов .root: {len(all_files)}")
        
        for file_path in all_files:
            file_size_gb = os.path.getsize(file_path) / (1024**3)
            logger.info(f"📄 Обработка: {file_path.name} ({file_size_gb:.4f} ГБ)")
            
            # Проверка WORM
            if not verify_worm_integrity(str(file_path)):
                logger.warning(f"⚠️ Пропуск файла: {file_path}")
                continue
            
            # Создание четностного шарда
            create_parity_shard(str(file_path))
            
            # Копирование на ленту
            tape_archive = copy_to_tape(str(file_path), date_str)
            
            # Эмуляция загрузки в S3
            s3_key = f"physics_data/{date_str}/{file_path.name}"
            local_copy = upload_to_local(str(file_path), s3_key)
            
            backup_log.append({
                'file': str(file_path),
                'name': file_path.name,
                'size_gb': file_size_gb,
                'tape': tape_archive,
                'local_copy': local_copy,
                'checksum': calculate_sha256(str(file_path)),
                'timestamp': datetime.now().isoformat()
            })
            
            logger.info(f"✅ Успешно обработан: {file_path.name}")
        
        # Сохраняем лог
        log_file = f"./backup_log_{date_str}.json"
        with open(log_file, 'w') as f:
            json.dump(backup_log, f, indent=2)
        
        # Очистка
        cleanup_local()
        
        logger.info(f"🎉 БЭКАП ЗАВЕРШЕН! Обработано файлов: {len(backup_log)}")
        logger.info(f"📋 Лог сохранен: {log_file}")
        
        print("\n" + "="*70)
        print("✅ ДЕМОНСТРАЦИОННЫЙ БЭКАП ВЫПОЛНЕН УСПЕШНО!")
        print(f"📁 Локальные копии: {LOCAL_BACKUP_DIR}")
        print(f"📁 Копии на ленте: {TAPE_TARGET}")
        print(f"📋 Лог бэкапа: {log_file}")
        print("="*70)
        
    except Exception as e:
        logger.error(f"❌ Ошибка бэкапа: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    backup_physics_data()
