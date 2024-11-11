from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import MatchRecord

from rest_framework.settings import api_settings

def index(request): # TODO can we remove this? I do not see why it is still here (aguilmea @ qtran)
    return render(request, "./templates/static/pong.html")

""" def room(request, room_name):
    return render(request, "pong/pong.html", {"room_name": room_name}) """


@api_view(['POST'])
def delete_user_stats(request):
	try:
		delete_claim  = request.auth.get('delete')
		if not delete_claim or delete_claim != True:
			return Response({'error': 'No delete parameter'}, status=status.HTTP_403_FORBIDDEN)
		# userid = request.auth.get('user_id')
		userid = request.user.user_id
		matchs = MatchRecord.objects.filter(winner=userid)
		for match in matchs:
			if match.winner == userid:
				match.winner = None
				match.save()
			if match.winner is None and match.loser is None:
				match.delete()
		matchs = MatchRecord.objects.filter(loser=userid)
		for match in matchs:
			if match.loser == userid:
				match.loser = None
				match.save()
			if match.winner is None and match.loser is None:
				match.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)
	except Exception as e:
		return Response({'delete_user_stats error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)