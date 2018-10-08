#!/usr/bin/python
# -*- coding: UTF-8 -*-
import Blacklist
import Whitelist
import NomoroboService

class CallScreener(object):
	def is_whitelisted(self):
		"""@ReturnType boolean"""
		pass

	def is_blacklisted(self):
		"""@ReturnType boolean"""
		pass

	def __init__(self):
		self._blacklist = None
		# @AssociationType Blacklist
		# @AssociationMultiplicity 1
		# @AssociationKind Composition
		self._whtielist = None
		# @AssociationType Whitelist
		# @AssociationMultiplicity 1
		# @AssociationKind Composition
		self._nomorobo = None
		# @AssociationType NomoroboService
		# @AssociationMultiplicity 1
		# @AssociationKind Composition

