# from services.dialog_service import DialogService
# from models.intents.intents import Intent
#
#
# def test_process_answer_pain():
#     service = DialogService()
#
#     reply, intent = service.process_answer("У меня сильная боль")
#
#     assert intent == Intent.CLARIFY_PAIN
#     assert "боль" in reply.lower()
#
#
# def test_process_answer_temperature():
#     service = DialogService()
#
#     reply, intent = service.process_answer("Температура 38")
#
#     assert intent == Intent.ASK_TEMPERATURE
#
#
# def test_process_answer_unknown():
#     service = DialogService()
#
#     reply, intent = service.process_answer("абракадабра")
#
#     assert intent is None
