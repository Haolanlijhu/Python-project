from otree.api import *

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'dictator_game'
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
    # The amount dictator send to the recipient
    send_amount = models.CurrencyField(choices=currency_range(cu(0.00), cu(7.00), cu(0.50)),
                                       label='How much would like to give to your '
                                             'matched partner?')
    take_amount = models.CurrencyField(choices=currency_range(cu(-2.00), cu(7.00), cu(0.50)),
                                       label='How much would like to give to or '
                                             'take from your matched partner?')


def set_payoffs(group: Group):
    # calculate the payoffs for the dictator and recipient in the game. Modify here for different payoff calculations.
    dictator = group.get_player_by_role(Constants.dictator_role)
    recipient = group.get_player_by_role(Constants.recipient_role)
    dictator.payoff = Constants.show_up_fee + Constants.endowment - group.send_amount
    recipient.payoff = Constants.show_up_fee + group.send_amount


class Player(BasePlayer):
    pass


# PAGES
class Instructions(Page):
    pass


class RoleAssignment(Page):
    pass


class Dictator(Page):
    form_model = 'group'
    form_fields = ['send_amount']

    @staticmethod
    def is_displayed(player: Player):
        return player.role == Constants.dictator_role


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs


class Results(Page):
    pass


page_sequence = [
    Instructions,
    RoleAssignment,
    Dictator,
    ResultsWaitPage,
    Results,
]
