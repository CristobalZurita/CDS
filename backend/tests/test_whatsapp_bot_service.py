from app.services.whatsapp_bot_service import WhatsAppBotService


def test_whatsapp_bot_service_matches_price_question():
    service = WhatsAppBotService()

    reply = service.build_reply("Hola, cuanto sale la reparacion?")

    assert reply.intent == "cotizacion"
    assert "depende del modelo" in reply.text.lower()
    assert "agendar revision" in reply.text.lower()


def test_whatsapp_bot_service_handoff_keyword_uses_configured_url():
    service = WhatsAppBotService()

    reply = service.build_reply("Quiero hablar con humano")

    assert reply.intent == "handoff"
    assert reply.handoff is True
    assert "https://wa.me/56982957538" in reply.text


def test_whatsapp_bot_service_triage_does_not_request_unhandled_attachments():
    service = WhatsAppBotService()

    reply = service.build_reply("Mi Korg no enciende")

    assert reply.intent == "triage"
    assert "foto" not in reply.text.lower()
    assert "video" not in reply.text.lower()


def test_whatsapp_bot_service_brand_plus_price_prefers_price_intent():
    service = WhatsAppBotService()

    reply = service.build_reply("Korg M1, cuanto sale la reparacion?")

    assert reply.intent == "cotizacion"
    assert "agendar revision" in reply.text.lower()


def test_whatsapp_bot_service_collect_details_advance_to_schedule():
    service = WhatsAppBotService()

    reply = service.build_reply("Korg, M1, no suenan unas teclas, no fue abierto.")

    assert reply.intent == "agenda"
    assert "agendar revision" in reply.text.lower()
