from rest_framework.views import APIView
from rest_framework.response import Response

class Api(APIView):

    def post(self, request):
        challenge = request.data.get('challenge')
        req_data = request.data
        # text = request.data.get('event').get('text')
        # if text is not None:
        #     if "점심" in text:
        #         print("sdf")
        #     user = request.data.get('event').get('user')
        #
        #     if user == 'U027QMQD0R0':
        #         print("봇")
        #     else:
        #         print("user ===>",user)

        return Response(status=200, data=dict(challenge=challenge))
