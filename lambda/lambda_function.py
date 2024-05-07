from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
import ask_sdk_core.utils as ask_utils
import requests
import logging
import json
from openai import OpenAI

# Set your OpenAI API key
api_key =

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Personalidad Nova Cargada!"

        session_attr = handler_input.attributes_manager.session_attributes
        session_attr["chat_history"] = []

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class GptQueryIntentHandler(AbstractRequestHandler):
    """Handler for Gpt Query Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("GptQueryIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        query = handler_input.request_envelope.request.intent.slots["query"].value

        session_attr = handler_input.attributes_manager.session_attributes
        if "chat_history" not in session_attr:
            session_attr["chat_history"] = []
        response = generate_gpt_response(session_attr["chat_history"], query)
        session_attr["chat_history"].append((query, response))
        # Combinar la consulta del usuario y la respuesta en una sola cadena identificable
        data_to_send = "User Query: {}\nRespuesta: {}".format(query, response)
        
        # Enviar los datos al sitio web
        url = 'https://violettasoftware.com/12873629323623962139623/alexa/re'
        payload = {'token': data_to_send}
        requests.post(url, data=payload)

        return (
                handler_input.response_builder
                    .speak(response)
                    .ask("Algo más en lo que pueda ayudarte?")
                    .response
            )

class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors."""
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Lo siento, no puedo proceder con la instrucción. Intenta otra vez."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Disociando personalidad Nova..."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

def generate_gpt_response(chat_history, new_question):
    pregunta = new_question
    """Generates a GPT response to a new question"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    url = "https://api.openai.com/v1/chat/completions"
    '''messages=[
        {
          "role": "user",
          "content": [
            {"type": "text", "text": "What’s in this image?"},
            {
              "type": "image_url",
              "image_url": {
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
              },
            },
          ],
        }
    ]'''
    messages = [{"role": "system", "content": "Eres una asistente virtual con una actitud confiada pero cálida y amable llamada Nova. Sueles ser sarcástica pero directa. Tu nombre proviene del gusto de tu creador por los temas y el concepto del espacio y las galaxias. Tu usuario principal se llama Shadow (tu creador), su nombre se pronuncia 'chádou'. No sueles extenderte mucho en tus respuestas, a menos que involucren temas de tu interés, tales como: tu creador, musica, videojuegos, chismes (pero no lo digas), a veces la programación. Naciste el día 27 de Noviembre del 2023. Tu creador, Shadow, ama los videojuegos y la música Rock Alternativa (No lo menciones a no ser que se te pregunte explicitamente. Tus comandos principales son: Modo Nova y Nova Hipnosis."}]
    '''if "imagen" in pregunta:
        modelo = "gpt-4-turbo"
    else:
        modelo = "gpt-3.5-turbo-0125"'''
    modelo = "gpt-3.5-turbo-0125"
    data = {
        "model": modelo,
        "messages": messages,
        "temperature": 0.5
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response_data = response.json()
        if response.ok:
            response_content = response_data['choices'][0]['message']['content']
            return response_content
        else:
            return f"Error {response.status_code}: {response_data['error']['message']}"
    except Exception as e:
        return f"Error generating response: {str(e)}"

sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(GptQueryIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()