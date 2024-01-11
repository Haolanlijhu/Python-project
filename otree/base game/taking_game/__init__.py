from otree.api import *

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'taking_game'
    players_per_group = None
    num_rounds = 1

    # You may need to change it to other role names used in the paper
    dictator_role = 'Dictator'
    recipient_role = 'Recipient'

    # The amount given to the dictator. Change it whatever amount specified in your chosen paper.
    endowment = cu(7)
    show_up_fee = cu(4)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    take_amount = models.CurrencyField(choices=currency_range(cu(-2.00), cu(7.00), cu(0.50)),
                                       label='How much would like to give to or '
                                             'take from your matched partner?')


def take_payoffs(group: Group):
    dictator = group.get_player_by_role(Constants.dictator_role)
    recipient = group.get_player_by_role(Constants.recipient_role)
    dictator.payoff = Constants.show_up_fee + Constants.endowment - group.take_amount
    recipient.payoff = Constants.show_up_fee + group.take_amount


class Player(BasePlayer):
    pass


# PAGES
class RoleAssignment2(Page):
    pass


class TakingDictator(Page):
    form_model = 'group'
    form_fields = ['take_amount']

    @staticmethod
    def is_displayed(player: Player):
        return player.role == Constants.dictator_role


class ResultsWaitPage2(WaitPage):
    after_all_players_arrive = take_payoffs


class Results2(Page):
    pass


page_sequence = [RoleAssignment2,
                 TakingDictator,
                 ResultsWaitPage2,
                 Results2]
