from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .services.chatbot_engine import get_response


@csrf_exempt
def chatbot_api(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("message", "")
        lat = data.get("lat")
        lng = data.get("lng")
        user_id = str(request.session.session_key or "default")
        response = get_response(user_message, user_id, lat, lng)
        return JsonResponse({"response_data": response})
    return JsonResponse({"error": "POST request required"}, status=400)
