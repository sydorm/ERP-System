---
description: Як оновити код та сервер (Git + Vultr)
---

Цей воркфлоу описує кроки для безпечного оновлення системи.

1. **Відправка змін у GitHub**
   // turbo
   $ git add .
   $ git commit -m "Опис змін"
   $ git push origin main

2. **Оновлення сервера Vultr**
   - Зайдіть у термінал Vultr.
   - Виконайте скрипт оновлення:
     $ ./scripts/update.sh
   - Якщо скрипт не має прав на запуск, виконайте:
     $ chmod +x scripts/update.sh

3. **Перевірка після оновлення**
   - Переконайтеся, що контейнери запущені:
     $ docker-compose ps
   - Перевірте логи бекенду у разі помилок:
     $ docker-compose logs backend
