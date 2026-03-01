# security/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils.RoleLSTM import RolePredictor

class AdaptRoleView(APIView):
    def post(self, request):
        # Expect JSON: {"context": [0.5, 2.0, 1.0, 0.0, 0.3]}  # your 5 features
        context = request.data.get('context')
        if not context or len(context) != 5:
            return Response({"error": "Invalid context vector"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            new_role = RolePredictor.predict(context)
            return Response({"recommended_role": new_role}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)