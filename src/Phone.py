#!/usr/bin/python
# -*- coding: UTF-8 -*-
import CallScreener
import Modem
import CallLogger
import Indicators

class Phone(object):
	def incoming_call(self, aCid):
		pass

	def __init__(self):
		self._call_screener = None
		# @AssociationType CallScreener
		# @AssociationMultiplicity 1
		# @AssociationKind Composition
		self._modem = None
		# @AssociationType Modem
		# @AssociationMultiplicity 1
		# @AssociationKind Composition
		self._call_logger = None
		# @AssociationType CallLogger
		# @AssociationMultiplicity 1
		# @AssociationKind Composition
		self._leds = None
		# @AssociationType Indicators
		# @AssociationMultiplicity 1
		# @AssociationKind Composition

