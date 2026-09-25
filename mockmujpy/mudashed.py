class dashed(object):
    '''
    mock ipywidgets GUI fit editor for jupiter nb

    a standalon GUI interface for win debugging purposes
    ::
        1. insert the data path, press DL and choose the first run
        2. edit Group0 [Groups ... for multi group] or load a standard groupomg with LG 
        2. insert the run # in the run list; Enter of press RL
    '''


##########################
# INIT
##########################
    def __init__(self,facility='PSI',test='GPS'):
        '''Launches the gui'''
 
        from mockmujpy.aux import make_copy
        from os import getcwd

        self.startuppath = getcwd()
        self.facility = facility
        self.mudashed_width = '900px'   
        self.output_width = '900px'
        self.textheight = '23px'
        self.labelheight = '23px'
        self.buttonheight = '48px'

        self.suite_button_color = '#d6cbbf'
        self.command_button_color = '#97b3ae'
        self.global_button_color = '#c29c94'
        self.model_button_color = '#c0b1ab'
    

        # initialize dashboard, a dictionary
        # self.log = self.suite.console
        #self.root = None # initialize for tkinter
        self.fig_fit = None
        self.fig_fft = None
        writeable_folder = make_copy(test) # if test returns data_dir(acting also as True)
        if writeable_folder: # normal and test mode
            self.test = test # needed in self.board
            if test: self.data_dir = writeable_folder # if test make_copy returns data_dir
            self.board()
        else: # start outside %HOME
            print('please start from a writeable folder')

    def log(self,string):
        """
        redirects log text to self.board_box ipywidgets Output  
        """

        with self.board_box: # just an Output
            # THIS MUST BE print, NOT self.log!
            print(string) 

    def _global(self):
        """
        True for self.dashboard with "globpardicts_guess" key

        """

        return "globpardicts_guess" in self.dashboard.keys()

    def _C12(self):
        """
        True if fit is C1 or C2
        """
        if self._global():
            return any([pardict['flag']=='#' for pardict in self.dashboard["globpardicts_guess"]])
        else:
            return False

    def _C1(self):
        """
        True for C1 fit
        """

        if self._C12() and not self._function_multi():
            return True
        else:
            return False
    def _C2(self):
        """
        True for C2 fit
        """

        if self._C12() and self._function_multi():
            return True
        else:
            return False

    def _function_multi(self):
        """
        True for A21, B21, C2 (global multigroup)
        """

        return any(['function_multi' in pardict.keys() for component in self.dashboard['model_guess'] for pardict in component['pardicts']])

    def _AB21(self):
        """
        True if no hash and function_multi
        """
    
        return self._global() and not self._C12()

    def _multigroup(self):
        """
        True if len(self.suite.groups)>1
        """

        return len(self.suite.groups)>1

    def _multirun(self):
        """
        True if self.suite.nruns>1
        """

        return self.suite.nruns>1

           
    def _on_Fit(self,b):
        """
        invokes mufit and muplotfit extracting their args from the widgets

        .. code::

            the_fit = mufit(self.suite,dashboard_file)
            the_plot = mufitplot(plot_range,the_fit,rotating_frame_frequencyMHz =rotfreq,plot_out=self.figure_box,fig_fit=self.fig_fit)
        """

        import json
        from mockmujpy.aux import mufit
        from mockmujpy.aux import mufitplot
        from mockmujpy.aux import ipyw_warning_dial, show_hide_tab

        OK = False if self._global() else True
        if not OK:
            title = 'Suite & global fit model mismatch'
            # global fit, check that groups and run list agree with dashboard
            if self._AB21() or self._C2():
                if not self._multigroup():
                    msg = 'Groups ...: are empty and a multi group fit was selected\n(some model function contains ;-separated values)'
                elif self._AB21(): OK = True
            if self._C12():
                OK = True
                if not self._multirun:
                    msg = 'Single run in run list submitting multi run fit\n(#-flags in global parameters)'
                    OK = False
            if not OK: # still False after the above changes
                overlay = ipyw_warning_dial(title = title,
                                            message = msg)
                show_hide_tab(overlay,self.on_modal_display_change,self.tab)
        dashbd = self.build_dashed()
        if dashbd and OK: # creates self.dashboard and returns True if no validation raise occurred
            dashboard_file = self.suite.__fitpath__+'dashed.json'
            #self.log('debug mudashed._on_Fit pardicts with # {}'.format(any([True for pardict in self.dashboard['globpardicts_guess'] if pardict['flag']=='#']))) 
            with open(str(dashboard_file),'w',encoding='utf-8') as f:
                json.dump(self.dashboard,f) # mufit wants to read this from a file
            self.board_box.clear_output()
            the_fit = mufit(self.suite,dashboard_file,dash_log = self.log) # writes text to board_box
            #self.figure_box.clear_output()
            plot_range = self.command_1.children[8].value
            rotfreq = self.command_1.children[9].value
            fft_range = self.command_1.children[12].value # not yet in use 
            lb = self.command_1.children[13].value # not yet in use 
            the_plot = mufitplot(plot_range, the_fit, rotating_frame_frequencyMHz = rotfreq, plot_out = self.figure_box, fig_fit = self.fig_fit) # plots in self.figure_box
            self.fig_fit = the_plot.fig
        else: 
            self.log('Build dashboard was unsuccessful, no fit')
        self.tab.selected_index = 2

    def _on_Plot(self,b):
        """
        invokes mufitplot from mudashed extracting its args from the widgets

        .. code::

            the_plot = mufitplot(plot_range,self.the_fit,rotating_frame_frequencyMHz=rotfreq,plot_out=self.figure_box,fig_fit=self.fig_fit)
        """
        
        # read dashed widget values (including guess, rotfreq
        # json.dump again
        # self.figure_box.clear_output()
        # if guess: mufit(plot_range,dashboard_file, no_fit = not guess,out=self.figure_box)
        # mufitplot(plot_range, guess = guess, rotating_frame_frequencyMHz = rotfreq, plot_out = self.figure_box)
        import json
        from mockmujpy.aux import mufit
        from mockmujpy.aux import mufitplot
        if self.build_dashed(): # creates self.dashboard and returns True if no validation raise occurred
            dashboard_file = self.suite.__fitpath__+'dashed.json'
            #self.log('debug mudashed._on_Plot: dumping {}'.format(dashboard_file))
            with open(str(dashboard_file),'w',encoding='utf-8') as f:
                json.dump(self.dashboard,f) # mufit wants to read this from a file
            guess = self.command_1.children[6].value=='Guess'
            self.the_fit = mufit(self.suite,dashboard_file,no_fit = guess, dash_log = self.log) # writes text to board_box
            #self.figure_box.clear_output()
            plot_range = self.command_1.children[8].value
            rotfreq = self.command_1.children[9].value
            the_plot = mufitplot(plot_range, 
                                 self.the_fit, 
                                 rotating_frame_frequencyMHz = rotfreq, 
                                 plot_out = self.figure_box, 
                                 fig_fit = self.fig_fit) # plots in self.figure_box
            self.fig_fit = the_plot.fig


    def _on_FFT(self,b):
        # later
        self.log('Nothing yet!')


    def command2dash(self):
        """
        Mock activates second row self.command_1 of mudashed command_box

        """

        self.log('                   Mock gui, doing nothing')
        self.log('The real mujpy builds Fit btn, range,  etc')
           
    def json2dash(self):
        '''
        builds second stage widgets & value from self.dashboard - LD and LF - or from NG_int.value and self.MN_text_value

        Mock version stops here 
        '''
        self.log('                   Mock gui, doing nothing')
        self.log('The real mujpy builds a widget model editor')
        self.tab.selected_index = 2

    def build_dashed(self):
        """
        reads dashed widget values and builds self.dashboard

            validates
            - values with errors, limits, invalid_err_lim
            uses read_pardict_from_widgets which also validates
            - function math syntax, muvalid
            - 0 <= get_indices < kmax = NG_int.value for global fits and mudashed index of this parameter
        """

        from mujpy.tools.tools import _available_components_, read_pardict_from_widgets
        from mujpy.tools.tools import add_step_limits, widg2pardicts

        self.dashboard = {}
        kids = self.command_1.children
        self.dashboard['version'] = kids[4].value # (string)
        self.dashboard['fit_range'] = kids[2].value # (string)
        self.dashboard['offset'] = str(self.suite.offset)
        glob = self.global_box.children # empty list is false
        if glob: 
            pardicts, kmax, error = widg2pardicts(self.global_box)
            if error: 
                self.log('widg2pardicts error?: {} '+error)
                return False
            #self.log('debug mudashed.build_dashed pardicts with # {}'.format(any([True for pardict in pardicts if pardict['flag']=='#']))) 
            self.dashboard['globpardicts_guess'] = pardicts
        model = []
        components = [self.MN_text.value[i:i + 2] for i in range(0, len(self.MN_text.value), 2)]
        avc = _available_components_()
        nparam = [len(av['pardicts']) for component in components for av in avc if component == av['name']] 
        left, right = self.model_box.children[1].children[0], self.model_box.children[1].children[1] 
        # list of two VBox, to be read, left and right columns
        rowleft, rowright, ki = 0, 0, 0

        for kc,npar in enumerate(nparam): # ks is component index and npar its number of parameters
            # skip (component+legend) and read npar rows
            # writes    name,  None, flag, [function] or function_multi if glob
            #           name, value, flag, [function] otherwise
            compdict = {'name':components[kc],'label':str(kc)}
            pardicts = [] # list of pardict
            if kc%2: # odd, right
                # see json2dash, component widgets:
                rowright += 2 # component and legend rows  
                for kp in range(npar):
                    kmax = kmax if glob else ki
                    pardict = read_pardict_from_widgets(right.children[rowright],kmax) # from widgets
                    if not isinstance(pardict,dict): 
                        self.log('right build_dash pardict {}'.format(pardict)) # is an erro message from read_pardict_from_widgets
                        self.log('------------------------ Is this right?')
                        return False
                    pardicts.append(pardict) # returns a pardict
                    rowright += 1 # incremented only for odd kc
                    ki +=1 # internal dashed parameter index incremented always
            else: # even, 0, 2, ... left
                rowleft += 2 # component and legend rows
                for kp in range(npar):
                    kmax = kmax if glob else ki
                    pardict = read_pardict_from_widgets(left.children[rowleft],kmax)
                    if not isinstance(pardict,dict): 
                        self.log('debug left build_dash pardict {}'.format(pardict))
                        self.log('------------------------ Is this right?')
                        return False# is an erro message from read_pardict_from_widgets
                    pardicts.append(pardict) # returns a pardict
                    rowleft += 1 # incremented only for even kc
                    ki +=1 # internal dashed parameter index incremented always
            compdict['pardicts'] = pardicts
            model.append(compdict)
        if not glob:
            self.dashboard['model_guess'] = add_step_limits(model) # adds errors, limits, pospar 
        else:
            self.dashboard['model_guess'] = model
        return True

    def _on_fit_type(self,change):
        '''
        toggle NG disabled False/enabled True and set self.NG_int.value = 0/1

        '''

        if change['new'] == 'sequential fit':
            self.NG_int.value = 0
            self.NG_int.disabled = True
        else:
            self.NG_int.value = 1
            self.NG_int.disabled = False

    def _on_LL(self,change):
        '''
        Load Last dashed.json, if it exists
        '''

        import json
        import os
        from mockmujpy.aux import check_dashboard_json

        file_json = self.suite.__fitpath__+'dashed.json'
        if os.path.isfile(file_json):
            with open(str(file_json),'r',encoding='utf-8') as f:
                self.dashboard = json.load(f) # copies json dict to self.dashboard
            ck = check_dashboard_json(self.dashboard)
            if ck:
                del self.dashboard
                self.log(ck+' typo in '+file_json)
                self.tab.selected_index = 2
                return
            self.log('Loaded model from {}'.format(file_json))
            if not self.command_1.children: 
                self.command2dash()
            self.json2dash() # builds widgets for this model
        else:
            self.tab.selected_index = 2
            self.log('>>>>>>>>>>>>>>>> file dashed.json not found')
 
    def _on_LF(self,b):
        '''
        Choose fit model to load from ./fit/ folder
        '''

        from mockmujpy.aux import check_dashboard_json 
        import json
        import os

        file_json = self.LF_button.value
        if os.path.isfile(file_json):
            if file_json[-4:]=='json':
                with open(str(file_json),'r',encoding='utf-8') as f:
                    self.dashboard = json.load(f) # copies json dict to self.dashboard
            ck = check_dashboard_json(self.dashboard)
            if ck:
                del self.dashboard
                self.log(ck+' typo in '+file_json)
                self.tab.selected_index = 2
                return
            self.log('Loaded model from {}'.format(file_json))
            if not self.command_1.children: self.command2dash()
            self.json2dash() # builds widgets for this model
        else:
            self.tab.selected_index = 2
            self.log('no valid json file was selected {}'.format(file_json))
 
    def _on_MN(self,change):
        '''
        if model_box is empty adds third stage widgets else edits model_box
        '''
    
        # command box, global box: VBox of rows (HBox)
        # model_box: HBox of two columns (VBox) of components (VBox) of rows, pardicts (HBox) of component widgets
        from mockmujpy.aux import validmodel, find_model_difference, _available_components_
        from json import loads as str2lst
        from ipywidgets import Text, IntText, Layout, Button, HBox,  \
                               VBox, ToggleButtons, Label, FloatText
        from mockmujpy.aux import ipyw_radio_dial, ipyw_warning_dial, show_hide_tab

        if change['type'] == 'change' and change['name'] == 'value':

            go = True
            model = change['new'].strip() # removes accidental lead & trail blanks
            #self.log('debug mudashed._on_MN change["new"] {}'.format(model))
            if not validmodel(model):
                overlay = ipyw_warning_dial(title = 'Wrong model syntax',
                                            message = '{} not made of valid components!'.format(model))
                self.MN_text.unobserve(self._on_MN,names='value')
                self.MN_text.value = ''
                self.MN_text.observe(self._on_MN,names='value') # observe again
                show_hide_tab(overlay,self.on_modal_display_change,self.tab)
                go = False
            if self.NG_int.value==1: # tarting route, butuspicious! forgot to set?
                set.tab.children[3].children[3], widg = ipyw_yes_no_dial(title = 'Check!',
                                                                         message = "only NG=1 global parameter\ndon't you need more?")
                go = not widg.value # widg.value is yes I do need more, no need can continue
                self.tab.children[3].children[3].layout.observe(self.on_modal_display_change,names='display')
                setattr(self.tab.children[3].children[3].layout, 'display', 'flex')
            else: # includes also starting stage!
                oldmodel = change['old']
                indices = find_model_difference(oldmodel,model) # returns 0 also if old is empty (initial stage) and new is 2 or more components!

                if len(indices)==0: # new model in the starting stage (no old model)!
                    if len(self.model_box.children)==0: go = True # starting stage only               
                if oldmodel != '' and model and go: # edit the dash
                    k = indices[0]
                    indices = [abs(j)-1 for j in indices] if k<0 else indices
                    action = 'Add after, in' if k>0 else 'Remove from'
                    m_c = model if k>0 else oldmodel
                    cc = [m_c[i:i+2] for i in range(0, len(m_c), 2)]
                    #self.log('debug mudashed._on_MN cc {}'.format(cc))
                    components = [(cc[i],i) for i in indices] # indices are 
                    if len(indices)>1: #decide which
                        set.tab.children[3].children[3], widg = ipyw_radio_dial(components,title='{} model {}'.format(action,model))
                        ki = widg.index
                        self.tab.children[3].children[3].layout.observe(self.on_modal_display_change,names='display')
                        setattr(self.tab.children[3].children[3].layout, 'display', 'flex')
                    elif len(indices)==1: # single component
                        ki = abs(k)
                    else: # complez
                        set.tab.children[3].children[3], widg = ipyw_yes_no_dial(title = '{} NEW EMPTY model'.format(model),
                                                                                 message = 'Is this OK?\n(NO keeps the old model)')
                        go = not widg.value # widg.value is yes I do need more, no need can continue
                        self.tab.children[3].children[3].layout.observe(self.on_modal_display_change,names='display')
                        setattr(self.tab.children[3].children[3].layout, 'display', 'flex')
                    if k<0: # remove component  len(indices)==1 an
                        del self.dashboard['model_guess'][ki]
                    else: # add component
                        #self.log('debug mudashed._on_MN cc[k] {}'.format(cc[k]))
                        for c in _available_components_():
                            if c['name'] == cc[k]: component = c
                        for j,p in enumerate(component['pardicts']):
                            component['pardicts'][j]['flag']='=' if 'globpardicts_guess' in self.dashboard else '~'
                        #self.log('debug mudashed._on_MN component {}'.format(component))
                        self.dashboard['model_guess'].insert(ki,component)
                        self.log('{}: inserted empty component {} in position {}'.format(m_c,cc[k],k))
                elif len(self.model_box.children)==0: # starting route
                    # rebuilds self.dashboard from widgets
                    if self.build_dashed():
                        self.command2dash() # create command_box from scratch
                # a complex new model edit with a yes askyesno answer jumps here 
                self.json2dash()  # always, if model and OK

    def _on_RL(self,change):
        """Traps the text widget's 'Enter' press safely."""

        if isinstance(change, dict) and isinstance(change.get('new'), dict):
            return
        runlist = change['new'] if isinstance(change, dict) else change
        if not runlist:
            return
            
        # Call the core worker function directly
        self.execute_suite_processing(runlist)

    def execute_suite_processing(self,runlist):
        """
        _on_RL and _on_button_RL real callback, decoupled to avoid sudden cascade of nested GUI updates that kill Windowsi

        
        start suite from run list input, checks path file exists

        beware: as of ipywidgets v. 8.1.5 this continuous_update=False is a bit of a mess
                change['new'] is initially a dict instead of a value
                and Enter triggers a double call.
                proceeds only id change['new'] is not a dict
        """
        
        import os
        from mockmujpy.aux import suite
        from mockmujpy.aux import derun, get_title, get_gtotals, get_grouping 
        from mockmujpy.aux import check_multigroup
        from mockmujpy.aux import ipyw_warning_dial, ipyw_path_file_dial, show_hide_tab
        from numpy import all

        self.log('runlist = {}'.format(runlist))
        datafile = self.suite_box.children[2].children[2].value  # path Text value

        try:
            grp = self.suite_box.children[1].children[1].value
            forward, backward = grp.split('-')
            if all(get_grouping(forward)>=0) and all(get_grouping(backward)>=0):
                grp_calib = [{'forward':forward, 
                          'backward':backward, 
                          'alpha':float(self.suite_box.children[1].children[2].value)}]
            else:
                raise NameError('No Group0')
        except ValueError as e:
            text = 'Exception {}'.format(e)
            text += '\nGroup0 syntax error: {}'.format(grp)
            overlay = ipyw_warning_dial(title = "Watch Group0 syntax",
                                        message = text)
            show_hide_tab(overlay,self.on_modal_display_change,self.tab)
            return
        grp = self.suite_box.children[1].children[4].value
        alph = self.suite_box.children[1].children[5].value 
        if grp:
            # these are potentially a ;-separated multigroup strings
            groups = grp.split(';')
            alphas = alph.split(';')
            #for group, alpha in zip(groups,alphas):
            for group, alpha in zip(groups,alphas):
                grp_c = check_multigroup(group,alpha)
                if isinstance(grp_c, str):
                    overlay = ipyw_warning_dial(title = "Watch Groups ... syntax",
                                                message = grp_c)
                    show_hide_tab(overlay,self.on_modal_display_change,self.tab)
                    return
                grp_calib.append(grp_c)

        offset = self.suite_box.children[1].children[8].value
        if os.path.isfile(datafile):
            if runlist:
                self.suite = suite(datafile , runlist , grp_calib , offset , 'input setuppath not used' ,console=self.log) #startuppath is set in suite
                # self.log info
                if self.suite.loadfirst: # suite loaded the data
                    # inserted the hold_trait_notification to preserve Windows:
                    with self.suite_box.hold_trait_notifications():
                        starttime_options = [' '.join(self.suite._the_runs_[k][0].get_timeStart_vector()) for k in range(self.suite.nruns)]
                        starttime_options.insert(0,'Run start times')
                        self.suite_box.children[0].children[0].options = starttime_options
                        self.suite_box.children[0].children[0].value = starttime_options[1]

                        stoptime_options = [' '.join(self.suite._the_runs_[k][0].get_timeStop_vector()) for k in range(self.suite.nruns)]
                        stoptime_options.insert(0,'Run stop times')
                        #self.log('nruns {}, SD_options = {}'.format(self.suite.nruns,starttime_options))
                        self.suite_box.children[0].children[1].options = stoptime_options
                        self.suite_box.children[0].children[1].value = stoptime_options[1]

                        title_options = [get_title(self.suite._the_runs_[k][0]) for k in range(self.suite.nruns)]
                        title_options.insert(0,'Titles')
                        self.suite_box.children[0].children[2].options = title_options
                        self.suite_box.children[0].children[2].value = title_options[1] 

                        comment_options = [self.suite._the_runs_[k][0].get_comment() for k in range(self.suite.nruns)]
                        comment_options.insert(0,'Comments')
                        self.suite_box.children[0].children[3].options = comment_options 
                        self.suite_box.children[0].children[3].value = comment_options[1]

                        totalcounts, groupcounts, nsbin, maxbin = get_gtotals(self.suite)
                        self.suite_box.children[0].children[4].value = nsbin
                        self.suite_box.children[0].children[5].value = maxbin 
                        goptions = ['Group counts']
                        toptions = ['Total counts']
                        runs,e = derun(runlist)
                        for runadd,groupcount,totalcount in zip(runs,groupcounts,totalcounts):
                            run = ','.join([run for run in runadd])
                            for k,gc in enumerate(groupcount):
                                counts = ': '+gc
                                goptions.append(run+'.'+str(k)+counts)
                            toptions.append(run+': '+totalcount[0])
                        
                        self.log('suite __fitpath__ is {}'.format(self.suite.__fitpath__))
                        self.suite_box.children[1].children[6].options = goptions
                        self.suite_box.children[1].children[7].options = toptions
                        self.command_box.children[0].children = self.command_0.children
                        #self.LF_modal, self.LF_button =  ipyw_path_file_dial(
                        #        self.LF_button,self._on_LF,
                        #        path = self.suite.__fitpath__,
                        #        filter_pattern = ['*.json'],
                        #        title = '<b>1-click select</b>')
                        #self.LF_modal.layout.observe(self.on_modal_display_change, names = 'display')

                else:
                    overlay = ipyw_warning_dial(title = 'Suite error',
                                                message = 'No runs loaded, runlist {}?'.format(runlist))
                    show_hide_tab(overlay,self.on_modal_display_change,self.tab)
            else:
                self.log('Please specify runlist')
        else:
            self.log('File {} not found'.format(datafile))
            self.log('paths must be either in startup path and below or absolute')

    def _on_LG(self,b):
        """
        group dict file load 

        """

        import os
        from ast import literal_eval as aeval

        groupfile = self.LG_button.value
        if groupfile:
            with open(str(groupfile),"r",encoding='utf-8') as f:
                grp_calib = f.readline()
            groupshnd1 = None
            for kg, group in enumerate(aeval(grp_calib)):
                alpha = str(group['alpha'])
                groupshnd = group['forward']+'-'+group['backward']
                if kg == 0:
                    self.suite_box.children[1].children[1].value = groupshnd
                    self.suite_box.children[1].children[2].value = alpha
                elif kg == 1:
                    alpha1 = alpha
                    groupshnd1 = groupshnd
                else:
                    alpha1 += ';'+alpha
                    groupshnd1 += ';'+groupshnd
            if groupshnd1:
                grp_txt = self.suite_box.children[1].children[4]
                alpha_txt = self.suite_box.children[1].children[5]
                grp_txt.unobserve(self._on_multigroup,names='value')
                alpha_txt.unobserve(self._on_multigroup,names='value')
                grp_txt.value = groupshnd1
                alpha_txt.value = alpha1
                grp_txt.observe(self._on_multigroup,names='value')
                alpha_txt.observe(self._on_multigroup,names='value')

    def on_modal_display_change(self,change):
        """switch tabs when change['new'] toggles 'flex' or 'none' """
        if change['new'] == 'flex':
            self.tab.selected_index = 3  # Passa alla scheda del modal
        elif change['new'] == 'none':
            self.tab.selected_index = 0  # Torna alla scheda principale

    def _on_RL_button(self,b):
        """Directly triggers execution without resetting the widget text."""

        # Directly read the current value
        runlist = self.suite_box.children[2].children[5].value
        
        # Call the core worker function directly instead of mutating the widget value
        self.execute_suite_processing(runlist)

    def _on_DL(self,b):
        """prototype data file written in path widget"""

        import os

        datafile = self.DL_button.value
        if datafile:
            self.suite_box.children[2].children[2].value = datafile 

    def _on_multigroup(self,change):
        """
        inserted further goups, check syntax and check that RL is pressed (again?)
        """

        from mockmujpy.aux import check_multigroup, ipyw_warning_dial, show_hide_tab
        if change['owner'].tooltip[0] == 'f':
            remind = True
            grp = change['new']
            alph = self.suite_box.children[1].children[5].value
        else:
            remind = False
            alph = change['new']
            grp = self.suite_box.children[1].children[4].value
        run_list = self.suite_box.children[2].children[5].value
        OK = len(grp.split(';'))==len(alph.split(';'))
        if grp and run_list and OK:
            grp_c = check_multigroup(grp,alph) # simply a syntax pre check 
            if isinstance(grp_c, str) and remind:
                overlay = ipyw_warning_dial(title = 'Warning, group syntax',
                                            message = grp_c)
                show_hide_tab(overlay,self.on_modal_display_change,self.tab)
                return
            overlay = ipyw_warning_dial(title = 'REMEMBER!',
                                        message = 'RL to reload data!')
            show_hide_tab(overlay,self.on_modal_display_change,self.tab)

    def board(self):
        '''
        gui entry point, draws the gui editor in 2 stages, suite, model selection

        each stage a new box is added to the gui:
        ::
            * suite box input and information
            * command box 
            *    model selection
        '''

        from ipywidgets.widgets import Output, ToggleButtons, Button, Label, Layout, Text, IntText
        from ipywidgets.widgets import Dropdown, FloatText, HBox, VBox, HTML, Box, Image, Textarea
        from ipywidgets.widgets import Tab
        from mockmujpy.aux import _available_components_, ipyw_path_file_dial, ValueButton
        from datetime import datetime
        import os
        from importlib import resources

        ##################################################################################################
        # Use from scratch
        # Three stages and four boxes, suite, command_, global_ and method_ box
        # first suite box, musuite is instantiated by a run list change [press Enter]
        # second first row of command box,
        # ToggleButtons select sequential/global fit 
        # IntText number of global parameter(NG) [default 0, disabled=True], update before 
        #   - ToggleButton.on_click toggles NG=1, disable=False
        # MN_text select model acronym [press Enter], LL load last fit/dashed.json, LF selects fit/*.json  
        #   - MN, LL, LF triggers third where
        #     self.command2dash() self.json2dash() build model_box, global_box children for all three cases
        # [widgets with tooltips, some actions preceeded by two letter label]
        ###################################################################################################
   
                        
                

