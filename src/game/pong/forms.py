from django import forms
from django.core.validators import RegexValidator
from django import forms

class CreateTournamentForm(forms.Form):
    room_name = forms.CharField(
        min_length=1, 
        max_length=30, 
        validators=[
            RegexValidator(
                r"^[a-zA-Z0-9_-]+$", 
                message="Room name can only contain letters, numbers, underscores, or hyphens."
            )
        ]
        # NOTE: before validation, the raw data stored in the form is cleaned
        # by the form, which in case of 
        # CharFields, strips leading and trailing whitespaces
        # the clean() method can be overridden to add custom cleaning
    )

    points_to_win = forms.IntegerField(
        min_value=1,
        max_value=25
    )
    
    max_player_num = forms.ChoiceField(
        choices=[
            (4, "4"),
            (8, "8"),
            (16, "16"),
        ]
    )
    

