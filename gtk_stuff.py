# coding=utf-8
# Copyright (c) 2010, Marco Candrian
""" graphical stuff (GTK) """


import pygtk
pygtk.require('2.0')
import gtk
import pango

import os
import platform
import time

#own import
import cfg
import helper
import ra_gnuplot
#import ra_matplot


##########################################
# Message Box{{{
##########################################
def message_dialog(parent, string):
    """ simple message dialog """
    dialog = gtk.MessageDialog(parent, gtk.DIALOG_MODAL |
                gtk.DIALOG_DESTROY_WITH_PARENT,gtk.MESSAGE_INFO, gtk.BUTTONS_OK, string)

    dialog.run()
    dialog.destroy()

##########################################}}}
# Main Window{{{
##########################################
def main_window():
    """ main window (display) """
    def delete_event(widget, event, data=None):
        """ Delete Event """
        return False

    def destroy(widget, data=None):
        """ Detroy """
        gtk.main_quit()

    #Event Callbacks
    def event_simple_cb(widget, event, data):
        """ general event callback function """
        if data == "para":
            (cmd1, cmd2) = akkupara_dialog()
            if not cmd1:
                return

            cfg.COMMAND_ABORT = False #reset

            helper.akkumatik_command(cmd1, "Übertragen")
            cfg.FLOG.write("Sending Command %s \"Übertragen\"\n" % cmd1)

            if cmd2:
                time.sleep(0.6) #else threads may get out of order somehow
                helper.akkumatik_command(cmd2, "Start")
                cfg.FLOG.write("Sending Command %s \"Start\"\n" % cmd2)
        elif data == "chart":
            ra_gnuplot.gnuplot()
            #ra_matplot.matplot()
        elif data == "recycle":
            cfg.FILE_BLOCK = True #stop reading in files (read_line)
            cfg.FSER.close()
            #truncates old file
            cfg.FSER = helper.open_file(cfg.TMP_DIR + '/serial-akkumatik.dat', 'w+b')
            cfg.FLOG.write("%s opened (new or create binary)" % \
                    cfg.TMP_DIR + '/serial-akkumatik.dat\n')
            cfg.FILE_BLOCK = False
            message_dialog(cfg.GTK_WINDOW, "Alte serielle Daten wurden geloescht.")
            return

        elif data == "quit":
            gtk.main_quit()

    def event_simple_enter_cb(widget, event, data):
        """ general event enter function """
        widget.get_child().set_from_file(cfg.EXE_DIR + \
                "/bilder/"+data+"_hover.png")

    def event_simple_leave_cb(widget, event, data):
        """ general event leave function """
        widget.get_child().set_from_file(cfg.EXE_DIR + "/bilder/"+data+".png")

    #AKKU OUTPUT Callbacks
    def eventcb(widget, event, data):
        """ callback function - eventboxes containing Akku-Ausgang pics """

        #True later on generate_output_strs() again
        cfg.START_STOP.set_sensitive(False)

        if data == "1":
            cfg.IMG_AKKU1.set_from_file(cfg.EXE_DIR + "/bilder/Ausgang.png")
            cfg.IMG_AKKU2.set_from_file(cfg.EXE_DIR + "/bilder/Ausgang_off.png")
            cfg.GEWAEHLTER_AUSGANG = 1
        else:
            cfg.IMG_AKKU2.set_from_file(cfg.EXE_DIR + "/bilder/Ausgang.png")
            cfg.IMG_AKKU1.set_from_file(cfg.EXE_DIR + "/bilder/Ausgang_off.png")
            cfg.GEWAEHLTER_AUSGANG = 2

    def event_enter_cb(widget, event, data):
        """ hover effect - hover when _off """
        if data == "1":
            if cfg.GEWAEHLTER_AUSGANG == 2:
                cfg.IMG_AKKU1.set_from_file(cfg.EXE_DIR + \
                        "/bilder/Ausgang_hover.png")
        else:
            if cfg.GEWAEHLTER_AUSGANG == 1:
                cfg.IMG_AKKU2.set_from_file(cfg.EXE_DIR + \
                        "/bilder/Ausgang_hover.png")
    def event_leave_cb(widget, event, data):
        """ hover effect 2 - reset """
        if data == "1":
            if cfg.GEWAEHLTER_AUSGANG == 1:
                cfg.IMG_AKKU1.set_from_file(cfg.EXE_DIR + "/bilder/Ausgang.png")
            else:
                cfg.IMG_AKKU1.set_from_file(cfg.EXE_DIR + "/bilder/Ausgang_off.png")
        else:
            if cfg.GEWAEHLTER_AUSGANG == 2:
                cfg.IMG_AKKU2.set_from_file(cfg.EXE_DIR + "/bilder/Ausgang.png")
            else:
                cfg.IMG_AKKU2.set_from_file(cfg.EXE_DIR + "/bilder/Ausgang_off.png")

    #START/STOP callbacks
    def event_start_stop_cb(widget, event, data):
        """ callback function - eventboxes containing START/STOP pics """

        if not cfg.START_STOP.get_sensitive():
            return

        #True later on generate_output_strs() again
        cfg.START_STOP.set_sensitive(False)

        #not running -> send start
        if cfg.PHASE == 0:
            if cfg.GEWAEHLTER_AUSGANG == 1:
                cfg.COMMAND_ABORT = False #reset
                helper.akkumatik_command("44", "Start")
                cfg.FLOG.write("Sending Command 44\n")
            else:
                cfg.COMMAND_ABORT = False #reset
                helper.akkumatik_command("48", "Start")
                cfg.FLOG.write("Sending Command 48\n")
        else: #running -> send stop
            if cfg.GEWAEHLTER_AUSGANG == 1:
                cfg.COMMAND_ABORT = False #reset
                helper.akkumatik_command("41", "Stop")
                cfg.FLOG.write("Sending Command 41\n")
            else:
                cfg.COMMAND_ABORT = False #reset
                helper.akkumatik_command("42", "Stop")
                cfg.FLOG.write("Sending Command 42\n")

    def event_start_stop_enter_cb(widget, event, data):
        """ enter event on start-stop button """
        cfg.START_STOP_HOVER = True
        if cfg.PHASE == 0:
            cfg.START_STOP.set_from_file(cfg.EXE_DIR + "/bilder/start_hover.png")
        else:
            cfg.START_STOP.set_from_file(cfg.EXE_DIR + "/bilder/stop_hover.png")

    def event_start_stop_leave_cb(widget, event, data):
        """ leave event on start-stop button """
        cfg.START_STOP_HOVER = False

        if cfg.PHASE == 0:
            cfg.START_STOP.set_from_file(cfg.EXE_DIR + "/bilder/start.png")
        else:
            cfg.START_STOP.set_from_file(cfg.EXE_DIR + "/bilder/stop.png")

    #def draw_pixbuf(widget, event):
        #""" add the picture to the window """
        #path = cfg.EXE_DIR + '/bilder/Display.png'
        #pixbuf = gtk.gdk.pixbuf_new_from_file(path)
        #widget.window.draw_pixbuf(widget.style.bg_gc[gtk.STATE_NORMAL], \
                #pixbuf, 0, 0, 0,0)

    cfg.GTK_WINDOW = gtk.Window(gtk.WINDOW_TOPLEVEL)
    cfg.GTK_WINDOW.set_title('Akkumatic Remote Display')
    cfg.GTK_WINDOW.set_size_request(917, 168)
    cfg.GTK_WINDOW.set_default_size(917, 168)
    cfg.GTK_WINDOW.set_position(gtk.WIN_POS_CENTER)

    cfg.GTK_WINDOW.connect("delete_event", delete_event)
    cfg.GTK_WINDOW.connect("destroy", destroy)
    cfg.GTK_WINDOW.set_border_width(8)

    # overall hbox
    hbox = gtk.HBox()
    cfg.GTK_WINDOW.add(hbox)
    hbox.connect('expose-event', helper.draw_pixbuf, \
            cfg.EXE_DIR + '/bilder/Display.png')

    # akkumatik display label
    gfixed = gtk.Fixed()
    hbox.pack_start(gfixed, True, True, 0)

    #Left part of display
    cfg.LABEL1 = gtk.Label()
    cfg.LABEL1.set_size_request(342, 92)
    cfg.LABEL1.set_alignment(0, 0)
    cfg.LABEL1.set_justify(gtk.JUSTIFY_LEFT)
    if platform.system() == "Windows":
        cfg.LABEL1.modify_font(pango.FontDescription("mono bold 25"))
        gfixed.put(cfg.LABEL1, 45, 40)
    else:
        cfg.LABEL1.modify_font(pango.FontDescription("mono 22"))
        gfixed.put(cfg.LABEL1, 45, 36)

    #Right part of display
    cfg.LABEL2 = gtk.Label()
    cfg.LABEL2.set_size_request(340, 100)
    cfg.LABEL2.set_alignment(0, 0)
    cfg.LABEL2.set_justify(gtk.JUSTIFY_LEFT)
    if platform.system() == "Windows":
        gfixed.put(cfg.LABEL2, 418, 33)
        cfg.LABEL2.modify_font(pango.FontDescription("mono bold 14"))
    else:
        cfg.LABEL2.modify_font(pango.FontDescription("mono 12"))
        gfixed.put(cfg.LABEL2, 418, 33)

    #Status of display
    cfg.LABEL_STATUS = gtk.Label()
    cfg.LABEL_STATUS.set_size_request(729, 22)
    cfg.LABEL_STATUS.set_alignment(0, 0)
    cfg.LABEL_STATUS.set_justify(gtk.JUSTIFY_LEFT)

    cfg.EVENT_BOX_LSTATUS = gtk.EventBox()
    cfg.EVENT_BOX_LSTATUS.set_visible_window(True)
    cfg.EVENT_BOX_LSTATUS.add(cfg.LABEL_STATUS)
    cfg.EVENT_BOX_LSTATUS.modify_bg(gtk.STATE_NORMAL, \
            cfg.EVENT_BOX_LSTATUS.get_colormap().alloc_color("#aaaaaa"))

    gfixed.put(cfg.EVENT_BOX_LSTATUS, 34, 136)
    if platform.system() == "Windows":
        cfg.LABEL_STATUS.modify_font(pango.FontDescription("mono bold 14"))
    else:
        cfg.LABEL_STATUS.modify_font(pango.FontDescription("mono bold 12"))

    #vbox for buttons
    vbox = gtk.VBox()
    hbox.pack_end(vbox, False, False, 0)

    # hbox for Akku1+2 and start/stop
    hbox = gtk.HBox()
    vbox.pack_start(hbox, False, False, 0)

    #AKKU1
    evbox = gtk.EventBox()
    evbox.set_visible_window(False)
    cfg.IMG_AKKU1 = gtk.Image()
    cfg.IMG_AKKU1.set_size_request(20, 48)
    evbox.add(cfg.IMG_AKKU1)
    evbox.connect("button-press-event", eventcb, "1")
    #hover effect
    evbox.connect("enter-notify-event", event_enter_cb, "1")
    evbox.connect("leave-notify-event", event_leave_cb, "1")
    if cfg.TOOLTIPS:
        evbox.set_tooltip_text("Akku Ausgang 1")
    hbox.pack_start(evbox, False, False, 0)


    #START/STOP
    evbox = gtk.EventBox()
    evbox.set_visible_window(False)
    cfg.START_STOP = gtk.Image()
    cfg.START_STOP.set_from_file(cfg.EXE_DIR+"/bilder/start.png")
    cfg.START_STOP.set_sensitive(False)
    evbox.add(cfg.START_STOP)
    evbox.connect("button-press-event", event_start_stop_cb, "StartStop")
    evbox.connect("enter-notify-event", event_start_stop_enter_cb, "StartStop")
    evbox.connect("leave-notify-event", event_start_stop_leave_cb, "StartStop")
    if cfg.TOOLTIPS:
        evbox.set_tooltip_text("Start/Stop")
    hbox.pack_start(evbox, True, True, 2)

    #AKKU2
    evbox = gtk.EventBox()
    evbox.set_visible_window(False)
    cfg.IMG_AKKU2 = gtk.Image()
    cfg.IMG_AKKU2.set_size_request(20, 48)
    evbox.add(cfg.IMG_AKKU2)
    evbox.connect("button-press-event", eventcb, "2")
    evbox.connect("enter-notify-event", event_enter_cb, "2")
    evbox.connect("leave-notify-event", event_leave_cb, "2")
    if cfg.TOOLTIPS:
        evbox.set_tooltip_text("Akku Ausgang 2")
    hbox.pack_end(evbox, False, False, 0)


    if cfg.GEWAEHLTER_AUSGANG == 1:
        cfg.IMG_AKKU2.set_from_file(cfg.EXE_DIR+"/bilder/Ausgang_off.png")
        cfg.IMG_AKKU1.set_from_file(cfg.EXE_DIR+"/bilder/Ausgang.png")
    else:
        cfg.IMG_AKKU1.set_from_file(cfg.EXE_DIR+"/bilder/Ausgang_off.png")
        cfg.IMG_AKKU2.set_from_file(cfg.EXE_DIR+"/bilder/Ausgang.png")

    vbox.pack_start(gtk.HSeparator(), False, False, 8)

    #hbox fuer 'parameter,chart'
    hbox = gtk.HBox()
    vbox.pack_start(hbox, False, False, 0)


    #para
    evbox = gtk.EventBox()
    evbox.set_visible_window(False)
    image = gtk.Image()
    image.set_from_file(cfg.EXE_DIR+"/bilder/para.png")
    image.set_size_request(55, 42)
    evbox.add(image)
    evbox.connect("button-press-event", event_simple_cb, "para")
    evbox.connect("enter-notify-event", event_simple_enter_cb, "para")
    evbox.connect("leave-notify-event", event_simple_leave_cb, "para")
    if cfg.TOOLTIPS:
        evbox.set_tooltip_text("Akku Parameter")
    hbox.pack_start(evbox, False, False, 0)

    #chart
    evbox = gtk.EventBox()
    evbox.set_visible_window(False)
    image = gtk.Image()
    image.set_from_file(cfg.EXE_DIR+"/bilder/chart.png")
    image.set_size_request(42, 42)
    evbox.add(image)
    evbox.connect("button-press-event", event_simple_cb, "chart")
    evbox.connect("enter-notify-event", event_simple_enter_cb, "chart")
    evbox.connect("leave-notify-event", event_simple_leave_cb, "chart")
    if cfg.TOOLTIPS:
        evbox.set_tooltip_text("Chart(s)")
    hbox.pack_end(evbox, False, False, 0)

    vbox.pack_start(gtk.HSeparator(), False, True, 8)

    #hbox fuer 'data stuff'
    hbox = gtk.HBox()
    vbox.pack_start(hbox, False, False, 0)

    #recycle
    evbox = gtk.EventBox()
    evbox.set_visible_window(False)
    image = gtk.Image()
    image.set_from_file(cfg.EXE_DIR+"/bilder/recycle.png")
    #image.set_size_request(28, 20)
    evbox.add(image)
    evbox.connect("button-press-event", event_simple_cb, "recycle")
    evbox.connect("enter-notify-event", event_simple_enter_cb, "recycle")
    evbox.connect("leave-notify-event", event_simple_leave_cb, "recycle")
    if cfg.TOOLTIPS:
        evbox.set_tooltip_text("Alte Daten löschen")
    hbox.pack_start(evbox, True, True, 0)

    evbox = gtk.EventBox()
    evbox.set_visible_window(False)
    image = gtk.Image()
    image.set_from_file(cfg.EXE_DIR+"/bilder/quit.png")
    image.set_size_request(38, 30)
    evbox.add(image)
    evbox.connect("button-press-event", event_simple_cb, "quit")
    evbox.connect("enter-notify-event", event_simple_enter_cb, "quit")
    evbox.connect("leave-notify-event", event_simple_leave_cb, "quit")
    if cfg.TOOLTIPS:
        evbox.set_tooltip_text("Programm verlassen")
    hbox.pack_end(evbox, False, True, 0)

    hbox.pack_end(gtk.VSeparator(), False, True, 2)

    vbox.pack_start(gtk.HSeparator(), False, True, 8)

    # after file-open (what is needed on plotting)... hm?
    cfg.GTK_WINDOW.show_all()
    cfg.LABEL_STATUS.hide()

    return

