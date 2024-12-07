
""" 
Plot using Clawpack's visclaw graphics.  This file can be run as ; 

    % python plot_filament.py

To learn more about visclaw graphics, see www.clawpack.org
    
""" 
import numpy as np
notpillowsphere = None

def set_blocknumber(current_data):
    global blocknumber
    blocknumber = current_data.patch.block_number
    return current_data.q[0,:,:]

def mapc2p_cart(xc, yc):
    xp = 2 * xc - 1
    yp = 2 * yc - 1
    zp = np.zeros_like(xp)  
    return xp, yp, zp


def mapc2p_disk_sp(xc, yc):
    d = np.maximum(np.abs(xc), np.abs(yc))
    d = np.maximum(d, 1e-10)  
    D = np.sin((np.pi * d) / 2) / np.sqrt(2)  
    R = np.ones_like(d)  
    center = D - np.sqrt(R**2 - D**2)

    xp = (D / d) * np.abs(xc)
    yp = (D / d) * np.abs(yc)

    ij = np.where(np.abs(yc) >= np.abs(xc))
    yp[ij] = center[ij] + np.sqrt(R[ij]**2 - xp[ij]**2)

    ij = np.where(np.abs(xc) >= np.abs(yc))
    xp[ij] = center[ij] + np.sqrt(R[ij]**2 - yp[ij]**2)

    xp*=np.sign(xc)
    yp *= np.sign(yc)

    return xp, yp



def mapc2p_pillowsphere(xc1, yc1):
    global comp_grid
    comp_grid = False 
    xc, yc, _ = mapc2p_cart(xc1, yc1)
    r1=1
    xp = xc
    yp = yc
    
    if blocknumber == 0:
        zp = np.zeros_like(xp)+1
    else:
        zp = -np.zeros_like(xp)-1

    if comp_grid:
        return xp, yp, zp

    
    d = np.maximum(xc - 1, 0) + np.maximum(-1 - xc, 0)
    xc = (1 - d) / (1 + d) * xc

    d = np.maximum(yc - 1, 0) + np.maximum(-1 - yc, 0)
    yc = (1 - d) / (1 + d) * yc

    
    xp, yp = mapc2p_disk_sp(xc, yc)

    r2 = np.minimum(xp**2 + yp**2, 1)
    zp = np.sqrt(1 - r2)

    
    mghost = (np.abs(xc) > 1) | (np.abs(yc) > 1)
    zp[mghost] = -zp[mghost]

    if blocknumber == 1:
        zp = -zp

    return xp, yp, zp

def mapc2p_cubedsphere(xc, yc):
    
    # Mapping based on block number
    if blocknumber == 0:
        yp, xp, zp = csphere_basic(xc, yc)
        zp = -zp
    elif blocknumber == 1:
        zp, xp, yp = csphere_basic(xc, yc)
    elif blocknumber == 2:
        zp, yp, xp = csphere_basic(xc, yc)
        xp = -xp
    elif blocknumber == 3:
        xp, yp, zp = csphere_basic(xc, yc)
    elif blocknumber == 4:
        xp, zp, yp = csphere_basic(xc, yc)
        yp = -yp
    elif blocknumber == 5:
        yp, zp, xp = csphere_basic(xc, yc)
    else:
        raise ValueError("Invalid block number")
    
    return xp, yp, zp

def csphere_basic(xc, yc):
    tan_xi = np.tan(0.5 * np.pi * (xc - 0.5))
    tan_eta = np.tan(0.5 * np.pi * (yc - 0.5))
    
    
    zp = 1.0 / np.sqrt(tan_xi**2 + tan_eta**2 + 1)
    xp = zp * tan_xi
    yp = zp * tan_eta
    
    return xp, yp, zp


