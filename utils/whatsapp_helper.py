"""Helper para gerar links de cobrança direta via WhatsApp Web."""

import urllib.parse
import webbrowser
from datetime import date


def clean_phone(phone: str) -> str:
    """Remove caracteres não numéricos do telefone e garante DDI 55."""
    if not phone:
        return ""
    digits = "".join(filter(str.isdigit, phone))
    if not digits:
        return ""
    if not digits.startswith("55") and len(digits) in (10, 11):
        digits = "55" + digits
    return digits


def generate_whatsapp_link(phone: str, message: str) -> str:
    """Gera link wa.me codificado."""
    phone_clean = clean_phone(phone)
    if not phone_clean:
        return ""
    encoded_msg = urllib.parse.quote(message)
    return f"https://wa.me/{phone_clean}?text={encoded_msg}"


def open_whatsapp_cobranca(phone: str, cliente_nome: str, valor: float, 
                           data_vencimento: date, tipo: str = "ATRASO") -> bool:
    """Abre o WhatsApp Web com mensagem pré-formatada."""
    venc_str = data_vencimento.strftime("%d/%m/%Y")
    valor_str = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    if tipo == "LEMBRETE":
        msg = (
            f"Olá *{cliente_nome}*, tudo bem?\n\n"
            f"📌 Passando para lembrar que a sua parcela no valor de *{valor_str}* "
            f"vence em *{venc_str}*.\n\n"
            f"Caso precise de ajuda ou queira antecipar, estamos à disposição!"
        )
    elif tipo == "HOJE":
        msg = (
            f"Olá *{cliente_nome}*, bom dia!\n\n"
            f"⏰ Lembrando que a sua parcela no valor de *{valor_str}* "
            f"vence *hoje ({venc_str})*.\n\n"
            f"Qualquer dúvida sobre o pagamento ou chave PIX, nos avise aqui!"
        )
    else:  # ATRASO
        msg = (
            f"Olá *{cliente_nome}*!\n\n"
            f"⚠️ Constamos em nosso sistema que a parcela no valor de *{valor_str}* "
            f"(vencimento *{venc_str}*) está pendente.\n\n"
            f"Entre em contato conosco o quanto antes para regularizar a situação ou renovar os juros. Obrigado!"
        )

    link = generate_whatsapp_link(phone, msg)
    if link:
        webbrowser.open(link)
        return True
    return False
