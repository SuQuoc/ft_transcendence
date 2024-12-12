from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
import logging

import requests
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
	

@api_view(['GET'])
def get_game_stats(request):
    try:
        user_id = request.query_params.get("profile_id", None)
        if user_id is None:
            user_id = request.user.user_id
			
        last_matches = MatchRecord.objects.filter(
		    Q(winner=user_id) | Q(loser=user_id)
                ).order_by('-timestamp')[:10]
        if not last_matches:
            return Response('No matches found', status=status.HTTP_204_NO_CONTENT)
        
        wins = MatchRecord.objects.filter(winner=user_id).count()
        losses = MatchRecord.objects.filter(loser=user_id).count()
        total_matches = wins + losses

        last_matches_data = list(last_matches.values('winner', 
													 'loser', 
													 'winner_score', 
													 'loser_score', 
													 'timestamp'))
        
        ids = set()
        for match in last_matches_data:
            ids.add(str(match['winner']))
            ids.add(str(match['loser']))
        
        
        displaynames = get_displaynames(request, ids)
        logging.warning("displaynames: " + str(displaynames))
        for match in last_matches_data:
            match["winner"] = str(displaynames.get(str(match['winner']), "[Unknown]"))
            match["loser"] = str(displaynames.get(str(match['loser']), "[Unknown]"))
        
        statistics = {
            'total_matches': total_matches,
            'wins': wins,
            'losses': losses,
            'last_matches': last_matches_data,
        }
        
        return Response(statistics, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'get_game_stats error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_displaynames(request, ids):
	request_uri = 'http://usermanagement:8000/um/get_displaynames'
	headers = {'Content-Type': 'application/json',}
	cookies = request.COOKIES
	data = {'user_ids': list(ids)}
	response = requests.post(request_uri, json=data, headers=headers, cookies=cookies)
	if response.status_code != status.HTTP_200_OK:
		raise Exception('Error getting displaynames from UM service')
	return (response.json())