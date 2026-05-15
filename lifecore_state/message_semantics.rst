Message Semantics
=================

Purpose
-------

This document will describe the intended semantics for future
``lifecore_state`` messages. Sprint 17.7 will complete this content before any
message ABI package is created.

Semantic topics
---------------

- what a state message represents;
- how observed state differs from a command;
- how validity and freshness should be expressed;
- how producers and consumers interpret state updates;
- which guarantees belong in message contracts;
- which guarantees belong outside the message ABI.

Current scope
-------------

This is not a ``.msg`` specification and does not create ROS 2 interfaces. It
records the questions and headings needed before Sprint 18 considers message
ABI work.

Review questions
----------------

- Which semantics must be represented directly in messages?
- Which semantics should remain in pure Python core logic?
- Which semantics should be left to ROS 2 integration layers?

ChatGPT ou Codex relira et contrôlera ces livrables avant validation finale du Sprint 17.
