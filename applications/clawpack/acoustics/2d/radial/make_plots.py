
""" 
Set up the plot figures, axes, and items to be done for each frame.

This module is imported by the plotting routines and then the
function setplot is called to set the plot parameters.
    
""" 

import os
import numpy as np
#if os.path.exists('_plots'):
    #qref_dir = os.path.abspath('_plots')
#else:
    #qref_dir = None
    #print ("Directory _plots not found")
alpha=0.5

def set_blocknumber(current_data):
    global blocknumber
    blocknumber = current_data.patch.block_number
    return current_data.q[0,:,:]

def mapc2p_fivepatch(xc, yc, alpha):
    m, n = xc.shape
     
    if blocknumber == 2:
        xp = (2 * xc - 1)*(alpha)
        yp = (2 * yc - 1)*(alpha)
    else:
        if blocknumber == 0:
            xc1 = xc
            yc1 = 1-yc
            xp, yp = bilinear_help(alpha, xc1.flatten(), yc1.flatten())
            yp = -yp
        elif blocknumber == 1:
            xc1 = yc
            yc1 = 1-xc
            yp, xp = bilinear_help(alpha, xc1.flatten(), yc1.flatten())
            xp = -xp
        elif blocknumber == 3:
            xc1 = yc
            yc1 = xc
            yp, xp = bilinear_help(alpha, xc1.flatten(), yc1.flatten())
        elif blocknumber == 4:
            xc1 = xc
            yc1 = yc
            xp, yp = bilinear_help(alpha, xc1.flatten(), yc1.flatten())
        else:
            raise ValueError(f"blockno = {blocknumber} is not valid.")
    
    xp = xp.reshape(m,n)
    yp = yp.reshape(m,n)
    zp = np.zeros_like(xp)

    
    return xp, yp, zp

def bilinear_help(alpha, xi, eta):
    
    xpc = [-alpha, -1, 1, alpha]
    ypc = [alpha, 1, 1, alpha]
    


    a = np.array([xpc[0], ypc[0]])
    u1 = np.array([xpc[3] - xpc[0], ypc[3] - ypc[0]])
    v1 = np.array([xpc[1] - xpc[0], ypc[1] - ypc[0]])
    v2 = np.array([xpc[2] - xpc[3], ypc[2] - ypc[3]])

    xb=np.zeros_like(xi)
    yb=np.zeros_like(eta)

    xb = a[0] + u1[0] * xi + v1[0] * eta + (v2[0] - v1[0]) * xi * eta
    yb = a[1] + u1[1] * xi + v1[1] * eta + (v2[1] - v1[1]) * xi * eta

    return xb, yb

def mapc2p_cart(xc, yc):
    xp = 2 * xc - 1
    yp = 2 * yc - 1
    zp = np.zeros_like(xp)  
    return xp, yp, zp

def mapc2p_pillowdisk(xc1,yc1):
    map_type='disk'
    xc,yc,zc=mapc2p_cart(xc1,yc1)

    xp=xc
    yp=yc
    zp=0*xp

    r1=1
    ijlower = np.where(xc < -1)[0]
    xc[ijlower] = -2 - xc[ijlower]
    d=np.maximum(np.abs(xc),np.abs(yc))
    d=np.maximum(d, 1e-10)

    if map_type=='disk':
        D=r1*d/np.sqrt(2)
    elif map_type in {'hemisphere', 'sphere'}:
        D=r1*np.sin(np.pi*d/2)/np.sqrt(2)
    else:
        raise ValueError('No mapping')
    
    R=r1*np.ones_like(d)

    center=D-np.sqrt(np.maximum(0,R**2-D**2))
    xp=D/d*np.abs(xc)
    yp=D/d*np.abs(yc)

    ij=np.where(np.abs(yc)>=np.abs(xc))
    yp[ij]=center[ij]+np.sqrt(np.maximum(0,R[ij]**2-xp[ij]**2))

    ij=np.where(np.abs(xc)>=np.abs(yc))

    xp=np.sign(xc)*xp
    yp=np.sign(yc)*yp

    if map_type=='disk':
        zp=0*xp
    elif map_type in {'hemisphere', 'sphere'}:
        zp=np.sqrt(r1**2-(xp**2+yp**2))
        zp[ijlower]=-zp[ijlower]
    else:
        raise ValueError('No mapping')
    
    if os.path.exists('rrot.dat'):
        rrot=np.loadtxt('rrot.dat')

        m,n=xc.shape

        xpv=xp.reshape(1,m*n)
        ypv=yp.reshape(1,m*n)
        zpv=zp.reshape(1,m*n)

        v=np.dot(rrot,np.vstack([xpv, ypv, zpv]))
        xp=v[0,:].reshape(m,n)
        yp=v[1,:].reshape(m,n)
        zp=v[2,:].reshape(m,n)
    
    return xp, yp, zp


def mapc2p_pillowdisk5(xc,yc,alpha):
    xc,yc,zc=mapc2p_fivepatch(xc,yc,alpha)

    xc=(xc+1)/2
    yc=(yc+1)/2
    xp,yp,zp=mapc2p_pillowdisk(xc,yc)

    return xp,yp,zp

