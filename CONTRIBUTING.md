## Вклад и запуск тестов

Спасибо за интерес к проекту! Короткие инструкции для разработчиков.

- Создайте виртуальное окружение (рекомендуется):

```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
```

- Установите зависимости:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

- Примечания по `pygame`:
  - Рекомендуется устанавливать `pygame` в системе через `pip install pygame`.
  - На Linux для headless-прогона тестов используйте `xvfb` (см. CI):

```bash
sudo apt-get install xvfb
xvfb-run -s "-screen 0 1280x720x24" pytest -q
```

- Запуск тестов локально:

```bash
# Обычный режим
pytest -q

# Headless (Linux)
SDL_VIDEODRIVER=dummy xvfb-run -s "-screen 0 1280x720x24" pytest -q
```

- Если у вас нет возможности установить `pygame`, тестовый набор содержит защитный мок в `tests/conftest.py`, который позволяет частичный запуск тестов, но для полного покрытия и интеграционных тестов требуется реальная библиотека `pygame`.

- CI: в проект добавлен GitHub Actions workflow `.github/workflows/ci.yml`, который устанавливает зависимости и запускает тесты в headless окружении.

Если хотите, могу:
- помочь установить `pygame` и прогнать тесты локально;
- добавить инструкции по отладке (VS Code launch/pytest config);
- добавить `pre-commit` и настройки форматирования.
