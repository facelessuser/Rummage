# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Oct 26 2018)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
from .controls.autocomplete_combo import AutoCompleteCombo
from .controls.date_picker import DatePicker
from wx.lib.masked import TimeCtrl
from .controls.result_lists import ResultFileList
from .controls.result_lists import ResultContentList
from .controls.encoding_list import EncodingList
from .controls.load_search_list import SavedSearchList
from .controls.search_chain_list import SearchChainList
from .controls.search_error_list import ErrorList
import wx.html2
from .controls.collapsible_pane import CollapsiblePane

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
        fgSizer13 = wx.FlexGridSizer( 1, 1, 0, 0 )
        fgSizer13.AddGrowableCol( 0 )
        fgSizer13.AddGrowableRow( 0 )
        fgSizer13.SetFlexibleDirection( wx.BOTH )
        fgSizer13.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_grep_notebook = wx.Notebook( self.m_main_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.NB_FIXEDWIDTH|wx.NB_NOPAGETHEME )
        self.m_grep_notebook.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )

        self.m_settings_panel = wx.Panel( self.m_grep_notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.m_settings_panel.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )

        bSizer10 = wx.BoxSizer( wx.VERTICAL )

        fgSizer2 = wx.FlexGridSizer( 8, 1, 0, 0 )
        fgSizer2.AddGrowableCol( 0 )
        fgSizer2.SetFlexibleDirection( wx.BOTH )
        fgSizer2.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        fgSizer8 = wx.FlexGridSizer( 0, 3, 0, 0 )
        fgSizer8.AddGrowableCol( 1 )
        fgSizer8.SetFlexibleDirection( wx.HORIZONTAL )
        fgSizer8.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_searchin_label = wx.StaticText( self.m_settings_panel, wx.ID_ANY, u"Search in", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_searchin_label.Wrap( -1 )

        fgSizer8.Add( self.m_searchin_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.ALIGN_RIGHT, 5 )

        self.m_searchin_text = AutoCompleteCombo(self.m_settings_panel, wx.ID_ANY)
        fgSizer8.Add( self.m_searchin_text, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.m_searchin_dir_picker = wx.Button( self.m_settings_panel, wx.ID_ANY, u"...", wx.DefaultPosition, wx.Size( -1,-1 ), wx.BU_EXACTFIT )
        fgSizer8.Add( self.m_searchin_dir_picker, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.m_searchfor_label = wx.StaticText( self.m_settings_panel, wx.ID_ANY, u"Search for", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_searchfor_label.Wrap( -1 )

        fgSizer8.Add( self.m_searchfor_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.ALIGN_RIGHT, 5 )

        self.m_searchfor_textbox = AutoCompleteCombo(self.m_settings_panel, wx.ID_ANY)
        fgSizer8.Add( self.m_searchfor_textbox, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5 )


        fgSizer8.Add( ( 0, 0), 1, wx.EXPAND, 5 )

        self.m_replace_label = wx.StaticText( self.m_settings_panel, wx.ID_ANY, u"Replace with", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_replace_label.Wrap( -1 )

        fgSizer8.Add( self.m_replace_label, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )

        self.m_replace_textbox = AutoCompleteCombo(self.m_settings_panel, wx.ID_ANY)
        fgSizer8.Add( self.m_replace_textbox, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.m_replace_plugin_dir_picker = wx.Button( self.m_settings_panel, wx.ID_ANY, u"...", wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT )
        fgSizer8.Add( self.m_replace_plugin_dir_picker, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


        fgSizer2.Add( fgSizer8, 1, wx.EXPAND, 5 )

        self.m_options_collapse = CollapsiblePane( self.m_settings_panel, wx.ID_ANY, u"Text search options", wx.DefaultPosition, wx.DefaultSize, wx.CP_DEFAULT_STYLE|wx.CP_NO_TLW_RESIZE )
        self.m_options_collapse.Collapse( False )

        self.m_options_collapse.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )

        bSizer23 = wx.BoxSizer( wx.VERTICAL )

        self.m_options_panel = wx.Panel( self.m_options_collapse.GetPane(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.m_options_panel.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )

        fgSizer9 = wx.FlexGridSizer( 0, 3, 0, 0 )
        fgSizer9.AddGrowableCol( 0 )
        fgSizer9.AddGrowableCol( 2 )
        fgSizer9.SetFlexibleDirection( wx.HORIZONTAL )
        fgSizer9.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )


        fgSizer9.Add( ( 0, 0), 1, wx.EXPAND, 5 )

        gbSizer2 = wx.GridBagSizer( 0, 0 )
        gbSizer2.SetFlexibleDirection( wx.BOTH )
        gbSizer2.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        gbSizer2.SetEmptyCellSize( wx.Size( -1,0 ) )

        self.m_regex_search_checkbox = wx.CheckBox( self.m_options_panel, wx.ID_ANY, u"Search with regex", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_regex_search_checkbox.SetValue(True)
        gbSizer2.Add( self.m_regex_search_checkbox, wx.GBPosition( 0, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_case_checkbox = wx.CheckBox( self.m_options_panel, wx.ID_ANY, u"Search case-sensitive", wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer2.Add( self.m_case_checkbox, wx.GBPosition( 0, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_dotmatch_checkbox = wx.CheckBox( self.m_options_panel, wx.ID_ANY, u"Dot matches newline", wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer2.Add( self.m_dotmatch_checkbox, wx.GBPosition( 0, 2 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_unicode_checkbox = wx.CheckBox( self.m_options_panel, wx.ID_ANY, u"Use Unicode properties", wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer2.Add( self.m_unicode_checkbox, wx.GBPosition( 0, 3 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_format_replace_checkbox = wx.CheckBox( self.m_options_panel, wx.ID_ANY, u"Format style replacements", wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer2.Add( self.m_format_replace_checkbox, wx.GBPosition( 1, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_bestmatch_checkbox = wx.CheckBox( self.m_options_panel, wx.ID_ANY, u"Best fuzzy match", wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer2.Add( self.m_bestmatch_checkbox, wx.GBPosition( 1, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_enhancematch_checkbox = wx.CheckBox( self.m_options_panel, wx.ID_ANY, u"Improve fuzzy fit", wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer2.Add( self.m_enhancematch_checkbox, wx.GBPosition( 1, 2 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_word_checkbox = wx.CheckBox( self.m_options_panel, wx.ID_ANY, u"Unicode word breaks", wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer2.Add( self.m_word_checkbox, wx.GBPosition( 1, 3 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_reverse_checkbox = wx.CheckBox( self.m_options_panel, wx.ID_ANY, u"Search backwards", wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer2.Add( self.m_reverse_checkbox, wx.GBPosition( 2, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_posix_checkbox = wx.CheckBox( self.m_options_panel, wx.ID_ANY, u"Use POSIX matching", wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer2.Add( self.m_posix_checkbox, wx.GBPosition( 2, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_fullcase_checkbox = wx.CheckBox( self.m_options_panel, wx.ID_ANY, u"Full case-folding", wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer2.Add( self.m_fullcase_checkbox, wx.GBPosition( 2, 2 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticline11 = wx.StaticLine( self.m_options_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        gbSizer2.Add( self.m_staticline11, wx.GBPosition( 3, 0 ), wx.GBSpan( 1, 4 ), wx.EXPAND |wx.ALL, 5 )

        self.m_boolean_checkbox = wx.CheckBox( self.m_options_panel, wx.ID_ANY, u"Boolean match", wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer2.Add( self.m_boolean_checkbox, wx.GBPosition( 4, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_count_only_checkbox = wx.CheckBox( self.m_options_panel, wx.ID_ANY, u"Count only", wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer2.Add( self.m_count_only_checkbox, wx.GBPosition( 4, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_backup_checkbox = wx.CheckBox( self.m_options_panel, wx.ID_ANY, u"Create backups", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_backup_checkbox.SetValue(True)
        gbSizer2.Add( self.m_backup_checkbox, wx.GBPosition( 4, 2 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        fgSizer40 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer40.SetFlexibleDirection( wx.BOTH )
        fgSizer40.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_NONE )

        self.m_force_encode_checkbox = wx.CheckBox( self.m_options_panel, wx.ID_ANY, u"Force", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer40.Add( self.m_force_encode_checkbox, 0, wx.ALL, 5 )

        m_force_encode_choiceChoices = []
        self.m_force_encode_choice = wx.Choice( self.m_options_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_force_encode_choiceChoices, 0 )
        self.m_force_encode_choice.SetSelection( 0 )
        fgSizer40.Add( self.m_force_encode_choice, 0, wx.ALL|wx.EXPAND, 5 )


        gbSizer2.Add( fgSizer40, wx.GBPosition( 4, 3 ), wx.GBSpan( 1, 1 ), wx.EXPAND, 5 )

        self.m_chains_checkbox = wx.CheckBox( self.m_options_panel, wx.ID_ANY, u"Use chain search", wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer2.Add( self.m_chains_checkbox, wx.GBPosition( 5, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_replace_plugin_checkbox = wx.CheckBox( self.m_options_panel, wx.ID_ANY, u"Use plugin replace", wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer2.Add( self.m_replace_plugin_checkbox, wx.GBPosition( 5, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )


        fgSizer9.Add( gbSizer2, 1, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 5 )


        fgSizer9.Add( ( 0, 0), 1, wx.EXPAND, 5 )


        self.m_options_panel.SetSizer( fgSizer9 )
        self.m_options_panel.Layout()
        fgSizer9.Fit( self.m_options_panel )
        bSizer23.Add( self.m_options_panel, 1, wx.EXPAND |wx.ALL, 5 )


        self.m_options_collapse.GetPane().SetSizer( bSizer23 )
        self.m_options_collapse.GetPane().Layout()
        bSizer23.Fit( self.m_options_collapse.GetPane() )
        fgSizer2.Add( self.m_options_collapse, 0, wx.EXPAND |wx.ALL, 5 )

        self.m_staticline3 = wx.StaticLine( self.m_settings_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer2.Add( self.m_staticline3, 0, wx.EXPAND |wx.ALL, 5 )

        fgSizer17 = wx.FlexGridSizer( 0, 5, 0, 0 )
        fgSizer17.AddGrowableCol( 1 )
        fgSizer17.SetFlexibleDirection( wx.BOTH )
        fgSizer17.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_regex_test_button = wx.Button( self.m_settings_panel, wx.ID_ANY, u"Test Regex", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer17.Add( self.m_regex_test_button, 0, wx.ALL, 5 )


        fgSizer17.Add( ( 0, 0), 1, wx.EXPAND, 5 )

        self.m_chain_button = wx.Button( self.m_settings_panel, wx.ID_ANY, u"Search Chains", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer17.Add( self.m_chain_button, 0, wx.ALL, 5 )

        self.m_save_search_button = wx.Button( self.m_settings_panel, wx.ID_ANY, u"Save Search", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer17.Add( self.m_save_search_button, 0, wx.ALL, 5 )

        self.m_load_search_button = wx.Button( self.m_settings_panel, wx.ID_ANY, u"Load Search", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer17.Add( self.m_load_search_button, 0, wx.ALL, 5 )


        fgSizer2.Add( fgSizer17, 1, wx.EXPAND, 5 )

        self.m_staticline111 = wx.StaticLine( self.m_settings_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer2.Add( self.m_staticline111, 0, wx.EXPAND |wx.ALL, 5 )

        self.m_limit_collapse = CollapsiblePane( self.m_settings_panel, wx.ID_ANY, u"File search", wx.DefaultPosition, wx.DefaultSize, wx.CP_DEFAULT_STYLE|wx.CP_NO_TLW_RESIZE )
        self.m_limit_collapse.Collapse( False )

        self.m_limit_collapse.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )

        bSizer26 = wx.BoxSizer( wx.VERTICAL )

        self.m_limit_panel = wx.Panel( self.m_limit_collapse.GetPane(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.m_limit_panel.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )

        gbSizer3 = wx.GridBagSizer( 0, 0 )
        gbSizer3.SetFlexibleDirection( wx.BOTH )
        gbSizer3.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_size_is_label = wx.StaticText( self.m_limit_panel, wx.ID_ANY, u"Size is", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_size_is_label.Wrap( -1 )

        gbSizer3.Add( self.m_size_is_label, wx.GBPosition( 0, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )

        m_logic_choiceChoices = [ u"any", u"greater than", u"equal to", u"less than" ]
        self.m_logic_choice = wx.Choice( self.m_limit_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_logic_choiceChoices, 0 )
        self.m_logic_choice.SetSelection( 0 )
        gbSizer3.Add( self.m_logic_choice, wx.GBPosition( 0, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        fgSizer37 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer37.SetFlexibleDirection( wx.HORIZONTAL )
        fgSizer37.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_size_text = wx.TextCtrl( self.m_limit_panel, wx.ID_ANY, u"1000", wx.DefaultPosition, wx.Size( -1,-1 ), 0 )
        fgSizer37.Add( self.m_size_text, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.m_size_type_label = wx.StaticText( self.m_limit_panel, wx.ID_ANY, u"KB", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_size_type_label.Wrap( -1 )

        fgSizer37.Add( self.m_size_type_label, 0, wx.BOTTOM|wx.RIGHT|wx.TOP|wx.ALIGN_CENTER_VERTICAL, 5 )


        gbSizer3.Add( fgSizer37, wx.GBPosition( 0, 2 ), wx.GBSpan( 1, 3 ), wx.EXPAND, 5 )

        self.m_exclude_label = wx.StaticText( self.m_limit_panel, wx.ID_ANY, u"Exclude folders", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_exclude_label.Wrap( -1 )

        gbSizer3.Add( self.m_exclude_label, wx.GBPosition( 0, 6 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )

        self.m_exclude_textbox = AutoCompleteCombo(self.m_limit_panel, wx.ID_ANY)
        gbSizer3.Add( self.m_exclude_textbox, wx.GBPosition( 0, 7 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5 )

        self.m_dirregex_checkbox = wx.CheckBox( self.m_limit_panel, wx.ID_ANY, u"Regex", wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer3.Add( self.m_dirregex_checkbox, wx.GBPosition( 0, 8 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.m_modified_label = wx.StaticText( self.m_limit_panel, wx.ID_ANY, u"Modified", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_modified_label.Wrap( -1 )

        gbSizer3.Add( self.m_modified_label, wx.GBPosition( 1, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )

        m_modified_choiceChoices = [ u"on any", u"after", u"on", u"before" ]
        self.m_modified_choice = wx.Choice( self.m_limit_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_modified_choiceChoices, 0 )
        self.m_modified_choice.SetSelection( 0 )
        gbSizer3.Add( self.m_modified_choice, wx.GBPosition( 1, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5 )

        self.m_modified_date_picker = DatePicker(self.m_limit_panel, wx.ID_ANY)
        gbSizer3.Add( self.m_modified_date_picker, wx.GBPosition( 1, 2 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5 )

        self.m_modified_time_picker = TimeCtrl(self.m_limit_panel, wx.ID_ANY, style=wx.TE_PROCESS_TAB, oob_color="white", fmt24hr=True)
        gbSizer3.Add( self.m_modified_time_picker, wx.GBPosition( 1, 3 ), wx.GBSpan( 1, 1 ), wx.BOTTOM|wx.LEFT|wx.TOP|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.m_modified_spin = wx.SpinButton( self.m_limit_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer3.Add( self.m_modified_spin, wx.GBPosition( 1, 4 ), wx.GBSpan( 1, 1 ), wx.TOP|wx.BOTTOM|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.m_filematch_label = wx.StaticText( self.m_limit_panel, wx.ID_ANY, u"Files which match", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_filematch_label.Wrap( -1 )

        gbSizer3.Add( self.m_filematch_label, wx.GBPosition( 1, 6 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )

        self.m_filematch_textbox = AutoCompleteCombo(self.m_limit_panel, wx.ID_ANY)
        gbSizer3.Add( self.m_filematch_textbox, wx.GBPosition( 1, 7 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5 )

        self.m_fileregex_checkbox = wx.CheckBox( self.m_limit_panel, wx.ID_ANY, u"Regex", wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer3.Add( self.m_fileregex_checkbox, wx.GBPosition( 1, 8 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.m_created_label = wx.StaticText( self.m_limit_panel, wx.ID_ANY, u"Created", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_created_label.Wrap( -1 )

        gbSizer3.Add( self.m_created_label, wx.GBPosition( 2, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )

        m_created_choiceChoices = [ u"on any", u"after", u"on", u"before" ]
        self.m_created_choice = wx.Choice( self.m_limit_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_created_choiceChoices, 0 )
        self.m_created_choice.SetSelection( 0 )
        gbSizer3.Add( self.m_created_choice, wx.GBPosition( 2, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5 )

        self.m_created_date_picker = DatePicker(self.m_limit_panel, wx.ID_ANY)
        gbSizer3.Add( self.m_created_date_picker, wx.GBPosition( 2, 2 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5 )

        self.m_created_time_picker = TimeCtrl(self.m_limit_panel, wx.ID_ANY, style=wx.TE_PROCESS_TAB, oob_color="white", fmt24hr=True)
        gbSizer3.Add( self.m_created_time_picker, wx.GBPosition( 2, 3 ), wx.GBSpan( 1, 1 ), wx.BOTTOM|wx.LEFT|wx.TOP|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.m_created_spin = wx.SpinButton( self.m_limit_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer3.Add( self.m_created_spin, wx.GBPosition( 2, 4 ), wx.GBSpan( 1, 1 ), wx.TOP|wx.BOTTOM|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.m_staticline41 = wx.StaticLine( self.m_limit_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_VERTICAL )
        gbSizer3.Add( self.m_staticline41, wx.GBPosition( 0, 5 ), wx.GBSpan( 3, 1 ), wx.EXPAND |wx.ALL, 5 )

        fgSizer32 = wx.FlexGridSizer( 0, 6, 0, 0 )
        fgSizer32.AddGrowableCol( 0 )
        fgSizer32.AddGrowableCol( 5 )
        fgSizer32.SetFlexibleDirection( wx.HORIZONTAL )
        fgSizer32.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )


        fgSizer32.Add( ( 0, 0), 1, wx.EXPAND, 5 )

        self.m_subfolder_checkbox = wx.CheckBox( self.m_limit_panel, wx.ID_ANY, u"Include subfolders", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_subfolder_checkbox.SetValue(True)
        fgSizer32.Add( self.m_subfolder_checkbox, 0, wx.ALL, 5 )

        self.m_hidden_checkbox = wx.CheckBox( self.m_limit_panel, wx.ID_ANY, u"Include hidden", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer32.Add( self.m_hidden_checkbox, 0, wx.ALL, 5 )

        self.m_symlinks_checkbox = wx.CheckBox( self.m_limit_panel, wx.ID_ANY, u"Follow symlinks", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer32.Add( self.m_symlinks_checkbox, 0, wx.ALL, 5 )

        self.m_binary_checkbox = wx.CheckBox( self.m_limit_panel, wx.ID_ANY, u"Include binary files", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer32.Add( self.m_binary_checkbox, 0, wx.ALL, 5 )


        fgSizer32.Add( ( 0, 0), 1, wx.EXPAND, 5 )


        gbSizer3.Add( fgSizer32, wx.GBPosition( 3, 0 ), wx.GBSpan( 1, 9 ), wx.EXPAND, 5 )


        gbSizer3.AddGrowableCol( 7 )
        gbSizer3.AddGrowableRow( 0 )
        gbSizer3.AddGrowableRow( 1 )
        gbSizer3.AddGrowableRow( 2 )
        gbSizer3.AddGrowableRow( 3 )

        self.m_limit_panel.SetSizer( gbSizer3 )
        self.m_limit_panel.Layout()
        gbSizer3.Fit( self.m_limit_panel )
        bSizer26.Add( self.m_limit_panel, 1, wx.EXPAND |wx.ALL, 5 )


        self.m_limit_collapse.GetPane().SetSizer( bSizer26 )
        self.m_limit_collapse.GetPane().Layout()
        bSizer26.Fit( self.m_limit_collapse.GetPane() )
        fgSizer2.Add( self.m_limit_collapse, 0, wx.EXPAND |wx.ALL, 5 )

        self.m_staticline12 = wx.StaticLine( self.m_settings_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer2.Add( self.m_staticline12, 0, wx.EXPAND |wx.ALL, 5 )

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

        self.m_file_menu.AppendSubMenu( self.m_export_submenuitem, u"Export Results" )

        self.m_file_menu.AppendSeparator()

        self.m_export_settings_menuitem = wx.MenuItem( self.m_file_menu, wx.ID_ANY, u"Export Settings", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_file_menu.Append( self.m_export_settings_menuitem )

        self.m_import_settings_menuitem = wx.MenuItem( self.m_file_menu, wx.ID_ANY, u"Import Settings", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_file_menu.Append( self.m_import_settings_menuitem )

        self.m_file_menu.AppendSeparator()

        self.m_quit_menuitem = wx.MenuItem( self.m_file_menu, wx.ID_EXit, u"&Exit", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_file_menu.Append( self.m_quit_menuitem )

        self.m_menu.Append( self.m_file_menu, u"File" )

        self.m_help_menu = wx.Menu()
        self.m_about_menuitem = wx.MenuItem( self.m_help_menu, wx.ID_ABOUT, u"&About Rummage", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_help_menu.Append( self.m_about_menuitem )

        self.m_update_menuitem = wx.MenuItem( self.m_help_menu, wx.ID_ANY, u"Check for Updates", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_help_menu.Append( self.m_update_menuitem )

        self.m_help_menu.AppendSeparator()

        self.m_documentation_menuitem = wx.MenuItem( self.m_help_menu, wx.ID_ANY, u"Documentation", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_help_menu.Append( self.m_documentation_menuitem )

        self.m_changelog_menuitem = wx.MenuItem( self.m_help_menu, wx.ID_ANY, u"Changelog", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_help_menu.Append( self.m_changelog_menuitem )

        self.m_license_menuitem = wx.MenuItem( self.m_help_menu, wx.ID_ANY, u"License", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_help_menu.Append( self.m_license_menuitem )

        self.m_support_info_menuitem = wx.MenuItem( self.m_help_menu, wx.ID_ANY, u"Support Info", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_help_menu.Append( self.m_support_info_menuitem )

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
        self.m_grep_notebook.Bind( wx.EVT_NOTEBOOK_PAGE_CHANGED, self.on_notebook_changed )
        self.m_options_collapse.Bind( wx.EVT_COLLAPSIBLEPANE_CHANGED, self.on_options_collapse )
        self.m_regex_search_checkbox.Bind( wx.EVT_CHECKBOX, self.on_regex_search_toggle )
        self.m_chains_checkbox.Bind( wx.EVT_CHECKBOX, self.on_chain_toggle )
        self.m_replace_plugin_checkbox.Bind( wx.EVT_CHECKBOX, self.on_plugin_function_toggle )
        self.m_regex_test_button.Bind( wx.EVT_BUTTON, self.on_test_regex )
        self.m_chain_button.Bind( wx.EVT_BUTTON, self.on_chain_click )
        self.m_save_search_button.Bind( wx.EVT_BUTTON, self.on_save_search )
        self.m_load_search_button.Bind( wx.EVT_BUTTON, self.on_load_search )
        self.m_limit_collapse.Bind( wx.EVT_COLLAPSIBLEPANE_CHANGED, self.on_limit_collapse )
        self.m_dirregex_checkbox.Bind( wx.EVT_CHECKBOX, self.on_dirregex_toggle )
        self.m_fileregex_checkbox.Bind( wx.EVT_CHECKBOX, self.on_fileregex_toggle )
        self.m_replace_button.Bind( wx.EVT_BUTTON, self.on_replace_click )
        self.m_search_button.Bind( wx.EVT_BUTTON, self.on_search_click )
        self.Bind( wx.EVT_MENU, self.on_preferences, id = self.m_preferences_menuitem.GetId() )
        self.Bind( wx.EVT_MENU, self.on_export_html, id = self.m_export_html_menuitem.GetId() )
        self.Bind( wx.EVT_MENU, self.on_export_csv, id = self.m_export_csv_menuitem.GetId() )
        self.Bind( wx.EVT_MENU, self.on_export_settings, id = self.m_export_settings_menuitem.GetId() )
        self.Bind( wx.EVT_MENU, self.on_import_settings, id = self.m_import_settings_menuitem.GetId() )
        self.Bind( wx.EVT_MENU, self.on_exit, id = self.m_quit_menuitem.GetId() )
        self.Bind( wx.EVT_MENU, self.on_about, id = self.m_about_menuitem.GetId() )
        self.Bind( wx.EVT_MENU, self.on_check_update, id = self.m_update_menuitem.GetId() )
        self.Bind( wx.EVT_MENU, self.on_documentation, id = self.m_documentation_menuitem.GetId() )
        self.Bind( wx.EVT_MENU, self.on_changelog, id = self.m_changelog_menuitem.GetId() )
        self.Bind( wx.EVT_MENU, self.on_license, id = self.m_license_menuitem.GetId() )
        self.Bind( wx.EVT_MENU, self.on_support, id = self.m_support_info_menuitem.GetId() )
        self.Bind( wx.EVT_MENU, self.on_issues, id = self.m_issues_menuitem.GetId() )
        self.Bind( wx.EVT_MENU, self.on_show_log_file, id = self.m_log_menuitem.GetId() )

    def __del__( self ):
        pass


    # Virtual event handlers, overide them in your derived class
    def on_close( self, event ):
        event.Skip()

    def on_notebook_changed( self, event ):
        event.Skip()

    def on_options_collapse( self, event ):
        event.Skip()

    def on_regex_search_toggle( self, event ):
        event.Skip()

    def on_chain_toggle( self, event ):
        event.Skip()

    def on_plugin_function_toggle( self, event ):
        event.Skip()

    def on_test_regex( self, event ):
        event.Skip()

    def on_chain_click( self, event ):
        event.Skip()

    def on_save_search( self, event ):
        event.Skip()

    def on_load_search( self, event ):
        event.Skip()

    def on_limit_collapse( self, event ):
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

    def on_export_settings( self, event ):
        event.Skip()

    def on_import_settings( self, event ):
        event.Skip()

    def on_exit( self, event ):
        event.Skip()

    def on_about( self, event ):
        event.Skip()

    def on_check_update( self, event ):
        event.Skip()

    def on_documentation( self, event ):
        event.Skip()

    def on_changelog( self, event ):
        event.Skip()

    def on_license( self, event ):
        event.Skip()

    def on_support( self, event ):
        event.Skip()

    def on_issues( self, event ):
        event.Skip()

    def on_show_log_file( self, event ):
        event.Skip()


###########################################################################
## Class DeleteDialog
###########################################################################

class DeleteDialog ( wx.Dialog ):

    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Delete", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        bSizer21 = wx.BoxSizer( wx.VERTICAL )

        self.m_progress_panel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.m_progress_panel.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )

        bSizer22 = wx.BoxSizer( wx.VERTICAL )

        self.m_progress_label = wx.StaticText( self.m_progress_panel, wx.ID_ANY, u"MyLabel", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_progress_label.Wrap( -1 )

        bSizer22.Add( self.m_progress_label, 0, wx.ALL, 5 )

        self.m_progress = wx.Gauge( self.m_progress_panel, wx.ID_ANY, 100, wx.DefaultPosition, wx.DefaultSize, wx.GA_HORIZONTAL )
        self.m_progress.SetValue( 0 )
        bSizer22.Add( self.m_progress, 0, wx.ALL|wx.EXPAND, 5 )

        fgSizer56 = wx.FlexGridSizer( 0, 4, 0, 0 )
        fgSizer56.AddGrowableCol( 0 )
        fgSizer56.AddGrowableCol( 3 )
        fgSizer56.SetFlexibleDirection( wx.BOTH )
        fgSizer56.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )


        fgSizer56.Add( ( 0, 0), 1, wx.EXPAND, 5 )

        self.m_okay_button = wx.Button( self.m_progress_panel, wx.ID_ANY, u"Close", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer56.Add( self.m_okay_button, 0, wx.ALL, 5 )

        self.m_cancel_button = wx.Button( self.m_progress_panel, wx.ID_ANY, u"Abort", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer56.Add( self.m_cancel_button, 0, wx.ALL, 5 )


        fgSizer56.Add( ( 0, 0), 1, wx.EXPAND, 5 )


        bSizer22.Add( fgSizer56, 1, wx.EXPAND, 5 )


        self.m_progress_panel.SetSizer( bSizer22 )
        self.m_progress_panel.Layout()
        bSizer22.Fit( self.m_progress_panel )
        bSizer21.Add( self.m_progress_panel, 1, wx.EXPAND |wx.ALL, 5 )


        self.SetSizer( bSizer21 )
        self.Layout()
        bSizer21.Fit( self )

        self.Centre( wx.BOTH )

        # Connect Events
        self.Bind( wx.EVT_CLOSE, self.on_close )
        self.Bind( wx.EVT_IDLE, self.on_idle )
        self.m_okay_button.Bind( wx.EVT_BUTTON, self.on_okay_click )
        self.m_cancel_button.Bind( wx.EVT_BUTTON, self.on_cancel_click )

    def __del__( self ):
        pass


    # Virtual event handlers, overide them in your derived class
    def on_close( self, event ):
        event.Skip()

    def on_idle( self, event ):
        event.Skip()

    def on_okay_click( self, event ):
        event.Skip()

    def on_cancel_click( self, event ):
        event.Skip()


###########################################################################
## Class ChecksumDialog
###########################################################################

class ChecksumDialog ( wx.Dialog ):

    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Hash", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        bSizer20 = wx.BoxSizer( wx.VERTICAL )

        self.m_hash_panel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.m_hash_panel.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )

        fgSizer54 = wx.FlexGridSizer( 5, 1, 0, 0 )
        fgSizer54.AddGrowableCol( 0 )
        fgSizer54.AddGrowableRow( 2 )
        fgSizer54.SetFlexibleDirection( wx.BOTH )
        fgSizer54.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_file_label = wx.StaticText( self.m_hash_panel, wx.ID_ANY, u"File.ext", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_file_label.Wrap( -1 )

        fgSizer54.Add( self.m_file_label, 0, wx.ALL, 5 )

        self.m_hash_label = wx.StaticText( self.m_hash_panel, wx.ID_ANY, u"Hash:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_hash_label.Wrap( -1 )

        fgSizer54.Add( self.m_hash_label, 0, wx.ALL, 5 )

        self.m_hash_textbox = wx.TextCtrl( self.m_hash_panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE|wx.TE_READONLY )
        self.m_hash_textbox.SetMinSize( wx.Size( 200,50 ) )

        fgSizer54.Add( self.m_hash_textbox, 1, wx.ALL|wx.EXPAND, 5 )

        self.m_hash_progress = wx.Gauge( self.m_hash_panel, wx.ID_ANY, 100, wx.DefaultPosition, wx.DefaultSize, wx.GA_HORIZONTAL )
        self.m_hash_progress.SetValue( 0 )
        fgSizer54.Add( self.m_hash_progress, 0, wx.ALL|wx.EXPAND, 5 )

        fgSizer55 = wx.FlexGridSizer( 0, 4, 0, 0 )
        fgSizer55.AddGrowableCol( 0 )
        fgSizer55.AddGrowableCol( 3 )
        fgSizer55.SetFlexibleDirection( wx.BOTH )
        fgSizer55.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )


        fgSizer55.Add( ( 0, 0), 1, wx.EXPAND, 5 )

        self.m_okay_button = wx.Button( self.m_hash_panel, wx.ID_ANY, u"Okay", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer55.Add( self.m_okay_button, 0, wx.ALL, 5 )

        self.m_cancel_button = wx.Button( self.m_hash_panel, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer55.Add( self.m_cancel_button, 0, wx.ALL, 5 )


        fgSizer55.Add( ( 0, 0), 1, wx.EXPAND, 5 )


        fgSizer54.Add( fgSizer55, 1, wx.EXPAND, 5 )


        self.m_hash_panel.SetSizer( fgSizer54 )
        self.m_hash_panel.Layout()
        fgSizer54.Fit( self.m_hash_panel )
        bSizer20.Add( self.m_hash_panel, 1, wx.EXPAND |wx.ALL, 5 )


        self.SetSizer( bSizer20 )
        self.Layout()
        bSizer20.Fit( self )

        self.Centre( wx.BOTH )

        # Connect Events
        self.Bind( wx.EVT_CLOSE, self.on_close )
        self.Bind( wx.EVT_IDLE, self.on_idle )
        self.m_okay_button.Bind( wx.EVT_BUTTON, self.on_okay_click )
        self.m_cancel_button.Bind( wx.EVT_BUTTON, self.on_cancel_click )

    def __del__( self ):
        pass


    # Virtual event handlers, overide them in your derived class
    def on_close( self, event ):
        event.Skip()

    def on_idle( self, event ):
        event.Skip()

    def on_okay_click( self, event ):
        event.Skip()

    def on_cancel_click( self, event ):
        event.Skip()


###########################################################################
## Class SupportInfoDialog
###########################################################################

class SupportInfoDialog ( wx.Dialog ):

    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Support Info", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )

        self.SetSizeHints( wx.Size( 300,300 ), wx.DefaultSize )

        bSizer20 = wx.BoxSizer( wx.VERTICAL )

        self.m_support_panel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.m_support_panel.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )

        fgSizer50 = wx.FlexGridSizer( 0, 1, 0, 0 )
        fgSizer50.AddGrowableCol( 0 )
        fgSizer50.AddGrowableRow( 0 )
        fgSizer50.SetFlexibleDirection( wx.BOTH )
        fgSizer50.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_info_textbox = wx.TextCtrl( self.m_support_panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE|wx.TE_READONLY )
        fgSizer50.Add( self.m_info_textbox, 1, wx.ALL|wx.EXPAND, 5 )

        fgSizer51 = wx.FlexGridSizer( 0, 4, 0, 0 )
        fgSizer51.AddGrowableCol( 0 )
        fgSizer51.AddGrowableCol( 2 )
        fgSizer51.SetFlexibleDirection( wx.BOTH )
        fgSizer51.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )


        fgSizer51.Add( ( 0, 0), 1, wx.EXPAND, 5 )

        self.m_copy_button = wx.Button( self.m_support_panel, wx.ID_ANY, u"Copy", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer51.Add( self.m_copy_button, 0, wx.ALL, 5 )

        self.m_cancel_button = wx.Button( self.m_support_panel, wx.ID_ANY, u"Close", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer51.Add( self.m_cancel_button, 0, wx.ALL, 5 )


        fgSizer51.Add( ( 0, 0), 1, wx.EXPAND, 5 )


        fgSizer50.Add( fgSizer51, 1, wx.EXPAND, 5 )


        self.m_support_panel.SetSizer( fgSizer50 )
        self.m_support_panel.Layout()
        fgSizer50.Fit( self.m_support_panel )
        bSizer20.Add( self.m_support_panel, 1, wx.EXPAND |wx.ALL, 5 )


        self.SetSizer( bSizer20 )
        self.Layout()
        bSizer20.Fit( self )

        self.Centre( wx.BOTH )

        # Connect Events
        self.m_copy_button.Bind( wx.EVT_BUTTON, self.on_copy )
        self.m_cancel_button.Bind( wx.EVT_BUTTON, self.on_cancel )

    def __del__( self ):
        pass


    # Virtual event handlers, overide them in your derived class
    def on_copy( self, event ):
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
        fgSizer40 = wx.FlexGridSizer( 0, 1, 0, 0 )
        fgSizer40.AddGrowableCol( 0 )
        fgSizer40.AddGrowableRow( 0 )
        fgSizer40.SetFlexibleDirection( wx.BOTH )
        fgSizer40.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_settings_notebook = wx.Notebook( self.m_settings_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.NB_NOPAGETHEME )
        self.m_settings_notebook.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )

        self.m_general_panel = wx.Panel( self.m_settings_notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.m_general_panel.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )

        fgSizer52 = wx.FlexGridSizer( 0, 1, 0, 0 )
        fgSizer52.AddGrowableCol( 0 )
        fgSizer52.SetFlexibleDirection( wx.BOTH )
        fgSizer52.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_single_checkbox = wx.CheckBox( self.m_general_panel, wx.ID_ANY, u"Single Instance (applies to new instances)", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer52.Add( self.m_single_checkbox, 0, wx.ALL, 5 )

        self.m_staticline10 = wx.StaticLine( self.m_general_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer52.Add( self.m_staticline10, 0, wx.EXPAND |wx.ALL, 5 )

        fgSizer38 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer38.AddGrowableCol( 1 )
        fgSizer38.SetFlexibleDirection( wx.BOTH )
        fgSizer38.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_language_label = wx.StaticText( self.m_general_panel, wx.ID_ANY, u"Language (restart required)", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_language_label.Wrap( -1 )

        fgSizer38.Add( self.m_language_label, 0, wx.ALL, 5 )

        m_lang_choiceChoices = []
        self.m_lang_choice = wx.Choice( self.m_general_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_lang_choiceChoices, 0 )
        self.m_lang_choice.SetSelection( 0 )
        fgSizer38.Add( self.m_lang_choice, 0, wx.ALIGN_RIGHT|wx.ALL, 5 )


        fgSizer52.Add( fgSizer38, 1, wx.EXPAND, 5 )

        self.m_staticline91 = wx.StaticLine( self.m_general_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer52.Add( self.m_staticline91, 0, wx.EXPAND |wx.ALL, 5 )

        fgSizer54 = wx.FlexGridSizer( 0, 3, 0, 0 )
        fgSizer54.SetFlexibleDirection( wx.BOTH )
        fgSizer54.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_update_checkbox = wx.CheckBox( self.m_general_panel, wx.ID_ANY, u"Check for updates daily", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer54.Add( self.m_update_checkbox, 0, wx.ALL, 5 )

        self.m_prerelease_checkbox = wx.CheckBox( self.m_general_panel, wx.ID_ANY, u"Include prereleases", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer54.Add( self.m_prerelease_checkbox, 0, wx.ALL, 5 )

        self.m_check_update_button = wx.Button( self.m_general_panel, wx.ID_ANY, u"Check Now", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer54.Add( self.m_check_update_button, 0, wx.ALL, 5 )


        fgSizer52.Add( fgSizer54, 1, wx.EXPAND, 5 )

        self.m_staticline101 = wx.StaticLine( self.m_general_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer52.Add( self.m_staticline101, 0, wx.EXPAND |wx.ALL, 5 )

        self.m_time_output_checkbox = wx.CheckBox( self.m_general_panel, wx.ID_ANY, u"International time format for file results", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer52.Add( self.m_time_output_checkbox, 0, wx.ALL, 5 )


        self.m_general_panel.SetSizer( fgSizer52 )
        self.m_general_panel.Layout()
        fgSizer52.Fit( self.m_general_panel )
        self.m_settings_notebook.AddPage( self.m_general_panel, u"General", False )
        self.m_search_panel = wx.Panel( self.m_settings_notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.m_search_panel.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )

        fgSizer43 = wx.FlexGridSizer( 0, 1, 0, 0 )
        fgSizer43.AddGrowableCol( 0 )
        fgSizer43.SetFlexibleDirection( wx.BOTH )
        fgSizer43.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        sbSizer8 = wx.StaticBoxSizer( wx.StaticBox( self.m_search_panel, wx.ID_ANY, u"Regex" ), wx.VERTICAL )

        gbSizer5 = wx.GridBagSizer( 0, 0 )
        gbSizer5.SetFlexibleDirection( wx.BOTH )
        gbSizer5.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_re_radio = wx.RadioButton( sbSizer8.GetStaticBox(), wx.ID_ANY, u"Use Re module", wx.DefaultPosition, wx.DefaultSize, wx.RB_GROUP )
        self.m_re_radio.SetValue( True )
        gbSizer5.Add( self.m_re_radio, wx.GBPosition( 0, 0 ), wx.GBSpan( 1, 2 ), wx.ALL, 5 )

        self.m_regex_radio = wx.RadioButton( sbSizer8.GetStaticBox(), wx.ID_ANY, u"Use Regex module", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_regex_radio.Enable( False )

        gbSizer5.Add( self.m_regex_radio, wx.GBPosition( 1, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        m_regex_ver_choiceChoices = [ u"V0", u"V1" ]
        self.m_regex_ver_choice = wx.Choice( sbSizer8.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_regex_ver_choiceChoices, 0 )
        self.m_regex_ver_choice.SetSelection( 0 )
        self.m_regex_ver_choice.Enable( False )

        gbSizer5.Add( self.m_regex_ver_choice, wx.GBPosition( 1, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_RIGHT, 5 )

        self.m_staticline11 = wx.StaticLine( sbSizer8.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        gbSizer5.Add( self.m_staticline11, wx.GBPosition( 2, 0 ), wx.GBSpan( 1, 2 ), wx.EXPAND |wx.ALL, 5 )

        self.m_backrefs_checkbox = wx.CheckBox( sbSizer8.GetStaticBox(), wx.ID_ANY, u"Enable Backrefs", wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer5.Add( self.m_backrefs_checkbox, wx.GBPosition( 3, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )


        gbSizer5.AddGrowableCol( 0 )

        sbSizer8.Add( gbSizer5, 1, wx.EXPAND, 5 )


        fgSizer43.Add( sbSizer8, 1, wx.EXPAND, 5 )

        sbSizer9 = wx.StaticBoxSizer( wx.StaticBox( self.m_search_panel, wx.ID_ANY, u"File/Folder Matching" ), wx.VERTICAL )

        fgSizer61 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer61.SetFlexibleDirection( wx.BOTH )
        fgSizer61.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_extmatch_checkbox = wx.CheckBox( sbSizer9.GetStaticBox(), wx.ID_ANY, u"Extended match", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer61.Add( self.m_extmatch_checkbox, 0, wx.ALL, 5 )

        self.m_brace_checkbox = wx.CheckBox( sbSizer9.GetStaticBox(), wx.ID_ANY, u"Brace expansion", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer61.Add( self.m_brace_checkbox, 0, wx.ALL, 5 )

        self.m_case_checkbox = wx.CheckBox( sbSizer9.GetStaticBox(), wx.ID_ANY, u"Case sensitive", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer61.Add( self.m_case_checkbox, 0, wx.ALL, 5 )

        self.m_globstar_checkbox = wx.CheckBox( sbSizer9.GetStaticBox(), wx.ID_ANY, u"Globstar (full path)", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer61.Add( self.m_globstar_checkbox, 0, wx.ALL, 5 )

        self.m_matchbase_checkbox = wx.CheckBox( sbSizer9.GetStaticBox(), wx.ID_ANY, u"Match base (full path)", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer61.Add( self.m_matchbase_checkbox, 0, wx.ALL, 5 )

        self.m_fullpath_checkbox = wx.CheckBox( sbSizer9.GetStaticBox(), wx.ID_ANY, u"Full path directory match", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer61.Add( self.m_fullpath_checkbox, 0, wx.ALL, 5 )

        self.m_fullfile_checkbox = wx.CheckBox( sbSizer9.GetStaticBox(), wx.ID_ANY, u"Full path file match", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer61.Add( self.m_fullfile_checkbox, 0, wx.ALL, 5 )


        sbSizer9.Add( fgSizer61, 1, wx.EXPAND, 5 )


        fgSizer43.Add( sbSizer9, 1, wx.EXPAND, 5 )


        self.m_search_panel.SetSizer( fgSizer43 )
        self.m_search_panel.Layout()
        fgSizer43.Fit( self.m_search_panel )
        self.m_settings_notebook.AddPage( self.m_search_panel, u"Search", False )
        self.m_encoding_panel = wx.Panel( self.m_settings_notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.m_encoding_panel.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )

        fgSizer57 = wx.FlexGridSizer( 3, 1, 0, 0 )
        fgSizer57.AddGrowableCol( 0 )
        fgSizer57.AddGrowableRow( 2 )
        fgSizer57.SetFlexibleDirection( wx.BOTH )
        fgSizer57.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        fgSizer58 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer58.SetFlexibleDirection( wx.BOTH )
        fgSizer58.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_encoding_label = wx.StaticText( self.m_encoding_panel, wx.ID_ANY, u"Encoding Detection", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_encoding_label.Wrap( -1 )

        fgSizer58.Add( self.m_encoding_label, 0, wx.ALL, 5 )

        m_encoding_choiceChoices = []
        self.m_encoding_choice = wx.Choice( self.m_encoding_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_encoding_choiceChoices, 0 )
        self.m_encoding_choice.SetSelection( 0 )
        fgSizer58.Add( self.m_encoding_choice, 0, wx.ALL, 5 )


        fgSizer57.Add( fgSizer58, 1, wx.EXPAND, 5 )

        self.m_filetype_label = wx.StaticText( self.m_encoding_panel, wx.ID_ANY, u"Special file types:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_filetype_label.Wrap( -1 )

        fgSizer57.Add( self.m_filetype_label, 0, wx.ALL, 5 )

        self.m_encoding_list = EncodingList(self.m_encoding_panel)
        fgSizer57.Add( self.m_encoding_list, 1, wx.ALL|wx.EXPAND, 5 )


        self.m_encoding_panel.SetSizer( fgSizer57 )
        self.m_encoding_panel.Layout()
        fgSizer57.Fit( self.m_encoding_panel )
        self.m_settings_notebook.AddPage( self.m_encoding_panel, u"Encoding", False )
        self.m_editor_panel = wx.Panel( self.m_settings_notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.m_editor_panel.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )

        fgSizer63 = wx.FlexGridSizer( 0, 1, 0, 0 )
        fgSizer63.AddGrowableCol( 0 )
        fgSizer63.AddGrowableRow( 0 )
        fgSizer63.SetFlexibleDirection( wx.BOTH )
        fgSizer63.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_help_html = wx.html2.WebView.New(self.m_editor_panel)
        self.m_help_html.SetMinSize( wx.Size( -1,100 ) )

        fgSizer63.Add( self.m_help_html, 0, wx.ALL|wx.EXPAND, 5 )

        fgSizer13 = wx.FlexGridSizer( 0, 3, 0, 0 )
        fgSizer13.AddGrowableCol( 1 )
        fgSizer13.SetFlexibleDirection( wx.BOTH )
        fgSizer13.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_editor_label = wx.StaticText( self.m_editor_panel, wx.ID_ANY, u"Editor", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_editor_label.Wrap( -1 )

        fgSizer13.Add( self.m_editor_label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.m_editor_text = wx.TextCtrl( self.m_editor_panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer13.Add( self.m_editor_text, 1, wx.ALL|wx.EXPAND, 5 )

        self.m_editor_button = wx.Button( self.m_editor_panel, wx.ID_ANY, u"Save", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer13.Add( self.m_editor_button, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


        fgSizer63.Add( fgSizer13, 1, wx.EXPAND, 5 )


        self.m_editor_panel.SetSizer( fgSizer63 )
        self.m_editor_panel.Layout()
        fgSizer63.Fit( self.m_editor_panel )
        self.m_settings_notebook.AddPage( self.m_editor_panel, u"Editor", False )
        self.m_notify_panel = wx.Panel( self.m_settings_notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.m_notify_panel.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )

        fgSizer35 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer35.AddGrowableCol( 1 )
        fgSizer35.SetFlexibleDirection( wx.BOTH )
        fgSizer35.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_visual_alert_checkbox = wx.CheckBox( self.m_notify_panel, wx.ID_ANY, u"Notification popup", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_visual_alert_checkbox.SetValue(True)
        fgSizer35.Add( self.m_visual_alert_checkbox, 0, wx.ALL, 5 )

        m_notify_choiceChoices = []
        self.m_notify_choice = wx.Choice( self.m_notify_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_notify_choiceChoices, 0 )
        self.m_notify_choice.SetSelection( 0 )
        fgSizer35.Add( self.m_notify_choice, 0, wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.m_audio_alert_checkbox = wx.CheckBox( self.m_notify_panel, wx.ID_ANY, u"Alert Sound", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_audio_alert_checkbox.SetValue(True)
        fgSizer35.Add( self.m_audio_alert_checkbox, 0, wx.ALL, 5 )


        fgSizer35.Add( ( 0, 0), 1, wx.EXPAND, 5 )

        self.m_term_note_label = wx.StaticText( self.m_notify_panel, wx.ID_ANY, u"Path to terminal-notifier", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_term_note_label.Wrap( -1 )

        self.m_term_note_label.Enable( False )

        fgSizer35.Add( self.m_term_note_label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.m_term_note_picker = wx.FilePickerCtrl( self.m_notify_panel, wx.ID_ANY, wx.EmptyString, u"Select a file", u"*.*", wx.DefaultPosition, wx.DefaultSize, wx.FLP_DEFAULT_STYLE|wx.FLP_FILE_MUST_EXIST )
        self.m_term_note_picker.Enable( False )

        fgSizer35.Add( self.m_term_note_picker, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )


        fgSizer35.Add( ( 0, 0), 1, wx.EXPAND, 5 )

        self.m_notify_test_button = wx.Button( self.m_notify_panel, wx.ID_ANY, u"Test", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer35.Add( self.m_notify_test_button, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )


        self.m_notify_panel.SetSizer( fgSizer35 )
        self.m_notify_panel.Layout()
        fgSizer35.Fit( self.m_notify_panel )
        self.m_settings_notebook.AddPage( self.m_notify_panel, u"Notifications", False )
        self.m_history_panel = wx.Panel( self.m_settings_notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.m_history_panel.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )

        fgSizer66 = wx.FlexGridSizer( 0, 1, 0, 0 )
        fgSizer66.AddGrowableCol( 0 )
        fgSizer66.AddGrowableRow( 1 )
        fgSizer66.SetFlexibleDirection( wx.BOTH )
        fgSizer66.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        fgSizer30 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer30.AddGrowableCol( 0 )
        fgSizer30.SetFlexibleDirection( wx.BOTH )
        fgSizer30.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_history_label = wx.StaticText( self.m_history_panel, wx.ID_ANY, u"0 Records", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_history_label.Wrap( -1 )

        fgSizer30.Add( self.m_history_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.m_history_clear_button = wx.Button( self.m_history_panel, wx.ID_ANY, u"Clear", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer30.Add( self.m_history_clear_button, 0, wx.ALIGN_RIGHT|wx.ALL, 5 )


        fgSizer66.Add( fgSizer30, 1, wx.EXPAND, 5 )

        self.m_cache_textbox = wx.TextCtrl( self.m_history_panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE|wx.TE_READONLY )
        self.m_cache_textbox.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )

        fgSizer66.Add( self.m_cache_textbox, 0, wx.ALL|wx.EXPAND, 5 )


        self.m_history_panel.SetSizer( fgSizer66 )
        self.m_history_panel.Layout()
        fgSizer66.Fit( self.m_history_panel )
        self.m_settings_notebook.AddPage( self.m_history_panel, u"History", False )
        self.m_backup_panel = wx.Panel( self.m_settings_notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.m_backup_panel.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )

        fgSizer401 = wx.FlexGridSizer( 0, 1, 0, 0 )
        fgSizer401.AddGrowableCol( 0 )
        fgSizer401.SetFlexibleDirection( wx.BOTH )
        fgSizer401.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        fgSizer41 = wx.FlexGridSizer( 0, 3, 0, 0 )
        fgSizer41.AddGrowableCol( 1 )
        fgSizer41.SetFlexibleDirection( wx.BOTH )
        fgSizer41.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_back_ext_label = wx.StaticText( self.m_backup_panel, wx.ID_ANY, u"Backup extension", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_back_ext_label.Wrap( -1 )

        fgSizer41.Add( self.m_back_ext_label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )

        self.m_back_ext_textbox = wx.TextCtrl( self.m_backup_panel, wx.ID_ANY, u"rum-bak", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer41.Add( self.m_back_ext_textbox, 0, wx.ALL|wx.EXPAND, 5 )

        self.m_back_ext_button = wx.Button( self.m_backup_panel, wx.ID_ANY, u"Save", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer41.Add( self.m_back_ext_button, 0, wx.ALL, 5 )

        self.m_back_folder_label = wx.StaticText( self.m_backup_panel, wx.ID_ANY, u"Backup folder", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_back_folder_label.Wrap( -1 )

        fgSizer41.Add( self.m_back_folder_label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )

        self.m_back_folder_textbox = wx.TextCtrl( self.m_backup_panel, wx.ID_ANY, u".rum-bak", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer41.Add( self.m_back_folder_textbox, 0, wx.ALL|wx.EXPAND, 5 )

        self.m_back_folder_button = wx.Button( self.m_backup_panel, wx.ID_ANY, u"Save", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer41.Add( self.m_back_folder_button, 0, wx.ALL, 5 )


        fgSizer401.Add( fgSizer41, 1, wx.EXPAND, 5 )

        self.m_staticline9 = wx.StaticLine( self.m_backup_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer401.Add( self.m_staticline9, 0, wx.EXPAND |wx.ALL, 5 )

        self.m_back2folder_checkbox = wx.CheckBox( self.m_backup_panel, wx.ID_ANY, u"Backup to folder", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer401.Add( self.m_back2folder_checkbox, 0, wx.ALL, 5 )


        self.m_backup_panel.SetSizer( fgSizer401 )
        self.m_backup_panel.Layout()
        fgSizer401.Fit( self.m_backup_panel )
        self.m_settings_notebook.AddPage( self.m_backup_panel, u"Backups", False )

        fgSizer40.Add( self.m_settings_notebook, 1, wx.EXPAND |wx.ALL, 5 )

        fgSizer22 = wx.FlexGridSizer( 0, 3, 0, 0 )
        fgSizer22.AddGrowableCol( 0 )
        fgSizer22.AddGrowableCol( 2 )
        fgSizer22.SetFlexibleDirection( wx.BOTH )
        fgSizer22.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )


        fgSizer22.Add( ( 0, 0), 1, wx.EXPAND, 5 )

        self.m_close_button = wx.Button( self.m_settings_panel, wx.ID_ANY, u"Close", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer22.Add( self.m_close_button, 0, wx.ALL, 5 )


        fgSizer22.Add( ( 0, 0), 1, wx.EXPAND, 5 )


        fgSizer40.Add( fgSizer22, 1, wx.EXPAND, 5 )


        self.m_settings_panel.SetSizer( fgSizer40 )
        self.m_settings_panel.Layout()
        fgSizer40.Fit( self.m_settings_panel )
        bSizer7.Add( self.m_settings_panel, 1, wx.EXPAND |wx.ALL, 5 )


        self.SetSizer( bSizer7 )
        self.Layout()
        bSizer7.Fit( self )

        self.Centre( wx.BOTH )

        # Connect Events
        self.Bind( wx.EVT_CLOSE, self.on_close )
        self.m_single_checkbox.Bind( wx.EVT_CHECKBOX, self.on_single_toggle )
        self.m_lang_choice.Bind( wx.EVT_CHOICE, self.on_language )
        self.m_update_checkbox.Bind( wx.EVT_CHECKBOX, self.on_update_toggle )
        self.m_prerelease_checkbox.Bind( wx.EVT_CHECKBOX, self.on_prerelease_toggle )
        self.m_check_update_button.Bind( wx.EVT_BUTTON, self.on_check )
        self.m_time_output_checkbox.Bind( wx.EVT_CHECKBOX, self.on_time_output_toggle )
        self.m_re_radio.Bind( wx.EVT_RADIOBUTTON, self.on_re_toggle )
        self.m_regex_radio.Bind( wx.EVT_RADIOBUTTON, self.on_regex_toggle )
        self.m_regex_ver_choice.Bind( wx.EVT_CHOICE, self.on_regex_ver_choice )
        self.m_backrefs_checkbox.Bind( wx.EVT_CHECKBOX, self.on_backrefs_toggle )
        self.m_extmatch_checkbox.Bind( wx.EVT_CHECKBOX, self.on_extmatch_toggle )
        self.m_brace_checkbox.Bind( wx.EVT_CHECKBOX, self.on_brace_toggle )
        self.m_case_checkbox.Bind( wx.EVT_CHECKBOX, self.on_case_toggle )
        self.m_globstar_checkbox.Bind( wx.EVT_CHECKBOX, self.on_globstar_toggle )
        self.m_matchbase_checkbox.Bind( wx.EVT_CHECKBOX, self.on_matchbase_toggle )
        self.m_fullpath_checkbox.Bind( wx.EVT_CHECKBOX, self.on_fullpath_toggle )
        self.m_fullfile_checkbox.Bind( wx.EVT_CHECKBOX, self.on_fullfile_toggle )
        self.m_encoding_choice.Bind( wx.EVT_CHOICE, self.on_chardet )
        self.m_editor_text.Bind( wx.EVT_TEXT, self.on_editor_changed )
        self.m_editor_button.Bind( wx.EVT_BUTTON, self.on_editor_change )
        self.m_visual_alert_checkbox.Bind( wx.EVT_CHECKBOX, self.on_notify_toggle )
        self.m_notify_choice.Bind( wx.EVT_CHOICE, self.on_notify_choice )
        self.m_audio_alert_checkbox.Bind( wx.EVT_CHECKBOX, self.on_alert_toggle )
        self.m_term_note_picker.Bind( wx.EVT_FILEPICKER_CHANGED, self.on_term_note_change )
        self.m_notify_test_button.Bind( wx.EVT_BUTTON, self.on_notify_test_click )
        self.m_history_clear_button.Bind( wx.EVT_BUTTON, self.on_clear_history )
        self.m_back_ext_textbox.Bind( wx.EVT_TEXT, self.on_back_ext_changed )
        self.m_back_ext_button.Bind( wx.EVT_BUTTON, self.on_back_ext_click )
        self.m_back_folder_textbox.Bind( wx.EVT_TEXT, self.on_back_folder_changed )
        self.m_back_folder_button.Bind( wx.EVT_BUTTON, self.on_back_folder_click )
        self.m_back2folder_checkbox.Bind( wx.EVT_CHECKBOX, self.on_back2folder_toggle )
        self.m_close_button.Bind( wx.EVT_BUTTON, self.on_cancel )

    def __del__( self ):
        pass


    # Virtual event handlers, overide them in your derived class
    def on_close( self, event ):
        event.Skip()

    def on_single_toggle( self, event ):
        event.Skip()

    def on_language( self, event ):
        event.Skip()

    def on_update_toggle( self, event ):
        event.Skip()

    def on_prerelease_toggle( self, event ):
        event.Skip()

    def on_check( self, event ):
        event.Skip()

    def on_time_output_toggle( self, event ):
        event.Skip()

    def on_re_toggle( self, event ):
        event.Skip()

    def on_regex_toggle( self, event ):
        event.Skip()

    def on_regex_ver_choice( self, event ):
        event.Skip()

    def on_backrefs_toggle( self, event ):
        event.Skip()

    def on_extmatch_toggle( self, event ):
        event.Skip()

    def on_brace_toggle( self, event ):
        event.Skip()

    def on_case_toggle( self, event ):
        event.Skip()

    def on_globstar_toggle( self, event ):
        event.Skip()

    def on_matchbase_toggle( self, event ):
        event.Skip()

    def on_fullpath_toggle( self, event ):
        event.Skip()

    def on_fullfile_toggle( self, event ):
        event.Skip()

    def on_chardet( self, event ):
        event.Skip()

    def on_editor_changed( self, event ):
        event.Skip()

    def on_editor_change( self, event ):
        event.Skip()

    def on_notify_toggle( self, event ):
        event.Skip()

    def on_notify_choice( self, event ):
        event.Skip()

    def on_alert_toggle( self, event ):
        event.Skip()

    def on_term_note_change( self, event ):
        event.Skip()

    def on_notify_test_click( self, event ):
        event.Skip()

    def on_clear_history( self, event ):
        event.Skip()

    def on_back_ext_changed( self, event ):
        event.Skip()

    def on_back_ext_click( self, event ):
        event.Skip()

    def on_back_folder_changed( self, event ):
        event.Skip()

    def on_back_folder_click( self, event ):
        event.Skip()

    def on_back2folder_toggle( self, event ):
        event.Skip()

    def on_cancel( self, event ):
        event.Skip()


###########################################################################
## Class FileExtDialog
###########################################################################

class FileExtDialog ( wx.Dialog ):

    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"File Extensions", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        bSizer23 = wx.BoxSizer( wx.VERTICAL )

        self.m_ext_panel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.m_ext_panel.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )

        fgSizer61 = wx.FlexGridSizer( 2, 1, 0, 0 )
        fgSizer61.AddGrowableCol( 0 )
        fgSizer61.SetFlexibleDirection( wx.BOTH )
        fgSizer61.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        fgSizer60 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer60.AddGrowableCol( 1 )
        fgSizer60.SetFlexibleDirection( wx.BOTH )
        fgSizer60.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_ext_label = wx.StaticText( self.m_ext_panel, wx.ID_ANY, u"Extensions", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_ext_label.Wrap( -1 )

        fgSizer60.Add( self.m_ext_label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.m_ext_textbox = wx.TextCtrl( self.m_ext_panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer60.Add( self.m_ext_textbox, 1, wx.ALL|wx.EXPAND, 5 )


        fgSizer61.Add( fgSizer60, 1, wx.EXPAND, 5 )

        fgSizer64 = wx.FlexGridSizer( 1, 4, 0, 0 )
        fgSizer64.AddGrowableCol( 0 )
        fgSizer64.AddGrowableCol( 3 )
        fgSizer64.SetFlexibleDirection( wx.BOTH )
        fgSizer64.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )


        fgSizer64.Add( ( 0, 0), 1, wx.EXPAND, 5 )

        self.m_okay_button = wx.Button( self.m_ext_panel, wx.ID_ANY, u"Okay", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer64.Add( self.m_okay_button, 0, wx.ALL, 5 )

        self.m_cancel_button = wx.Button( self.m_ext_panel, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer64.Add( self.m_cancel_button, 0, wx.ALL, 5 )


        fgSizer64.Add( ( 0, 0), 1, wx.EXPAND, 5 )


        fgSizer61.Add( fgSizer64, 1, wx.EXPAND, 5 )


        self.m_ext_panel.SetSizer( fgSizer61 )
        self.m_ext_panel.Layout()
        fgSizer61.Fit( self.m_ext_panel )
        bSizer23.Add( self.m_ext_panel, 1, wx.EXPAND |wx.ALL, 5 )


        self.SetSizer( bSizer23 )
        self.Layout()
        bSizer23.Fit( self )

        self.Centre( wx.BOTH )

        # Connect Events
        self.m_okay_button.Bind( wx.EVT_BUTTON, self.on_okay_click )
        self.m_cancel_button.Bind( wx.EVT_BUTTON, self.on_cancel_click )

    def __del__( self ):
        pass


    # Virtual event handlers, overide them in your derived class
    def on_okay_click( self, event ):
        event.Skip()

    def on_cancel_click( self, event ):
        event.Skip()


###########################################################################
## Class ExportSettingsDialog
###########################################################################

class ExportSettingsDialog ( wx.Dialog ):

    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Export Settings", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        bSizer17 = wx.BoxSizer( wx.VERTICAL )

        self.m_export_panel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.m_export_panel.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )

        fgSizer42 = wx.FlexGridSizer( 0, 1, 0, 0 )
        fgSizer42.AddGrowableCol( 0 )
        fgSizer42.SetFlexibleDirection( wx.BOTH )
        fgSizer42.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_general_settings_checkbox = wx.CheckBox( self.m_export_panel, wx.ID_ANY, u"General settings", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer42.Add( self.m_general_settings_checkbox, 0, wx.ALL, 5 )

        self.m_chains_checkbox = wx.CheckBox( self.m_export_panel, wx.ID_ANY, u"Chains", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer42.Add( self.m_chains_checkbox, 0, wx.ALL, 5 )

        self.m_patterns_checkbox = wx.CheckBox( self.m_export_panel, wx.ID_ANY, u"Search/replace patterns", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer42.Add( self.m_patterns_checkbox, 0, wx.ALL, 5 )

        fgSizer43 = wx.FlexGridSizer( 0, 4, 0, 0 )
        fgSizer43.AddGrowableCol( 0 )
        fgSizer43.AddGrowableCol( 3 )
        fgSizer43.SetFlexibleDirection( wx.BOTH )
        fgSizer43.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )


        fgSizer43.Add( ( 0, 0), 1, wx.EXPAND, 5 )

        self.m_export_button = wx.Button( self.m_export_panel, wx.ID_ANY, u"Export", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer43.Add( self.m_export_button, 0, wx.ALL, 5 )

        self.m_close_button = wx.Button( self.m_export_panel, wx.ID_ANY, u"Close", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer43.Add( self.m_close_button, 0, wx.ALL, 5 )


        fgSizer43.Add( ( 0, 0), 1, wx.EXPAND, 5 )


        fgSizer42.Add( fgSizer43, 1, wx.EXPAND, 5 )


        self.m_export_panel.SetSizer( fgSizer42 )
        self.m_export_panel.Layout()
        fgSizer42.Fit( self.m_export_panel )
        bSizer17.Add( self.m_export_panel, 1, wx.EXPAND |wx.ALL, 5 )


        self.SetSizer( bSizer17 )
        self.Layout()
        bSizer17.Fit( self )

        self.Centre( wx.BOTH )

        # Connect Events
        self.m_export_button.Bind( wx.EVT_BUTTON, self.on_export_click )
        self.m_close_button.Bind( wx.EVT_BUTTON, self.on_cancel_click )

    def __del__( self ):
        pass


    # Virtual event handlers, overide them in your derived class
    def on_export_click( self, event ):
        event.Skip()

    def on_cancel_click( self, event ):
        event.Skip()


###########################################################################
## Class ImportSettingsDialog
###########################################################################

class ImportSettingsDialog ( wx.Dialog ):

    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Import Settings", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        bSizer17 = wx.BoxSizer( wx.VERTICAL )

        self.m_import_panel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.m_import_panel.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )

        fgSizer42 = wx.FlexGridSizer( 0, 1, 0, 0 )
        fgSizer42.AddGrowableCol( 0 )
        fgSizer42.AddGrowableRow( 3 )
        fgSizer42.SetFlexibleDirection( wx.BOTH )
        fgSizer42.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_general_settings_checkbox = wx.CheckBox( self.m_import_panel, wx.ID_ANY, u"General settings", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer42.Add( self.m_general_settings_checkbox, 0, wx.ALL, 5 )

        self.m_chains_checkbox = wx.CheckBox( self.m_import_panel, wx.ID_ANY, u"Chains", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer42.Add( self.m_chains_checkbox, 0, wx.ALL, 5 )

        self.m_patterns_checkbox = wx.CheckBox( self.m_import_panel, wx.ID_ANY, u"Search/Replace patterns", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer42.Add( self.m_patterns_checkbox, 0, wx.ALL, 5 )

        self.m_results_textbox = wx.TextCtrl( self.m_import_panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE|wx.TE_READONLY )
        self.m_results_textbox.SetMinSize( wx.Size( -1,64 ) )

        fgSizer42.Add( self.m_results_textbox, 1, wx.ALL|wx.EXPAND, 5 )

        fgSizer43 = wx.FlexGridSizer( 0, 4, 0, 0 )
        fgSizer43.AddGrowableCol( 0 )
        fgSizer43.AddGrowableCol( 3 )
        fgSizer43.SetFlexibleDirection( wx.BOTH )
        fgSizer43.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )


        fgSizer43.Add( ( 0, 0), 1, wx.EXPAND, 5 )

        self.m_import_button = wx.Button( self.m_import_panel, wx.ID_ANY, u"Import", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer43.Add( self.m_import_button, 0, wx.ALL, 5 )

        self.m_close_button = wx.Button( self.m_import_panel, wx.ID_ANY, u"Close", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer43.Add( self.m_close_button, 0, wx.ALL, 5 )


        fgSizer43.Add( ( 0, 0), 1, wx.EXPAND, 5 )


        fgSizer42.Add( fgSizer43, 1, wx.EXPAND, 5 )


        self.m_import_panel.SetSizer( fgSizer42 )
        self.m_import_panel.Layout()
        fgSizer42.Fit( self.m_import_panel )
        bSizer17.Add( self.m_import_panel, 1, wx.EXPAND |wx.ALL, 5 )


        self.SetSizer( bSizer17 )
        self.Layout()
        bSizer17.Fit( self )

        self.Centre( wx.BOTH )

        # Connect Events
        self.m_import_button.Bind( wx.EVT_BUTTON, self.on_import_click )
        self.m_close_button.Bind( wx.EVT_BUTTON, self.on_cancel_click )

    def __del__( self ):
        pass


    # Virtual event handlers, overide them in your derived class
    def on_import_click( self, event ):
        event.Skip()

    def on_cancel_click( self, event ):
        event.Skip()


###########################################################################
## Class OverwriteDialog
###########################################################################

class OverwriteDialog ( wx.Dialog ):

    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Overwrite", pos = wx.DefaultPosition, size = wx.Size( 300,-1 ), style = wx.DEFAULT_DIALOG_STYLE )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        bSizer12 = wx.BoxSizer( wx.VERTICAL )

        self.m_overwrite_panel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.m_overwrite_panel.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )

        fgSizer33 = wx.FlexGridSizer( 0, 1, 0, 0 )
        fgSizer33.AddGrowableCol( 0 )
        fgSizer33.AddGrowableRow( 0 )
        fgSizer33.AddGrowableRow( 1 )
        fgSizer33.AddGrowableRow( 2 )
        fgSizer33.SetFlexibleDirection( wx.BOTH )
        fgSizer33.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        fgSizer52 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer52.AddGrowableCol( 1 )
        fgSizer52.AddGrowableRow( 0 )
        fgSizer52.SetFlexibleDirection( wx.BOTH )
        fgSizer52.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_bitmap = wx.StaticBitmap( self.m_overwrite_panel, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size( 64,64 ), 0 )
        self.m_bitmap.SetMinSize( wx.Size( 64,64 ) )

        fgSizer52.Add( self.m_bitmap, 0, wx.ALL, 5 )

        self.m_message_label = wx.StaticText( self.m_overwrite_panel, wx.ID_ANY, u"Overwrite?", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTER_HORIZONTAL )
        self.m_message_label.Wrap( -1 )

        fgSizer52.Add( self.m_message_label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


        fgSizer33.Add( fgSizer52, 1, wx.EXPAND, 5 )

        fgSizer53 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer53.AddGrowableCol( 0 )
        fgSizer53.AddGrowableRow( 0 )
        fgSizer53.SetFlexibleDirection( wx.BOTH )
        fgSizer53.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_remember_checkbox = wx.CheckBox( self.m_overwrite_panel, wx.ID_ANY, u"Apply to all", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer53.Add( self.m_remember_checkbox, 0, wx.ALL|wx.EXPAND, 5 )


        fgSizer33.Add( fgSizer53, 1, wx.EXPAND, 5 )

        fgSizer34 = wx.FlexGridSizer( 0, 4, 0, 0 )
        fgSizer34.AddGrowableCol( 0 )
        fgSizer34.AddGrowableCol( 3 )
        fgSizer34.AddGrowableRow( 0 )
        fgSizer34.SetFlexibleDirection( wx.BOTH )
        fgSizer34.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )


        fgSizer34.Add( ( 0, 0), 1, wx.EXPAND, 5 )

        self.m_overwrite_button = wx.Button( self.m_overwrite_panel, wx.ID_ANY, u"Overwrite", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer34.Add( self.m_overwrite_button, 0, wx.ALL, 5 )

        self.m_cancel_button = wx.Button( self.m_overwrite_panel, wx.ID_ANY, u"Skip", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer34.Add( self.m_cancel_button, 0, wx.ALL, 5 )


        fgSizer34.Add( ( 0, 0), 1, wx.EXPAND, 5 )


        fgSizer33.Add( fgSizer34, 1, wx.EXPAND, 5 )


        self.m_overwrite_panel.SetSizer( fgSizer33 )
        self.m_overwrite_panel.Layout()
        fgSizer33.Fit( self.m_overwrite_panel )
        bSizer12.Add( self.m_overwrite_panel, 1, wx.EXPAND |wx.ALL, 5 )


        self.SetSizer( bSizer12 )
        self.Layout()

        self.Centre( wx.BOTH )

        # Connect Events
        self.m_overwrite_button.Bind( wx.EVT_BUTTON, self.on_overwrite )
        self.m_cancel_button.Bind( wx.EVT_BUTTON, self.on_skip )

    def __del__( self ):
        pass


    # Virtual event handlers, overide them in your derived class
    def on_overwrite( self, event ):
        event.Skip()

    def on_skip( self, event ):
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

        self.m_test_text = wx.TextCtrl( self.m_tester_panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_DONTWRAP|wx.TE_MULTILINE|wx.TE_PROCESS_TAB|wx.TE_RICH2 )
        sbSizer11.Add( self.m_test_text, 1, wx.ALL|wx.EXPAND|wx.FIXED_MINSIZE, 5 )


        fgSizer18.Add( sbSizer11, 1, wx.EXPAND, 5 )

        sbSizer111 = wx.StaticBoxSizer( wx.StaticBox( self.m_tester_panel, wx.ID_ANY, u"Result" ), wx.VERTICAL )

        self.m_test_replace_text = wx.TextCtrl( self.m_tester_panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_DONTWRAP|wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_RICH2 )
        sbSizer111.Add( self.m_test_replace_text, 1, wx.ALL|wx.EXPAND, 5 )


        fgSizer18.Add( sbSizer111, 1, wx.EXPAND, 5 )

        sbSizer9 = wx.StaticBoxSizer( wx.StaticBox( self.m_tester_panel, wx.ID_ANY, u"Regex Input" ), wx.VERTICAL )

        fgSizer41 = wx.FlexGridSizer( 0, 1, 0, 0 )
        fgSizer41.AddGrowableCol( 0 )
        fgSizer41.SetFlexibleDirection( wx.BOTH )
        fgSizer41.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        fgSizer39 = wx.FlexGridSizer( 0, 4, 0, 0 )
        fgSizer39.AddGrowableCol( 1 )
        fgSizer39.SetFlexibleDirection( wx.HORIZONTAL )
        fgSizer39.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_find_label = wx.StaticText( self.m_tester_panel, wx.ID_ANY, u"Find", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_find_label.Wrap( -1 )

        fgSizer39.Add( self.m_find_label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )

        self.m_regex_text = wx.TextCtrl( self.m_tester_panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer39.Add( self.m_regex_text, 0, wx.ALL|wx.EXPAND, 5 )


        fgSizer39.Add( ( 0, 0), 1, wx.EXPAND, 5 )


        fgSizer39.Add( ( 0, 0), 1, wx.EXPAND, 5 )

        self.m_replace_label = wx.StaticText( self.m_tester_panel, wx.ID_ANY, u"Replace", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_replace_label.Wrap( -1 )

        fgSizer39.Add( self.m_replace_label, 0, wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.m_replace_text = wx.TextCtrl( self.m_tester_panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer39.Add( self.m_replace_text, 0, wx.ALL|wx.EXPAND, 5 )

        self.m_replace_plugin_dir_picker = wx.Button( self.m_tester_panel, wx.ID_ANY, u"...", wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT )
        fgSizer39.Add( self.m_replace_plugin_dir_picker, 0, wx.ALL, 5 )

        self.m_reload_button = wx.Button( self.m_tester_panel, wx.ID_ANY, u"Reload", wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT )
        fgSizer39.Add( self.m_reload_button, 0, wx.ALL, 5 )


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

        self.m_regex_search_checkbox = wx.CheckBox( self.m_tester_panel, wx.ID_ANY, u"Regex search", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer19.Add( self.m_regex_search_checkbox, 0, wx.ALL, 5 )

        self.m_case_checkbox = wx.CheckBox( self.m_tester_panel, wx.ID_ANY, u"Search case-sensitive", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer19.Add( self.m_case_checkbox, 0, wx.ALL, 5 )

        self.m_dotmatch_checkbox = wx.CheckBox( self.m_tester_panel, wx.ID_ANY, u"Dot matches newline", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer19.Add( self.m_dotmatch_checkbox, 0, wx.ALL, 5 )

        self.m_unicode_checkbox = wx.CheckBox( self.m_tester_panel, wx.ID_ANY, u"Use Unicode properties", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer19.Add( self.m_unicode_checkbox, 0, wx.ALL, 5 )

        self.m_format_replace_checkbox = wx.CheckBox( self.m_tester_panel, wx.ID_ANY, u"Format style replacements", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer19.Add( self.m_format_replace_checkbox, 0, wx.ALL, 5 )

        self.m_bestmatch_checkbox = wx.CheckBox( self.m_tester_panel, wx.ID_ANY, u"Best fuzzy match", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer19.Add( self.m_bestmatch_checkbox, 0, wx.ALL, 5 )

        self.m_enhancematch_checkbox = wx.CheckBox( self.m_tester_panel, wx.ID_ANY, u"Improve fuzzy fit", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer19.Add( self.m_enhancematch_checkbox, 0, wx.ALL, 5 )

        self.m_word_checkbox = wx.CheckBox( self.m_tester_panel, wx.ID_ANY, u"Unicode word breaks", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer19.Add( self.m_word_checkbox, 0, wx.ALL, 5 )

        self.m_reverse_checkbox = wx.CheckBox( self.m_tester_panel, wx.ID_ANY, u"Search backwards", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer19.Add( self.m_reverse_checkbox, 0, wx.ALL, 5 )

        self.m_posix_checkbox = wx.CheckBox( self.m_tester_panel, wx.ID_ANY, u"Use POSIX matching", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer19.Add( self.m_posix_checkbox, 0, wx.ALL, 5 )

        self.m_fullcase_checkbox = wx.CheckBox( self.m_tester_panel, wx.ID_ANY, u"Full case-folding", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer19.Add( self.m_fullcase_checkbox, 0, wx.ALL, 5 )


        fgSizer42.Add( fgSizer19, 1, wx.EXPAND, 5 )


        fgSizer42.Add( ( 0, 0), 1, wx.EXPAND, 5 )


        fgSizer42.Add( ( 0, 0), 1, wx.EXPAND, 5 )

        self.m_staticline7 = wx.StaticLine( self.m_tester_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer42.Add( self.m_staticline7, 0, wx.EXPAND |wx.ALL, 5 )


        fgSizer42.Add( ( 0, 0), 1, wx.EXPAND, 5 )


        fgSizer42.Add( ( 0, 0), 1, wx.EXPAND, 5 )

        fgSizer391 = wx.FlexGridSizer( 0, 3, 0, 0 )
        fgSizer391.SetFlexibleDirection( wx.BOTH )
        fgSizer391.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_replace_plugin_checkbox = wx.CheckBox( self.m_tester_panel, wx.ID_ANY, u"Use replace plugin", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer391.Add( self.m_replace_plugin_checkbox, 0, wx.ALL, 5 )


        fgSizer42.Add( fgSizer391, 1, wx.EXPAND, 5 )


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
        self.m_reload_button.Bind( wx.EVT_BUTTON, self.on_reload_click )
        self.m_regex_search_checkbox.Bind( wx.EVT_CHECKBOX, self.on_regex_toggle )
        self.m_case_checkbox.Bind( wx.EVT_CHECKBOX, self.on_case_toggle )
        self.m_dotmatch_checkbox.Bind( wx.EVT_CHECKBOX, self.on_dot_toggle )
        self.m_unicode_checkbox.Bind( wx.EVT_CHECKBOX, self.on_unicode_toggle )
        self.m_format_replace_checkbox.Bind( wx.EVT_CHECKBOX, self.on_format_replace_toggle )
        self.m_bestmatch_checkbox.Bind( wx.EVT_CHECKBOX, self.on_bestmatch_toggle )
        self.m_enhancematch_checkbox.Bind( wx.EVT_CHECKBOX, self.on_enhancematch_toggle )
        self.m_word_checkbox.Bind( wx.EVT_CHECKBOX, self.on_word_toggle )
        self.m_reverse_checkbox.Bind( wx.EVT_CHECKBOX, self.on_reverse_toggle )
        self.m_posix_checkbox.Bind( wx.EVT_CHECKBOX, self.on_posix_toggle )
        self.m_fullcase_checkbox.Bind( wx.EVT_CHECKBOX, self.on_fullcase_toggle )
        self.m_replace_plugin_checkbox.Bind( wx.EVT_CHECKBOX, self.on_replace_plugin_toggle )
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

    def on_reload_click( self, event ):
        event.Skip()

    def on_regex_toggle( self, event ):
        event.Skip()

    def on_case_toggle( self, event ):
        event.Skip()

    def on_dot_toggle( self, event ):
        event.Skip()

    def on_unicode_toggle( self, event ):
        event.Skip()

    def on_format_replace_toggle( self, event ):
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

    def on_fullcase_toggle( self, event ):
        event.Skip()

    def on_replace_plugin_toggle( self, event ):
        event.Skip()

    def on_use( self, event ):
        event.Skip()

    def on_cancel( self, event ):
        event.Skip()


###########################################################################
## Class SaveSearchDialog
###########################################################################

class SaveSearchDialog ( wx.Dialog ):

    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Save Search and Replace", pos = wx.DefaultPosition, size = wx.Size( 400,-1 ), style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )

        self.SetSizeHints( wx.Size( 400,-1 ), wx.DefaultSize )

        bSizer9 = wx.BoxSizer( wx.VERTICAL )

        self.m_save_panel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.m_save_panel.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )

        fgSizer24 = wx.FlexGridSizer( 0, 1, 0, 0 )
        fgSizer24.AddGrowableCol( 0 )
        fgSizer24.AddGrowableRow( 1 )
        fgSizer24.SetFlexibleDirection( wx.BOTH )
        fgSizer24.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        gbSizer5 = wx.GridBagSizer( 0, 0 )
        gbSizer5.SetFlexibleDirection( wx.BOTH )
        gbSizer5.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_name_label = wx.StaticText( self.m_save_panel, wx.ID_ANY, u"Search name", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_name_label.Wrap( -1 )

        gbSizer5.Add( self.m_name_label, wx.GBPosition( 0, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_RIGHT, 5 )

        self.m_name_text = wx.TextCtrl( self.m_save_panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer5.Add( self.m_name_text, wx.GBPosition( 0, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5 )

        self.m_comment_label = wx.StaticText( self.m_save_panel, wx.ID_ANY, u"Comment", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_comment_label.Wrap( -1 )

        gbSizer5.Add( self.m_comment_label, wx.GBPosition( 1, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_RIGHT, 5 )

        self.m_comment_textbox = wx.TextCtrl( self.m_save_panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer5.Add( self.m_comment_textbox, wx.GBPosition( 1, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5 )

        self.m_staticline7 = wx.StaticLine( self.m_save_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        gbSizer5.Add( self.m_staticline7, wx.GBPosition( 2, 0 ), wx.GBSpan( 1, 2 ), wx.EXPAND |wx.ALL, 5 )

        self.m_search_label = wx.StaticText( self.m_save_panel, wx.ID_ANY, u"Search", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_search_label.Wrap( -1 )

        gbSizer5.Add( self.m_search_label, wx.GBPosition( 3, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_RIGHT, 5 )

        self.m_search_textbox = wx.TextCtrl( self.m_save_panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        gbSizer5.Add( self.m_search_textbox, wx.GBPosition( 3, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5 )

        self.m_replace_label = wx.StaticText( self.m_save_panel, wx.ID_ANY, u"Replace", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_replace_label.Wrap( -1 )

        gbSizer5.Add( self.m_replace_label, wx.GBPosition( 4, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_RIGHT, 5 )

        self.m_replace_textbox = wx.TextCtrl( self.m_save_panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        gbSizer5.Add( self.m_replace_textbox, wx.GBPosition( 4, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5 )

        self.m_flags_label = wx.StaticText( self.m_save_panel, wx.ID_ANY, u"Flags", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_flags_label.Wrap( -1 )

        gbSizer5.Add( self.m_flags_label, wx.GBPosition( 5, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_RIGHT, 5 )

        self.m_flags_textbox = wx.TextCtrl( self.m_save_panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        gbSizer5.Add( self.m_flags_textbox, wx.GBPosition( 5, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5 )

        self.m_type_checkbox = wx.CheckBox( self.m_save_panel, wx.ID_ANY, u"Literal", wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer5.Add( self.m_type_checkbox, wx.GBPosition( 6, 0 ), wx.GBSpan( 1, 2 ), wx.ALL, 5 )

        self.m_replace_plugin_checkbox = wx.CheckBox( self.m_save_panel, wx.ID_ANY, u"Replace plugin", wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer5.Add( self.m_replace_plugin_checkbox, wx.GBPosition( 7, 0 ), wx.GBSpan( 1, 2 ), wx.ALL, 5 )


        gbSizer5.AddGrowableCol( 1 )
        gbSizer5.AddGrowableRow( 0 )
        gbSizer5.AddGrowableRow( 1 )

        fgSizer24.Add( gbSizer5, 1, wx.EXPAND, 5 )

        fgSizer25 = wx.FlexGridSizer( 0, 4, 0, 0 )
        fgSizer25.AddGrowableCol( 0 )
        fgSizer25.AddGrowableCol( 3 )
        fgSizer25.AddGrowableRow( 0 )
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

        self.Centre( wx.BOTH )

        # Connect Events
        self.m_type_checkbox.Bind( wx.EVT_CHECKBOX, self.on_toggle )
        self.m_replace_plugin_checkbox.Bind( wx.EVT_CHECKBOX, self.on_toggle )
        self.m_apply_button.Bind( wx.EVT_BUTTON, self.on_apply )
        self.m_cancel_button.Bind( wx.EVT_BUTTON, self.on_cancel )

    def __del__( self ):
        pass


    # Virtual event handlers, overide them in your derived class
    def on_toggle( self, event ):
        event.Skip()


    def on_apply( self, event ):
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

        fgSizer37 = wx.FlexGridSizer( 0, 6, 0, 0 )
        fgSizer37.AddGrowableCol( 0 )
        fgSizer37.AddGrowableCol( 4 )
        fgSizer37.SetFlexibleDirection( wx.BOTH )
        fgSizer37.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )


        fgSizer37.Add( ( 0, 0), 1, wx.EXPAND, 5 )

        self.m_edit_button = wx.Button( self.m_load_panel, wx.ID_ANY, u"Edit", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer37.Add( self.m_edit_button, 0, wx.ALL, 5 )

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
        self.Bind( wx.EVT_CLOSE, self.on_close )
        self.m_edit_button.Bind( wx.EVT_BUTTON, self.on_edit_click )
        self.m_delete_button.Bind( wx.EVT_BUTTON, self.on_delete )
        self.m_load_button.Bind( wx.EVT_BUTTON, self.on_load )
        self.m_cancel_button.Bind( wx.EVT_BUTTON, self.on_cancel )

    def __del__( self ):
        pass


    # Virtual event handlers, overide them in your derived class
    def on_close( self, event ):
        event.Skip()

    def on_edit_click( self, event ):
        event.Skip()

    def on_delete( self, event ):
        event.Skip()

    def on_load( self, event ):
        event.Skip()

    def on_cancel( self, event ):
        event.Skip()


###########################################################################
## Class SearchChainDialog
###########################################################################

class SearchChainDialog ( wx.Dialog ):

    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Search Chains", pos = wx.DefaultPosition, size = wx.Size( 470,288 ), style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )

        self.SetSizeHints( wx.Size( 470,288 ), wx.DefaultSize )

        bSizer16 = wx.BoxSizer( wx.VERTICAL )

        self.m_chain_panel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.m_chain_panel.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )

        fgSizer38 = wx.FlexGridSizer( 2, 1, 0, 0 )
        fgSizer38.AddGrowableCol( 0 )
        fgSizer38.AddGrowableRow( 0 )
        fgSizer38.SetFlexibleDirection( wx.BOTH )
        fgSizer38.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_chain_list = SearchChainList(self.m_chain_panel)
        fgSizer38.Add( self.m_chain_list, 1, wx.ALL|wx.EXPAND, 5 )

        fgSizer39 = wx.FlexGridSizer( 0, 6, 0, 0 )
        fgSizer39.AddGrowableCol( 0 )
        fgSizer39.AddGrowableCol( 5 )
        fgSizer39.AddGrowableRow( 0 )
        fgSizer39.SetFlexibleDirection( wx.BOTH )
        fgSizer39.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )


        fgSizer39.Add( ( 0, 0), 1, wx.EXPAND, 5 )

        self.m_add_button = wx.Button( self.m_chain_panel, wx.ID_ANY, u"Add", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer39.Add( self.m_add_button, 0, wx.ALL, 5 )

        self.m_edit_button = wx.Button( self.m_chain_panel, wx.ID_ANY, u"Edit", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer39.Add( self.m_edit_button, 0, wx.ALL, 5 )

        self.m_remove_button = wx.Button( self.m_chain_panel, wx.ID_ANY, u"Delete", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer39.Add( self.m_remove_button, 0, wx.ALL, 5 )

        self.m_cancel_button = wx.Button( self.m_chain_panel, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer39.Add( self.m_cancel_button, 0, wx.ALL, 5 )


        fgSizer39.Add( ( 0, 0), 1, wx.EXPAND, 5 )


        fgSizer38.Add( fgSizer39, 1, wx.EXPAND, 5 )


        self.m_chain_panel.SetSizer( fgSizer38 )
        self.m_chain_panel.Layout()
        fgSizer38.Fit( self.m_chain_panel )
        bSizer16.Add( self.m_chain_panel, 1, wx.EXPAND |wx.ALL, 5 )


        self.SetSizer( bSizer16 )
        self.Layout()

        self.Centre( wx.BOTH )

        # Connect Events
        self.Bind( wx.EVT_CLOSE, self.on_close )
        self.m_add_button.Bind( wx.EVT_BUTTON, self.on_add_click )
        self.m_edit_button.Bind( wx.EVT_BUTTON, self.on_edit_click )
        self.m_remove_button.Bind( wx.EVT_BUTTON, self.on_remove_click )
        self.m_cancel_button.Bind( wx.EVT_BUTTON, self.on_cancel_click )

    def __del__( self ):
        pass


    # Virtual event handlers, overide them in your derived class
    def on_close( self, event ):
        event.Skip()

    def on_add_click( self, event ):
        event.Skip()

    def on_edit_click( self, event ):
        event.Skip()

    def on_remove_click( self, event ):
        event.Skip()

    def on_cancel_click( self, event ):
        event.Skip()


###########################################################################
## Class EditSearchChainDialog
###########################################################################

class EditSearchChainDialog ( wx.Dialog ):

    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Edit/Create Search Chain", pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        bSizer16 = wx.BoxSizer( wx.VERTICAL )

        self.m_chain_panel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.m_chain_panel.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )

        fgSizer38 = wx.FlexGridSizer( 0, 1, 0, 0 )
        fgSizer38.AddGrowableCol( 0 )
        fgSizer38.AddGrowableRow( 1 )
        fgSizer38.SetFlexibleDirection( wx.BOTH )
        fgSizer38.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        sbSizer13 = wx.StaticBoxSizer( wx.StaticBox( self.m_chain_panel, wx.ID_ANY, u"Name" ), wx.VERTICAL )

        self.m_chain_textbox = wx.TextCtrl( self.m_chain_panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        sbSizer13.Add( self.m_chain_textbox, 0, wx.ALL|wx.EXPAND, 5 )


        fgSizer38.Add( sbSizer13, 1, wx.EXPAND, 5 )

        sbSizer14 = wx.StaticBoxSizer( wx.StaticBox( self.m_chain_panel, wx.ID_ANY, u"Chain" ), wx.VERTICAL )

        gbSizer3 = wx.GridBagSizer( 0, 0 )
        gbSizer3.SetFlexibleDirection( wx.BOTH )
        gbSizer3.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        m_search_choiceChoices = []
        self.m_search_choice = wx.Choice( self.m_chain_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_search_choiceChoices, wx.CB_SORT )
        self.m_search_choice.SetSelection( 0 )
        gbSizer3.Add( self.m_search_choice, wx.GBPosition( 0, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5 )

        m_search_listChoices = []
        self.m_search_list = wx.ListBox( self.m_chain_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_search_listChoices, wx.LB_SINGLE )
        self.m_search_list.SetMinSize( wx.Size( 200,-1 ) )

        gbSizer3.Add( self.m_search_list, wx.GBPosition( 1, 0 ), wx.GBSpan( 4, 1 ), wx.ALL|wx.EXPAND, 5 )

        self.m_add_button = wx.Button( self.m_chain_panel, wx.ID_ANY, u"Add", wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer3.Add( self.m_add_button, wx.GBPosition( 0, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_remove_button = wx.Button( self.m_chain_panel, wx.ID_ANY, u"Delete", wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer3.Add( self.m_remove_button, wx.GBPosition( 1, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_up_button = wx.Button( self.m_chain_panel, wx.ID_ANY, u"Up", wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer3.Add( self.m_up_button, wx.GBPosition( 2, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_down_button = wx.Button( self.m_chain_panel, wx.ID_ANY, u"Down", wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer3.Add( self.m_down_button, wx.GBPosition( 3, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )


        gbSizer3.AddGrowableCol( 0 )
        gbSizer3.AddGrowableRow( 4 )

        sbSizer14.Add( gbSizer3, 1, wx.EXPAND, 5 )


        fgSizer38.Add( sbSizer14, 1, wx.EXPAND, 5 )

        fgSizer41 = wx.FlexGridSizer( 0, 4, 0, 0 )
        fgSizer41.AddGrowableCol( 0 )
        fgSizer41.AddGrowableCol( 3 )
        fgSizer41.AddGrowableRow( 0 )
        fgSizer41.SetFlexibleDirection( wx.BOTH )
        fgSizer41.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )


        fgSizer41.Add( ( 0, 0), 1, wx.EXPAND, 5 )

        self.m_apply_button = wx.Button( self.m_chain_panel, wx.ID_ANY, u"Apply", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer41.Add( self.m_apply_button, 0, wx.ALL, 5 )

        self.m_cancel_button = wx.Button( self.m_chain_panel, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer41.Add( self.m_cancel_button, 0, wx.ALL, 5 )


        fgSizer41.Add( ( 0, 0), 1, wx.EXPAND, 5 )


        fgSizer38.Add( fgSizer41, 1, wx.EXPAND, 5 )


        self.m_chain_panel.SetSizer( fgSizer38 )
        self.m_chain_panel.Layout()
        fgSizer38.Fit( self.m_chain_panel )
        bSizer16.Add( self.m_chain_panel, 1, wx.EXPAND |wx.ALL, 5 )


        self.SetSizer( bSizer16 )
        self.Layout()
        bSizer16.Fit( self )

        self.Centre( wx.BOTH )

        # Connect Events
        self.m_add_button.Bind( wx.EVT_BUTTON, self.on_add_click )
        self.m_remove_button.Bind( wx.EVT_BUTTON, self.on_remove_click )
        self.m_up_button.Bind( wx.EVT_BUTTON, self.on_up_click )
        self.m_down_button.Bind( wx.EVT_BUTTON, self.on_down_click )
        self.m_apply_button.Bind( wx.EVT_BUTTON, self.on_apply_click )
        self.m_cancel_button.Bind( wx.EVT_BUTTON, self.on_cancel_click )

    def __del__( self ):
        pass


    # Virtual event handlers, overide them in your derived class
    def on_add_click( self, event ):
        event.Skip()

    def on_remove_click( self, event ):
        event.Skip()

    def on_up_click( self, event ):
        event.Skip()

    def on_down_click( self, event ):
        event.Skip()

    def on_apply_click( self, event ):
        event.Skip()

    def on_cancel_click( self, event ):
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
        self.m_error_panel.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )

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
        self.m_error_text_panel.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )

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


###########################################################################
## Class HtmlDialog
###########################################################################

class HtmlDialog ( wx.Dialog ):

    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Html Dialog", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE|wx.DIALOG_NO_PARENT|wx.RESIZE_BORDER )

        self.SetSizeHints( wx.Size( -1,-1 ), wx.Size( -1,-1 ) )

        bSizer23 = wx.BoxSizer( wx.VERTICAL )

        self.m_content_html = wx.html2.WebView.New(self)
        bSizer23.Add( self.m_content_html, 1, wx.ALL|wx.EXPAND, 5 )


        self.SetSizer( bSizer23 )
        self.Layout()
        bSizer23.Fit( self )

        self.Centre( wx.BOTH )

    def __del__( self ):
        pass


###########################################################################
## Class ColumnDialog
###########################################################################

class ColumnDialog ( wx.Dialog ):

    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Arrange Columns", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        bSizer25 = wx.BoxSizer( wx.VERTICAL )

        self.m_column_panel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.m_column_panel.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )

        fgSizer58 = wx.FlexGridSizer( 2, 1, 0, 0 )
        fgSizer58.AddGrowableCol( 0 )
        fgSizer58.AddGrowableRow( 0 )
        fgSizer58.SetFlexibleDirection( wx.BOTH )
        fgSizer58.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        gbSizer6 = wx.GridBagSizer( 0, 0 )
        gbSizer6.SetFlexibleDirection( wx.BOTH )
        gbSizer6.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        m_column_listChoices = []
        self.m_column_list = wx.ListBox( self.m_column_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_column_listChoices, wx.LB_SINGLE )
        gbSizer6.Add( self.m_column_list, wx.GBPosition( 0, 0 ), wx.GBSpan( 3, 1 ), wx.ALL|wx.EXPAND, 5 )

        self.m_up_button = wx.Button( self.m_column_panel, wx.ID_ANY, u"Up", wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer6.Add( self.m_up_button, wx.GBPosition( 0, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_down_button = wx.Button( self.m_column_panel, wx.ID_ANY, u"Down", wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer6.Add( self.m_down_button, wx.GBPosition( 1, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )


        gbSizer6.AddGrowableCol( 0 )
        gbSizer6.AddGrowableRow( 2 )

        fgSizer58.Add( gbSizer6, 1, wx.EXPAND, 5 )

        fgSizer59 = wx.FlexGridSizer( 1, 4, 0, 0 )
        fgSizer59.AddGrowableCol( 0 )
        fgSizer59.AddGrowableCol( 3 )
        fgSizer59.AddGrowableRow( 0 )
        fgSizer59.SetFlexibleDirection( wx.BOTH )
        fgSizer59.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )


        fgSizer59.Add( ( 0, 0), 1, wx.EXPAND, 5 )

        self.m_apply_button = wx.Button( self.m_column_panel, wx.ID_ANY, u"Apply", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer59.Add( self.m_apply_button, 0, wx.ALL, 5 )

        self.m_cancel_button = wx.Button( self.m_column_panel, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer59.Add( self.m_cancel_button, 0, wx.ALL, 5 )


        fgSizer59.Add( ( 0, 0), 1, wx.EXPAND, 5 )


        fgSizer58.Add( fgSizer59, 1, wx.EXPAND, 5 )


        self.m_column_panel.SetSizer( fgSizer58 )
        self.m_column_panel.Layout()
        fgSizer58.Fit( self.m_column_panel )
        bSizer25.Add( self.m_column_panel, 1, wx.EXPAND |wx.ALL, 5 )


        self.SetSizer( bSizer25 )
        self.Layout()
        bSizer25.Fit( self )

        self.Centre( wx.BOTH )

        # Connect Events
        self.m_up_button.Bind( wx.EVT_BUTTON, self.on_up_click )
        self.m_down_button.Bind( wx.EVT_BUTTON, self.on_down_click )
        self.m_apply_button.Bind( wx.EVT_BUTTON, self.on_apply_click )
        self.m_cancel_button.Bind( wx.EVT_BUTTON, self.on_cancel_click )

    def __del__( self ):
        pass


    # Virtual event handlers, overide them in your derived class
    def on_up_click( self, event ):
        event.Skip()

    def on_down_click( self, event ):
        event.Skip()

    def on_apply_click( self, event ):
        event.Skip()

    def on_cancel_click( self, event ):
        event.Skip()


