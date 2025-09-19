from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .services.chatbot_engine import get_response


@csrf_exempt
def chatbot_api(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("message", "")
        response = get_response(user_message)
        return JsonResponse({"response": response})
    return JsonResponse({"error": "POST request required"}, status=400)
