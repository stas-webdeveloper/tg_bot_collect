## Запуск на сервере

- Скопируй папку telegram-bot на сервер.
- Перейди в неё и выполни:

```bash
docker build -t aiobot .
docker run -d --name aiobot --restart always aiobot
```

### Проверить статус:

```bash
docker logs -f aiobot
```

**Если всё ок, увидишь**:

🤖 Bot is running...

Теперь можешь писать своему боту в Telegram — и заявки будут сохраняться в data/clients.db.