def mapc2p(xc1, yc1):
    global notpillowsphere
    map_type = 'pillowsphere'  # This is the maptype, since in matlab it was over written to this
    
    if map_type =='nomap': 
        xp=xc1
        yp=yc1
        zp=np.zeros_like(xc1)
    elif map_type == 'pillowsphere':
        notpillowsphere = False
        xp, yp, zp = mapc2p_pillowsphere(xc1, yc1)
    elif map_type == 'cubedsphere':
        xp, yp, zp = mapc2p_cubedsphere(xc1, yc1)
        b = blocknumber 
        s = 0.0
        if b == 0:
            zp -= s
        elif b == 1:
            yp += s
        elif b == 2:
            xp -= s
        elif b == 3:
            zp += s
        elif b == 4:
            yp -= s
        elif b == 5:
            xp += s
    else:
        raise ValueError("Invalid mapping")
    
    return xp, yp



#--------------------------
def setplot(plotdata):
#--------------------------
    
    """ 
    Specify what is to be plotted at each frame.
    Input:  plotdata, an instance of ClawPlotData.
    Output: a modified version of plotdata.
    
    """ 


    from clawpack.visclaw import colormaps
    import clawpack.forestclaw as pyclaw

    plotdata.clearfigures()  # clear any old figures,axes,items data
    plotdata.format = 'forestclaw'
    
    # ------------------------------------------------------------
    # Figure for pcolor plot
    # ------------------------------------------------------------

    plotfigure = plotdata.new_plotfigure(name='q[0]', figno=0)

    # Set up for axes in this figure:
    plotaxes = plotfigure.new_plotaxes()
    plotaxes.xlimits = 'auto'
    plotaxes.ylimits = 'auto'
    plotaxes.title = 'q[0]'
    plotaxes.scaled = True

    # Set up for item on these axes:
    plotitem = plotaxes.new_plotitem(plot_type='2d_pcolor')
    plotitem.plot_var = set_blocknumber
    plotitem.pcolor_cmap = colormaps.yellow_red_blue
    

    plotitem.MappedGrid = True
    plotitem.mapc2p = mapc2p
    plotitem.pcolor_cmin = 0.0
    plotitem.pcolor_cmax = 1.0
    plotitem.add_colorbar = True
    plotitem.amr_celledges_show = [False,False,False,False]
    plotitem.amr_patchedges_show = [True,True,False,False]
    plotitem.show = True       # show on plot?
    #plotitem.plot_grid = False  # Disable grid plotting

    
   
    plotfigure = plotdata.new_plotfigure(name='filament (tikz)', figno=1)
    plotfigure.use_for_kml = True
    plotfigure.kml_xlimits = [0,2]
    plotfigure.kml_ylimits = [0,2]

    mx = 8
    maxlevel = 4
    resolution = mx*2**maxlevel
    figsize = [4.0,4.0]
    dpi = resolution/figsize[0]


    #-----------------------------------------
    # Figures for gauges
    #-----------------------------------------
    plotfigure = plotdata.new_plotfigure(name='q', figno=300, \
                    type='each_gauge')
    plotfigure.clf_each_gauge = True

    # Set up for axes in this figure:
    plotaxes = plotfigure.new_plotaxes()
    plotaxes.xlimits = 'auto'
    plotaxes.ylimits = 'auto'
    plotaxes.title = 'q'

    # Plot q as blue curve:
    plotitem = plotaxes.new_plotitem(plot_type='1d_plot')
    plotitem.plot_var = 0
    plotitem.plotstyle = 'b-'

    #-----------------------------------------

    # Parameters used only when creating html and/or latex hardcopy
    # e.g., via clawpack.visclaw.frametools.printframes:

    plotdata.printfigs = True                # print figures
    plotdata.print_format = 'png'            # file format
    plotdata.print_framenos = 'all'          # list of frames to print
    plotdata.print_fignos = [0,1]            # list of figures to print
    plotdata.html = True                    # create html files of plots?
    plotdata.html_homelink = '../README.html'   # pointer for top of index
    plotdata.html_movie = 'JSAnimation'      # new style, or "4.x" for old style
    plotdata.latex = False                    # create latex file of plots?
    plotdata.latex_figsperline = 2           # layout of plots
    plotdata.latex_framesperline = 1         # layout of plots
    plotdata.latex_makepdf = False           # also run pdflatex?

    plotdata.kml = False      # Set to true to get tikz output

    return plotdata



if __name__=="__main__":
    from clawpack.visclaw.plotclaw import plotclaw
    plotclaw(outdir='.',setplot=setplot,plotdir='_plots',format='forestclaw')



    
