from django.db import models

""" class Person(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

    def __str__(self):
        return self.last_name
"""


class MatchRecord(models.Model):
    winner = models.UUIDField()
    loser = models.UUIDField()
    winner_score = models.IntegerField()
    loser_score = models.IntegerField()

    def __str__(self):
        return f"winner: {self.winner} - loser: {self.loser}"

