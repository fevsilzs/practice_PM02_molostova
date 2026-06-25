Recovery Runbook - Аварийное восстановление

Научный проект CERN-like

Версия: 1.0 | Дата: 17.06.2026





1\. ОБЩАЯ ИНФОРМАЦИЯ



Сценарий: Коррупция данных на ленточной библиотеке в ЦОД-1

Цель: Восстановить доступ к данным за 48 часов (RTO)

Тип данных: WORM (Write Once, Read Many)

Ответственный: Дежурный инженер Physics Data Team





СЦЕНАРИЙ 1: ВОССТАНОВЛЕНИЕ МЕТАДАННЫХ POSTGRESQL



Шаг 1. Проверка инфраструктуры (5 мин)



1\. Проверка доступа к S3

&#x20;  aws s3 ls s3://cern-backup-prod/ --region us-west-2



2\. Проверка свободного места

&#x20;  df -h /data/restore/



3\. Проверка PostgreSQL

&#x20;  psql -h new-db.cern.ch -U postgres -c "SELECT version();"



Шаг 2. Восстановление из Full Backup (15 мин)



1\. Скачать бэкап

&#x20;  aws s3 cp s3://cern-backup-prod/postgresql/full/latest.dump.zst /tmp/ --region us-west-2



2\. Распаковать

&#x20;  zstd -d /tmp/latest.dump.zst



3\. Восстановить

&#x20;  pg\_restore -h new-db.cern.ch -U postgres -d metadata /tmp/latest.dump



4\. Проверить

&#x20;  psql -h new-db.cern.ch -U postgres -d metadata -c "\\dt"



Шаг 3. Применение WAL (PITR) - 20 мин



1\. Скачать WAL-файлы

&#x20;  aws s3 cp s3://cern-backup-prod/postgresql/wal/ /tmp/wal/ --recursive --region us-west-2



2\. Настроить recovery.conf

&#x20;  echo "restore\_command = 'cp /tmp/wal/%f %p'" > /var/lib/postgresql/recovery.conf

&#x20;  echo "recovery\_target\_time = '2026-06-16 14:25:00'" >> recovery.conf

&#x20;  echo "recovery\_target\_action = 'promote'" >> recovery.conf



3\. Перезапустить PostgreSQL

&#x20;  systemctl restart postgresql



4\. Проверить

&#x20;  psql -h new-db.cern.ch -U postgres -d metadata -c "SELECT COUNT(\*) FROM data\_files;"



Шаг 4. Проверка консистентности (5 мин)



&#x20;  psql -h new-db.cern.ch -U postgres -d metadata -c "

&#x20;  SELECT DATE(created\_at) as day, COUNT(\*) as file\_count 

&#x20;  FROM data\_files 

&#x20;  WHERE created\_at > '2026-06-01'

&#x20;  GROUP BY DATE(created\_at)

&#x20;  ORDER BY day DESC;"





СЦЕНАРИЙ 2: ВОССТАНОВЛЕНИЕ ROOT-ФАЙЛОВ



Шаг 5. Проверка повреждений на ленте (30 мин)



1\. Проверить статус ленты

&#x20;  mt -f /dev/st0 status



2\. Проверить целостность архива

&#x20;  tar -tvf /mnt/tape\_library/backup\_20260616.tar --warning=no-timestamp | head -50



Шаг 6. Восстановление с Glacier (40 часов)



1\. Запрос на восстановление

&#x20;  aws glacier initiate-job --account-id - --vault-name physics-archive \\

&#x20;  --job-parameters '{"Type":"restore", "Tier":"Bulk"}' --region us-west-2



2\. Получить ID задания

&#x20;  JOB\_ID=$(aws glacier list-jobs --account-id - --vault-name physics-archive \\

&#x20;  --region us-west-2 --query "JobList\[0].JobId" --output text)



3\. Скачать файлы

&#x20;  aws s3 cp s3://glacier-restore/physics\_20260616/ /data/restore/ --recursive --region us-west-2



Шаг 7. Восстановление с реплики ЦОД-2 (24 часа)



&#x20;  ssh tape-library-cod2.cern.ch "tar -cvf /tmp/restore\_20260616.tar /mnt/tape/\*20260616\*"

&#x20;  scp tape-library-cod2.cern.ch:/tmp/restore\_20260616.tar /data/restore/

&#x20;  tar -xvf /data/restore/restore\_20260616.tar -C /data/experiment/



Шаг 8. Reed-Solomon восстановление (2 часа)



&#x20;  python3 /scripts/repair\_reed\_solomon.py --file file.root --parity /data/parity/ --output /data/repaired/





ВРЕМЕННЫЕ МЕТРИКИ



Шаг 1: Проверка инфраструктуры           5 минут

Шаг 2: Восстановление PostgreSQL (Full)  15 минут

Шаг 3: Применение WAL (PITR)             20 минут

Шаг 4: Проверка консистентности          5 минут

Шаг 5: Проверка повреждений на ленте     30 минут

Шаг 6: Восстановление с Glacier          40 часов

Шаг 7: Reed-Solomon восстановление       2 часа

ИТОГО: \~43 часа (Укладываемся в 48 часов RTO)

