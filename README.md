## PHILOSOPHY OF DESIGN

* Information must be asymmetrical.

* Rules must be intuitively understandable.

* The simulation physics must be clean and deterministic. Ambiguity must lie in the observation of said physics.

---

## SETUP

Every player owns a house arranged in a circle.

The game begins with a night.

---

## NIGHT

Each player chooses ONE:

* Travel to another house
* Stay home

Activities are selected once at the beginning of the night, and CANNOT be changed later.

---

## TRAVELLING

Players who choose to travel pick to depart:

* Early
* or Late

Distance matters.

The farther the destination, the longer it takes to reach there.

Arrival time is deterministic - the same combination of departure time and distance is guaranteed to give the same arrival time.

---

## STAYING HOME

Players who stay home gain information via peeking.

A player staying home may choose ONE neighboring house to watch (i.e., peek at).

Players can then know:

* if anyone enters the neighbor house
* if anyone leaves the neighbor house
* relative ordering of these events, if far enough apart

Peeking does NOT reveal:

* actions,
* exact arrival timing,
* identity,
* role.

---

## PRESENCE

A player inside of their own home knows:

* when another person enters their house,

though no exact timestamps are given.

A visitor in another player's house knows:

* whether the owner was home upon arrival.

Identities are not revealed in both cases.

---

## ACTIONS

Roles grant actions.

Actions automatically attempt to resolve upon arrival.

An action succeeds if:

* the target is still present when the visitor arrives.

Otherwise:

* the action gets deferred, and remains pending till dawn.

More specifically, events are resolved in the following order:

1. arrivals
2. arrival-triggered actions
3. effects of actions
4. departure

---

## DAWN

After night and before day, all players automatically return to their houses.

Pending actions CANNOT be resolved at night, if already failed once.

They can only be carried over to dawn, where they are resolved before day begins.

---

## DAY

Reveal:

* only deaths,

not:

* movement,
* action history,
* etc.

Then discussion begins.

Voting eliminates one player.
Ties fail.

Only roles are revealed upon elimination.

---

## BRIEF HISTORY

* **The Immortal Traveler glitch**. Implicit intent used to mean that travelling automatically nullified all actions. This was solved with the **Dawn Compromise**.

* **The Quadratic Unfairness problem**. After intent was separated from destination, the mafias encountered a frustrating balance issue: it was too difficult and random to kill anyone, because state space had effectively been squared. This was also solved with the **Dawn Compromise**.

* **The Dawn Compromise**. Following discovery of many errors, the core of the game had to be compromised. The dawn phase was added to resolve pending actions, and night mostly became reserved for information flow.

* **The David-Flora Resolution order**. Testing unearthed an ordering problem where multiple events happened simultaneously. Named after two of the testing characters, David, the mafia, and Flora, the target. This issue was handled using a tick-based interaction system.
