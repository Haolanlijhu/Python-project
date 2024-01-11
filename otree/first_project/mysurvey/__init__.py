from otree.api import *


doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'mysurvey'
    players_per_group = None
    num_rounds = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    gender = models.IntegerField(choices=[[1, "Female"], [2, "Male"]], label="Which gender do you identify?")
    age = models.IntegerField(min=18, max=100, label="How old are you?")
    subject = models.StringField(lable="What is your subject of study?")

# PAGESo
class Question(Page):
    form_model = "player"
    form_fields = ["gender", "age", "subject"]

class Results(Page):
    pass


page_sequence = [Question, Results]
