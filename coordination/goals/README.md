# goals/

Integrator-owned, time-boxed autonomous mission briefs. The user activates one by naming
it ("pursue the goal in coordination/goals/<file>"). A goal file is self-contained: it
restates the liveness and stop rules inline, lists explicit may / may-not authority, gives
a bounded fallback ladder, and states its end condition. The window starts when the
receiving agent accepts, not when the file was committed. Goal files never authorize
Arena writes.