def mapc2p(xc,yc):
    map_type='pillowdisk5'
    if map_type=='nomap':
        xp=xc
        yp=yc
    elif map_type=='pillowdisk5':
        xp,yp,zp=mapc2p_pillowdisk5(xc,yc, alpha)
    else:
        raise ValueError('Invalid mapping')
    
    zp=0*xp
    
    return xp,yp


#--------------------------
def setplot(plotdata):
#--------------------------
    
    """ 
    Specify what is to be plotted at each frame.
    Input:  plotdata, an instance of clawpack.visclaw.data.ClawPlotData.
    Output: a modified version of plotdata.
    
    """ 


    from clawpack.visclaw import colormaps

    plotdata.clearfigures()  # clear any old figures,axes,items data
    

    # Figure for pressure
    # -------------------

    plotfigure = plotdata.new_plotfigure(name='Pressure', figno=0)

    # Set up for axes in this figure:
    plotaxes = plotfigure.new_plotaxes()
    plotaxes.xlimits = 'auto'
    plotaxes.ylimits = 'auto'
    plotaxes.title = 'Pressure'
    plotaxes.scaled = True      # so aspect ratio is 1
    #plotaxes.afteraxes = addgauges

    # Set up for item on these axes:
    plotitem = plotaxes.new_plotitem(plot_type='2d_pcolor')
    plotitem.plot_var = set_blocknumber
    plotitem.pcolor_cmap = colormaps.red_yellow_blue
    plotitem.MappedGrid = True
    plotitem.mapc2p = mapc2p
    plotitem.add_colorbar = True
    plotitem.show = True       # show on plot?
    plotitem.pcolor_cmin = -2.0
    plotitem.pcolor_cmax = 2.0
    plotitem.amr_patchedges_show = [True,True,True,False,False]
    plotitem.amr_celledges_show = [False,False,False,False,False]
    
    

    # Figure for scatter plot
    # -----------------------

    plotfigure = plotdata.new_plotfigure(name='scatter', figno=3)
    #plotfigure.show = (qref_dir is not None)

    # Set up for axes in this figure:
    plotaxes = plotfigure.new_plotaxes()
    plotaxes.xlimits = [0,1.5]
    plotaxes.ylimits = [-2.,4.]
    plotaxes.title = 'Scatter plot'

    # Set up for item on these axes: scatter of 2d data
    #plotitem = plotaxes.new_plotitem(plot_type='1d_from_2d_data')
    
    def p_vs_r(current_data):
        # Return radius of each grid cell and p value in the cell
        from pylab import sqrt
        x = current_data.x
        y = current_data.y
        r = sqrt(x**2 + y**2)
        q = current_data.q
        p = q[0,:,:]
        return r,p

    #plotitem.map_2d_to_1d = p_vs_r
    #plotitem.plot_var = 0
    #plotitem.plotstyle = 'o'
    #plotitem.color = 'b'
    #plotitem.show = True       # show on plot?
    
    # Set up for item on these axes: 1d reference solution
    #plotitem = plotaxes.new_plotitem(plot_type='1d_plot')
    #plotitem.outdir = qref_dir
    #plotitem.plot_var = 0
    #plotitem.plotstyle = '-'
    #plotitem.color = 'r'
    #.kwargs = {'linewidth': 2}
    #plotitem.show = True       # show on plot?
    #plotaxes.afteraxes = "pylab.legend(('2d data', '1d reference solution'))"
    

    #-----------------------------------------
    # Figures for gauges
    #-----------------------------------------
    plotfigure = plotdata.new_plotfigure(name='q', figno=300, \
                    type='each_gauge')
    plotfigure.clf_each_gauge = True

    plotaxes = plotfigure.new_plotaxes()
    plotaxes.xlimits = 'auto'
    plotaxes.ylimits = 'auto'
    plotaxes.title = 'Pressure'
    plotitem = plotaxes.new_plotitem(plot_type='1d_plot')
    plotitem.plot_var = 0
    plotitem.plotstyle = 'b-'


    # Parameters used only when creating html and/or latex hardcopy
    # e.g., via clawpack.visclaw.frametools.printframes:

    plotdata.printfigs = True                # print figures
    plotdata.print_format = 'png'            # file format
    plotdata.print_framenos = 'all'          # list of frames to print
    plotdata.print_fignos = 'all'            # list of figures to print
    plotdata.html = True                     # create html files of plots?
    plotdata.html_homelink = '../README.html'   # pointer for top of index
    plotdata.html_movie = 'JSAnimation'      # new style, or "4.x" for old style
    plotdata.latex = True                    # create latex file of plots?
    plotdata.latex_figsperline = 2           # layout of plots
    plotdata.latex_framesperline = 1         # layout of plots
    plotdata.latex_makepdf = False           # also run pdflatex?

    return plotdata

    
    
# To plot gauge locations on pcolor or contour plot, use this as
# an afteraxis function:

#def addgauges(current_data):
    #from clawpack.visclaw import gaugetools
    #gaugetools.plot_gauge_locations(current_data.plotdata, \
         #gaugenos='all', format_string='ko', add_labels=True)
if __name__=="__main__":
    from clawpack.visclaw.plotclaw import plotclaw
    plotclaw(outdir='.',setplot=setplot,plotdir='_plots',format='forestclaw')
