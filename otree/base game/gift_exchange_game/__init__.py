from otree.api import *

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'gift_exchange_game'
    players_per_group = None
    num_rounds = 1

    # Change the name of the role here:
    principle_role = 'Principle'
    agent_role = 'Agent'

    # Change the effort and cost level here. The current effort_levels = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    # The current cost_levels = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45], change the cost levels according to your paper.
    effort_levels = [i/10 for i in range(10)]
    cost_levels = [cu(5 * i) for i in range(10)]


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    # The wage to be set by the principle
    wage = models.CurrencyField(label='Choose the wage for the agent:', min=0, max=100)

    # The effort level chosen by the agent
    effort = models.FloatField(label='Choose the effort level for the principle', min=0, max=1)

    cost = models.CurrencyField()


# validate the values entered for effort
def effort_error_message(player, value):
    if value not in Constants.effort_levels:
        return 'Please enter a number between 0 and 1. E.g., 0.1.'


def set_cost(group: Group):
    cost = [cost for effort, cost in zip(Constants.effort_levels, Constants.cost_levels) if effort == group.effort][0]
    print('The effort level chosen by the agent is', group.effort, 'The corresponding cost level is ', cost)

    # set the group cost to the cost corresponding to the effort level.
    group.cost = cost


def set_payoff(group: Group):
    principle = group.get_player_by_role(Constants.principle_role)
    agent = group.get_player_by_role(Constants.agent_role)

    # change the payoff calculation of the principle ana agent here
    principle.payoff = (cu(120) - group.wage) * group.effort
    agent.payoff = group.wage - group.cost


class Player(BasePlayer):
    pass


# PAGES
class Instructions(Page):
    pass


class RoleAssignment(Page):
    pass


class Principle(Page):
    form_model = 'group'
    form_fields = ['wage']

    @staticmethod
    def is_displayed(player: Player):
        return player.role == Constants.principle_role


class Agent(Page):
    form_model = 'group'
    form_fields = ['effort']

    @staticmethod
    def is_displayed(player: Player):
        return player.role == Constants.agent_role


class WaitForPrinciple(WaitPage):
    pass


class ResultsWaitPage(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        set_cost(group)
        set_payoff(group)


class Results(Page):
    pass


page_sequence = [
    Instructions,
    RoleAssignment,
    Principle,
    WaitForPrinciple,
    Agent,
    ResultsWaitPage,
    Results
]
