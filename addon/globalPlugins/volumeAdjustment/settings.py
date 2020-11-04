#settings.py
# Add-on settings panel
# A part of NonVisual Desktop Access (NVDA)
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2020 Olexandr Gryshchenko <grisov.nvaccess@mailnull.com>

import addonHandler
from logHandler import log
try:
	addonHandler.initTranslation()
except addonHandler.AddonError:
	log.warning("Unable to initialise translations. This may be because the addon is running from NVDA scratchpad.")

import wx
from gui import SettingsPanel, guiHelper, nvdaControls
import config
from threading import Thread
from . import addonName, addonSummary
from .core import devices, hidden, AudioUtilities


class VASettingsPanel(SettingsPanel):
	"""Add-on settings panel object"""
	title = addonSummary

	def __init__(self, parent):
		"""Initializing the add-on settings panel object"""
		super(VASettingsPanel, self).__init__(parent)

	def makeSettings(self, sizer: wx._core.BoxSizer):
		"""Populate the panel with settings controls.
		@param sizer: The sizer to which to add the settings controls.
		@type sizer: wx._core.BoxSizer
		"""
		sHelper = guiHelper.BoxSizerHelper(self, sizer=sizer)
		# Translators: The label of the component in the settings panel
		self.hideDevices = sHelper.addLabeledControl(_("Hide audio &devices:"), nvdaControls.CustomCheckListBox, choices=[])
		self.devs = dict(hidden.devices)
		self.devs.update({devices[i].id: devices[i].name for i in range(len(devices))})
		for id,name in self.devs.items():
			self.hideDevices.Append(name, id)
		if len(self.devs)>0:
			self.hideDevices.SetCheckedStrings([self.devs[id] for id in hidden.devices])
			self.hideDevices.SetSelection(0)

		devButtons = wx.BoxSizer(wx.HORIZONTAL)
		# Translators: The label of the button in the settings panel
		self.updateDevicesButton = wx.Button(self, label=_("&Update"))
		self.updateDevicesButton.Bind(wx.EVT_BUTTON, self.onUpdateDevicesButton)
		devButtons.Add(self.updateDevicesButton)
		# Translators: The label of the button in the settings panel
		self.clearDevicesButton = wx.Button(self, label=_("&Clear"))
		self.clearDevicesButton.Bind(wx.EVT_BUTTON, self.onClearDevicesButton)
		devButtons.Add(self.clearDevicesButton)
		sizer.Add(devButtons, flag=wx.RIGHT)

		self.procs = [s.Process.name() for s in AudioUtilities.GetAllSessions() if s.Process and s.Process.name()]
		self.procs.extend([proc for proc in hidden.processes if proc not in self.procs])
		# Translators: The label of the component in the settings panel
		self.hideProcesses = sHelper.addLabeledControl(_("Hide &processes:"), nvdaControls.CustomCheckListBox, choices=self.procs)
		if len(self.procs)>0:
			self.hideProcesses.SetCheckedStrings(hidden.processes)
			self.hideProcesses.SetSelection(0)

		procButtons = wx.BoxSizer(wx.HORIZONTAL)
		# Translators: The label of the button in the settings panel
		self.updateProcessesButton = wx.Button(self, label=_("&Update"))
		self.updateProcessesButton.Bind(wx.EVT_BUTTON, self.onUpdateProcessesButton)
		procButtons.Add(self.updateProcessesButton)
		# Translators: The label of the button in the settings panel
		self.clearProcessesButton = wx.Button(self, label=_("&Clear"))
		self.clearProcessesButton.Bind(wx.EVT_BUTTON, self.onClearProcessesButton)
		procButtons.Add(self.clearProcessesButton)
		sizer.Add(procButtons, flag=wx.RIGHT)

		# Translators: The label of the component in the settings panel
		self.volumeStep = sHelper.addLabeledControl(_("&Step to change the volume level:"), nvdaControls.SelectOnFocusSpinCtrl,
			value=str(config.conf[addonName]['step']), min=1, max=20)

	def onUpdateDevicesButton(self, event) -> None:
		"""Update the list of connected audio devices when the appropriate button is pressed.
		@param event: event that occurs when a wx.Button is pressed
		@type event: wx.core.PyEventBinder
		"""
		devices.initialize()
		self.hideDevices.Clear()
		self.devs = dict(hidden.devices)
		self.devs.update({devices[i].id: devices[i].name for i in range(len(devices))})
		for id,name in self.devs.items():
			self.hideDevices.Append(name, id)
		if len(self.devs)>0:
			self.hideDevices.SetCheckedStrings([self.devs[id] for id in hidden.devices])
			self.hideDevices.SetSelection(0)
		self.hideDevices.SetFocus()

	def onClearDevicesButton(self, event) -> None:
		"""Uncheck all installed checkboxes and remove unnecessary audio devices.
		@param event: event that occurs when a wx.Button is pressed
		@type event: wx.core.PyEventBinder
		"""
		self.hideDevices.Clear()
		for dev in devices:
			self.hideDevices.Append(dev.name, dev.id)
		if len(devices)>0:
			self.hideDevices.SetSelection(0)
		self.hideDevices.SetFocus()

	def onUpdateProcessesButton(self, event) -> None:
		"""Update the list of currently running processes when the appropriate button is pressed.
		@param event: event that occurs when a wx.Button is pressed
		@type event: wx.core.PyEventBinder
		"""
		self.procs = [s.Process.name() for s in AudioUtilities.GetAllSessions() if s.Process and s.Process.name()]
		self.procs.extend([proc for proc in hidden.processes if proc not in self.procs])
		self.hideProcesses.Clear()
		self.hideProcesses.SetItems(self.procs)
		if len(self.procs)>0:
			self.hideProcesses.SetCheckedStrings(hidden.processes)
			self.hideProcesses.SetSelection(0)
		self.hideProcesses.SetFocus()

	def onClearProcessesButton(self, event) -> None:
		"""Uncheck all installed checkboxes and remove unnecessary processes.
		@param event: event that occurs when a wx.Button is pressed
		@type event: wx.core.PyEventBinder
		"""
		self.procs = [s.Process.name() for s in AudioUtilities.GetAllSessions() if s.Process and s.Process.name()]
		self.hideProcesses.Clear()
		self.hideProcesses.SetItems(self.procs)
		if len(self.procs)>0:
			self.hideProcesses.SetSelection(0)
		self.hideProcesses.SetFocus()

	def postInit(self) -> None:
		"""Set system focus to the first component in the settings panel."""
		self.hideDevices.SetFocus()

	def onSave(self) -> None:
		"""Update Configuration when clicking OK."""
		config.conf[addonName]['step'] = self.volumeStep.GetValue()
		devs = {}
		for checked in self.hideDevices.GetCheckedItems():
			id = self.hideDevices.GetClientData(checked)
			devs[id] = self.devs[id]
		hidden.devices = devs
		hidden.processes = self.hideProcesses.GetCheckedStrings()
		hidden.save()
		# Re-initialize the list of devices for the new settings to take effect
		Thread(target=devices.initialize, args=[hidden.devices]).start()