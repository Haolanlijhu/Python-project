from otree.api import *

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'trust_game'
    players_per_group = 2
    num_rounds = 1

    # Change the name of the roles here:
    trustee_role = 'Trustee'
    trustor_role = 'Trustor'

    # Change the endowment of the game here
    endowment = cu(10)

    # Change the multiplier here
    multiplier = 3


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    # The trustor send amount
    send_amount = models.CurrencyField(min=cu(0), max=Constants.endowment, label='How much would you send to your '
                                                                                 'matched partner?')

    # The trustee return amount
    return_amount = models.CurrencyField(min=cu(0), label='How much would you like to send back to your matched '
                                                          'partner?')


# Dynamically decide on the maximum amount can be returned by the trustor
def return_amount_max(player):
    return player.send_amount * Constants.multiplier


# Change the calculation of the payoffs for the trustor and trustee here
def set_payoff(group: Group):
    trustor = group.get_player_by_role(Constants.trustor_role)
    trustee = group.get_player_by_role(Constants.trustee_role)
    trustor.payoff = Constants.endowment - group.send_amount + group.return_amount
    trustee.payoff = Constants.multiplier * group.send_amount - group.return_amount


class Player(BasePlayer):
    pass


# PAGES
class Instructions(Page):
    pass


class RoleAssignment(Page):
    pass


class Send(Page):
    form_model = 'group'
    form_fields = ['send_amount']

    @staticmethod
    def is_displayed(player: Player):
        return player.role == Constants.trustor_role


class WaitForTrustor(WaitPage):
    pass


class Sendback(Page):
    form_model = 'group'
    form_fields = ['return_amount']

    @staticmethod
    def is_displayed(player: Player):
        return player.role == Constants.trustee_role

    # Modify the displayed multiplied amount here:
    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        return dict(
            multiplied_amount=Constants.multiplier * group.send_amount
        )


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoff


class Results(Page):
    pass


page_sequence = [
    Instructions,
    RoleAssignment,
    Send,
    WaitForTrustor,
    Sendback,
    ResultsWaitPage,
    Results
]