##########################
# initiate gui first stage
##########################   
        """
        tabs Fit Log Help About
        info [SD] Text^ [PD] Text^ [TT] Text^ [CM] Text^ [NS] Text^ [MB] Text^ 
             [3]  15    [3]  15         20         20         10         10    tot 90
             [GR] Text α FloatText [GR] Text α FloatText
                  16   3  16            16   3  16        tot 70
             [#]  Path Text DLButton Run List Text* OF IntText  
             [8]  5    24   10       10       16    3  10       tot 78

        self.suite_box [^ disabled, Buttons all on_click, * observe]
        """


        info_width = ['16%','16%','27%','27%','6%','8%']
        SD_drop = Dropdown(options = ['Run start times'], value='Run start times',
                        layout = Layout(width=info_width[0]),
                        tooltip = 'run start times',
                           )# this is not disabled = True, but has no observe
        SD_drop.add_class("custom-grey-dropdown") #  and is color gray
        PD_drop = Dropdown(options = ['Run stop times'], value='Run stop times',
                        layout = Layout(width=info_width[1]),
                        tooltip = 'run stop time')
        PD_drop.add_class("custom-grey-dropdown") #  and is color gray
        TL_drop = Dropdown(options = ['Titles'], value='Titles',
                        layout = Layout(width=info_width[2]),
                        tooltip = 'titles')
        TL_drop.add_class("custom-grey-dropdown") #  and is color gray
        CM_drop = Dropdown(options = ['Comments'], value='Comments',
                        layout = Layout(width=info_width[3]),
                        tooltip = 'comments')
        CM_drop.add_class("custom-grey-dropdown") #  and is color gray
        NS_text = Text(value='',
                        layout = Layout(width=info_width[4]),
                        tooltip = 'ns/bin',
                        disabled = True)
        MB_text = Text(value='0',
                          layout=Layout(width=info_width[5]),
                          tooltip='max bins',disabled = True)

        suite_info = HBox([
                       SD_drop,
                       PD_drop,
                       TL_drop,
                       CM_drop,
                       NS_text,
                       MB_text
                       ])

        groups_width=['7%','15%','7%','18%','14%','10%']
        GR_label = [Label('Group 0:',layout=Layout(width=groups_width[0])),
                    Label('Groups ...:',layout=Layout(width=groups_width[0]))]
        GR_text =  [Text(value='3-4',layout=Layout(width=groups_width[1]),tooltip = '3-4\n2,3-4,1\n[fwd-bwd]'),
                    Text(value='',placeholder='option, or LG',continuous_update=False,layout=Layout(width=groups_width[1]),tooltip = 'fw1-bw1;fw2-bw2')]
        GR_text[1].observe(self._on_multigroup,names='value')
        alpha_text = [Text(value='1.0',layout=Layout(width=groups_width[2]),tooltip = 'group α'),
                      Text(value='1.0',continuous_update=False,layout=Layout(width=groups_width[2]),tooltip = 'group α')]
        alpha_text[1].observe(self._on_multigroup,names='value')
        GT_dropdown = Dropdown(value = 'Group counts',
                               options = ['Group counts','Run: 0, 0'],
                               #disabled = True,
                               layout = Layout(width=groups_width[3]))
        TO_dropdown = Dropdown(value = 'Total counts',
                               options = ['Total counts','Run: 0'],
                               layout = Layout(width=groups_width[4]))
        value = 20 if self.facility == 'PSI' else 7
        OF_inttext = IntText(value = value,
                             description = 'OF',
                             layout = Layout(width=groups_width[5]),
                             tooltip = 'first good bin')
        OF_inttext.style.description_width = '30%'


        #GT_text = [Text(value='0',layout=Layout(width=groups_width[3]),tooltip='Group total',disabled = True),
        #           Text(value='0',layout=Layout(width=groups_width[7]),tooltip='Group total',disabled = True)]

        suite_groups = HBox([
                            GR_label[0],
                            GR_text[0],
                            alpha_text[0],
                            GR_label[1],
                            GR_text[1],
                            alpha_text[1],
                            GT_dropdown,
                            TO_dropdown,
                            OF_inttext
                            ])
 
        runs_width = ['7%','4%','54%','5%','16%']
        grouppath = self.startuppath+os.path.sep+'groups'+os.path.sep
        self.LG_button = ValueButton(description='LG',
                           tooltip = 'Groups file selection',
                           layout = Layout(width=runs_width[0]))
        LG_modal, self.LG_button = ipyw_path_file_dial(
                self.LG_button,self._on_LG,
                path = grouppath,
                filter_pattern = '*.grp',
                title = '<b>1-click select</b>')
        LG_modal.layout.observe(self.on_modal_display_change, names = 'display')
        LG_modal.layout.width='100%'

        self.LG_button.style.button_color = self.suite_button_color
        
        path_value = self.data_dir if self.test else os.path.join(self.startuppath,'data') if 'suite' not in self.__dir__() else self.suite.__datapath__
        self.DL_button = ValueButton(description='DL',
                           tooltip = 'Data file selection',
                           layout = Layout(width=runs_width[0]))
        DL_modal, self.DL_button =  ipyw_path_file_dial(
                self.DL_button,self._on_DL,
                path = path_value,
                filter_pattern = ['*.bin','*.root','*.mdu','*.nxs'],
                title = '<b>(1-click select</b>')
        DL_modal.layout.observe(self.on_modal_display_change, names = 'display')
        

        #if self.test:
        #    RL_value = '822' if self.test=='GPS' else '3561' if self.test=='LEM' else '126645'
        #else:
        RL_value = ''
        RL_text = Text(value=RL_value,
                       placeholder='run #s, Enter or RL',
                      tooltip='e.g. 822\nor 822,823:827:-1',
                      layout=Layout(width=runs_width[4]),
                      continuous_update = False)
        RL_text.observe(self._on_RL,names='value')
        RL_button = Button(description='RL',
                           tooltip = 'Load run list',
                           layout = Layout(width=runs_width[0]))
        RL_button.on_click(self._on_RL_button)
        RL_button.style.button_color = self.suite_button_color

        suite_runs = HBox([
                        self.LG_button,
                        Label(value='path',
                            layout=Layout(width=runs_width[1])),
                        Text(value = path_value,
                            placeholder = 'to proto-data-file (enables DL)', 
                            tooltip = 'path to proto-run/n(from start path\nor absolute',
                            layout = Layout(width=runs_width[2]),
                            continuous_update = False),
                        self.DL_button,
                        Label(value='run list',
                              layout=Layout(width=runs_width[3])),
                        RL_text,
                        #Label(value='OF',
                        #      layout = Layout(width=runs_width[5]),tooltip = 'first good bin'),
                        RL_button
                        ])
                            
        self.suite_box = VBox([suite_info,suite_groups,suite_runs],layout=Layout(width=self.mudashed_width,border='1.5px solid DarkGoldenrod'))
        
        custom_css = """
                      <style>  
                        .jp-OutputArea-output pre { white-space: pre !important; }
                        .container { width:100% !important; }
                        /* background and text color for unselected ToggleButtons */
                        .widget-toggle-button {
                            background-color: #b5d6d0;
                            color: #888888 ;
                        }

                        /* background and text color for SELECTED ToggleButtons (active) */
                        .widget-toggle-button.mod-active {
                            background-color: #97b3ae;
                            color: #000000;
                            border-color: #4b5957 ;
                        }           
                        /* SD_ PD_ TL_ CM_ dropdown in nsuite_info */
                        .custom-grey-dropdown select option {
                            color: grey !important;
                        } 
                    </style>

                    """
        
        # 2. Inietta il CSS nel notebook tramite un widget HTMLi
        css_widget = HTML(value=custom_css)
        display(css_widget)
        command_width = ['38%','21%','11%','14%','8%','8%']
        self.figure_box = Output(layout=Layout(width='100%',height='410px'))# width='900px'
        self.board_box = Output(layout=Layout(width='100%',height='650px',overflow_y='auto'))
        fit_type = ToggleButtons(options = ['sequential fit','global fit'],
                                 value = 'sequential fit',
                                 tooltips = ['A1 A20 B1 B20\nsingle asymmetry fit','A21 B21 C1 C2\nmulti asymmetries fit'],
                                 layout = Layout(width=command_width[0]))
        fit_type.observe(self._on_fit_type,names='value')
        fit_type.style.description_width='0%'

        self.NG_int = IntText(value = 0,description='global parameters',
                        tooltip = 'parameters number',
                        layout = Layout(width=command_width[1],height=self.textheight),
                        disabled = True)
        self.NG_int.style.description_width = '58%'

        MN_label = Label(value='model acronym',layout=Layout(width=command_width[2]))
        self.MN_text = Text(value = '',
                            placeholder = 'xx, Enter to lauch',
                            tooltip = 'e.g. mg\n   almgml',
                            layout = Layout(width=command_width[3],height=self.textheight),
                            continuous_update=False) # requires CR
        self.MN_text.observe(self._on_MN,names='value')

        LL_button = Button(description = 'LL',
                           tooltip = 'Load last model\nif exists',
                           layout = Layout(width=command_width[4]))
        LL_button.style.button_color = self.command_button_color
        LL_button.on_click(self._on_LL)
        
        fit_path = os.path.join(self.startuppath,'fit') if 'suite' not in self.__dir__() else self.suite.__fitpath__
        self.LF_button = ValueButton(description = 'LF',
                           tooltip = 'Load fit file',
                           layout = Layout(width=command_width[5]))
        self.LF_button.style.button_color = self.command_button_color
        self.LF_modal, self.LF_button =  ipyw_path_file_dial(
                self.LF_button,self._on_LF,
                path = fit_path,
                filter_pattern = ['*.json'],
                title = '<b>1-click select</b>')
        self.LF_modal.layout.observe(self.on_modal_display_change, names = 'display')

        layout = Layout(width=self.mudashed_width,border='1px solid CadetBlue')
        board_width='930px'
        command_0 = HBox([])
        self.command_0 = HBox([fit_type,self.NG_int,MN_label,self.MN_text,LL_button,self.LF_button],layout={'width':self.mudashed_width})
        self.command_1 = HBox([],layout={'width':self.mudashed_width})
        self.command_box = VBox([command_0,self.command_1],layout=layout)
        #self.command_box.add_class("command_box_style",layout=layout)
        self.global_box = VBox([],layout=Layout(width=self.mudashed_width,border='1px solid Coral'))
        #self.global_box.add_class("global_box_style",layout=layout)
        self.model_box = VBox([],layout=Layout(width=self.mudashed_width,border='1px solid RosyBrown')) # filled with neft and right columns
        #self.model_box.add_class("model_box_style",layout=layout)
        dash = VBox([self.suite_box,
                     self.command_box,
                     self.global_box,
                     self.model_box],
                    layout={'width':'100%','border':self.model_button_color}) # 'width':board_width
        #panels = HBox([dash,VBox([self.figure_box,self.board_box])],layout={'width':'100%'})
        dash.add_class("inter-font-container")
        self.fetch_box(Text(value='Mock fetch data'))
        help_text = 'Available components,  by unique two letters, and their Minuit parameters, (x is a time array [μs])'
        for c in _available_components_():
            help_text += '\n{}: {}'.format(c['name'],c['tip'].replace('\n    ',' ',2)) 
        help_box.value = help_text
        logo_file = resources.files('mujpy.logo').joinpath("logo.png")
        logo_image = logo_file.read_bytes()
        logo = Box([Image(value=logo_image)],layout=Layout(width='114px',height='100px'))
        about_text = " Mock mujpy        "+'v'+'3.0.demo'
        about_text += "\npython μSR data analysis"
        about_text += "\nby R. De Renzi 2017-2026"
        about_text += "\n_________________________________________________"
        about_text += "\ncontributors, direct and indirect"
        about_text += "\nmusr2py: P. Bonfà (wrapper), A. Amato, A. Raselli"
        about_text += "\ndynamical KT: G. Allodi"
        about_text += "\nideas stolen from: A. Suter (musrfit)"
        about_text += "\ncgi-bin fetch and ideas: Z. Salman"
        about_text += "\nroot by uproot (muroot2py wrapper)"
        about_text += "\nnexus by nexusformat /muisis2py wrapper)"

        about = HBox([logo,Textarea(
            value = about_text,
            disabled=True, # Prevents users from editing the text
            layout=Layout(width='786px',height='160px')           #,height='250px' # Height constraint triggers the scrollbar
            )],layout=Layout(width='900px'))
        dialog = VBox([LG_modal,DL_modal,self.LF_modal,HBox([])],layout=Layout(width='786px',height='100%'))
        self.tab = Tab([dash,self.fetch_box,self.board_box,dialog,help_box,about],layout=Layout(width='940px'))
        self.tab.add_class(custom_css)
        self.tab.titles = ['Fit','Fetch data','Log','Dialogs','Help','About']
        self.tab.selected_index = 0
        display(self.tab)
        # Button( icon = 'fa-trash' #, <i class="fa-thin fa-trash"></i>
        #https://stackoverflow.com/questions/60116974/what-is-the-icon-argument-for-ipywidgets-button
