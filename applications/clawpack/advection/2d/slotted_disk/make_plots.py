
""" 
Plot using Clawpack's visclaw graphics.  This file can be run as ; 

    % python plot_filament.py

To learn more about visclaw graphics, see www.clawpack.org
    
""" 
import numpy as np

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
    # Disk mapping used for the sphere
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
    
    
    zp = 1. / np.sqrt(tan_xi**2 + tan_eta**2 + 1)
    xp = zp * tan_xi
    yp = zp * tan_eta
    
    return xp, yp, zp


def mapc2p(xc1, yc1):
    global notpillowsphere
    map_type = 'cubedsphere'  # This is the maptype, since in matlab it was over written to this
    
    b = blocknumber  
    if map_type == 'pillowsphere':
        notpillowsphere = False
        xp, yp, zp = mapc2p_pillowsphere(xc1, yc1)
    elif map_type == 'cubedsphere':
        xp, yp, zp = mapc2p_cubedsphere(xc1, yc1)
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
            raise ValueError(f"blocknumber={blocknumber} is out of bounds.")
    
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
    plotitem.pcolor_cmap = slotted_cmap

    plotitem.MappedGrid = True
    plotitem.mapc2p = mapc2p
    plotitem.pcolor_cmin = -0.5
    plotitem.pcolor_cmax = 1.0
    plotitem.add_colorbar = True
    plotitem.amr_celledges_show = [False,False,False,False,False,False]
    plotitem.amr_patchedges_show = [True,True,True,True,False,False]
    plotitem.show = True       # show on plot?
    
   
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


## Parula colormap for MATLAB (https://github.com/BIDS/colormap/blob/master/parula.py)

from matplotlib.colors import LinearSegmentedColormap

cm_data = [[0.2081, 0.1663, 0.5292], [0.2116238095, 0.1897809524, 0.5776761905], 
 [0.212252381, 0.2137714286, 0.6269714286], [0.2081, 0.2386, 0.6770857143], 
 [0.1959047619, 0.2644571429, 0.7279], [0.1707285714, 0.2919380952, 
  0.779247619], [0.1252714286, 0.3242428571, 0.8302714286], 
 [0.0591333333, 0.3598333333, 0.8683333333], [0.0116952381, 0.3875095238, 
  0.8819571429], [0.0059571429, 0.4086142857, 0.8828428571], 
 [0.0165142857, 0.4266, 0.8786333333], [0.032852381, 0.4430428571, 
  0.8719571429], [0.0498142857, 0.4585714286, 0.8640571429], 
 [0.0629333333, 0.4736904762, 0.8554380952], [0.0722666667, 0.4886666667, 
  0.8467], [0.0779428571, 0.5039857143, 0.8383714286], 
 [0.079347619, 0.5200238095, 0.8311809524], [0.0749428571, 0.5375428571, 
  0.8262714286], [0.0640571429, 0.5569857143, 0.8239571429], 
 [0.0487714286, 0.5772238095, 0.8228285714], [0.0343428571, 0.5965809524, 
  0.819852381], [0.0265, 0.6137, 0.8135], [0.0238904762, 0.6286619048, 
  0.8037619048], [0.0230904762, 0.6417857143, 0.7912666667], 
 [0.0227714286, 0.6534857143, 0.7767571429], [0.0266619048, 0.6641952381, 
  0.7607190476], [0.0383714286, 0.6742714286, 0.743552381], 
 [0.0589714286, 0.6837571429, 0.7253857143], 
 [0.0843, 0.6928333333, 0.7061666667], [0.1132952381, 0.7015, 0.6858571429], 
 [0.1452714286, 0.7097571429, 0.6646285714], [0.1801333333, 0.7176571429, 
  0.6424333333], [0.2178285714, 0.7250428571, 0.6192619048], 
 [0.2586428571, 0.7317142857, 0.5954285714], [0.3021714286, 0.7376047619, 
  0.5711857143], [0.3481666667, 0.7424333333, 0.5472666667], 
 [0.3952571429, 0.7459, 0.5244428571], [0.4420095238, 0.7480809524, 
  0.5033142857], [0.4871238095, 0.7490619048, 0.4839761905], 
 [0.5300285714, 0.7491142857, 0.4661142857], [0.5708571429, 0.7485190476, 
  0.4493904762], [0.609852381, 0.7473142857, 0.4336857143], 
 [0.6473, 0.7456, 0.4188], [0.6834190476, 0.7434761905, 0.4044333333], 
 [0.7184095238, 0.7411333333, 0.3904761905], 
 [0.7524857143, 0.7384, 0.3768142857], [0.7858428571, 0.7355666667, 
  0.3632714286], [0.8185047619, 0.7327333333, 0.3497904762], 
 [0.8506571429, 0.7299, 0.3360285714], [0.8824333333, 0.7274333333, 0.3217], 
 [0.9139333333, 0.7257857143, 0.3062761905], [0.9449571429, 0.7261142857, 
  0.2886428571], [0.9738952381, 0.7313952381, 0.266647619], 
 [0.9937714286, 0.7454571429, 0.240347619], [0.9990428571, 0.7653142857, 
  0.2164142857], [0.9955333333, 0.7860571429, 0.196652381], 
 [0.988, 0.8066, 0.1793666667], [0.9788571429, 0.8271428571, 0.1633142857], 
 [0.9697, 0.8481380952, 0.147452381], [0.9625857143, 0.8705142857, 0.1309], 
 [0.9588714286, 0.8949, 0.1132428571], [0.9598238095, 0.9218333333, 
  0.0948380952], [0.9661, 0.9514428571, 0.0755333333], 
 [0.9763, 0.9831, 0.0538]]

slotted_cmap = LinearSegmentedColormap.from_list('slotted_cmap', cm_data)
# For use of "viscm view"
test_cm = slotted_cmap


if __name__=="__main__":
    from clawpack.visclaw.plotclaw import plotclaw
    plotclaw(outdir='.',setplot=setplot,plotdir='_plots',format='forestclaw')



    
