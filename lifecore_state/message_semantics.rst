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

Current semantic direction
--------------------------

The current architecture direction distinguishes semantic units from transport
events.

``StateSample``
	A sample is the semantic unit of observed value. It answers what value was
	observed for a descriptor, at what time, and with what quality.

``StateUpdate``
	An update is a synchronization event for a known scope. It may carry one or
	more samples, partial mutations, invalidation information, or another
	accepted update form.

``StateCommand``
	A command is requested intent, not observed truth. Command outcomes must be
	represented separately from the command itself.

``StateOwner``
	Ownership is semantic. The authoritative owner of a descriptor must not be
	inferred only from the ROS node currently relaying a message.

``StateRegistry``
	A registry is primarily a scoped catalog of known contracts. It must not be
	treated as a default global mutable store or blackboard runtime.

Message ABI guard rails
-----------------------

- message contracts must preserve the distinction between sample, update,
	snapshot, delta, and command semantics;
- descriptor identity should remain deterministic inside a registry scope;
- stable semantic paths are preferred over generated UUIDs when descriptors
	originate from structured registries or external specifications;
- quality describes reliability of a value, not business state and not
	lifecycle state;
- runtime policy must not be hidden inside ABI fields when it belongs in pure
	semantics or ROS integration layers.

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
- Does Sprint 18 need explicit transport concepts for store or mirror, or is
	the registry distinction sufficient at ABI review time?

ChatGPT ou Codex relira et contrôlera ces livrables avant validation finale du Sprint 17.