##########################################}}}
# Akku Parameter Dialog{{{
##########################################
def akkupara_dialog(): #{{{
    """ The Akkuparameter Dialog """

    def save_akkulist():
        """ Save the current akku-list """
        fha = helper.open_file(cfg.EXE_DIR + "/liste_akkus.dat", "wb")
        for item in akkulist:
            line = ""
            for tmp in item:
                line += str(tmp)  + '\xff'
            line = line[:-1] # remove last xff
            line += "\n"
            fha.write(line)
        fha.close()

    def button_akku_cb(widget, para_dia, data=None):
        """ Add, overwrite or delete from the akkulist """

        if data == "+":
            dialog = gtk.Dialog("Name Akkuparameter ", \
                    para_dia, \
                    gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, \
                    (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, \
                    gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))

            label = gtk.Label("Akkuparameter Name")
            dialog.vbox.pack_start(label, True, True, 8)
            label.show()

            tbx = gtk.Entry()
            tbx.set_max_length(40)
            tbx.show()
            dialog.vbox.pack_start(tbx, True, True, 8)

            # run the dialog
            retval = dialog.run()

            txt = tbx.get_text().strip()

            dialog.destroy()

            if retval == -3: #OK
                # if no text... quit
                if txt == "":
                    message_dialog(para_dia, "Nicht gespeichert - es wurde kein Namen angegeben")
                    dialog.destroy()
                    return

                #check if there is that name already -> quit
                i = 0
                for item in akkulist:
                    if item[0] == txt:
                        message_dialog(para_dia, "Name existiert bereits.\n\
Allenfalls den \">\" Button verwenden um \
zu überschreiben.")
                        dialog.destroy()
                        return
                    i += 1

                akkulist.append([txt, \
                        int(cb_atyp.get_active()), \
                        int(cb_prog.get_active()), \
                        int(cb_lart.get_active()), \
                        int(cb_stromw.get_active()), \
                        int(cb_stoppm.get_active()), \
                        int(sp_anzzellen.get_value()), \
                        int(sp_kapazitaet.get_value()), \
                        int(sp_ladelimit.get_value()), \
                        int(sp_entladelimit.get_value()), \
                        int(sp_menge.get_value()), \
                        int(sp_zyklen.get_value())])

                #sort on 'name'
                akkulist.sort(key = lambda x: x[0].lower())

                for item in akkulist:
                    if item[0] == txt:
                        tmp = "Parameter: "
                        tmp +=  ", ".join(str(x) for x in item) + '\n'
                        tmp += "Gespeichert als %s" % txt
                        tmp += '\n'
                        cfg.FLOG.write(tmp)
                        break

                #find new item in new ordered list
                i = 0
                for item in akkulist:
                    if item[0] == txt:
                        break
                    i += 1

                #append new just there into gtk-combo
                cb_akkulist.insert_text(i, txt)
                cb_akkulist.set_active(i)

        elif data == ">":

            active_i = cb_akkulist.get_active()
            active_txt = cb_akkulist.get_active_text()
            if active_i == -1:
                message_dialog(para_dia, "Kein Namen zum überschreiben ausgewählt")
                return
                #find name
            #remove from list
            akkulist.pop(active_i)

            #reinsert into list
            akkulist.insert(active_i, [active_txt, \
                    int(cb_atyp.get_active()), \
                    int(cb_prog.get_active()), \
                    int(cb_lart.get_active()), \
                    int(cb_stromw.get_active()), \
                    int(cb_stoppm.get_active()), \
                    int(sp_anzzellen.get_value()), \
                    int(sp_kapazitaet.get_value()), \
                    int(sp_ladelimit.get_value()), \
                    int(sp_entladelimit.get_value()), \
                    int(sp_menge.get_value()), \
                    int(sp_zyklen.get_value())])

            item = akkulist[active_i]
            tmp = "Parameter: "
            tmp +=  ", ".join(str(x) for x in item) + '\n'
            tmp += "Gespeichert als %s" % active_txt
            tmp += '\n'
            message_dialog(para_dia, "'%s' wurde überschrieben" % (active_txt))
            cfg.FLOG.write(tmp)

        elif data == "-":

            active_i = cb_akkulist.get_active()
            if active_i == -1:
                message_dialog(para_dia, "Kein Namen zum löschen ausgewählt")
                return

            dialog = gtk.Dialog("Akkuparameter löschen", \
                    para_dia, \
                    gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, \
                    (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, \
                    gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))

            label = gtk.Label('Akkuparameter "%s" löschen?' %\
                    (akkulist[active_i][0]))
            align = gtk.Alignment(0, 0, 0, 0)
            align.set_padding(16, 16, 8, 8)
            align.show()
            align.add(label)
            dialog.vbox.pack_start(align, True, True, 0)
            label.show()

            # run the dialog
            retval = dialog.run()
            dialog.destroy()

            if retval == -3: #OK
                akkulist.pop(active_i) #gtk synchron to akkulist (should)
                cb_akkulist.remove_text(active_i)
                cfg.FLOG.write("Akku-Parameter geloescht '" + \
                        akkulist[active_i][0] + '\'\n\n')


        save_akkulist()

    def block_signals():
        cb_atyp.handler_block(cb_atyp_hd)
        cb_prog.handler_block(cb_prog_hd)
        cb_lart.handler_block(cb_lart_hd)
        cb_stoppm.handler_block(cb_stoppm_hd)
        cb_stromw.handler_block(cb_stromw_hd)

    def unblock_signals():
        cb_atyp.handler_unblock(cb_atyp_hd)
        cb_prog.handler_unblock(cb_prog_hd)
        cb_lart.handler_unblock(cb_lart_hd)
        cb_stoppm.handler_unblock(cb_stoppm_hd)
        cb_stromw.handler_unblock(cb_stromw_hd)

    def cb_akkulist_cb(data=None):
        """ Assign values according to saved Akku-parameters """
        val = cb_akkulist.get_active_text()
        for item in akkulist:
            if item[0] == val:
                cb_atyp.set_active(int(item[1]))
                cb_prog.set_active(int(item[2]))
                cb_lart.set_active(int(item[3]))
                cb_stromw.set_active(int(item[4]))
                cb_stoppm.set_active(int(item[5]))
                sp_anzzellen.set_value(int(item[6]))
                sp_kapazitaet.set_value(int(item[7]))
                sp_ladelimit.set_value(int(item[8]))
                sp_entladelimit.set_value(int(item[9]))
                sp_menge.set_value(int(item[10]))
                sp_zyklen.set_value(int(item[11]))
                break

    def combo_general_cb(data, old_atyp):
        """ akku-typ callback (when changed) """

        def stoppm_lademenge():
            """ only lademenge """
            model = cb_stoppm.get_model()
            model.clear()
            model.append([cfg.STOPPMETHODE[0]])
            cb_stoppm.set_active(0) #Lademenge

        # else this callback calls itself for nothing
        # on changes it makes itself
        block_signals()

        #get data
        atyp = cb_atyp.get_active_text()
        atyp_nr = cfg.AKKU_TYP.index(atyp)
        stoppm = cb_stoppm.get_active_text()
        stromw = cb_stromw.get_active_text()
        amprog = cb_prog.get_active_text()
        lart = cb_lart.get_active_text()

        # General stromwahl stuff
        if amprog == "Laden":
            sp_entladelimit.set_sensitive(False)
            sp_entladelimit_label.set_sensitive(False)
            sp_ladelimit.set_sensitive(True)
            sp_ladelimit_label.set_sensitive(True)

        elif amprog == "Entladen":
            sp_entladelimit.set_sensitive(True)
            sp_entladelimit_label.set_sensitive(True)
            sp_ladelimit.set_sensitive(False)
            sp_ladelimit_label.set_sensitive(False)
        else: #programs that require both
            sp_entladelimit.set_sensitive(True)
            sp_entladelimit_label.set_sensitive(True)
            sp_ladelimit.set_sensitive(True)
            sp_ladelimit_label.set_sensitive(True)
            # if Auto it gets changed later on Nixx

        #NiCd, NiMh
        if atyp_nr in [0, 1]:
            if old_atyp[0] != atyp_nr: #new

                old_atyp[0] = atyp_nr
                model = cb_lart.get_model()
                model.clear()
                model.append([cfg.LADEART[0]])
                model.append([cfg.LADEART[1]])
                model.append([cfg.LADEART[2]])
                cb_lart.set_active(cfg.NIXX_LADEART)
                lart = cfg.LADEART[cfg.NIXX_LADEART]

                model = cb_stromw.get_model()
                model.clear()
                model.append([cfg.STROMWAHL[0]])
                model.append([cfg.STROMWAHL[1]])
                model.append([cfg.STROMWAHL[2]])

                cb_stromw.set_active(cfg.NIXX_STROMWAHL)
                stromw = cfg.STROMWAHL[cfg.NIXX_STROMWAHL]

                model = cb_stoppm.get_model()
                model.clear()
                model.append([cfg.STOPPMETHODE[0]])
                model.append([cfg.STOPPMETHODE[1]])
                model.append([cfg.STOPPMETHODE[2]])
                model.append([cfg.STOPPMETHODE[3]])
                model.append([cfg.STOPPMETHODE[4]])
                cb_stoppm.set_active(cfg.NIXX_STOPPM)
                stoppm = cfg.STOPPMETHODE[cfg.NIXX_STOPPM]
                cb_stoppm.set_sensitive(True)

                cb_stromw.set_sensitive(True)
                cb_lart.set_sensitive(True)

                #Lademenge only when lademenge
                #kapa. if lademenge
                if cfg.NIXX_STOPPM == 0: #Lademenge
                    sp_menge.set_sensitive(True)
                    sp_menge_label.set_sensitive(True)
                else:
                    sp_menge.set_sensitive(False)
                    sp_menge_label.set_sensitive(False)

            else: #not new
                #store Nixx lademethode for later restore
                cfg.NIXX_STOPPM = cfg.STOPPMETHODE.index(stoppm)
                cfg.NIXX_STROMWAHL = cfg.STROMWAHL.index(stromw)
                cfg.NIXX_LADEART = cfg.LADEART.index(lart)

            # general Nixx stuff
            # No anz_zellen if...
            if amprog == "Laden":
                sp_anzzellen.set_sensitive(False)
                sp_anzzellen_label.set_sensitive(False)
            else:
                sp_anzzellen.set_sensitive(True)
                sp_anzzellen_label.set_sensitive(True)

            if cfg.NIXX_STROMWAHL == 0: # AUTO:
                sp_ladelimit.set_sensitive(False)
                sp_ladelimit_label.set_sensitive(False)
                sp_entladelimit.set_sensitive(False)
                sp_entladelimit_label.set_sensitive(False)

        #Blei, BeiGel
        elif atyp_nr in [2, 3]:
            if old_atyp[0] != atyp_nr:
                old_atyp[0] = atyp_nr

                model = cb_lart.get_model()
                model.clear()
                model.append([cfg.LADEART[0]])
                cb_lart.set_active(0) # and set to 0
                lart = "Konst"

                cb_lart.set_sensitive(False)

                model = cb_stromw.get_model()
                model.clear()
                model.append([cfg.STROMWAHL[2]])
                cb_stromw.set_sensitive(False)
                cb_stromw.set_active(0)
                stromw = cfg.STROMWAHL[2] #fest

                stoppm_lademenge()
                stoppm = "Lademenge"

                sp_anzzellen.set_sensitive(True)
                sp_anzzellen_label.set_sensitive(True)

        #LiLo, LiPo, LiFe, Uixx
        elif atyp_nr in [4, 5, 6, 7]:
            if atyp == cfg.AKKU_TYP[atyp_nr] and old_atyp[0] != atyp_nr:
                old_atyp[0] = atyp_nr
                model = cb_lart.get_model()
                model.clear()
                model.append([cfg.LADEART[0]])
                model.append([cfg.LADEART[3]])
                cb_lart.set_active(0) # and set to 0
                lart = "Konst"

                model = cb_stromw.get_model()
                model.clear()
                model.append([cfg.STROMWAHL[2]])

                if stromw == None:
                    tmp = 0
                else:
                    tmp = cfg.STROMWAHL.index(stromw)

                if tmp == 3: #ext. Wiederstand
                    cb_stromw.set_active(1)
                    stromw = cfg.STROMWAHL[3] #ext...
                else:
                    cb_stromw.set_active(0)
                    stromw = cfg.STROMWAHL[0] #Fest

                stoppm_lademenge()
                stoppm = "Lademenge"

                cb_stromw.set_sensitive(False)
                cb_lart.set_sensitive(True)
                sp_anzzellen.set_sensitive(True)
                sp_anzzellen_label.set_sensitive(True)

        # lagern etc. -> no zyklen
        if amprog == "Lagern" or amprog == "Laden" or \
                amprog == "Entladen" or amprog == "Sender":
            sp_zyklen.set_value(1)
            sp_zyklen.set_sensitive(False)
            sp_zyklen_label.set_sensitive(False)
        else:
            sp_zyklen.set_sensitive(True)
            sp_zyklen_label.set_sensitive(True)

        # ext-Wiederstand only on Entladen + Ausg==1
        # TODO: nach dem anderen? damit bei Nixx...
        cb_model = cb_stromw.get_model()
        xflag = False
        xiter = cb_model.get_iter_first()
        position = 0
        if xiter:
            #find ext. Wiederstand and store into position
            while True:
                if cb_model.get_value(xiter, 0) == cfg.STROMWAHL[3]:
                    xflag = True
                    break
                xiter = cb_model.iter_next(xiter)
                if not xiter:
                    break
                position += 1
            if amprog == "Entladen" and cfg.GEWAEHLTER_AUSGANG == 1:
                # yes - add it - it's not yet there (False)
                if xflag == False:
                    cb_stromw.append_text(cfg.STROMWAHL[3])
                    cb_stromw.set_sensitive(True)
            else:
                # remove it - it's there (True)
                if xflag == True:
                    xyz = cb_stromw.get_active()
                    cb_stromw.remove_text(position)
                    #ext. wieder - was selected -> 0 now
                    if xyz == position:
                        cb_stromw.set_active(0)
                        #stromw = cfg.STROMWAHL[0] # Depends... but not used anyway
                    # Only one entry left then -> disable
                    if position == 1:
                        cb_stromw.set_sensitive(False)

        #general Lademenge thingy
        if atyp_nr != 0 and atyp_nr != 1: #no Nixx
            cb_stoppm.set_sensitive(False) #because only one in list
        else:
            cb_stoppm.set_sensitive(True)

        if stoppm == "Lademenge":
            sp_menge_label.set_sensitive(True)
            sp_menge.set_sensitive(True)
        else:
            sp_menge_label.set_sensitive(False)
            sp_menge.set_sensitive(False)

        unblock_signals()

    def get_akkulist():
        """ load akkulist from harddrive """
        if os.path.exists(cfg.EXE_DIR + "/liste_akkus.dat"):
            fha = helper.open_file(cfg.EXE_DIR + "/liste_akkus.dat", "rb")
        else:
            return []

        ret = []
        for item in fha.readlines():
            tmp = item.split('\xff')
            #tmp = tmp[:-1] # remove -  last is newline
            if len(tmp) != 12:
                tmp = "Error in liste_akkus.dat - is " +\
                        str(len(tmp)) + " - should be 12"
                print (tmp)
                cfg.FLOG.write(tmp + '\n')
                continue

            #shoveling into r but with integer values now (besides of first)
            rtmp = []
            flag = True
            for xyx in tmp:
                if flag == True:
                    rtmp.append(str(xyx))
                    flag = False
                else:
                    rtmp.append(int(xyx))
            ret.append(rtmp)

        fha.close()
        return ret

    #######################################
    #GTK Akku parameter dialog main window
    dialog = gtk.Dialog("Akkumatik Settings Ausgang "\
            + str(cfg.GEWAEHLTER_AUSGANG), cfg.GTK_WINDOW, \
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)

    #dialog.add_button("Abbruch", 0)

    #Abbruch
    image = gtk.Image()
    image.set_from_file(cfg.EXE_DIR + \
            "/bilder/Cancel24.png")
    if cfg.TOOLTIPS:
        image.set_tooltip_text("Abbruch")
    image.show()
    button = gtk.Button()
    button.add(image)
    button.show()
    dialog.add_action_widget(button, 0)

    #Uebertragen
    image = gtk.Image()
    image.set_from_file(cfg.EXE_DIR + \
            "/bilder/Transfer24.png")
    if cfg.TOOLTIPS:
        image.set_tooltip_text("Parameter übertragen")
    image.show()
    button = gtk.Button()
    button.add(image)
    button.show()
    dialog.add_action_widget(button, 2)

    #Start
    image = gtk.Image()
    image.set_from_file(cfg.EXE_DIR + \
            "/bilder/start24.png")
    if cfg.TOOLTIPS:
        image.set_tooltip_text("Übertragen + starten")
    image.show()
    button = gtk.Button()
    button.set_size_request(136, 30)
    #button.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ccddcc"))
    button.add(image)
    button.show()
    dialog.add_action_widget(button, -3)

    frame = gtk.Frame(None)
    dialog.vbox.pack_start(frame, True, True, 0)

    dialog.vbox.connect('expose-event', helper.draw_pixbuf, \
            cfg.EXE_DIR + '/bilder/akku-para.png')

    hbox = gtk.HBox(False, 0)
    hbox.show()
    frame.add(hbox)
    frame.show()

    #add button
    image = gtk.Image()
    image.set_from_file(cfg.EXE_DIR + \
            "/bilder/add.png")
    if cfg.TOOLTIPS:
        image.set_tooltip_text("Parameter abspeichern als ...")
    image.show()
    button = gtk.Button()
    button.add(image)

    button.connect("clicked", button_akku_cb, dialog, "+")
    hbox.pack_start(button, False, True, 1)
    button.show()

    # overwriteg
    image = gtk.Image()
    image.set_from_file(cfg.EXE_DIR + \
            "/bilder/overwrite.png")
    if cfg.TOOLTIPS:
        image.set_tooltip_text("Überschreiben")
    image.show()
    button = gtk.Button()
    button.add(image)

    button.connect("clicked", button_akku_cb, dialog, ">")
    hbox.pack_start(button, False, True, 1)
    button.show()

    cb_akkulist = gtk.combo_box_new_text()
    hbox.pack_start(cb_akkulist, True, True, 1)

    # [atyp,prog,lart,stromw,stoppm,Zellen,Kapa,I-lade,I-entlade,Menge]
    akkulist = get_akkulist()

    for item in akkulist:
        cb_akkulist.append_text(item[0])

    cb_akkulist.connect("changed", cb_akkulist_cb)
    cb_akkulist.show()

    image = gtk.Image()
    image.set_from_file(cfg.EXE_DIR + \
            "/bilder/remove.png")
    if cfg.TOOLTIPS:
        image.set_tooltip_text("Eintrag löschen")
    image.show()
    button = gtk.Button()
    button.add(image)

    button.connect("clicked", button_akku_cb, dialog, "-")
    hbox.pack_start(button, False, True, 1)
    button.show()

    #list, so the callback-function can change the value
    old_atyp = [-1]

    #####################################
    # hbox over the whole dialog (besides of akkulist)

    hbox = gtk.HBox(False, 0)
    dialog.vbox.pack_start(hbox, False, False, 0)
    hbox.show()

    # vbox over the whole left part dialog (besides of akkulist)
    vbox = gtk.VBox(False, 0)
    vbox.set_size_request(210, 320)
    vbox.set_border_width(0)
    hbox.pack_start(vbox, False, False, 8)
    vbox.show()

    #frame 1,1 (vbox)
    frame = gtk.Frame(None)
    frame.modify_bg(gtk.STATE_NORMAL, \
            gtk.gdk.color_parse("#666666"))
    frame.set_label("Batterie")

    evbox = gtk.EventBox()
    evbox.modify_bg(gtk.STATE_NORMAL, \
            gtk.gdk.color_parse("#cccccc"))
    frame.add(evbox)

    vbox.pack_start(frame, False, False, 8)
    vbox_frame = gtk.VBox(False, 0)
    vbox_frame.set_border_width(4)
    evbox.add(vbox_frame)

    frame.show()
    evbox.show()
    vbox_frame.show()

    #stuff into frame (vbox)
    cb_atyp = gtk.combo_box_new_text()
    for item in cfg.AKKU_TYP:
        cb_atyp.append_text(item)
    cb_atyp.set_active(cfg.ATYP[cfg.GEWAEHLTER_AUSGANG])
    cb_atyp.show()
    cb_atyp_hd = cb_atyp.connect("changed", combo_general_cb, old_atyp)

    vbox_frame.pack_start(cb_atyp, False, False, 2)

    hbox_iframe = gtk.HBox(False, 0)
    hbox_iframe.show()
    vbox_frame.pack_start(hbox_iframe, False, False, 0)

    sp_anzzellen_label = gtk.Label(" Zellen-Anzahl: ")
    hbox_iframe.pack_start(sp_anzzellen_label, False, False, 0)
    sp_anzzellen_label.show()
    adj = gtk.Adjustment(cfg.ANZAHL_ZELLEN[cfg.GEWAEHLTER_AUSGANG], \
            0.0, 99999, 1, 1, 0.0)
    sp_anzzellen = gtk.SpinButton(adj, 0.0, 0)
    sp_anzzellen.set_wrap(False)
    sp_anzzellen.set_numeric(True)
    hbox_iframe.pack_end(sp_anzzellen, False, False, 0)
    sp_anzzellen.show()

    hbox_iframe = gtk.HBox(False, 0)
    hbox_iframe.show()
    vbox_frame.pack_start(hbox_iframe, False, False, 0)

    sp_kapazitaet_label = gtk.Label(" Kapazität mAh: ")
    hbox_iframe.pack_start(sp_kapazitaet_label, False, False, 4)
    sp_kapazitaet_label.show()
    adj = gtk.Adjustment(cfg.KAPAZITAET[cfg.GEWAEHLTER_AUSGANG], \
            0.0, 99999, 25, 25, 0.0)
    sp_kapazitaet = gtk.SpinButton(adj, 1.0, 0)
    sp_kapazitaet.set_wrap(False)
    sp_kapazitaet.set_numeric(True)
    hbox_iframe.pack_end(sp_kapazitaet, False, False, 0)
    sp_kapazitaet.show()

    #frame 1,2 (vbox)
    frame = gtk.Frame(None)
    frame.modify_bg(gtk.STATE_NORMAL, \
            gtk.gdk.color_parse("#999999"))
    frame.set_label("Programm")

    evbox = gtk.EventBox()
    evbox.modify_bg(gtk.STATE_NORMAL, \
            gtk.gdk.color_parse("#cccccc"))
    frame.add(evbox)

    vbox.pack_start(frame, False, False, 8)
    vbox_frame = gtk.VBox(False, 0)
    vbox_frame.set_border_width(4)
    evbox.add(vbox_frame)

    frame.show()
    evbox.show()
    vbox_frame.show()

    cb_prog = gtk.combo_box_new_text()

    if cfg.GEWAEHLTER_AUSGANG == 1:
        for item in cfg.AMPROGRAMM:
            cb_prog.append_text(item)
    else: #no Entladen...
        cb_prog.append_text(cfg.AMPROGRAMM[0])
        cb_prog.append_text(cfg.AMPROGRAMM[6])

    cb_prog.set_active(cfg.PRG[cfg.GEWAEHLTER_AUSGANG])
    cb_prog_hd = cb_prog.connect("changed", combo_general_cb, old_atyp)
    cb_prog.show()
    vbox_frame.pack_start(cb_prog, False, False, 2)

    hbox_iframe = gtk.HBox(False, 0)
    hbox_iframe.show()
    vbox_frame.pack_start(hbox_iframe, False, False, 0)

    sp_zyklen_label = gtk.Label(" Zyklen")
    hbox_iframe.pack_start(sp_zyklen_label, False, False, 0)
    sp_zyklen_label.show()
    adj = gtk.Adjustment(cfg.ZYKLEN[cfg.GEWAEHLTER_AUSGANG], 1, 99999, 1, 1, 0.0)
    sp_zyklen = gtk.SpinButton(adj, 0.0, 0)
    sp_zyklen.set_wrap(False)
    sp_zyklen.set_numeric(True)
    hbox_iframe.pack_end(sp_zyklen, False, False, 0)
    sp_zyklen.show()

    # vbox over the whole right part dialog (besides of akkulist)
    vbox = gtk.VBox(False, 0)
    vbox.set_size_request(210, 320)
    vbox.set_border_width(0)
    hbox.pack_start(vbox, False, False, 8)
    vbox.show()

    #frame 2,1 (vbox)
    frame = gtk.Frame(None)
    frame.modify_bg(gtk.STATE_NORMAL, \
            gtk.gdk.color_parse("#669999"))
    frame.set_label("Ladeart")

    evbox = gtk.EventBox()
    evbox.modify_bg(gtk.STATE_NORMAL, \
            gtk.gdk.color_parse("#cccccc"))
    frame.add(evbox)

    vbox.pack_start(frame, False, False, 8)
    vbox_frame = gtk.VBox(False, 0)
    vbox_frame.set_border_width(4)
    evbox.add(vbox_frame)

    frame.show()
    evbox.show()
    vbox_frame.show()

    cb_lart = gtk.combo_box_new_text()
    for item in cfg.LADEART[:-1]: #exclude LiPo
        cb_lart.append_text(item)
    cb_lart.set_active(cfg.LART[cfg.GEWAEHLTER_AUSGANG])
    cb_lart_hd = cb_lart.connect("changed", combo_general_cb, old_atyp)
    cb_lart.show()
    vbox_frame.pack_start(cb_lart, False, False, 2)

    #frame 2,2 (vbox)
    frame = gtk.Frame(None)
    frame.modify_bg(gtk.STATE_NORMAL, \
            gtk.gdk.color_parse("#666699"))
    frame.set_label("Stromwahl")

    evbox = gtk.EventBox()
    evbox.modify_bg(gtk.STATE_NORMAL, \
            gtk.gdk.color_parse("#cccccc"))
    frame.add(evbox)

    vbox.pack_start(frame, False, False, 8)
    vbox_frame = gtk.VBox(False, 0)
    vbox_frame.set_border_width(4)
    evbox.add(vbox_frame)

    frame.show()
    evbox.show()
    vbox_frame.show()

    cb_stromw = gtk.combo_box_new_text()
    for item in cfg.STROMWAHL:
        cb_stromw.append_text(item)
    cb_stromw.set_active(cfg.STROMW[cfg.GEWAEHLTER_AUSGANG])
    cb_stromw_hd = cb_stromw.connect("changed", combo_general_cb, old_atyp)
    cb_stromw.show()
    vbox_frame.pack_start(cb_stromw, False, False, 2)

    hbox_iframe = gtk.HBox(False, 0)
    hbox_iframe.show()
    vbox_frame.pack_start(hbox_iframe, False, False, 0)

    sp_ladelimit_label = gtk.Label(" I-Laden mA:")
    hbox_iframe.pack_start(sp_ladelimit_label, False, False, 0)
    sp_ladelimit_label.show()
    adj = gtk.Adjustment(cfg.LADELIMIT[cfg.GEWAEHLTER_AUSGANG], \
            0.0, 99999, 25, 25, 0.0)
    sp_ladelimit = gtk.SpinButton(adj, 1.0, 0)
    sp_ladelimit.set_wrap(False)
    sp_ladelimit.set_numeric(True)
    hbox_iframe.pack_end(sp_ladelimit, False, False, 0)
    sp_ladelimit.show()

    hbox_iframe = gtk.HBox(False, 0)
    hbox_iframe.show()
    vbox_frame.pack_start(hbox_iframe, False, False, 0)

    sp_entladelimit_label = gtk.Label(" I-Entladen mA:")
    hbox_iframe.pack_start(sp_entladelimit_label, False, False, 0)
    sp_entladelimit_label.show()
    adj = gtk.Adjustment(cfg.ENTLADELIMIT[cfg.GEWAEHLTER_AUSGANG], \
            0.0, 99999, 25, 25, 0.0)
    sp_entladelimit = gtk.SpinButton(adj, 1.0, 0)
    sp_entladelimit.set_wrap(False)
    sp_entladelimit.set_numeric(True)
    hbox_iframe.pack_end(sp_entladelimit, False, False, 0)
    if cfg.GEWAEHLTER_AUSGANG == 2:
        sp_entladelimit.set_sensitive(False)
    sp_entladelimit.show()

    #frame 2,3 (vbox)
    frame = gtk.Frame(None)
    frame.modify_bg(gtk.STATE_NORMAL, \
            gtk.gdk.color_parse("#cc9999"))
    frame.set_label("Stoppmethode")

    evbox = gtk.EventBox()
    evbox.modify_bg(gtk.STATE_NORMAL, \
            gtk.gdk.color_parse("#cccccc"))
    frame.add(evbox)

    vbox.pack_start(frame, False, False, 8)
    vbox_frame = gtk.VBox(False, 0)
    vbox_frame.set_border_width(4)
    evbox.add(vbox_frame)

    frame.show()
    evbox.show()
    vbox_frame.show()

    cb_stoppm = gtk.combo_box_new_text()
    for item in cfg.STOPPMETHODE:
        cb_stoppm.append_text(item)
    cb_stoppm.set_active(cfg.STOPPM[cfg.GEWAEHLTER_AUSGANG])
    cb_stoppm_hd = cb_stoppm.connect("changed", combo_general_cb, old_atyp)
    cb_stoppm.show()
    vbox_frame.pack_start(cb_stoppm, False, False, 2)

    hbox_iframe = gtk.HBox(False, 0)
    hbox_iframe.show()
    vbox_frame.pack_start(hbox_iframe, False, False, 0)

    sp_menge_label = gtk.Label(" Menge mAh:")
    hbox_iframe.pack_start(sp_menge_label, False, False, 0)
    sp_menge_label.show()
    adj = gtk.Adjustment(cfg.MENGE[cfg.GEWAEHLTER_AUSGANG], \
            0.0, 99999, 25, 25, 0.0)
    sp_menge = gtk.SpinButton(adj, 1.0, 0)
    sp_menge.set_wrap(False)
    sp_menge.set_numeric(True)
    hbox_iframe.pack_end(sp_menge, False, False, 0)
    sp_menge.show()

    combo_general_cb("", old_atyp)

    hex_str = None
    hex_str2 = None

    while True:
        # run the dialog
        # reloading it multiple times seems to work flawlessly
        retval = dialog.run()

        if retval == -3 or retval == 2: #OK or uebertragen got pressed

            #can easily happen, when loading stored parameters
            #into akku 2 where no entladen is available
            if cb_prog.get_active_text() == None:
                message_dialog(dialog, "'Programm' ist nicht gewählt")
                continue


            hex_str = str(30 + cfg.GEWAEHLTER_AUSGANG) #kommando 31 or 32
            hex_str += helper.get_pos_hex(cb_atyp.get_active_text(), cfg.AKKU_TYP)
            hex_str += helper.get_pos_hex(cb_prog.get_active_text(), cfg.AMPROGRAMM)
            hex_str += helper.get_pos_hex(cb_lart.get_active_text(), cfg.LADEART)
            hex_str += \
                    helper.get_pos_hex(cb_stromw.get_active_text(), cfg.STROMWAHL)

            tmp = cb_stoppm.get_active_text()
            if tmp == None: #replace lipo None need something
                tmp = cfg.STOPPMETHODE[0] #"Lademenge"
            hex_str += helper.get_pos_hex(tmp, cfg.STOPPMETHODE)

            hex_str += helper.get_16bit_hex(int(sp_anzzellen.get_value()))
            hex_str += helper.get_16bit_hex(int(sp_kapazitaet.get_value()))
            hex_str += helper.get_16bit_hex(int(sp_ladelimit.get_value()))
            hex_str += helper.get_16bit_hex(int(sp_entladelimit.get_value()))
            hex_str += helper.get_16bit_hex(int(sp_menge.get_value()))
            hex_str += helper.get_16bit_hex(int(sp_zyklen.get_value()))

            #since akkumatik is not sending this stuff from its own (yet)
            cfg.KAPAZITAET[cfg.GEWAEHLTER_AUSGANG] = int(sp_kapazitaet.get_value())
            cfg.LADELIMIT[cfg.GEWAEHLTER_AUSGANG] = int(sp_ladelimit.get_value())
            cfg.ENTLADELIMIT[cfg.GEWAEHLTER_AUSGANG] = \
                    int(sp_entladelimit.get_value())
            cfg.MENGE[cfg.GEWAEHLTER_AUSGANG] = int(sp_menge.get_value())
            cfg.ZYKLEN[cfg.GEWAEHLTER_AUSGANG] = int(sp_zyklen.get_value())

            #Kommando u08 Akkutyp u08 program u08 lade_mode u08 strom_mode
            #u08 stop_mode u16 zellenzahl u16 capacity u16 i_lade u16 i_entl
            #u16 menge u16 zyklenzahl

            if retval == -3: #Additionally start the thing
                if cfg.GEWAEHLTER_AUSGANG == 1:
                    hex_str2 = "44"
                else:
                    hex_str2 = "48"
        break
    dialog.destroy()
    return (hex_str, hex_str2)

# vim: set nosi ai ts=8 et shiftwidth=4 sts=4 fdm=marker foldnestmax=1 :
