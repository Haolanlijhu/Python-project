from otree.api import *

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'take_game'
    players_per_group = None
    num_rounds = 1
    dictator_role = 'Dictator'
    recipient_role = 'Recipient'
    endowment = cu(7)
    show_up_fee = cu(4)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    send_amount = models.CurrencyField(choices=currency_range(cu(0), cu(7), cu(0.5)), lable="How much would you like "
                                                                                            "to give to or take from"
                                                                                            " your matched partner?")


def set_payoffs(group: Group):
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


class WaitForDictator(Page):
    after_all_players_arrive = set_payoffs


class Results(Page):
    pass


page_sequence = [
    Instructions,
    RoleAssignment,
    Dictator,
    WaitForDictator,
    Results
]
