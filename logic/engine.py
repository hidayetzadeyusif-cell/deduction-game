from dataclasses import dataclass
from typing import Literal
from random import shuffle

DAWN_TICK = 1000

@dataclass(frozen=True)
class Decision:
    kind: Literal["peek", "travel"]

    # for travel
    destination: int | None = None # target house's owner ID
    departure: Literal["early", "late"] | None = None
    action: str | None = None

    # for staying
    peek_target: int | None = None # target ID

@dataclass
class Player:
    id: str
    location: str # current house's owner ID
    role: str
    decision: Decision | None = None
    alive: bool = True

@dataclass
class Death:
    id: str # ID of the dead person
    night: int # night of death
    tick: int # tick of death

@dataclass
class GameState:
    players: list[Player]
    deaths: list[Death] = []

    night: 1

def distance(game: GameState, house1: str, house2: str) -> int:
    '''Returns the distance between two houses. Houses are marked by their owner ID.'''
    idx1 = None
    idx2 = None
    for i, p in enumerate(game.players):
        if p.id == house1: idx1 = i
        if p.id == house2: idx2 = i
    
    if idx1 is None or idx2 is None:
        raise ValueError("Given house(s) do not exist.")
    
    idx1, idx2 = min(idx1, idx2), max(idx1, idx2)

    return min(idx2 - idx1, len(game.players) - idx2 + idx1)

def departure_tick(departure: Literal["early", "late"]):
    '''Returns the exact tick of a departure category.'''
    if departure == "early": return 1
    if departure == "late": return 3
    raise ValueError("Invalid departure time.")

def arrival_tick(
        game: GameState, 
        source: int, 
        destination: int, 
        departure: Literal["early", "late"]
    ) -> int:
    '''Returns the arrival tick of a player:

* Leaving from the source house,
* Traveling to the destination house,
* Departing at a given time.

Houses are marked by owner ID.''' 

    return distance(game, source, destination) + departure_tick(departure)


@dataclass(order=True)
class Event:
    tick: int
    resolution_priority: int
    kind: str
    actor: int # actor ID
    target: int # target ID


def get_player(game: GameState, player_id: str) -> Player:
    for player in game.players:
        if player.id == player_id: return player
    raise ValueError("Player does not exist.")

def players_peeking_at(game: GameState, house_id: int) -> list[Player]:
    '''Returns all players peeking at a target house.'''
    return [
        player
        for player in game.players
        if player.alive and player.decision.peek_target == house_id
    ]


def get_valid_peek_targets(game: GameState, player_id: str) -> list[str]:
    return [
        player.id
        for player in game.players
        if distance(game, player.id, player_id) == 1
    ]

def get_valid_destinations(game: GameState, player_id: str) -> list[str]:
    return [
        player.id
        for player in game.players
        if player.id != player_id
    ]

def role_relative_action(role: str):
    if role == "mafia": return "kill"
    return "visit"


def generate_events(game: GameState) -> list[Event]:
    events = []
    for player in game.players:
        player_id = player.id
        decision = player.decision

        if decision.kind == "travel":
            departure_time = departure_tick(decision.departure)
            events.append(
                Event(
                    departure_time, 
                    3,
                    "departure", 
                    player_id, 
                    decision.destination
                )
            )

            arrival_time = arrival_tick(game, player_id, decision.destination, decision.departure)
            events.append(
                Event(
                    arrival_time, 
                    0,
                    "arrival", 
                    player_id, 
                    decision.destination
                )
            )
            events.append(
                Event(
                    arrival_time, 
                    1,
                    role_relative_action(get_player(game, player_id).role), 
                    player_id, 
                    decision.destination
                )
            )
    return sorted(events)

def apply_event(game: GameState, event: Event):
    player = get_player(game, event.actor)
    new_events = []

    if not player.alive:
        return []

    if event.kind == "departure":
        player.location = None

    elif event.kind == "arrival":
        player.location = event.target

    elif event.kind == "kill":
        victim = get_player(game, event.target)

        if victim.location == victim.id:
            new_events.append(Event(
                event.tick,
                2,
                "death",
                event.actor,
                event.target
            ))
        else:
            new_events.append(Event(
                DAWN_TICK,
                2,
                "death",
                event.actor,
                event.target
            ))
    
    elif event.kind == "death":
        victim = get_player(game, event.target)
        victim.alive = False
        game.deaths.append(Death(
            event.target,
            game.night,
            event.tick
        ))
    
    return new_events

@dataclass
class Observation:
    fuzzy_tick: str
    message: str

def get_fuzzy_tick(tick):
    if 1 <= tick <= 3: return "early into the night"
    if 4 <= tick <= 7: return "late into the night"
    if tick == DAWN_TICK: return "at dawn"
    raise ValueError("Impossible tick value.")
     
def observe_event(game: GameState, event: Event) -> dict[str, list[Observation]]:
    observations = {
        player.id: []
        for player in game.players
    }

    fuzzy_tick = get_fuzzy_tick(event.tick)

    if event.kind == 'arrival':
        owner = get_player(game, event.target)

        for player in players_peeking_at(game, owner.id):
            observations[player.id].append(
                Observation(
                    fuzzy_tick,
                    f"someone entered {owner.id}'s home {fuzzy_tick}"
                )
            )

        if owner.location == owner.id:
            observations[event.actor].append(
                Observation(
                    fuzzy_tick,
                    f"{owner.id} was home when {event.actor} arrived {fuzzy_tick}"
                )
            )
            observations[owner.id].append(
                Observation(
                    fuzzy_tick,
                    f"someone entered {owner.id}'s home {fuzzy_tick}"
                )
            )
        else:
            observations[event.actor].append(
                Observation(
                    fuzzy_tick,
                    f"{owner.id} was not home when {event.actor} arrived {fuzzy_tick}"
                )
            )

    if event.kind == 'departure':
        traveller = get_player(game, event.actor)

        for player in players_peeking_at(game, traveller.id):
            observations[player.id].append(
                Observation(
                    fuzzy_tick,
                    f"someone left {traveller.id}'s home {fuzzy_tick}"
                )
            )

    return observations


def simulate_night(game: GameState):
    events = generate_events(game)
    intel = {
        player.id: []
        for player in game.players
    }
    
    while events:
        event = events.pop(0)

        new_events = apply_event(game, event)
        events.extend(new_events)
        events.sort()

        for player, observations in observe_event(game, event).items():
            intel[player] += observations

    return {"events": generate_events(game), "intel": intel}


def assign_roles_randomly(game: GameState, roles: dict[str, int]):
    all_roles = []
    for role, freq in roles.items(): all_roles += [role for _ in range(freq)]

    if len(all_roles) > len(game.players): raise ValueError("Too many roles")
    if len(all_roles) < len(game.players): raise ValueError("Too few roles")
    
    shuffle(all_roles)
    
    for i, player in enumerate(game.players):
        player.role = all_roles[i]
