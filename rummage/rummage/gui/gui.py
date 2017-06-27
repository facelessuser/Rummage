# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Jun 22 2017)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.adv
import wx.xrc
from .autocomplete_combo import AutoCompleteCombo
from .date_picker import DatePicker
from wx.lib.masked import TimeCtrl
from .result_lists import ResultFileList
from .result_lists import ResultContentList
from .load_search_list import SavedSearchList
from .search_error_list import ErrorList

wx.ID_EXit = 1000

###########################################################################
## Class RummageFrame
###########################################################################

class RummageFrame ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Rummage", pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.DEFAULT_FRAME_STYLE|wx.RESIZE_BORDER|wx.TAB_TRAVERSAL )
		
		self.SetSizeHints( wx.Size( -1,-1 ), wx.DefaultSize )
		self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )
		
		bFrameSizer = wx.BoxSizer( wx.VERTICAL )
		
		self.m_main_panel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		fgSizer13 = wx.FlexGridSizer( 2, 1, 0, 0 )
		fgSizer13.AddGrowableCol( 0 )
		fgSizer13.AddGrowableRow( 0 )
		fgSizer13.SetFlexibleDirection( wx.BOTH )
		fgSizer13.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_grep_notebook = wx.Notebook( self.m_main_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.NB_FIXEDWIDTH|wx.NB_NOPAGETHEME )
		self.m_grep_notebook.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )
		
		self.m_settings_panel = wx.Panel( self.m_grep_notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.m_settings_panel.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )
		
		bSizer10 = wx.BoxSizer( wx.VERTICAL )
		
		fgSizer2 = wx.FlexGridSizer( 5, 1, 0, 0 )
		fgSizer2.AddGrowableCol( 0 )
		fgSizer2.SetFlexibleDirection( wx.BOTH )
		fgSizer2.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		sbSizer2 = wx.StaticBoxSizer( wx.StaticBox( self.m_settings_panel, wx.ID_ANY, u"Search and Replace" ), wx.HORIZONTAL )
		
		fgSizer6 = wx.FlexGridSizer( 0, 1, 0, 0 )
		fgSizer6.AddGrowableCol( 0 )
		fgSizer6.SetFlexibleDirection( wx.BOTH )
		fgSizer6.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer8 = wx.FlexGridSizer( 0, 3, 0, 0 )
		fgSizer8.AddGrowableCol( 1 )
		fgSizer8.SetFlexibleDirection( wx.BOTH )
		fgSizer8.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_searchin_label = wx.StaticText( self.m_settings_panel, wx.ID_ANY, u"Search in", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_searchin_label.Wrap( -1 )
		fgSizer8.Add( self.m_searchin_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )
		
		self.m_searchin_text = AutoCompleteCombo(self.m_settings_panel, wx.ID_ANY)
		fgSizer8.Add( self.m_searchin_text, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_searchin_dir_picker = wx.Button( self.m_settings_panel, wx.ID_ANY, u"...", wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT )
		fgSizer8.Add( self.m_searchin_dir_picker, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.m_searchfor_label = wx.StaticText( self.m_settings_panel, wx.ID_ANY, u"Search for", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_searchfor_label.Wrap( -1 )
		fgSizer8.Add( self.m_searchfor_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )
		
		self.m_searchfor_textbox = AutoCompleteCombo(self.m_settings_panel, wx.ID_ANY)
		fgSizer8.Add( self.m_searchfor_textbox, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		fgSizer8.Add( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.m_replace_label = wx.StaticText( self.m_settings_panel, wx.ID_ANY, u"Replace with", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_replace_label.Wrap( -1 )
		fgSizer8.Add( self.m_replace_label, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		self.m_replace_textbox = AutoCompleteCombo(self.m_settings_panel, wx.ID_ANY)
		fgSizer8.Add( self.m_replace_textbox, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		fgSizer6.Add( fgSizer8, 1, wx.EXPAND, 5 )
		
		fgSizer9 = wx.FlexGridSizer( 0, 3, 0, 0 )
		fgSizer9.AddGrowableCol( 0 )
		fgSizer9.AddGrowableCol( 2 )
		fgSizer9.SetFlexibleDirection( wx.BOTH )
		fgSizer9.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		
		fgSizer9.Add( ( 0, 0), 1, wx.EXPAND, 5 )
		
		gbSizer2 = wx.GridBagSizer( 0, 0 )
		gbSizer2.SetFlexibleDirection( wx.BOTH )
		gbSizer2.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		gbSizer2.SetEmptyCellSize( wx.Size( -1,0 ) )
		
		self.m_regex_search_checkbox = wx.CheckBox( self.m_settings_panel, wx.ID_ANY, u"Search with regex", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_regex_search_checkbox.SetValue(True) 
		gbSizer2.Add( self.m_regex_search_checkbox, wx.GBPosition( 0, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		self.m_case_checkbox = wx.CheckBox( self.m_settings_panel, wx.ID_ANY, u"Search case-sensitive", wx.DefaultPosition, wx.DefaultSize, 0 )
		gbSizer2.Add( self.m_case_checkbox, wx.GBPosition( 0, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		self.m_dotmatch_checkbox = wx.CheckBox( self.m_settings_panel, wx.ID_ANY, u"Dot matches newline", wx.DefaultPosition, wx.DefaultSize, 0 )
		gbSizer2.Add( self.m_dotmatch_checkbox, wx.GBPosition( 0, 2 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		self.m_unicode_checkbox = wx.CheckBox( self.m_settings_panel, wx.ID_ANY, u"Use Unicode properties", wx.DefaultPosition, wx.DefaultSize, 0 )
		gbSizer2.Add( self.m_unicode_checkbox, wx.GBPosition( 0, 3 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		self.m_bestmatch_checkbox = wx.CheckBox( self.m_settings_panel, wx.ID_ANY, u"Best fuzzy match", wx.DefaultPosition, wx.DefaultSize, 0 )
		gbSizer2.Add( self.m_bestmatch_checkbox, wx.GBPosition( 1, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		self.m_enhancematch_checkbox = wx.CheckBox( self.m_settings_panel, wx.ID_ANY, u"Improve fuzzy fit", wx.DefaultPosition, wx.DefaultSize, 0 )
		gbSizer2.Add( self.m_enhancematch_checkbox, wx.GBPosition( 1, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		self.m_word_checkbox = wx.CheckBox( self.m_settings_panel, wx.ID_ANY, u"Unicode word breaks", wx.DefaultPosition, wx.DefaultSize, 0 )
		gbSizer2.Add( self.m_word_checkbox, wx.GBPosition( 1, 2 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		self.m_reverse_checkbox = wx.CheckBox( self.m_settings_panel, wx.ID_ANY, u"Search backwards", wx.DefaultPosition, wx.DefaultSize, 0 )
		gbSizer2.Add( self.m_reverse_checkbox, wx.GBPosition( 1, 3 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		self.m_posix_checkbox = wx.CheckBox( self.m_settings_panel, wx.ID_ANY, u"Use POSIX matching", wx.DefaultPosition, wx.DefaultSize, 0 )
		gbSizer2.Add( self.m_posix_checkbox, wx.GBPosition( 2, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		self.m_format_replace_checkbox = wx.CheckBox( self.m_settings_panel, wx.ID_ANY, u"Format style replacements", wx.DefaultPosition, wx.DefaultSize, 0 )
		gbSizer2.Add( self.m_format_replace_checkbox, wx.GBPosition( 2, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		self.m_fullcase_checkbox = wx.CheckBox( self.m_settings_panel, wx.ID_ANY, u"Full case-folding", wx.DefaultPosition, wx.DefaultSize, 0 )
		gbSizer2.Add( self.m_fullcase_checkbox, wx.GBPosition( 2, 2 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		self.m_staticline11 = wx.StaticLine( self.m_settings_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		gbSizer2.Add( self.m_staticline11, wx.GBPosition( 3, 0 ), wx.GBSpan( 1, 4 ), wx.EXPAND |wx.ALL, 5 )
		
		self.m_boolean_checkbox = wx.CheckBox( self.m_settings_panel, wx.ID_ANY, u"Boolean match", wx.DefaultPosition, wx.DefaultSize, 0 )
		gbSizer2.Add( self.m_boolean_checkbox, wx.GBPosition( 4, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		self.m_count_only_checkbox = wx.CheckBox( self.m_settings_panel, wx.ID_ANY, u"Count only", wx.DefaultPosition, wx.DefaultSize, 0 )
		gbSizer2.Add( self.m_count_only_checkbox, wx.GBPosition( 4, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		self.m_backup_checkbox = wx.CheckBox( self.m_settings_panel, wx.ID_ANY, u"Create backups", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_backup_checkbox.SetValue(True) 
		gbSizer2.Add( self.m_backup_checkbox, wx.GBPosition( 4, 2 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		fgSizer40 = wx.FlexGridSizer( 0, 2, 0, 0 )
		fgSizer40.SetFlexibleDirection( wx.BOTH )
		fgSizer40.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_NONE )
		
		self.m_force_encode_checkbox = wx.CheckBox( self.m_settings_panel, wx.ID_ANY, u"Force", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer40.Add( self.m_force_encode_checkbox, 0, wx.ALL, 5 )
		
		m_force_encode_choiceChoices = []
		self.m_force_encode_choice = wx.Choice( self.m_settings_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_force_encode_choiceChoices, wx.CB_SORT )
		self.m_force_encode_choice.SetSelection( 0 )
		fgSizer40.Add( self.m_force_encode_choice, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		gbSizer2.Add( fgSizer40, wx.GBPosition( 4, 3 ), wx.GBSpan( 1, 1 ), wx.EXPAND, 5 )
		
		
		fgSizer9.Add( gbSizer2, 1, wx.EXPAND, 5 )
		
		
		fgSizer9.Add( ( 0, 0), 1, wx.EXPAND, 5 )
		
		
		fgSizer6.Add( fgSizer9, 1, wx.EXPAND, 5 )
		
		self.m_staticline3 = wx.StaticLine( self.m_settings_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		fgSizer6.Add( self.m_staticline3, 0, wx.EXPAND |wx.ALL, 5 )
		
		fgSizer17 = wx.FlexGridSizer( 0, 4, 0, 0 )
		fgSizer17.AddGrowableCol( 1 )
		fgSizer17.SetFlexibleDirection( wx.BOTH )
		fgSizer17.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_regex_test_button = wx.Button( self.m_settings_panel, wx.ID_ANY, u"Test Regex", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer17.Add( self.m_regex_test_button, 0, wx.ALL, 5 )
		
		
		fgSizer17.Add( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.m_save_search_button = wx.Button( self.m_settings_panel, wx.ID_ANY, u"Save Search", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer17.Add( self.m_save_search_button, 0, wx.ALL, 5 )
		
		self.m_load_search_button = wx.Button( self.m_settings_panel, wx.ID_ANY, u"Load Search", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer17.Add( self.m_load_search_button, 0, wx.ALL, 5 )
		
		
		fgSizer6.Add( fgSizer17, 1, wx.EXPAND, 5 )
		
		
		sbSizer2.Add( fgSizer6, 1, wx.EXPAND, 5 )
		
		
		fgSizer2.Add( sbSizer2, 1, wx.EXPAND, 5 )
		
		sbSizer4 = wx.StaticBoxSizer( wx.StaticBox( self.m_settings_panel, wx.ID_ANY, u"Limit Search" ), wx.VERTICAL )
		
		gbSizer3 = wx.GridBagSizer( 0, 0 )
		gbSizer3.SetFlexibleDirection( wx.BOTH )
		gbSizer3.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_size_is_label = wx.StaticText( self.m_settings_panel, wx.ID_ANY, u"Size is", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_size_is_label.Wrap( -1 )
		gbSizer3.Add( self.m_size_is_label, wx.GBPosition( 0, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		m_logic_choiceChoices = [ u"any", u"greater than", u"equal to", u"less than" ]
		self.m_logic_choice = wx.Choice( self.m_settings_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_logic_choiceChoices, 0 )
		self.m_logic_choice.SetSelection( 0 )
		gbSizer3.Add( self.m_logic_choice, wx.GBPosition( 0, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		fgSizer37 = wx.FlexGridSizer( 0, 2, 0, 0 )
		fgSizer37.SetFlexibleDirection( wx.HORIZONTAL )
		fgSizer37.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_size_text = wx.TextCtrl( self.m_settings_panel, wx.ID_ANY, u"1000", wx.DefaultPosition, wx.Size( -1,-1 ), 0 )
		fgSizer37.Add( self.m_size_text, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_size_type_label = wx.StaticText( self.m_settings_panel, wx.ID_ANY, u"KB", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_size_type_label.Wrap( -1 )
		fgSizer37.Add( self.m_size_type_label, 0, wx.BOTTOM|wx.RIGHT|wx.TOP|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		gbSizer3.Add( fgSizer37, wx.GBPosition( 0, 2 ), wx.GBSpan( 1, 3 ), wx.EXPAND, 5 )
		
		self.m_exclude_label = wx.StaticText( self.m_settings_panel, wx.ID_ANY, u"Exclude folders", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_exclude_label.Wrap( -1 )
		gbSizer3.Add( self.m_exclude_label, wx.GBPosition( 0, 6 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		self.m_exclude_textbox = AutoCompleteCombo(self.m_settings_panel, wx.ID_ANY)
		gbSizer3.Add( self.m_exclude_textbox, wx.GBPosition( 0, 7 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5 )
		
		self.m_dirregex_checkbox = wx.CheckBox( self.m_settings_panel, wx.ID_ANY, u"Regex", wx.DefaultPosition, wx.DefaultSize, 0 )
		gbSizer3.Add( self.m_dirregex_checkbox, wx.GBPosition( 0, 8 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_modified_label = wx.StaticText( self.m_settings_panel, wx.ID_ANY, u"Modified", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_modified_label.Wrap( -1 )
		gbSizer3.Add( self.m_modified_label, wx.GBPosition( 1, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		m_modified_choiceChoices = [ u"on any", u"after", u"on", u"before" ]
		self.m_modified_choice = wx.Choice( self.m_settings_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_modified_choiceChoices, 0 )
		self.m_modified_choice.SetSelection( 0 )
		gbSizer3.Add( self.m_modified_choice, wx.GBPosition( 1, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5 )
		
		self.m_modified_date_picker = DatePicker(self.m_settings_panel, wx.ID_ANY)
		gbSizer3.Add( self.m_modified_date_picker, wx.GBPosition( 1, 2 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		self.m_modified_time_picker = TimeCtrl(self.m_settings_panel, wx.ID_ANY, style=wx.TE_PROCESS_TAB, oob_color="white", fmt24hr=True)
		gbSizer3.Add( self.m_modified_time_picker, wx.GBPosition( 1, 3 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		self.m_modified_spin = wx.SpinButton( self.m_settings_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
		gbSizer3.Add( self.m_modified_spin, wx.GBPosition( 1, 4 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		self.m_filematch_label = wx.StaticText( self.m_settings_panel, wx.ID_ANY, u"Files which match", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_filematch_label.Wrap( -1 )
		gbSizer3.Add( self.m_filematch_label, wx.GBPosition( 1, 6 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		self.m_filematch_textbox = AutoCompleteCombo(self.m_settings_panel, wx.ID_ANY)
		gbSizer3.Add( self.m_filematch_textbox, wx.GBPosition( 1, 7 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5 )
		
		self.m_fileregex_checkbox = wx.CheckBox( self.m_settings_panel, wx.ID_ANY, u"Regex", wx.DefaultPosition, wx.DefaultSize, 0 )
		gbSizer3.Add( self.m_fileregex_checkbox, wx.GBPosition( 1, 8 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_created_label = wx.StaticText( self.m_settings_panel, wx.ID_ANY, u"Created", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_created_label.Wrap( -1 )
		gbSizer3.Add( self.m_created_label, wx.GBPosition( 2, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		m_created_choiceChoices = [ u"on any", u"after", u"on", u"before" ]
		self.m_created_choice = wx.Choice( self.m_settings_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_created_choiceChoices, 0 )
		self.m_created_choice.SetSelection( 0 )
		gbSizer3.Add( self.m_created_choice, wx.GBPosition( 2, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5 )
		
		self.m_created_date_picker = DatePicker(self.m_settings_panel, wx.ID_ANY)
		gbSizer3.Add( self.m_created_date_picker, wx.GBPosition( 2, 2 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		self.m_created_time_picker = TimeCtrl(self.m_settings_panel, wx.ID_ANY, style=wx.TE_PROCESS_TAB, oob_color="white", fmt24hr=True)
		gbSizer3.Add( self.m_created_time_picker, wx.GBPosition( 2, 3 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		self.m_created_spin = wx.SpinButton( self.m_settings_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
		gbSizer3.Add( self.m_created_spin, wx.GBPosition( 2, 4 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		self.m_staticline41 = wx.StaticLine( self.m_settings_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_VERTICAL )
		gbSizer3.Add( self.m_staticline41, wx.GBPosition( 0, 5 ), wx.GBSpan( 3, 1 ), wx.EXPAND |wx.ALL, 5 )
		
		fgSizer32 = wx.FlexGridSizer( 0, 5, 0, 0 )
		fgSizer32.AddGrowableCol( 0 )
		fgSizer32.AddGrowableCol( 4 )
		fgSizer32.SetFlexibleDirection( wx.BOTH )
		fgSizer32.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		
		fgSizer32.Add( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.m_subfolder_checkbox = wx.CheckBox( self.m_settings_panel, wx.ID_ANY, u"Include subfolders", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_subfolder_checkbox.SetValue(True) 
		fgSizer32.Add( self.m_subfolder_checkbox, 0, wx.ALL, 5 )
		
		self.m_hidden_checkbox = wx.CheckBox( self.m_settings_panel, wx.ID_ANY, u"Include hidden", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer32.Add( self.m_hidden_checkbox, 0, wx.ALL, 5 )
		
		self.m_binary_checkbox = wx.CheckBox( self.m_settings_panel, wx.ID_ANY, u"Include binary files", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer32.Add( self.m_binary_checkbox, 0, wx.ALL, 5 )
		
		
		fgSizer32.Add( ( 0, 0), 1, wx.EXPAND, 5 )
		
		
		gbSizer3.Add( fgSizer32, wx.GBPosition( 3, 0 ), wx.GBSpan( 1, 9 ), wx.EXPAND, 5 )
		
		
		gbSizer3.AddGrowableCol( 7 )
		gbSizer3.AddGrowableRow( 0 )
		gbSizer3.AddGrowableRow( 1 )
		gbSizer3.AddGrowableRow( 2 )
		gbSizer3.AddGrowableRow( 3 )
		
		sbSizer4.Add( gbSizer3, 1, wx.EXPAND, 5 )
		
		
		fgSizer2.Add( sbSizer4, 1, wx.EXPAND, 5 )
		
		self.m_progressbar = wx.Gauge( self.m_settings_panel, wx.ID_ANY, 100, wx.DefaultPosition, wx.Size( -1,5 ), wx.GA_HORIZONTAL )
		self.m_progressbar.SetValue( 0 ) 
		fgSizer2.Add( self.m_progressbar, 0, wx.ALIGN_CENTER|wx.ALL|wx.EXPAND, 5 )
		
		fgSizer38 = wx.FlexGridSizer( 0, 3, 0, 0 )
		fgSizer38.AddGrowableCol( 0 )
		fgSizer38.SetFlexibleDirection( wx.BOTH )
		fgSizer38.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		
		fgSizer38.Add( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.m_replace_button = wx.Button( self.m_settings_panel, wx.ID_ANY, u"Replace", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer38.Add( self.m_replace_button, 0, wx.ALL, 5 )
		
		self.m_search_button = wx.Button( self.m_settings_panel, wx.ID_ANY, u"Search", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer38.Add( self.m_search_button, 0, wx.ALIGN_RIGHT|wx.ALL, 5 )
		
		
		fgSizer2.Add( fgSizer38, 1, wx.EXPAND, 5 )
		
		
		bSizer10.Add( fgSizer2, 1, wx.EXPAND, 5 )
		
		
		self.m_settings_panel.SetSizer( bSizer10 )
		self.m_settings_panel.Layout()
		bSizer10.Fit( self.m_settings_panel )
		self.m_grep_notebook.AddPage( self.m_settings_panel, u"Search", True )
		self.m_result_file_panel = wx.Panel( self.m_grep_notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.m_result_file_panel.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )
		
		bSizer7 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_result_file_list = ResultFileList(self.m_result_file_panel)
		bSizer7.Add( self.m_result_file_list, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		self.m_result_file_panel.SetSizer( bSizer7 )
		self.m_result_file_panel.Layout()
		bSizer7.Fit( self.m_result_file_panel )
		self.m_grep_notebook.AddPage( self.m_result_file_panel, u"Files", False )
		self.m_result_content_panel = wx.Panel( self.m_grep_notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.m_result_content_panel.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )
		
		bSizer6 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_result_list = ResultContentList(self.m_result_content_panel)
		bSizer6.Add( self.m_result_list, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		self.m_result_content_panel.SetSizer( bSizer6 )
		self.m_result_content_panel.Layout()
		bSizer6.Fit( self.m_result_content_panel )
		self.m_grep_notebook.AddPage( self.m_result_content_panel, u"Content", False )
		
		fgSizer13.Add( self.m_grep_notebook, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		self.m_main_panel.SetSizer( fgSizer13 )
		self.m_main_panel.Layout()
		fgSizer13.Fit( self.m_main_panel )
		bFrameSizer.Add( self.m_main_panel, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		self.SetSizer( bFrameSizer )
		self.Layout()
		bFrameSizer.Fit( self )
		self.m_statusbar = self.CreateStatusBar( 1, wx.STB_SIZEGRIP, wx.ID_ANY )
		self.m_menu = wx.MenuBar( 0 )
		self.m_file_menu = wx.Menu()
		self.m_preferences_menuitem = wx.MenuItem( self.m_file_menu, wx.ID_PREFERENCES, u"&Preferences", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_file_menu.Append( self.m_preferences_menuitem )
		
		self.m_export_submenuitem = wx.Menu()
		self.m_export_html_menuitem = wx.MenuItem( self.m_export_submenuitem, wx.ID_ANY, u"HTML", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_export_submenuitem.Append( self.m_export_html_menuitem )
		
		self.m_export_csv_menuitem = wx.MenuItem( self.m_export_submenuitem, wx.ID_ANY, u"CSV", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_export_submenuitem.Append( self.m_export_csv_menuitem )
		
		self.m_file_menu.AppendSubMenu( self.m_export_submenuitem, u"Export" )
		
		self.m_file_menu.AppendSeparator()
		
		self.m_quit_menuitem = wx.MenuItem( self.m_file_menu, wx.ID_EXit, u"&Exit", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_file_menu.Append( self.m_quit_menuitem )
		
		self.m_menu.Append( self.m_file_menu, u"File" ) 
		
		self.m_view_menu = wx.Menu()
		self.m_hide_limit_menuitem = wx.MenuItem( self.m_view_menu, wx.ID_ANY, u"Hide Limit Search Panel", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_view_menu.Append( self.m_hide_limit_menuitem )
		
		self.m_menu.Append( self.m_view_menu, u"View" ) 
		
		self.m_help_menu = wx.Menu()
		self.m_about_menuitem = wx.MenuItem( self.m_help_menu, wx.ID_ABOUT, u"&About Rummage", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_help_menu.Append( self.m_about_menuitem )
		
		self.m_help_menu.AppendSeparator()
		
		self.m_documentation_menuitem = wx.MenuItem( self.m_help_menu, wx.ID_ANY, u"Documentation", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_help_menu.Append( self.m_documentation_menuitem )
		
		self.m_issues_menuitem = wx.MenuItem( self.m_help_menu, wx.ID_ANY, u"Help and Support", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_help_menu.Append( self.m_issues_menuitem )
		
		self.m_help_menu.AppendSeparator()
		
		self.m_log_menuitem = wx.MenuItem( self.m_help_menu, wx.ID_ANY, u"Open Log File", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_help_menu.Append( self.m_log_menuitem )
		
		self.m_menu.Append( self.m_help_menu, u"Help" ) 
		
		self.SetMenuBar( self.m_menu )
		
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.Bind( wx.EVT_CLOSE, self.on_close )
		self.m_regex_search_checkbox.Bind( wx.EVT_CHECKBOX, self.on_regex_search_toggle )
		self.m_regex_test_button.Bind( wx.EVT_BUTTON, self.on_test_regex )
		self.m_save_search_button.Bind( wx.EVT_BUTTON, self.on_save_search )
		self.m_load_search_button.Bind( wx.EVT_BUTTON, self.on_load_search )
		self.m_dirregex_checkbox.Bind( wx.EVT_CHECKBOX, self.on_dirregex_toggle )
		self.m_fileregex_checkbox.Bind( wx.EVT_CHECKBOX, self.on_fileregex_toggle )
		self.m_replace_button.Bind( wx.EVT_BUTTON, self.on_replace_click )
		self.m_search_button.Bind( wx.EVT_BUTTON, self.on_search_click )
		self.Bind( wx.EVT_MENU, self.on_preferences, id = self.m_preferences_menuitem.GetId() )
		self.Bind( wx.EVT_MENU, self.on_export_html, id = self.m_export_html_menuitem.GetId() )
		self.Bind( wx.EVT_MENU, self.on_export_csv, id = self.m_export_csv_menuitem.GetId() )
		self.Bind( wx.EVT_MENU, self.on_exit, id = self.m_quit_menuitem.GetId() )
		self.Bind( wx.EVT_MENU, self.on_hide_limit, id = self.m_hide_limit_menuitem.GetId() )
		self.Bind( wx.EVT_MENU, self.on_about, id = self.m_about_menuitem.GetId() )
		self.Bind( wx.EVT_MENU, self.on_documentation, id = self.m_documentation_menuitem.GetId() )
		self.Bind( wx.EVT_MENU, self.on_issues, id = self.m_issues_menuitem.GetId() )
		self.Bind( wx.EVT_MENU, self.on_show_log_file, id = self.m_log_menuitem.GetId() )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def on_close( self, event ):
		event.Skip()
	
	def on_regex_search_toggle( self, event ):
		event.Skip()
	
	def on_test_regex( self, event ):
		event.Skip()
	
	def on_save_search( self, event ):
		event.Skip()
	
	def on_load_search( self, event ):
		event.Skip()
	
	def on_dirregex_toggle( self, event ):
		event.Skip()
	
	def on_fileregex_toggle( self, event ):
		event.Skip()
	
	def on_replace_click( self, event ):
		event.Skip()
	
	def on_search_click( self, event ):
		event.Skip()
	
	def on_preferences( self, event ):
		event.Skip()
	
	def on_export_html( self, event ):
		event.Skip()
	
	def on_export_csv( self, event ):
		event.Skip()
	
	def on_exit( self, event ):
		event.Skip()
	
	def on_hide_limit( self, event ):
		event.Skip()
	
	def on_about( self, event ):
		event.Skip()
	
	def on_documentation( self, event ):
		event.Skip()
	
	def on_issues( self, event ):
		event.Skip()
	
	def on_show_log_file( self, event ):
		event.Skip()
	

###########################################################################
## Class RegexTestDialog
###########################################################################

class RegexTestDialog ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )
		
		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )
		
		bSizer8 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_tester_panel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.m_tester_panel.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )
		
		fgSizer18 = wx.FlexGridSizer( 5, 1, 0, 0 )
		fgSizer18.AddGrowableCol( 0 )
		fgSizer18.AddGrowableRow( 0 )
		fgSizer18.AddGrowableRow( 1 )
		fgSizer18.SetFlexibleDirection( wx.BOTH )
		fgSizer18.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		sbSizer11 = wx.StaticBoxSizer( wx.StaticBox( self.m_tester_panel, wx.ID_ANY, u"Text" ), wx.VERTICAL )
		
		self.m_test_text = wx.TextCtrl( self.m_tester_panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE|wx.TE_RICH2 )
		sbSizer11.Add( self.m_test_text, 1, wx.ALL|wx.EXPAND|wx.FIXED_MINSIZE, 5 )
		
		
		fgSizer18.Add( sbSizer11, 1, wx.EXPAND, 5 )
		
		sbSizer111 = wx.StaticBoxSizer( wx.StaticBox( self.m_tester_panel, wx.ID_ANY, u"Result" ), wx.VERTICAL )
		
		self.m_test_replace_text = wx.TextCtrl( self.m_tester_panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_RICH2 )
		sbSizer111.Add( self.m_test_replace_text, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		fgSizer18.Add( sbSizer111, 1, wx.EXPAND, 5 )
		
		sbSizer9 = wx.StaticBoxSizer( wx.StaticBox( self.m_tester_panel, wx.ID_ANY, u"Regex Input" ), wx.VERTICAL )
		
		fgSizer41 = wx.FlexGridSizer( 0, 1, 0, 0 )
		fgSizer41.AddGrowableCol( 0 )
		fgSizer41.SetFlexibleDirection( wx.BOTH )
		fgSizer41.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer39 = wx.FlexGridSizer( 0, 2, 0, 0 )
		fgSizer39.AddGrowableCol( 1 )
		fgSizer39.SetFlexibleDirection( wx.BOTH )
		fgSizer39.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_find_label = wx.StaticText( self.m_tester_panel, wx.ID_ANY, u"Find", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_find_label.Wrap( -1 )
		fgSizer39.Add( self.m_find_label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		self.m_regex_text = wx.TextCtrl( self.m_tester_panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer39.Add( self.m_regex_text, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_replace_label = wx.StaticText( self.m_tester_panel, wx.ID_ANY, u"Replace", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_replace_label.Wrap( -1 )
		fgSizer39.Add( self.m_replace_label, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )
		
		self.m_replace_text = wx.TextCtrl( self.m_tester_panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer39.Add( self.m_replace_text, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		fgSizer41.Add( fgSizer39, 1, wx.EXPAND, 5 )
		
		fgSizer42 = wx.FlexGridSizer( 0, 3, 0, 0 )
		fgSizer42.AddGrowableCol( 0 )
		fgSizer42.AddGrowableCol( 2 )
		fgSizer42.SetFlexibleDirection( wx.BOTH )
		fgSizer42.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		
		fgSizer42.Add( ( 0, 0), 1, wx.EXPAND, 5 )
		
		fgSizer19 = wx.FlexGridSizer( 0, 3, 0, 0 )
		fgSizer19.SetFlexibleDirection( wx.BOTH )
		fgSizer19.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_case_checkbox = wx.CheckBox( self.m_tester_panel, wx.ID_ANY, u"Search case-sensitive", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer19.Add( self.m_case_checkbox, 0, wx.ALL, 5 )
		
		self.m_dotmatch_checkbox = wx.CheckBox( self.m_tester_panel, wx.ID_ANY, u"Dot matches newline", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer19.Add( self.m_dotmatch_checkbox, 0, wx.ALL, 5 )
		
		self.m_unicode_checkbox = wx.CheckBox( self.m_tester_panel, wx.ID_ANY, u"Use Unicode properties", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer19.Add( self.m_unicode_checkbox, 0, wx.ALL, 5 )
		
		self.m_bestmatch_checkbox = wx.CheckBox( self.m_tester_panel, wx.ID_ANY, u"Best fuzzy match", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_bestmatch_checkbox.Hide()
		
		fgSizer19.Add( self.m_bestmatch_checkbox, 0, wx.ALL, 5 )
		
		self.m_enhancematch_checkbox = wx.CheckBox( self.m_tester_panel, wx.ID_ANY, u"Improve fuzzy fit", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_enhancematch_checkbox.Hide()
		
		fgSizer19.Add( self.m_enhancematch_checkbox, 0, wx.ALL, 5 )
		
		self.m_word_checkbox = wx.CheckBox( self.m_tester_panel, wx.ID_ANY, u"Unicode word breaks", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_word_checkbox.Hide()
		
		fgSizer19.Add( self.m_word_checkbox, 0, wx.ALL, 5 )
		
		self.m_reverse_checkbox = wx.CheckBox( self.m_tester_panel, wx.ID_ANY, u"Search backwards", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_reverse_checkbox.Hide()
		
		fgSizer19.Add( self.m_reverse_checkbox, 0, wx.ALL, 5 )
		
		self.m_posix_checkbox = wx.CheckBox( self.m_tester_panel, wx.ID_ANY, u"Use POSIX matching", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_posix_checkbox.Hide()
		
		fgSizer19.Add( self.m_posix_checkbox, 0, wx.ALL, 5 )
		
		self.m_format_replace_checkbox = wx.CheckBox( self.m_tester_panel, wx.ID_ANY, u"Format style replacements", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_format_replace_checkbox.Hide()
		
		fgSizer19.Add( self.m_format_replace_checkbox, 0, wx.ALL, 5 )
		
		self.m_fullcase_checkbox = wx.CheckBox( self.m_tester_panel, wx.ID_ANY, u"Full case-folding", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_fullcase_checkbox.Hide()
		
		fgSizer19.Add( self.m_fullcase_checkbox, 0, wx.ALL, 5 )
		
		
		fgSizer42.Add( fgSizer19, 1, wx.EXPAND, 5 )
		
		
		fgSizer42.Add( ( 0, 0), 1, wx.EXPAND, 5 )
		
		
		fgSizer41.Add( fgSizer42, 1, wx.EXPAND, 5 )
		
		
		sbSizer9.Add( fgSizer41, 1, wx.EXPAND, 5 )
		
		
		fgSizer18.Add( sbSizer9, 1, wx.EXPAND, 5 )
		
		fgSizer20 = wx.FlexGridSizer( 0, 4, 0, 0 )
		fgSizer20.AddGrowableCol( 0 )
		fgSizer20.AddGrowableCol( 3 )
		fgSizer20.SetFlexibleDirection( wx.BOTH )
		fgSizer20.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		
		fgSizer20.Add( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.m_use_regex_button = wx.Button( self.m_tester_panel, wx.ID_ANY, u"Use", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer20.Add( self.m_use_regex_button, 0, wx.ALL, 5 )
		
		self.m_close_button = wx.Button( self.m_tester_panel, wx.ID_ANY, u"Close", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer20.Add( self.m_close_button, 0, wx.ALL, 5 )
		
		
		fgSizer20.Add( ( 0, 0), 1, wx.EXPAND, 5 )
		
		
		fgSizer18.Add( fgSizer20, 1, wx.EXPAND, 5 )
		
		
		self.m_tester_panel.SetSizer( fgSizer18 )
		self.m_tester_panel.Layout()
		fgSizer18.Fit( self.m_tester_panel )
		bSizer8.Add( self.m_tester_panel, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		self.SetSizer( bSizer8 )
		self.Layout()
		bSizer8.Fit( self )
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.Bind( wx.EVT_CLOSE, self.on_close )
		self.m_test_text.Bind( wx.EVT_TEXT, self.on_test_changed )
		self.m_regex_text.Bind( wx.EVT_TEXT, self.on_regex_changed )
		self.m_replace_text.Bind( wx.EVT_TEXT, self.on_replace_changed )
		self.m_case_checkbox.Bind( wx.EVT_CHECKBOX, self.on_case_toggle )
		self.m_dotmatch_checkbox.Bind( wx.EVT_CHECKBOX, self.on_dot_toggle )
		self.m_unicode_checkbox.Bind( wx.EVT_CHECKBOX, self.on_unicode_toggle )
		self.m_bestmatch_checkbox.Bind( wx.EVT_CHECKBOX, self.on_bestmatch_toggle )
		self.m_enhancematch_checkbox.Bind( wx.EVT_CHECKBOX, self.on_enhancematch_toggle )
		self.m_word_checkbox.Bind( wx.EVT_CHECKBOX, self.on_word_toggle )
		self.m_reverse_checkbox.Bind( wx.EVT_CHECKBOX, self.on_reverse_toggle )
		self.m_posix_checkbox.Bind( wx.EVT_CHECKBOX, self.on_posix_toggle )
		self.m_format_replace_checkbox.Bind( wx.EVT_CHECKBOX, self.on_format_replace_toggle )
		self.m_fullcase_checkbox.Bind( wx.EVT_CHECKBOX, self.on_fullcase_toggle )
		self.m_use_regex_button.Bind( wx.EVT_BUTTON, self.on_use )
		self.m_close_button.Bind( wx.EVT_BUTTON, self.on_cancel )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def on_close( self, event ):
		event.Skip()
	
	def on_test_changed( self, event ):
		event.Skip()
	
	def on_regex_changed( self, event ):
		event.Skip()
	
	def on_replace_changed( self, event ):
		event.Skip()
	
	def on_case_toggle( self, event ):
		event.Skip()
	
	def on_dot_toggle( self, event ):
		event.Skip()
	
	def on_unicode_toggle( self, event ):
		event.Skip()
	
	def on_bestmatch_toggle( self, event ):
		event.Skip()
	
	def on_enhancematch_toggle( self, event ):
		event.Skip()
	
	def on_word_toggle( self, event ):
		event.Skip()
	
	def on_reverse_toggle( self, event ):
		event.Skip()
	
	def on_posix_toggle( self, event ):
		event.Skip()
	
	def on_format_replace_toggle( self, event ):
		event.Skip()
	
	def on_fullcase_toggle( self, event ):
		event.Skip()
	
	def on_use( self, event ):
		event.Skip()
	
	def on_cancel( self, event ):
		event.Skip()
	

###########################################################################
## Class LoadSearchDialog
###########################################################################

class LoadSearchDialog ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Searches", pos = wx.DefaultPosition, size = wx.Size( 470,288 ), style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )
		
		self.SetSizeHints( wx.Size( 470,288 ), wx.DefaultSize )
		
		bSizer13 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_load_panel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.m_load_panel.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )
		
		fgSizer36 = wx.FlexGridSizer( 2, 1, 0, 0 )
		fgSizer36.AddGrowableCol( 0 )
		fgSizer36.AddGrowableRow( 0 )
		fgSizer36.SetFlexibleDirection( wx.BOTH )
		fgSizer36.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_search_list = SavedSearchList(self.m_load_panel)
		fgSizer36.Add( self.m_search_list, 1, wx.ALL|wx.EXPAND, 5 )
		
		fgSizer37 = wx.FlexGridSizer( 0, 5, 0, 0 )
		fgSizer37.AddGrowableCol( 0 )
		fgSizer37.AddGrowableCol( 4 )
		fgSizer37.SetFlexibleDirection( wx.BOTH )
		fgSizer37.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		
		fgSizer37.Add( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.m_delete_button = wx.Button( self.m_load_panel, wx.ID_ANY, u"Remove", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer37.Add( self.m_delete_button, 0, wx.ALL, 5 )
		
		self.m_load_button = wx.Button( self.m_load_panel, wx.ID_ANY, u"Load", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer37.Add( self.m_load_button, 0, wx.ALL, 5 )
		
		self.m_cancel_button = wx.Button( self.m_load_panel, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer37.Add( self.m_cancel_button, 0, wx.ALL, 5 )
		
		
		fgSizer37.Add( ( 0, 0), 1, wx.EXPAND, 5 )
		
		
		fgSizer36.Add( fgSizer37, 1, wx.EXPAND, 5 )
		
		
		self.m_load_panel.SetSizer( fgSizer36 )
		self.m_load_panel.Layout()
		fgSizer36.Fit( self.m_load_panel )
		bSizer13.Add( self.m_load_panel, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		self.SetSizer( bSizer13 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_delete_button.Bind( wx.EVT_BUTTON, self.on_delete )
		self.m_load_button.Bind( wx.EVT_BUTTON, self.on_load )
		self.m_cancel_button.Bind( wx.EVT_BUTTON, self.on_cancel )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def on_delete( self, event ):
		event.Skip()
	
	def on_load( self, event ):
		event.Skip()
	
	def on_cancel( self, event ):
		event.Skip()
	

###########################################################################
## Class SettingsDialog
###########################################################################

class SettingsDialog ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Preferences", pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )
		
		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )
		
		bSizer7 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_settings_panel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,-1 ), wx.TAB_TRAVERSAL )
		fgSizer17 = wx.FlexGridSizer( 0, 1, 0, 0 )
		fgSizer17.AddGrowableCol( 0 )
		fgSizer17.SetFlexibleDirection( wx.BOTH )
		fgSizer17.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		sbSizer7 = wx.StaticBoxSizer( wx.StaticBox( self.m_settings_panel, wx.ID_ANY, u"Editor" ), wx.VERTICAL )
		
		fgSizer13 = wx.FlexGridSizer( 0, 2, 0, 0 )
		fgSizer13.AddGrowableCol( 0 )
		fgSizer13.SetFlexibleDirection( wx.BOTH )
		fgSizer13.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_editor_text = wx.TextCtrl( self.m_settings_panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
		fgSizer13.Add( self.m_editor_text, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.m_editor_button = wx.Button( self.m_settings_panel, wx.ID_ANY, u"Change", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer13.Add( self.m_editor_button, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		
		sbSizer7.Add( fgSizer13, 1, wx.EXPAND, 5 )
		
		
		fgSizer17.Add( sbSizer7, 1, wx.EXPAND, 5 )
		
		sbSizer8 = wx.StaticBoxSizer( wx.StaticBox( self.m_settings_panel, wx.ID_ANY, u"General" ), wx.VERTICAL )
		
		self.m_single_checkbox = wx.CheckBox( self.m_settings_panel, wx.ID_ANY, u"Single Instance (applies to new instances)", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer8.Add( self.m_single_checkbox, 0, wx.ALL, 5 )
		
		fgSizer38 = wx.FlexGridSizer( 0, 2, 0, 0 )
		fgSizer38.AddGrowableCol( 1 )
		fgSizer38.SetFlexibleDirection( wx.BOTH )
		fgSizer38.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_language_label = wx.StaticText( self.m_settings_panel, wx.ID_ANY, u"Language (restart required)", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_language_label.Wrap( -1 )
		fgSizer38.Add( self.m_language_label, 0, wx.ALL, 5 )
		
		m_lang_choiceChoices = []
		self.m_lang_choice = wx.Choice( self.m_settings_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_lang_choiceChoices, 0 )
		self.m_lang_choice.SetSelection( 0 )
		fgSizer38.Add( self.m_lang_choice, 0, wx.ALIGN_RIGHT|wx.ALL, 5 )
		
		
		sbSizer8.Add( fgSizer38, 1, wx.EXPAND, 5 )
		
		
		fgSizer17.Add( sbSizer8, 1, wx.EXPAND, 5 )
		
		sbSizer12 = wx.StaticBoxSizer( wx.StaticBox( self.m_settings_panel, wx.ID_ANY, u"Regular Expression Modules" ), wx.VERTICAL )
		
		fgSizer43 = wx.FlexGridSizer( 0, 2, 0, 0 )
		fgSizer43.AddGrowableCol( 0 )
		fgSizer43.SetFlexibleDirection( wx.BOTH )
		fgSizer43.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_re_radio = wx.RadioButton( self.m_settings_panel, wx.ID_ANY, u"Use re module", wx.DefaultPosition, wx.DefaultSize, wx.RB_GROUP )
		self.m_re_radio.SetValue( True ) 
		fgSizer43.Add( self.m_re_radio, 0, wx.ALL, 5 )
		
		
		fgSizer43.Add( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.m_bre_radio = wx.RadioButton( self.m_settings_panel, wx.ID_ANY, u"Use re module with backrefs", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer43.Add( self.m_bre_radio, 0, wx.ALL, 5 )
		
		
		fgSizer43.Add( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.m_regex_radio = wx.RadioButton( self.m_settings_panel, wx.ID_ANY, u"Use regex module", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_regex_radio.Enable( False )
		
		fgSizer43.Add( self.m_regex_radio, 0, wx.ALL, 5 )
		
		
		fgSizer43.Add( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.m_bregex_radio = wx.RadioButton( self.m_settings_panel, wx.ID_ANY, u"Use regex module with backrefs", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_bregex_radio.Enable( False )
		
		fgSizer43.Add( self.m_bregex_radio, 0, wx.ALL, 5 )
		
		
		fgSizer43.Add( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.m_regex_version_label = wx.StaticText( self.m_settings_panel, wx.ID_ANY, u"Regex module version to use", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_regex_version_label.Wrap( -1 )
		self.m_regex_version_label.Enable( False )
		
		fgSizer43.Add( self.m_regex_version_label, 0, wx.ALL, 5 )
		
		m_regex_ver_choiceChoices = [ u"V0", u"V1" ]
		self.m_regex_ver_choice = wx.Choice( self.m_settings_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_regex_ver_choiceChoices, 0 )
		self.m_regex_ver_choice.SetSelection( 0 )
		self.m_regex_ver_choice.Enable( False )
		
		fgSizer43.Add( self.m_regex_ver_choice, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )
		
		
		sbSizer12.Add( fgSizer43, 1, wx.EXPAND, 5 )
		
		
		fgSizer17.Add( sbSizer12, 1, wx.EXPAND, 5 )
		
		sbSizer101 = wx.StaticBoxSizer( wx.StaticBox( self.m_settings_panel, wx.ID_ANY, u"Notifications" ), wx.VERTICAL )
		
		fgSizer35 = wx.FlexGridSizer( 0, 2, 0, 0 )
		fgSizer35.AddGrowableCol( 1 )
		fgSizer35.SetFlexibleDirection( wx.BOTH )
		fgSizer35.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_visual_alert_checkbox = wx.CheckBox( self.m_settings_panel, wx.ID_ANY, u"Notification popup", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_visual_alert_checkbox.SetValue(True) 
		fgSizer35.Add( self.m_visual_alert_checkbox, 0, wx.ALL, 5 )
		
		m_notify_choiceChoices = []
		self.m_notify_choice = wx.Choice( self.m_settings_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_notify_choiceChoices, 0 )
		self.m_notify_choice.SetSelection( 0 )
		fgSizer35.Add( self.m_notify_choice, 0, wx.ALIGN_RIGHT|wx.ALL, 5 )
		
		self.m_audio_alert_checkbox = wx.CheckBox( self.m_settings_panel, wx.ID_ANY, u"Alert Sound", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_audio_alert_checkbox.SetValue(True) 
		fgSizer35.Add( self.m_audio_alert_checkbox, 0, wx.ALL, 5 )
		
		
		fgSizer35.Add( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.m_term_note_label = wx.StaticText( self.m_settings_panel, wx.ID_ANY, u"Path to terminal-notifier", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_term_note_label.Wrap( -1 )
		self.m_term_note_label.Enable( False )
		self.m_term_note_label.Hide()
		
		fgSizer35.Add( self.m_term_note_label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_term_note_picker = wx.FilePickerCtrl( self.m_settings_panel, wx.ID_ANY, wx.EmptyString, u"Select a file", u"*.*", wx.DefaultPosition, wx.DefaultSize, wx.FLP_DEFAULT_STYLE|wx.FLP_FILE_MUST_EXIST )
		self.m_term_note_picker.Enable( False )
		self.m_term_note_picker.Hide()
		
		fgSizer35.Add( self.m_term_note_picker, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		sbSizer101.Add( fgSizer35, 1, wx.EXPAND, 5 )
		
		
		fgSizer17.Add( sbSizer101, 1, wx.EXPAND, 5 )
		
		sbSizer10 = wx.StaticBoxSizer( wx.StaticBox( self.m_settings_panel, wx.ID_ANY, u"History" ), wx.VERTICAL )
		
		fgSizer30 = wx.FlexGridSizer( 0, 2, 0, 0 )
		fgSizer30.AddGrowableCol( 0 )
		fgSizer30.SetFlexibleDirection( wx.BOTH )
		fgSizer30.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_history_label = wx.StaticText( self.m_settings_panel, wx.ID_ANY, u"0 Records", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_history_label.Wrap( -1 )
		fgSizer30.Add( self.m_history_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.m_history_clear_button = wx.Button( self.m_settings_panel, wx.ID_ANY, u"Clear", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer30.Add( self.m_history_clear_button, 0, wx.ALIGN_RIGHT|wx.ALL, 5 )
		
		
		sbSizer10.Add( fgSizer30, 1, wx.EXPAND, 5 )
		
		
		fgSizer17.Add( sbSizer10, 1, wx.EXPAND, 5 )
		
		fgSizer22 = wx.FlexGridSizer( 0, 2, 0, 0 )
		fgSizer22.AddGrowableCol( 0 )
		fgSizer22.SetFlexibleDirection( wx.BOTH )
		fgSizer22.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		
		fgSizer22.Add( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.m_close_button = wx.Button( self.m_settings_panel, wx.ID_ANY, u"Close", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer22.Add( self.m_close_button, 0, wx.ALL, 5 )
		
		
		fgSizer17.Add( fgSizer22, 1, wx.EXPAND, 5 )
		
		
		self.m_settings_panel.SetSizer( fgSizer17 )
		self.m_settings_panel.Layout()
		fgSizer17.Fit( self.m_settings_panel )
		bSizer7.Add( self.m_settings_panel, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		self.SetSizer( bSizer7 )
		self.Layout()
		bSizer7.Fit( self )
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_editor_button.Bind( wx.EVT_BUTTON, self.on_editor_change )
		self.m_single_checkbox.Bind( wx.EVT_CHECKBOX, self.on_single_toggle )
		self.m_lang_choice.Bind( wx.EVT_CHOICE, self.on_language )
		self.m_re_radio.Bind( wx.EVT_RADIOBUTTON, self.on_re_toggle )
		self.m_bre_radio.Bind( wx.EVT_RADIOBUTTON, self.on_bre_toggle )
		self.m_regex_radio.Bind( wx.EVT_RADIOBUTTON, self.on_regex_toggle )
		self.m_bregex_radio.Bind( wx.EVT_RADIOBUTTON, self.on_bregex_toggle )
		self.m_regex_ver_choice.Bind( wx.EVT_CHOICE, self.on_regex_ver_choice )
		self.m_visual_alert_checkbox.Bind( wx.EVT_CHECKBOX, self.on_notify_toggle )
		self.m_notify_choice.Bind( wx.EVT_CHOICE, self.on_notify_choice )
		self.m_audio_alert_checkbox.Bind( wx.EVT_CHECKBOX, self.on_alert_toggle )
		self.m_term_note_picker.Bind( wx.EVT_FILEPICKER_CHANGED, self.on_term_note_change )
		self.m_history_clear_button.Bind( wx.EVT_BUTTON, self.on_clear_history )
		self.m_close_button.Bind( wx.EVT_BUTTON, self.on_cancel )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def on_editor_change( self, event ):
		event.Skip()
	
	def on_single_toggle( self, event ):
		event.Skip()
	
	def on_language( self, event ):
		event.Skip()
	
	def on_re_toggle( self, event ):
		event.Skip()
	
	def on_bre_toggle( self, event ):
		event.Skip()
	
	def on_regex_toggle( self, event ):
		event.Skip()
	
	def on_bregex_toggle( self, event ):
		event.Skip()
	
	def on_regex_ver_choice( self, event ):
		event.Skip()
	
	def on_notify_toggle( self, event ):
		event.Skip()
	
	def on_notify_choice( self, event ):
		event.Skip()
	
	def on_alert_toggle( self, event ):
		event.Skip()
	
	def on_term_note_change( self, event ):
		event.Skip()
	
	def on_clear_history( self, event ):
		event.Skip()
	
	def on_cancel( self, event ):
		event.Skip()
	

###########################################################################
## Class EditorDialog
###########################################################################

class EditorDialog ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Configure Editor", pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )
		
		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )
		
		bSizer6 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_editor_panel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.m_editor_panel.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )
		
		fgSizer14 = wx.FlexGridSizer( 4, 1, 0, 0 )
		fgSizer14.AddGrowableCol( 0 )
		fgSizer14.AddGrowableRow( 2 )
		fgSizer14.SetFlexibleDirection( wx.BOTH )
		fgSizer14.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_instructions_label = wx.StaticText( self.m_editor_panel, wx.ID_ANY, u"Select the application and then set the arguments.\n\nSpecial variables:\n{$file} --> file path\n{$line} --> line number\n{$col} --> column number", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTRE )
		self.m_instructions_label.Wrap( 325 )
		fgSizer14.Add( self.m_instructions_label, 1, wx.ALL|wx.EXPAND, 5 )
		
		sbSizer6 = wx.StaticBoxSizer( wx.StaticBox( self.m_editor_panel, wx.ID_ANY, u"Application" ), wx.VERTICAL )
		
		self.m_editor_picker = wx.FilePickerCtrl( self.m_editor_panel, wx.ID_ANY, wx.EmptyString, u"Select Editor", u"*.*", wx.DefaultPosition, wx.DefaultSize, wx.FLP_DEFAULT_STYLE )
		sbSizer6.Add( self.m_editor_picker, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		fgSizer14.Add( sbSizer6, 1, wx.EXPAND, 5 )
		
		sbSizer5 = wx.StaticBoxSizer( wx.StaticBox( self.m_editor_panel, wx.ID_ANY, u"Arguments" ), wx.VERTICAL )
		
		fgSizer15 = wx.FlexGridSizer( 2, 2, 0, 0 )
		fgSizer15.AddGrowableCol( 0 )
		fgSizer15.AddGrowableRow( 1 )
		fgSizer15.SetFlexibleDirection( wx.BOTH )
		fgSizer15.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_arg_text = wx.TextCtrl( self.m_editor_panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
		fgSizer15.Add( self.m_arg_text, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.m_add_arg_button = wx.Button( self.m_editor_panel, wx.ID_ANY, u"Add", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer15.Add( self.m_add_arg_button, 0, wx.ALL, 5 )
		
		m_arg_listChoices = []
		self.m_arg_list = wx.ListBox( self.m_editor_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_arg_listChoices, wx.LB_SINGLE )
		fgSizer15.Add( self.m_arg_list, 1, wx.ALL|wx.EXPAND, 5 )
		
		fgSizer23 = wx.FlexGridSizer( 0, 1, 0, 0 )
		fgSizer23.SetFlexibleDirection( wx.BOTH )
		fgSizer23.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_remove_arg_button = wx.Button( self.m_editor_panel, wx.ID_ANY, u"Delete", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer23.Add( self.m_remove_arg_button, 0, wx.ALL, 5 )
		
		self.m_edit_button = wx.Button( self.m_editor_panel, wx.ID_ANY, u"Edit", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer23.Add( self.m_edit_button, 0, wx.ALL, 5 )
		
		self.m_staticline2 = wx.StaticLine( self.m_editor_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		fgSizer23.Add( self.m_staticline2, 0, wx.EXPAND |wx.ALL, 5 )
		
		self.m_up_button = wx.Button( self.m_editor_panel, wx.ID_ANY, u"Up", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer23.Add( self.m_up_button, 0, wx.ALL, 5 )
		
		self.m_down_button = wx.Button( self.m_editor_panel, wx.ID_ANY, u"Down", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer23.Add( self.m_down_button, 0, wx.ALL, 5 )
		
		
		fgSizer15.Add( fgSizer23, 1, wx.EXPAND, 5 )
		
		
		sbSizer5.Add( fgSizer15, 1, wx.EXPAND, 5 )
		
		
		fgSizer14.Add( sbSizer5, 1, wx.EXPAND, 5 )
		
		fgSizer21 = wx.FlexGridSizer( 0, 4, 0, 0 )
		fgSizer21.AddGrowableCol( 0 )
		fgSizer21.AddGrowableCol( 3 )
		fgSizer21.SetFlexibleDirection( wx.BOTH )
		fgSizer21.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		
		fgSizer21.Add( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.m_apply_button = wx.Button( self.m_editor_panel, wx.ID_ANY, u"Apply", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer21.Add( self.m_apply_button, 0, wx.ALL, 5 )
		
		self.m_cancel_button = wx.Button( self.m_editor_panel, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer21.Add( self.m_cancel_button, 0, wx.ALL, 5 )
		
		
		fgSizer21.Add( ( 0, 0), 1, wx.EXPAND, 5 )
		
		
		fgSizer14.Add( fgSizer21, 1, wx.EXPAND, 5 )
		
		
		self.m_editor_panel.SetSizer( fgSizer14 )
		self.m_editor_panel.Layout()
		fgSizer14.Fit( self.m_editor_panel )
		bSizer6.Add( self.m_editor_panel, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		self.SetSizer( bSizer6 )
		self.Layout()
		bSizer6.Fit( self )
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_arg_text.Bind( wx.EVT_TEXT_ENTER, self.on_arg_enter )
		self.m_add_arg_button.Bind( wx.EVT_BUTTON, self.on_add )
		self.m_remove_arg_button.Bind( wx.EVT_BUTTON, self.on_remove )
		self.m_edit_button.Bind( wx.EVT_BUTTON, self.on_edit )
		self.m_up_button.Bind( wx.EVT_BUTTON, self.on_up )
		self.m_down_button.Bind( wx.EVT_BUTTON, self.on_down )
		self.m_apply_button.Bind( wx.EVT_BUTTON, self.on_apply )
		self.m_cancel_button.Bind( wx.EVT_BUTTON, self.on_cancel )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def on_arg_enter( self, event ):
		event.Skip()
	
	def on_add( self, event ):
		event.Skip()
	
	def on_remove( self, event ):
		event.Skip()
	
	def on_edit( self, event ):
		event.Skip()
	
	def on_up( self, event ):
		event.Skip()
	
	def on_down( self, event ):
		event.Skip()
	
	def on_apply( self, event ):
		event.Skip()
	
	def on_cancel( self, event ):
		event.Skip()
	

###########################################################################
## Class ArgDialog
###########################################################################

class ArgDialog ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Edit Argument", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )
		
		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )
		
		bSizer9 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_arg_panel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.m_arg_panel.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )
		
		fgSizer24 = wx.FlexGridSizer( 0, 1, 0, 0 )
		fgSizer24.AddGrowableCol( 0 )
		fgSizer24.SetFlexibleDirection( wx.BOTH )
		fgSizer24.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_arg_text = wx.TextCtrl( self.m_arg_panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer24.Add( self.m_arg_text, 1, wx.ALL|wx.EXPAND, 5 )
		
		fgSizer25 = wx.FlexGridSizer( 0, 4, 0, 0 )
		fgSizer25.AddGrowableCol( 0 )
		fgSizer25.AddGrowableCol( 3 )
		fgSizer25.SetFlexibleDirection( wx.BOTH )
		fgSizer25.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		
		fgSizer25.Add( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.m_apply_button = wx.Button( self.m_arg_panel, wx.ID_ANY, u"Apply", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer25.Add( self.m_apply_button, 0, wx.ALL, 5 )
		
		self.m_cancel_button = wx.Button( self.m_arg_panel, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer25.Add( self.m_cancel_button, 0, wx.ALL, 5 )
		
		
		fgSizer25.Add( ( 0, 0), 1, wx.EXPAND, 5 )
		
		
		fgSizer24.Add( fgSizer25, 1, wx.EXPAND, 5 )
		
		
		self.m_arg_panel.SetSizer( fgSizer24 )
		self.m_arg_panel.Layout()
		fgSizer24.Fit( self.m_arg_panel )
		bSizer9.Add( self.m_arg_panel, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		self.SetSizer( bSizer9 )
		self.Layout()
		bSizer9.Fit( self )
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_apply_button.Bind( wx.EVT_BUTTON, self.on_apply )
		self.m_cancel_button.Bind( wx.EVT_BUTTON, self.on_cancel )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def on_apply( self, event ):
		event.Skip()
	
	def on_cancel( self, event ):
		event.Skip()
	

###########################################################################
## Class SaveSearchDialog
###########################################################################

class SaveSearchDialog ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Search Name", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )
		
		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )
		
		bSizer9 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_save_panel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.m_save_panel.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )
		
		fgSizer24 = wx.FlexGridSizer( 0, 1, 0, 0 )
		fgSizer24.AddGrowableCol( 0 )
		fgSizer24.SetFlexibleDirection( wx.BOTH )
		fgSizer24.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer34 = wx.FlexGridSizer( 0, 2, 0, 0 )
		fgSizer34.AddGrowableCol( 1 )
		fgSizer34.SetFlexibleDirection( wx.BOTH )
		fgSizer34.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_name_label = wx.StaticText( self.m_save_panel, wx.ID_ANY, u"Name", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_name_label.Wrap( -1 )
		fgSizer34.Add( self.m_name_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.m_name_text = wx.TextCtrl( self.m_save_panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer34.Add( self.m_name_text, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		fgSizer24.Add( fgSizer34, 1, wx.EXPAND, 5 )
		
		fgSizer25 = wx.FlexGridSizer( 0, 4, 0, 0 )
		fgSizer25.AddGrowableCol( 0 )
		fgSizer25.AddGrowableCol( 3 )
		fgSizer25.SetFlexibleDirection( wx.BOTH )
		fgSizer25.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		
		fgSizer25.Add( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.m_apply_button = wx.Button( self.m_save_panel, wx.ID_ANY, u"Save", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer25.Add( self.m_apply_button, 0, wx.ALL, 5 )
		
		self.m_cancel_button = wx.Button( self.m_save_panel, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer25.Add( self.m_cancel_button, 0, wx.ALL, 5 )
		
		
		fgSizer25.Add( ( 0, 0), 1, wx.EXPAND, 5 )
		
		
		fgSizer24.Add( fgSizer25, 1, wx.EXPAND, 5 )
		
		
		self.m_save_panel.SetSizer( fgSizer24 )
		self.m_save_panel.Layout()
		fgSizer24.Fit( self.m_save_panel )
		bSizer9.Add( self.m_save_panel, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		self.SetSizer( bSizer9 )
		self.Layout()
		bSizer9.Fit( self )
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_apply_button.Bind( wx.EVT_BUTTON, self.on_apply )
		self.m_cancel_button.Bind( wx.EVT_BUTTON, self.on_cancel )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def on_apply( self, event ):
		event.Skip()
	
	def on_cancel( self, event ):
		event.Skip()
	

###########################################################################
## Class AboutDialog
###########################################################################

class AboutDialog ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"About", pos = wx.DefaultPosition, size = wx.Size( 300,-1 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )
		
		bSizer12 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_about_panel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.m_about_panel.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )
		
		fgSizer33 = wx.FlexGridSizer( 0, 2, 0, 0 )
		fgSizer33.AddGrowableCol( 1 )
		fgSizer33.SetFlexibleDirection( wx.BOTH )
		fgSizer33.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_bitmap = wx.StaticBitmap( self.m_about_panel, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size( 64,64 ), 0 )
		fgSizer33.Add( self.m_bitmap, 0, wx.ALL, 5 )
		
		fgSizer34 = wx.FlexGridSizer( 0, 1, 0, 0 )
		fgSizer34.AddGrowableCol( 0 )
		fgSizer34.SetFlexibleDirection( wx.BOTH )
		fgSizer34.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_app_label = wx.StaticText( self.m_about_panel, wx.ID_ANY, u"Rummage", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTRE )
		self.m_app_label.Wrap( -1 )
		self.m_app_label.SetFont( wx.Font( 20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )
		
		fgSizer34.Add( self.m_app_label, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_version_label = wx.StaticText( self.m_about_panel, wx.ID_ANY, u"Version", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTRE )
		self.m_version_label.Wrap( -1 )
		fgSizer34.Add( self.m_version_label, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_dev_toggle = wx.ToggleButton( self.m_about_panel, wx.ID_ANY, u"Contact >>", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer34.Add( self.m_dev_toggle, 0, wx.ALL, 5 )
		
		self.m_staticline4 = wx.StaticLine( self.m_about_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		fgSizer34.Add( self.m_staticline4, 0, wx.EXPAND |wx.ALL, 5 )
		
		self.m_developers_label = wx.StaticText( self.m_about_panel, wx.ID_ANY, u"Dev", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTRE )
		self.m_developers_label.Wrap( -1 )
		self.m_developers_label.Hide()
		
		fgSizer34.Add( self.m_developers_label, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		fgSizer33.Add( fgSizer34, 1, wx.EXPAND, 5 )
		
		
		fgSizer33.Add( ( 64, 0), 1, wx.EXPAND, 5 )
		
		
		fgSizer33.Add( ( 0, 0), 1, wx.EXPAND, 5 )
		
		
		self.m_about_panel.SetSizer( fgSizer33 )
		self.m_about_panel.Layout()
		fgSizer33.Fit( self.m_about_panel )
		bSizer12.Add( self.m_about_panel, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		self.SetSizer( bSizer12 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_dev_toggle.Bind( wx.EVT_TOGGLEBUTTON, self.on_toggle )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def on_toggle( self, event ):
		event.Skip()
	

###########################################################################
## Class SearchErrorDialog
###########################################################################

class SearchErrorDialog ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Errors", pos = wx.DefaultPosition, size = wx.Size( 470,288 ), style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )
		
		self.SetSizeHints( wx.Size( 470,288 ), wx.DefaultSize )
		
		bSizer13 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_error_panel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		fgSizer40 = wx.FlexGridSizer( 1, 1, 0, 0 )
		fgSizer40.AddGrowableCol( 0 )
		fgSizer40.AddGrowableRow( 0 )
		fgSizer40.SetFlexibleDirection( wx.BOTH )
		fgSizer40.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_error_list = ErrorList(self.m_error_panel)
		fgSizer40.Add( self.m_error_list, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		self.m_error_panel.SetSizer( fgSizer40 )
		self.m_error_panel.Layout()
		fgSizer40.Fit( self.m_error_panel )
		bSizer13.Add( self.m_error_panel, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		self.SetSizer( bSizer13 )
		self.Layout()
		
		self.Centre( wx.BOTH )
	
	def __del__( self ):
		pass
	

###########################################################################
## Class ErrorTextDialog
###########################################################################

class ErrorTextDialog ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Error", pos = wx.DefaultPosition, size = wx.Size( 470,288 ), style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )
		
		self.SetSizeHints( wx.Size( 470,288 ), wx.DefaultSize )
		
		bSizer14 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_error_text_panel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer15 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_error_textbox = wx.TextCtrl( self.m_error_text_panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.TE_MULTILINE )
		bSizer15.Add( self.m_error_textbox, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		self.m_error_text_panel.SetSizer( bSizer15 )
		self.m_error_text_panel.Layout()
		bSizer15.Fit( self.m_error_text_panel )
		bSizer14.Add( self.m_error_text_panel, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		self.SetSizer( bSizer14 )
		self.Layout()
		
		self.Centre( wx.BOTH )
	
	def __del__( self ):
		pass
